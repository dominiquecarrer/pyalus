import numpy as np
from pyal2.exit_status import exit_status
import logging

def stack_it(one_band_list, sensorname, check_sizes = False, stack_axis = 2):
    """ Reflectance object is created from several ReflectanceOneBand objects. Stacking data for all bands along the merge_axis dimension. """

    # security check in case there is nothing to  merge
    if len(one_band_list) == 0:
        logging.error(f"No band available for the sensor {sensorname}")
        raise Exception('Input error')
    
    one_band_type_name = type(one_band_list[0]).__name__
    if one_band_type_name == 'Angle':
        out = AngleMultiBand()
    elif one_band_type_name == 'LWCS_maskOneBand':
        out = LWCS_mask()
    elif one_band_type_name == 'ReflectanceOneBand':
        out = Reflectance()
    elif one_band_type_name == 'ReflectanceOneBandCov':
        out = ReflectanceCov()
    else:
        logging.error(f'Cannot stack object type {one_band_type_name}')
        exit_status('UNABLE_TO_PROCESS')

    # This is the actual code perfoming the merge. The reste of this function is only security checks.
    out.values = np.stack([x.values for x in one_band_list], axis = stack_axis)

    # keep the metadata
    out.sensorname = sensorname

    # propagate (and check) the scenes_dates
    out.scenes_dates = one_band_list[0].scenes_dates
    for dataset in one_band_list:
        if dataset.scenes_dates != out.scenes_dates:
            logging.error(f'ERROR : Mismatch in scenes dates : {dataset.scenes_dates} != {out.scenes_dates}')

    # propagate (and check) the missing data value
    out.missing = one_band_list[0].missing
    for dataset in one_band_list:
        if dataset.missing != out.missing:
            logging.error(f'ERROR : Mismatch in scenes dates : {dataset.missing} != {out.missing}')

    # TODO : propagate also the filenames it would be usefull to debug
    #attrs = { 'filenames': out.filenames })

    if check_sizes:
        shape_one_band = one_band_list[0].values.shape
        # shape_one_band is : (xsize, ysize,n_scenes)
        shape = (shape_one_band[0], shape_one_band[1], len(one_band_list), shape_one_band[2])
        if out.values.shape != shape:
            logging.error(str(shape_one_band))
            logging.error(str(shape))
            logging.error(str(out.values.shape))
            raise Exception('Merging error')
    return out

class ReflectanceCov():
    pass
class Reflectance():
    pass
class LWCS_mask():
    pass
class AngleMultiBand():
    pass
