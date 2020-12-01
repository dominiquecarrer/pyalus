#!/usr/bin/env python 
import logging
import numpy as np
from datetime import datetime
from datetime import timedelta

from pyal2 import __version__
from pyal2.utils.augmented_netcdf import AugmentedNetcdfDataset
from pyal2.data_matrix import DataMatrixFloat, DataMatrixInteger
from pyal2.utils.io import ensure_dir

data_params = []

class Writer(dict):
    """ This class is responsible to write brdf and albedos with c3s format. See al2_runner to have example on how to run it."""
    def __init__(self, config, xoutputsize, youtputsize, n_channels_ref, model_len, model_id, output_channel_names, inalbedos_names, outalbedos_names, xslice, yslice, date):
        self.albedo_file     = config['albedo']['filename']
        self.brdf_file       = config['brdf']['filename']
        self.xoutputsize      = xoutputsize
        self.youtputsize      = youtputsize
        self.n_channels_ref  = n_channels_ref
        self.model_len       = model_len
        self.model_id        = model_id
        self.output_channel_names = output_channel_names
        self.inalbedos_names      = inalbedos_names
        self.outalbedos_names     = outalbedos_names
        self.xslice = xslice
        self.yslice = yslice
        self.date   = date


    def write_all_brdf(self, al2runner):
        # write brdf
        self.write_brdf(al2runner.brdf.values, 'K012', 'brdf')
        self.write_brdf(al2runner.covariance.values, 'CK', 'covariance')
        self.write_brdf(al2runner.quality.values, 'Z-QFLAG', 'quality')
        self.write_brdf(al2runner.age.values, 'Z-AGE', 'age')
        self.write_brdf(al2runner.latitude.values, 'latitude', 'latitude')
        self.write_brdf(al2runner.longitude.values, 'longitude', 'longitude')
        self.write_brdf(al2runner.n_valid_obs_out.values[:,:,:].min(axis=2), 'Z-NMOD', 'n_valid_obs')

    def write_all_spectral_albedos(self, al2runner):
        # Write the spectral albedos
        for iband in range(self.n_channels_ref):
            channelname = self.output_channel_names[iband]
            for iin, inname in enumerate(self.inalbedos_names):
                self.write_albedo(al2runner.albedos.values[:,:,iband, iin],
                        'AL-{channelname}-{inname}'.format(inname=inname, channelname=channelname), 'albedo')
                self.write_albedo(al2runner.albedos_cov.values[:,:,iband, iin],
                        'AL-{channelname}-{inname}-ERR'.format(inname=inname, channelname=channelname), 'albedo_cov')
            # we decided to write only on QFLAG and one NMOD for in the general albedos file
            #self.write_albedo(al2runner.albedos_age[:,:,iband], f'Z-AGE-{channelname}', 'age')
            #self.write_albedo(al2runner.albedos_quality[:,:,iband], f'Z-QFLAG-{channelname}', 'quality')
            #self.write_albedo(al2runner.n_valid_obs_out[:,:,iband], f'Z-NMOD-{channelname}', 'n_valid_obs')
        self.write_albedo(al2runner.latitude.values             , 'latitude', 'latitude')
        self.write_albedo(al2runner.longitude.values            , 'longitude', 'longitude')

    def write_all_albedos(self, al2runner):
        # Write the VI/NI/BB albedos
        for iout, outname in enumerate(self.outalbedos_names):
            for iin, inname in enumerate(self.inalbedos_names):
                fullname = inname + '-' + outname
                self.write_albedo(al2runner.outalbedos.values[:,:,iin, iout], 'AL-{fullname}'.format(fullname=fullname), 'albedo')
                self.write_albedo(al2runner.outalbedos_cov.values[:,:,iin, iout], 'AL-{fullname}-ERR'.format(fullname=fullname), 'albedo_cov')
        self.write_albedo(al2runner.outalbedos_age.values[:,:], 'Z-AGE', 'age')
        self.write_albedo(al2runner.outalbedos_quality.values[:,:], 'Z-QFLAG', 'quality')
        self.write_albedo(al2runner.n_valid_obs_out.values[:,:,:].min(axis=2), 'Z-NMOD', 'n_valid_obs')

    def write_brdf(self, data, key, typ):
        """ Will write the numpy array "data", in the file defined above in "self.brdf_file", on the data layer "key".
            "typ" should be a known identifier, as the data will be processed differently according its value.
        """
        logging.debug('Writing ' + key + ':' + typ + ' to ' + self.brdf_file)
        try:
            ensure_dir(self.brdf_file)
            try:
                f = AugmentedNetcdfDataset(self.brdf_file,'a', format='NETCDF4')
            except OSError:
                f = AugmentedNetcdfDataset(self.brdf_file,'w', format='NETCDF4')
                f.createDimensionIfNotExists('X', self.xoutputsize)
                f.createDimensionIfNotExists('Y', self.youtputsize)
                f.createDimensionIfNotExists('NBAND', self.n_channels_ref)
                f.createDimensionIfNotExists('KERNEL_INDEX', self.model_len)
                f.createDimensionIfNotExists('KERNEL_INDEX2', self.model_len)
                self._set_date_and_version(f, self.date, __version__, self.model_id)
            if typ == 'brdf':                             outvar = f.createVariableIfNotExists(key, data.dtype, ('X','Y','NBAND','KERNEL_INDEX'), zlib=True, complevel=5, fletcher32=True)
            elif typ == 'covariance':                     outvar = f.createVariableIfNotExists(key, data.dtype, ('X','Y','NBAND','KERNEL_INDEX', 'KERNEL_INDEX2'),zlib=True,  complevel=5, fletcher32=True)
            elif typ == 'quality':                        outvar = f.createVariableIfNotExists(key, data.dtype, ('X','Y','NBAND'),zlib=True,  complevel=5, fletcher32=True)
            elif typ == 'age':                            outvar = f.createVariableIfNotExists(key, data.dtype, ('X','Y','NBAND'),zlib=True,  complevel=5, fletcher32=True)
            elif typ == 'latitude' or typ == 'longitude': outvar = f.createVariableIfNotExists(key, data.dtype, ('X','Y'),zlib=True,  complevel=5, fletcher32=True)
            elif typ == 'n_valid_obs':
                data = data.astype('int8')
                outvar = f.createVariableIfNotExists(key, data.dtype, ('X','Y'),zlib=True,  complevel=5, fletcher32=True,
                        attributes = {'units': '', 'long_name' : 'NMOD for {key}'.format(key=key) } )
            else:
                raise Exception('Unknown type of data to write : typ = ' + str(typ))
            # here is the actual writing command
            outvar[self.xslice, self.yslice,...] = data[...]
            f.close()
        except Exception as e:
            print(e)
            logging.error('Problem writing ' + key + ' on ' + self.brdf_file + ' : ' + str(e))
            raise(e)

    def write_albedo(self, data, key, typ):
        """ Will write the numpy array "data", in the file defined above in "self.albedo_file", on the data layer "key".
            "typ" should be a known identifier, as the data will be processed differently according its value.
        """
        logging.debug('Writing ' + key + ' to ' + self.albedo_file) # + str(self.date))
        try:
            ensure_dir(self.albedo_file)
            try:
                f = AugmentedNetcdfDataset(self.albedo_file,'a', format='NETCDF4')
            except OSError:
                f = AugmentedNetcdfDataset(self.albedo_file,'w', format='NETCDF4')
                f.createDimensionIfNotExists('longitude', self.xoutputsize)
                f.createDimensionIfNotExists('latitude', self.youtputsize)
                f.createDimensionIfNotExists('NBAND', self.n_channels_ref)
                self._set_date_and_version(f, self.date, __version__, self.model_id)
                f.setncattr('institution', 'VITO')
            if typ == 'albedo':
                #print(f'--------------')
                #print(f'DATA {self.date} :{key}: {data[0, 0]}')
                scale_factor = 1./10000
                missing_value = -32767
                dtype = np.int16
                outvar = f.createVariableIfNotExists(key, dtype, ('latitude','longitude'), complevel=5, fletcher32=True, zlib=True,
                        attributes = {'units': '', 'offset':0., 'scale_factor':scale_factor,
                                      'long_name' : 'Albedo {key}'.format(key=key) } )
                missing = np.isnan(data)
                #######with numpy.warning.filterwarnings(divide='ignore'):
                #######        numpy.float64(1.0) / 0.0
                data[data < -3.0] = -3.0
                data[data >  3.0] =  3.0
                #print(f'{self.date} :{key}: m, s, l: {missing[0, 0]}')
                data = data / scale_factor
                data = data.astype(dtype)
                data[missing] = missing_value
                #print(f'DATA {self.date} :{key}: {data[0, 0]}')
                outvar[self.xslice, self.yslice] = data[:,:]
                #outvar[self.xslice, self.yslice] = 7
                ##f.close()

                ##f = AugmentedNetcdfDataset(self.albedo_file,'r', format='NETCDF4')
                ##var = f[key]
                ##var.set_auto_maskandscale(False)
                ###print(f'HERE {self.date} :{key}: {var[self.xslice, self.yslice][0,0]}')
                ##f.close()

                ##f = AugmentedNetcdfDataset(self.albedo_file,'r', format='NETCDF4')
                ##print(f'autoscale {self.date} :{key}: {f[key][self.xslice, self.yslice][0,0]}')
            elif typ == 'albedo_cov':
                scale_factor = 1./10000
                missing_value = -32767
                dtype = np.int16
                outvar = f.createVariableIfNotExists(key, dtype, ('latitude','longitude'), complevel=5, fletcher32=True, zlib=True,
                        attributes = {'units': '', 'offset': 0., 'scale_factor':scale_factor,
                                      'long_name' : 'Albedo cov {key}'.format(key=key) } )
                missing = np.isnan(data)
                data[data < -3.0] = -3.0
                data[data >  3.0] =  3.0
                data = data / scale_factor
                data = data.astype(dtype)
                data[missing] = missing_value
                outvar[self.xslice, self.yslice] = data[:,:]
            elif typ == 'age':
                data = data.astype('int8')
                outvar = f.createVariableIfNotExists(key, data.dtype, ('latitude','longitude'), complevel=5, fletcher32=True, zlib=True,
                        attributes = {'units': 'days',
                                      'long_name' : 'Age {key}'.format(key=key) } )
                outvar[self.xslice, self.yslice] = data[:,:]
            elif typ == 'n_valid_obs':
                data = data.astype('int8')
                outvar = f.createVariableIfNotExists(key, data.dtype, ('latitude','longitude'), complevel=5, fletcher32=True, zlib=True,
                        attributes = {'units': '',
                                      'long_name' : 'NMOD for {key}'.format(key=key) } )
                outvar[self.xslice, self.yslice] = data[:,:]
            elif typ == 'quality':
                data = data.astype('uint8')
                outvar = f.createVariableIfNotExists(key, data.dtype, ('latitude','longitude'), complevel=5, fletcher32=True, zlib=True,
                        attributes = {'units': '',
                                      'long_name' : 'Quality flag {key}'.format(key=key)  } )
                outvar[self.xslice, self.yslice] = data[:,:]
            elif typ == 'latitude':
                outvar = f.createVariableIfNotExists(key, data.dtype, ('latitude'), complevel=5, fletcher32=True, zlib=True,
                        attributes = {'units': 'degrees',
                                      'title' : 'latitude',
                                      'long_name' : 'latitude' } )
                outvar[self.xslice] = data[:,0] # as per VITO's request, take only first column]
            elif typ == 'longitude':
                outvar = f.createVariableIfNotExists(key, data.dtype, ('longitude'), complevel=5, fletcher32=True, zlib=True,
                        attributes = {'units': 'degrees',
                                      'title' : 'longitude',
                                      'long_name' : 'longitude' } )
                outvar[self.yslice] = data[0,:] # as peer VITO's request, take only first row
            else:
                raise Exception('Unknown type of data to write : typ = ' + str(typ))
            f.close()
        except Exception as e:
            logging.error('Problem writing ' + key + ' : ' + str(e))
            raise Exception()

    def _set_date_and_version(self, f, date, version, model_id):
        f.setncattr_string("DATE",date.strftime('%Y%m%d-%M%S'))
        f.setncattr_string("VERSION",version)
        if not model_id is None:
            f.setncattr("BRDF_MODEL_ID",model_id)
