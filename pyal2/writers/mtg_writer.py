#!/usr/bin/env python 
import logging
import numpy as np
from datetime import datetime
from datetime import timedelta
import netCDF4 as nc

from pyal2 import __version__
from pyal2.utils.augmented_netcdf import AugmentedNetcdfDataset
from pyal2.data_matrix import DataMatrixFloat, DataMatrixInteger
from pyal2.utils.io import ensure_dir

data_params = []

long_names = {  'Q-Flag' : 'Q-Flag',
                'Z_Age' : 'Age of Information',
                'AL-SP-BH': 'Albedo Spectral Bi-Hemispherical',
                'AL-SP-DH': 'Albedo Spectral Directional-Hemispherical',
                'AL-SP-BH-ERR': 'Error of Albedo Spectral Bi-Hemispherical',
                'AL-SP-DH-ERR': 'Error of Albedo Spectral Directional-Hemispherical',
                'AL-BB-BH': 'Albedo Shortwave Broadband Bi-Hemispherical',
                'AL-BB-DH': 'Albedo Shortwave Broadband Directional-Hemispherical',
                'AL-NI-BH': 'Albedo NearInfrared Broadband Bi-Hemispherical',
                'AL-NI-DH': 'Albedo NearInfrared Broadband Directional-Hemispherical',
                'AL-VI-BH': 'Albedo Visible Broadband Bi-Hemispherical',
                'AL-VI-DH': 'Albedo Visible Broadband Directional-Hemispherical',
                'AL-BB-BH-ERR': 'Error of Albedo Shortwave Broadband Bi-Hemispherical',
                'AL-BB-DH-ERR': 'Error of Albedo Shortwave Broadband Directional-Hemispherical',
                'AL-NI-BH-ERR': 'Error of Albedo NearInfrared Broadband Bi-Hemispherical',
                'AL-NI-DH-ERR': 'Error of Albedo NearInfrared Broadband Directional-Hemispherical',
                'AL-VI-BH-ERR': 'Error of Albedo Visible Broadband Bi-Hemispherical',
                'AL-VI-DH-ERR': 'Error of Albedo Visible Broadband Directional-Hemispherical'}
product_id = { 'Q-Flag' : 128,
                'Z_Age' : 128,
                'AL-SP-BH': 84,
                'AL-SP-DH': 84,
                'AL-SP-BH-ERR': 128,
                'AL-SP-DH-ERR': 128,
                'AL-NI-BH': 84,
                'AL-VI-BH': 84,
                'AL-BB-BH': 84,
                'AL-NI-DH': 84,
                'AL-VI-DH': 84,
                'AL-BB-DH': 84,
                'AL-VI-DH-ERR': 128,
                'AL-NI-DH-ERR': 128,
                'AL-BB-DH-ERR': 128,
                'AL-VI-BH-ERR': 128,
                'AL-NI-BH-ERR': 128,
                'AL-BB-BH-ERR': 128
                }

