import numpy as np
try:
    import coloredlogs, logging
    coloredlogs.install(level='WARNING')
except ImportError:
    import logging
def setup():
    from pyal2.msg.msg_al2_runner import MSGAl2Runner
    runner = MSGAl2Runner()
    from pyal2.msg.msg_data_manager import MSGDataManager
    dm=MSGDataManager('config/acf.msg', 'config/pcf.msg.genericdate',startseries=True, 
                      dates=['2016-08-01','2016-08-02'])
    runner.setup(dm)
    return runner, dm

def test_2():
    dates = dm['dates']
    dates
    ts = None
    #runner.debuglevel = 10000
    for idate, date in enumerate(dates[:]):
        print('runner.current_startseries' , runner.current_startseries)
        runner.process(xslice=slice(311,312), yslice=slice(2049,2050), dates=[date])
        nbands = runner.brdf.shape[2]
        print(str(date) + ' instant new old')
        for i in [0,1,2]:
            print(str(date) + '    k' + str(i) + ' ' + ' ' + str(runner.brdf[0,0,0,i])+ ' ' + str(runner.brdf1[0,0,0,i])+ ' ' + str(runner.brdf_in.data[0,0,0,i]))
            print(str(date) + ' covk' + str(i) + ' ' + ' ' + str(runner.covariance[0,0,0,i,i])+ ' ' + str(runner.covariance1[0,0,0,i,i])+ ' ' + str(runner.covariance_in.data[0,0,0,i,i]))
        for i in [0,1,2]:
            for iband in range(0,nbands):
                if ts is None : ts = np.zeros((10, len(dates),nbands,3))
                ts[0,idate,iband,i] = runner.brdf[0,0,0,i]
                ts[1,idate,iband,i] = runner.brdf1[0,0,0,i]
                ts[2,idate,iband,i] = runner.brdf_in.data[0,0,0,i]
                ts[3,idate,iband,i] = runner.covariance[0,0,0,i,i]
                ts[4,idate,iband,i] = runner.covariance1[0,0,0,i,i]
                ts[5,idate,iband,i] = runner.covariance_in.data[0,0,0,i,i]
        for i in [0,1]:
            for j in [0,1]: # should be more
                ts[6,idate,i,j] = runner.outalbedos[0,0,i,j]
                ts[7,idate,i,j] = runner.outalbedos_cov[0,0,i,j]                
                ts[8,idate,i,j] = runner.outalbedos_age[0,0,i,j]
                ts[9,idate,i,j] = runner.outalbedos_quality[0,0,i,j]
    return runner, ts

runner, dm = setup()
runner, ts = test_2()

# f, ax = plot_now(runner, f=f, ax=ax)
