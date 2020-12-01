#!/usr/bin/env python3
from datetime import datetime
from datetime import timedelta
import argparse
import calendar
import f90nml
import glob
import logging
import math
import numpy as np
import os
import re
import sys
import time

try:
    import coloredlogs, logging
except ImportError:
    import logging

def last_day_of_the_month(date):
    return calendar.monthrange(date.year, date.month)[1]

# TODO : most of this file should be cleaned up, deleted, etc
class ConfigCreatorGeneric(dict):
    """ This class provides set of useful function to handle configuration management for all projects """
    def __init__(self, keywords=None):
        if keywords is None: keywords = {}
        self.keywords = keywords

    def instanciating_filename_helper(self, date, v, hacky_str_dict):
        v = v.format(**self.keywords)
        for hacky_str, newdate in hacky_str_dict.items():
            if v[-len(hacky_str):] == hacky_str:
                date = newdate
                v = v[:-len(hacky_str)]
        return date.strftime(v)

    def instanciate_keywords(self, value):
        if isinstance(value, str):
            value = value.format(**self.keywords)
            return value
        if isinstance(value, dict):
           for k,v in value.items():
               value[k] = self.instanciate_keywords(v)
        if isinstance(value, list):
           value = [self.instanciate_keywords(v) for v in value]
        return value


