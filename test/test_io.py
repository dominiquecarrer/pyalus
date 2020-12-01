#!/usr/bin/env python
from __future__ import print_function

from datetime import datetime
from datetime import timedelta
import argparse
import numpy as np
import os
import re
import shutil
import sys
import time
import h5py

try:
    import coloredlogs, logging
except ImportError:
    import logging

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')
import testal2
print(testal2.is_nan.__doc__)
#import pymdaln.check_versions
import numpy as np

errcode, errmsg = testal2.is_nan(0,'acf dummy string',np.NaN)
if errcode != 0:
    print('test on is_nan failed')
    print(errcode)
    exit(-1)

errcode, errmsg = testal2.is_nan(0,'acf dummy string',np.nan)
if errcode != 0:
    print('test on is_nan failed')
    print(errcode)
    exit(-1)

errcode, errmsg = testal2.is_nan(0,'acf dummy string',0)
if errcode == 0:
    print('test on is_nan failed')
    print(errcode)
    exit(-1)

#####################
import pyal2.config_creator
from pyal2.exit_status import exit_status
import pyal2.al2 as al2
doc = al2.model_fit.__doc__
