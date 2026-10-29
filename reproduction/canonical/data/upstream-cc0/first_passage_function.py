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
