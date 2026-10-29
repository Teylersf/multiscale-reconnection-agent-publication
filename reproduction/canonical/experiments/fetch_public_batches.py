"""Fetch 32 public OSF files (3,107,362,288 bytes) serially into an explicit directory.

No credentials required. Existing complete files are skipped only after size and
SHA256 verification. An interrupted prefix is resumed only after its recorded
local digest and pinned strong remote ETag are revalidated. Public OSF URLs use
standard redirects; signed redirect URLs are never printed or recorded.
"""
import argparse
import ast
import datetime as dt
from email.utils import parsedate_to_datetime
import hashlib
from http.client import IncompleteRead
import json
import math
import os
from pathlib import Path
import shutil
import struct
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data/upstream-cc0/released-cohort-inventory.json'
UA='reproducibility-audit-public-cohort/1.0'


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def npy_header(raw):
    if raw[:6]!=b'\x93NUMPY':raise ValueError('Response is not an NPY file')
    version=tuple(raw[6:8])
    if version==(1,0):n=struct.unpack('<H',raw[8:10])[0];start=10
    elif version in ((2,0),(3,0)):n=struct.unpack('<I',raw[8:12])[0];start=12
    else:raise ValueError('Unsupported NPY version')
    if start+n>len(raw):raise ValueError('NPY header exceeds the inspected prefix')
    info=ast.literal_eval(raw[start:start+n].decode('latin1'))
    if info['descr'] not in ('<f4','<f8') or info['fortran_order']:
        raise ValueError('Unexpected NPY dtype or array order')
    return {'version':list(version),'data_offset':start+n,**info}


def now():return dt.datetime.now(dt.timezone.utc).isoformat()


