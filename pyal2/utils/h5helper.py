#!/usr/bin/env python 
import numpy as np
import logging
import h5py
from datetime import datetime
class H5helper:
    def format_recursively(self, value):
        if isinstance(value,str):
            #value = self.format_one(value, ichannel)
            value = value.encode('ASCII')
        if isinstance(value,list):
            value = [self.format_recursively(elt) for elt in value]
        return value
