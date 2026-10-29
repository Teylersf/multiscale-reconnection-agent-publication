"""Memory-bounded analysis of the two publicly released OSF trajectory batches.

Run ``python experiments/analyze_public_batches.py --self-test`` without raw data.
After acquiring the 32 pinned files, supply ``--cohort-dir PATH``. Raw GB arrays
stay outside the repository. Numeric NPY inputs use mmap and allow_pickle=False.
The source's inspected function excerpt is executed only for validation; the
original script's filesystem operations and plotting are never executed.
"""
from pathlib import Path
import argparse
import ast
import contextlib
import csv
import hashlib
import io
import json
import time
import numpy as np

if not __debug__:
    raise RuntimeError('Do not use Python -O: input-integrity and numerical checks must remain enabled.')
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'upstream-cc0'
SEPARATORS = (5.77, 16.40)
LABELS = ('IS1', 'IS2', 'TB', 'DS', 'CS')
FP_LABELS = ('CS', 'DS', 'phase_residual')
PINNED_FUNCTION_SHA = '2909f9e6acec3c48f3838e86c15ffd18a9563dc57984e400b0baadd22f16655f'


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def source_function():
    path = DATA / 'first_passage_function.py'
    assert file_sha(path) == PINNED_FUNCTION_SHA
    tree = ast.parse(path.read_text(encoding='utf-8'))
    assert len(tree.body) == 1 and isinstance(tree.body[0], ast.FunctionDef)
    namespace = {'np': np, 'tqdm': lambda x, **kw: x}
    exec(compile(tree, str(path), 'exec'), namespace)
    return namespace['get_energy_by_region_w_bands']


