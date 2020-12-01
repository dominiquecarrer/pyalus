#!/usr/bin/env python


from datetime import datetime
from datetime import timedelta
import argparse
import os
import sys
import time
import numpy as np

try:
    import coloredlogs, logging
except ImportError:
    import logging

# In case the package has not been properly installed (with pip install) we make sure that the folder "pyal2" is in the import path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/self_import/.')
import pyal2
from pyal2.exit_status import exit_status
from pyal2.chunking import chunk_2D, chunk_1D
from pyal2.parallel import ExceptionInSubprocessWrapper, chunk_init
import pyal2
import pyal2.lib.toc_r

import json

from pyal2.readers.c3s.brdf import BrdfReader
from pyal2.c3s.tocr_io import TocrIO

def parse_args():
        parser = argparse.ArgumentParser(description='Read a BRDF model and produce a TOC-R product', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        #parser.add_argument('acf', help='Algorithm config file')
        #parser.add_argument('pcf', help='Product config file')
        parser.add_argument('-i', '--infile', help='input BRDF file') #, default='output/brdf.20020505-000000.out.nc')
        parser.add_argument('-o', '--outfile', help="output TOC R file")
        parser.add_argument('-l', '--loglevel', help='log level. CRITICAL ERROR WARNING INFO or DEBUG', default='ERROR')
        parser.add_argument('-d','--debuglevel', type=int, help='debug level. higher means more debug information (also mean more memory and slower execution)', default=0)
        parser.add_argument('--nice', type=int, help='Lower the priority of the process (nice +value)', default=0)
        parser.add_argument('--version', action='store_true', help='Show version information and exits')
        args = parser.parse_args()

        # Processing args and config
        os.nice(args.nice)
        coloredlogs.install(level=args.loglevel.upper())
        return args

def main():
    args = parse_args()

    infilename = args.infile
    reader = BrdfReader()
    logging.info(f'Loading brdf from {infilename}')
    reader.load_brdf(infilename, model_len=None, n_channels_ref=None, xslice=None, yslice=None)

    xsize = reader.brdf.values.shape[0]
    ysize = reader.brdf.values.shape[1]
    date = reader.previous_date
    tocr = np.full((xsize, ysize, reader.n_channels_ref), np.nan, order='F', dtype='<f4')
    solzenith = np.full((xsize, ysize), np.nan, order='F', dtype='<f4')
    tocr_cov = np.full((xsize, ysize, reader.n_channels_ref), np.nan, order='F', dtype='<f4')

    errcode, errmsg = pyal2.lib.toc_r.toc_r(debuglevel=args.debuglevel, model=reader.model_id,
            day_of_year=date.timetuple().tm_yday,
            latitude = np.asfortranarray(reader.latitude.values, '<f4'),
            k_array= np.asfortranarray(reader.brdf.values, '<f4'),
            ck_array= np.asfortranarray(reader.covariance.values, '<f4'),
            toc_min=-0.1, toc_max=2.0,
            sig_min=0.0, sig_max=10.0,
            solzenith_out = solzenith,
            tocr=tocr, tocr_cov=tocr_cov)

    writer = TocrIO(outfilename=args.outfile)
    writer.xoutputsize = xsize
    writer.youtputsize = ysize
    writer.n_channels_ref = reader.n_channels_ref
    writer.model_id = reader.model_id
    writer.write_tocr(tocr,     slice(0, xsize), slice(0, ysize), date, 'TOC-R', 'TOC-R')
    writer.write_tocr(tocr_cov, slice(0, xsize), slice(0, ysize), date, 'TOC-R-ERR', 'TOC-R-ERR')

    # hack introduced by VITO
    missing=np.isnan(tocr)
    reader.quality.values[missing] = 128
    # end-of hack introduced by VITO

    writer.write_tocr(reader.quality.values, slice(0, xsize), slice(0, ysize), date, 'Z-QFLAG', 'Z-QFLAG')
    writer.write_tocr(reader.n_valid_obs.values, slice(0, xsize), slice(0, ysize), date, 'Z-NMOD', 'n_valid_obs')
    writer.write_tocr(solzenith, slice(0, xsize), slice(0, ysize), date, 'SOLZENITH', 'solzenith')
    writer.write_tocr(reader.latitude.values, slice(0, xsize), slice(0, ysize), date, 'latitude', 'latitude')
    writer.write_tocr(reader.longitude.values, slice(0, xsize), slice(0, ysize), date, 'longitude', 'longitude')
    print('Processed ' + str(date))

    exit_status("PROCESS_OK")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        exit_status("UNABLE_TO_PROCESS")
