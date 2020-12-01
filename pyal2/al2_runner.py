#!/usr/bin/env python
#####################################################################
# Program running each chunk
# */*/2018 First version
#

import numpy as np
import os
import sys
from datetime import datetime

try:
    import coloredlogs, logging
except ImportError:
    import logging

import pyal2
import pyal2.lib.al2
#import pymdaln.check_versions
from pyal2.exit_status import exit_status
from pyal2.parallel import ExceptionInSubprocessWrapper, FakeLock, chunk_init
from pyal2.data_matrix import DataMatrixFloat, DataMatrixInteger
from pyal2.readers import get_data_reader
# note that "readers" is a folder. The function "get_data_reader" is located in readers/__init__.py
from pyal2.writers import get_data_writer
# note that "writers" is a folder. The function "get_data_writer" is located in writers/__init__.py
from pyal2.readers.empty_brdf import Brdf as EmptyBrdf
from pyal2.utils.dict_utils import get_param_in_tree, set_param_in_tree

reference_date =  datetime(1900,1,1)

def datetime_to_int64(d):
    """ This function transform a datetime object (or list of datetime objects)
        into a 64-bit integer to provide the number of seconds since a reference date.
        - using seconds allows to make sure that we do not have too many rounding issue
                      (even if the input dates can have milliseconds
        - using 64 bits allows to process dates from 1900 to 2100 and more"""
    if isinstance(d, list):
        return np.array([datetime_to_int64(elt) for elt in d])
    if d < reference_date:
        logging.warn(f'date {d} is before the minimum supported date (which is {reference_date}. \
                      You may encounter some temporal paradox issues.')
    delta = d - reference_date
    delta_in_seconds = delta.total_seconds()
    delta_in_seconds = np.int64(delta_in_seconds)
    # print(f'date conversion from datetime_to_int64({d}) -> {delta_in_seconds}')
    return delta_in_seconds


