#!/usr/bin/env python 
from pyal2.readers.generic import GenericReader
import logging
import numpy as np
import h5py

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
        # note that we loop until one read is successful because we expect the latitude to be the same for each scene date
        # in order to ensure this, we could add a security check (read each date and compare to the latest one).
        for idate, d in enumerate(scenes_dates):
            filename = dataloc[d]['filename']

            # save filename for debug purposes
            self.filenames[d] = filename
            logging.debug(str(d) + ' ' + filename )

            try:
                # actual reading of the data
                f = h5py.File(filename, 'r')
                dataset = f[key]

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
                self.values[:,:] = data

                self.show_info(self.name, f[key])

                f.close()
                # return as soon as a file has been successfully read
                logging.debug('extract of ' + key + ' data = '+str(self.values[0,0]))
                return self
            except Exception as e:
                # if anything bad happenned when reading the data
                logging.info(f'Problem reading {filename} for the key {key}' + ' to get the ' + self.name + ' ' + str(e))
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
