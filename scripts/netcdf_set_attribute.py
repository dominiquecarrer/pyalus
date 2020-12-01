#!/usr/bin/env python
import argparse
import netCDF4
from datetime import datetime
import os
import logging
from shutil import copyfile


def ensure_dir(filename=None):
    dirname = os.path.dirname(filename)
    if dirname != '' and not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except NotADirectoryError as e:
            logging.error(f'Cannot create directory {dirname} : A file with the same name may already exist.')
            raise(e)
        except Exception as e:
            if not os.path.exists(dirname):
                raise(e)

def robust_parse_date(date):
    try:
        return datetime.strptime(date, '%Y%m%d')
    except ValueError:
        try:
            return datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(date, '%d-%m-%Y')
            except ValueError:
                try:
                    return datetime.strptime(date, '%Y/%m/%d')
                except ValueError:
                    return datetime.strptime(date, '%Y%m%d-%M%S')

def instanciate_filename(filename, date=None):
    """ instanciate a filename if needed.
    >>> instanciate_filename('foo%Y:19990705')
    ['foo1999', datetime(1999,7,5)]
    >>> instanciate_filename('foo%Y:19990705', datetime(1950,1,1))
    ['foo1950', datetime(1950,1,1)]
    """
    if '@' in filename:
        filename, date = filename.split('@')
    if not date is None:
        date = robust_parse_date(date)
        filename = date.strftime(filename)
    return filename, date


parser = argparse.ArgumentParser(description='Copy a netcdf file and set value of a given attribute in netCDF file.')
parser.add_argument('-i', '--inputfile', help='input filename', required=True)
parser.add_argument('-o', '--outputfile', help='output filename', required=True)
parser.add_argument('-d', '--newdate', help='New date value, not that DATE is always written in a given format. For instance 19991231-0000. You can also specify ":-1Y"')
args = parser.parse_args()

newdate = args.newdate

if 'fromsensorname_start_date' in newdate: # special value : 1 year less
    from sensor_constants import sensor_constants
    _ , sensorname = newdate.split(':')
    olddate = sensor_constants[sensorname]['date_end_spinoff']
    # ~ newdate = sensor_constants[sensorname]['date_start']
    # ~ newdate = robust_parse_date(newdate)
    # ~ newdate = newdate.strftime('%Y%m%d-%M%S')
# ~ else:
    # ~ # Untested code :
    # ~ # TODO -> test !!!
    # ~ olddate = None
    # ~ newdate = robust_parse_date(newdate)
    # ~ newdate = newdate.strftime('%Y%m%d-%M%S')

args.inputfile, date_of_inputfile = instanciate_filename(args.inputfile, olddate)

inf = netCDF4.Dataset(args.inputfile, 'r')
k = 'DATE'
oldv = inf.getncattr(k)
print(f'Previous value : {k} = {oldv}')
oldv = datetime.strptime(oldv, '%Y%m%d-%M%S')

if not(date_of_inputfile is None) and oldv != date_of_inputfile:
    print(f'Beware, input filename does not match its attribute date : {date_of_inputfile} != {oldv}')

# ~ if newdate == ':-1Y': # special value : 1 year less
newdate = datetime(oldv.year - 1, oldv.month, oldv.day, oldv.hour, oldv.minute, oldv.second)
newdate = newdate.strftime('%Y%m%d-%M%S')
# ~ else: # other value, parse the new value for date
    # ~ newdate = robust_parse_date(newdate)
    # ~ newdate = newdate.strftime('%Y%m%d-%M%S')
print(f'New value : {k} = {newdate}')
inf.close()
print(f'{args.inputfile} has been read')


args.outputfile, _ = instanciate_filename(args.outputfile, newdate)
ensure_dir(args.outputfile)
copyfile(args.inputfile, args.outputfile)

outf = netCDF4.Dataset(args.outputfile, 'a')
outf.setncattr_string(k,newdate)
outf.close()
print(f'{args.outputfile} has been written')


