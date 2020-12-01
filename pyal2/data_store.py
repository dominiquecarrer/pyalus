#!/usr/bin/env python 
##########################################################
# Configuration Manager :
# Algorithm and Product config file loading and adapting for each step
#
# @fpinaut
# *-*-2018 Ititiation
# 13-12-2018 light modification for yaml reading => c3s do not mean f90nlm 
#
import re
import collections
import logging
import hashlib
import os,sys
import os.path
import itertools
import math
import yaml
import datetime as dt
from datetime import timedelta
from copy import deepcopy

import numpy as np

from pyal2.exit_status import exit_status
from pyal2.utils.dict_utils import instanciate_keywords
from pyal2.utils.parsing import (last_day_of_the_month, robust_date_parse, 
            parse_boolean, parse_command_line_dates)
from pyal2.utils.dict_utils import get_param_in_tree, set_param_in_tree
from pyal2.utils.yaml import to_yaml_function, from_yaml_function
from pyal2.config_utils.f90nml_msg import f90nml_to_yaml_msg
from pyal2.config_utils.f90nml_c3s import f90nml_to_yaml_c3s
from pyal2.readers import get_dataloc_reader
# note that "readers" is a folder. The function "get_dataloc_reader" is located in readers/__init__.py
from pyal2.data_box import DataBox
from pyal2.utils.io import ensure_dir
from pyal2.utils.yaml import save_yaml
from pyal2.utils.dict_utils import instanciate_datetime


date_filters = {'10_20_lastdayofthemonth': ( timedelta(days=1),
                                             lambda x: (x.day == 10 or x.day == 20 or x.day == last_day_of_the_month(x)) ),
                #'15m':                     ( timedelta(minutes=1),
                #                             lambda x: (x.minute == 0 or x.minute == 15 or x.minute == 30 or x.minute == 45)  )
                '1d':                     ( timedelta(days=1),
                                             lambda x: True)
            }

