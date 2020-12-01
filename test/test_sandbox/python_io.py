#!/usr/bin/env python
import netCDF4
import numpy as np

ref = -3.12298
scale_factor = 1./10000.
dtype = np.int16 #'int16'

f = netCDF4.Dataset('test.nc','w', format='NETCDF4')
f.set_auto_maskandscale(False)
f.createDimension('longitude', 2)
f.createDimension('latitude', 2)
var = f.createVariable('key', dtype, ('latitude','longitude'), complevel=5, fletcher32=True, zlib=True)
var.set_auto_maskandscale(False)
var.setncattr('offset', 0.)
var.setncattr('scale_factor', scale_factor)
var.setncattr('missing_value', -32767)
#var.setncattr('_FillValue', -32767)
#ADD thisvar.setncattr('missing', 1./scale_factor)
var[0,0] = ref / scale_factor
var[0,1] = -32767 #np.ma.masked
f.close()


f = netCDF4.Dataset('test.nc','r', format='NETCDF4')
f.set_auto_maskandscale(False)
var = f.variables['key']
var.set_auto_maskandscale(False)
value = var[0,:]
value = value * scale_factor
f.close()
print(f'initial = {ref}  -> read = {value}')

f = netCDF4.Dataset('test.nc','r', format='NETCDF4')
var = f.variables['key']
value = var[0,:]
f.close()
print(f'autoscale = {value}, {np.isnan(value)}')

print()




f = netCDF4.Dataset('test2.nc','w', format='NETCDF4')
f.set_auto_scale(True)
f.set_auto_mask(False)
f.createDimension('longitude', 2)
f.createDimension('latitude', 2)
var = f.createVariable('key', dtype, ('latitude','longitude'), complevel=5, fletcher32=True, zlib=True)
f.set_auto_maskandscale(True)
var.setncattr('offset', 0.)
var.setncattr('scale_factor', scale_factor)
var.setncattr('missing_value', -32767)
f.set_auto_scale(True)
f.set_auto_mask(False)
var[0,0] = ref
var[0,1] = -32767 * scale_factor
f.close()

f = netCDF4.Dataset('test2.nc','r', format='NETCDF4')
f.set_auto_maskandscale(False)
var = f.variables['key']
var.set_auto_maskandscale(False)
value = var[0,:]
value = value * scale_factor
f.close()
print(f'initial = {ref}  -> read = {value}')

f = netCDF4.Dataset('test2.nc','r', format='NETCDF4')
var = f.variables['key']
value = var[0,:]
f.close()
print(f'autoscale = {value}, {np.isnan(value)}')
