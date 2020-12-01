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

export site=${1:-Avignon}

echo "testing c3s albedo on one point for $site, using f90 namelist as input"

mkdir -p log

python3 ../../pyal2/wrapper.py acf.c3s.multi-sensor.true.for_test.yaml pcf.c3s.multi-sensor.for_test.yaml  -i VGT --keywords name testname-spinoff sensorname VGT  site $site --instrument VGT --loglevel debug -x 1 1 -y 1 1 --outputdates 2002-06-20,2002-07-21  --startserie True 1>log/log.1  2>log/logerr.1

python3 ../../pyal2/wrapper.py acf.c3s.multi-sensor.false.for_test.yaml pcf.c3s.multi-sensor.for_test.yaml  -i VGT --keywords name testname sensorname VGT site $site --instrument VGT --loglevel debug -x 1 1 -y 1 1 --debuglevel 10000 --outputdates 2002-07-20,2002-08-20 --startserie False  1>log/log.2  2>log/logerr.2


echo "testing c3s tocr on one point"
python3 ../../pyal2/wrapper_toc_r.py  -i output-data/$site/2002/07/c_c3s_brdf_20020720000000_Avignon_VGT_V1.0.nc -o output-data/$site/2002/07/c_c3s_tocr_20020720000000_Avignon_VGT_V1.0.nc  1>>log/log.1 2>>log/logerr.1
python3 ../../pyal2/wrapper_toc_r.py  -i output-data/$site/2002/07/c_c3s_brdf_20020731000000_Avignon_VGT_V1.0.nc -o output-data/$site/2002/07/c_c3s_tocr_20020731000000_Avignon_VGT_V1.0.nc 1>>log/log.2 2>>log/logerr.2

echo "Test passed with success"
#python3 ../../pyal2/validation/check_tests_c3s.py --old test-data/c3s/output-ref-v0.13.5-model3/test/testc3s/output-full/$site/2002/09/c_c3s_brdf_20020920000000_GLOBE_VGT_V1.0.nc --new output-testname/$site/2002/09/c_c3s_brdf_20020920000000_GLOBE_VGT_V1.0.nc --type brdf
