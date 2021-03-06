#!/usr/bin/env python 
from .generic import GenericReader
import logging
import numpy as np

data_params = []

class Latitude(GenericReader):
    """ Fake reader when the data is unavailable """
    def load(self, xslice, yslice, scenes_dates, dataloc):
        # initialise empty matrix of the right size, with nan values (this assumes that xslice.step = 1 or None)
        shape = (xslice.stop - xslice.start, yslice.stop - yslice.start)
        self.values = np.full(shape, np.nan, order='F', dtype='<f4')
        logging.info(f'No data for {type(self).__name__} : using empty matrix {self.values.shape}')
        return self

    #def to_xr(self):
    #    """ xarray serialisation """
    #    import xarray as xr
    #    return xr.DataArray(self.values[:,:],
    #            dims = ['x', 'y'],
    #            name = self.name,
    #            attrs = { 'filenames': self.filenames })
