#!/usr/bin/env python 
import logging
import numpy as np
from datetime import datetime
from datetime import timedelta

from pyal2 import __version__
from pyal2.utils.augmented_netcdf import AugmentedNetcdfDataset
from pyal2.readers.generic import GenericReader
from pyal2.utils.io import ensure_dir

data_params = ['filenames', 'key']

class BrdfClimReader(GenericReader):
    """ This class read a BRDF file """

    def load(self, filenames, key, xslice, yslice, scenes_dates=None, dataloc=None):
 
        shapeK = (xslice.stop - xslice.start, yslice.stop - yslice.start, 4, 3)
        shapeCK = (xslice.stop - xslice.start, yslice.stop - yslice.start, 4, 3, 3)

        logging.info('Reading climatic BRDF from ' + filenames) 
        try:
            with AugmentedNetcdfDataset(filenames, 'r') as f:
                try:
                    scale = f.getncattr("SCALE_FACTOR")
                except:
                    scale = 1
                if key == 'K012':
                    self.values = np.full(shapeK, np.nan, order='F', dtype='<f8')
                    self.values[:,:,:,:] = scale * f[key][xslice, yslice, :, :]
                    self.show_info(self.name, f[key])
                elif (key == 'CK') or (key == 'CKa') or (key == 'CKb') or (key == 'CKab'):
                    self.values = np.full(shapeCK, np.nan, order='F', dtype='<f8')
                    logging.debug(f'actual size of covariance matrix {f[key].shape}')
                    self.values[:,:,:,:,:] = scale * f[key][xslice, yslice, :, :, :]
                    self.show_info(self.name, f[key])
                else:
                    logging.error('Wrong parameter key')
                    
            logging.debug('extraction of climatic brdf ' + str(self.values[0,0,0]))
            return self
        except Exception as e:
            logging.error('Problem reading BRDF climato file "' +
                          str(filenames) + '" ' + str(e))
            raise(e)
