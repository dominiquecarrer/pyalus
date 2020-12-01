#!/usr/bin/env python

import numpy as np
import os
import sys
import math

try:
    import coloredlogs, logging
except ImportError:
    import logging

from pyal2.lib.brdfwrapper import brdfwrapper as kernels
import xarray as xr

#model_id = runner.configuration.model_id, n_channels = runner.configuration.n_channels, azimuth_sat = runner.azimuth_sat.values, azimuth_sol = runner.azimuth_sol.values, zenith_sol = runner.zenith_sol.values, zenith_sat = runner.zenith_sat.values, brdf = runner.brdf, scenes_dates = runner.scenes_dates

def apply_brdf_model(brdf, model_id, inputdata, index_coord = 'scenedatetime', scale_percent=100, x=0, y=0):
    """ Compute reflectance using the angles and brdf model and brdf values for the point x,y.
    Multiply it by 100. to have value easier to compare to what is in runner.reflectance.values.
    Compute also phi_del. Input must be in degree."""
    if len(inputdata.dims) > 2:
        print(f'Selecting only x={x} and y={y} in brdf computation')
        inputdata = inputdata.sel(x=x,y=x)
    model_len = brdf.shape[3]
    param_coord = [ 'k' + str(i) for i in range(0, model_len)]
    idcoord = inputdata.coords[index_coord]
    band_coord = inputdata.coords['band']

    f0f1f2mat = np.full((model_len, len(idcoord)), np.nan)
    refl = np.full((len(band_coord), len(idcoord)), np.nan)

    for idate, index in enumerate(inputdata[index_coord]):
        azimuth_sol=float(inputdata.sel(**{index_coord:index})['azimuth_sol'].values)
        azimuth_sat=float(inputdata.sel(**{index_coord:index})['azimuth_sat'].values)
        zenith_sat=float(inputdata.sel(**{index_coord:index})['zenith_sat'].values)
        zenith_sol=float(inputdata.sel(**{index_coord:index})['zenith_sol'].values)

        if azimuth_sat > 360.: azimuth_sat = 360.
        if azimuth_sol > 360.: azimuth_sol = 360.
        azimuth_del = azimuth_sat - azimuth_sol
        if azimuth_del < 0.: azimuth_del += 360.

        theta_obs = zenith_sat / 180 * math.pi
        theta_sun = zenith_sol / 180 * math.pi
        phi_del = azimuth_del / 180 * math.pi
        f0f1f2 = kernels(debuglevel=1,
                     theta_obs=theta_obs,
                     phi_del=phi_del,
                     theta_sun=theta_sun,
                     model=model_id)[0]

        f0f1f2mat[:,idate] = f0f1f2

        for iband, band in enumerate(inputdata['band']):
            k0k1k2 = brdf[0,0,iband,:]
            #if iband == 0: print(f'theta_obs={theta_obs},phi_del={phi_del},theta_sun={theta_sun}',iband,idate, k0k1k2,f0f1f2,np.dot(k0k1k2, f0f1f2))
            refl[iband, idate] = np.dot(k0k1k2, f0f1f2)

    refl = refl * scale_percent

    f0f1f2_xr =  xr.DataArray(f0f1f2mat,
             dims = ['param', index_coord],
             name = 'reflectance_model',
             coords={index_coord: idcoord, 'param': param_coord})
    refl_xr = xr.DataArray(refl,
             dims = ['band', index_coord],
             name = 'reflectance_model',
             coords={'band': band_coord, index_coord: idcoord})
    outds = xr.Dataset({ 'reflectance_model' : refl_xr,
                        'f0f1f2': f0f1f2_xr})
    return outds


def apply_brdf_model2(brdf, azimuth_sat, azimuth_sol, zenith_sat, zenith_sol, scenes_dates, n_channels, model_id, scale_percent=100., x=0, y=0):
    """ Compute reflectance using the angles and brdf model and brdf values for the point x,y.
    Multiply it by 100. to have value easier to compare to what is in runner.reflectance.values.
    Compute also phi_del"""
    reflectance_model = np.full((azimuth_sol.values.shape[0],azimuth_sol.values.shape[1],n_channels,azimuth_sol.values.shape[2]), np.nan)

    azimuth_sat.values[azimuth_sat.values > 360.] = 360.
    azimuth_sol.values[azimuth_sol.values > 360.] = 360.
    azimuth_del = azimuth_sat.values[:,:,:] - azimuth_sol.values[:,:,:]
    azimuth_del[azimuth_del < 0.] += 360.
    for iscene, scene_date in enumerate(scenes_dates):
        theta_obs = zenith_sat.values[x,y,iscene] / 180 * math.pi
        phi_del = azimuth_del[x,y,iscene] / 180 * math.pi
        theta_sun = zenith_sol.values[x,y,iscene] / 180 * math.pi
        f0f1f2 = kernels(debuglevel=1,
                     theta_obs=theta_obs,
                     phi_del=phi_del,
                     theta_sun=theta_sun,
                     model=model_id)[0]
        for iband in range(0,n_channels):
            try:
                k0k1k2 = brdf.values[0,0,iband,:]
            except:
                k0k1k2 = brdf[0,0,iband,:]
            reflectance_model[x,y,iband,iscene] = np.dot(k0k1k2, f0f1f2)
    print(f'scale_percent {scale_percent}')
    return reflectance_model * scale_percent , azimuth_del