def fetch_one(entry,dest,state,save):
    target=(dest/entry['local_relative_path']).resolve()
    if not target.is_relative_to(dest.resolve()):raise ValueError('Destination escapes output directory')
    target.parent.mkdir(parents=True,exist_ok=True);part=target.with_suffix('.npy.part')
    record=state['files'].setdefault(entry['id'],{'source_id':entry['id'],'public_url':entry['download_url'],
            'local_relative_path':entry['local_relative_path'],'expected_bytes':entry['size'],'expected_sha256':entry['sha256']})
    for complete in (target,part):
        if complete.exists() and complete.stat().st_size==entry['size'] and digest(complete)==entry['sha256']:
            if complete==part:part.replace(target)
            record.update(status='verified',actual_bytes=entry['size'],actual_sha256=entry['sha256'],verified_utc=now());save();return
    if target.exists():raise ValueError('An existing final file fails verification; preserve it and choose a clean output directory')
    for attempt in range(1,13):
        try:
            with urlopen(Request(entry['download_url'],headers={'Range':'bytes=0-255','User-Agent':UA}),timeout=60) as response:
                if response.status not in (200,206):raise ValueError('Unexpected header-request HTTP status')
                raw=response.read(256);etag=response.headers.get('ETag','')
                if response.status==206 and response.headers.get('Content-Range')!=f"bytes 0-255/{entry['size']}":
                    raise ValueError('Invalid prefix Content-Range')
                record['npy_header']=npy_header(raw)
            if etag!=f'"{entry["md5"]}"':raise ValueError('Pinned strong ETag mismatch')
            offset=0
            if part.exists():
                if (record.get('partial_bytes')==part.stat().st_size and record.get('partial_sha256')==digest(part)
                        and record.get('partial_etag')==etag and part.stat().st_size<entry['size']):
                    offset=part.stat().st_size
                else:part.unlink()
            headers={'User-Agent':UA,'Accept-Encoding':'identity'}
            if offset:headers.update({'Range':f'bytes={offset}-','If-Range':etag})
            with urlopen(Request(entry['download_url'],headers=headers),timeout=90) as response:
                if offset:
                    expected=f"bytes {offset}-{entry['size']-1}/{entry['size']}"
                    if response.status!=206 or response.headers.get('Content-Range')!=expected:
                        raise ValueError('Server rejected validated range resume')
                elif response.status!=200:raise ValueError('Unexpected full-download HTTP status')
                if response.headers.get('ETag')!=etag:raise ValueError('ETag changed during acquisition')
                record.update(status='downloading',attempt=attempt,started_utc=now(),resume_offset=offset);save()
                with part.open('ab' if offset else 'wb') as stream:
                    while True:
                        chunk=response.read(4*1024*1024)
                        if not chunk:break
                        stream.write(chunk)
                        if stream.tell()>entry['size']:raise ValueError('Response exceeds expected file size')
                    stream.flush();os.fsync(stream.fileno())
            actual_size=part.stat().st_size;actual_sha=digest(part)
            if actual_size!=entry['size'] or actual_sha!=entry['sha256']:
                part.unlink();raise ValueError('Completed file fails size/SHA256 verification; rejected prefix discarded')
            part.replace(target)
            record.update(status='verified',actual_bytes=actual_size,actual_sha256=actual_sha,verified_utc=now())
            for key in ('partial_bytes','partial_sha256','partial_etag','last_error'):record.pop(key,None)
            save();return
        except (HTTPError,URLError,TimeoutError,OSError,ValueError,IncompleteRead) as exc:
            # Do not stringify URLs from a redirect error. Only its type/status are public.
            code=getattr(exc,'code',None)
            record.update(status='retry_wait',last_error={'type':type(exc).__name__,'http_status':code},attempt=attempt)
            if part.exists():record.update(partial_bytes=part.stat().st_size,partial_sha256=digest(part),partial_etag=locals().get('etag'))
            delay=min(60,5*2**min(attempt-1,4))
            if isinstance(exc,HTTPError):
                retry_after=exc.headers.get('Retry-After','')
                if retry_after.isdigit():delay=max(delay,int(retry_after))
                elif retry_after:
                    try:
                        at=parsedate_to_datetime(retry_after)
                        delay=max(delay,math.ceil((at-dt.datetime.now(dt.timezone.utc)).total_seconds()))
                    except (ValueError,TypeError,OverflowError):pass
            record['retry_delay_seconds']=delay;save()
            print(f"Retry {attempt} for {entry['local_relative_path']}: {type(exc).__name__}, HTTP {code}; wait {delay}s",flush=True)
            if attempt==12:raise RuntimeError('Repeated acquisition failure; see the sanitized receipt') from None
            time.sleep(delay)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True,help='Explicit external directory; download is 3.11 GB')
    args=parser.parse_args();dest=args.output_dir.resolve()
    if dest.is_relative_to(ROOT):raise ValueError('Choose a cache outside this repository to keep the 3.11 GB raw data out of the release')
    dest.mkdir(parents=True,exist_ok=True)
    inventory=json.loads(MANIFEST.read_text(encoding='utf-8'));entries=inventory['files']
    if len(entries)!=32 or sum(e['size'] for e in entries)!=3107362288:raise ValueError('Unexpected public cohort inventory')
    if len({e['id'] for e in entries})!=32 or len({e['local_relative_path'] for e in entries})!=32:
        raise ValueError('Duplicate source identity or output path')
    for e in entries:
        if e['download_url']!=f"https://osf.io/download/{e['id']}/":raise ValueError('Unexpected source URL')
    missing=sum(e['size'] for e in entries if not (dest/e['local_relative_path']).exists())
    if shutil.disk_usage(dest).free<missing+200000000:raise ValueError('Insufficient free space for the requested cohort')
    receipt=dest/'public-fetch-receipt.json'
    state=json.loads(receipt.read_text(encoding='utf-8')) if receipt.exists() else {'schema_version':1,'files':{}}
    pin=digest(MANIFEST)
    if state.get('inventory_sha256',pin)!=pin:raise ValueError('Receipt belongs to another inventory')
    state['inventory_sha256']=pin
    def save():
        state['updated_utc']=now();tmp=receipt.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8');tmp.replace(receipt)
    entries.sort(key=lambda e:(e['released_batch'],e['time_batch'],e['kind']))
    for i,e in enumerate(entries,1):
        fetch_one(e,dest,state,save)
        print(f"[{i}/32] VERIFIED {e['local_relative_path']} ({e['size']} bytes)",flush=True)
    state.update(complete=True,total_verified_files=32,total_verified_bytes=3107362288);save()


if __name__=='__main__':main()