class Ledger:
    """O(particles*regions) persistent memory, bounded time-block input memory."""
    def __init__(self, n):
        self.n = n
        self.samples = 0
        self.first = self.previous_g = self.previous_r = self.tags = None
        self.native_dtype = None
        self.cs_first = np.full(n, -1, dtype=np.int64)
        self.cs_last = np.full(n, -1, dtype=np.int64)
        self.ds_any = np.full(n, -1, dtype=np.int64)
        self.ds_after_cs = np.full(n, -1, dtype=np.int64)
        self.events = {}
        self.left = np.zeros((n, 5), dtype=np.float64)
        self.right = self.left.copy()
        self.left_pos = self.left.copy(); self.left_neg = self.left.copy()
        self.right_pos = self.left.copy(); self.right_neg = self.left.copy()
        self.bound = self.left.copy()
        self.entries = np.zeros((n, 5), dtype=np.int64)
        self.transitions = np.zeros(n, dtype=np.int64)
        self.transition_l1 = np.zeros(n, dtype=np.float64)
        self.cs_samples_after_ds = np.zeros(n, dtype=np.int64)
        self.cs_entries_after_ds = np.zeros(n, dtype=np.int64)
        self.max_gamma = np.zeros(n)

    def event(self, key, mask, g, last=False):
        stored = getattr(self, key)
        found = mask.any(axis=0)
        if not last:
            found &= stored < 0
        columns = np.flatnonzero(found)
        if not len(columns):
            return
        rows = ((len(g)-1-np.argmax(mask[::-1, columns], axis=0)) if last
                else np.argmax(mask[:, columns], axis=0))
        stored[columns] = self.samples + rows
        self.events[key][columns] = g[rows, columns]

    def consume(self, gamma, region, tags=None):
        g = np.asarray(gamma)
        r = np.asarray(region)
        assert g.ndim == 2 and g.shape == r.shape and g.shape[1] == self.n
        assert len(g) and np.isfinite(g).all() and np.isfinite(r).all()
        assert np.array_equal(r, np.rint(r)) and np.isin(r, np.arange(1, 6)).all()
        r = r.astype(np.uint8)
        if self.first is None:
            self.native_dtype = g.dtype
            self.first = g[0].copy()
            self.events = {k: np.zeros(self.n, dtype=g.dtype) for k in
                           ('cs_first', 'cs_last', 'ds_any', 'ds_after_cs')}
            for label in range(1, 6):
                self.entries[:, label-1] += r[0] == label
        assert g.dtype == self.native_dtype
        if tags is not None:
            tag = np.asarray(tags)
            assert tag.shape == g.shape and np.isfinite(tag).all()
            assert np.array_equal(tag, np.rint(tag))
            if self.tags is None:
                self.tags = tag[0].astype(np.int64)
                assert len(np.unique(self.tags)) == self.n
            assert np.array_equal(tag, np.broadcast_to(self.tags, tag.shape))
        cs = r == 5; ds = r == 4
        self.event('cs_first', cs, g)
        self.event('cs_last', cs, g, last=True)
        self.event('ds_any', ds, g)
        indices = self.samples + np.arange(len(g))[:, None]
        after = (self.cs_first[None, :] >= 0) & (indices > self.cs_first[None, :])
        self.event('ds_after_cs', ds & after, g)
        self.cs_samples_after_ds += np.sum(cs & (self.ds_after_cs[None, :] >= 0)
                                         & (indices > self.ds_after_cs[None, :]), axis=0)
        gf = g.astype(np.float64)
        self.max_gamma = np.maximum(self.max_gamma, np.max(np.abs(gf), axis=0))
        if self.previous_g is None:
            seqg, seqr = gf, r
            interval_start = self.samples
        else:
            seqg = np.concatenate((self.previous_g[None, :].astype(np.float64), gf), axis=0)
            seqr = np.concatenate((self.previous_r[None, :], r), axis=0)
            interval_start = self.samples - 1
        dg = np.diff(seqg, axis=0)
        left, right = seqr[:-1], seqr[1:]
        changed = left != right
        self.transitions += changed.sum(axis=0)
        self.transition_l1 += np.sum(np.where(changed, np.abs(dg), 0), axis=0)
        target_indices = interval_start + np.arange(1, len(seqg))[:, None]
        self.cs_entries_after_ds += np.sum(changed & (right == 5)
            & (self.ds_after_cs[None, :] >= 0)
            & (target_indices > self.ds_after_cs[None, :]), axis=0)
        for label in range(1, 6):
            lm, rm = left == label, right == label
            ld, rd = np.where(lm, dg, 0), np.where(rm, dg, 0)
            j = label-1
            self.left[:, j] += ld.sum(axis=0)
            self.right[:, j] += rd.sum(axis=0)
            self.left_pos[:, j] += np.maximum(ld, 0).sum(axis=0)
            self.left_neg[:, j] += np.minimum(ld, 0).sum(axis=0)
            self.right_pos[:, j] += np.maximum(rd, 0).sum(axis=0)
            self.right_neg[:, j] += np.minimum(rd, 0).sum(axis=0)
            self.bound[:, j] += np.where(lm != rm, np.abs(dg), 0).sum(axis=0)
            self.entries[:, j] += (changed & rm).sum(axis=0)
        self.previous_g = g[-1].copy(); self.previous_r = r[-1].copy()
        self.samples += len(g)

    def finish(self):
        g0, gn = self.first, self.previous_g
        fp = np.zeros((self.n, 3), dtype=np.float64)
        cs = self.cs_first >= 0; ds_after = self.ds_after_cs >= 0
        with_ds = cs & ds_after
        no_ds = cs & ~ds_after
        only_ds = ~cs & (self.ds_any >= 0)
        neither = ~cs & ~only_ds
        a, z, b, d = (self.events[k] for k in ('cs_first','cs_last','ds_after_cs','ds_any'))
        # Keep the source's native float32 subtraction/addition semantics exactly.
        fp[with_ds,0] = b[with_ds]-a[with_ds]
        fp[with_ds,1] = gn[with_ds]-b[with_ds]
        fp[with_ds,2] = a[with_ds]-g0[with_ds]
        fp[no_ds,0] = z[no_ds]-a[no_ds]
        fp[no_ds,2] = (a[no_ds]-g0[no_ds])+(gn[no_ds]-z[no_ds])
        fp[only_ds,1] = gn[only_ds]-d[only_ds]
        fp[only_ds,2] = d[only_ds]-g0[only_ds]
        fp[neither,2] = gn[neither]-g0[neither]
        total = gn.astype(np.float64)-g0.astype(np.float64)
        source_rounding_bound = 16*np.finfo(self.native_dtype).eps*np.maximum(self.max_gamma, 1)
        assert np.all(np.abs(fp.sum(axis=1)-total) <= source_rounding_bound)
        assert np.allclose(self.left.sum(axis=1), total, rtol=0, atol=1e-9)
        assert np.allclose(self.right.sum(axis=1), total, rtol=0, atol=1e-9)
        assert np.allclose(self.left_pos+self.left_neg,self.left,rtol=0,atol=1e-9)
        assert np.allclose(self.right_pos+self.right_neg,self.right,rtol=0,atol=1e-9)
        assert np.all(np.abs(self.right-self.left) <= self.bound+1e-9)
        assert np.all(np.abs(self.right-self.left).sum(axis=1) <= 2*self.transition_l1+1e-9)
        return {'initial_gamma':g0, 'final_gamma':gn, 'total_net_gain':total,
                'first_passage':fp, 'left':self.left, 'right':self.right,
                'symmetric':(self.left+self.right)/2,
                'left_gross_positive':self.left_pos,'left_gross_negative':self.left_neg,
                'right_gross_positive':self.right_pos,'right_gross_negative':self.right_neg,
                'tag':self.tags if self.tags is not None else np.arange(self.n),
                'region_entries':self.entries,'region_reentries':np.maximum(self.entries-1,0),
                'region_transitions':self.transitions,'transition_L1':self.transition_l1,
                'endpoint_difference_bound':self.bound,
                'CS_samples_after_first_subsequent_DS':self.cs_samples_after_ds,
                'CS_entries_after_first_subsequent_DS':self.cs_entries_after_ds,
                'first_CS_index':self.cs_first,'first_subsequent_DS_index':self.ds_after_cs,
                'source_fp_closure_residual':fp.sum(axis=1)-total}


