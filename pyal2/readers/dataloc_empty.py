import logging
from datetime import datetime
from datetime import timedelta
import netCDF4
from pyal2.utils.parsing import glob_list


# The list of parameters in the dataloc_reader_function
datetime_params = ['input_dates', 'xoutputsize', 'youtputsize']
metadata_params = []

def dataloc_reader_function(output_dates, input_dates, xoutputsize, youtputsize):
    """ This function reads the dates of a list input file, a list of input_dates. And output a dictionnary of dataloc : {input_date -> filename}
    Input :
        output_dates        (this parameter is included by default) : list of output date to process. This is the dates of the output file names. There is one date for each time step to process.
                            For this reader, there MUST be only one date. This has been done to compare the current code to the previous fortran code which only work with one output date.
    The following parameters must be defined in the lists 'datetime_params' or 'metadata_params' above :
        input_dates         : list of input dates for each scene.
        xoutputsize         : should be 3712 in the config file
        youtputsize         : should be 3712 in the config file
    Output :
        A dictionnary {input_date:filename} to find a file from a date.
        A dictionnary of metadata hard coded to 
        """
    dataloc = {}
    metadata = {}
    return dataloc, metadata
