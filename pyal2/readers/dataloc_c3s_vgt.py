import logging
from datetime import datetime
from datetime import timedelta
import netCDF4
from pyal2.utils.parsing import glob_list


# The list of parameters in the dataloc_reader_function
datetime_params = ['filenames', 'input_startdate_key', 'input_enddate_key']
metadata_params = ['key']

def dataloc_reader_function(output_dates, filenames, input_startdate_key, input_enddate_key, key):
    """ This function reads the dates of a list of input file patterns and create a dictionnary of dataloc : {input_date -> filename}. 
    It also uses additional parameters, as defined in the config file : input_startdate_key, input_enddate_key, key.
    It also read some metadata information (sizes of the input).
    Input :
        output_dates        (this parameter is included by default) : list of output date to process. This is the dates of the output file names. There is one date for each time step to process.
    The following parameters must be defined in the lists 'datetime_params' or 'metadata_params' above :
        filenames           : list of filename patterns to use as input.
        input_startdate_key : key in the input file used to compute the date of the files
        input_enddate_key   : key in the input file used to compute the date of the files
        key                 : key in the input file used to read the meta data
    Output :
        A dictionnary {input_date: {'filename' : filename} } to find a file from a date.
        A dictionnary of metadata.
    See the .yaml files generated by the to_yaml functions to have an example.
        """
    dataloc = {}
    metadata = {}
    # glob all files : from the list "filenames", find all existing files whose filename matches a date in "output_dates"
    filenameslist = glob_list(filenames, output_dates)
    for filename in filenameslist:
        # open each file in the filenameslist
        try:
            f = netCDF4.Dataset(filename, 'r')
            try:
                # try reading the dates in the expected format
                datefirst = datetime.strptime(f.getncattr(input_startdate_key), '%Y%m%d')
                datelast = datetime.strptime(f.getncattr(input_enddate_key), '%Y%m%d')
            except ValueError:
                # if this does not work, try reading the dates in another format
                datefirst = datetime.strptime(f.getncattr(input_startdate_key), '%Y/%m/%d %H:%M:%S')
                datelast = datetime.strptime(f.getncattr(input_enddate_key), '%Y/%m/%d %H:%M:%S')
                # if this fails, an exception will be raised (and the file will be skipped with an error message, see below)
            dateaverage = datefirst + (datelast - datefirst) / 2.

            # floor to the second to have a integer number of seconds
            dateaverage = datetime(dateaverage.year, dateaverage.month,dateaverage.day, dateaverage.hour, dateaverage.minute, dateaverage.second)

            dataloc[dateaverage] = {'filename': filename}

            # advice : in case there are several dates in the same file, the following pattern can be used :
            # list_with_all_dates_in_file = ...
            # for i, date in enumerate(list_with_all_dates_in_file):
            #    dataloc[date] = {'filename': filename}

            if not metadata:
                # do this only once
                # read the size of the input
                # hint: this may be also the right place to read other input metadata
                if len(f[key].shape) == 3:
                    metadata['xoutputsize'] = f[key].shape[1]
                    metadata['youtputsize'] = f[key].shape[2]
                elif len(f[key].shape) == 2:
                    metadata['xoutputsize'] = f[key].shape[0]
                    metadata['youtputsize'] = f[key].shape[0]
                else:
                    logging.error('Shape of data matrix is wrong')
            f.close()
        except Exception as e:
            logging.error('Cannot process file ' + filename + ' to get the dates using keys : (' + str(input_startdate_key) + ',' + str(input_enddate_key) + ') : ' + str(e))
    logging.info(f'Found {len(dataloc)} dates in {filenames}')
    if not len(dataloc):
        logging.error(f'Cannot find input data. Processing anyways.')
    return dataloc, metadata
