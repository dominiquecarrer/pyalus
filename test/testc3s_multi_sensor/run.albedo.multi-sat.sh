#!/bin/bash


set -e
# Any subsequent(*) commands which fail will cause the shell script to exit immediately
#
# This test show how to run the wrapper for the first time step, with startseries = True) and for the second (and other) time steps (when startseries = False)

# This script show be run from pyal2/test/sometestname

# cd to the script's directory
cd "$(dirname "$0")"

export site='Avignon'

echo "testing c3s ALBEDO for two dates for one site"

mkdir -p ./log


echo "python3 ../../pyal2/wrapper.py ./acf.c3s.multi-sensor.true.yaml ./pcf.c3s.multi-sensor.yaml -l debug --keywords name run-climato-clim site $site --instruments PROBAV AVHRR_NOAA11 --outputdates 2015-01-01,2015-02-01 1988-11-01,1988-12-30"
python3 ../../pyal2/wrapper.py ./acf.c3s.multi-sensor.true.yaml ./pcf.c3s.multi-sensor.yaml -l debug --keywords name run-climato-clim site $site --instruments PROBAV AVHRR_NOAA11 --outputdates 2015-01-01 1988-11-01,1988-12-30 1>log/log.1  2>log/logerr.1

echo "----------------------------- End ok before spin off $site start true -------------------------------" 

../../scripts/netcdf_set_attribute.py --inputfile output-data/$site/2015/01/c_c3s_brdf_20150131000000_${site}_PROBAV_V1.0.nc --outputfile output-data/$site/2014/12/c_c3s_brdf_20141231000000_${site}_PROBAV_V1.0.nc --newdate :-1Y  1>>log/log.1  2>>log/logerr.1
echo "-----------------------------Copy BRDF PROBAV OK -------------------------------" 
../../scripts/netcdf_set_attribute.py --inputfile output-data/$site/1988/12/c_c3s_brdf_19881220000000_${site}_AVHRR_NOAA11_V1.0.nc --outputfile output-data/$site/1988/11/c_c3s_brdf_19881120000000_${site}_AVHRR_NOAA11_V1.0.nc --newdate :-1Y  1>>log/log.1  2>>log/logerr.1
echo "-----------------------------Copy BRDF AVHRR11 OK -------------------------------" 
echo " Warning The spin off constructed in the test folder are wrong, usually the same \
        decade of the next year should be used"

python3 ../../pyal2/wrapper.py ./acf.c3s.multi-sensor.false.yaml ./pcf.c3s.multi-sensor.yaml -l info --keywords name run-climato-clim site $site --instruments PROBAV AVHRR_NOAA11 --outputdates 2015-01-01 1988-11-01,1988-12-30 1>>log/log.1  2>>log/logerr.1

echo "----------------------------- END OK -------------------------------" 
