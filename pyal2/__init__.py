#!/usr/bin/env python 
import sys
import os

def get_version():
    """ Get the version number in the `version` file in the same directory. """
    filename = os.path.dirname(os.path.realpath(__file__)) + '/version'
    with open(filename) as version_file:
            version = version_file.read().strip()
    return version

__version__ = get_version()
