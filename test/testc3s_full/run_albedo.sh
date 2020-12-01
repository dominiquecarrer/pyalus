#!/bin/bash

set -e
set -x
# Any subsequent(*) commands which fail will cause the shell script to exit immediately
#
# This test show how to run the wrapper for the first time step, with startseries = True) and for the second (and other) time steps (when startseries = False)
# This script show be run from pyal2/test/sometestname

cd "$(dirname "$0")"  # cd to the script's directory

export sensor=${1:-'AVHRR_NOAA11'}
export site=${2:-'Avignon'}
export testname=${3:-'testname'}

echo "Testing c3s ALBEDO for $sensor on $site"

export LOGDIR=./log/$site/$sensor
mkdir -p $LOGDIR

python3 ../../pyal2/wrapper.py config/acf.c3s.multi-sensor.true.yaml config/pcf.c3s.$sensor.yaml -l debug --keywords name $testname-spinoff site $site sensorname $sensor year '*' --instruments $sensor --outputdates fromsensor-spinoff:$sensor --startserie True 1>$LOGDIR/log.1.spinoff  2>$LOGDIR/logerr.1.spinoff

echo "----------------------------- Finished spin-off period for $sensor on $site"

../../scripts/netcdf_set_attribute.py --inputfile output-$testname-spinoff/$site/'%Y/%m/c_c3s_brdf_%Y%m%d000000'_${site}_${sensor}_V1.0.nc --outputfile output-$testname/$site/'%Y/%m/c_c3s_brdf_%Y%m%d000000'_${site}_${sensor}_V1.0.nc --newdate fromsensorname_start_date:$sensor  1>>$LOGDIR/log.2.set_brdf 2>>$LOGDIR/logerr.2.set_brdf
echo "-----------------------------Copy BRDF OK -------------------------------"


python3 ../../pyal2/wrapper.py config/acf.c3s.multi-sensor.true.yaml config/pcf.c3s.$sensor.yaml -l debug --keywords name $testname site $site sensorname $sensor year '*' --instruments $sensor --outputdates fromsensor:$sensor --startserie False 1>$LOGDIR/log.3.nospinoff  2>$LOGDIR/logerr.3.nospinoff

echo "----------------------------- END of $sensor on $site OK -------------------------------" 
