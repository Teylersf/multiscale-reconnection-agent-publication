## Deposited first-passage routine

The following is the complete unmodified function at lines 344-403 of the
December 6, 2025 version-1 OSF file `python_scripts/tracer_functions.py` [2].
The parent file SHA-256 is
`3f93e1685dd9664e279f8b14535d4ebc6ba2946442e4831f4eaf24db315d61ba`;
the exact 60-line excerpt SHA-256 is
`2909f9e6acec3c48f3838e86c15ffd18a9563dc57984e400b0baadd22f16655f`.
Its CC0 provenance, stable file identifiers and numeric-fixture conversions
are recorded in the reproducibility package. The original routine expects
NumPy as `np` and a `tqdm` iterator in its surrounding module; the audit harness
supplies these without executing the original module's top-level I/O.
Line labels in the typeset listing refer to the parent-file line numbers.

```
def get_energy_by_region_w_bands(gamma_data,region_data,separator1,separator2): # separator 1, 2 interms of gamma, not gamma-1
    npart = len(gamma_data[0,:])
    dgamma_cs_1 = np.zeros(npart)
    dgamma_ds_1 = np.zeros(npart)
    dgamma_isls_1 = np.zeros(npart)
    dgamma_cs_2 = np.zeros(npart)
    dgamma_ds_2 = np.zeros(npart)
    dgamma_isls_2 = np.zeros(npart)
    idx_1 = np.array([], dtype=int)
    idx_2 = np.array([], dtype=int)
    
    for i in tqdm(range(npart), desc="Processing particles"):
        gamma = gamma_data[:,i]
        region = region_data[:,i]


        if gamma[-1] < separator2 and gamma[-1] > separator1 :
            idx_1 = np.append(idx_1,int(i))
            # Now check if transits current sheet
            if len(np.where(region[:]==5)[0]) > 0:
                cs1 = np.where(region[:]==5)[0][0]
                cs_last = np.where(region[:]==5)[0][-1]
                if len(np.where(region[cs1 + 1:]==4)[0]) > 0:
                    ds1 = np.where(region[cs1 + 1:]==4)[0][0] + cs1+1
                    dgamma_cs_1[i] = gamma[ds1] - gamma[cs1]
                    dgamma_ds_1[i] = gamma[-1] - gamma[ds1]
                    dgamma_isls_1[i] = gamma[cs1] - gamma[0]
                else:
                    dgamma_cs_1[i] = gamma[cs_last]-gamma[cs1]
                    dgamma_isls_1[i] = gamma[cs1] - gamma[0] + (gamma[-1]-gamma[cs_last])
            elif len(np.where(region[:]==4)[0]) > 0:
                ds1 = np.where(region[:]==4)[0][0]
                dgamma_ds_1[i] = gamma[-1] - gamma[ds1]
                dgamma_isls_1[i] = gamma[ds1] - gamma[0]
            else:
                dgamma_isls_1[i] = gamma[-1] - gamma[0]
                print(i)
        elif gamma[-1] > separator2: 
            idx_2 = np.append(idx_2,int(i))
            # Now check if transits current sheet
            if len(np.where(region[:]==5)[0]) > 0:
                cs1 = np.where(region[:]==5)[0][0]
                cs_last = np.where(region[:]==5)[0][-1]
                if len(np.where(region[cs1 + 1:]==4)[0]) > 0:
                    ds1 = np.where(region[cs1 + 1:]==4)[0][0] + cs1+1
                    dgamma_cs_2[i] = gamma[ds1] - gamma[cs1]
                    dgamma_ds_2[i] = gamma[-1] - gamma[ds1]
                    dgamma_isls_2[i] = gamma[cs1] - gamma[0]
                else:
                    dgamma_cs_2[i] = gamma[cs_last]-gamma[cs1]
                    dgamma_isls_2[i] = gamma[cs1] - gamma[0] + (gamma[-1]-gamma[cs_last])
            elif len(np.where(region[:]==4)[0]) > 0:
                ds1 = np.where(region[:]==4)[0][0]
                dgamma_ds_2[i] = gamma[-1] - gamma[ds1]
                dgamma_isls_2[i] = gamma[ds1] - gamma[0]
            else:
                dgamma_isls_2[i] = gamma[-1] - gamma[0]
                print(i)

    return dgamma_cs_1[idx_1], dgamma_ds_1[idx_1], dgamma_isls_1[idx_1],dgamma_cs_2[idx_2], dgamma_ds_2[idx_2], dgamma_isls_2[idx_2],idx_1,idx_2
```

The unused `cs_last` value in the downstream branch does not alter that
branch's first-passage definition. Branches for no subsequent downstream
visit and no sheet visit are preserved here; they are not replaced by the
simplified two-passage formula used in the main counterexample. The
routine's exact threshold comparisons and original return ordering are
also retained. Printing this later deposited version does not establish
that these exact source bytes were executed before the v1 preprint.