def run_array(g, r, block=113):
    out = Ledger(g.shape[1])
    for i in range(0,len(g),block):
        out.consume(g[i:i+block],r[i:i+block])
    return out.finish()


def self_checks():
    started=time.perf_counter(); source=source_function(); rng=np.random.default_rng(251115988)
    cases=[]
    for dtype in (np.float32,np.float64):
        for ntime,npart in ((1,7),(2,13),(157,101),(1001,31)):
            g=(1+np.abs(rng.normal(size=(ntime,npart)))*20).astype(dtype)
            r=rng.integers(1,6,size=g.shape)
            if npart>6:
                r[:,0]=1;r[:,1]=4;r[:,2]=5;r[:,3]=2
                g[-1,:7]=np.asarray([1,5.77,16.40,5.78,16.41,6,17],dtype=dtype)
            got=run_array(g,r,block=19)
            with contextlib.redirect_stdout(io.StringIO()): result=source(g,r,*SEPARATORS)
            assert np.array_equal(result[6],np.flatnonzero((g[-1]>SEPARATORS[0])&(g[-1]<SEPARATORS[1])))
            assert np.array_equal(result[7],np.flatnonzero(g[-1]>SEPARATORS[1]))
            for offset,indices in ((0,result[6]),(3,result[7])):
                expected=np.column_stack(result[offset:offset+3])
                assert np.array_equal(got['first_passage'][indices],expected)
            other=run_array(g,r,block=41)
            for key in ('first_passage','left','right','symmetric','region_transitions','CS_samples_after_first_subsequent_DS','CS_entries_after_first_subsequent_DS'):
                if key in ('left','right','symmetric'):
                    assert np.allclose(got[key],other[key],rtol=1e-13,atol=1e-11),key
                else:
                    assert np.array_equal(got[key],other[key]),key
            dg=np.diff(g.astype(np.float64),axis=0)
            for label in range(1,6):
                assert np.allclose(got['left'][:,label-1],np.where(r[:-1]==label,dg,0).sum(axis=0),rtol=1e-13,atol=1e-11)
                assert np.allclose(got['right'][:,label-1],np.where(r[1:]==label,dg,0).sum(axis=0),rtol=1e-13,atol=1e-11)
            cases.append({'dtype':np.dtype(dtype).str,'samples':ntime,'particles':npart,'pass':True})
    # Validate all four source-linked selected traces without altering their dtype.
    for sf in (2,3,4,5):
        with np.load(DATA/f'trajectory_sf{sf}.npz',allow_pickle=False) as a:
            got=run_array(a['gamma'][:,None],a['regiondata'][:,None],block=257)
            with contextlib.redirect_stdout(io.StringIO()): result=source(a['gamma'][:,None],a['regiondata'][:,None],*SEPARATORS)
            for offset,indices in ((0,result[6]),(3,result[7])):
                assert np.array_equal(got['first_passage'][indices],np.column_stack(result[offset:offset+3]))
    return {'status':'pass','random_and_boundary_cases':cases,'four_source_linked_traces':True,
            'block_boundary_invariance':True,'native_source_arithmetic_exact':True,
            'runtime_seconds':time.perf_counter()-started}


