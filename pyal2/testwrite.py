#!/usr/bin/env python 
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')
import pyal2
from pyal2.parallel import ExceptionInSubprocessWrapper, chunk_init

def writeh5(chunk, filename):
    import h5py

    try:
        write_lock.acquire()

        f = h5py.File(filename, 'a')
        print(chunk,'opened')
        key = 'test'
        if key in f.keys():
            dataset = f[key]
        else:
            dataset = f.create_dataset(key,chunks=True,compression='gzip',fletcher32=True, shape=(100,100), dtype='f4')
        dataset[(chunk*10):((chunk+1)*10), :] = chunk
        print(chunk,'writing')
        f.close()
        print(chunk,'closed')

        write_lock.release()
    except Exception as e:
        write_lock.acquire(False)
        write_lock.release()
        return ExceptionInSubprocessWrapper(e)

def writenetcdf(chunk, filename):
    import netCDF4

    try:
        write_lock.acquire()

        try:
            f = netCDF4.Dataset(filename,'a', format='NETCDF4')
        except OSError:
            f = netCDF4.Dataset(filename,'w', format='NETCDF4')
            f.createDimension('X', 100)
            f.createDimension('Y', 100)
            f.setncattr_string("DATE",'20170512')
        print(chunk,'opened')
        key = 'test'
        if key in f.variables.keys():
            outvar = f.variables[key]
        else:
            outvar = f.createVariable(key, 'f4', ('X','Y'), complevel=5, fletcher32=True)
        outvar[(chunk*10):((chunk+1)*10), :] = chunk
        print(chunk,'writing')
        f.close()
        print(chunk,'closed')

        write_lock.release()
    except Exception as e:
        write_lock.acquire(False)
        write_lock.release()
        return ExceptionInSubprocessWrapper(e)

if __name__ == "__main__":
    cpu = 5
    global write_lock
    write_lock = Lock()
    with Pool(cpu, initializer=chunk_init, initargs=(write_lock,)) as p:
        #results = p.starmap(writeh5, [(i,'testh5.h5') for i in range(0,10)])
        results = p.starmap(writenetcdf, [(i,'testnetcdf.nc') for i in range(0,10)])
    for result in results:
        if isinstance(result, ExceptionInSubprocessWrapper):
            result.re_raise()