class Writer(dict):
    """ This class is responsible to write brdf and albedos with c3s format. See al2_runner to have example on how to run it."""
    def __init__(self, config, xoutputsize, youtputsize, n_channels_ref, model_len, model_id, output_channel_names, inalbedos_names, outalbedos_names, xslice, yslice, date):
        self.config     = config
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

        self.dtype = 'i2' # beware there is rounding of the value below

    def write_all_brdf(self, al2runner):
		            
        self.write_brdf(al2runner.brdf.values, 'brdf')
        self.write_brdf_covariance(al2runner.covariance.values, 'brdf')

        self.write_brdf(al2runner.brdf1.values, 'brdf-d01')
        self.write_brdf_covariance(al2runner.covariance1.values, 'brdf-d01')
        
        for ichannel in range(0, self.n_channels_ref):
            filename = self.config['brdf'][f'band{ichannel+1}']['filename']
            ensure_dir(filename)
            self._write_global_attributes(self.date, filename, options=None)
            data = al2runner.age.values[:,:,ichannel]
            self.write_age(data, filename=filename)

        for ichannel in range(0, self.n_channels_ref):
            filename = self.config['brdf'][f'band{ichannel+1}']['filename']
            ensure_dir(filename)
            self._write_global_attributes(self.date, filename, options=None)
            data = al2runner.quality.values[:,:,ichannel]
            self.write_qflag(data, filename=filename)

        for ichannel in range(0, self.n_channels_ref):
            ensure_dir(filename)
            filename = self.config['brdf-d01'][f'band{ichannel+1}']['filename']
            self._write_global_attributes(self.date, filename, options=None)
            data = al2runner.quality1.values[:,:,ichannel]
            self.write_qflag(data, filename=filename)

    def write_all_spectral_albedos(self, al2runner):
        for ichannel in range(0, self.n_channels_ref):
            filename = self.config['albedo-sp'][f'band{ichannel+1}']['filename']

            data = al2runner.albedos.values
            self.write_albedo_per_band(data, 'albedo',filename, ichannel, missing=-1, scale=10000., offset=0.)

            data = al2runner.albedos_cov.values
            self.write_albedo_per_band(data, 'albedo-err',filename, ichannel, missing=-1, scale=10000., offset=0.)

            data = al2runner.albedos_age.values[:,:,ichannel]
            self.write_age(data, filename=filename)

            data = al2runner.albedos_quality.values[:,:,ichannel]
            self.write_qflag(data, filename=filename)


    def write_all_albedos(self, al2runner):

        filename = self.config['albedo']['filename']

        data = al2runner.outalbedos.values[:,:,:]
        self.write_albedo_after_spectral_integration(data, 'albedo', filename, missing_val=-1, scale=10000., offset=0.)

        data = al2runner.outalbedos_cov.values[:,:,:]
        self.write_albedo_after_spectral_integration(data, 'albedo-err', filename, missing_val=-1, scale=10000., offset=0.)

        data = al2runner.outalbedos_age.values[:,:]
        self.write_age(data, filename=filename)

        data = al2runner.outalbedos_quality.values[:,:]
        self.write_qflag(data, filename=filename)

    def write_age(self, data, outkey = 'Z_Age', missing=-1, dtype = 'int8', filename = None):
        logging.debug('Writing ' + filename + ' for ' + str(outkey))
        ensure_dir(filename)
        try:
            f = AugmentedNetcdfDataset(filename,'a', format='NETCDF4')
            f.createDimensionIfNotExists('x', self.xoutputsize)
            f.createDimensionIfNotExists('y', self.youtputsize)
        except OSError:
            f = AugmentedNetcdfDataset(filename,'w', format='NETCDF4')
            f.createDimensionIfNotExists('x', self.xoutputsize)
            f.createDimensionIfNotExists('y', self.youtputsize)
            self._set_date_and_version(f, self.date, __version__, self.model_id)
            f.setncattr('institution', 'IPMA')
        outvar = f.createVariableIfNotExists(outkey, data.dtype, ('y','x'),zlib=True,  complevel=5, fletcher32=True)
        
        data = data.astype(dtype)
        outvar[self.xslice, self.yslice] = data
        f.close()

    def write_qflag(self, data, outkey = 'QFLAGS', dtype = 'uint8', filename = None):
        logging.debug('Writing ' + filename + ' for ' + str(outkey))
        try:
            f = AugmentedNetcdfDataset(filename,'a', format='NETCDF4')
            f.createDimensionIfNotExists('x', self.xoutputsize)
            f.createDimensionIfNotExists('y', self.youtputsize)
            f.createDimensionIfNotExists('NBAND', self.n_channels_ref)
        except OSError:
            f = AugmentedNetcdfDataset(filename,'w', format='NETCDF4')
            f.createDimensionIfNotExists('x', self.xoutputsize)
            f.createDimensionIfNotExists('y', self.youtputsize)
            f.createDimensionIfNotExists('NBAND', self.n_channels_ref)
            self._set_date_and_version(f, self.date, __version__, self.model_id)
            f.setncattr('institution', 'IPMA')
            
        outvar = f.createVariableIfNotExists(outkey, data.dtype, ('y','x'),zlib=True,  complevel=5, fletcher32=True)
        data = data.astype(dtype)
        outvar[self.xslice, self.yslice] = data
        f.close()

    def write_brdf(self, alldata, configkey, scale=10000., offset=0., missing=-32768):
        """ Write data in hdf file for the K012 kernel coefficients of the brdf model """
        for ichannel in range(0, self.n_channels_ref):
            for iparam in range(0, self.model_len):
                filename = self.config[configkey][f'band{ichannel+1}']['filename']
                outkey = f'K{iparam}'
                logging.debug('Writing ' + filename + ' for ' + str(outkey))
                ensure_dir(filename)
                try:
                    f = AugmentedNetcdfDataset(filename,'a', format='NETCDF4')
                except OSError:
                    f = AugmentedNetcdfDataset(filename,'w', format='NETCDF4')
                    f.createDimensionIfNotExists('longitude', self.xoutputsize)
                    f.createDimensionIfNotExists('latitude', self.youtputsize)
                    f.createDimensionIfNotExists('NBAND', self.n_channels_ref)
                    f.createDimensionIfNotExists('KERNEL_INDEX', self.model_len)
                    f.createDimensionIfNotExists('KERNEL_INDEX2', self.model_len)
                    self._set_date_and_version(f, self.date, __version__, self.model_id)
                
                data = alldata[:,:,ichannel, iparam]
                logging.debug('Average : ' + str(np.mean(data[:])))
                data_int = ((data * scale) + offset).round().astype(self.dtype)
                data_int[np.isnan(data)] = missing
                #~ dataset[self.xslice,self.yslice] = data_int
                missing = np.int16(missing)
                outvar = f.createVariableIfNotExists(outkey, data_int.dtype, ('latitude','longitude'), 
                         zlib=True, complevel=5, fletcher32=True,
                         attributes = {'units': '', 'offset':offset, 'scale_factor':scale, '_FillValue': missing,
                                      'long_name' : f'BRDF {outkey}' } )
                        
                outvar[self.xslice, self.yslice] = data_int
                logging.debug('Average : ' + str(np.mean(data_int[:])))
                f.close()
            
    def write_brdf_covariance(self, alldata, configkey, scale=10000., offset=0., missing=-32768):
        """ Write covariance in hdf file for the K012 kernel coefficients of the brdf model """
        for ichannel in range(0, self.n_channels_ref):
            for iparam in range(0, self.model_len):
                for jparam in range(iparam, self.model_len):
                    filename = self.config[configkey][f'band{ichannel+1}']['cov']
                    ensure_dir(filename)
                    outkey = f'C{iparam}{jparam}'
                    logging.debug('Writing ' + filename + ' for ' + str(outkey))

                    try:
                        f = AugmentedNetcdfDataset(filename,'a', format='NETCDF4')
                    except OSError:
                        f = AugmentedNetcdfDataset(filename,'w', format='NETCDF4')
                        f.createDimensionIfNotExists('longitude', self.xoutputsize)
                        f.createDimensionIfNotExists('latitude', self.youtputsize)
                        f.createDimensionIfNotExists('NBAND', self.n_channels_ref)
                        f.createDimensionIfNotExists('KERNEL_INDEX', self.model_len)
                        f.createDimensionIfNotExists('KERNEL_INDEX2', self.model_len)
                        self._set_date_and_version(f, self.date, __version__, self.model_id)
                        
                    data = alldata[:,:,ichannel, iparam, jparam]
                    data_int = ((data * scale) + offset).round().astype(self.dtype)
                    data_int[np.isnan(data)] = missing
                    missing = np.int16(missing)
                    #~ dataset[self.xslice,self.yslice] = data_int
                    outvar = f.createVariableIfNotExists(outkey, data_int.dtype, 
                        ('latitude','longitude'), zlib=True, complevel=5, fletcher32=True,
                        attributes = {'units': '', 'offset':offset, 'scale_factor':scale, '_FillValue': missing,
                                      'long_name' : 'BRDF covariance {key}'.format(key=outkey) } )

                    outvar = data_int
                    f.close()

    def write_albedo_per_band(self, alldata, typ, filename, ichannel, missing=-1, scale=10000., offset=0.):
        dtype='<i2' # beware there is rounding of the value below
        logging.debug('Writing ' + filename + ' for albedo err channel ' + str(ichannel + 1))
        
        ensure_dir(filename)
        try:
            f = AugmentedNetcdfDataset(filename,'a', format='NETCDF4')
        except OSError:
            f = AugmentedNetcdfDataset(filename,'w', format='NETCDF4')
            f.createDimensionIfNotExists('x', self.xoutputsize)
            f.createDimensionIfNotExists('y', self.youtputsize)
            f.createDimensionIfNotExists('time', 1)
            self._set_date_and_version(f, self.date, __version__, self.model_id)
            f.setncattr('institution', 'IPMA')
    
        for j, bhdh in enumerate(self.inalbedos_names):
            if typ == 'albedo':
                outkey = 'AL-SP-' + bhdh
                scale_factor = 1./10000
                missing_value = np.int16(-32768)
                dtype = np.int16

                outvar = f.createVariableIfNotExists(outkey, dtype, ('time','y','x'), complevel=5, fletcher32=True, zlib=True, 
                                            attributes = {'units': '', 'offset':0., '_FillValue': missing_value,
                                             'scale_factor':scale_factor, 'long_name' : 'Albedo {key}'.format(key=outkey) }  )
                data = np.array([alldata[:,:,ichannel,j]]) # pas beau
                
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
                outvar[0, self.xslice, self.yslice] = data[:,:,:]
            elif typ == 'albedo-err':
                outkey = 'AL-SP-' + bhdh + '-ERR'
                scale_factor = 1./10000
                missing_value = np.int16(-32768)
                dtype = np.int16
                                      
                outvar = f.createVariableIfNotExists(outkey, dtype, ('time','y','x'), complevel=5, fletcher32=True, zlib=True,
                        attributes = {'units': '', 'offset': 0., 'scale_factor':scale_factor, '_FillValue': missing_value,
                                      'long_name' : 'Albedo cov {key}'.format(key=outkey) } )
                data = np.array([alldata[:,:,ichannel,j]])
                missing = np.isnan(data)
                data[data < -3.0] = -3.0
                data[data >  3.0] =  3.0
                data = data / scale_factor
                data = data.astype(dtype)
                data[missing] = missing_value
                outvar[0, self.xslice, self.yslice] = data[:,:,:]
                
            #~ data = alldata[:,:,ichannel,j]
            #~ data_int = ((data * scale) + offset).round().astype(dtype)
            #~ data_int[np.isnan(data)] = missing
            #~ outvar[self.xslice,self.yslice] = data_int
        f.close()

    def write_albedo_after_spectral_integration(self, alldata, typ, filename, missing_val=-1, scale=10000., offset=0.):
        dtype='<i2' # beware there is rounding of the value below
        ensure_dir(filename)                        
        try:
            f = AugmentedNetcdfDataset(filename,'a', format='NETCDF4')
        except OSError:
            f = AugmentedNetcdfDataset(filename,'w', format='NETCDF4')
            f.createDimensionIfNotExists('longitude', self.xoutputsize)
            f.createDimensionIfNotExists('latitude', self.youtputsize)  
            f.createDimensionIfNotExists('time', 1)
            
        for iout, outname in enumerate(self.outalbedos_names):
            for iin, inname in enumerate(self.inalbedos_names):

                fullname = outname + '-' + inname

                if typ == 'albedo':
                    outkey = 'AL-' + fullname
                    scale_factor = 1./10000
                    missing_value = np.int16(-32767)
                    dtype = np.int16
                    outvar = f.createVariableIfNotExists(outkey, dtype, ('time', 'latitude','longitude'), complevel=5, fletcher32=True, zlib=True,
                            attributes = {'units': '', 'offset':0., 'scale_factor':scale_factor,  '_FillValue': missing_value,
                                          'long_name' : 'Albedo {key}'.format(key=outkey) } )

                    data = np.array([alldata[:,:,iin, iout]])            
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
                    outvar[:, self.xslice, self.yslice] = data[:,:,:]
                elif typ == 'albedo-err':
                    outkey = 'AL-' + fullname + '-ERR'
                    scale_factor = 1./10000
                    missing_value = np.int16(-32767)
                    dtype = np.int16
                    outvar = f.createVariableIfNotExists(outkey, dtype, ('time', 'latitude','longitude'), complevel=5, fletcher32=True, zlib=True,
                            attributes = {'units': '', 'offset': 0., 'scale_factor':scale_factor, '_FillValue': missing_value,
                                          'long_name' : 'Albedo cov {key}'.format(key=outkey) } )

                    data = np.array([alldata[:,:,iin, iout]])
                    missing = np.isnan(data)
                    data[data < -3.0] = -3.0
                    data[data >  3.0] =  3.0
                    data = data / scale_factor
                    data = data.astype(dtype)
                    data[missing] = missing_value
                    outvar[:, self.xslice, self.yslice] = data[:,:,:]
                if outkey == 'AL-NI-BH' or outkey == 'AL-NI-BH-ERR' or outkey == 'AL-VI-BH' or outkey == 'AL-VI-BH-ERR':
                    continue
                data = alldata[:,:,iin, iout]
                data_int = ((data * scale) + offset).round().astype(dtype)

                data_int[np.isnan(data)] = missing_val
                #~ dataset[self.xslice,self.yslice] = data_int
        f.close()

    def _set_date_and_version(self, f, date, version, model_id):
        f.setncattr_string("DATE", date.strftime('%Y%m%d-%M%S'))
        f.setncattr_string("VERSION", version)
        if not model_id is None:
            f.setncattr("BRDF_MODEL_ID", model_id)

    def _write_global_attributes(self, date, filename, options=None):
        """ Write hdf attributes that are global to the output hdf file """
        if options is None:
            options = {}
        common_attributes =  {
            'image_reference_time': date.strftime('%Y%m%d%H%M%S'),
            'time_coverage_start': '20210801000000',
            'date_created':  datetime.now().strftime('%Y%m%d%H%M%S'),
            'SAF': 'LSA',
            'CENTRE': 'IM-PT',
            'name': 'MTDAL',
            'archive_facility': 'IPMA', #'PARENT_PRODUCT_NAME': ['BRF', 'SAA/SZA', 'VAA/VZA', '-'],
            'SPECTRAL_CHANNEL_ID': '1 2 4 for MTG',
            'algorithm_version': '1.0.0',
            'base_algorithm_version': '1.0.0',   # should come from pyal1 code
            'product_version': '1.0.0',
            'cloud_coverage': '-',
            'OVERALL_QUALITY_FLAG': 'OK',
            'ASSOCIATED_QUALITY_INFORMATION': '-',
            'REGION_NAME': 'MTG-Disk',
            'COMPRESSION': 0,
            'FIELD_TYPE': 'Product',
            'FORECAST_STEP': 0,
            'NC': self.youtputsize,
            'NL': self.xoutputsize,
            'NB_PARAMETERS': 5,
            'platform': 'MTG1',   # should come from pyal1 code
            'sensor': 'FCI',
            'INSTRUMENT_MODE': 'STATIC_VIEW',
            'orbit_type': 'GEO',
            'PROJECTION_NAME': 'GEOS(+000.0)',
            'START_ORBIT_NUMBER': 0,
            'END_ORBIT_NUMBER': 0,
            'SUB_SATELLITE_POINT_START_LAT': 0.0,
            'SUB_SATELLITE_POINT_START_LON': 0.0,
            'SUB_SATELLITE_POINT_END_LAT': 0.0,
            'SUB_SATELLITE_POINT_END_LON': 0.0,
            'PIXEL_SIZE': '3.1km',
            'contacts' : 'helpdesk.landsaf@ipma.pt',
            'grid_mapping' : 'geostationary',
            'GRANULE_TYPE': 'DP',
            'processing_level': '03',
            'PRODUCT_ACTUAL_SIZE': ' 110231552',
            'processing_mode': 'N',
            'disposition_mode' : 'I',
            'DISPOSITION_FLAG': 'O',
            'product_frequency': 'daily',
            'STATISTIC_TYPE': 'recursive, timescale: 5days'}
        # the options dict overwrites the default values
        for k,v in options.items():
            common_attributes[k] = v

        f = AugmentedNetcdfDataset(filename,'a', format='NETCDF4')

        for k, v in common_attributes.items():
            v = _format_recursively(v)
            f.setncattr(k, v)
            
        f.close()

def get_channel_id(ichannel):
    return [1,2,4][ichannel] # for some reason LSA SAF channel ids are 1, 2, 4 for C1 C2 C3

def _format_recursively(value):
        if isinstance(value,str):
            value = value.encode('ASCII')
        if isinstance(value,list):
            value = [_format_recursively(elt) for elt in value]
        return value
