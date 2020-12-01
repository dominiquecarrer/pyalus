#!/bin/bash
set -e
set -x
# Any subsequent(*) commands which fail will cause the shell script to exit immediately
#
# This test show how to run the wrapper for the first time step, with startseries = True) and for the second (and other) time steps (when startseries = False)

# cd to the script's directory
cd "$(dirname "$0")"

export site=${1:-Avignon}

echo "testing c3s ALBEDO on long period and region for $site, using f90 namelist as input"

mkdir -p log

python3 ../../pyal2/wrapper.py ./config/acf.c3s.multi-sensor.false.yaml pcf.c3s.multi-sensor.yaml --keywords name testname site $site --loglevel info --instruments VGT --outputdates 2002-05-20,2002-10-01 --startserie True 1>log/log  2>log/logerr

echo "testing c3s TOC-R on long period and region for $site"

for brdf in $(ls output-testname/$site/*/*/c_c3s_brdf_*_Avignon_VGT_V1.0.nc)
do
    output=$(echo -n "$brdf" | sed -e 's:_brdf_:_tocr_:g')
    python3 ../../pyal2/wrapper_toc_r.py  -i $brdf -o $output 1>>log/log 2>>log/logerr
done



################
# CHECK VALUES
################
echo python3 ../../pyal2/validation/check_tests_c3s_netcdf.py -pvalid -pvalid valid-data/output-testname/Avignon/2002/09/ -ptest output-testname/Avignon/2002/09/
python3 ../../pyal2/validation/check_tests_c3s_netcdf.py -pvalid valid-data/output-testname/Avignon/2002/09/ -ptest output-testname/Avignon/2002/09/ 

echo "Test finished with success !"

