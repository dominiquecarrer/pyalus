
#########################################################################################
######################## README Pyal2 multi-sensor version ##############################
#########################################################################################
author: florian.pinault@meteo.fr & mickael.parde@meteo.fr
date first version : 27th of june 2019
This python 3 package applies brdf kernels models on TOC reflectance data (generates a brdf model output) 
and applies angular and spectral integration (generates an albedos output).

>>>>>>****** Introduction ******<<<<<<<


This readme aims in describing breafly the new process of the algorithm computing
surface albedo and brdf.
This python 3 package applies brdf kernels models on TOC reflectance data 
(generates a brdf model output) and applies angular and spectral integration (generates an albedos output).
This 2.0 version distributed to VITO in july 2019 is preliminary. The algorithm
is slightly changed since first version and all combinations have not been tested.
Please inform M.Pardé (mickael.parde@meteo.fr) if bugs or strange behaviour are
found.

>>>>>>****** Installation ******<<<<<<<

pip install mydirectory/pyal2
Note : numpy must be installed (error message will be raised).

A part of the code is written in fortran. This part should be compiled before starting.
> cd pyal2
> make all

This part is tested in meteo-france on a Mageia linux core. The previous version was 
already used at Vito and no major modification where added to the programs. 
We suppose then that No problem sould be encountered.

>>>>>>******  Basic utilisation ******<<<<<<<


The launch of the process is done using a script. One exemple of the kind of script
is given in file run.multi-sat.brdf.spinoff.sh.

In this script several steps are going through :
- A first launch for the estimation of a BRDF corresponding to the first year with first
data.
- A copy of the last BRDF estimation at the end of the first year.
- A second launch of the algorithm with the previous BRDF as first guess.

The function launch is a python3 script:

python3 ../pyal2/wrapper.py 
        ./config/acf.c3s.multi-sensor.false.brdf.yaml 
        ./config/pcf.c3s.multi-sensor.yaml 
        -l info 
        --keywords name run-climato-clim site $site 
        --instruments PROBAV,AVHRR_NOAA11 
        --outputdates 2013-10-20,2018-10-01 1988-11-30,1994-09-20 1>log/log.1  2>log/logerr.1


Where 
* wrapper.py is the program master.
* acf.c3s.multi-sensor.false.brdf.yaml is the algorithm configuration file.
* pcf.c3s.multi-sensor.yaml is the global configuration file
* -l : is a option that define at wich level will be the logging mode. ERROR, WARNING or INFO ?
* --keywords : is a liste of keys:values that will replace in the pcf file the {key} by the values
* --instruments : Liste of instruments that will be processed
* --outputdates : liste of startdates,enddates associated to each instruments

instrument : firstdate  : enddate
AVHRR7     : 20-09-1981 : 31-12-1984
AVHRR9     : 20-03-1985 : 10-11-1988
AVHRR11    : 30-11-1988 : 20-09-1994
AVHRR14    : 10-02-1995 : 10-03-2001
AVHRR16    : 20-03-2001 : 10-05-2003
AVHRR17    : 20-09-2003 : 31-12-2005
VGT        : 01-04-1998 : 01-05-2014
PROBAV     : 20-10-2013 : 01-10-2018

This startdate and enddates are driving the way we proceed the spin-off. Last BRDF computed
the first year will be copied in a new netcdf file with a new name to start agains the same 
year.

Therefore : 
  'AVHRR_NOAA7'   : 'date_start': '20-09-1981', 'date_end_spinoff': '10-09-1982
  'AVHRR_NOAA9'  :  'date_start': '20-03-1985', 'date_end_spinoff': '10-03-1986
  'AVHRR_NOAA11' :  'date_start': '20-11-1988', 'date_end_spinoff': '20-11-1989
  'AVHRR_NOAA14' :  'date_start': '10-02-1995', 'date_end_spinoff': '31-01-1996
  'AVHRR_NOAA16' :  'date_start': '20-03-2001', 'date_end_spinoff': '10-03-2002
  'AVHRR_NOAA17' :  'date_start': '20-09-2002', 'date_end_spinoff': '10-09-2003
where date_end_spinoff is the last date included and date_start is the date corresponding
to the first run. Then the new brdf file should be data_start minus 1 decade.
  
  In the script file another program is used: netcdf_set_attribute.py 
this script copy the last brdf file in another folder that will be used in
the following.

>>>>>>****** Managing Parameter configuration file  ******<<<<<<<

In this file written in yaml format we access to the definition of:

- input data directory : key = filenames
    Warning, all the toc files should be present in the place defined here !!!
- output data directory : key = output,albedo and brdf
- definition of climatological albedo : key = brdf_clim, filename
    Warning, all the brdf should be present in the place defined here !!!
- brdf path that will be used in the Kalman process : key = output,brdf


>>>>>>****** Running tests *************<<<<<<<<<

quick run
>makefile testonepoint

long run
>makefile test
