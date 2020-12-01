#!/usr/bin/env python
import f90nml
import logging
import os
from copy import deepcopy
from pyal2.exit_status import exit_status
from pyal2.utils.dict_utils import get_param_in_tree, set_param_in_tree
from pyal2.utils.yaml import to_yaml_function, from_yaml_function
from pyal2.readers import get_data_reader
# note that "readers" is a folder. The function "get_data_reader" is located in readers/__init__.py
from pyal2.readers.stacking import stack_it
from datetime import datetime
from datetime import timedelta

class DataBox(dict):
    def __init__(self, date, xslice, yslice):
        self['date'] = date
        self['xslice'] = xslice
        self['yslice'] = yslice


    def filter_scenes_dates(self, dstore, sensor, outputdate):
        """ This function filters the scenes dates available from the dstore.
        It keeps only the dates that are relevant for the current time step and
        to store them in the newly created DataBox object """

        # create a deep copy of the dstore dict because we will delete the information
        # about files that are irrelevant for the current date.

        self.update(deepcopy(dstore))

        for path in self['input'][sensor]['_names']: # the variable "path" loops through all input data layers
            if (path[-1] is 'brdf_clim') or (path[-1] is 'brdf_clim_cov'): continue
            # We there exclude the BRDF_clim criteria to select the available dates for the calculation of Albedo
            # The concequence could be that no BRDF clim is found but we continue anyway to process.
            
            data_type = get_param_in_tree(self, ['input', sensor] + path, 'scenes_dates_indexing_method')

            logging.debug(f' in data_box filter_scenes_dates we now treat {path}')
            # get the data location : filenames for this input layer
            dataloc = get_param_in_tree(self, ['input',sensor] + path, '_dataloc')
            # get ALL the dates that are available for this layer

            availabledates = list(dataloc.keys())

            # using the time_span from the config, select only
            # the relevant dates in relevant_scene_dates
            time_span_for_composition_in_days = self['time_span_for_composition']
            relevant_scene_dates = compute_relevant_scenes_dates(availabledates,
                                                                 outputdate,
                                                                 time_span_for_composition_in_days,
                                                                 [sensor, path])
            logging.info(f'{sensor}/{path}: {len(relevant_scene_dates)} dates ({len(availabledates)} available)')
            # remove the dates that are not relevant
            if data_type == 'dynamic':
                for toremove in (set(availabledates) - set(relevant_scene_dates)):
                    del dataloc[toremove]
            elif data_type == 'static':
                relevant_scene_dates = availabledates

            logging.debug(f' Length of the relevant_scene_dates is now {len(relevant_scene_dates)} ')
            # and save the list of dates in the DataBox object
            # to keep the information about their order (even if we can alway reorder them)
            set_param_in_tree(self, ['input',sensor] + path,
                              '_scenes_dates', value=relevant_scene_dates)
            set_param_in_tree(self, ['input',sensor] + path,
                              '_scenes_dates.comment',
                              value=f'This list contains all the relevant scene dates to compute output for date ({outputdate})')


    def cleanup_missing_data(self, sensor):
        """ This function ensure that incomplete scenes are removed : for a given date, if an
        input data layer is missing, all other layers are also removed for this date. """

        # get all available dates
        alldates = []

        for path in self['input'][sensor]['_names']:
            alldates += get_param_in_tree(self, ['input',sensor] + path, '_scenes_dates')
        # make it a set (unique value and allow to compute difference with "-")
        alldates = set(alldates)
        # find missing data dates
        toremove = []
        for path in self['input'][sensor]['_names']:

            data_type = get_param_in_tree(self, ['input', sensor] + path, 'scenes_dates_indexing_method')
            logging.debug(f'data type in cleanup_missing_data {data_type}')

            if data_type == 'dynamic':
                dates_for_this_path = get_param_in_tree(self, ['input',sensor] + path, '_scenes_dates')
                missing = alldates - set(dates_for_this_path)
                logging.debug(f'find missing : {path} :  {len(dates_for_this_path)} : {len(missing)}')
                if missing:
                    logging.error(f'{sensor} : Removing date {missing} because {path} data is missing')
                toremove += missing
        fulldates = sorted(list(alldates - set(toremove)))

        for path in self['input'][sensor]['_names']:
            data_type = get_param_in_tree(self, ['input', sensor] + path, 'scenes_dates_indexing_method')
            if data_type == 'dynamic':
                set_param_in_tree(self, ['input',sensor] + path, '_scenes_dates', value=fulldates)
                logging.debug(f"{len(fulldates)} dates actually will be used for {sensor} {path}")
            else:
                dateslist = get_param_in_tree(self, ['input', sensor] + path, '_scenes_dates')
                dateslist = dateslist * len(fulldates)
                set_param_in_tree(self, ['input',sensor] + path, '_scenes_dates', value=dateslist)
                logging.debug(f"{len(dateslist)} dates actually will be used for {sensor} {path}")
                logging.debug(f"Some dates were actually artificially replicated for {sensor} {path}")

    def get_data(self, internalkey, sensor):
        # loop through all sensors, even multi sensor is not implemented :
        # dbox['input']['sensors'] should have only one element.

        logging.debug(f'Reading {internalkey} data for sensor {sensor}')
        indexing_method = get_param_in_tree(self, ['input', sensor, internalkey], 'band_indexing_method')
        if indexing_method == 'full':
            return self.get_data_per_band(sensor, internalkey)
        elif indexing_method == 'sparse':
            return self.get_data_sparse(sensor, internalkey)
        elif indexing_method == 'constant':
            return self.get_data_all_bands(sensor, internalkey)

    def get_data_all_bands(self, sensor, internalkey):
        """ This function uses the config dictionnary to locate the appropriate
        code that must be used to read the data.  The piece of code to run is
        located in the folder 'readers'.  The function 'get_data_reader()'
        (which is in readers/__init__.py) is responsible to transform the string
        "readername" into data_reader_class  (code that can read the data) and
        data_params (list params required by data_reader_class).  Then actual data is
        read and the return value of the get_data function is an object
        containing the data and some logging information. This function is used
        when all bands need to be read together """
        path = ['input', sensor, internalkey]
        # get the reader from the config
        readername = get_param_in_tree(self, path , 'data_reader_name')
        data_reader_class, data_params = get_data_reader(readername)
        # get the actual value of the parameters required by this reader
        data_params_dict = {p:get_param_in_tree(self, path, p) for p in data_params}
        data_object = data_reader_class(name=internalkey)
        # read the data
        logging.debug(f' using {readername} {path}, and parameters {data_params_dict.keys()}')
        data_object = data_object.load(**{'scenes_dates': get_param_in_tree(self, path , '_scenes_dates'),
                                          'xslice'      : get_param_in_tree(self, [], 'xslice'),
                                          'yslice'      : get_param_in_tree(self, [], 'yslice'),
                                          'dataloc'     : get_param_in_tree(self, path , '_dataloc'),
                                          **data_params_dict})
        logging.info(f'Data loaded {internalkey} : {data_object.values.shape} matrix for sensor {sensor}')
        return data_object

    def get_data_per_band(self, sensor, internalkey):
        """ This function uses the config dictionnary to locate the appropriate code that
        must be used to read the data. The piece of code to run is located in the folder
        'readers'. The function 'get_data_reader()' (which is in readers/__init__.py) is
        responsible to transform the string "readername" into data_reader_class (code
        that can read the data) and data_params (list params required by
        data_reader_class). Then actual data is read and the return value of the get_data
        function is an object containing the data (along with some logging information).
        This function is used when each band needs to be read separately. Then it
        aggregate them together """

        # there are multiple values for this layer, one for each band.
        # Find the paths to the config for each band
        band_keys = get_param_in_tree(self, ['input', sensor, internalkey], 'band_keys')
        paths = [['input', sensor, internalkey, band_key] for band_key in band_keys]

        data_objects = []
        for path in paths:
            # get the reader from the config
            readername = get_param_in_tree(self, path , 'data_reader_name')
            data_reader_class, data_params = get_data_reader(readername)

            # get the actual value of the parameters required by this reader
            data_params_dict = {p:get_param_in_tree(self, path, p) for p in data_params}
            data_object = data_reader_class(name=internalkey)
            # read the data
            logging.debug(f' using {readername} {path}, and parameters {data_params_dict.keys()}')
            data_object = data_object.load(**{'scenes_dates': get_param_in_tree(self, path , '_scenes_dates'),
                                              'xslice'      : get_param_in_tree(self, [], 'xslice'),
                                              'yslice'      : get_param_in_tree(self, [], 'yslice'),
                                              'dataloc'     : get_param_in_tree(self, path , '_dataloc'),
                                              **data_params_dict})
            data_objects.append(data_object)

        # now the list "data_objects" contains a list of matrix, let us merge it into one unique matrix
        # a drawback of moving the data around like this is slightly slower than loading
        # directly into the final matrix, but this is not a real problem considering
        # that the moves performed in memory are very fast compared to reading from disk.
        # the main advantage of this is to simplify the I/O code (and to allow easily a different
        # configuration for each band if needed)
        data_object = stack_it(data_objects, sensorname=sensor)

        logging.info(f'Data loaded {internalkey} : {data_object.values.shape} matrix for sensor {sensor}')
        return data_object

    def get_data_sparse(self, sensor, internalkey):
        """ This function uses the config dictionnary to locate the appropriate code that
        must be used to read the data. The piece of code to run is located in the folder
        'readers'. The function 'get_data_reader()' (which is in readers/__init__.py) is
        responsible to transform the string "readername" into data_reader_class (code
        that can read the data) and data_params (list params required by
        data_reader_class). Then actual data is read and the return value of the get_data
        function is an object containing the data (along with some logging information).
        This function is used when each band needs to be read separately. Then it
        aggregate them together """

        # there are multiple values for this layer, one for each band.
        # Find the paths to the config for each band
        #~ band_keys = get_param_in_tree(self, ['input', sensor, internalkey], 'band_keys')
        try:
            band_indices = get_param_in_tree(self, ['input', sensor, internalkey], 'band_indexing_list')
        except:
            logging.error(' Error in get_data_sparse ')
            exit_status('UNABLE_TO_PROCESS')


        paths = [['input', sensor, internalkey, band_key] for band_key in band_indices]

        data_objects = []
        for path in paths:
            # get the reader from the config
            readername = get_param_in_tree(self, path , 'data_reader_name')
            data_reader_class, data_params = get_data_reader(readername)

            # get the actual value of the parameters required by this reader
            data_params_dict = {p:get_param_in_tree(self, path, p) for p in data_params}
            data_object = data_reader_class(name=internalkey)
            # read the data
            logging.debug(f' using {readername} {path}, and parameters {data_params_dict.keys()}')
            data_object = data_object.load(**{'scenes_dates': get_param_in_tree(self, path , '_scenes_dates'),
                                              'xslice'      : get_param_in_tree(self, [], 'xslice'),
                                              'yslice'      : get_param_in_tree(self, [], 'yslice'),
                                              'dataloc'     : get_param_in_tree(self, path , '_dataloc'),
                                              **data_params_dict})
            data_objects.append(data_object)

        # now the list "data_objects" contains a list of matrix, let us merge it into one unique matrix
        # a drawback of moving the data around like this is slightly slower than loading
        # directly into the final matrix, but this is not a real problem considering
        # that the moves performed in memory are very fast compared to reading from disk.
        # the main advantage of this is to simplify the I/O code (and to allow easily a different
        # configuration for each band if needed)
        data_object = stack_it(data_objects, sensorname=sensor)

        logging.info(f'Data loaded {internalkey} : {data_object.values.shape} matrix for sensor {sensor}')
        return data_object

    def get_debug_info_array(self):
        xslice = self['xslice']
        yslice = self['yslice']
        return [xslice.start or 0, xslice.stop or 0, xslice.step or 1,
                yslice.start or 0, yslice.stop or 0, yslice.step or 1,
               (xslice.start is None) * 1, (xslice.stop is None) * 1, (xslice.step is None) * 1,
               (yslice.start is None) * 1, (yslice.stop is None) * 1, (yslice.step is None) * 1]


    def to_yaml(self, filename=None):
        """ This function saves the full state of the object DataStore into an human readable file """
        return to_yaml_function(dict(self), filename=filename)

    def load_full_yaml(self, filename):
        """ This function loads a object DataStore that has been saved into a file previously.
        It overwrites any value in the current object. """

        dic = from_yaml_function(filename, transform_lists_to_nparray=['spectral_normalisation_err'])
        self.clear()
        self.update(dic)
        self['loaded_from_file'] = filename


def compute_relevant_scenes_dates(availabledates, date, time_span_for_composition_in_days, info):
    """ select dates in the composition time span (20 days usually),
    from the available dates in the input data. Note: This will works
    as long as we take all data in a given day.""" # TODO
    logging.debug(f' The availabledates length is now {len(availabledates)} ')
    datemax = datetime(date.year, date.month, date.day) + timedelta(days=1) # +1 : rounding to end of day
    datemin = datemax - time_span_for_composition_in_days - timedelta(days=1)  # -1 : rounding to start of day
    scenes_dates = sorted([d for d in availabledates if (d < datemax) and (d >= datemin)])
    if len(scenes_dates) == 0:
        logging.error(f'No scene available in the data for {info} between ' + str(datemin) + ' and ' + str(datemax))
    else:
        logging.debug(f'{info} : using data from ' + str(scenes_dates[0]) + ' to ' + \
                      str(scenes_dates[-1]) + ' (' + str(len(scenes_dates)) + ' scenes)')
    for i, d in enumerate(scenes_dates):
        logging.debug(str(i) + ' ' +str(d))
    return scenes_dates

