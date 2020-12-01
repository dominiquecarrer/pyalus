#!/bin/bash
set -e
set -x
# Any subsequent(*) commands which fail will cause the shell script to exit immediately
#
# This test show how to run the wrapper for the first time step, with startseries = True) and for the second (and other) time steps (when startseries = False)

# It will run only on one point to be fast, this test can be used in automatic testing during development : when you modify the code, it can detect basic coding error.
# Moreover the debug setup are enabled to the maximum of verbosity and the output is redirected in log files for debuging and inspection.

# cd to the script's directory
cd "$(dirname "$0")"

mkdir -p log

export site=${1:-Avignon}
echo "testing c3s albedo on one point for $site, using yaml file as input"
#echo python3 ../../pyal2/wrapper.py acf.c3s.vgt.test.yaml  pcf.c3s.vgt.test.yaml --keywords name test-deep sensorstringinfilenames VGT sensor VGT site $site -i VGT --outputdates 2002-01-01,2002-02-01
#python3 ../../pyal2/wrapper.py acf.c3s.vgt.test.yaml  pcf.c3s.vgt.test.yaml --keywords name test-deep sensorstringinfilenames VGT sensor VGT site $site -i VGT --outputdates 2002-01-01,2002-02-01 -l info 1>log/log.1  2>log/logerr.1

python3 ../../pyal2/wrapper.py acf.c3s.vgt.test.yaml pcf.c3s.vgt.test.yaml -l info --keywords name test-deep site $site sensorname VGT year '*' --instruments VGT --outputdates  2002-01-01,2002-02-01 --startserie True 1>log/log.1.spinoff  2>log/logerr.1.spinoff

echo "----------------------------- PyAl2 OK -------------------------------"

echo "validating c3s albedo on one point for $site by comparing with data generated at Meteo France"
python3 ../../pyal2/validation/check_tests_c3s_netcdf.py -ptest "output-test-deep/$site/2002/01/" -pvalid "valid-data/"

echo "--------------------------Validation  OK -------------------------------"