def scalar(x):
    return float(x) if np.isfinite(x) else None


def metrics(values, total):
    finite=np.isfinite(total)&np.isfinite(values); nonzero=finite&(total!=0)
    with np.errstate(divide='ignore',invalid='ignore'):
        ratios=values/total
    return {'particles':len(total),'zero_total_count':int(np.sum(total==0)),
            'negative_total_count':int(np.sum(total<0)),
            'near_zero_total_abs_below_1e_minus_12':int(np.sum(np.abs(total)<1e-12)),
            'nonfinite_ratio_count':int(np.sum(~np.isfinite(ratios))),
            'unfiltered_particle_mean_fraction':scalar(np.mean(ratios)) if len(total) else None,
            'paired_finite_nonzero_particle_mean_fraction':scalar(np.mean(ratios[nonzero])) if np.any(nonzero) else None,
            'paired_finite_nonzero_count':int(nonzero.sum()),
            'aggregate_net_gain_share':scalar(np.sum(values)/np.sum(total)) if len(total) and np.sum(total)!=0 else None,
            'regional_net_gain_sum':float(np.sum(values)), 'total_net_gain_sum':float(np.sum(total)),
            'negative_regional_net_gain_count':int(np.sum(values<0)),
            'positive_per_particle_net_gain_sum':float(np.maximum(values,0).sum()),
            'negative_per_particle_net_gain_sum':float(np.minimum(values,0).sum()),
            'fraction_below_zero_count':int(np.sum(ratios<0)),
            'fraction_above_one_count':int(np.sum(ratios>1))}


def summarize(arrays,mask):
    total=arrays['total_net_gain'][mask]; out={}
    for method in ('first_passage','left','right','symmetric'):
        values=arrays[method][mask]
        names=FP_LABELS if method=='first_passage' else LABELS
        channels={name:values[:,i] for i,name in enumerate(names)}
        if method=='first_passage':
            channels['CS_plus_phase_residual']=values[:,0]+values[:,2]
        else:
            channels['CS_plus_IS1_plus_IS2']=values[:,4]+values[:,0]+values[:,1]
            channels['all_nonDS_including_TB']=values[:,4]+values[:,0]+values[:,1]+values[:,2]
        out[method]={k:metrics(v,total) for k,v in channels.items()}
        if method=='first_passage':
            original_total=values.sum(axis=1)
            out[method]['original_source_mean_DS_using_source_sum_denominator']=metrics(values[:,1],original_total)
        if method in ('left','right'):
            out[method]['gross_recorded_increments']={name:{'positive':float(arrays[method+'_gross_positive'][mask,i].sum()),
              'negative':float(arrays[method+'_gross_negative'][mask,i].sum())} for i,name in enumerate(LABELS)}
    out['diagnostics']={
        'particles':int(mask.sum()),'net_total_min':scalar(total.min()) if len(total) else None,
        'net_total_max':scalar(total.max()) if len(total) else None,
        'region_transition_count':int(arrays['region_transitions'][mask].sum()),
        'transition_L1_net_increment_sum':float(arrays['transition_L1'][mask].sum()),
        'particles_with_CS_after_first_subsequent_DS':int(np.sum(arrays['CS_samples_after_first_subsequent_DS'][mask]>0)),
        'CS_samples_after_first_subsequent_DS':int(arrays['CS_samples_after_first_subsequent_DS'][mask].sum()),
        'CS_entries_after_first_subsequent_DS':int(arrays['CS_entries_after_first_subsequent_DS'][mask].sum()),
        'region_reentries':{name:int(arrays['region_reentries'][mask,i].sum()) for i,name in enumerate(LABELS)},
        'maximum_FP_float32_closure_residual':float(np.max(np.abs(arrays['source_fp_closure_residual'][mask]))) if len(total) else None,
        'maximum_left_closure_residual':float(np.max(np.abs(arrays['left'][mask].sum(axis=1)-total))) if len(total) else None,
        'maximum_right_closure_residual':float(np.max(np.abs(arrays['right'][mask].sum(axis=1)-total))) if len(total) else None}
    return out


