import f90nml
import math
import logging
import yaml
import numpy as np
from pyal2.utils.parsing import robust_date_parse

def f90nml_to_yaml_msg(acffile, pcffile, prefix='log/', extension='.yaml'):
    with open(acffile,'r') as f:
        acf = f90nml.read(acffile)
    with open(pcffile,'r') as f:
        pcf = f90nml.read(pcffile)

    # Transform acf file
    time_span_for_composition = {'days': 1}
    logging.warn('MSG : Forcing time_span_for_composition to ' + str(time_span_for_composition))
    if not 'model_len' in acf['nam_inv']:
        acf['nam_inv']['model_len'] = 3
        logging.warn('MSG : model_len not defined in acf file, using default value model_len = ' + str(acf['nam_inv']['model_len']))

    norm_err = [0.0, 1.0, 0.0, 1.0, 0.0,1.0, 0.0, 1.0, 0.0, 1.0,0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0]

    aout = {
      'nam_inv' : {
        'initial_value_brdf_k'   : np.nan,
        'initial_value_brdf_ck'  : np.nan,
        'initial_value_brdf_age' : -1,
        'initial_value_brdf_quality' : 0,
        'brdf_clim_activated':False,
        'bad_cma_elim' : acf['nam_inv']['bad_cma_elim'],
        'bad_cma_factor' : acf['nam_inv']['bad_cma_factor'],
        'co_bb_bh' : acf['nam_inv']['co_bb_bh'],
        'co_bb_bh_snow' : acf['nam_inv']['co_bb_bh_snow'],
        'co_bb_dh' : acf['nam_inv']['co_bb_dh'],
        'co_bb_dh_snow' : acf['nam_inv']['co_bb_dh_snow'],
        'co_ni_bh' : acf['nam_inv']['co_ni_bh'],
        'co_ni_bh_snow' : acf['nam_inv']['co_ni_bh_snow'],
        'co_ni_dh' : acf['nam_inv']['co_ni_dh'],
        'co_ni_dh_snow' : acf['nam_inv']['co_ni_dh_snow'],
        'co_vi_bh' : acf['nam_inv']['co_vi_bh'],
        'co_vi_bh_snow' : acf['nam_inv']['co_vi_bh_snow'],
        'co_vi_dh' : acf['nam_inv']['co_vi_dh'],
        'co_vi_dh_snow' : acf['nam_inv']['co_vi_dh_snow'],
        'composition' : acf['nam_inv']['composition'],
        'k_reg' : acf['nam_inv']['k_reg'],
        'model' : acf['nam_inv']['model'],
        'model_len' : acf['nam_inv']['model_len'],
        'n_obs_limit' : acf['nam_inv']['n_obs_limit'],
        'n_slot_elim' : acf['nam_inv']['n_slot_elim'],
        'recursion' : acf['nam_inv']['recursion'],
        'shadow_elim' : acf['nam_inv']['shadow_elim'],
        'shadow_factor' : acf['nam_inv']['shadow_factor'],
        'sig_k_reg' : acf['nam_inv']['sig_k_reg'],
        'sig_nadir_a' : acf['nam_inv']['sig_nadir_a'],
        'sig_nadir_b' : acf['nam_inv']['sig_nadir_b'],
        'sigma_co' : acf['nam_inv']['sigma_co'],
        'sigrefl_max' : acf['nam_inv']['sigrefl_max'],
        'sigrefl_min' : acf['nam_inv']['sigrefl_min'],
        'snow_flag_one' : acf['nam_inv']['snow_flag_one'],
        'startseries' : acf['nam_inv']['startseries'],
        'time_span_for_composition' : time_span_for_composition,
        'timescale' : acf['nam_inv']['timescale'],
      },
      'nam_proc': {
        'compression' : acf['NAM_PROC']['compression'],
        'disposition_flag' : acf['NAM_PROC']['disposition_flag'],
        'linesblock' : acf['NAM_PROC']['linesblock'],
        'loglinfrequ' : acf['NAM_PROC']['loglinfrequ'],
        'path_tmp' : acf['NAM_PROC']['path_tmp'],
        'processing_mode' : acf['NAM_PROC']['processing_mode'],
        'unit' : acf['NAM_PROC']['unit']
      },
      'nam_scale': {'alb_max': acf['nam_scale']['alb_max'],
            'alb_min': acf['nam_scale']['alb_min'],
            'cxx_max': acf['nam_scale']['cxx_max'],
            'cxx_min': acf['nam_scale']['cxx_min'],
            'cxy_max': acf['nam_scale']['cxy_max'],
            'cxy_min': acf['nam_scale']['cxy_min'],
            'missingvalue': acf['nam_scale']['missingvalue'],
            'missingvalue_kcov': acf['nam_scale']['missingvalue_kcov'],
            'par_max': acf['nam_scale']['par_max'],
            'par_min': acf['nam_scale']['par_min'],
            'scale_alb': acf['nam_scale']['scale_alb'],
            'scale_cov': acf['nam_scale']['scale_cov'],
            'scale_par': acf['nam_scale']['scale_par'],
            'scale_sig': acf['nam_scale']['scale_sig'],
            'sig_max': acf['nam_scale']['sig_max'],
            'sig_min': acf['nam_scale']['sig_min'],
      },
      'output_channel_names' : ['C1', 'C2', 'C3'],
      'spectral': {
        'MSG': {
          'nbands':  3,
          'theta_ref_dh_limit' : acf['nam_inv']['theta_ref_dh_limit'],
          'theta_sat_limit' : acf['nam_inv']['theta_sat_limit'],
          'theta_sat_wlimit' : acf['nam_inv']['theta_sat_wlimit'],
          'theta_sol_limit' : acf['nam_inv']['theta_sol_limit'],
          'theta_sol_midi_limit' : acf['nam_inv']['theta_sol_midi_limit'],
          'theta_sol_wlimit' : acf['nam_inv']['theta_sol_wlimit'],
          'typical_cov_rescale' : np.ones(3),
          'normalisation': np.ones((2,3,4,4)),
#          'normalisation_err': np.ones((2,3,4)),
          'normalisation_err': np.reshape(np.array(norm_err),(2,3,4)),
          'enable_normalisation':False,
          }
      }
    }

    # reorder filenames
    filelist = pcf['NAM_ALG_INPUT_FILES_PATH']['YFILEINP']
    latitudefile = filelist.pop(0)

    checkpoint_filenames = { 'band1' : { 'values': filelist[0],  'cov': filelist[1]},
                             'band2' : { 'values': filelist[2],  'cov': filelist[3]},
                             'band3' : { 'values': filelist[4],  'cov': filelist[5]} }
    filelist = filelist[6:]

    listkeys = ['band1', 'band2', 'band3', 'azimuth_sol', 'zenith_sol', 'azimuth_sat', 'zenith_sat']
    filenames = {k:[] for k in listkeys}
    # find the number of scenes from the len fo the input
    nb_scenes = int(len(filelist) / len(listkeys) + 0.00001)
    filenames['latitude'] = [latitudefile for i in range(0,nb_scenes)]
    for i in range(0,nb_scenes):
        for k in listkeys:
            filenames[k].append(filelist.pop(0))

    # Transform list into tuple to make it easier latter
    for k in listkeys  + ['latitude']:
        filenames[k] = tuple(filenames[k])

    input_dates = tuple([robust_date_parse(filename) for filename in filenames['band1']])

    # Transform pcf file
    pout = {'nam_alg_modes': {
                'mode': pcf['nam_alg_modes']['mode']
           },
           'globalconfig': {
                'remove_bad_quality_reflectance': False,
                'n_channels_ref':3,
                'use_cache':False,
                'logdir':'log/'
           },
           'dates': {'output_date': 'infer_from_output_filename'},
           'input': {
               'MSG': {
                  'input_enddate_key': 'IMAGE_ACQUISITION_TIME',
                  'input_startdate_key': 'IMAGE_ACQUISITION_TIME',
                  'input_dates' : input_dates,
                  'dataloc_reader_name': 'dataloc_msg_retrocompatibility',
                  'xoutputsize' : 3712,
                  'youtputsize' : 3712,
                  'sat_specific': 0,
                  'azimuth_sat': {
                      'band1': {'filenames':filenames['azimuth_sat'], 'data_reader_name': 'msg_angle'},
                      'band2': {'filenames':filenames['azimuth_sat'], 'data_reader_name': 'msg_angle'},
                      'band3': {'filenames':filenames['azimuth_sat'], 'data_reader_name': 'msg_angle'},
                      'key': 'VAA', 'band_indexing_method': 'sparse', 
                      'band_indexing_list' : ['band1', 'band2', 'band3'], 
                      'scenes_dates_indexing_method': 'static'},
                  'azimuth_sol': { 'data_reader_name': 'msg_angle', 'filenames': filenames['azimuth_sol'], 'key': 'SAA', 'band_indexing_method': 'constant','scenes_dates_indexing_method': 'dynamic'},
                  'zenith_sat':  { 
                      'band1': {'filenames':filenames['zenith_sat'], 'data_reader_name': 'msg_angle'},
                      'band2': {'filenames':filenames['zenith_sat'], 'data_reader_name': 'msg_angle'},
                      'band3': {'filenames':filenames['zenith_sat'], 'data_reader_name': 'msg_angle'},
                      'key': 'VZA', 'band_indexing_method': 'sparse', 
                      'band_indexing_list' : ['band1', 'band2', 'band3'],
                      'scenes_dates_indexing_method': 'static'},
                  'zenith_sol':  { 'data_reader_name': 'msg_angle', 'filenames': filenames['zenith_sol'],  'key': 'SZA', 'band_indexing_method': 'constant','scenes_dates_indexing_method': 'dynamic'},
                  'latitude':    { 'data_reader_name': 'msg_latitude', 'filenames': filenames['latitude'], 'key': 'LAT', 'band_indexing_method': 'constant','scenes_dates_indexing_method': 'static'},
                  'longitude':   { 'data_reader_name': 'empty_longitude', 'filenames': filenames['latitude'],            'band_indexing_method': 'constant' ,'scenes_dates_indexing_method': 'static'},
                  'lwcs_mask': { 'key':'BRF_Q_Flag',
                      'band1': {'filenames':filenames['band1'], 'data_reader_name': 'msg_lwcs_mask'},
                      'band2': {'filenames':filenames['band2'], 'data_reader_name': 'msg_lwcs_mask'},
                      'band3': {'filenames':filenames['band3'], 'data_reader_name': 'msg_lwcs_mask'},
                      'band_indexing_method': 'full',
                      'scenes_dates_indexing_method': 'dynamic'
                  },
                  'toc_reflectance': { 'key':'BRF-TOC',
                      'band1': {'filenames':filenames['band1'], 'data_reader_name': 'msg_reflectance_toc'},
                      'band2': {'filenames':filenames['band2'], 'data_reader_name': 'msg_reflectance_toc'},
                      'band3': {'filenames':filenames['band3'], 'data_reader_name': 'msg_reflectance_toc'},
                      'band_indexing_method': 'full',
                      'scenes_dates_indexing_method': 'dynamic'
                  },
                  'toc_reflectance_cov': {
                      'band1': {'filenames':filenames['band1'], 'data_reader_name': 'empty_reflectance_toc_cov'},
                      'band2': {'filenames':filenames['band2'], 'data_reader_name': 'empty_reflectance_toc_cov'},
                      'band3': {'filenames':filenames['band3'], 'data_reader_name': 'empty_reflectance_toc_cov'},
                      'band_indexing_method': 'full',
                      'scenes_dates_indexing_method': 'dynamic'
                      },
                'output': {
                   'albedo'  : { 'filename': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][9],  'cov': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][9]},
                   'albedo-sp': {
                       'band1' : { 'filename': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][2], 'cov': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][2]},
                       'band2' : { 'filename': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][5], 'cov': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][5]},
                       'band3' : { 'filename': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][8], 'cov': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][8]}
                    },
                   'brdf': {
                       'band1' : { 'filename': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][0],  'cov': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][1]},
                       'band2' : { 'filename': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][3],  'cov': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][4]},
                       'band3' : { 'filename': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][6],  'cov': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][7]}
                    },
                   'brdf-d01': {
                       'band1' : { 'filename': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][10], 'cov': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][11]},
                       'band2' : { 'filename': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][12], 'cov': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][13]},
                       'band3' : { 'filename': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][14], 'cov': pcf['NAM_ALG_OUTPUT_FILES_PATH']['YFILEOUT'][15]}
                    },
                    'date_pattern': '1d', #'10_20_lastdayofthemonth'
                    'writer': 'msg_writer'
                    },
           'output_channel_names': ['C1', 'C2', 'C3'],
           'inputcheckpoint': {
               'filenames' : checkpoint_filenames,
               'reader': 'msg_brdf'
                }
               }
            }
        }
    return aout, pout
