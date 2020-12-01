#!/usr/bin/env python 
import logging
import numpy as np
from datetime import datetime
from datetime import timedelta

from pyal2 import __version__
from pyal2.utils.augmented_netcdf import AugmentedNetcdfDataset
from pyal2.data_matrix import DataMatrixFloat, DataMatrixInteger
from pyal2.utils.io import ensure_dir

data_params = ['filename']

class BrdfReader(dict):
    """ This class read a BRDF file """

    def load_brdf(self, filename, model_len, n_channels_ref, xslice, yslice):
        self.filename = filename
        self.infer_params(xslice, yslice)
        logging.info('Reading BRDF and qflag from ' + self.filename) # + str(date))
        try:
            with AugmentedNetcdfDataset(self.filename,'r') as f:
                # TODO : honor the missing values and set to np.nan
                self.previous_date = datetime.strptime(f.getncattr('DATE'), '%Y%m%d-%M%S')
                self.latitude    = DataMatrixFloat(f['latitude'][self.xslice, self.yslice])
                self.longitude   = DataMatrixFloat(f['longitude'][self.xslice, self.yslice])
                self.brdf        = DataMatrixFloat(f['K012'][self.xslice, self.yslice,:,:])
                self.covariance  = DataMatrixFloat(f['CK'][self.xslice, self.yslice,:,:,:])
                self.quality     = DataMatrixInteger(f['Z-QFLAG'][self.xslice, self.yslice,:])
                self.age_obs     = DataMatrixInteger(f['Z-AGE'][self.xslice, self.yslice,:])
                self.n_valid_obs = DataMatrixInteger(f['Z-NMOD'][self.xslice, self.yslice])
        except Exception as e:
            logging.error('Problem reading brdf file "' + str(self.filename) + '" ' + str(e))
            raise(e)

    def infer_params(self,xslice=None,yslice=None):
        """ Infer brdf parameters, size, slices, from the file. If xslice and yslice are given, use them instead of infering the full size of the brdf file """
        try:
            # open the brdf file as a netcdf
            with AugmentedNetcdfDataset(self.filename,'r') as f:
                # read the model_id from the attributes
                self.model_id = f.getncattr("BRDF_MODEL_ID")
                logging.info(f'Reading brdf config from brdf file : model id = {self.model_id}')

                # use the layer "CK" to get the sizes
                shape = f['CK'].shape
                if xslice is None:
                    # if xslice is unknown, defined it to be the whole range in the file
                    self.xslice = slice(0,shape[0])
                    logging.info(f'Reading brdf config from brdf file : xslice = {self.xslice}')
                else:
                    # else, use the rovided value
                    self.xslice = xslice
                if yslice is None:
                    # if yslice is unknown, defined it to be the whole range in the file
                    self.yslice = slice(0,shape[1])
                    logging.info(f'Reading brdf config from brdf file : yslice = {self.yslice}')
                else:
                    # else, use the rovided value
                    self.yslice = yslice

                # read also the number of bands in the brdf file
                self.n_channels_ref = shape[2]
                logging.info(f'Reading brdf config from brdf file : n_channels_ref = {self.n_channels_ref}')

                # read also the model_len from the brdf file
                self.model_len = shape[3]
                logging.info(f'Reading brdf config from brdf file : model_len = {self.model_len}')

        except Exception as e:
            logging.error('Problem reading brdf file "' + str(self.filename) + '" ' + str(e))
            raise(e)

    #def read_albedo(self, xslice, yslice):
    #    """ Read albedo output file. This is not used in production. But has been added for sake of completion and to validate and plot output data. not tested """
    #    #brdf_io = BrdfIO(dm, self.current_startseries)
    #    #brdf_io.read_albedo(xslice, yslice)
    #    n_outalbedos_names = len(self.outalbedos_names)
    #    n_inalbedos_names = len(self.inalbedos_names)
    #    self.outalbedos         = np.zeros((xslice.stop - xslice.start, yslice.stop - yslice.start, n_inalbedos_names, n_outalbedos_names), order='F', dtype='f4')
    #    self.outalbedos_cov     = np.zeros((xslice.stop - xslice.start, yslice.stop - yslice.start, n_inalbedos_names, n_outalbedos_names), order='F', dtype='f4')
    #    logging.info('Reading Albedo from ' + self.outfilename_albedo) # + str(date))
    #    try:
    #        with AugmentedNetcdfDataset(self.outfilename_albedo,'r') as f:
    #            for iout, outname in enumerate(self.outalbedos_names):
    #                for iin, inname in enumerate(self.inalbedos_names):
    #                    fullname = inname + '-' + outname
    #                    self.outalbedos[:,:,iin, iout] = f['AL-' + fullname][xslice, yslice]
    #                    self.outalbedos_cov[:,:,iin, iout] = f['AL-' + fullname + '-ERR'][xslice, yslice]

    #            self.albedos_age     = f['age'][xslice, yslice,:,:]
    #            self.albedos_quality = f['quality'][xslice, yslice,:,:]
    #    except Exception as e:
    #        logging.error('Problem reading albedo file "' + str(self.outfilename_albedo) + '" ' + str(e))
    #        raise(e)