def analyze_band(folder, band, entries,block):
    start=time.perf_counter(); validated=[]; source=source_function(); ledger=None
    assert len(entries)==16 and len({e['id'] for e in entries})==16
    assert len({(e['kind'],e['time_batch']) for e in entries})==16
    assert {(e['kind'],e['time_batch']) for e in entries}=={(k,t) for k in ('tracer','region') for t in range(8)}
    sample_g=[];sample_r=[];sample_indices=None
    coordinate_min=np.full(2,np.inf);coordinate_max=np.full(2,-np.inf)
    for chunk in range(8):
        pair={e['kind']:e for e in entries if e['time_batch']==chunk}
        assert set(pair)=={'tracer','region'}
        maps={}
        for kind,e in pair.items():
            path=folder/e['local_relative_path']
            assert path.stat().st_size==e['size'] and file_sha(path)==e['sha256'],str(path)
            maps[kind]=np.load(path,mmap_mode='r',allow_pickle=False)
            assert not maps[kind].dtype.hasobject
            validated.append({'id':e['id'],'size':e['size'],'sha256':e['sha256'],
                'local_relative_path':e['local_relative_path'],'dtype':maps[kind].dtype.str,
                'shape':list(maps[kind].shape)})
        t,r=maps['tracer'],maps['region'];assert t.ndim==3 and t.shape[0]==17 and t.shape[1:]==r.shape
        assert t.dtype==np.float32 and r.dtype==np.float64
        if ledger is None:
            ledger=Ledger(r.shape[1]);sample_indices=np.unique(np.linspace(0,r.shape[1]-1,32,dtype=int))
        assert ledger.n==r.shape[1]
        for j,c in enumerate((1,2)):
            coordinate_min[j]=min(coordinate_min[j],float(t[c].min()))
            coordinate_max[j]=max(coordinate_max[j],float(t[c].max()))
        for i in range(0,r.shape[0],block):
            ledger.consume(t[0,i:i+block,:],r[i:i+block,:],t[3,i:i+block,:])
        sample_g.append(np.asarray(t[0,:,sample_indices]).T.copy())
        sample_r.append(np.asarray(r[:,sample_indices]).copy())
        del maps,t,r
    arrays=ledger.finish();sg=np.concatenate(sample_g,axis=0);sr=np.concatenate(sample_r,axis=0)
    with contextlib.redirect_stdout(io.StringIO()): expected=source(sg,sr,*SEPARATORS)
    for offset,indices in ((0,expected[6]),(3,expected[7])):
        assert np.array_equal(arrays['first_passage'][sample_indices[indices]],np.column_stack(expected[offset:offset+3]))
    g=arrays['final_gamma'];masks={'all_posted':np.ones(len(g),bool),
       'intermediate':(g>SEPARATORS[0])&(g<SEPARATORS[1]),'high':g>SEPARATORS[1]}
    excluded=~(masks['intermediate']|masks['high'])
    result={'batch':band,'particles':len(g),'samples_per_particle':ledger.samples,
      'initial_gamma_range':[float(arrays['initial_gamma'].min()),float(arrays['initial_gamma'].max())],
      'final_gamma_range':[float(g.min()),float(g.max())],
      'strict_band_counts':{k:int(v.sum()) for k,v in masks.items()},
      'excluded_from_both_bands':{'total':int(excluded.sum()),'at_lower_separator':int(np.sum(g==SEPARATORS[0])),
        'at_upper_separator':int(np.sum(g==SEPARATORS[1])),'below_lower_separator':int(np.sum(g<SEPARATORS[0]))},
      'stable_unique_integer_tag_order_verified_all_samples':True,
      'time_order_policy':'Filename t00-t07 order follows the posted loader. Arrays contain no timestamp channel; physical timestamp continuity is not independently verified.',
      'tag_is_identity_not_weight':True,'raw_inputs_verified':validated,
      'coordinate_ranges':{k:[float(coordinate_min[i]),float(coordinate_max[i])] for i,k in enumerate(('x','z'))},
      'tag_range':[int(arrays['tag'].min()),int(arrays['tag'].max())],
      'tag_order_ascending':bool(np.all(np.diff(arrays['tag'])>0)),
      'packed_tag_prefix_13bit_range':[int((arrays['tag']>>13).min()),int((arrays['tag']>>13).max())],
      'exact_native_source_validation':{'selected_indices':sample_indices.tolist(),'particles':len(sample_indices),'pass':True},
      'subsets':{k:summarize(arrays,v) for k,v in masks.items()},'runtime_seconds':time.perf_counter()-start}
    return result,arrays


