#!/usr/bin/env python 
from pyal2.readers.generic import GenericReader
from pyal2.utils.augmented_netcdf import AugmentedNetcdfDataset
import logging
import numpy as np
import netCDF4

data_params = ['key', 'n_channels', 'options']

initial_missing_value = 0b010 # this value will be modified when the method 'adapt_mask_to_SAF' is called

def _binary_repr_array(array,typ=None):
    """ Private function to write textual representation of LWCS_mask. For debugging and logging purposes """
    outtab = []
    for x in array.flatten():
        outtab.append(str(x)+':'+np.binary_repr(x) + ':' + _string_repr(x, typ))
    return ' '.join(outtab)

def _string_repr(xbin,typ):
    """ Private function to write textual representation of LWCS_mask. For debugging and logging purposes. Only typ='saf' is supported """
    if np.isnan(xbin): return 'nan'
    xbin = int(xbin)
    out = ''
    if typ == 'saf':
        landsea = np.bitwise_and(xbin, 0b11) # land sea bits
        if landsea == 0b01 :
            out=out+'land'
        elif landsea == 0b00 :
            out=out+'sea'
        elif landsea == 0b11 :
            out=out+'inland-water'
        elif landsea == 0b10 :
            out=out+'space'
        else:
            out=out+'ERROR'+str(landsea)
        out=out+'.'

        mask = np.bitwise_and(xbin, 0b11100) # clear/shadow/undef/cloud/ice bits
        if mask == 0b00100 :
            out=out+'clear'
        elif mask == 0b10100 :
            out=out+'shadow'
        elif mask == 0b00000 :
            out=out+'nomask'
        elif mask == 0b01100 :
            out=out+'cloud'
        elif mask == 0b10000 :
            out=out+'snow'
        else:
            out=out+'error'+str(mask)

    if typ == 'c3s-avhrr':
        landsea = np.bitwise_and(xbin, 0b1000) # land sea bits
        if landsea == 0b1000 :
            out=out+'land'
        elif landsea == 0b0000 :
            out=out+'sea'
        out=out+'.'

        mask = np.bitwise_and(xbin, 0b111) # clear/shadow/undef/cloud/ice bits
        if mask == 0b000 :
            out=out+'clear'
        elif mask == 0b001 :
            out=out+'shadow'
        elif mask == 0b010 :
            out=out+'nomask'
        elif mask == 0b011 :
            out=out+'cloud'
        elif mask == 0b100 :
            out=out+'snow'
        else:
            out=out+'error'+str(mask)
        out=out+'.'

        def is_on(x, nbit):
            return np.bitwise_and(x, nbit) == nbit

        if is_on(xbin, 0b10000000000) and is_on(xbin, 0b1000000): #  ok
            out=out+'o'
        else:
            out=out+'x'

        if is_on(xbin, 0b01000000000) and is_on(xbin, 0b0100000): #  ok
            out=out+'o'
        else:
            out=out+'x'

        if is_on(xbin, 0b00100000000) and is_on(xbin, 0b0010000): #  ok
            out=out+'o'
        else:
            out=out+'x'

    return out

def adapt_mask_to_SAF(data, old_missing):
    """ Converts SPOT-VGT landwater mask into SAF landwater mask format. Convert also the missing value. """
    missing_mask = (data == old_missing)
    #self.newdata = np.zeros_like(data)
    #           Spot        LSA-SAF
    # Land      1...   ->   01
    # Sea       0...   ->   00
    #                       11 inland water
    #                       10 space
    landsea = np.right_shift(np.bitwise_and(data, 0b1000),3) # land sea bit

    #           Spot        LSA-SAF
    # Clear     000    ->   001..  Clear
    # Shadow    001    ->   101..  Shadow
    # Undef     010    ->   000..  Nomask
    # Could     011    ->   011..  Cloud
    # Ice       100    ->   100..  Snow
    #                              shadow_X
    mask = np.bitwise_and(data, 0b0111) # clear/shadow/undef/cloud/ice

    data[:] = 0b100000
    data[mask == 0b000] = 0b00100
    data[mask == 0b001] = 0b10100
    data[mask == 0b010] = 0b00000
    new_missing = 0b000
    data[mask == 0b011] = 0b01100
    data[mask == 0b100] = 0b10000

    data = data + landsea

    if np.any(data == 0b100000):
        logging.error('error converting lwcs_mask (transformed) ')

    data += 0b10000000 # add bit "processed"
    #new_missing += 0b10000000 # add bit "processed"
    data[missing_mask] = 0
    return data, new_missing

