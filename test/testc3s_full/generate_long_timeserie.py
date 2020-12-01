#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 14:56:55 2019

@author: pinaultf
"""

import sys
#sys.path = ['/cnrm/vegeo/pinaultf/experiments/NO_SAVE/c3s-exp14-big-run/pyal2/'] + sys.path 

import my
import my.io

sys.path = ['/home/pinaultf/mycodes/pyal2/'] + sys.path 
import coloredlogs
coloredlogs.install(level='ERROR')
import tqdm
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
print(sys.path)

import pyal2
import pyal2.validation

import pyal2.validation.visu as visu
import importlib;importlib.reload(visu);

all_avhrr = [f'AVHRR_NOAA{i}' for i in [7,9,11,14,16,17]]
#all_avhrr = [f'AVHRR_NOAA{i}' for i in [7,9,11,14,17]]
all_sensors = all_avhrr + ['VGT'] + ['PROBAV']
#all_sensors = all_avhrr +  ['PROBAV']
sensorcols = ['blue','darkblue','blue','darkblue','blue','darkblue','blue','darkblue','blue','darkblue','blue','darkblue','blue','darkblue',]
sensorcols2 = ['red','darkred','red','darkred','red','darkred','red','darkred','red','darkred','red','darkred','red','darkred',]
sensorcols4 = ['red','darkblue','red','darkblue','red','darkblue','red','darkblue','red','darkblue','red','darkblue','red','darkblue',]
#sensorcols3 = ['goldenrod', 'darkorange','goldenrod', 'darkorange','goldenrod', 'darkorange','goldenrod', 'darkorange','goldenrod', 'darkorange',]
sensorcols3 = ['black', 'brown','black', 'grey','black', 'grey','black', 'grey','black', 'grey','black', 'grey','black', 'grey','black', 'grey']
markers = 'x+x+x+x+x+x+x+x+x+x+'
linestyle = ['-','--',':','-','--',':','-','--',':','-','--',':','-','--',':','-','--',':','-','--',':','-','--',':','-','--',':']


def removenan(d):
    return d.where(d > -2., np.nan)
def removenan_and_select(d):
    return removenan(d.isel(LAT=slice(20,30),LON=slice(20,30))).mean(dim=('LAT','LON'))
    #return removenan(d.isel(LAT=25,LON=25).squeeze())

def plot_one_site(sitename, keys):
    f, ax = plt.subplots(1,1)
    for sensorname in all_avhrr:
        nd = e.gather_pyal2(sitename, sensorname=sensorname, suffix='benchmark') 
        
        for key in keys:
            #nd[key].isel(datetime=slice(0,),LAT=25,LON=25).plot() #vmax=0.5,         
            nd[key].isel(LAT=25,LON=25).plot(ax = ax) #vmax=0.5,         
        plt.legend(keys)
    return f
   
    
#e = visu.Exp(input_pyal2="pyal2-{suffix}/test/testc3s_full/output-testname/{sitename}/*/*/c_c3s_al_*_{sitename}_{sensorname}_V1.0.nc" , year_of_interest='*')
#f = plot_one_site('Avignon', keys=['AL-B0-BH', 'AL-B2-BH', 'AL-B3-BH', 'AL-MIR-BH', 'AL-BH-BB'])     
        
#suffix='benchmark-nosnow'
suffix='benchmark-bis'
sitename = 'Avignon'

#key =  'AL-BH-BB' #'AL-B0-BH' #'NMOD'
#key =  'AL-MIR-BH' 
#key =  'AL-B0-BH' 
#key =  'AL-B2-BH'
#key =  'NMOD'
#keys = ['AL-B0-BH', 'AL-B0-BH-ERR','AL-MIR-BH', 'AL-MIR-BH-ERR', 'AL-BH-BB', 'AL-BH-BB-ERR']# 'AL-B2-BH'] #, 'AL-B3-BH', 'AL-MIR-BH', 'AL-BH-BB']
#keys = ['AL-B0-BH','AL-B0-BH-ERR','AL-B0-BH','AL-B0-BH-ERR','AL-B0-BH','AL-B0-BH-ERR','AL-B0-BH','AL-B0-BH-ERR','AL-BH-BB','AL-BH-BB-ERR']
#keys = ['AL-B0-BH','AL-B0-BH-ERR'] #,'AL-BH-BB']
#keys = ['AL-BH-VI','AL-BH-VI-ERR','AL-BH-NI','AL-BH-NI-ERR'] #,'AL-BH-BB']
#keys = ['AL-B0-BH','AL-BH-BB']
keys = ['AL-B0-BH', 'AL-B2-BH', 'AL-B3-BH', 'AL-MIR-BH', 'AL-BH-BB']
#keys = [ 'AL-BH-BB']
#keys = ['AL-BH-BB','AL-BH-VI','AL-BH-NI'] #,  'AL-DH-BB']

f,axs=plt.subplots(len(keys)+1,1,sharex=True,figsize=(20,15))
plt.subplots_adjust(right=0.7)
#for isensor, sensorname in enumerate(all_avhrr):
for isensor, sensorname in enumerate(all_sensors):
    e = visu.Exp(input_pyal2=f'test/testc3s_full/output-testname/{sitename}/*/*/c_c3s_al_*_{sitename}_{sensorname}_V1.0.nc' , year_of_interest='*')

    nd = e.gather_pyal2(sitename, sensorname=sensorname, suffix=suffix) 
    #nd = e.gather_pyal2(sitename, sensorname=se, suffix='old-oldcoeffs')    
   # nd2 = e.gather_pyal2(sitename, sensorname=f'AVHRR_NOAA{avhrrnb}', suffix='old-newcoeffs')    
   # nd3 = e.gather_pyal2(sitename, sensorname=f'AVHRR_NOAA{avhrrnb}', suffix='old-newcoeffsnewspinup')        
    
    for key,ax in zip(keys,axs):                
        col = sensorcols4[isensor]
        mar = ' '# markers[isensor]        
        removenan_and_select(nd[key]).plot(label=f'{sensorname}',ax=ax, color=col, alpha=0.7, marker=mar) #,linewidth=2)      
        removenan_and_select(nd[key] + nd[key+'-ERR']).plot(label='_nolegend_',ax=ax, color=col,  linestyle='--',alpha=0.2)        
        removenan_and_select(nd[key] - nd[key+'-ERR']).plot(label='_nolegend_',ax=ax, color=col,  linestyle='--',alpha=0.2)
        
        col = sensorcols2[isensor]
        mar = ' '         
        #removenan_and_select(nd2[key]).plot(label=f'AVHRR {avhrrnb} n',ax=ax, color=col, linestyle='-', marker=mar,alpha=0.7)        
        #removenan_and_select(nd2[key] + nd2[key+'-ERR']).plot(label='_nolegend_',ax=ax, color=col,  linestyle='--',alpha=0.2)        
        #removenan_and_select(nd2[key] - nd2[key+'-ERR']).plot(label='_nolegend_',ax=ax, color=col,  linestyle='--',alpha=0.2)
        

        col = sensorcols3[isensor]
        mar = ' '
        #removenan_and_select(nd3[key]).plot(label=f'AVHRR {avhrrnb} n newspinup',ax=ax, color=col, linestyle='-', marker=mar,alpha=0.7)
        #removenan_and_select(nd3[key] + nd3[key+'-ERR']).plot(label='_nolegend_',ax=ax, color=col,  linestyle='-',alpha=0.2)
        #removenan_and_select(nd3[key] - nd3[key+'-ERR']).plot(label='_nolegend_',ax=ax, color=col,  linestyle='-',alpha=0.2)
        

        ax.set_ylim(top=0.4, bottom=0.)
        if ax == axs[0]:
            ax.legend(loc='center left')#, fancybox=True, shadow=True, ncol=1, bbox_to_anchor=(0.95, 0.5))
        ax.set_title(f'{sitename} {key}')
        
    col = sensorcols[isensor]
    ax = axs[-1]    
    for key in ['NMOD']:
        d = nd[key].isel(LAT=slice(20,30),LON=slice(20,30))
        d.mean(dim=('LAT','LON')).plot(label=f'{sensorname}',ax=ax, color=col)
    plt.ylim(top=30, bottom=-1)   
    plt.tight_layout()

my.io.ensure_dir(f'img/allts/{sitename}/{suffix}.jpg')
plt.savefig(f'img/allts/{sitename}/{suffix}.jpg')
