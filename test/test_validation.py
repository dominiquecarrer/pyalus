def setup():
    from pyal2.c3s.c3s_al2_runner import C3SAl2Runner
    runner = C3SAl2Runner()
    from pyal2.c3s.c3s_data_manager import C3SDataManager
    dm=C3SDataManager('config/acf.c3s', 'config/pcf.c3s',startseries=True, dates=['2002-03-05','2002-04-05'])
    runner.setup(dm)
    return runner, dm

def test_1():
    dates = dm['dates']
    dates
    #runner.debuglevel = 10000
    for date in dates[0:3]:
        runner.process(xslice=slice(25,26), yslice=slice(25,26), dates=[date])
        print(str(date) + ' instant brdf = ' + str(runner.brdf[0,0,0,:]))    
    return runner

runner, dm = setup()
test_1()

# f, ax = plot_now(runner, f=f, ax=ax)