def parse_args():
    parser = argparse.ArgumentParser(description='This script instanciates a generic pcf config file into several pcf files. Each generated file is specific to one given date.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('generic', help='Generic pcf file')
    parser.add_argument('--dates', nargs='+', help='date start and end')
    parser.add_argument('--keywords', nargs='+', help="keyword to replace in config file")
    parser.add_argument('--loglevel', help='log level. CRITICAL ERROR WARNING INFO or DEBUG', default='INFO')
    parser.add_argument('--input-complete-scene-only', nargs='+', help='Check carefully the output in debug mode to make sure that this is what you want to do. For msg and eps: yfileinp 7 7')
    parser.add_argument('--filterdate', help='Filter date according to the sensor you are considering. Supported values : msg, eps')
    parser.add_argument('--check-h5', type=int, help='level of verbosity if the input files are uncorrupted hdf5 files. 0 : no check. 1 or more : deeper check.', default=0)
    parser.add_argument('--outdir', required=True, help='Output directory where the instanciated files will be generated')
    args = parser.parse_args()

    # Processing args and config
    coloredlogs.install(level=args.loglevel.upper())
    return args

def args_for_test():
    """Used to feed arguments manually when testing the script in spyder"""
    generic = '/cnrm/vegeo/lellouchg/experiments/NO_SAVE/ori_vs_new_coefandbrdf/pcf_config/pcf.eps.genericdate'
    dates = ['20160604','20161226']
    keywords = None
    loglevel = 'INFO'
    input_complete_scene_only = ['yfileinp','7','7']
    check_h5 = 0 
    outdir = 'config-bis'
    filterdate = 'eps'
    return generic, dates, keywords, loglevel, input_complete_scene_only, check_h5, outdir, filterdate

class EmptyList(Exception):
    pass

def remove_incomplete_scenes(l, check_function, offset=0, block_size=1, verbose=True):
    """
    This will read the list l assuming it is a list of blocks, check each element (using check_function) and remove the block containing the faulty element and return a new list.
    For instance :

    >>> remove_incomplete_scenes(l = [100,100,1,2,3,4,5,6,7,-1,9], check_function = (lambda x: x>0), offset=2, block_size=3, verbose=False)
    [100, 100, 1, 2, 3, 4, 5, 6]

    The last block (3 elements) has been removed because one scene (-1) is not valid.
    """

    outlist = []
    # keep all elements before ignore_start_lines
    outlist = l[0:offset]

    # then process each block
    n_block = (len(l)-offset ) //block_size
    for i in range(offset, len(l), block_size):
        i_block = (i-offset) // block_size
        # take a block of element
        block = l[i:(i+block_size)]
        # check each element
        check = {}
        for elt in block:
            check[elt] = check_function(elt)
        if all(check.values()):
            # add them if all are good
            outlist = outlist + block
        else:
            # do not add else
            for elt in block:
                if not check[elt]:
                    if verbose: logging.warn(str(i) + ' : Removing block '+ str(i_block) + ' because element does not comply with the check function : ' + str(elt))
    if len(outlist) == offset:
        raise EmptyList()
    return outlist

def filter_date_eps(date):
    # return True if the date is ok for eps
    return (date.day == 5 or date.day == 15 or date.day == 25)

def find_previous_date_eps(date):
    curr = date
    curr = curr - timedelta(days=1)
    while not filter_date_eps(curr):
        curr = curr - timedelta(days=1)
    return curr

def find_date_range_eps(date_start, date_end):
    dates = []
    curr = date_start
    while curr <= date_end:
        if filter_date_eps(curr):
            dates.append(curr)
        curr = curr + timedelta(days=1)
    return dates

def find_date_range_msg(date_start, date_end):
    dates = []
    curr = date_start
    while curr <= date_end:
        dates.append(curr)
        curr = curr + timedelta(days=1)
    return dates

def main():

# load parameters
    if 'MF_TESTING_ENABLED' in os.environ or 'SPYDER_ARGS' in os.environ: 
        # the variable 'SPYDER_ARGS' is enabled when runnning the script in spyder (with the big green arrow) to test the script
        # the variable MF_TESTING_ENABLED is unused for now
        print('---------------------------------------\n|       Testing args were used           |\n---------------------------------------')      
        generic, dates, keywords, loglevel, input_complete_scene_only, check_h5, outdir, filterdate = args_for_test()
    else:
        args = parse_args()
        print('---------------------------------------\n|    Command line args were used      |\n---------------------------------------')
        dates = args.dates
        generic = args.generic
        keywords = args.keywords     
        loglevel = args.loglevel
        input_complete_scene_only = args.input_complete_scene_only
        check_h5 = args.check_h5
        outdir = args.outdir
        filterdate = args.filterdate

    datestart = datetime.strptime(dates[0], '%Y%m%d')
    dateend = datetime.strptime(dates[1], '%Y%m%d')
    tool = ConfigCreatorGeneric(keywords)

    missing_dates = 0
    # define eps dates [05,15,25] for the period of interest
    if filterdate.upper() == 'EPS':
        dates = find_date_range_eps(datestart,dateend)
    elif filterdate.upper() == 'MSG':
        dates = find_date_range_msg(datestart,dateend)
    else:
        raise Exception(f'Unsupported option {filterdate}')

    for idate, date in enumerate(dates):
        replacedict = {'#-19 day': date - timedelta(days=missing_dates+19),'#-18 day': date - timedelta(days=missing_dates+18),'#-17 day': date - timedelta(days=missing_dates+17),'#-16 day': date - timedelta(days=missing_dates+16),'#-15 day': date - timedelta(days=missing_dates+15),'#-14 day': date - timedelta(days=missing_dates+14),'#-13 day': date - timedelta(days=missing_dates+13),'#-12 day': date - timedelta(days=missing_dates+12),'#-11 day': date - timedelta(days=missing_dates+11),'#-10 day': date - timedelta(days=missing_dates+10),'#-9 day': date - timedelta(days=missing_dates+9),'#-8 day': date - timedelta(days=missing_dates+8),'#-7 day': date - timedelta(days=missing_dates+7),'#-6 day': date - timedelta(days=missing_dates+6),'#-5 day': date - timedelta(days=missing_dates+5),'#-4 day': date - timedelta(days=missing_dates+4),'#-3 day': date - timedelta(days=missing_dates+3),'#-2 day': date - timedelta(days=missing_dates+2),'#-1 day': date - timedelta(days=missing_dates+1), '#etal-10 day': find_previous_date_eps(date)}
        try:
            nml = f90nml.read(generic)
            for k,v in dict(nml).items():
                k2 = k.upper()
                for kk,vv in dict(v).items():
                    kk2 = kk.upper()
                    if not isinstance(vv, list):
                        continue
                    newlist = []
                    for vvv in vv:
                        if isinstance(vvv, str):
                            vvv = tool.instanciating_filename_helper(date, vvv, replacedict)
                        newlist.append(vvv)
                    if input_complete_scene_only and kk == input_complete_scene_only[0]:
                        newlist = remove_incomplete_scenes(newlist, lambda x: tool._check_input_file(x, check_h5, silent=True), offset=int(input_complete_scene_only[1]), block_size=int(input_complete_scene_only[2]))
                    nml[k][kk] = newlist
            outfile = outdir + '/' +  os.path.basename(generic + '.' + date.strftime('%Y%m%d%H%M'))
            nml.write(outfile)
            logging.info('Generated ' + outfile)
            missing_dates = 0
        except EmptyList:
            logging.error('Skipped date ' + str(date) + ' because empty file list')
            missing_dates = missing_dates + 1


if __name__ == "__main__":
    main()