class LWCS_mask(GenericReader):
    """ Reader for LWCS_mask data """
    def load(self, key, xslice, yslice, scenes_dates, dataloc, n_channels, options):
        ignore_quality_bit = options.get('ignore_quality_bit', None)
        lwcs_mask_style = options.get('lwcs_mask_style','VGT')
        # save dates for debug purposes
        self.scenes_dates = scenes_dates

        # initialise empty matrix of the right size, with nan values (this assumes that xslice.step = 1 or None)
        shape = (xslice.stop - xslice.start, yslice.stop - yslice.start, n_channels, len(self.scenes_dates))
        self.missing = initial_missing_value
        self.values = np.full(shape, self.missing, order='F', dtype='int8')

        # loop through all each input scene date
        for idate, d in enumerate(self.scenes_dates):
            filename = dataloc[d]['filename']

            # save filename for debug purposes
            self.filenames[d] = filename
            logging.debug(str(d) + ' ' + filename )

            try:
                # actual reading of the data
                with AugmentedNetcdfDataset(filename,'r') as f:
                    for iband in range(0,n_channels):
                        # first dimension is the date, there is only one date per file. Therefore we have a 0 here
                        self.values[:,:,iband,idate] = f[key][0,xslice,yslice]
                    self.show_info(self.name, f[key])
            except Exception as e:
                # if anything bad happenned when reading the data
                logging.error('Problem reading ' + filename + '/' + 'key' + ' to get the ' + self.name + ' ' + str(e))
                # just log the problem and skip it
                continue
            logging.debug('initial lwcs_mask (first pixel) ' + self.name + ' data = '+str(_binary_repr_array(self.values[0,0,:])))

        try:
            self.badquality = np.zeros(self.values.shape, order='F', dtype='bool')
            if ignore_quality_bit is None:
                if lwcs_mask_style == 'VGT':
                    quality_bits =[0b00010000,0b00100000,0b01000000,0b10000000] # SWIR BLUE RED NIR
                    quality_bits = quality_bits[0:n_channels]
                    for iband, bit in enumerate(quality_bits):
                            self.badquality[:,:,iband,:] = (np.bitwise_and(self.values[:,:,iband,:], bit) != bit)
                elif lwcs_mask_style == 'AVHRR':
                    logging.debug(f'Filtering bad reflectances : self.values[:,:,:,:] {self.values[:,:,:,:]} ')
                    self.badquality = np.zeros(self.values.shape, order='F', dtype='bool')
                    logging.debug(f'1 Filtering bad reflectances : badquality = {self.badquality}')
                    if n_channels == 2:
                        # this is how it how it should be but the bits 8 9 10 seems to be absents
                        #self.badquality[:,:,0,:] = (np.bitwise_and(self.values[:,:,0,:], 0b10001000000) == 0b10000000000) # band b1 : bits 10 and 6
                        #self.badquality[:,:,1,:] = (np.bitwise_and(self.values[:,:,1,:], 0b01000100000) == 0b01000000000) # band b2 : bits 9  and 5
                        self.badquality[:,:,0,:] = (np.bitwise_and(self.values[:,:,0,:], 0b00001000000) == 0b00000000000) # band b1 : bits 6
                        logging.debug(f'2 Filtering bad reflectances : {self.values[:,:,0,:]} badquality = {self.badquality}')
                        self.badquality[:,:,1,:] = (np.bitwise_and(self.values[:,:,1,:], 0b00000100000) == 0b00000000000) # band b2 : bits 5
                        logging.debug(f'2 Filtering bad reflectances : {self.values[:,:,1,:]} badquality = {self.badquality}')
                    elif n_channels == 3:
                        # this is how it how it should be but the bits 8 9 10 seems to be absents
                        #self.badquality[:,:,0,:] = (np.bitwise_and(self.values[:,:,0,:], 0b10001000000) == 0b10000000000) # band b1 : bits 10 and 6
                        #self.badquality[:,:,1,:] = (np.bitwise_and(self.values[:,:,1,:], 0b01000100000) == 0b01000000000) # band b2 : bits 9 and 5
                        #self.badquality[:,:,2,:] = (np.bitwise_and(self.values[:,:,2,:], 0b00100010000) == 0b00100000000) # band b3a : bits 8 and 4
                        self.badquality[:,:,0,:] = (np.bitwise_and(self.values[:,:,0,:], 0b00001000000) == 0b00000000000) # band b1 : bits 6
                        self.badquality[:,:,1,:] = (np.bitwise_and(self.values[:,:,1,:], 0b00000100000) == 0b00000000000) # band b2 : bits 5
                        self.badquality[:,:,2,:] = (np.bitwise_and(self.values[:,:,2,:], 0b00000010000) == 0b00000000000) # band b3a : bits 4
                        logging.debug(f'3 Filtering bad reflectances : badquality = {self.badquality}')
            else:
                logging.warn(f'Option ignore_quality_bit is set to {ignore_quality_bit} -> force value of qflag to "good quality".')
                self.badquality[:,:,:,:] = False

        except:
            logging.error('Problem reading bad quality of the lwcs_mask. Ignoring it. DO NOT IGNORE THIS ERROR')

        logging.debug(f'lwcs_mask missing initial : {self.missing}')
        self.values, self.missing = adapt_mask_to_SAF(self.values, self.missing)
        logging.debug(f'lwcs_mask missing transformed : {self.missing}')
        logging.debug('initial lwcs_mask (transformed to SAF) ' + self.name + ' data = '+str(_binary_repr_array(self.values[0,0,0,:], 'saf')))

        logging.debug('extract of ' + key + ' data = '+str(self.values[0,0,:,:]))
        return self

    def remove_bad_quality_reflectance_but_ignore_band4_qflag(self, reflectance,reflectance_cov):
        """ This function is tricky. Read carefully the comments. """
        logging.warn('Removing bad quality reflectance based on qflag value. But ignore the SWIR flag')

        # increase covariance of bad quality data
        reflectance_cov.values[self.badquality] = reflectance_cov.values[self.badquality] * 10.

        # find real bad quality pixels ignoring last band (swir)
        badquality_ignoring_swir =  (np.sum(self.badquality[:,:,[1,2,3],:], axis=2) > 1)
        # set swir flag to good quality
        self.badquality[:,:,0,:] = np.bitwise_and(self.badquality[:,:,0,:], badquality_ignoring_swir)
        # put all bad reflectance value to nan
        reflectance.values[self.badquality] = np.nan
        return

    def remove_bad_quality_reflectance(self, reflectance,reflectance_cov):
        """ This function is tricky. Read carefully the comments. """
        logging.info('Removing bad quality reflectance based on qflag value.')
        # increase covariance of bad quality data
        #reflectance_cov.values[self.badquality] = reflectance_cov.values[self.badquality] * 10.

        # First take the quality flag into account to remove the reflectances that have been flagged as bad quality. Set them to np.nan
        reflectance.values[self.badquality] = np.nan

        # Second step is to propagate the np.nan value to the other band : if one reflectance is np.nan for a given band, the values for other bands should be set to np.nan
        # Note that we rely here on the fact that the reflectance data's third dimension (i.e. 2) is the "band" dimension.

        # the variable "bad" is one dimension smaller that the initial data 'reflectance.values'.
        bad = np.isnan(reflectance.values[:,:,:,:]).any(axis=2)
        # the variable "bad_extended" has the same size as the initial data.
        # it will be build in order to find which data should be set to nan
        bad_extended = np.full(reflectance.values.shape, False, order='F', dtype='bool')

        # for each band, the information that at least one band is bad quality is propagated to the other band
        for iband in range(0,reflectance.values.shape[2]):
            bad_extended[:,:,iband,:] = bad[:,:,:]

        # now apply the filter
        reflectance.values[bad_extended] = np.nan


    def to_xr(self):
        """ xarray serialisation """
        import xarray as xr
        return xr.DataArray(self.values[:,:,:],
                dims = ['x', 'y', 'scenedatetime'],
                name = self.name,
                coords= { 'scenedatetime': self.scenes_dates },
                attrs = { 'filenames': self.filenames })
