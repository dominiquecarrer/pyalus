import yaml
import logging
import numpy as np
import copy
#from numpy import ndarray
from pyal2.utils.io import ensure_dir

def to_yaml_function(obj, filename=None):
    """ Function to write a object into a yaml file. This allow better debugging and logging. """
    obj = copy.deepcopy(obj)
    obj = serialize_for_json(obj)
    if filename:
        with open(filename,'w') as f:
            yaml.dump(obj, f, indent=2)
    return yaml.dump(obj, indent=2)

def from_yaml_function(filename, transform_lists_to_nparray=None):
    """ Function to read a object from a yaml file. """
    if transform_lists_to_nparray is None: transform_lists_to_nparray = []
    with open(filename,'r') as f:
        dic = yaml.unsafe_load(f)
    dic = serialize_from_json(dic, transform_lists_to_nparray)
    return dic

def save_yaml(dic, filename):
    ensure_dir(filename)
    with open(filename,'w') as f:
        yaml.dump(dic, f, indent=2)

# NOT-USED
# The commented code below could be used to allow objects to be read and written in a file. see https://pyyaml.org/wiki/PyYAMLDocumentation for details
#
# def numpyarray_representer(dumper, data):
#     return dumper.represent_sequence('!numpyarrayaslist', data.tolist())
# yaml.add_representer(np.ndarray, numpyarray_representer)
#
# def _numpyarray_constructor(loader, node):
#     value = loader.construct_sequence(node)
#     return value
#     return np.ndarray(value)
# yaml.add_constructor('!numpyarrayaslist', _numpyarray_constructor)
# end of NOT-USED


# NOT-USED :  This is another way to write a nested dictionary in a file when there are special object that cannot be written easily (datetime, numpy arrays, other
#
def serialize_for_json(value):
    if isinstance(value, dict):
       for k in list(value.keys()):
           v = value[k]
           del value[k]
           newk = serialize_for_json(k)
           value[newk] = serialize_for_json(v)
    if isinstance(value, list):
       value = [serialize_for_json(v) for v in value]
       return value
    #if isinstance(value, datetime):
    #    value = value.strftime('$DATETIME:%Y/%m/%d/%H:%M:%S')
    #    return value
    #if isinstance(value, timedelta):
    #    value = '$TIMEDELTA:' + str(value.total_seconds()) + 'sec'
    #    return value
    #if isinstance(value, slice):
    #    value = '$SLICE:' + str(value.start) + ':' + str(value.stop) + ':' + str(value.step or 1)
    #    return value
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value
#
def serialize_from_json(value, transform_lists_to_nparray):
    if isinstance(value, dict):
       for k in list(value.keys()):
           v = value[k]
           del value[k]
           newk = serialize_from_json(k, transform_lists_to_nparray)
           if newk in transform_lists_to_nparray:
               v = np.array(v)
           value[newk] = serialize_from_json(v, transform_lists_to_nparray)
    if isinstance(value, list):
       value = [serialize_from_json(v, transform_lists_to_nparray) for v in value]
       return value
    #if isinstance(value, datetime):
    #    value = value.strftime('$DATETIME:%Y/%m/%d/%H:%M:%S')
    #    return value
    #if isinstance(value, timedelta):
    #    value = '$TIMEDELTA:' + str(value.total_seconds()) + 'sec'
    #    return value
    #if isinstance(value, slice):
    #    value = '$SLICE:' + str(value.start) + ':' + str(value.stop) + ':' + str(value.step or 1)
    #    return value
    return value
#
# -- end of NOT-USED

