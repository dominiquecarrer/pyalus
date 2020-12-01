import glob
import re
import logging
from datetime import datetime
from datetime import timedelta
import calendar

def glob_list(filepatterns, duplicate_with_dates=None, log_error_on_empty = True, sort=True):
    """ This method take a list of file patterns and return a unique sorted list 
    of file matching one of the pattern. If duplicate_with_dates is provided,
     the patterns are duplicated and instanciated for each date using datetime.strftime() """
    # if input is not a list, transform it into a list
    if not isinstance(filepatterns, list):
        filepatterns = [filepatterns]
    # duplicate with dates if requested
    if not duplicate_with_dates is None:
        filepatterns2 = []
        for f in filepatterns:
            filepatterns2 += [date.strftime(f) for date in duplicate_with_dates]
        filepatterns = filepatterns2
    # find all file matching pattern
    globbedlist = []
    for f in filepatterns:
        globbedlist += glob.glob(f)
    # make list unique (and sort to make it more reproducible)
    if sort:
        globbedlist = sorted(list(set(globbedlist)))
    # basic check if requested
    if log_error_on_empty and len(globbedlist) == 0:
        logging.error('Found 0 file matching patterns {filepatterns}'.format(filepatterns=filepatterns))
    return globbedlist

def parse_command_line_dates(args_dates):
    """ Parse a list of one or two dates, provided as string, and transform them into real datetime object """
    if not args_dates: return None
    if not isinstance(args_dates, list): raise Exception('Wrong type for args_dates, must be a list')
    if len(args_dates) == 2:
        # if two dates are given in command line, used them as start and end date
        date_start, date_end = [robust_date_parse(date) for date in args_dates]
    if len(args_dates) == 1:
        # if a csv file is given in command line, used it to get the start and end date
        import pandas as pd
        filename, satname, keystart, keyend = re.search('file://(.*)@(.*):([a-zA-Z_0-9]*):([a-zA-Z_0-9]*)', args_dates[0]).groups()
        data = pd.read_csv(filename)
        data = data.set_index(['sensor'])
        data = data.loc[satname]
        date_start, date_end = [self._parse_date(date) for date in [data[keystart], data[keyend]]]
        logging.info(f'Dates provided in file {filename} at line {satname} : {keystart}={date_start}, {keyend}={date_end}')
    dates = [date_start, date_end]
    logging.info('Dates provided from command line ' +  str(dates))
    return dates

def robust_date_parse(date):
    """ Robust parsing to find a date : from a string with 12 digits, 8 digits or from a filename ending with such a string. """
    logging.debug(f'Parsing {date}')
    if len(date) == 19:
        return datetime.strptime(date,'%Y/%m/%d/%H:%M:%S')
    if len(date) == 16:
        return datetime.strptime(date,'%Y/%m/%d/%H:%M')
    if len(date) == 14:
        return datetime.strptime(date,'%Y%m%d%H%M%S')
    if len(date) == 12:
        return datetime.strptime(date,'%Y%m%d%H%M')
    if len(date) == 10:
        try:
            return datetime.strptime(date,'%Y/%m/%d')
        except ValueError:
            try:
                return datetime.strptime(date,'%Y-%m-%d')
            except ValueError:
                return datetime.strptime(date,'%d-%m-%Y')
    if len(date) == 8:
        return datetime.strptime(date,'%Y%m%d')
    date = re.sub('.h5$', '', date)
    try:
        return datetime.strptime(date[-12:],'%Y%m%d%H%M')
    except ValueError:
        return datetime.strptime(date[-8:],'%Y%m%d')

def last_day_of_the_month(date):
    return calendar.monthrange(date.year, date.month)[1]

def parse_boolean(arg_value, default_value=None, name=None):
    """ Parse a boolean parameter from string into boolean, with default_value """
    if arg_value is None:
        return default_value
    elif arg_value == True:
        return True
    elif arg_value == False:
        return False
    elif arg_value.lower() == 'true':
        return True
    elif arg_value.lower() == 'false':
        return False
    else:
        raise Exception('Unknown value to convert to boolean ' + (name or '') + ' = ' + arg_value)
