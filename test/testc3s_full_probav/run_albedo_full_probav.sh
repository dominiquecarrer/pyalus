#!/bin/bash
set -e
# Any subsequent(*) commands which fail will cause the shell script to exit immediately
#
# This test show how to run the wrapper for the first time step, with startseries = True) and for the second (and other) time steps (when startseries = False)

# It will run only on one point to be fast, this test can be used in automatic testing during development : when you modify the code, it can detect basic coding error.
# Moreover the debug setup are enabled to the maximum of verbosity and the output is redirected in log files for debuging and inspection.

# cd to the script's directory
cd "$(dirname "$0")"

export site=${1:-X28Y05}

echo "testing c3s albedo on one chunck for $site, using yaml file as input"

mkdir -p log
echo "python3 ../../pyal2/wrapper.py acf.c3s.full_probav.yaml pcf.c3s.full_probav.yaml --keywords name test sensorstringinfilenames PROBAV sensor PROBAV site $site  -i PROBAV -l info --outputdates 2015-02-05,2015-03-08"
python3 ../../pyal2/wrapper.py acf.c3s.full_probav.yaml pcf.c3s.full_probav.yaml --keywords name test sensorname PROBAV sensor PROBAV site $site -i PROBAV -l info --outputdates 2015-02-05,2015-03-08 1>log/log.1  2>log/logerr.1

echo "----------------------------- FIN OK -------------------------------" 