class DataStore(dict):
    """ The DataStore is responsible to reads the config files to get the relevant parameters,
    it also parses the inputfiles to get their dates, and creates one :class:`DataBox`
    for each step (date) to process.
    """

    def load_config(self, acf, pcf, dates=None, startseries=None,
                    window_predefined=None, window_lat=None, window_lon=None,
                    debuglevel=0, keywords=None, config_format=None,
                    instruments=None):
        """
        This is the main function to initialize DataStore object.
        It reads the config files to get the relevant parameters, it also
        parses the inputfiles to get their dates, and creates one DataBox
        for each step (date) to process.

        Required parameters are the algorithm config file (acf) and the product config file (pcf).
        Optional parameters to overwrite the values from the config files :

        :param dates: Start and end dates (as strings)
        :type dates: [string, string]
        :param startseries: For the first time step of the algorithm, a
        value set to 'False' will attempt to load an a priori BRDF file
        checkpoint, which must be specific in the pcf file. 'True' will
        not attempt to load a pervious brdf file and will use default values
        with high variance. Note that this parameter impacts **only the first
        date to be processed** : if several output dates are computed with the
        same command, the BRDF checkpoint for the next steps (other than the
        first one) **will** be used, even if the parameter startseries is set to 'True'.**
        :type startseries: boolean
        :param window_predefined: not implemented.
        :param window_lat: list of two integers. Define a rectangle region (a subset) to process.
        Only these pixels will be processed.
        :param window_lon: see window_lat
        :param debuglevel: the higher the value is, the more verbose output will be.
        Will affect fortran code only.
        :param keywords: a dictionnary of {key:string}. BEFORE processing
        the yaml config files, all occurences of "{key}" will be replaced
        by the string. Useful for batch processing on several regions using
        the same config file.
        :param config_format: for backward compatibility, if set to 'f90nml_c3s',
        the acf and files will be transformed from a f90 namelist into standard
        yaml before using it.
        :type config_format: 'f90nml_c3s' or 'f90nml_msg'

        >>> to,lnk = '../test/testc3s_full/data_c3s_alldata','data_c3s_alldata'
        >>> if not os.path.realpath(lnk) == os.path.realpath(to): os.symlink(to, lnk)
        >>> dstore = DataStore();

        >>> dstore.load_config('../config/acf.c3s.multi-sensor.true.yaml', '../config/pcf.c3s.VGT.yaml', dates=[['2002-06-20','2002-07-20']], startseries=None, window_predefined=None, window_lat=[25,25], window_lon=[25,25], debuglevel=0, keywords={'year':'1998','name':'VGT','sensorname':'VGT','site':'Avignon'}, config_format='yaml', instruments=['VGT'])
        >>> dstore['n_channels_meas']
        [4]

        >>> dstore = DataStore();
        >>> dstore.load_config('../config/acf.c3s.multi-sensor.true.yaml', '../config/pcf.c3s.AVHRR_NOAA11.yaml', dates=[['2002-06-20','2002-07-20']], startseries=None, window_predefined=None, window_lat=[25,25], window_lon=[25,25], debuglevel=0, keywords={'year':'1988','name':'AVHRR11','sensorname':'AVHRR_NOAA11','site':'Avignon'}, config_format='yaml', instruments=['AVHRR_NOAA11'])
        >>> dstore['n_channels_meas']
        [3]

        #>>> dstore = DataStore();
        #>>> dstore.load_config('../config/acf.c3s.multi-sensor.true.yaml', '../config/pcf.c3s.AVHRR_NOAA7.yaml', dates=[['2002-06-20','2002-07-20']], startseries=None, window_predefined=None, window_lat=[25,25], window_lon=[25,25], debuglevel=0, keywords={'name':'AVHRR7','sensorname':'AVHRR_NOAA7','site':'Avignon'}, config_format='yaml', instruments=['AVHRR_NOAA7'])
        #>>> dstore['n_channels_meas']
        #[2]

        """

        if keywords is None: keywords = {}

        #  if required, transform the config files from f90 namelist into standard yaml
        if config_format == 'yaml':
            with open(acf,'r') as f: self.acf = yaml.unsafe_load(f)
            with open(pcf,'r') as f: self.pcf = yaml.unsafe_load(f)
        elif config_format == 'f90nml_c3s' or config_format == 'f90nmlc3s': 
                    self.acf, self.pcf = f90nml_to_yaml_c3s(acf, pcf)
        elif config_format == 'f90nml_msg' or config_format == 'f90nmlmsg': 
                    self.acf, self.pcf  = f90nml_to_yaml_msg(acf, pcf)
        else:
            logging.critical(f'Unknown config format {config_format}')
            exit_status("UNABLE_TO_CONFIG")


        if config_format != 'yaml':
            # write config file for logging purposes if required
            save_yaml(self.acf, f'log/{keywords.get("name","")}/{os.path.basename(acf)}')
            save_yaml(self.pcf, f'log/{keywords.get("name","")}/{os.path.basename(pcf)}')

        self['acf_file'] = acf
        self['pcf_file'] = pcf

        # all occurences of "{key}" will be replaced by its value from the dictionary "keywords"
        self.acf = instanciate_keywords(self.acf, keywords)
        self.pcf = instanciate_keywords(self.pcf, keywords)

        if instruments is None:
            instruments = self.pcf['input'].keys()
            logging.debug('No instrument defined in parameters, using pcf file : instruments = {instruments}')

        logging.debug('Parsing acf and pcf files is OK')
        # global config hook, read the parameters "globalconfig" in the acf and pcf and make it available eveywhere.
        # useful to debug and trace some issue. But DO NOT use it too much, it will break the logic of the code,
        # create confusion, prevent maintanabilty and give bad karma.
        self['globalconfig'] = {}
        self['globalconfig'].update(self.acf.get('globalconfig',{}))
        self['globalconfig'].update(self.pcf.get('globalconfig',{}))
        self['globalconfig']['debuglevel'] = debuglevel

        try:
            self['n_channels_ref'] = self['globalconfig']['n_channels_ref']
        except KeyError:
            self['n_channels_ref'] = 4
            logging.warning(f'No n_channels_ref provided, usind default value {self["n_channels_ref"]}')

        # initialisation of 'input' dictionnary
        self['input'] = dict()

        for j,instr in enumerate(instruments):

            # read relevant parameters, from acf and pcf file into the "self" config dict
            self[instr]= dict()
            self[instr]['output_dates'] = self._read_dates(args_dates=dates[j],
                    filename = self.pcf['input'][instr]['output']['albedo'].get('filename', None) 
                            or self.pcf['input'][instr]['output']['albedo']['band1']['filename'],
                    configfile_dates = self.pcf['dates']['output_date'],
                    date_filter=self.pcf['input'][instr]['output'].get('date_pattern', None))

            logging.info('We finishted _read_dates in load_config, instr ' + str(instr))

            # read the checkpoint parameters
            self[instr]['inputcheckpoint'] = self.pcf['input'][instr]['inputcheckpoint']

            # use cache ?
            self.pcf['input'][instr]['use_cache'] = self.pcf['globalconfig']['use_cache']

            self[instr]['output'] = self.pcf['input'][instr]['output']

            self[instr]['startseries'] = (parse_boolean(startseries)
                                or self.pcf.get('startseries',None)
                                or self.acf.get('startseries',None)
                                or self.acf.get('nam_inv',{}).get('startseries',None)
                                )

            # Change the firstdate with the one readed in sensors_constants => first date
            #self[instr]['inputcheckpoint']['firstdate'] = self[instr]['output_dates'][0].strftime('%Y/%m/%d')
            # parse input filenames to get their dates
            # this should populate self['input'][instr] and some metadata (xsize, ysize, etc)
            self.setup_input_one_sensor(self.pcf['input'][instr], instr)

            # if cropping is required, restrict the size of the zone to process
            # note that these xfullslice, yfullslice (zone to process) are not
            # related to xslice,yslice (chunk to process)
            if window_lat:
                self['xfullslice'] = slice(window_lat[0] - 1, window_lat[1] )
                self['xfullsize'] = self['xfullslice'].stop - self['xfullslice'].start
                logging.warn('Restricting to x slice : ' + str(self['xfullslice']))
            if window_lon:
                self['yfullslice'] = slice(window_lon[0] - 1, window_lon[1] )
                self['yfullsize'] = self['yfullslice'].stop - self['yfullslice'].start
                logging.warn('Restricting to y slice : ' + str(self['yfullslice']))


        # TODO : n_channels_meas is duplicated in some places, need to clean this up when doing multisensor
        #~ firstsensor = self['input']['sensors'][0]
        #~ self['sensorname'] = firstsensor
        #~ if len(self['input']['sensors']) != 1:
            #~ raise Exception('Multiple sensors detected in input {str(self["input"]["sensors"])}. Not implemented')
        #~ self['n_channels_meas'] = self['input'][firstsensor]['n_channels_meas']
        self['sensorname'] = instruments#self['input']['sensors'][:]
        self['n_channels_meas'] = list()
        list_to_del = list()

        for sensor in self.acf['spectral'].keys():
            if sensor in self['sensorname']:
                self['n_channels_meas'].append(self.acf['spectral'][sensor]['nbands'])
            else:
                # Deleting sensor in acf['spectral'] tree
                list_to_del.append(sensor)
        for sensor in list_to_del:
            del self.acf['spectral'][sensor]

        logging.warning(f'we will work on these sensors : '+ str(self['sensorname']))

        self.load_acf(self.acf, sensorlist=self['sensorname'], 
            n_channel_meas=self['n_channels_meas'], startseries=self[instr]['startseries'])

    def create_data_box(self, date, instrument, xslice, yslice, 
                        previous_date=None, make_sure_checkpoint_exists=True):
        """
        This function create a DataBox object : a copy of the main config
        which is specific to the current date.

        The algorithm relies on the value of the current BRDF state.
        For each time step a BRDF is saved and used for the next steps.
        As there are several possible ways to run the code, choosing
        the brdf file to load at each time step has multiple if-then-else tests.

        Note the use of :func:`pyal2.utils.dict_utils.instanciate_datetime`
        to transform a string template into a string specific to a given date.

        You can also look at the yaml files producted in the logs to
        understand the details and debug.
        """

        # Create an empty object
        logging.info(f'Creating a DataBox for date {date}, (using previous_date {previous_date})')
        dbox = DataBox(date, xslice, yslice)

        # fill the new object with the config that is relevant for the given date
        # and the given sensor
 
        dbox.filter_scenes_dates(self, instrument, outputdate = date)

        # perfom consistency check, remove incomplete scene, etc.
        dbox.cleanup_missing_data(instrument)

        dbox['previous_date'] = previous_date

        # Find the brdf a priori inputcheckpoint file if required.
        if previous_date is None: # No previous date : we are at the first time step.
                                  #Either we need to find a checkpoint to load, or we start the serie.

            if self['acf']['nam_inv']['startseries'] == True: # startseries == True in the config file
                # we will not load brdf file, default initial values will be used
                dbox['inputcheckpoint'] = None
                logging.info(f'First time step time step in this run : No need for brdf file checkpoint')

            else: # startseries == False in the config file
                # we do need to find brdf file(s) to load
                if 'firstdate' in self[instrument]['inputcheckpoint']:
                    firstdate = robust_date_parse(self[instrument]['inputcheckpoint']['firstdate'])
                    # use the date provided in the config file
                    dbox['inputcheckpoint'] = instanciate_datetime(deepcopy(self[instrument]['inputcheckpoint']), firstdate)
                else:
                    # no date is provided in the config file (inputcheckpoint dict) :
                    #the value of a filename for the 'inputcheckpoint' in the configfile must be a real filename
                    dbox['inputcheckpoint'] = self[instrument]['inputcheckpoint']
                    #if make_sure_checkpoint_exists:
                    #    if not os.path.isfile(dbox['inputcheckpoint']):
                    #        logging.critical(f'The brdf inputcheckpoint {dbox["inputcheckpoint"]}
                    # cannot be found. You may need to provide a initial date to resolve this string into a real filename')
                logging.info(f'First time step in this run : will use a first brdf file checkpoint : {self[instrument]["inputcheckpoint"]}')
        else:
            # if a previous date is available, we are not at the first time step.
            #Another time step has been run and its brdf checkpoint should be loaded
            logging.info(f'Not the first time step in this run : checkpoint = {self[instrument]["inputcheckpoint"]}')

            dbox['inputcheckpoint'] = instanciate_datetime(deepcopy(self[instrument]['inputcheckpoint']),
                                                           previous_date)
            dbox[instrument]['startseries'] = False
            logging.info(f'Not the first time step in this run : will use brdf file checkpoint from date {previous_date}: {dbox["inputcheckpoint"]}')

        # instanciate output filenames
        dbox[instrument]['output'] = instanciate_datetime(dbox[instrument]['output'], date)
        if self['acf']['nam_inv']['brdf_clim_activated']:
            dbox['input'][instrument]['brdf_clim'] = instanciate_datetime(dbox['input'][instrument]['brdf_clim'], date)
            dbox['input'][instrument]['brdf_clim_cov'] = instanciate_datetime(dbox['input'][instrument]['brdf_clim_cov'], date)
        # write to file for debug purposes
        logdir = dbox.get('globalconfig', {}).get('logdir',None)
        if logdir:
            dbox.to_yaml(f'{logdir}/dbox.{date}.yaml')
        return dbox

    def _read_dates(self, args_dates, filename, configfile_dates, date_filter=None):
        """ Handling of dates : 
            from commande line (higher priority),
            or from acf (second higher priority), 
            or if nothing is found, it uses the output filename to infer the date
        args_dates should be None, or a list of two parseable dates strings
        or a schedule file + appropriate key such as file://schedule.csv@AVHRR_NOAA17
        if configfile_dates == 'infer_from_output_filename', filename should end with a date string
        """

        # dates provided in command line
        dates = parse_command_line_dates(args_dates)

        # no date provided : infer from output filename
        if not dates and configfile_dates == 'infer_from_output_filename':
            dates = [robust_date_parse(filename)]
            logging.info('Date read from output filename ' + filename + ' : ' + str(dates))
            return dates

        # last chance : dates provided in algo config file
        if not dates:
            dates = [robust_date_parse(date) for date in configfile_dates ]
            logging.info('Dates to process from config file ' + str(dates))

        #########################################################

        # Now some dates must have been found
        if len(dates) != 1 and len(dates) != 2:
            logging.critical('Dates to process is ' + str(dates) + '. But this is expected to be a list of 1 or 2 elements.')

        if len(dates) > 1:
            # if there are several dates, use the first and the last to
            # expand to have a list of dates to process, matching the filter
            date_start, date_end = dates[0], dates[-1]
            timedelta, date_filter_function = date_filters[date_filter]
            curr = date_start
            dates = []
            while (curr <= date_end):
                if (date_filter_function is None) or date_filter_function(curr):
                    dates.append(curr)
                curr = curr + timedelta
            logging.info(str(len(dates)) + ' dates to process.')
            logging.debug(str(dates))
        return dates


    def setup_input_one_sensor(self, inputconfig, sensor):
        """
        Quick parse of all the available data and create dict of
        how to find data with date for each variable and each file.

        This function will created dictionaries following the scheme :

        :param inputconfig: input configuration for one sensor
        :type inputconfig: dict
        :rtype: dict of dict of dict date -> { sensor -> scene -> band -> reflectance,etc}
                                                               -> angle
                                                               -> lat/lon}

        See the output file in .yaml format to understand/check
        the structure of the nested dictionnary
        """

        # make a copy of the config dic because we are going to populate
        # it an we don't want to change the original input
        self['input'][sensor] = deepcopy(inputconfig)

        # The number of bands is infered from the input files :
        # This is the number of input layers starting with "band" followed by a number
        band_keys = [k for k in inputconfig['toc_reflectance'].keys() if re.match('^band[0-9]*$', k) ]
        self['input'][sensor]['n_channels_meas'] = len(band_keys)
        self['input'][sensor]['band_keys'] = band_keys
        logging.info(f'Sensor {sensor} : {band_keys}')

        # the list of input names will be used in data_manager_one_step.
        self['input'][sensor]['_names'] = []

        list_param = ["toc_reflectance", "toc_reflectance_cov", "lwcs_mask", "azimuth_sol", "azimuth_sat" \
                  , "zenith_sol", "zenith_sat", "latitude", "longitude"]

        if self.acf['nam_inv']['brdf_clim_activated'] is True:
            list_param.append('brdf_clim')
            list_param.append('brdf_clim_cov')

        for k in list_param:
            per_band = get_param_in_tree(self, ['input', sensor, k], 'band_indexing_method')
            if per_band == 'full':
                self['input'][sensor]['_names'] += [list(i) for i in itertools.product([k], band_keys)]
            elif per_band == 'sparse':
                band_keys = get_param_in_tree(self, ['input', sensor, k], 'band_indexing_list')
                self['input'][sensor]['_names'] += [list(i) for i in itertools.product([k], band_keys)]
            elif per_band == 'constant':
                self['input'][sensor]['_names'] += [[k]]
        self['input'][sensor]['_names'] = tuple(self['input'][sensor]['_names'])

        # initialize empty cache.
        cache = {}

        for sensorpath in self['input'][sensor]['_names']:

            # for each input data path
            path = [*sensorpath]
            # get the code and list of parameters names that are needed to read the data files
            logging.debug(f'Reading metadata {path}')
            #if sensorpath == 'brdf_clim':import ipdb; ipdb.set_trace()
            readername = get_param_in_tree(inputconfig, path, 'dataloc_reader_name')
            logging.info(f'Reading metadata for path {path}, using {readername}')
            dataloc_reader_function, required_params, datetime_params  = get_dataloc_reader(readername)
            logging.debug(f'The dataloc_reader_function ({dataloc_reader_function.__doc__}) needs the parameters {datetime_params}, {required_params}')

            if not inputconfig['use_cache']:
                required_params_dict = {p:get_param_in_tree(inputconfig, path, p) for p in required_params}
                dataloc, metadata = dataloc_reader_function(**{'output_dates':self[sensor]['output_dates'], **required_params_dict})
            else:
                # get cache key in case the files have aleady been opened before
                cache_dict = {p:get_param_in_tree(inputconfig, path, p) for p in datetime_params}
                cachekey, filecachekey = get_frozen_keys({'dataloc_reader_name':readername, **cache_dict})
                cachefile = f'cache/dataloc/{filecachekey}'
                logging.debug(f'Using cache {path}: f{filecachekey} : {cachekey}')

                if cachekey in cache:
                    # the (unique) cachekey has been found, reuse the value in cache
                    dataloc = cache[cachekey]
                elif os.path.exists(cachefile):
                    dataloc, metadata = from_yaml_function(cachefile)
                    cache[cachekey] = dataloc
                else:     
                    # the cache key has not been found, run the actual function to read
                    # data location from the files get the actual values for the required_parameters

                    required_params_dict = {p:get_param_in_tree(inputconfig, path, p) for p in required_params}

                    dataloc, metadata = dataloc_reader_function(**{'output_dates':self[sensor]['output_dates'], **required_params_dict})

                    # save into the cache
                    cache[cachekey] = dataloc
                    save_yaml([dataloc, metadata], filename = cachefile)

            # dataloc has been found, set the value in the appropriate place in the nested dictionary
            set_param_in_tree(self['input'][sensor], path, '_dataloc', value=dataloc)
            if not 'xoutputsize' in self:
                # do this only once
                # set also the sizes of the output
                self['xoutputsize'] = metadata['xoutputsize']
                self['youtputsize'] = metadata['youtputsize']
                self['xfullsize'], self['yfullsize'] = self['xoutputsize'], self['youtputsize']
                self['xfullslice'] = slice(0,self['xfullsize'])
                self['yfullslice'] = slice(0,self['yfullsize'])
                self['.xoutputsize'] = 'Comment: xoutputsize should be the size \
                of the output file, xfullslice should be the size of the input file. Currently, they are identical.'
                self['.xoutputsize.'] = 'When processing only 1/10 pixels or 1/100 pixels, \
                    they could be different, but this has not be implemented.'


    def load_acf(self, acf, sensorlist, n_channel_meas, startseries):
        """ Parse algorithm configuration file dictionnary. """
        self['acf'] = acf

        self['time_span_for_composition'] = timedelta(**self['acf']['nam_inv']['time_span_for_composition'])

        self['model_len'] = self['acf']['nam_inv']['model_len']
        # brdf model
        self['model_len'] = self['acf']['nam_inv']['model_len']

        # BEWARE : note the final .T to transpose the array.
        #The config format should be changed but this is keep
        # for now to ensure backward compatibility with old config files
        self['acf']['nam_inv']['sig_k_reg'] = np.array(self['acf']['nam_inv']['sig_k_reg'],
                                                       order='F', dtype='f4').reshape(self['n_channels_ref'],
                                                                                      self['model_len']).T.tolist()
        self['acf']['nam_inv']['k_reg'] = np.array(self['acf']['nam_inv']['k_reg'],
                                                   order='F', dtype='f4').reshape(self['n_channels_ref'],
                                                                                  self['model_len']).T.tolist()
        i=0
        # build read spectral normalisation coefficients matrix,
        # the input format should be changed to make it more clear
        for sensorname, spectralconfig in self['acf']['spectral'].items():

            logging.debug(sensorname)
            try:
                n_normalisation_type = 2
                
                if (spectralconfig['normalisation'] == []) or (spectralconfig['normalisation'] is None):
                    # give default value if spectral_normalisation is
                    # not set : identity with intercept=0.
                    logging.warning('No spectral normalisation coefficient provided. Using default identity matrix, with zero offset')
                    size = spectralconfig['nbands']
                    #~ b = np.zeros(size)
                    #~ a = np.identity(size)
                    #~ c1 = np.vstack((b,a)).T
                    #~ c2 = np.vstack((b,a)).T
                    #~ spectralconfig['spectral_normalisation'] = np.stack((c1,c2),axis=0)
                    spectralconfig['spectral_normalisation'] = np.zeros((2,size,size+1,4))
                    logging.error('warning line to remove and change')
                    shape = (n_normalisation_type, self['n_channels_ref'],4)
                    spectralconfig['spectral_normalisation_err'] = np.zeros(shape)
                    spectralconfig['spectral_normalisation_err'][:,:,0] = 0.
                    spectralconfig['spectral_normalisation_err'][:,:,1] = 1.
                    spectralconfig['spectral_normalisation_err'][:,:,2] = 0.
                    spectralconfig['spectral_normalisation_err'][:,:,3] = 1.
                else:
                    # some value has been given as a list. Do some manipulation to have the correct format
                    # TODO : use a better input format for the matrix.
                    data = spectralconfig['normalisation']
                    #shape = (n_normalisation_type, self['n_channels_ref'], self['n_channels_meas'][i]+1)
                    spectralconfig['spectral_normalisation'] = data
                    data = spectralconfig['normalisation_err']
                    shape = (n_normalisation_type, self['n_channels_ref'], 4)
                    spectralconfig['spectral_normalisation_err'] = np.reshape(data, shape)
                    i+=1
            except KeyError:
                logging.debug('Error during the normalization parameters reading')
                spectralconfig['spectral_normalisation'] = None
            #spectralconfig['spectral_normalisation'] = spectralconfig['spectral_normalisation'].tolist()

        self['model_id'] =  int(self['acf']['nam_inv']['model'])

        # read spectral coeff conversion from the config file into self.coeff
        self['n_mask'] = 2 # number of different conversion coefficients. It is 2 because there are 'nosnow' and 'snow'
        self['inalbedos_names'] =  ['DH', 'BH']
        self['outalbedos_names'] = ['VI', 'NI', 'BB']
        self['nalbedos'] = len(self['inalbedos_names'])
        self['n_outalbedos'] = len(self['outalbedos_names'])
        self['coeffs'] = np.zeros((self['n_channels_ref'] + 1,self['nalbedos'],self['n_outalbedos'], self['n_mask']), order='F', dtype='f4')
        for iout, outname in enumerate(self['outalbedos_names']):
            for iin, inname in enumerate(self['inalbedos_names']):
                fullname = inname + '-' + outname
                key_in_acf = ('co_' + outname + '_' + inname).lower()
                nosnow = self['acf']['nam_inv'][key_in_acf]
                snow = self['acf']['nam_inv'][key_in_acf + '_snow']
                logging.debug('Loaded coefficients for albedo (nosnow) ' + fullname +' :'+str(nosnow))
                logging.debug('Loaded coefficients for albedo (snow)   ' + fullname +' :'+str(snow))
                self['coeffs'][:,iin,iout,0] = nosnow
                self['coeffs'][:,iin,iout,1] = snow
        self['coeffs'] = self['coeffs'].tolist()

    def to_yaml(self, filename=None):
        """ This function saves the full state of the object DataStore into an human readable file """
        if filename: logging.debug(f'data_store : config written in {filename}')
        ensure_dir(filename)
        return to_yaml_function(dict(self), filename=filename)

    def load_full_yaml(self, filename):
        """ This function loads a object DataStore that has been saved
        into a file previously. It overwrites any value in the current object. """
        logging.debug(f'data_manager_creator : config read in {filename}')
        dic = from_yaml_function(filename, transform_lists_to_nparray=['spectral_normalisation_err'])
        self.clear()
        self.update(dic)
        self['loaded_from_file'] = filename

def get_frozen_keys(dic):
    #logging.debug(f'cache dict : {dic}')
    #dic = deepcopy(dic)
    for k in dic.keys():
        v = dic[k]
        if isinstance(v,list):
            dic[k] = tuple(v)
    d = collections.OrderedDict()
    for k in sorted(dic.keys()):
        d[k] = dic[k]

    filecachekey = hashlib.md5(str(d).encode("utf-8")).hexdigest()

    return frozenset(dic.items()), filecachekey

