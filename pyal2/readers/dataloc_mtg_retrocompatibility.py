import logging
from datetime import datetime
from datetime import timedelta
import netCDF4
import os

from pyal2.utils.parsing import glob_list


# The list of parameters in the dataloc_reader_function
#~ datetime_params = ['filenames', 'input_dates', 'xoutputsize', 'youtputsize']
datetime_params = ['filenames',  'input_startdate_key', 'input_enddate_key', 'xoutputsize', 'youtputsize']
metadata_params = []

def dataloc_reader_function(output_dates, filenames,input_startdate_key, input_enddate_key, xoutputsize, youtputsize):
    """ This function reads the dates of a list input file, a list of input_dates. And output a dictionnary of dataloc : {input_date -> filename}
    Input :
        output_dates        (this parameter is included by default) : list of output date to process. This is the dates of the output file names. There is one date for each time step to process.
                            For this reader, there MUST be only one date. This has been done to compare the current code to the previous fortran code which only work with one output date.
    The following parameters must be defined in the lists 'datetime_params' or 'metadata_params' above :
        filenames           : list of filenames for each scene
        input_dates         : list of input dates for each scene.
        xoutputsize         : should be 3712 in the config file
        youtputsize         : should be 3712 in the config file
    Output :
        A dictionnary {input_date:filename} to find a file from a date.
        A dictionnary of metadata hard coded to 
        """
    dataloc = {}
    metadata = {'xoutputsize':xoutputsize, 'youtputsize':youtputsize}
    for filename in filenames:
        # open each file in the filenameslist
        try:
            f = netCDF4.Dataset(filename, 'r')
            try:
                # try reading the dates in the expected format
                datefirst = datetime.strptime(f.getncattr(input_startdate_key), '%Y-%m-%d %H:%M')
                datelast = datetime.strptime(f.getncattr(input_enddate_key), '%Y-%m-%d %H:%M')
            except:
                # if this does not work, try reading the dates in another format, in the file name indeed
                datefirst = datetime.strptime(filename.split('.')[-2][-12:], '%Y%m%d%H%M')
                datelast = datetime.strptime(filename.split('.')[-2][-12:], '%Y%m%d%H%M')
                # if this fails, an exception will be raised (and the file will be skipped with an error message, see below)
            dateaverage = datefirst + (datelast - datefirst) / 2.

            # floor to the second to have a integer number of seconds
            dateaverage = datetime(dateaverage.year, dateaverage.month,dateaverage.day, dateaverage.hour, dateaverage.minute, dateaverage.second)
            dataloc[dateaverage] = {'filename': filename}
            f.close()
        except Exception as e:
            logging.error('Cannot process file ' + filename + ' to get the dates using keys : (' + str(input_startdate_key) + ',' + str(input_enddate_key) + ') : ' + str(e))

    return dataloc, metadata
