#!/usr/bin/env python 
from pyal2.readers.generic import GenericReader
import logging
import numpy as np
import netCDF4 as nc

data_params = ['key']

class Latitude(GenericReader):
    """ Reader for Angle data (VAA VZA SZA SAA), and similar data. """
    def load(self, key, xslice, yslice, scenes_dates, dataloc):
        # save dates for debug purposes
        self.scenes_dates = scenes_dates

        # initialise empty matrix of the right size, with nan values (this assumes that xslice.step = 1 or None)
        shape = (xslice.stop - xslice.start, yslice.stop - yslice.start)
        self.values = np.full(shape, np.nan, order='F', dtype='<f4')

        # loop through all each input scene date
        # note that we loop until one read is successful because we 
        # expect the latitude to be the same for each scene date
        # in order to ensure this, we could add a security check 
        # (read each date and compare to the latest one).
        for idate, d in enumerate(scenes_dates):
            filename = dataloc[d]['filename']

            # save filename for debug purposes
            self.filenames[d] = filename
            logging.debug(str(d) + ' ' + filename )

            try:
                # actual reading of the data
                f = nc.Dataset(filename, 'r')
                dataset = f.variables[key]

                # read the values
                data = dataset[0, xslice, yslice]

                # convert to float
                data = data.astype('<f4') 

                # put the data in the right place in the full matrix
                self.values[:,:] = data

                self.show_info(self.name, f.variables[key])

                f.close()
                # return as soon as a file has been successfully read
                logging.debug('extract of ' + key + ' data = '+str(self.values[0,0]))
                return self
            except Exception as e:
                # if anything bad happenned when reading the data
                logging.info(f'Problem reading {filename} for the key {key}' +
                        ' to get the ' + self.name + ' ' + str(e))
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