class Al2Runner:
    """ Generic runner to call fortan functions. The data should be loaded in the `self` object.
    Compared to calling directly the fortran code, using this design pattern (using inheritance)
    ensures that the data is loaded and allow better debugging when a variable is missing,
    but this may be changed latter on. """
    def __init__(self, dstore=None, write_lock=None, hook_end_of_spectral_integration=None):
        if not dstore is None:
            self.dstore = dstore
        if write_lock is None:
            write_lock = FakeLock()
        self.write_lock = write_lock
        self.hook_end_of_spectral_integration = hook_end_of_spectral_integration

    def process(self, instr, xslice=None, yslice=None, dates=None):
        """ Load data. Run algorithm. Save output """
        print(instr)
        try:
            if xslice is None: xslice = self.dstore['xfullslice']
            if yslice is None: yslice = self.dstore['yfullslice']
            if dates is None:  dates = self.dstore[instr]['output_dates']

            # dbox is a object DataBox, responsible for finding the data for one step in the Kalman filter
            dbox = None

            for date in dates:
                dbox = self.process_one_date(instr, xslice, yslice, dbox, date)

        except Exception as e:
            logging.critical(f'Problem with slices {(xslice, yslice)}')
            return ExceptionInSubprocessWrapper(e, f'Problem with slices {(xslice, yslice)}')

    def process_one_date(self, instr, xslice, yslice, previous_dbox, date):
        logging.warn('                                                                         ')
        logging.warn('--- Running date : ' + str(date) + ' ---' + ' for instrument' + str(instr))
        # get the previous date from the previous dbox object if there is one
        if previous_dbox is None:
            previous_date = None
            logging.debug(f'previous_date is set to None')
        else:
            previous_date = previous_dbox['date']
            logging.debug(f'setting previous_date = {previous_date} from previous dbox')
        # and create a new dbox object
        
        dbox = self.dstore.create_data_box(date, instr, xslice, yslice, previous_date=previous_date)

        # save it for debugging
        self.dbox = dbox

        # Read or create previous brdf, previous qflag, previous date, etc
        self.get_checkpoint_data(dbox, date, instr)

        # ask dbox to provide the input data (this comment is useless : remove it)
        self.get_input_data(dbox, instr)

        self.currentdatetime = date
        self.day_of_year = date.timetuple().tm_yday

        # initialize the output and intermediate arrays (using dbox) (this comment is useless : remove it)
        self.initialize_output_and_intermediate_arrays(dbox)

        self.run_model_fit(dbox, instr)
        self.run_angular_integration(dbox, instr)
        self.run_spectral_integration(dbox, instr)
        self.write(dbox, date, xslice, yslice, instr)
        return dbox

    def get_checkpoint_data(self, dbox, date, sensor):
        """ To read previous BRDF parameters estimation for Kalman filter """
        
        inputcheckpoint = dbox['inputcheckpoint']
        logging.debug(f'Getting checkpoint from {inputcheckpoint}')
        xslice = dbox['xslice']
        yslice = dbox['yslice']
        model_len = dbox['model_len']
        n_channels_ref  = dbox['n_channels_ref']

        if inputcheckpoint and not dbox[f'{sensor}']['startseries']:
 	    # If inputcheckpoint is available or if second calculation after spin-off
            self.current_startseries = False
            data_reader_class, data_params = get_data_reader(inputcheckpoint['reader'])
            data_params_dict = {p:get_param_in_tree(inputcheckpoint,[], p) for p in data_params}

            reader = data_reader_class()
            reader.load_brdf(**data_params_dict, n_channels_ref=n_channels_ref,
                             model_len=model_len, xslice=xslice, yslice=yslice)
        else:
            # no check point, create empty initial state
            logging.debug('Setting up empty initial brdf')
            print('Setting up empty initial brdf, often due to error')
            self.current_startseries = True
            reader = EmptyBrdf().load_brdf(xslice, yslice, n_channels_ref, model_len)
        self.quality_in = reader.quality
        self.age_obs_in = reader.age_obs
        self.brdf_in = reader.brdf
        self.covariance_in = reader.covariance

        self.days_last_in = (date - reader.previous_date).days

    def get_input_data(self, dbox, sensor):
        """ This function uses the object dbox to load all the input data,
        except the previous brdf."""

        self.zenith_sat = dbox.get_data('zenith_sat', sensor)
        self.zenith_sol = dbox.get_data('zenith_sol', sensor)
        self.azimuth_sat = dbox.get_data('azimuth_sat', sensor)
        self.azimuth_sol = dbox.get_data('azimuth_sol', sensor)

        self.latitude = dbox.get_data('latitude', sensor)
        self.longitude = dbox.get_data('longitude', sensor)

        self.reflectance = dbox.get_data('toc_reflectance', sensor)
        self.reflectance_cov = dbox.get_data('toc_reflectance_cov', sensor)
        self.lwcs_mask = dbox.get_data('lwcs_mask', sensor)
 
        if dbox['acf']['nam_inv']['brdf_clim_activated']:
            logging.info('Setting up initial climatological brdf')
            self.brdf_clim = dbox.get_data('brdf_clim', sensor)
            self.covariance_clim = dbox.get_data('brdf_clim_cov', sensor)
        else:
            self.brdf_clim =  DataMatrixInteger().full(shape=self.brdf_in.values.shape, value=-1, dtype='int8')
            self.covariance_clim =  DataMatrixInteger().full(shape=self.covariance_in.values.shape, value=-1, dtype='int8')
            logging.info('No climatological brdf is now used')
            
        # Put here any additional tweaks to the input data that need to be run when all data has been loaded :
        # tweak the reflectance using the input quality flag
        if dbox['globalconfig'].get('remove_bad_quality_reflectance_but_ignore_band4_qflag', False): # sould be enabled for C3S-VGT v 0.x.6
            logging.warn('config option enabled : remove_bad_quality_reflectance_but_ignore_band4_qflag')
            self.lwcs_mask.remove_bad_quality_reflectance_but_ignore_band4_qflag(self.reflectance, self.reflectance_cov)
        elif dbox['globalconfig'].get('remove_bad_quality_reflectance', False): # sould be enabled for C3S-VGT v 0.x.5
            logging.warn('config option enabled : remove_bad_quality_reflectance')
            self.lwcs_mask.remove_bad_quality_reflectance(self.reflectance, self.reflectance_cov)
        else:
            pass

        # additional tweak. TODO latter : remove this line if it is useless ?
        self.lwcs_mask.values = np.asfortranarray(self.lwcs_mask.values, 'i1')

        self.scenesdatetimes = dbox['input'][sensor]['latitude']['_scenes_dates']
        self.sat_specific = dbox['input'][sensor]['sat_specific']

    def initialize_output_and_intermediate_arrays(self, dbox):
        """
        This function uses dbox to get the size of the matrix to instanciate. Then it
        creates all the required arrays of type DataMatrixInteger or DataMatrixFloat.
        We may want to optimize this part :

        - to save memory : only initialize the matrices when they are needed)
        - or to optimise speed : reuse the same matrices in order to avoid deleting
        creating new matrices at every time step/chunk.

        The advantages of implementing such optimisation may be very small.
        """

        self.sizex = sizex  = dbox['xslice'].stop - dbox['xslice'].start
        self.sizey = sizey  = dbox['yslice'].stop - dbox['yslice'].start
        self.n_channels_ref = n_channels_ref  = dbox['n_channels_ref']
        self.model_len = model_len = dbox['model_len']
        nalbedos = dbox['nalbedos']
        n_outalbedos = dbox['n_outalbedos']

        self.brdf        = DataMatrixFloat().full(shape=(sizex, sizey, n_channels_ref, model_len), dtype='f4',value=dbox['acf']['nam_inv']['initial_value_brdf_k'])
        self.brdf1       = DataMatrixFloat().full(shape=(sizex, sizey, n_channels_ref, model_len), dtype='f4',value=dbox['acf']['nam_inv']['initial_value_brdf_k'])
        self.age         = DataMatrixInteger().full(shape=(sizex, sizey, n_channels_ref), dtype='int8', value=dbox['acf']['nam_inv']['initial_value_brdf_age'])
        self.quality     = DataMatrixInteger().full(shape=(sizex, sizey, n_channels_ref), dtype='int8',value=dbox['acf']['nam_inv']['initial_value_brdf_quality'])
        self.quality1    = DataMatrixInteger().full(shape=(sizex, sizey, n_channels_ref), dtype='int8',value=dbox['acf']['nam_inv']['initial_value_brdf_quality'])
        self.covariance  = DataMatrixFloat().full(shape=(sizex, sizey, n_channels_ref, model_len, model_len), dtype='f4', value=dbox['acf']['nam_inv']['initial_value_brdf_ck'])
        self.covariance1 = DataMatrixFloat().full(shape=(sizex, sizey, n_channels_ref, model_len, model_len), dtype='f4', value=dbox['acf']['nam_inv']['initial_value_brdf_ck'])

        self.snow_mask_out = DataMatrixInteger().full(shape=(sizex, sizey), dtype='i1')
        self.n_valid_obs_out = DataMatrixInteger().full(shape=(sizex, sizey, n_channels_ref), value=-1, dtype='int8')
        self.albedos         = DataMatrixFloat().full(shape=(sizex, sizey, n_channels_ref, nalbedos), value=np.nan, dtype='f4')
        self.albedos_cov     = DataMatrixFloat().full(shape=(sizex, sizey, n_channels_ref, nalbedos), value=np.nan, dtype='f4')
        self.albedos_age     = DataMatrixInteger().full(shape=(sizex, sizey, n_channels_ref), value=-1, dtype='int8')
        self.albedos_age     = DataMatrixInteger().full(shape=(sizex, sizey, n_channels_ref), value=-1, dtype='int8')
        self.albedos_quality = DataMatrixInteger().full(shape=(sizex, sizey, n_channels_ref), value=0,  dtype='int8')

        self.outalbedos         = DataMatrixFloat().full(shape=(sizex, sizey, nalbedos, n_outalbedos), value=np.nan, dtype='f4')
        self.outalbedos_cov     = DataMatrixFloat().full(shape=(sizex, sizey, nalbedos, n_outalbedos), value=np.nan, dtype='f4')
        self.outalbedos_age     = DataMatrixFloat().full(shape=(sizex, sizey), value=-1, dtype='f4')
        self.outalbedos_quality = DataMatrixFloat().full(shape=(sizex, sizey), value=1,  dtype='f4')

    def check_consistency_of_input_data(self, dbox, sensor):
        # number of input bands
        for k in ['lwcs_mask', 'zenith_sat', 'azimuth_sat', 'zenith_sol', 'azimuth_sol', 'reflectance', 'reflectance_cov']:
            exec(f"print('{k} : ' + str(self.{k}.values.shape))")

        #print(f"lwcs_mask_missing:{ self.lwcs_mask.missing }")
        print(f"spectral_normalisation :{np.array(dbox['acf']['spectral'][sensor]['spectral_normalisation']).shape}")
        print(f"spectral_normalisation_err :{ dbox['acf']['spectral'][sensor]['spectral_normalisation_err'].shape}")
        print(f"latitude:{ self.latitude.values.astype('<f4').shape }")
        print(f"longitude:{ self.longitude.values.astype('<f4').shape}")
        #print(f"model:{                 dbox['model_id']}")
        #print(f"recursion:{             dbox['acf']['nam_inv']['recursion']             }")
        #print(f"startseries:{           self.current_startseries}")
        #print(f"composition:{           dbox['acf']['nam_inv']['composition']           }")
        #print(f"bad_cma_elim:{          dbox['acf']['nam_inv']['bad_cma_elim']          }")
        ##print(f"bad_cma_factor:{        dbox['acf']['nam_inv']['bad_cma_factor']        }")
        #print(f"shadow_elim:{           dbox['acf']['nam_inv']['shadow_elim']           }")
        #print(f"shadow_factor:{         dbox['acf']['nam_inv']['shadow_factor']         }")
        #print(f"n_slot_elim:{           dbox['acf']['nam_inv']['n_slot_elim']           }")
        #print(f"n_obs_limit:{           dbox['acf']['nam_inv']['n_obs_limit']           }")
        #print(f"timescale:{             dbox['acf']['nam_inv']['timescale']             }")
        #print(f"snow_flag_one:{         dbox['acf']['nam_inv']['snow_flag_one']         }")
        #print(f"theta_sat_limit:{       dbox['acf']['spectral'][sensor]['theta_sat_limit']       }")
        #print(f"theta_sol_limit:{       dbox['acf']['spectral'][sensor]['theta_sol_limit']       }")
        #print(f"theta_sat_wlimit:{      dbox['acf']['spectral'][sensor]['theta_sat_wlimit']      }")
        #print(f"theta_sol_wlimit:{      dbox['acf']['spectral'][sensor]['theta_sol_wlimit']      }")
        print(f"sig_nadir_a  :{         np.array(dbox['acf']['nam_inv']['sig_nadir_a'], order='F', dtype='f4')}")
        print(f"sig_nadir_b  :{         np.array(dbox['acf']['nam_inv']['sig_nadir_b'], order='F', dtype='f4')}")
        print(f"typical_cov_rescale_values :{ np.array(dbox['acf']['spectral'][sensor]['typical_cov_rescale'], order='F', dtype='f4')}")
        print(f"sigrefl_min  :{         dbox['acf']['nam_inv']['sigrefl_min']}")
        print(f"sigrefl_max  :{         dbox['acf']['nam_inv']['sigrefl_max']}")
        print(f"k_reg  :{               np.array(dbox['acf']['nam_inv']['k_reg'], order='F', dtype='f4')}")
        print(f"sig_k_reg  :{           np.array(dbox['acf']['nam_inv']['sig_k_reg'], order='F', dtype='f4')}")
        #print(f"par_max  :{ dbox['acf']['nam_scale']['par_max']}")
        #print(f"par_min  :{ dbox['acf']['nam_scale']['par_min']}")
        #print(f"cxx_max  :{ dbox['acf']['nam_scale']['cxx_max']}")
        #print(f"cxx_min  :{ dbox['acf']['nam_scale']['cxx_min']}")
        #print(f"cxy_max  :{ dbox['acf']['nam_scale']['cxy_max']}")
        #print(f"cxy_min  :{ dbox['acf']['nam_scale']['cxy_min']}")
        #print(f"day_of_year:{ self.day_of_year }")
        #print(f"days_last_in:{ self.days_last_in }")
        print(f"zenith_sat:{ self.zenith_sat.values.shape}")
        print(f"azimuth_sat:{ self.azimuth_sat.values.shape}")
        print(f"zenith_sol:{ self.zenith_sol.values.shape}")
        print(f"azimuth_sol:{ self.azimuth_sol.values.shape}")
        print(f"reflectance:{ self.reflectance.values.shape}")
        print(f"reflectance_cov:{ self.reflectance_cov.values.shape}")
        #print(f"scenesdatetimes:{ scenesdatetimes}")
        #print(f"currentdatetime:{ currentdatetime}")
        print(f"quality_in:{ self.quality_in.values.shape     }")
        print(f"age_obs_in:{ self.age_obs_in.values.shape     }")
        print(f"brdf_in:{ self.brdf_in.values.shape           }")
        print(f"covariance_in:{ self.covariance_in.values.shape}")
        print(f"brdf_clim :{ self.brdf_clim.values.shape      }")
        print(f"covariance_clim :{ self.covariance_clim.values.shape }")
        #print(f"brdf_clim_activated :{ dbox['acf']['nam_inv']['brdf_clim_activated']}")
        #print(f"sat_specific :{ self.sat_specific}")
        #print(f"enable_normalisation:{ dbox['acf']['spectral'][sensor]['enable_normalisation']}")
        #print(f"refl_outliers_elim_param1:{ dbox['acf']['nam_inv'].get('refl_outliers_elim_param1',1.)}")
        #print(f"refl_outliers_elim_param2:{ dbox['acf']['nam_inv'].get('refl_outliers_elim_param2',3.)}")
        #print(f"refl_outliers_elim_band_ref:{dbox['acf']['nam_inv'].get('refl_outliers_elim_band_ref',-1), # for AVHRR this should be 2, for VGT it should be }")
        #print(f"refl_outliers_elim_band_in:{dbox['acf']['nam_inv'].get('refl_outliers_elim_band_in',-1)}")

        #ndvi_nir=index_nir, ndvi_red=index_red,
        #ndvi2_nir=index2_nir, ndvi2_red=index2_red,
        # this one it should be always 1
        # output
        print(f"REF brdf:{ self.brdf.values.shape }")
        print(f"REF brdf1:{ self.brdf1.values.shape }")
        print(f"REF quality :{ self.quality.values.shape}")
        print(f"REF quality1 :{ self.quality1.values.shape}")
        print(f"REF age_out:{ self.age.values.shape}")
        print(f"REF n_valid_obs_out:{ self.n_valid_obs_out.values.shape}")
        print(f"REF covariance:{ self.covariance.values.shape }")
        print(f"REF covariance1:{ self.covariance1.values.shape }")
        print(f"REF snow_mask_out:{ self.snow_mask_out.values.shape}")
        #debuginfo = dbox.get_debug_info_array())

    def run_model_fit(self, dbox, sensor):
        """ Wrapper aroud the fortran function model_fit """

        logging.warn('Model fitting !')
        scenesdatetimes= datetime_to_int64(self.scenesdatetimes)
        if len(scenesdatetimes) == 0:
            scenesdatetimes = np.array([0])
        currentdatetime= datetime_to_int64(self.currentdatetime)

        # TODO : put these hard coded value in the acf param file
        if (dbox['acf']['spectral'][sensor]['nbands'] == 2) | (dbox['acf']['spectral'][sensor]['nbands'] == 3):
            index_red = 1
            index_nir = 2
        elif dbox['acf']['spectral'][sensor]['nbands'] == 4:
            index_red=2
            index_nir=3
        index2_red = 2
        index2_nir = 3
        
        # Controling the input angles depending on the type of sensor
        indexing_method = dbox['input'][sensor]['azimuth_sat']['band_indexing_method']
        
        if indexing_method == 'sparse':
            band_indexing_list = dbox['input'][sensor]['azimuth_sat']['band_indexing_list']
            angle_index = np.array([int(band_indexing_list[i].split('d')[1]) for i in range(len(band_indexing_list))])
            # band_indexing_list is written this way : ['band1','band2'] The band number is after the 'd'
            # Values from 0 to n_channels_ref
        else:
            angle_index = np.ones(self.n_channels_ref)

        #self.check_consistency_of_input_data(dbox, sensor)
        pyal2.lib.al2.model_fit(
               debuglevel = dbox['globalconfig']['debuglevel'],
               # input
               xstart=1, ystart=1,xend=self.sizex, yend=self.sizey,
               lwcs_mask= self.lwcs_mask.values ,
               lwcs_mask_missing= self.lwcs_mask.missing ,
               spectral_normalisation = np.array(dbox['acf']['spectral'][sensor]['spectral_normalisation']),
               spectral_normalisation_err = dbox['acf']['spectral'][sensor]['spectral_normalisation_err'],
               latitude= self.latitude.values.astype('<f4') ,
               longitude= self.longitude.values.astype('<f4'),
               model=                 dbox['model_id'],
               recursion=             dbox['acf']['nam_inv']['recursion']             ,
               startseries=           self.current_startseries,
               composition=           dbox['acf']['nam_inv']['composition']           ,
               bad_cma_elim=          dbox['acf']['nam_inv']['bad_cma_elim']          ,
               bad_cma_factor=        dbox['acf']['nam_inv']['bad_cma_factor']        ,
               shadow_elim=           dbox['acf']['nam_inv']['shadow_elim']           ,
               shadow_factor=         dbox['acf']['nam_inv']['shadow_factor']         ,
               n_slot_elim=           dbox['acf']['nam_inv']['n_slot_elim']           ,
               n_obs_limit=           dbox['acf']['nam_inv']['n_obs_limit']           ,
               timescale=             dbox['acf']['nam_inv']['timescale']             ,
               snow_flag_one=         dbox['acf']['nam_inv']['snow_flag_one']         ,
               theta_sat_limit=       dbox['acf']['spectral'][sensor]['theta_sat_limit']       ,
               theta_sol_limit=       dbox['acf']['spectral'][sensor]['theta_sol_limit']       ,
               theta_sat_wlimit=      dbox['acf']['spectral'][sensor]['theta_sat_wlimit']      ,
               theta_sol_wlimit=      dbox['acf']['spectral'][sensor]['theta_sol_wlimit']      ,
               sig_nadir_a  =         np.array(dbox['acf']['nam_inv']['sig_nadir_a'], order='F', dtype='f4'),
               sig_nadir_b  =         np.array(dbox['acf']['nam_inv']['sig_nadir_b'], order='F', dtype='f4'),
               typical_cov_rescale_values = np.array(dbox['acf']['spectral'][sensor]['typical_cov_rescale'], order='F', dtype='f4'),
               angle_index =          np.array(angle_index, order='F'),
               sigrefl_min  =         dbox['acf']['nam_inv']['sigrefl_min'],
               sigrefl_max  =         dbox['acf']['nam_inv']['sigrefl_max'],
               k_reg  =               np.array(dbox['acf']['nam_inv']['k_reg'], order='F', dtype='f4'),
               sig_k_reg  =           np.array(dbox['acf']['nam_inv']['sig_k_reg'], order='F', dtype='f4'),
               par_max  = dbox['acf']['nam_scale']['par_max'],
               par_min  = dbox['acf']['nam_scale']['par_min'],
               cxx_max  = dbox['acf']['nam_scale']['cxx_max'],
               cxx_min  = dbox['acf']['nam_scale']['cxx_min'],
               cxy_max  = dbox['acf']['nam_scale']['cxy_max'],
               cxy_min  = dbox['acf']['nam_scale']['cxy_min'],
               day_of_year= self.day_of_year ,
               days_last_in= self.days_last_in ,
               zenith_sat= self.zenith_sat.values,
               azimuth_sat= self.azimuth_sat.values,
               zenith_sol= self.zenith_sol.values,
               azimuth_sol= self.azimuth_sol.values,
               reflectance= self.reflectance.values,
               reflectance_cov= self.reflectance_cov.values,
               scenesdatetimes= scenesdatetimes,
               currentdatetime= currentdatetime,
               quality_in= self.quality_in.values     ,
               age_obs_in= self.age_obs_in.values     ,
               brdf_in= self.brdf_in.values           ,
               covariance_in= self.covariance_in.values,
               brdf_clim = self.brdf_clim.values      ,
               covariance_clim = self.covariance_clim.values ,
               brdf_clim_activated = dbox['acf']['nam_inv']['brdf_clim_activated'],
               sat_specific = self.sat_specific,
               enable_normalisation=
               dbox['acf']['spectral'][sensor]['enable_normalisation'],
               refl_outliers_elim_param1= dbox['acf']['nam_inv'].get('refl_outliers_elim_param1',1.),
               refl_outliers_elim_param2= dbox['acf']['nam_inv'].get('refl_outliers_elim_param2',3.),
               refl_outliers_elim_band_ref=dbox['acf']['nam_inv'].get('refl_outliers_elim_band_ref',-1), # for AVHRR this should be 2, for VGT it should be 1
               refl_outliers_elim_band_in=dbox['acf']['nam_inv'].get('refl_outliers_elim_band_in',-1),

               ndvi_nir=index_nir, ndvi_red=index_red,
               ndvi2_nir=index2_nir, ndvi2_red=index2_red,
               # this one it should be always 1
               # output
               brdf= self.brdf.values ,
               brdf1= self.brdf1.values ,
               quality = self.quality.values,
               quality1 = self.quality1.values,
               age_out= self.age.values,
               n_valid_obs_out= self.n_valid_obs_out.values,
               covariance= self.covariance.values ,
               covariance1= self.covariance1.values ,
               snow_mask_out= self.snow_mask_out.values,
               debuginfo = dbox.get_debug_info_array())

    def run_angular_integration(self, dbox, sensor):
        """ Wrapper aroud the fortran function albedo_angular_integration """
        logging.warn('Angular integration !')

        pyal2.lib.al2.albedo_angular_integration(
               # input
               debuglevel = dbox['globalconfig']['debuglevel'],
               xstart=1, ystart=1,xend=self.sizex, yend=self.sizey,
               square_my_input_variance=True,
               k_array  = self.brdf.values,
               ck_array = self.covariance.values,
               latitude = self.latitude.values.astype('<f4') ,
               longitude= self.longitude.values.astype('<f4'),
               theta_ref_dh_limit   = dbox['acf']['spectral'][sensor]['theta_ref_dh_limit'],
               theta_sol_midi_limit = dbox['acf']['spectral'][sensor]['theta_sol_midi_limit'],
               day_of_year = self.day_of_year,
               snow_mask_out= self.snow_mask_out.values,
               model    = dbox['acf']['nam_inv']['model'],
               alb_max  = dbox['acf']['nam_scale']['alb_max'],
               alb_min  = dbox['acf']['nam_scale']['alb_min'],
               sig_max  = dbox['acf']['nam_scale']['sig_max'],
               sig_min  = dbox['acf']['nam_scale']['sig_min'],
               cxx_max  = dbox['acf']['nam_scale']['cxx_max'],
               cxy_max  = dbox['acf']['nam_scale']['cxy_max'],
               cxy_min  = dbox['acf']['nam_scale']['cxy_min'],
               # output
               albedos = self.albedos.values,
               albedos_cov = self.albedos_cov.values,
               age = self.age.values, albedos_age = self.albedos_age.values,
               quality = self.quality.values, albedos_quality = self.albedos_quality.values,
               debuginfo = dbox.get_debug_info_array())
        # WARNING : This is deleted because the weighting is done inside the model_fit
        for iband in range(0, self.albedos_cov.values.shape[2]):   
            a = dbox['acf']['spectral'][sensor]['spectral_normalisation_err'][0,iband,2]
            b = dbox['acf']['spectral'][sensor]['spectral_normalisation_err'][0,iband,3]
            self.albedos_cov.values[:,:,iband,:] = a + b * self.albedos_cov.values[:,:,iband,:]

    def run_spectral_integration(self, dbox, sensor):
        """ Wrapper aroud the fortran function albedo_spectral_integration """
        logging.warn('Spectral integration !')

        pyal2.lib.al2.albedo_spectral_integration(
               debuglevel = dbox['globalconfig']['debuglevel'],
               # input
               xstart=1, ystart=1,xend=self.sizex, yend=self.sizey,
               albedos = self.albedos.values,
               albedos_cov = self.albedos_cov.values ,
               albedos_age = self.albedos_age.values ,
               albedos_quality = self.albedos_quality.values,
               mask_array = self.snow_mask_out.values,
               latitude= self.latitude.values.astype('<f4') ,
               longitude= self.longitude.values.astype('<f4'),
               coeffs = dbox['coeffs'],
               sigma_co  = dbox['acf']['nam_inv']['sigma_co'],
               alb_max  = dbox['acf']['nam_scale']['alb_max'],
               alb_min  = dbox['acf']['nam_scale']['alb_min'],
               sig_max  = dbox['acf']['nam_scale']['sig_max'],
               sig_min  = dbox['acf']['nam_scale']['sig_min'],
               # output
               outalbedos = self.outalbedos.values,
               outalbedos_cov = self.outalbedos_cov.values ,
               outalbedos_age = self.outalbedos_age.values ,
               outalbedos_quality = self.outalbedos_quality.values,
               debuginfo = dbox.get_debug_info_array())

        if self.hook_end_of_spectral_integration:
            self.hook_end_of_spectral_integration(self)


    def write(self, dbox, date, xslice, yslice, sensor):
        """
        This function Write the output files.

        It uses the dbox config manager to find the writer functions to call to write
        the output, then it calls them to write brdf, spectral albedos and broadband albedos :

            - if MSG, it uses writers/msg_writer.py
            - if C3S, it uses writers/c3s_writer.py
            - if MTG, it uses writers/mtg_writer.py
            
        Note : In order to make this function parallel-safe, this function
        make sure not to write several file at the same time by using a write
        lock semaphore, in case multiple processes are used.
            """
        try: # use a write lock to write output file, in case there are several threads/processes
            self.write_lock.acquire()
            logging.info(f'Writing output for {date}, {xslice}, {yslice}')
            data_writer_class, _ = get_data_writer(dbox[sensor]['output']['writer'])
            # create a writer object with all the relevant parameters
            writer = data_writer_class(config=dbox[sensor]['output'],
                                        xoutputsize=dbox['xoutputsize'],
                                        youtputsize=dbox['youtputsize'],
                                        n_channels_ref=dbox['n_channels_ref'],
                                        model_len=dbox['model_len'],
                                        model_id=dbox['model_id'],
                                        output_channel_names=dbox['acf']['output_channel_names'],
                                        outalbedos_names=dbox['outalbedos_names'],
                                        inalbedos_names=dbox['inalbedos_names'],
                                        xslice=xslice, yslice=yslice, date=date)
            writer.write_all_brdf(self)
            writer.write_all_spectral_albedos(self)
            writer.write_all_albedos(self)
            logging.info(f'Finished writing output for {date}, {xslice}, {yslice}')
            self.write_lock.release()
        except Exception as e:
            self.write_lock.acquire(False)
            self.write_lock.release()
            logging.critical('Problem writing ' + str((xslice, yslice)))
            raise(e)


    def to_xr(self):
        """
        Transform the current data in an xarray.Dataset. TODO.
        """
        import xarray as xr
        return xr.Dataset({'reflectance': self.reflectance.to_xr(),
                         'azimuth_sol': self.azimuth_sol.to_xr(),
                         'azimuth_sat': self.azimuth_sat.to_xr(),
                         'zenith_sol': self.zenith_sol.to_xr(),
                         'zenith_sat': self.zenith_sat.to_xr()
                         })
