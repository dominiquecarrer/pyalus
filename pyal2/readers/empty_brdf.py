from .generic import GenericReader
import logging
import numpy as np
from datetime import datetime
from datetime import timedelta

from pyal2.data_matrix import DataMatrixFloat, DataMatrixInteger

data_params = []

class Brdf():
    """ Fake reader when the data is unavailable """
    def load_brdf(self, xslice, yslice, n_channels_ref, model_len):
        self.xslice = xslice
        self.yslice = yslice
        self.quality    = DataMatrixInteger(np.zeros((self.xslice.stop - self.xslice.start, self.yslice.stop - self.yslice.start, n_channels_ref),                     order='F', dtype='i1'))
        self.age_obs    = DataMatrixInteger(np.zeros((self.xslice.stop - self.xslice.start, self.yslice.stop - self.yslice.start, n_channels_ref),                     order='F', dtype='i1'))
        self.brdf       = DataMatrixFloat(np.zeros((self.xslice.stop - self.xslice.start, self.yslice.stop - self.yslice.start, n_channels_ref, model_len),            order='F', dtype='<f4'))
        self.covariance = DataMatrixFloat(np.zeros((self.xslice.stop - self.xslice.start, self.yslice.stop - self.yslice.start, n_channels_ref, model_len, model_len), order='F', dtype='<f4'))

        self.previous_date = datetime(1970,1,1)
        logging.info('First step of start_series = true -> using empty initial BRDF and qflag ')
        logging.info(f'No data for {type(self).__name__} : using empty matrix')
        return self

    #def to_xr(self):
    #    """ xarray serialisation """
    #    import xarray as xr
    #    return xr.DataArray(self.values[:,:],
    #            dims = ['x', 'y'],
    #            name = self.name,
    #            attrs = { 'filenames': self.filenames })
