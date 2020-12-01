#!/usr/bin/env python 
import logging
import numpy as np
import h5py
from datetime import datetime
from pyal2.data_matrix import DataMatrixFloat, DataMatrixInteger

data_params = ['filenames']

class BrdfReader():
    """ Reader for MSG brdf data """
    def load_brdf(self, filenames, model_len, n_channels_ref, xslice, yslice):
        # save filenames for debug purposes
        self.filenames = filenames

        sizex = xslice.stop - xslice.start
        sizey = yslice.stop - yslice.start

        self.brdf        = DataMatrixFloat().full(shape=(sizex, sizey, n_channels_ref, model_len), dtype='f4')
        self.covariance  = DataMatrixFloat().full(shape=(sizex, sizey, n_channels_ref, model_len, model_len), dtype='f4')
        self.age_obs     = DataMatrixInteger().full(shape=(sizex, sizey, n_channels_ref), dtype='int8')
        self.quality     = DataMatrixInteger().full(shape=(sizex, sizey, n_channels_ref), dtype='int8')

        # Read K0 K1 K2, brdf coefficients, for each band. And age_obs and Qflag. And date in the file.
        for ichannel in range(0, n_channels_ref):
            filename = filenames[f'band{ichannel+1}']['values']
            logging.info('Reading ' + filename)

            f = h5py.File(filename, 'r')
            self.previous_date = datetime.strptime(f.attrs['IMAGE_ACQUISITION_TIME'].decode('ASCII'), '%Y%m%d%H%M%S')
            for iparam in range(0, model_len):
                key = f'K{iparam}'
                dataset = f[key]

                # read the values
                scale, offset = dataset.attrs['SCALING_FACTOR'], dataset.attrs['OFFSET']
                data = dataset[xslice,yslice].astype('<f4') / scale + offset

                # read the missing values mask
                missing = dataset.attrs['MISSING_VALUE']
                missingdata = (data == missing)

                # apply the missing value mask
                data[missingdata == missing] = np.nan

                # put the data in the right place in the full matrix
                self.brdf.values[:,:,ichannel, iparam] = data

            self.age_obs.values[:,:,ichannel] = f['Z_Age'][xslice,yslice]
            self.quality.values[:,:,ichannel] = f['Q-Flag'][xslice,yslice]

            f.close()

            logging.debug('extract of brdf data (channel {ichannel}) = '+str(self.brdf.values[0,0,:,:]))
            logging.debug('extract of age_obs brdf data (channel {ichannel}) = '+str(self.age_obs.values[0,0,:]))
            logging.debug('extract of quality brdf data (channel {ichannel}) = '+str(self.quality.values[0,0,:]))

        logging.debug(f' found date of input brdf : {self.previous_date}')


        # Read CK covariance for each band
        for ichannel in range(0, n_channels_ref):
            filename = filenames[f'band{ichannel+1}']['cov'] # notice here the key is "cov" instead of "values"
            logging.info('Reading ' + filename)
            try:
                f = h5py.File(filename, 'r')
                for iparam in range(0, model_len):
                  for jparam in range(iparam, model_len):
                    key = f'C{iparam}{jparam}'
                    dataset = f[key]

                    # TODO remove this :
                    # weirdsize = 1+model_len*(model_len-1)

                    # read the values
                    scale, offset = dataset.attrs['SCALING_FACTOR'], dataset.attrs['OFFSET']
                    data = dataset[xslice,yslice]

                    # read the missing values mask
                    missing = dataset.attrs['MISSING_VALUE']
                    missingdata = (data == missing)

                    # convert to float
                    data = data.astype('<f4') / scale + offset

                    # apply the missing value mask
                    data[missingdata] = np.nan

                    # put the data in the right place in the full matrix
                    self.covariance.values[:,:,ichannel, iparam, jparam] = data

                f.close()
            except Exception as e:
                logging.error('Problem reading ' + filename)
            logging.debug('extract of brdf cov data (channel {ichannel}) = '+str(self.covariance.values[0,0,:,:,:]))

        return self

    def to_xr(self):
        """ xarray serialisation """
        import xarray as xr
        return xr.DataArray(self.values[:,:,:],
                dims = ['x', 'y', 'scenedatetime'],
                name = self.name,
                coords= { 'scenedatetime': self.scenes_dates },
                attrs = { 'filenames': self.filenames })
