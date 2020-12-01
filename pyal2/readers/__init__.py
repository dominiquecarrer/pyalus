import importlib
import logging
import sys

def get_dataloc_reader(reader_string):
    """
    This function is responsible to import the appropriate code to read data location.
    reader_string should be something like 'dataloc_c3s_vgt' and it will return the fucntion located in `pyal2/readers/dataloc_c3s_vgt.py`.
    """
    logging.debug(f' looking for dataloc_reader {reader_string}')
    module = importlib.import_module('pyal2.readers.' + reader_string)
    return module.dataloc_reader_function, module.datetime_params + module.metadata_params, module.datetime_params


def get_data_reader(reader_string):
    """
    This function is responsible to import the appropriate code to read data. The mechanism to import is different from the one above in :func:`get_data_reader()`. Nevertheless the functionnality is the same : use a string as input and return the relevant code/function/class location.

    """
    logging.debug(f' looking for data_reader {reader_string}')

    if reader_string == 'msg_angle':
        import pyal2.readers.msg.angle
        return pyal2.readers.msg.angle.Angle, pyal2.readers.msg.angle.data_params
    if reader_string == 'msg_latitude':
        import pyal2.readers.msg.latitude
        return pyal2.readers.msg.latitude.Latitude, pyal2.readers.msg.latitude.data_params
    if reader_string == 'msg_longitude':
        import pyal2.readers.msg.longitude
        return pyal2.readers.msg.longitude.Longitude, pyal2.readers.msg.longitude.data_params
    if reader_string == 'msg_reflectance_toc':
        import pyal2.readers.msg.reflectance_toc
        return pyal2.readers.msg.reflectance_toc.ReflectanceOneBand, pyal2.readers.msg.reflectance_toc.data_params
    if reader_string == 'msg_reflectance_toc_cov':
        import pyal2.readers.msg.reflectance_toc_cov
        return pyal2.readers.msg.reflectance_toc_cov.ReflectanceOneBandCov, pyal2.readers.msg.reflectance_toc_cov.data_params
    if reader_string == 'msg_lwcs_mask':
        import pyal2.readers.msg.lwcs_mask
        return pyal2.readers.msg.lwcs_mask.LWCS_maskOneBand, pyal2.readers.msg.lwcs_mask.data_params
    if reader_string == 'msg_brdf':
        import pyal2.readers.msg.brdf
        return pyal2.readers.msg.brdf.BrdfReader, pyal2.readers.msg.brdf.data_params
        
    if reader_string == 'mtg_angle':
        import pyal2.readers.mtg.angle
        return pyal2.readers.mtg.angle.Angle, pyal2.readers.mtg.angle.data_params
    if reader_string == 'mtg_latitude':
        import pyal2.readers.mtg.latitude
        return pyal2.readers.mtg.latitude.Latitude, pyal2.readers.mtg.latitude.data_params
    if reader_string == 'mtg_longitude':
        import pyal2.readers.mtg.longitude
        return pyal2.readers.mtg.longitude.Longitude, pyal2.readers.mtg.longitude.data_params
    if reader_string == 'mtg_reflectance_toc':
        import pyal2.readers.mtg.reflectance_toc
        return pyal2.readers.mtg.reflectance_toc.ReflectanceOneBand, pyal2.readers.mtg.reflectance_toc.data_params
    if reader_string == 'mtg_reflectance_toc_cov':
        import pyal2.readers.mtg.reflectance_toc_cov
        return pyal2.readers.mtg.reflectance_toc_cov.ReflectanceOneBandCov, pyal2.readers.mtg.reflectance_toc_cov.data_params
    if reader_string == 'mtg_lwcs_mask':
        import pyal2.readers.mtg.lwcs_mask
        return pyal2.readers.mtg.lwcs_mask.LWCS_maskOneBand, pyal2.readers.mtg.lwcs_mask.data_params
    if reader_string == 'mtg_brdf':
        import pyal2.readers.mtg.brdf
        return pyal2.readers.mtg.brdf.BrdfReader, pyal2.readers.mtg.brdf.data_params


    if reader_string == 'c3s_angle':
        import pyal2.readers.c3s.angle
        return pyal2.readers.c3s.angle.Angle, pyal2.readers.c3s.angle.data_params
    if reader_string == 'c3s_latitude':
        import pyal2.readers.c3s.latitude
        return pyal2.readers.c3s.latitude.Latitude, pyal2.readers.c3s.latitude.data_params
    if reader_string == 'c3s_longitude':
        import pyal2.readers.c3s.longitude
        return pyal2.readers.c3s.longitude.Longitude, pyal2.readers.c3s.longitude.data_params
    if reader_string == 'c3s_reflectance_toc':
        import pyal2.readers.c3s.reflectance_toc
        return pyal2.readers.c3s.reflectance_toc.ReflectanceOneBand, pyal2.readers.c3s.reflectance_toc.data_params
    if reader_string == 'c3s_reflectance_toc_cov':
        import pyal2.readers.c3s.reflectance_toc_cov
        return pyal2.readers.c3s.reflectance_toc_cov.ReflectanceOneBandCov, pyal2.readers.c3s.reflectance_toc_cov.data_params
    if reader_string == 'c3s_lwcs_mask':
        import pyal2.readers.c3s.lwcs_mask
        return pyal2.readers.c3s.lwcs_mask.LWCS_mask, pyal2.readers.c3s.lwcs_mask.data_params
    if reader_string == 'c3s_brdf':
        import pyal2.readers.c3s.brdf
        return pyal2.readers.c3s.brdf.BrdfReader, pyal2.readers.c3s.brdf.data_params
    if reader_string == 'c3s_brdf_clim':
        import pyal2.readers.c3s.brdf_clim
        return pyal2.readers.c3s.brdf_clim.BrdfClimReader, pyal2.readers.c3s.brdf_clim.data_params

    if reader_string == 'empty_brdf':
        import pyal2.readers.empty_brdf
        return pyal2.readers.empty_brdf.Brdf, pyal2.readers.empty_brdf.data_params
    if reader_string == 'empty_angle':
        import pyal2.readers.empty_angle
        return pyal2.readers.empty_angle.Angle, pyal2.readers.empty_angle.data_params
    if reader_string == 'empty_latitude':
        import pyal2.readers.empty_latitude
        return pyal2.readers.empty_latitude.Latitude, pyal2.readers.empty_latitude.data_params
    if reader_string == 'empty_longitude':
        import pyal2.readers.empty_longitude
        return pyal2.readers.empty_longitude.Longitude, pyal2.readers.empty_longitude.data_params
    if reader_string == 'empty_reflectance_toc':
        import pyal2.readers.empty_reflectance_toc
        return pyal2.readers.empty_reflectance_toc.ReflectanceOneBand, pyal2.readers.empty_reflectance_toc.data_params
    if reader_string == 'empty_reflectance_toc_cov':
        import pyal2.readers.empty_reflectance_toc_cov
        return pyal2.readers.empty_reflectance_toc_cov.ReflectanceOneBandCov, pyal2.readers.empty_reflectance_toc_cov.data_params
    if reader_string == 'empty_lwcs_mask':
        import pyal2.readers.empty_lwcs_mask
        return pyal2.readers.empty_lwcs_mask.LWCS_mask, pyal2.readers.empty_lwcs_mask.data_params

    raise Exception(f'Error : cannot find reader {reader_string}. It needs to be defined in the file pyal2/readers/__init__.py')