def write_outputs(records,arrays,checks,provenance):
    results=ROOT/'results';results.mkdir(exist_ok=True)
    overlap=np.intersect1d(arrays['inter_energy']['tag'],arrays['high_energy']['tag'])
    assert len(overlap)==0,'Overlapping IDs prevent the declared pooled comparison; do not deduplicate silently.'
    pooled={k:np.concatenate([arrays[b][k] for b in ('inter_energy','high_energy')],axis=0)
            for k in arrays['inter_energy']}
    pg=pooled['final_gamma']
    pm={'all_posted':np.ones(len(pg),bool),'intermediate':(pg>SEPARATORS[0])&(pg<SEPARATORS[1]),'high':pg>SEPARATORS[1]}
    pe=~(pm['intermediate']|pm['high'])
    records.append({'batch':'released_union','constituent_batches':['inter_energy','high_energy'],
      'particles':len(pg),'samples_per_particle':records[0]['samples_per_particle'],
      'strict_band_counts':{k:int(v.sum()) for k,v in pm.items()},
      'excluded_from_both_bands':{'total':int(pe.sum()),'at_lower_separator':int(np.sum(pg==SEPARATORS[0])),
       'at_upper_separator':int(np.sum(pg==SEPARATORS[1])),'below_lower_separator':int(np.sum(pg<SEPARATORS[0]))},
      'pooling_policy':'Concatenate distinct per-particle histories first, then apply the strict final-gamma cuts; no averaging of folder averages.',
      'stable_unique_integer_tag_order_verified_all_samples':True,
      'subsets':{k:summarize(pooled,v) for k,v in pm.items()}})
    report={'schema_version':1,'status':'pass','scope':'The two released convenience batches, not the full Fig6 population.',
      'weight_policy':'Unit empirical weights for every released particle; conditional on the posted equal-macro-weight deck these also reproduce within-batch physical number weights. No inverse-inclusion weights or representative population claim.',
      'denominator_policy':'All methods compared on identical IDs and A=gamma_final-gamma_initial evaluated in float64 from stored float32 values. Signed gains retained. Unfiltered source behavior and finite/nonzero paired subsets are both reported. Source original FP-sum denominator is separately reported.',
      'precision_policy':'Stored gamma float32 preserved. FP endpoint arithmetic exactly reproduces native upstream float32 operations; full-history increments use float64 subtraction of the same stored samples and float64 accumulation. Neither reconstructs higher-precision Lorentz factors.',
      'region_policy':'Full-history labels IS1,IS2,TB,DS,CS remain separate. Actual CS+IS1+IS2 excludes TB; all-nonDS including TB is separately named. Source CS+phase_residual is an epoch pool and is not renamed local CS+island work.',
      'sensitivity_policy':'Left/right/symmetric are recorded endpoint conventions, not confidence intervals or continuous-work error bounds.',
      'sampling_limits':'Public sample selection/inclusion probabilities are undocumented. No estimate of the omitted intermediate batches, full-population correction, convergence or unbiased uncertainty is inferred.',
      'unbanded_diagnostics_policy':'all_posted evaluates the same chronological phase formula for every released history, including below-cutoff particles, for diagnostics. Only the strict intermediate/high subsets reproduce the source band selection.',
      'main_comparison_cohort':'released_union',
      'implementation':{'analysis_script':'experiments/analyze_public_batches.py','analysis_script_sha256':file_sha(Path(__file__)),
          'numpy_version':np.__version__,'source_excerpt_sha256':PINNED_FUNCTION_SHA,
          'input_manifest_sha256':file_sha(ROOT/provenance)},
      'separators_gamma':list(SEPARATORS),'self_checks':checks,'provenance_manifest':provenance,
      'cross_batch_identity_check':{'overlapping_tag_count':len(overlap),'overlapping_tags':overlap.tolist(),
                                   'batches_kept_separate':True},'batches':records}
    (results/'public-batch-checks.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    flat={f'{band}__{key}':value for band,data in arrays.items() for key,value in data.items()}
    np.savez_compressed(results/'public-batch-per-particle.npz',**flat)
    with (results/'public-batch-per-particle.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.writer(stream);writer.writerow(['released_batch','tag','initial_gamma','final_gamma','A','FP_CS','FP_DS','FP_phase_residual',
          *[f'{method}_{label}' for method in ('left','right','symmetric') for label in LABELS],
          'region_transitions','transition_L1','CS_samples_after_first_subsequent_DS','CS_entries_after_first_subsequent_DS'])
        for band,data in arrays.items():
            for i in range(len(data['tag'])):
                writer.writerow([band,int(data['tag'][i]),float(data['initial_gamma'][i]),float(data['final_gamma'][i]),float(data['total_net_gain'][i]),
                  *data['first_passage'][i].tolist(),*[float(v) for method in ('left','right','symmetric') for v in data[method][i]],
                  int(data['region_transitions'][i]),float(data['transition_L1'][i]),int(data['CS_samples_after_first_subsequent_DS'][i]),int(data['CS_entries_after_first_subsequent_DS'][i])])
    make_figure(records)


