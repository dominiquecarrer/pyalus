#!/bin/bash
set -e
# Any subsequent(*) commands which fail will cause the shell script to exit immediately
#
# This test show how to run the wrapper for the first time step, with startseries = True) and for the second (and other) time steps (when startseries = False)

# cd to the script's directory
cd "$(dirname "$0")"

echo "testing msg albedo on full disk, using f90 namelist as input"

mkdir -p log
#
python3 ../../pyal2/wrapper.py acf.msg.model0.startserie.true.yaml pcf.msg.2016-08-01.yaml -i MSG --config-format yaml --outputdates 2016-08-01 --keywords name full --loglevel info --chunksize 500 --cpu 3 1>log/log.1  2>log/logerr.1
echo "first step with startserie true ok"
python3 ../../pyal2/wrapper.py acf.msg.model0.startserie.false.yaml pcf.msg.2016-08-02.yaml -i MSG --config-format yaml --outputdates 2016-08-02 --keywords name full --loglevel info --chunksize 500 --cpu 3  1>log/log.2  2>log/logerr.2

echo "checking output value at  -x 1 3712 -y 1 3712"

python3 ../../pyal2/validation/check_tests_msg.py --old ./reference-data --new output -x 1 3712 -y 1 3712 --date 20160802

for filename in $(cd output; ls); do
    echo "Checking file $filename"
    echo 'not checking attributes  ARCHIVE_FACILITY NB_PARAMETERS SENSING_START_TIME NOMINAL_LONG PRODUCT_ALGORITHM_VERSION PRODUCT IMAGE_ACQUISITION_TIME PROCESSING_LEVEL NC OVERALL_QUALITY_FLAG FORECAST_STEP CFAC SENSING_END_TIME SATELLITE REGION_NAME COMPRESSION CLOUD_COVERAGE CENTRE FIELD_TYPE NL SUB_SATELLITE_POINT_END_LAT STATISTIC_TYPE PRODUCT_TYPE SAF ORBIT_TYPE GRANULE_TYPE DISPOSITION_FLAG PARENT_PRODUCT_NAME PRODUCT_ACTUAL_SIZE ASSOCIATED_QUALITY_INFORMATION PROJECTION_NAME INSTRUMENT_ID NOMINAL_PRODUCT_TIME END_ORBIT_NUMBER SUB_SATELLITE_POINT_END_LON LFAC START_ORBIT_NUMBER SUB_SATELLITE_POINT_START_LON PIXEL_SIZE PROCESSING_MODE SPECTRAL_CHANNEL_ID LOFF NOMINAL_LAT SUB_SATELLITE_POINT_START_LAT COFF TIME_RANGE INSTRUMENT_MODE'
    ../../pyal2/validation/h5dif test-data/msg/$filename output/$filename -p 0.0001  -l -i ARCHIVE_FACILITY NB_PARAMETERS SENSING_START_TIME NOMINAL_LONG PRODUCT_ALGORITHM_VERSION PRODUCT IMAGE_ACQUISITION_TIME PROCESSING_LEVEL NC OVERALL_QUALITY_FLAG FORECAST_STEP CFAC SENSING_END_TIME SATELLITE REGION_NAME COMPRESSION CLOUD_COVERAGE CENTRE FIELD_TYPE NL SUB_SATELLITE_POINT_END_LAT STATISTIC_TYPE PRODUCT_TYPE SAF ORBIT_TYPE GRANULE_TYPE DISPOSITION_FLAG PARENT_PRODUCT_NAME PRODUCT_ACTUAL_SIZE ASSOCIATED_QUALITY_INFORMATION PROJECTION_NAME INSTRUMENT_ID NOMINAL_PRODUCT_TIME END_ORBIT_NUMBER SUB_SATELLITE_POINT_END_LON LFAC START_ORBIT_NUMBER SUB_SATELLITE_POINT_START_LON PIXEL_SIZE PROCESSING_MODE SPECTRAL_CHANNEL_ID LOFF NOMINAL_LAT SUB_SATELLITE_POINT_START_LAT COFF TIME_RANGE INSTRUMENT_MODE
done
