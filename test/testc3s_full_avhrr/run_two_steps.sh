#!/bin/bash
set -x
set -e
# Any subsequent(*) commands which fail will cause the shell script to exit immediately
#
# This test show how to run the wrapper for the first time step, with startseries = True) and for the second (and other) time steps (when startseries = False)

# This script show be run from pyal2/test/sometestname

# cd to the script's directory
cd "$(dirname "$0")"


echo "testing c3s ALBEDO for two dates for one site"

../../pyal2/wrapper.py acf.c3s.AVHRR_NOAA7.true pcf.c3s.genericsite.2bands.AVHRR_NOAA7.1981-09-20 -f f90nml_c3s -s  c3s -l debug --keywords sensor AVRHH_NOAA7 name testname -d 1000 -y 32 36 -x 35 40 --keywords sensor AVRHH_NOAA7 name testname 1>log.1981-09-20  2>logerr.1981-09-20
../../pyal2/wrapper.py acf.c3s.AVHRR_NOAA7.false pcf.c3s.genericsite.2bands.AVHRR_NOAA7.1981-09-30 -f f90nml_c3s -s c3s -l debug --keywords sensor AVRHH_NOAA7 name testname -d 1000 -y 32 36 -x 35 40 --keywords sensor AVRHH_NOAA7 name testname 1>log.1981-09-30  2>logerr.1981-09-30


#echo "testing c3s TOC-R for $site $sensorname"
#for brdf in $(ls output-testname$testname/$site/*/*/c_c3s_brdf_*_GLOBE_*$sensorname*_V1.0.nc)
#do
#    output=$(echo -n "$brdf" | sed -e 's:_brdf_:_tocr_:g')
#    python3 ../../pyal2/wrapper_toc_r.py  -i $brdf -o $output 1>>log/$site/log.$sensorname.tocr 2>>log/$site/logerr.$sensorname.tocr
#done


