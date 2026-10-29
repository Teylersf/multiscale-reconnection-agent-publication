"""Offline authorized agent-edition preparation; no network, Git or credentials."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
CANONICAL=ROOT.parent/'multiscale-reconnection-audit'
PRIVATE=ROOT.parents[1]/'.publishing-access/multiscale-outgoing'
CANONICAL_REPOSITORY='https://github.com/Teylersf/multiscale-reconnection-audit'
AGENT_REPOSITORY='https://github.com/Teylersf/multiscale-reconnection-agent-publication'
AGENT_ID='agent_29b9bf7a'
AGENT_NAME='Lattice Audit Agent'
IDENTITY='gist:7c74312cf47dcc31c789a8b1c3dedd25'
PLATFORM_HEADINGS=['Introduction','Related Work','Methodology','Results','Discussion','Limitations','Conclusion']
TAGS=['magnetic-reconnection','particle-energization','first-passage','regional-attribution','reproducibility']
PREPARER_BYTES=Path(__file__).read_bytes()

MATH = re.compile(r"\\\[.*?\\\]|\\\(.*?\\\)|\$\$.*?\$\$|(?<![\\$])\$(?!\$).*?(?<!\\)\$(?!\$)", re.S)
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n").encode("utf-8")


def utf16_length(text):
    return len(text.encode("utf-16-le")) // 2


def words(text):
    return len(re.findall(r"\b[\w'-]+\b", text))


def sections(text):
    matches = list(re.finditer(r"^## (.+)$", text, re.M))
    out = {}
    for i, m in enumerate(matches):
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        if m.group(1) in out:
            raise ValueError("Duplicate canonical section heading")
        out[m.group(1)] = text[m.end():end].strip()
    return out


def numbered_sections(parsed):
    out = {}
    for heading, body in parsed.items():
        m = re.fullmatch(r"([1-8])\. (.+)", heading)
        if m:
            if int(m.group(1)) in out:
                raise ValueError("Duplicate canonical numbered section")
            out[int(m.group(1))] = (heading, body)
    if sorted(out) != list(range(1, 9)):
        raise ValueError("Expected exactly canonical numbered sections 1 through 8")
    return out


def appendix_sections(parsed):
    """Keep optional top-level appendices in source order; never discard one."""
    numbered = numbered_sections(parsed)
    keys = list(parsed)
    out = {}
    if list(numbered) != list(range(1,9)):
        raise ValueError("Required scientific sections must remain in order 1 through 8")
    for heading, body in parsed.items():
        match = re.fullmatch(r"Appendix ([A-Z])(?:[.:]\s*|\s+|$)(.*)", heading)
        if match:
            letter = match.group(1)
            if letter in out:
                raise ValueError("Duplicate canonical appendix letter")
            out[letter] = (heading, body)
    expected = [chr(ord('A')+i) for i in range(len(out))]
    if list(out) != expected:
        raise ValueError("Appendices must be contiguous and ordered A, B, ...")
    permitted = {"Abstract", "References", *(h for h,_ in numbered.values()),
                 *(h for h,_ in out.values())}
    if set(parsed) != permitted:
        raise ValueError("Unrecognized top-level scientific heading; refuse to omit it")
    conclusion = keys.index(numbered[8][0])
    reference = keys.index("References")
    if conclusion >= reference or any(not conclusion < keys.index(h) < reference
                                     for h,_ in out.values()):
        raise ValueError("Appendices must follow Conclusion and precede References")
    if keys != ["Abstract", *(h for h,_ in numbered.values()),
                *(h for h,_ in out.values()), "References"]:
        raise ValueError("Canonical top-level section order is inconsistent")
    return out


def protected_blocks(text):
    """Full text equality is primary; these independent inventories aid review."""
    return {
        "math": math_tokens(text),
        "tables": re.findall(r"(?m)^(?:[ \t]*\|[^\n]*\|[ \t]*(?:\n|$))+", text),
        "quotations": re.findall(r"(?m)^(?:>[^\n]*(?:\n|$))+", text),
        "code_fences": re.findall(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$", text),
        "proof_markers": re.findall(r"(?m)^(?:#{3,6}\s+)?(?:\*\*)?Proof\b[^\n]*", text),
    }


def platform_arrangement(numbered, appendices):
    """Return unchanged bodies in the required seven-plus-optional order."""
    mapped = [numbered[1][1], numbered[2][1], numbered[3][1],
              "### "+numbered[4][0]+"\n\n"+numbered[4][1]+"\n\n### "+numbered[5][0]+"\n\n"+numbered[5][1],
              numbered[6][1], numbered[7][1], numbered[8][1]]
    headings = list(PLATFORM_HEADINGS)
    if appendices:
        mapped.append("\n\n".join("### "+heading+"\n\n"+body
                                   for heading,body in appendices.values()))
        headings.append("Appendix")
    return headings, mapped


def references(text):
    matches = list(re.finditer(r"^\[(\d+)\] (.+?)(?=\n\n\[\d+\] |\Z)", text, re.M | re.S))
    if not matches:
        raise ValueError("No canonical reference records found")
    result, originals = [], []
    for match in matches:
        number, record = match.group(1), match.group(2).strip()
        originals.append(match.group(0).strip())
        explicit = re.search(r"(?<!\*)\*([^*]+)\*(?!\*)", record)
        if "same title" in record:
            if not result:
                raise ValueError("Unresolved 'same title' reference")
            title = result[-1]["title"]
            author_part = record.split(", same title", 1)[0]
        elif explicit:
            title = explicit.group(1)
            author_part = record[:explicit.start()].rstrip(", ")
        else:
            raise ValueError("Reference requires an explicit verified canonical title")
        authors = [s.strip() for s in re.split(r",\s*|\s+and\s+", author_part) if s.strip()]
        urls = [u.rstrip(".;,") for u in re.findall(r"https?://[^\s]+", record)]
        years = re.findall(r"\b(?:19|20)\d{2}\b", record)
        if not authors or not urls or not years:
            raise ValueError("Reference lacks canonical authors, year or URL")
        item = {"ref_id": number, "type": "external",
                "source": "arxiv" if "arxiv.org" in urls[0] else "doi" if "doi.org" in urls[0] else "url",
                "title": title, "authors": authors, "year": int(years[0]), "url": urls[0]}
        doi = next((u.split("doi.org/", 1)[1] for u in urls if "doi.org/" in u), None)
        if doi:
            item["doi"] = doi
        result.append(item)
    if [int(x["ref_id"]) for x in result] != list(range(1, len(result)+1)):
        raise ValueError("Reference numbering must be contiguous")
    return result, originals


def math_tokens(text):
    return MATH.findall(text)


def scientific_paragraphs(text):
    return Counter(block.strip() for block in re.split(r"\n\s*\n", text.strip())
                   if block.strip() and not re.fullmatch(r"#{1,6} .+", block.strip()))


DISCLOSURE=(
    '**Authorship and assistance.** Lattice Audit Agent is the explicitly authorized agent author of this venue-specific edition. '
    'Human operator and canonical author: Taylor Kalin. The canonical manuscript retains Taylor Kalin at '
    +CANONICAL_REPOSITORY+'/blob/main/paper/manuscript.md . '
    'The scientific sections, mathematics, proofs, tables, figures and references are retained; only the byline, this disclosure and figure routes are adapted. '
    'AI tools assisted source retrieval, mathematical checks, code, internal adversarial review and drafting. These are not independent human peer review. '
    'The platform agent byline does not replace Taylor Kalin canonical authorship.')


def copy_inputs(canonical):
    manifest={}; manifest_names=['results/artifact-sha256.json']
    for name in ('results/revision-artifact-sha256.json','results/v1.2-artifact-sha256.json'):
        if (canonical/name).is_file():manifest_names.append(name)
    for manifest_name in manifest_names:
        current=json.loads((canonical/manifest_name).read_text(encoding='utf-8'))
        for name,digest in current.items():
            # Later versioned manifests supersede this reproduction document;
            # old numeric evidence must keep its original bytes.
            if name in manifest and manifest[name]!=digest and name!='REPRODUCIBILITY.md':
                raise ValueError('Conflicting scientific artifact manifests: '+name)
            if not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Invalid scientific file SHA256')
            manifest[name]=digest
    names=set(manifest)|set(manifest_names)|{'paper/main.pdf'}
    names.update(n for n in ['README.md','SOURCE.md','requirements.txt','LICENSE-CODE','LICENSE-MANUSCRIPT'] if (canonical/n).is_file())
    names.update(p.relative_to(canonical).as_posix() for p in (canonical/'paper').glob('*.md'))
    result={}
    for name in sorted(names):
        p=canonical/name
        if p.is_symlink() or not p.resolve().is_relative_to(canonical.resolve()):raise ValueError('Copy input escapes canonical root')
        if any(x in {'audit','submissions','.publishing-access','private','__pycache__'} for x in Path(name).parts):raise ValueError('Nonpublic copy input')
        data=p.read_bytes()
        if name in manifest and sha(data)!=manifest[name]:raise ValueError('Science-manifest mismatch: '+name)
        if p.suffix in {'.json','.md','.py'} and re.search(r'(?:[A-Z]:[\\/]|/pscratch/)',data.decode('utf-8')):raise ValueError('Private absolute path in copy input: '+name)
        result[name]=data
    return result


def main():
    if sys.flags.optimize:raise RuntimeError('Do not disable preservation assertions with Python -O')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--canonical-root',type=Path,default=CANONICAL)
    parser.add_argument('--expected-code-commit',required=True)
    parser.add_argument('--expected-manuscript-sha256',required=True)
    parser.add_argument('--outgoing-dir',type=Path,default=PRIVATE)
    parser.add_argument('--candidate',action='store_true',help='Label the locally prepared edition as a candidate; all formal gates remain closed')
    args=parser.parse_args();canonical=args.canonical_root.resolve()
    if not re.fullmatch('[0-9a-f]{40}',args.expected_code_commit):raise ValueError('Full scientific commit required')
    raw=(canonical/'paper/manuscript.md').read_bytes()
    if sha(raw)!=args.expected_manuscript_sha256:raise ValueError('Canonical manuscript changed')
    source=raw.decode('utf-8')
    if args.expected_code_commit not in source:raise ValueError('Scientific pin absent from manuscript')
    title=re.search(r'^# (.+)$',source,re.M).group(1)
    version,date=re.search(r'^Version ([^;\s]+); (.+)$',source,re.M).groups()
    parsed=sections(source);numbered=numbered_sections(parsed);appendices=appendix_sections(parsed)
    canonical_metadata=json.loads((canonical/'submissions/metadata.json').read_text(encoding='utf-8'))
    if (canonical_metadata.get('version')!=version
            or canonical_metadata.get('scientific_code_commit')!=args.expected_code_commit
            or canonical_metadata.get('title')!=title
            or canonical_metadata.get('abstract')!=parsed['Abstract']):
        raise ValueError('Canonical metadata and manuscript pins disagree')
    code_doi=canonical_metadata.get('code_doi')
    if not isinstance(code_doi,str) or 'https://doi.org/'+code_doi not in source:
        raise ValueError('Current computational archive DOI absent from manuscript')
    ordered=[*numbered.values(),*appendices.values()]
    science='\n\n'.join(body for _,body in ordered);abstract=parsed['Abstract']
    audited_excerpt=(canonical/'data/upstream-cc0/first_passage_function.py').read_bytes()
    listing=[b for b in re.findall(r'(?ms)^```[^\n]*\n(.*?)^```',science)
             if b.startswith('def get_energy_by_region_w_bands(')]
    if len(listing)!=1 or listing[0].encode('utf-8')!=audited_excerpt:
        raise ValueError('The complete pinned upstream function listing must remain byte-exact')
    refs,ref_blocks=references(parsed['References'])
    if len(refs)<8:raise ValueError('At least eight references required')
    disclosures=re.findall(r'^\*\*Authorship and assistance\.\*\* .+$',source,re.M)
    if len(disclosures)!=1:raise ValueError('Exactly one canonical authorship disclosure required')
    original_disclosure=disclosures[0];images=IMAGE.findall(source);link_map={}
    for caption,link in images:
        p=(canonical/'paper'/link).resolve()
        if not link.startswith('../figures/') or p.parent!=canonical/'figures' or not p.is_file():raise ValueError('Unexpected figure route')
        link_map[link]='reproduction/canonical/figures/'+p.name
    def adapt(body,absolute=False):
        body=body.replace(original_disclosure,DISCLOSURE)
        for old,new in link_map.items():
            if absolute:new='https://raw.githubusercontent.com/Teylersf/multiscale-reconnection-agent-publication/main/'+new
            body=body.replace(']('+old+')',']('+new+')')
        return body
    def restore(body,absolute=False):
        body=body.replace(DISCLOSURE,original_disclosure)
        for old,new in link_map.items():
            if absolute:new='https://raw.githubusercontent.com/Teylersf/multiscale-reconnection-agent-publication/main/'+new
            body=body.replace(']('+new+')',']('+old+')')
        return body
    agent_body='\n\n'.join('## '+heading+'\n\n'+adapt(body) for heading,body in ordered)
    paper=('# '+title+'\n\n**'+AGENT_NAME+'**  \nAuthorized agent edition. Human operator and canonical author: **Taylor Kalin**.  \n'
        'AgentPub identity: `'+AGENT_ID+'`; AAES identity: `'+IDENTITY+'`.  \n'
        'Canonical author: https://taylorkalin.com ; ORCID 0009-0003-9000-9315.  \nVersion '+version+'; '+date+'\n\n'
        '## Abstract\n\n'+abstract+'\n\n'+agent_body+'\n\n## References\n\n'+parsed['References']+'\n')
    headings,mapped=platform_arrangement(numbered,appendices);platform=[];source_label_exceptions=[]
    for heading,body in zip(headings,mapped):
        content=adapt(body,absolute=True)
        # Preserve source-code subscripts such as gamma[0] literally, while
        # deriving citation metadata only from prose outside code spans.
        citation_text=re.sub(r'(?ms)^```[^\n]*\n.*?^```[ \t]*$', '', content)
        citation_text=re.sub(r'`[^`\n]+`', '', citation_text)
        labels=set(re.findall(r'\[(\d+)\](?!\()',citation_text));valid={r['ref_id'] for r in refs}
        unresolved=labels-valid
        # The source preprint footnote number is literal scientific text, not
        # reference32 of this article. Preserve the text exactly.
        if unresolved:
            if (unresolved!={'32'} or content.count('[32]')!=1
                    or "preprint's footnote [32]" not in content):raise ValueError('Unresolved citation')
            source_label_exceptions.append({'section':heading,'label':'32','meaning':'explicit source-preprint footnote number, not this bibliography'})
        citations=sorted(labels&valid,key=int)
        platform.append({'heading':heading,'content':content,'citations':citations})
    caps={s['heading']:{'unicode_codepoints':len(s['content']),'utf16_code_units':utf16_length(s['content'])} for s in platform}
    if any(max(v.values())>49000 for v in caps.values()):raise ValueError('Section exceeds49000; scientific truncation forbidden')
    restored_platform='\n\n'.join(restore(s['content'],absolute=True) for s in platform)
    ap=sections(paper)
    restored_paper='\n\n'.join(restore(body) for _,body in [*numbered_sections(ap).values(),*appendix_sections(ap).values()])
    assert restored_paper==science and restored_platform=='\n\n'.join(mapped)
    assert scientific_paragraphs(restored_platform)==scientific_paragraphs(science)
    assert protected_blocks(science)==protected_blocks(restored_platform)==protected_blocks(restored_paper)
    assert math_tokens(science)==math_tokens(restored_platform)==math_tokens(restored_paper)
    assert IMAGE.findall(restored_platform)==images
    assert ap['Abstract']==abstract and ap['References']==parsed['References']
    assert '??' not in paper and 'TODO' not in paper
    schema_path=ROOT/'reproduction/venue-schema-snapshot.json';schema_bytes=schema_path.read_bytes();schema=json.loads(schema_bytes)
    constraints=schema['agentpub']['research_article_constraints'];body_words=sum(words(s['content']) for s in platform)
    guidelines={'title':len(title)<=constraints['title']['max_chars'],
        'abstract':words(abstract)<=constraints['abstract']['max_words'],
        'references':len(refs)>=constraints['references']['min_count'],
        'body_words':constraints['body_word_count']['min_words']<=body_words<=constraints['body_word_count']['max_words'],
        'required_section_order':headings[:7]==PLATFORM_HEADINGS,
        'allowed_sections':all(h in constraints['sections']['allowed'] for h in headings)}
    if not all(guidelines.values()):raise ValueError('Official template format check failed')
    note=('Authorized agent edition; Taylor Kalin is human operator and canonical author. All scientific paragraphs, complete proofs, math, tables, figures, captions and references remain. '
        'Sections4+5 form Results; complete appendices follow Conclusion in Appendix. Exact model identifier and token usage were not recorded. '
        'agent_model is not recorded and total_tokens=-1 is an explicit missing-data sentinel, not an estimate; input_tokens/output_tokens are omitted. '
        'Local preparation is not a submission. Publish.fun published canonical version 1.2.0 as PF-261029.000003 on 29 October 2026; this agent edition includes the subsequent canonical editorial clarifications. '
        'No update of the published Publish.fun article, formal agent review or venue eligibility is certified by preparation. '
        'Full edition: '+AGENT_REPOSITORY+'/blob/main/paper.md ; canonical PDF: '+CANONICAL_REPOSITORY+'/blob/main/paper/main.pdf .')
    payload={'title':title,'abstract':abstract,'paper_type':'research_article',
        'authors':[{'agent_id':AGENT_ID,'display_name':AGENT_NAME,'model_type':'not recorded'}],
        'sections':platform,'references':refs,'tags':TAGS,
        'metadata':{'agent_model':'not recorded','agent_platform':'Codex desktop','total_tokens':-1,'submission_note':note}}
    now=datetime.now(timezone.utc).isoformat()
    metadata={'aaes_version':'4.2','title':title,'abstract':abstract,'author_ids':[IDENTITY],
        'submitted_at':now,'tags':TAGS,'generation_environment':{'model':'not recorded',
            'tools':['Python','NumPy','Matplotlib'],'prompt_strategy':'Source-specific audit, exact identities and counterexamples, paired analysis of all released batches, preserved public examples, positive reconstruction and internal adversarial review.',
            'notes':'Agent author Lattice Audit Agent; human operator/canonical author Taylor Kalin. Self-funded. Exact model/token usage unavailable. Timestamp is preparation, not AAES registration. No independent human peer review or new PIC run.'},
        'novelty_statement':'Source-specific distinction between first-passage phases and regional particle energization, connected to eight printed annotations in four public illustrations and exact full-history links for three examples. Paired analysis of all 1,003 released histories selects 667 intermediate and 84 high-band records under the source cuts. The complete unchanged source function also executes on all 1,003 inputs and exactly matches every selected output. Both particle-mean fractions and total-net-gain shares are compared on identical records with signed gains. Paired history resampling adds explicitly conditional iid empirical percentile ranges, without population-confidence or significance claims. Exact counterexamples accompany finite-cadence and estimand limits. Elementary identities are standard. Unknown release probabilities and the mismatch to the published intermediate-band point prevent a full historical-cohort correction, universal bias direction, physical confidence bound or claimed reversal of the original population result.'}
    claims=[
        {'text':'The deposited particle-attribution function computes chronological phases that need not equal time-local regional gains.','kind':'finding','status':'proposed','evidence_summary':'Section4/AppendixA, source lines344–403, results/first-passage-checks.json.','confidence_note':'Posted code postdates arXivv1; exact historical full-cohort execution is not identified.'},
        {'text':'Zero-transition-increment traces reverse the inferred dominant region while preserving total gain.','kind':'finding','status':'proposed','evidence_summary':'Intermediate/high-band return tests and ordered controls.','confidence_note':'Constructed counterexamples, not PIC outcomes or a cohort-bias estimate.'},
        {'text':'The function reproduces all eight CS/DS annotations in four deposited illustrative trajectories.','kind':'finding','status':'proposed','evidence_summary':'Hash-pinned fixtures and Section4 output table.','confidence_note':'Four selected examples; no representative cohort estimate or uniquely corrected continuous-work partition.'},
        {'text':'Display transformations reconstruct published regional electron-frame curves and preserve downstream dominance of that proxy.','kind':'finding','status':'proposed','evidence_summary':'AppendixC and results/proxy-verification.json.','confidence_note':'Display operations are an independently inferred reconstruction. No exact historical plotting-program identity, new PIC run or De magnetic-energy closure is claimed.'},
        {'text':'In the 84 available high-band records, the downstream particle mean changes from 0.500318 under first passage to 0.370129 under symmetric saved-history attribution; the share of total net gain changes from 0.490959 to 0.393724.','kind':'finding','status':'proposed','evidence_summary':'Section 5, results/public-batch-checks.json, results/public-batch-independent-verification.json and per-particle NPZ/CSV.','confidence_note':'All 1,003 released histories are pooled before strict cuts, selecting 667 intermediate and 84 high-band records. Unknown release probabilities and the original intermediate-point mismatch prevent a full-population correction. The two estimands do not undergo the same ordering change; endpoint conventions are not a continuous-work bound.'},
        {'text':'Executing the complete pinned source function on all 1,003 released inputs gives exact index and regional-array agreement for all 751 selected histories; paired resampling diagnostics cover both bands and both estimands.','kind':'finding','status':'proposed','evidence_summary':'Section 5 and results/full-source-validation-v1.2.0.json, paired-history-bootstrap-v1.2.0.json and full-source-bootstrap-independent-v1.2.0.json.','confidence_note':'Resampling uses 20,000 iid empirical history draws per band with common paired IDs. Unknown release selection and within-run particle correlation prevent population confidence or significance claims and can make these conditional ranges too narrow.'}]
    registration={'source':'github:Teylersf/multiscale-reconnection-agent-publication',
        'submission':{'kind':'paper','maturity':'final'},'project':{'title':title,'summary':abstract,
             'research_question':'Does the deposited first-passage estimator equal recorded regional energization, and how do paired saved-history fractions differ on the available released batches under both estimands?','status':'active'},'claims':claims}
    pf={};receipt=canonical/'submissions/publishfun-receipt.json'
    if receipt.exists():
        row=json.loads(receipt.read_text(encoding='utf-8'));pf={k:v for k,v in row.get('response',{}).items() if k in ['id','status','current_round']}
    current_receipt=canonical/'submissions/publishfun-current-status.json'
    pf_current={}
    if current_receipt.is_file():
        current=json.loads(current_receipt.read_text(encoding='utf-8'))
        pf_current={k:v for k,v in current.get('response',{}).items()
                    if k in ['id','status','current_round','editorial_state','published_at']}
        if pf.get('id') and pf_current.get('id')!=pf['id']:raise ValueError('Foreign Publish.fun status receipt')
    context={'prepared_at_utc':now,'canonical_version':version,'canonical_manuscript_sha256':sha(raw),
        'scientific_code_commit':args.expected_code_commit,'code_doi':code_doi,
        'publishfun_last_submission_receipt':pf,'publishfun_last_observed_status':pf_current,
        'publication_state':'local_candidate_prepared_not_submitted' if args.candidate else 'local_prepared_not_submitted',
        'candidate_only':args.candidate,'publishfun_release_verified':False,
        'submission_gate_open':False,'agentpub_submission_gate_open':False,'aaes_submission_gate_open':False,
        'public_agent_edition_verified':False,'identity_or_AAES_eligibility_verified':False,
        'note':'The canonical version 1.2.0 was published by Publish.fun as PF-261029.000003 on 29 October 2026. This agent edition is prepared, not submitted, and includes subsequent editorial clarifications. Local gate flags remain conservative: the preparer does not independently certify publication, public repository access or venue eligibility. The separately authorized publisher rechecks this study live.'}
    inputs=copy_inputs(canonical)
    if inputs.get('paper/manuscript.md')!=raw:raise ValueError('Canonical changed during preparation')
    copies={'reproduction/canonical/'+name:data for name,data in inputs.items()}
    manifest=[{'canonical_path':name,'copy_path':'reproduction/canonical/'+name,'bytes':len(data),'sha256':sha(data)} for name,data in inputs.items()]
    checks={'canonical_version':version,'canonical_manuscript_sha256':sha(raw),'scientific_code_commit':args.expected_code_commit,
        'preparer_sha256':sha(PREPARER_BYTES),'schema_snapshot_sha256':sha(schema_bytes),'platform_sections':headings,
        'section_character_counts':caps,'math_segments':len(math_tokens(science)),
        'protected_block_counts':{k:len(v) for k,v in protected_blocks(science).items()},
        'figures':len(images),'references':len(refs),'reference_source_blocks':ref_blocks,'source_label_exceptions':source_label_exceptions,
        'body_regex_words':body_words,'abstract_regex_words':words(abstract),'guideline_checks':guidelines,
        'scientific_section_bodies':[{'heading':h,'sha256':sha(b.encode())} for h,b in ordered],
        'all_scientific_paragraphs_exact_after_declared_reversal':True,'ordered_math_exact':True,
        'complete_proofs_tables_figures_captions_references_preserved':True,'abstract_exact':True,
        'upstream_function_listing_sha256':sha(audited_excerpt),
        'upstream_function_listing_lines':len(audited_excerpt.splitlines()),
        'allowed_changes':['agent byline','one explicit disclosure','declared figure routes','platform grouping'],
        'copied_scientific_files':manifest,'submission_gate_open':False,
        'agentpub_payload_sha256':sha(encode_json(payload)),'aaes_registration_sha256':sha(encode_json(registration)),
        'model_identifier_or_token_usage_estimated':False,'token_missing_data_sentinel':-1}
    readme=f'''# {title}

Agent edition by **{AGENT_NAME}**. Human operator and canonical author: **Taylor Kalin**.

Version {version}. The [canonical audit]({CANONICAL_REPOSITORY}) retains Taylor Kalin. All scientific sections, complete proofs, tables, figure captions, ordered mathematics and references remain. Only the declared byline/disclosure, image routes and platform grouping change.

- [Full agent manuscript](paper.md)
- [AAES metadata](metadata.json)
- [Preservation checks](reproduction/adapter-checks.json)
- [Reproduction](reproduction/README.md)
- [Preparation context](reproduction/submission-context.json)

This package preserves {len(math_tokens(science))} scientific math segments, {len(images)} figures and {len(refs)} references, with {len(manifest)} byte-exact canonical copies. Numerical snapshot: `{args.expected_code_commit}`. Current software/data DOI: https://doi.org/{code_doi} .

The revision includes a paired analysis of all 1,003 released histories: 667 intermediate and 84 high-band records meet the source cuts. In the available high subset the downstream particle mean changes from 0.500318 to 0.370129 under symmetric attribution. Its total-net-gain share changes from 0.490959 to 0.393724; it was already below one half under first passage. The complete pinned function validates every selected output exactly. Paired history resampling supplies conditional iid empirical percentile ranges, whose selection and particle-correlation limits are explicit. Unknown release probabilities and the mismatch to the original intermediate-band point prevent a full historical-cohort correction or a population-wide ordering claim. Endpoint alternatives and resampling ranges are not certified continuous-work bounds or population confidence intervals. Positive field and inferred proxy checks remain. AI-assisted internal checks are not independent human peer review.

**Agent edition prepared; not submitted.** Publish.fun published canonical version 1.2.0 as [PF-261029.000003](https://publish.fun/papers/PF-261029.000003) on 29 October 2026. This version {version} agent edition incorporates the subsequent editorial clarifications; it does not claim that the published Publish.fun article has been updated. Local preparer gate flags remain conservative. Public edition availability, identity access, AAES eligibility and venue rendering require separate verification. Outgoing API bodies remain in the private local publishing directory; no credentials or submission automation are included.

Own text/figures: CC BY4.0; own code: MIT. Upstream CC0 fixtures/excerpt retain their provenance; other works/software retain applicable rights. Existing AAES identity: [{IDENTITY}](https://gist.github.com/Teylersf/7c74312cf47dcc31c789a8b1c3dedd25).
'''
    reproduction=f'''# Reproduction of agent edition {version}

Scientific numerical pin: `{args.expected_code_commit}`. Current manuscript and file hashes are in adapter-checks.json.

```console
cd reproduction/canonical
python -m pip install -r requirements.txt
python experiments/verify_analytic_checks.py
python experiments/verify_first_passage.py
python experiments/verify_proxy_curves.py
python experiments/verify_public_batch_summary.py
python experiments/verify_source_bootstrap_compact.py
```

These bounded CPU checks use local numeric-only fixtures. They do not rerun VPIC or estimate a full-cohort correction. They preserve signed gains and separate discrete allocation from continuous work. Only the pinned attribution function excerpt is run, not unrelated top-level filesystem operations.

For complete raw-batch reproduction, follow reproduction/canonical/REPRODUCIBILITY.md. The explicit fetcher downloads32 files (3.11GB) serially into a separately chosen external cache and the analyzer processes the verified arrays in bounded time blocks. No large raw arrays are copied into this agent package. The compact summary verifier reads the frozen per-particle exports without network or another raw-array acquisition.

The version1.2 source-function/resampling command in that document requires the same verified raw cache and a fresh output directory; it performs no download. All prior numeric outputs remain byte-exact. The compact bootstrap verifier reproduces the frozen resampling diagnostics without another raw-data read.

```console
python reproduction/prepare_packages.py --expected-code-commit {args.expected_code_commit} --expected-manuscript-sha256 {sha(raw)}{' --candidate' if args.candidate else ''}
```

Keep the canonical checkout beside this repository or use --canonical-root. Preparation performs no network, Git, credential access, registration or submission. Sections1–8 and every appendix remain in paper.md; AgentPub maps3 to Methodology,4+5 to Results,6 to Discussion,7 to Limitations and8 to Conclusion, followed by Appendix. It requires exact full-section/paragraph restoration, ordered math and proof/table/caption inventories and all references. Every platform section fits Unicode and UTF16 within49000; official word/reference/order checks pass without shortening or padding science.

Only approved manifest science, owned paper/PDF and supporting licenses are copied. Private notes, source PDFs, venue receipts, credentials and HPC paths are excluded. Outgoing API bodies stay private; their hashes/counts are public. Model/token usage were not recorded: agent_model is explicitly not recorded and total_tokens=-1 is a missing-data sentinel, not an estimate. Local preparer gate flags remain conservative and do not certify external availability or eligibility. Publish.fun published canonical version 1.2.0 as PF-261029.000003; this agent edition includes subsequent editorial clarifications. Any formal agent submission requires separate live checks. AAES account verification is a separate operational constraint.

Copy selection merges artifact-sha256.json, revision-artifact-sha256.json and v1.2-artifact-sha256.json in that order when present. A later REPRODUCIBILITY.md hash supersedes the historical document hash; conflicting hashes for earlier numerical evidence are rejected. Versioned manifests remain alongside the current document so the historical snapshots remain identifiable.
'''
    products={'paper.md':paper.encode(),'agent-paper.md':paper.encode(),'metadata.json':encode_json(metadata),'README.md':readme.encode(),
        'reproduction/README.md':reproduction.encode(),'reproduction/adapter-checks.json':encode_json(checks),
        'reproduction/submission-context.json':encode_json(context),
        '.gitattributes':(
            b'* text=auto eol=lf\n*.json -text\n*.csv -text\n*.npy binary\n*.npz binary\n*.png binary\n*.pdf binary\n'
            b'# Preserve the byte-exact attributed source listing in agent/canonical copies.\n'
            b'paper.md whitespace=-blank-at-eol\nagent-paper.md whitespace=-blank-at-eol\n'
            b'reproduction/canonical/paper/audited-function.md whitespace=-blank-at-eol\n'
            b'reproduction/canonical/paper/manuscript.md whitespace=-blank-at-eol\n'
            b'reproduction/canonical/data/upstream-cc0/first_passage_function.py whitespace=-blank-at-eol\n'),
        '.gitignore':b'__pycache__/\n*.pyc\n',**copies}
    if Path(__file__).read_bytes()!=PREPARER_BYTES or schema_path.read_bytes()!=schema_bytes:raise ValueError('Preparer/schema changed')
    for name,data in inputs.items():
        if (canonical/name).read_bytes()!=data:raise ValueError('Canonical input changed: '+name)
    for name,data in products.items():
        p=ROOT/name
        if not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Output escapes root')
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    args.outgoing_dir.mkdir(parents=True,exist_ok=True)
    outgoing={'multiscale-agentpub-payload.json':encode_json(payload),'multiscale-aaes-registration.json':encode_json(registration)}
    for name,data in outgoing.items():(args.outgoing_dir/name).write_bytes(data)
    for name,data in products.items():assert (ROOT/name).read_bytes()==data
    for name,data in outgoing.items():assert (args.outgoing_dir/name).read_bytes()==data
    print(json.dumps({'prepared':True,'canonical_sha256':sha(raw),'math_segments':checks['math_segments'],
        'figures':len(images),'references':len(refs),'copies':len(manifest),'body_regex_words':body_words,
        'section_character_counts':caps,'agentpub_payload_sha256':checks['agentpub_payload_sha256'],
        'aaes_registration_sha256':checks['aaes_registration_sha256'],'submission_gate_open':False,
        'outgoing_filenames':list(outgoing)}))


if __name__=='__main__':main()
