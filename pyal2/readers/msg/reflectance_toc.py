#!/usr/bin/env python 
from pyal2.readers.generic import GenericReader
import logging
import numpy as np
import h5py

data_params = ['key']

class ReflectanceOneBand(GenericReader):
    """ Reader for Reflectance data, for one band only. """
    def load(self, key, xslice, yslice, scenes_dates, dataloc):
        # save dates for debug purposes
        self.scenes_dates = scenes_dates

        # initialise empty matrix of the right size, with nan values (this assumes that xslice.step = 1 or None)
        shape = (xslice.stop - xslice.start, yslice.stop - yslice.start,max(1,len(scenes_dates)))
        self.values = np.full(shape, np.nan, order='F', dtype='<f4')

        # loop through all each input scene date
        for idate, d in enumerate(scenes_dates):
            filename = dataloc[d]['filename']

            # save filename for debug purposes
            self.filenames[d] = filename
            logging.debug(f'Reading {d} : {filename}')

            try:
                # actual reading of the data
                f = h5py.File(filename, 'r')
                dataset = f[key]
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
                # Note : we are using the intermediate variable "data" because it may be slower to work directly with the full matrix if the data for one date is not contigous.
                self.values[:,:,idate] = data

                self.show_info(self.name, f[key])

                f.close()
            except Exception as e:
                # if anything bad happenned when reading the data
                logging.info(f'Problem reading ' + filename + '/' + 'key' + ' to get the ' + self.name + ' ' + str(e))
                # just log the problem and skip it
                continue
        logging.debug('extract of ' + key + ' data = '+str(self.values[0,0,:]))
        return self

    def to_xr(self):
        """ xarray serialisation """
        import xarray as xr
        return xr.DataArray(self.values[:,:,:],
                dims = ['x', 'y', 'scenedatetime'],
                name = self.name,
                coords= { 'scenedatetime': self.scenes_dates },
                attrs = { 'filenames': self.filenames })