def make_figure(records):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':12,'axes.titlesize':12,'axes.labelsize':12,
                         'xtick.labelsize':12,'ytick.labelsize':12})
    display=[r for r in records if r['batch']=='released_union']
    panels=[(r,band,r['subsets'][band]) for r in display for band in ('intermediate','high')
            if r['subsets'][band]['diagnostics']['particles']]
    fig,axes=plt.subplots(1,len(panels),figsize=(5.1*len(panels),4.4),layout='constrained',squeeze=False)
    names=('first_passage','left','symmetric','right');x=np.arange(4)
    for ax,(record,expected,s) in zip(axes[0],panels):
        mean=[s[m]['DS']['unfiltered_particle_mean_fraction'] for m in names]
        share=[s[m]['DS']['aggregate_net_gain_share'] for m in names]
        ax.plot(x,mean,'o-',label='Mean particle fraction',color='#2274a5')
        ax.plot(x,share,'s--',label='Fraction of batch net gain',color='#cf7625')
        ax.set_xticks(x,['First passage','Left','Symmetric','Right'],rotation=12)
        ax.set_ylabel('Downstream signed net-gain fraction')
        ax.set_title(f"Available {expected} histories (n={s['diagnostics']['particles']})")
        ax.axhline(.5,color='#888',lw=.7,ls=':');ax.grid(alpha=.2);ax.legend(fontsize=11)
    fig.suptitle('Released convenience batches: paired attribution and averaging conventions\nUnit empirical weights; no population estimate or confidence interval',fontsize=11)
    folder=ROOT/'figures';folder.mkdir(exist_ok=True)
    fig.savefig(folder/'public-batch-comparison.png',dpi=200);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cohort-dir',type=Path)
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--time-block',type=int,default=256)
    args=parser.parse_args();assert args.time_block>0
    checks=self_checks()
    if args.cohort_dir is None:
        print(json.dumps(checks,indent=2));return
    provenance=json.loads((DATA/'released-cohort-inventory.json').read_text(encoding='utf-8'))
    records=[];allarrays={}
    for band in ('inter_energy','high_energy'):
        print('Analyzing',band,flush=True)
        record,arrays=analyze_band(args.cohort_dir,band,[e for e in provenance['files'] if e['released_batch']==band],args.time_block)
        records.append(record);allarrays[band]=arrays
    write_outputs(records,allarrays,checks,'data/upstream-cc0/released-cohort-inventory.json')
    print(json.dumps({'status':'pass','batches':[(r['batch'],r['particles'],r['samples_per_particle']) for r in records]},indent=2))


if __name__=='__main__':
    main()
