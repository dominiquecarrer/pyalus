#!/bin/bash
set -x
set -e
# Any subsequent(*) commands which fail will cause the shell script to exit immediately
#
# This test show how to run the wrapper for the first time step, with startseries = True) and for the second (and other) time steps (when startseries = False)

# This script show be run from pyal2/test/sometestname

# cd to the script's directory
cd "$(dirname "$0")"

export site='Avignon'
dd=`date -d now +'%s%N'`

echo "testing c3s ALBEDO for two dates for one site"

tmp=`grep TMP_FOLDER $1| cut -f2 -d:| sed "s/^\( \)*\(.*\)/\2/"`
mkdir -p $tmp

echo "change ipma pcf file to pyal2 format "
python ../pyal2/convert_utils/convert_pcf_format.py --apid2pyal2 -l info -a $1 -p $tmp/pcf.lsasaf.mtg.$dd.yaml --empty_file ../pyal2/convert_utils/pcf.mtg.generic.yaml

echo "convertion is ok" 
echo " " 

# extraction of the ACF file name
nb=`grep -n "STATIC_CONFIG_PYTHON" $1  | cut -f1 -d:`
let nb=nb+1;
global_acf_file_name=`head -$nb $1 | tail -1 | cut -d\" -f2`

# extraction of mode
year=`grep image_reference_time $1| cut -f2 -d:|cut -f1 -d\-| sed "s/^\( \)*\(.*\)/\2/"`
month=`grep image_reference_time $1| cut -f2 -d:|cut -f2 -d\-`
day=`grep image_reference_time $1| cut -f2 -d:|cut -f3 -d\-|cut -f1 -d\ `

# run pyal2
python3 ../pyal2/wrapper.py $global_acf_file_name $tmp/pcf.lsasaf.mtg.$dd.yaml -l info --keywords name run-mtg --instruments MTG --outputdates "$year-$month-$day","$year-$month-$day"

echo "----------------------------- End ok before spin off $site start true -------------------------------" 
