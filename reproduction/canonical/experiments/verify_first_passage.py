"""Portable checks of first-passage versus recorded-history energy attribution.

Run from any directory with Python and NumPy. Matplotlib creates the scientific
figure unless --no-figure is supplied. All default inputs are inside this repo;
NPZ fixtures are read with allow_pickle=False. No network or author PIC run.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/upstream-cc0'
RESULTS=ROOT/'results'
FIGURES=ROOT/'figures'
LABELS={1:'IS1',2:'IS2',3:'TB',4:'DS',5:'CS'}
SEPARATORS=(5.77,16.40)
PRINTED={8:{'CS':2.33,'DS':4.26},9:{'CS':0.,'DS':14.01},
         10:{'CS':64.49,'DS':30.80},11:{'CS':3.51,'DS':47.34}}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load_verified_inputs():
    manifest=json.loads((DATA/'provenance.json').read_text(encoding='utf-8'))
    inputs={}
    for item in manifest['files']:
        path=ROOT/item['local_file']
        if not path.resolve().is_relative_to(ROOT):
            raise ValueError('Fixture path leaves repository')
        raw=path.read_bytes()
        if len(raw)!=item['local_bytes'] or sha(raw)!=item['local_sha256']:
            raise ValueError('Fixture digest mismatch: '+item['local_file'])
        if item['kind']=='numeric_trajectory_fixture':
            with np.load(path,allow_pickle=False) as arrays:
                if set(arrays.files)!=set(item['arrays']):
                    raise ValueError('Unexpected fixture keys')
                values={key:arrays[key].copy() for key in arrays.files}
            for key,a in values.items():
                expected=item['arrays'][key]
                if (a.dtype.hasobject or a.dtype.str!=expected['dtype'] or list(a.shape)!=expected['shape']
                        or sha(a.tobytes(order='C'))!=expected['c_order_values_sha256']):
                    raise ValueError('Numeric conversion mismatch: '+item['local_file']+'/'+key)
            inputs[item['mapped_arxiv_v1_figure']]=values
        elif item['kind']=='exact_function_excerpt':
            # Execute only this already inspected function definition, not the
            # original script with top-level imports, data loading and plotting.
            tree=ast.parse(raw.decode('utf-8'))
            if len(tree.body)!=1 or not isinstance(tree.body[0],ast.FunctionDef):
                raise ValueError('Unexpected upstream excerpt syntax')
            if tree.body[0].name!='get_energy_by_region_w_bands':
                raise ValueError('Unexpected upstream function')
            namespace={'np':np,'tqdm':lambda iterable,**kwargs:iterable}
            exec(compile(tree,str(path),'exec'),namespace)
            supplied=namespace[tree.body[0].name]
    if set(inputs)!={8,9,10,11}:
        raise ValueError('Expected four selected original-figure traces')
    return supplied,inputs,manifest

def first_passage(supplied,gamma,regions):
    output=supplied(np.asarray(gamma)[:,None],np.asarray(regions,dtype=int)[:,None],*SEPARATORS)
    band='intermediate' if SEPARATORS[0]<gamma[-1]<SEPARATORS[1] else 'high'
    offset=0 if band=='intermediate' else 3
    if any(len(output[offset+i])!=1 for i in range(3)):
        raise ValueError('Trace does not satisfy one of the requested final-energy bands')
    return band,{name:float(output[offset+i][0]) for i,name in enumerate(('CS','DS','islands'))}

def recorded_history(gamma,regions):
    g=np.asarray(gamma,dtype=np.float64)
    r=np.asarray(regions,dtype=int)
    if g.ndim!=1 or r.shape!=g.shape or not set(np.unique(r)).issubset(LABELS):
        raise ValueError('Invalid trace shape or region labels')
    dg=np.diff(g)
    left={name:float(dg[r[:-1]==label].sum(dtype=np.float64)) for label,name in LABELS.items()}
    right={name:float(dg[r[1:]==label].sum(dtype=np.float64)) for label,name in LABELS.items()}
    bounds={}
    for label,name in LABELS.items():
        a=dg*((r[1:]==label).astype(int)-(r[:-1]==label).astype(int))
        lower=left[name]+float(np.minimum(a,0).sum())
        upper=left[name]+float(np.maximum(a,0).sum())
        bounds[name]={'lower':lower,'upper':upper,'endpoint_difference_bound':float(np.abs(a).sum()),
                      'midpoint':(left[name]+right[name])/2}
        assert lower-1e-10<=left[name]<=upper+1e-10
        assert lower-1e-10<=right[name]<=upper+1e-10
    total=float(g[-1]-g[0])
    assert np.isclose(sum(left.values()),total,rtol=1e-12,atol=1e-10)
    assert np.isclose(sum(right.values()),total,rtol=1e-12,atol=1e-10)
    transitions=r[1:]!=r[:-1]
    return {'left_endpoint':left,'right_endpoint':right,'total_net_gain':total,
            'region_transition_count':int(transitions.sum()),
            'L1_net_increment_at_region_transitions':float(np.abs(dg[transitions]).sum()),
            'endpoint_allocation_bounds':bounds}

def synthetic_checks(supplied):
    histories=[
      ('monotone_control_intermediate',[1.1,1.1,2.1,2.1,12.1,12.1],[1,5,5,4,4,4]),
      ('monotone_control_high',[1.1,1.1,11.1,11.1,111.1,111.1],[1,5,5,4,4,4]),
      ('reentry_intermediate',[1.1,1.1,1.2,1.2,1.3,1.3,11.3,11.3],[1,5,5,4,4,5,5,4]),
      ('reentry_high',[1.1,1.1,2.1,2.1,3.1,3.1,103.1,103.1],[1,5,5,4,4,5,5,4]),
      ('early_DS_intermediate',[1.1,1.1,6.1,6.1,6.2,6.2,6.3],[1,4,4,5,5,4,4]),
      ('early_DS_high',[1.1,1.1,51.1,51.1,52.1,52.1,53.1],[1,4,4,5,5,4,4]),
    ]
    records=[]
    for name,g,r in histories:
        band,fp=first_passage(supplied,g,r)
        full=recorded_history(g,r)
        boundary=[g[i+1]-g[i] for i in range(len(g)-1) if r[i+1]!=r[i]]
        assert all(x==0 for x in boundary),'Synthetic transition work must vanish'
        assert np.isclose(sum(fp.values()),full['total_net_gain'],rtol=1e-12,atol=1e-12)
        assert all(np.isclose(full['left_endpoint'][k],full['right_endpoint'][k]) for k in LABELS.values())
        local={'CS':full['left_endpoint']['CS'],'DS':full['left_endpoint']['DS'],
               'islands':full['left_endpoint']['IS1']+full['left_endpoint']['IS2']+full['left_endpoint']['TB']}
        matches=all(np.isclose(fp[k],local[k],rtol=1e-12,atol=1e-12) for k in fp)
        assert matches==name.startswith('monotone_control')
        if name.startswith('reentry'):
            assert fp['DS']>fp['CS'] and local['CS']>local['DS']
        records.append({'case':name,'band':band,'gamma':g,'regions':r,'first_passage':fp,
                        'recorded_history':full,'zero_transition_increments':True,
                        'matches_recorded_history':matches})
    return records

def selected_trace_checks(supplied,inputs):
    records=[]
    for figure,data in sorted(inputs.items()):
        source_gamma=data['gamma']
        gamma=source_gamma.astype(np.float64)
        r=data['regiondata'].astype(int)
        assert np.array_equal(r,data['regiondata'])
        band,fp=first_passage(supplied,source_gamma,r)
        full=recorded_history(gamma,r)
        rounded={k:round(fp[k],2) for k in ('CS','DS')}
        assert rounded==PRINTED[figure],f'Original figure {figure} label reproduction failed'
        cs=np.flatnonzero(r==5)
        ds=np.flatnonzero(r==4)
        first_cs=int(cs[0]) if len(cs) else None
        ds_after=ds[ds>first_cs] if first_cs is not None else ds
        first_ds=int(ds_after[0]) if len(ds_after) else None
        dg=np.diff(gamma); t=np.arange(len(dg))
        after_mask=((r[:-1]==5)&(r[1:]==5)&(t>=first_ds)) if first_ds is not None else np.zeros(len(dg),bool)
        records.append({'original_figure':figure,'samples':len(gamma),'band':band,
          'initial_gamma':float(gamma[0]),'final_gamma':float(gamma[-1]),
          'first_passage':fp,'printed_CS_DS':PRINTED[figure],
          'matches_all_printed_CS_DS_values_at_2dp':True,'recorded_history':full,
          'CS_labelled_samples_after_first_DS':int(np.sum(r[first_ds+1:]==5)) if first_ds is not None else 0,
          'same_label_CS_net_gain_after_first_DS':float(dg[after_mask].sum())})
    return records

def plot_evidence(synthetic,selected):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    colors={'CS':'#cf7625','DS':'#2274a5','IS':'#858d93'}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'svg.fonttype':'none'})
    fig=plt.figure(figsize=(11,7.2),layout='constrained')
    grid=fig.add_gridspec(2,2,height_ratios=[1,1.08])
    ax=fig.add_subplot(grid[0,:])
    case=next(x for x in synthetic if x['case']=='reentry_intermediate')
    gamma=case['gamma']; regions=case['regions']
    for i,label in enumerate(regions[:-1]):
        color=colors['CS' if label==5 else ('DS' if label==4 else 'IS')]
        ax.axvspan(i,i+1,color=color,alpha=.15,lw=0)
    ax.plot(range(len(gamma)),gamma,'o-',color='#222222',lw=1.8,ms=4)
    ax.axvline(3,color=colors['DS'],ls='--',lw=1)
    ax.text(3.08,10.0,'First downstream entry',color=colors['DS'],fontsize=9)
    ax.text(5.12,6.6,r'$\Delta\gamma=10$ in CS',color=colors['CS'],fontsize=10)
    ax.set(xlabel='Recorded sample',ylabel=r'$\gamma$',xlim=(-.1,7.1),ylim=(.7,12.5),
           title='(a) A synthetic return to the primary sheet; zero gain at region transitions')
    ax.legend(handles=[Patch(facecolor=colors['IS'],alpha=.3,label='Islands'),
                       Patch(facecolor=colors['CS'],alpha=.3,label='Primary sheet (CS)'),
                       Patch(facecolor=colors['DS'],alpha=.3,label='Downstream (DS)')],
              frameon=False,ncol=3,loc='upper left')
    ax=fig.add_subplot(grid[1,0])
    x=np.arange(2);width=.3
    fp=case['first_passage']; local=case['recorded_history']['left_endpoint']
    cs=[fp['CS'],local['CS']];ds=[fp['DS'],local['DS']]
    ax.bar(x-width/2,cs,width,color=colors['CS'],label='CS')
    ax.bar(x+width/2,ds,width,color=colors['DS'],label='DS')
    for pos,value in zip(x-width/2,cs):ax.text(pos,value+.22,f'{value:.1f}',ha='center',fontsize=10)
    for pos,value in zip(x+width/2,ds):ax.text(pos,value+.22,f'{value:.1f}',ha='center',fontsize=10)
    ax.set(xticks=x,xticklabels=['First-passage\nfunction','Recorded full\nregion history'],
           ylabel=r'Attributed net $\Delta\gamma$',ylim=(0,11.8),
           title='(b) Same total gain, reversed allocation')
    ax.legend(frameon=False,ncol=2,loc='upper center')
    ax=fig.add_subplot(grid[1,1])
    positions=np.arange(4)
    fp_values=[];left=[];right=[]
    for row in selected:
        total=row['recorded_history']['total_net_gain']
        fp_values.append(row['first_passage']['DS']/total)
        left.append(row['recorded_history']['left_endpoint']['DS']/total)
        right.append(row['recorded_history']['right_endpoint']['DS']/total)
    for i,l,r in zip(positions,left,right):ax.plot([i,i],[l,r],color='#a2a2a2',lw=2,zorder=1)
    ax.scatter(positions-.06,fp_values,c='#222222',marker='o',label='First passage',zorder=4,s=35)
    ax.scatter(positions,left,c=colors['CS'],marker='<',label='Left endpoint',zorder=3,s=40)
    ax.scatter(positions+.06,right,c=colors['DS'],marker='>',label='Right endpoint',zorder=3,s=40)
    ax.axhline(1,color='#aaaaaa',lw=.8,ls=':')
    ax.set(xticks=positions,xticklabels=[f'Fig. {r["original_figure"]}' for r in selected],
           ylabel='DS net gain / total net gain',ylim=(.15,1.3),
           title='(c) Four deposited illustrative traces')
    ax.legend(frameon=False,fontsize=8,loc='lower right')
    ax.text(.02,.98,'Endpoint choices, not confidence intervals',transform=ax.transAxes,
            ha='left',va='top',fontsize=8,color='#555555')
    FIGURES.mkdir(exist_ok=True)
    path=FIGURES/'first-passage-attribution.png'
    fig.savefig(path,dpi=200,facecolor='white',metadata={'Title':'First-passage versus recorded-history energy attribution',
                 'Author':'Taylor Kalin','Description':'Synthetic counterexample and four selected deposited traces; no population-bias inference.'})
    plt.close(fig)
    return {'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-figure',action='store_true',help='Run numerical checks without importing Matplotlib.')
    args=parser.parse_args()
    supplied,inputs,provenance=load_verified_inputs()
    synthetic=synthetic_checks(supplied)
    selected=selected_trace_checks(supplied,inputs)
    example_gains=np.array([5.,5.,15.]);example_fractions=np.array([1.,1.,0.])
    mean_fraction=float(np.mean(example_fractions))
    weighted=float(np.sum(example_gains*example_fractions)/np.sum(example_gains))
    assert mean_fraction>.5>weighted
    result={'schema_version':1,'python_version':sys.version.split()[0],'numpy_version':np.__version__,
      'input_provenance_file':'data/upstream-cc0/provenance.json',
      'upstream_function_parent_sha256':next(x['upstream']['hashes']['sha256'] for x in provenance['files'] if x['kind']=='exact_function_excerpt'),
      'band_separators_gamma':list(SEPARATORS),'synthetic_cases':synthetic,'selected_traces':selected,
      'mean_fraction_example':{'energy_gains':example_gains.tolist(),'DS_fractions':example_fractions.tolist(),
           'particle_mean_fraction':mean_fraction,'energy_weighted_fraction':weighted},
      'checks':{'fixture_and_numeric_array_hashes':True,'both_band_branches_tested':True,
         'monotone_positive_controls_pass':True,'zero_transition_reentry_counterexamples_pass':True,
         'all_eight_original_figure_labels_reproduced':True,'recorded_history_telescoping_closure':True,
         'endpoint_net_allocation_bounds_checked':True,'numeric_only_default_fixture_loading':True},
      'scope':['Four author-selected traces, not a representative cohort.',
         'Left/right recorded-history estimates are sampling conventions, not exact continuous crossing-time work.',
         'Endpoint net-allocation bounds assume allocation of each interval net increment between its endpoint regions; they are not certified physical-work bounds.',
         'No full-cohort bias, sign of published mean change, PIC rerun or headline reversal is established.']}
    if not args.no_figure:result['figure']=plot_evidence(synthetic,selected)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS/'first-passage-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'all_checks_pass':all(result['checks'].values()),'synthetic_cases':len(synthetic),
          'selected_traces':len(selected),'printed_values_reproduced':8,'figure':result.get('figure')}))

if __name__=='__main__':main()
