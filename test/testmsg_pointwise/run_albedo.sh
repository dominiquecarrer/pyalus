#!/bin/bash
set -e
# Any subsequent(*) commands which fail will cause the shell script to exit immediately
#
# This test show how to run the wrapper for the first time step, with startseries = True) and for the second (and other) time steps (when startseries = False)

# It will run only on one point to be fast, this test can be used in automatic testing during development : when you modify the code, it can detect basic coding error.
# Moreover the debug setup are enabled to the maximum of verbosity and the output is redirected in log files for debuging and inspection.

# cd to the script's directory
cd "$(dirname "$0")"

echo "testing msg albedo on one point"

mkdir -p log

python3 ../../pyal2/wrapper.py acf.msg.model0.startserie.true.yaml pcf.msg.2016-08-01.yaml -i MSG -f yaml --outputdates 2016-08-01 --keywords name onepoint --loglevel debug -x 1500 1500 -y 1500 1500 --debuglevel 10000 1>log/log.1  2>log/logerr.1
python3 ../../pyal2/wrapper.py acf.msg.model0.startserie.false.yaml pcf.msg.2016-08-02.yaml -i MSG -f yaml --outputdates 2016-08-02 --keywords name onepoint --loglevel debug -x 1500 1500 -y 1500 1500 --debuglevel 10000 1>log/log.2  2>log/logerr.2

echo "checking output value at  -x 1500 1500 -y 1500 1500"
echo "python3 ../../pyal2/validation/check_tests_msg.py --old ./valid-data --new output -x 1500 1500 -y 1500 1500 --date 20160801"
python3 ../../pyal2/validation/check_tests_msg.py --old ./reference-data --new output-onepoint -x 1500 1500 -y 1500 1500 --date 20160801

echo "python3 ../../pyal2/validation/check_tests_msg.py --old ./valid-data --new output -x 1500 1500 -y 1500 1500 --date 20160802"
python3 ../../pyal2/validation/check_tests_msg.py --old ./reference-data --new output-onepoint -x 1500 1500 -y 1500 1500 --date 20160802
