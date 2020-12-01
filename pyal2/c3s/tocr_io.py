#!/usr/bin/env python 
import logging
import numpy as np
from datetime import datetime
from datetime import timedelta

from pyal2 import __version__
from pyal2.utils.augmented_netcdf import AugmentedNetcdfDataset
from pyal2.utils.io import ensure_dir

class TocrIO():
    """ Read and Write toc r data. """
    def __init__(self, outfilename):
        self.outfilename = outfilename

    def write_tocr(self, data, xslice, yslice, date, key, typ):
        logging.info('Writing ' + typ + ' to ' + self.outfilename)
        try:
            ensure_dir(self.outfilename)
            try:
                f = AugmentedNetcdfDataset(self.outfilename,'a', format='NETCDF4')
            except OSError:
                f = AugmentedNetcdfDataset(self.outfilename,'w', format='NETCDF4')
                f.createDimensionIfNotExists('latitude', self.xoutputsize)
                f.createDimensionIfNotExists('longitude', self.youtputsize)
                f.createDimensionIfNotExists('NBAND', self.n_channels_ref)
                self._set_date_and_version(f, date, __version__, self.model_id)
            if typ == 'TOC-R' or typ == 'TOC-R-ERR':
                scale_factor = 1./10000.0
                missing_value = -32767
                outvar = f.createVariableIfNotExists(key, 'int16', ('latitude','longitude','NBAND'), zlib=True, complevel=5, fletcher32=True,
                        attributes = {'units': '', 'offset':0., 'scale_factor':scale_factor } )
                missing = np.isnan(data)
                data[data < 0] = 0.0
                data[data > 1.01] = 1.0
                data = data / scale_factor
                data = data.astype(np.int16)
                data[missing] = missing_value
                outvar[xslice, yslice,:] = data[:,:,:]
            elif typ=='Z-QFLAG':
                outvar=f.createVariableIfNotExists(key, 'uint8', ('latitude','longitude','NBAND'), zlib=True, complevel=5, fletcher32=True)
                outvar[xslice,yslice,:]=data[:,:,:]
            elif typ == 'solzenith':
                outvar = f.createVariableIfNotExists(key, data.dtype, ('latitude','longitude'), zlib=True, complevel=5, fletcher32=True)
                outvar[xslice, yslice] = data[:,:]
            elif typ == 'n_valid_obs':
                data = data.astype('int8')
                outvar = f.createVariableIfNotExists(key, data.dtype, ('latitude','longitude'), zlib=True, complevel=5, fletcher32=True,
                        attributes = {'units': '',
                                      'long_name' : 'NMOD for {key}'.format(key=key) } )
                outvar[xslice, yslice] = data[:,:]
            elif typ == 'latitude':
                outvar = f.createVariableIfNotExists(key, data.dtype, ('latitude'), complevel=5, fletcher32=True, zlib=True,
                        attributes = {'units': 'degrees',
                                      'title' : 'latitude',
                                      'long_name' : 'latitude' } )
                outvar[xslice] = data[:,0] # as per VITO's request, take only first column]
            elif typ == 'longitude':
                outvar = f.createVariableIfNotExists(key, data.dtype, ('longitude'), complevel=5, fletcher32=True, zlib=True,
                        attributes = {'units': 'degrees',
                                      'title' : 'longitude',
                                      'long_name' : 'longitude' } )
                outvar[yslice] = data[0,:] # as peer VITO's request, take only first row
            else:
                raise Exception('Unknown type of data to write : typ = ' + str(typ))
            f.close()
        except Exception as e:
            logging.error('Problem writing ' + key + ' on ' + self.outfilename + ' : ' + str(e))
            raise(e)

    def _set_date_and_version(self, f, date, version, model_id):
        f.setncattr_string("DATE",date.strftime('%Y%m%d-%M%S'))
        f.setncattr_string("VERSION",version)
        if not model_id is None:
            f.setncattr("BRDF_MODEL_ID",model_id)
