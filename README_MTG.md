
# pyal2 

author: florian.pinault@meteo.fr & mickael.parde@meteo.fr
date first version : 27th of june 2019
date version MTG : 24th of july 2020

This python 3 package applies brdf kernels models on TOC reflectance data (generates a brdf model output) 
and applies angular and spectral integration (generates an albedos output).

## *Introduction*

This readme aims in describing breafly the new process of the algorithm computing
surface albedo and brdf for mtg FCI sensor.
This version is a first version that will proceed only 3 channels. No scientific
validation have been done and future evolutions should be performed.

Please inform M.Pardé (mickael.parde@meteo.fr) if bugs or strange behaviour are
found.

## *Installation*


A part of the code is written in fortran. This part should be compiled before starting.
> cd pyal2
> make all

This part is tested in meteo-france on a Mageia linux core. 

## *Installation*
### *Requirements*
* numpy==1.13.3
* f90nml==0.21 
* coloredlogs==7.0
* h5py==2.7.1 
* netCDF4==1.3.1 
* tblib==1.3.2 
* pyyaml==3.13 
* xarray==0.11.0

## *Basic utilisation*


The launch of the process is done using a script. One exemple of the kind of script is given in file script/wrapper.sh.
The script should be launched this way:

```
$ script/wrapper.sh ./config/pcf.mtg_apid.yaml
```

In this script several steps are going through :

* first a convertion of the apid format pcf file is performed to get a pcf file in pyal2 format

```
$ python ../pyal2/convert_utils/convert_pcf_format.py
                    --apid2pyal2 
                    -l info 
                    -a ../config/pcf.mtg_apid.yaml
                    -p ./config/pcf.lsasaf.mtg.yaml 
                    --empty_file ../pyal2/convert_utils/pcf.mtg.generic.yaml
```


where --apid2pyal2 states that we want to convert a apid formated pcf file in a pyal2 format
      -a is the name of the apid formated file
      -p is the pyal2 formated file
      --empty_file is the name of the generic pyal2 file 
      -l is the level of verbose we want : info, warning, debug?

* The function then launched is a python3 script:

```
$ python3 ../pyal2/wrapper.py 

        ./config/acf.mtg.startserie.true.yaml
        ./config/pcf.lsasaf.mtg.yaml 
        -l info 
        --keywords name run-mtg
        --instruments MTG
        --outputdates date_start,date_end 1>log/log.1  2>log/logerr.1
```


Where :
* wrapper.py is the program master.
* acf.c3s.mtg.yaml is the algorithm configuration file.
* pcf.c3s.mtg.yaml is the global configuration file
* -l : is a option that define at wich level will be the logging mode. ERROR, WARNING or INFO ?
* --keywords : is a liste of keys:values that will replace in the pcf file the {key} by the values
* --instruments : Liste of instruments that will be processed
* --outputdates : liste of startdates,enddates associated to each instruments

The chosen date is the one writen in pcf file with the name **image_reference_time**

## *Managing Parameter configuration file*

In this file written in yaml format we access to the definition of:

  **`MODE`**
defines the processing to be performed.
- 1 : This is the first run
- 2 : This is the second run using spin-off (used only for reprocessing)

  **`LOG_LEVEL`**:
used to manage code verbosity in python and fortran codes. Valid values are the levels of the python logging library ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", 
see https://docs.python.org/2/library/logging.html#logging-levels). Fortran code (scientific core) logging is only activated when LOG_LEVEL="DEBUG".

 **`ROI/region_name`**: text identifying the area processed; used for output files attributes.
 
 **image_reference_time**: date we will process the MTDAL product
 
 **satellite**: Satellite name
 
