import numpy as np
try:
    import coloredlogs, logging
    coloredlogs.install(level='WARNING')
except ImportError:
    import logging
def setup():
    from pyal2.c3s.c3s_al2_runner import C3SAl2Runner
    runner = C3SAl2Runner()
    from pyal2.c3s.c3s_data_manager import C3SDataManager
    dm=C3SDataManager('config/acf.c3s', 'config/pcf.c3s',startseries=True, 
                      dates=['2001-02-05','2003-12-25'])
    runner.setup(dm)
    return runner, dm

def test_2():
    dates = dm['dates']
    dates
    ts = None
    #runner.debuglevel = 10000
    for idate, date in enumerate(dates[:]):
        #print('runner.current_startseries' , runner.current_startseries)
        runner.process(xslice=slice(25,26), yslice=slice(25,26), dates=[date])
        nbands = runner.brdf.shape[2]
        #print(str(date) + ' instant new old')
        #for i in [0,1,2]:
        #    print(str(date) + '    k' + str(i) + ' ' + ' ' + str(runner.brdf[0,0,0,i])+ ' ' + str(runner.brdf1[0,0,0,i])+ ' ' + str(runner.brdf_in[0,0,0,i]))
        #    print(str(date) + ' covk' + str(i) + ' ' + ' ' + str(runner.covariance[0,0,0,i,i])+ ' ' + str(runner.covariance1[0,0,0,i,i])+ ' ' + str(runner.covariance_in[0,0,0,i,i]))
        print(runner.outalbedos_age)
        for iband in range(0,nbands):
            for i in [0,1,2]:            
                if ts is None : ts = np.zeros((20, len(dates),nbands,3))
                ts[0,idate,iband,i] = runner.brdf[0,0,0,i]
                ts[1,idate,iband,i] = runner.brdf1[0,0,0,i]
                ts[2,idate,iband,i] = runner.brdf_in[0,0,0,i]
                ts[3,idate,iband,i] = runner.covariance[0,0,0,i,i]
                ts[4,idate,iband,i] = runner.covariance1[0,0,0,i,i]
            ts[5,idate,iband] = runner.age_obs_in[0,0,iband]
            ts[6,idate,iband] = runner.age[0,0,iband]
        for i in [0,1]:
            for j in [0,1]: # should be more
                ts[10,idate,i,j] = runner.outalbedos[0,0,i,j]
                ts[11,idate,i,j] = runner.outalbedos_cov[0,0,i,j]                
                
                
                #aa = runner.outalbedos_age[i,j]
                
                ts[12,idate,i,j] = runner.outalbedos_age[0,0]
                ts[13,idate,i,j] = runner.age_obs_in[0,0,j]
                ts[14,idate,i,j] = runner.age[0,0,i]                
                
                ts[15,idate,i,j] = runner.outalbedos_quality[0,0]
                ts[16,idate,i,j] = runner.quality_in[0,0,i]
                ts[17,idate,i,j] = runner.quality1[0,0,i]
                ts[18,idate,i,j] = runner.quality[0,0,i]
                
    return runner, ts

runner, dm = setup()
runner, ts = test_2()

# f, ax = plot_now(runner, f=f, ax=ax)
