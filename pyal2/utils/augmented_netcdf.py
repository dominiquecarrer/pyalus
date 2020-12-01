#!/usr/bin/env python 
import netCDF4
class AugmentedNetcdfDataset(netCDF4.Dataset):
    """ This class is a slight modification of the standard netCDf4 Dataset, adding a few convient methods. Notice the write lock limitation. """

    def __init__(self, *args, **kwargs):
        super(AugmentedNetcdfDataset, self).__init__(*args, **kwargs)
        self.set_auto_maskandscale(False)


    def createVariableIfNotExists(self, *args,**kwargs):
        """ Create a variable in a netCDF file if it does not already exists. Note: this is not multiprocess safe. The write lock must be acquired before running this """
        key = args[0]
        attributes = kwargs.pop('attributes', {})
        if key in self.variables.keys():
            var = self.variables[key]
            var.set_auto_mask(False)
            var.set_auto_scale(False)
        else:
            var = self.createVariable(*args,**kwargs)
            var.set_auto_mask(False)
            var.set_auto_scale(False)
            for k,v in attributes.items():
              var.setncattr(k,v)
        return var

    def createDimensionIfNotExists(self, *args,**kwargs):
        """ Create a dimensions in a netCDF file if it does not already exists. Note: this is not multiprocess safe. The write lock must be acquired before running this """
        key = args[0]
        if key in self.dimensions.keys():
            return self.dimensions[key]
        else:
            return self.createDimension(*args,**kwargs)
