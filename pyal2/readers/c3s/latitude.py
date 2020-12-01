#!/usr/bin/env python 
from pyal2.readers.generic import GenericReader
import logging
import numpy as np
from pyal2.utils.augmented_netcdf import AugmentedNetcdfDataset
from pyal2.exit_status import exit_status
from pyal2.utils.parsing import last_day_of_the_month, robust_date_parse, parse_boolean, parse_command_line_dates
from pyal2.utils.dict_utils import instanciate_datetime
from copy import deepcopy

data_params = ['key', 'inputcheckpoint']

class Latitude(GenericReader):
    """ Reader for Latitude data  and similar data. """
    def load(self, key, inputcheckpoint, xslice, yslice, scenes_dates, dataloc):
        # save dates for debug purposes
        self.scenes_dates = scenes_dates

        # initialise empty matrix of the right size, with nan values (this assumes that xslice.step = 1 or None)
        shape = (xslice.stop - xslice.start, yslice.stop - yslice.start)
        self.values = np.full(shape, np.nan, order='F', dtype='<f8')

        if len(scenes_dates) == 0:
            # hack : if no scenes, we still need to get the latitude to compute
            # theta_sol_midi in albedo_angular_integration.f90
            filename = inputcheckpoint['filename']
            firstdate = robust_date_parse(inputcheckpoint['firstdate'])
            filename = instanciate_datetime(deepcopy(filename), firstdate)
            logging.warn('No data. Using latitude from file ' + filename)
            try:
                with AugmentedNetcdfDataset(filename,'r') as f:
                    self.values[:,:] = f['latitude'][xslice, yslice]
                    return self
            except FileNotFoundError:
                logging.error('Apparently there is no input data scenes for this date. There is no BRDF checkpoint file either. The algorithm cannot be initialized with no input data') 
                exit_status('UNABLE_TO_CONFIG')
            return

        # loop through all each input scene date
        # note that we loop until one read is successful because we expect the
        # latitude to be the same for each scene date
        # in order to ensure this, we could add a security check (read each
        # date and compare to the latest one).
        for idate, d in enumerate(scenes_dates):
            filename = dataloc[d]['filename']

            # save filename for debug purposes
            self.filenames = {d:filename}
            logging.debug(str(d) + ' ' + filename )

            try:
                # actual reading of the data
                # TODO : honor the missing values and set to np.nan
                with AugmentedNetcdfDataset(filename,'r') as f:
                    self.values[:,:] = f[key][xslice, yslice]
                    self.show_info(self.name, f[key])
                logging.debug('extract of ' + key + ' data = '+str(self.values[0,0]))
                # return as soon as a file has been successfully read
                return self
            except KeyError as e:
                # if anything bad happend when reading the data
                logging.info('Problem reading ' + filename + '/' + 'key' + ' to get the ' + self.name + ' ' + str(e))
                # just log the problem and skip it

        # if no files could be loaded successfully, show an error message
        logging.error('Cannot read files for "' + str(key) + '" : input files location are : ' + str(dataloc))
        return self

    def to_xr(self):
        """ xarray serialisation """
        import xarray as xr
        return xr.DataArray(self.values[:,:],
                dims = ['x', 'y'],
                name = self.name,
                attrs = { 'filenames': self.filenames })
