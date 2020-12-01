import logging
import numpy as np
from pyal2.readers.generic import GenericReader
from pyal2.utils.augmented_netcdf import AugmentedNetcdfDataset

data_params = ['key']

class Angle(GenericReader):
    """ Reader for Angle data (VAA VZA SZA SAA), and similar data. """
    def load(self, key, xslice, yslice, scenes_dates, dataloc):
        # save dates for debug purposes
        self.scenes_dates = scenes_dates

        # initialise empty matrix of the right size, with nan values (this assumes that xslice.step = 1 or None)
        shape = (xslice.stop - xslice.start, yslice.stop - yslice.start,max(1,len(self.scenes_dates)))
        self.values = np.full(shape, np.nan, order='F', dtype='<f4')

        # loop through all each input scene date

        for idate, d in enumerate(scenes_dates):
            filename = dataloc[d]['filename']

            # save filename for debug purposes
            self.filenames[d] = filename
            logging.debug(str(d) + ' ' + filename )

            try:
                # actual reading of the data
                with AugmentedNetcdfDataset(filename,'r') as f:
                    # TODO : honor the missing values and set to np.nan
                    scale, offset = f[key].getncattr("SCALE"), f[key].getncattr("OFFSET")
                    # first dimension is the date, there is only one date per file. Therefore we have a 0 here
                    data = f[key][0,xslice,yslice]
                    data = (data / scale) - offset
                    # just to make sure, recenter the data. This is not needed but is an additional security.
                    # TODO : remove it if it is not needed
                    data[data > 180] -= 360
                    data[data < -180] += 360
                    # put the data in the right place in the full matrix
                    # Note : we are using the intermediate variable "data" 
                    # because it may be slower to work directly with the full matrix if the data for one date is not contigous.
                    self.values[:,:,idate] = data
                    self.show_info(self.name, f[key])
            except Exception as e:
                # if anything bad happenned when reading the data
                logging.info('Problem reading ' + filename + '/' + 'key' + ' to get the ' + self.name + ' ' + str(e))
                # just log the problem and skip the date
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
