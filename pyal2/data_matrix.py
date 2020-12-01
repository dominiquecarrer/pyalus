import numpy as np

class DataMatrixFloat():
    """ This class is Wrapper aroud a matrix containing data. We choose this technique, called 'boxing', to put each array in a box (the box here is the DataMatrixFloat object) in order to :
     - Access the data through the .values attribute. Which is consistent with xarray and make things easier for debugging, visualisation and potentially to switch to xarray
     - Be able to add metadata easily without creating additional variables. Typical example is storing the missing values along with its data. This is the paradigm advocated by the netCDF group.
     - Be able to trace the data or additional parameter to store next to the data
     """
    def __init__(self, data=None):
        if not data is None: self.values = data
    def full(self, shape, dtype, value = np.nan):
        self.values = np.full(shape, value, order = 'F', dtype = dtype)
        return self

class DataMatrixInteger():
    """ Almost identical to DataMatrixFloat. Notice the default value in the full(...) function : '0' instead of '0.' """
    def __init__(self, data=None):
        if not data is None: self.values = data
    def full(self, shape, dtype, value = 0):
        self.values = np.full(shape, value, order = 'F', dtype = dtype)
        return self

