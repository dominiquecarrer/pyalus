#!/bin/bash
set -e
# Any subsequent(*) commands which fail will cause the shell script to exit immediately
#
# This test show how to run the wrapper for the first time step, with startseries = True) and for the second (and other) time steps (when startseries = False)

# It will run only on one point to be fast, this test can be used in automatic testing during development : when you modify the code, it can detect basic coding error.
# Moreover the debug setup are enabled to the maximum of verbosity and the output is redirected in log files for debuging and inspection.

# cd to the script's directory
cd "$(dirname "$0")"

export site=${1:-Avignon}

echo "testing c3s albedo for $site, using f90 namelist as input"

mkdir -p log/$site

echo "python3 ../.././pyal2/wrapper.py ../config/acf.c3s.avhrr_for_test.yaml ../config/pcf.c3s.avhrr.yaml  --keywords name testname site $site year '2001' --loglevel info --instruments AVHRR_NOAA16 --outputdates 2001-12-01,2001-12-31 1>log/$site/log.16 2>log/$site/logerr.16"
python3 ../.././pyal2/wrapper.py ../config/acf.c3s.avhrr_for_test.yaml ./pcf.c3s.avhrr.yaml  --keywords name testname site $site year '2001' --loglevel info --instruments AVHRR_NOAA16 --outputdates 2001-12-01,2001-12-31 1>log/$site/log.16 2>log/$site/logerr.16

echo "testing c3s TOC-R on long period and region for $site"

for brdf in $(ls output-testname/$site/*/*/c_c3s_brdf_*_$site_*.nc)
do
    output=$(echo -n "$brdf" | sed -e 's:_brdf_:_tocr_:g')
    python3 ../../pyal2/wrapper_toc_r.py  -i $brdf -o $output 1>>log/$site/log.16 2>>log/$site/logerr.16
done

echo "Tests passed with success"