### Dynamic

    **`VAA`**: *CURRENT(t)*  actually the %Y%m%d will be replaced by Year Month and Day values
    **`VZA`**: *CURRENT(t)*  actually the %Y%m%d will be replaced by Year Month and Day values
    **`SAA`**: *CURRENT(t)*  actually the %Y%m%d will be replaced by Year Month and Day values
    **`SZA`**: *CURRENT(t)*  actually the %Y%m%d will be replaced by Year Month and Day values
    **`TOC_REFLECTANCE_BAND1`**: *CURRENT(t)*
    **`TOC_REFLECTANCE_BAND2`**: *CURRENT(t)*
    **`TOC_REFLECTANCE_BAND3`**: *CURRENT(t)*
    **`TOC_REFLECTANCE_COV_BAND1`**: *CURRENT(t)*
    **`TOC_REFLECTANCE_COV_BAND2`**: *CURRENT(t)*`
    **`TOC_REFLECTANCE_COV_BAND3`**: *CURRENT(t)*
    **`INPUTCHECKPOINT_BAND1`**:*CURRENT(t-1day)*  the brdf used as input is the previous brdf (%Y%m%d minus one day)
    **`INPUTCHECKPOINT_BAND2`**:*CURRENT(t-1day)*  the brdf used as input is the previous brdf (%Y%m%d minus one day)
    **`INPUTCHECKPOINT_BAND3`**:*CURRENT(t-1day)*  the brdf used as input is the previous brdf (%Y%m%d minus one day)
    **`INPUTCHECKPOINT_BAND1_COV`**:*CURRENT(t-1day)*
    **`INPUTCHECKPOINT_BAND2_COV`**:*CURRENT(t-1day)*
    **`INPUTCHECKPOINT_BAND3_COV`**:*CURRENT(t-1day)* 
    **`LWCS_MASK`**: *CURRENT(t)* 

### static

    LAT: *STATIC* the same file should be writen the same number of time than the toc reflectances
    LON: *STATIC*
    
    

- input data directory : key = filenames
    Warning, all the toc files should be present in the place defined here !!!
- output data directory : key = output,albedo and brdf
- definition of climatological albedo : key = brdf_clim, filename
    Warning, all the brdf should be present in the place defined here !!!
- brdf path that will be used in the Kalman process : key = output,brdf

## *Outputs*

- NC_LSASAF_MTG_ALBEDO_MTG-Disk_20200305.nc            
- NC_LSASAF_MTG_AL-C1-CK-D01_MTG-Disk_20200305.nc      
- NC_LSASAF_MTG_AL-C1-CK_MTG-Disk_20200305.nc          
- NC_LSASAF_MTG_AL-C1-K012-D01_MTG-Disk_20200305.nc    
- NC_LSASAF_MTG_AL-C1-K012_MTG-Disk_20200305.nc        
- NC_LSASAF_MTG_AL-C1_MTG-Disk_20200305.nc           
- NC_LSASAF_MTG_AL-C2-CK-D01_MTG-Disk_20200305.nc  
- NC_LSASAF_MTG_AL-C2-CK_MTG-Disk_20200305.nc      
- NC_LSASAF_MTG_AL-C2-K012-D01_MTG-Disk_20200305.nc
- NC_LSASAF_MTG_AL-C2-K012_MTG-Disk_20200305.nc    
- NC_LSASAF_MTG_AL-C2_MTG-Disk_20200305.nc         
- NC_LSASAF_MTG_AL-C3-CK-D01_MTG-Disk_20200305.nc 
- NC_LSASAF_MTG_AL-C3-CK_MTG-Disk_20200305.nc
- NC_LSASAF_MTG_AL-C3-K012-D01_MTG-Disk_20200305.nc
- NC_LSASAF_MTG_AL-C3-K012_MTG-Disk_20200305.nc
- NC_LSASAF_MTG_AL-C3_MTG-Disk_20200305.nc

where :
- ALBEDO_MTG : Broadband albedo
- AL-C1-CK-D01 : Channel 1 BRDF CK values Day one (no Kalman filter)
- AL-C1-CK : Channel 1 BRDF CK values  ( Kalman filter)
- AL-C1-K012-D01 : Channel 1 BRDF K0,1,2 values Day one (no Kalman filter)
- AL-C1-K012 : Channel 1 BRDF K0,1,2 values (Kalman filter)
- AL-C1 : Spectral albedo (BH and DH)

C2 and C3 are for channel 2 and 3.






