"""Portable bounded arithmetic checks for the methods comment.

Run from a checkout: python experiments/verify_analytic_checks.py
No network, external cache, source-script execution, or plasma simulation.
The analytic proofs are in the manuscript; these small checks corroborate them.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform

import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def fadeev(x,z,epsilon=.4,printed=False):
    f=np.cosh(z)+epsilon*np.cos(x)
    return np.array([np.sinh(x if printed else z)/f,
                     np.sqrt(1-epsilon**2)/f,epsilon*np.sin(x)/f])


def sheet(x,z,force_free=True,guide=1.):
    by=np.sqrt(1/np.cosh(z)**2+guide**2) if force_free else guide+0*z
    return np.array([np.tanh(z),by,0*z])


def differentiate(fun,x,z):
    h=1e-28
    dx=np.imag(fun(x+1j*h,z))/h
    dz=np.imag(fun(x,z+1j*h))/h
    return float(dx[0]+dz[2]),np.array([-dz[1],dz[0]-dx[2],dx[1]])


def local(g,r):
    dg=np.diff(g)
    left=np.bincount(r[:-1],weights=dg,minlength=6)
    right=np.bincount(r[1:],weights=dg,minlength=6)
    assert np.isclose(left.sum(),g[-1]-g[0])
    assert np.isclose(right.sum(),g[-1]-g[0])
    return left,right


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'results/analytic-checks.json')
    args=parser.parse_args()

    # Ancillary analytic field identities in B0=L=1 units.
    divs,forces,norms=[],[],[]
    for x in np.linspace(-math.pi,math.pi,11):
        for z in np.linspace(-2,2,9):
            b=fadeev(x,z);div,curl=differentiate(fadeev,x,z)
            f=math.cosh(z)+.4*math.cos(x)
            alpha=math.sqrt(1-.4**2)/f
            divs.append(abs(div));forces.append(float(np.linalg.norm(curl-alpha*b)))
            norms.append(abs(float(b@b)-(math.cosh(z)-.4*math.cos(x))/f))
    assert max(divs+forces+norms)<5e-14
    printed_div,_=differentiate(lambda x,z:fadeev(x,z,printed=True),0,0)
    assert math.isclose(printed_div,5/7,rel_tol=1e-14)
    z_force=math.atanh(1/math.sqrt(3))
    _,curl=differentiate(lambda x,z:sheet(x,z,force_free=False),0,z_force)
    uniform_force=np.cross(curl,sheet(0,z_force,force_free=False))
    assert math.isclose(uniform_force[2],-2/(3*math.sqrt(3)),rel_tol=1e-14)
    guide_res=max(float(np.linalg.norm(np.cross(differentiate(sheet,0,z)[1],sheet(0,z))))
                  for z in np.linspace(-4,4,101))
    assert guide_res<1e-14

    # Epoch versus full-history attribution with zero transition increments.
    r=np.array([1,5,5,4,4,5,5,4])
    g=np.array([2.,2.,3.,3.,4.,4.,104.,104.])
    a=int(np.flatnonzero(r==5)[0]);b=int(np.flatnonzero((r==4)&(np.arange(len(r))>a))[0])
    fp={'CS':float(g[b]-g[a]),'DS':float(g[-1]-g[b]),'initial':float(g[a]-g[0])}
    left,right=local(g,r)
    assert np.array_equal(left,right)
    assert fp['CS']==1 and fp['DS']==101 and left[5]==101 and left[4]==1
    assert sum(fp.values())==102 and left.sum()==102
    assert np.all(np.diff(g)[r[:-1]!=r[1:]]==0)
    bias=float(np.sum((1-(r[b:-1]==4))*np.diff(g)[b:])
               -np.sum((r[:b]==4)*np.diff(g)[:b]))
    assert bias==fp['DS']-left[4]==100
    # Ordered one-pass positive control.
    gc=np.array([2.,2.,3.,3.,104.,104.]);rc=np.array([1,5,5,4,4,4])
    control,_=local(gc,rc)
    assert control[5]==gc[3]-gc[1] and control[4]==gc[-1]-gc[3]

    # Sharp per-region allocation range. Aggregate L/U are not its extrema.
    gr=np.array([10.,12.,15.,11.,10.]);rr=np.array([4,5,4,5,4])
    dg=np.diff(gr);lr,ur=local(gr,rr)
    lchi=np.eye(6)[rr[:-1]].T;rchi=np.eye(6)[rr[1:]].T
    a_coeff=(rchi-lchi)*dg
    B=np.abs(a_coeff).sum(axis=1)
    lower=lr+np.minimum(a_coeff,0).sum(axis=1)
    upper=lr+np.maximum(a_coeff,0).sum(axis=1)
    endpoint_T=float(np.abs(dg[rr[:-1]!=rr[1:]]).sum())
    allocations=[]
    for theta in itertools.product((0.,1.),repeat=len(dg)):
        h=(lchi+(rchi-lchi)*np.array(theta))@dg
        assert np.isclose(h.sum(),gr[-1]-gr[0])
        assert np.all(h>=lower-1e-14) and np.all(h<=upper+1e-14)
        allocations.append(h)
    allocations=np.array(allocations)
    assert np.allclose(allocations.min(axis=0),lower)
    assert np.allclose(allocations.max(axis=0),upper)
    assert np.allclose((lower+upper)/2,(lr+ur)/2)
    assert np.allclose(upper-lower,B)
    for h in allocations:
        for other in allocations:
            assert np.max(np.abs(h-other))<=endpoint_T+1e-14
            assert np.sum(np.abs(h-other))<=2*endpoint_T+1e-14
    assert lr[4]==-2 and ur[4]==2 and lower[4]==-5 and upper[4]==5

    # Coarse equal endpoints conceal a gain in C and equal loss in D.
    hidden_gain=7.
    fine_g=np.array([2.,2.,2.+hidden_gain,2.+hidden_gain,2.])
    fine_r=np.array([4,5,5,4,4])
    resolved,_=local(fine_g,fine_r)
    coarse_g=fine_g[[0,-1]];coarse_r=fine_r[[0,-1]]
    coarse,_=local(coarse_g,coarse_r)
    coarse_T=float(np.abs(np.diff(coarse_g)[coarse_r[:-1]!=coarse_r[1:]]).sum())
    assert coarse_T==0 and coarse.sum()==0 and resolved[5]==7 and resolved[4]==-7

    # Particle-mean versus energy-share identity, with an in-band example.
    A=np.array([5.,5.,15.]);fractions=np.array([1.,1.,0.])
    mean=float(fractions.mean());energy_share=float((A*fractions).sum()/A.sum())
    covariance=float(np.mean((A-A.mean())*(fractions-fractions.mean())))
    assert np.isclose(energy_share,mean+covariance/A.mean())
    assert mean>.5 and energy_share<.5
    final_gamma=1.1+A
    assert np.all((final_gamma>5.77)&(final_gamma<16.4))
    w=np.array([1.,2.,4.]);mu=lambda x:float(np.dot(w,x)/w.sum())
    weighted_cov=mu((A-mu(A))*(fractions-mu(fractions)))
    weighted_energy=mu(A*fractions)/mu(A)
    assert np.isclose(weighted_energy,mu(fractions)+weighted_cov/mu(A))
    signed=np.array([-2.,7.])
    assert signed.sum()==5 and np.maximum(signed,0).sum()==7

    # Standard diagnostic identity: normalized c=1 units.
    v=np.array([.2,0.,0.]);mag=np.array([0.,0.,1.]);j=np.array([0.,.3,0.])
    electric=-np.cross(v,mag);gamma=1/math.sqrt(1-float(v@v))
    de=gamma*float(j@(electric+np.cross(v,mag)))
    lab_work=float(j@electric)
    assert de==0 and np.isclose(lab_work,.06)
    gamma_f=1.25;p_f=math.sqrt(gamma_f**2-1)
    pair_kinetic_gain=2*(gamma_f-1);pair_de=p_f**2
    assert pair_kinetic_gain==.5 and pair_de==.5625

    report={
        'scope':'Small analytic and finite-array checks; no source simulation or cohort reconstruction.',
        'groups':{
            'corrected_equilibrium':{'passed':True,'units':'B0=L=1',
                'printed_divergence_at_origin':printed_div,'corrected_max_divergence_residual':max(divs),
                'corrected_max_curl_minus_alpha_B_residual':max(forces),
                'corrected_max_B_squared_identity_residual':max(norms),
                'B_squared_range_epsilon04':[3/7,7/3]},
            'guide_profile':{'passed':True,'uniform_replacement_curl_cross_B_witness':uniform_force.tolist(),
                'posted_force_free_profile_max_curl_cross_B_residual':guide_res,
                'historical_execution_inferred':False},
            'first_passage':{'passed':True,'source_code_executed':False,
                'first_passage':fp,'full_history_CS':float(left[5]),'full_history_DS':float(left[4]),
                'total_gain':102.,'transition_increments_zero':True,'exact_DS_discrepancy':bias,
                'one_pass_control_passed':True},
            'discrete_allocations':{'passed':True,'exhaustive_allocations':len(allocations),
                'DS_left':float(lr[4]),'DS_right':float(ur[4]),'DS_attainable_net_range':[float(lower[4]),float(upper[4])],
                'DS_B_R':float(B[4]),'T_endpoint':endpoint_T,'closure_for_every_allocation':True,
                'is_continuous_physical_work_bound':False},
            'unresolved_excursion':{'passed':True,'coarse_T_endpoint':coarse_T,
                'coarse_CS':float(coarse[5]),'coarse_DS':float(coarse[4]),
                'fine_visit_CS':float(resolved[5]),'fine_visit_DS':float(resolved[4]),
                'interpretation':'Zero endpoint diagnostic does not bound unresolved regional work.'},
            'estimands':{'passed':True,'particle_gains':A.tolist(),'DS_particle_fractions':fractions.tolist(),
                'final_gamma_all_in_intermediate_band':final_gamma.tolist(),'number_mean':mean,
                'energy_share':energy_share,'population_covariance':covariance,
                'weighted_number_mean':mu(fractions),'weighted_energy_share':weighted_energy,
                'weighted_covariance':weighted_cov},
            'signed_gains':{'passed':True,'regional_net_gains':signed.tolist(),
                'total_net_gain':5.,'sum_after_clipping_negative':7.,'clipping_preserves_closure':False},
            'standard_nonideal_work_identity':{'passed':True,'c1_ideal_motional_De':float(de),
                'c1_ideal_motional_J_dot_E':lab_work,
                'cold_pair_electric_energy_loss':.5,'cold_pair_kinetic_energy_gain':pair_kinetic_gain,
                'cold_pair_integrated_De':pair_de,'cold_pair_magnetic_energy_loss':0.,
                'is_source_reconnection_result':False},
        },
        'all_checks_passed':True,
        'limitations':['Array identities do not identify an exact historical source executable.',
            'No full-cohort bias, sign, headline reversal or continuous-work uncertainty is inferred.',
            'Velocity-file producer semantics are not verified by this analytic script.'],
        'producer':{'path':'experiments/verify_analytic_checks.py',
            'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'python':platform.python_version(),'numpy':np.__version__},
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'all_checks_passed':True,'groups':len(report['groups']),
                      'output':str(args.output),'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
