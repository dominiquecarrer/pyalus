import f90nml
import math
import logging
import yaml

from pyal2.utils.io import ensure_dir

def f90nml_to_yaml_c3s(acffile, pcffile, prefix='log/', extension='.yaml'):
    with open(acffile,'r') as f:
        acf = f90nml.read(acffile)
    with open(pcffile,'r') as f:
        pcf = f90nml.read(pcffile)

    # Transform acf file
    time_span_for_composition = {'days': 20}
    logging.warn('C3S : Forcing time_span_for_composition to ' + str(time_span_for_composition))
    if not 'model_len' in acf['nam_inv']:
        acf['nam_inv']['model_len'] = 3
        logging.warn('C3S : model_len not defined in acf file, using default value model_len = ' + str(acf['nam_inv']['model_len']))

    n_channels_meas = len(acf['SPECTRAL']['channel_meas_names'])
    logging.info(f'Input sensor has {n_channels_meas} bands')

    aout = {
      'nam_inv' : {
        'initial_value_brdf_k'   : 0.,
        'initial_value_brdf_ck'  : 0.,
        'initial_value_brdf_age' : 0,
        'initial_value_brdf_quality' : 0,
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
        'brdf_clim_activated' : acf['nam_inv']['brdf_clim_activated'],
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
        'theta_ref_dh_limit' : acf['nam_inv']['theta_ref_dh_limit'],
        'theta_sat_limit' : acf['nam_inv']['theta_sat_limit'],
        'theta_sat_wlimit' : acf['nam_inv']['theta_sat_wlimit'],
        'theta_sol_limit' : acf['nam_inv']['theta_sol_limit'],
        'theta_sol_midi_limit' : acf['nam_inv']['theta_sol_midi_limit'],
        'theta_sol_wlimit' : acf['nam_inv']['theta_sol_wlimit'],
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
      'output_channel_names' : acf['spectral']['channel_ref_names'],
      'spectral': {
        '{sensor}': {
          'nbands':  n_channels_meas,
          'typical_cov_rescale' : acf['nam_inv']['typical_cov_rescale'],
          'normalisation': acf['spectral']['normalisation'],
          'normalisation_err': acf['spectral']['normalisation_err'],
          'enable_normalisation':True,
          }
      }
    }

    # the "options" parameters are ways to pass options to tweak the behaviour of the relevant parts of the code
    # these are hacks, bad and difficult to maintain. They will produce bugs. Difficult to track.
    # they should not be here. The input data should be cleaned up before processing and these options should be removed.
    # general options
    options = {}
    options['remove_bad_quality_reflectance_but_ignore_band4_qflag'] = acf['nam_proc'].get('remove_bad_quality_reflectance_but_ignore_band4_qflag', False)
    options['remove_bad_quality_reflectance'] = acf['nam_proc'].get('remove_bad_quality_reflectance', False)
    # options specific to lwcs
    lwcsoptions = {'ignore_quality_bit' : acf['nam_proc'].get('ignore_quality_bit', None) ,
                   'lwcs_mask_style' : acf['nam_proc'].get('lwcs_mask_style', None) }

    output_date = pcf['dates']['output_date']
    if not isinstance(output_date, list): # if this is a single date, transform it into a list
        output_date = [output_date]

    # Transform pcf file
    pout = {'nam_alg_modes': {
                'mode': pcf['nam_alg_modes']['mode']
           },
           'globalconfig': {
               **options,
               'logdir':'log/{name}/'
           },
           'dates': {'output_date': output_date },
           'input': {
               '{sensor}': {
                  'sat_specific': 2,
                  'azimuth_sat': {'data_reader_name': 'c3s_angle', 'key': '/LEVEL2B/GEOMETRY/VNIR/VAA', 'per_band': False,'type': 'dynamic'},
                  'azimuth_sol': {'data_reader_name': 'c3s_angle', 'key': '/LEVEL2B/GEOMETRY/SAA', 'per_band': False,'type': 'dynamic'},
                  'zenith_sat': {'data_reader_name': 'c3s_angle', 'key': '/LEVEL2B/GEOMETRY/VNIR/VZA', 'per_band': False,'type': 'dynamic'},
                  'zenith_sol': {'data_reader_name': 'c3s_angle', 'key': '/LEVEL2B/GEOMETRY/SZA', 'per_band': False,'type': 'dynamic'},
                  'dataloc_reader_name': 'dataloc_c3s_vgt',
                  'filenames': pcf['INPUTFILES']['FILENAMES'],
                  'input_enddate_key': 'time_coverage_end',
                  'input_startdate_key': 'time_coverage_start',
                  'latitude': {'data_reader_name': 'c3s_latitude', 'key': 'latitudes', 'per_band': False,'type': 'dynamic'},
                  'longitude': {'data_reader_name': 'c3s_longitude', 'key': 'longitudes', 'per_band': False,'type': 'dynamic'},
                  'lwcs_mask': {'data_reader_name': 'c3s_lwcs_mask', 'key': '/LEVEL2B/QUALITY/SM', 'n_channels': n_channels_meas, 'per_band': False, 'options':lwcsoptions,'type': 'dynamic'},
                  'toc_reflectance': {
                      **{f'band{i}': {'data_reader_name': 'c3s_reflectance_toc', 'key': f'/LEVEL2B/RADIOMETRY/band{i}/TOC'} for i in range(1,n_channels_meas+1)},
                      'per_band': True,
                      'type': 'dynamic'
                  },
                  'toc_reflectance_cov':{
                      **{f'band{i}': {'data_reader_name': 'c3s_reflectance_toc', 'key': f'/LEVEL2B/RADIOMETRY/band{i}/TOC_ERR'} for i in range(1,n_channels_meas+1)},
                      'per_band': True,
                      'type': 'dynamic'
                    }
                }
            },
           'output_channel_names' : acf['spectral']['channel_ref_names'],
           'inputcheckpoint': {
               'filename' : pcf['INPUTCHECKPOINT']['brdf'],
               'firstdate' : pcf['DATES'].get('checkpoint_date', None),
               'reader': 'c3s_brdf'
            },
           'output': {
               'albedo': {
                   'filename': pcf['OUTPUTFILES']['albedos'],
                },
               'brdf': {
                   'filename': pcf['OUTPUTFILES']['brdf'],
                },
               'date_pattern': '10_20_lastdayofthemonth',
               'writer': 'c3s_writer'
           }
        }
    return aout, pout
