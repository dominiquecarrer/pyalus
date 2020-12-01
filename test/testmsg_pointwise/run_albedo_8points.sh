#!/bin/bash
set -e
# Any subsequent(*) commands which fail will cause the shell script to exit immediately
#
# This test show how to run the wrapper for the first time step, with startseries = True) and for the second (and other) time steps (when startseries = False)

# It will run only on one point to be fast, this test can be used in automatic testing during development : when you modify the code, it can detect basic coding error.
# Moreover the debug setup are enabled to the maximum of verbosity and the output is redirected in log files for debuging and inspection.

# cd to the script's directory
cd "$(dirname "$0")"

echo "testing msg albedo on eight points"

mkdir -p log

xList=([1]="1500" [2]="808"  [3]="524"  [4]="352"  [5]="1952" [6]="2624" [7]="104")
yList=([1]="1500" [2]="2092" [3]="1656" [4]="2528" [5]="3080" [6]="3152" [7]="1464") 

for i in "${!xList[@]}"; do

  python3 ../../pyal2/wrapper.py acf.msg.model0.startserie.true.yaml pcf.msg.2016-08-01.yaml -i MSG -f yaml --outputdates 2016-08-01 --keywords name point${i} --loglevel debug -x ${xList[i]} ${xList[i]} -y ${yList[i]} ${yList[i]} --debuglevel 10000 1>log/log.1.${i}  2>log/logerr.1.${i}
  python3 ../../pyal2/wrapper.py acf.msg.model0.startserie.false.yaml pcf.msg.2016-08-02.yaml -i MSG -f yaml --outputdates 2016-08-02 --keywords name point${i} --loglevel debug -x ${xList[i]} ${xList[i]} -y ${yList[i]} ${yList[i]} --debuglevel 10000 1>log/log.2.${i}  2>log/logerr.2.${i}

  echo '      ' 1>log/log.diff  2>log/logerr.diff
  echo '      ' 1>>log/log.diff  2>>log/logerr.diff
  echo "checking output value at -x ${xList[i]} ${xList[i]} -y ${yList[i]} ${yList[i]}" 1>>log/log.diff  2>>log/logerr.diff
  echo "python3 ../../pyal2/validation/check_tests_msg.py --old ./valid-data --new output-point${i} -x ${xList[i]} ${xList[i]} -y ${yList[i]} ${yList[i]}  --date 20160801" 1>>log/log.diff  2>>log/logerr.diff
  python3 ../../pyal2/validation/check_tests_msg.py --old ./reference-data --new output-point${i} -x ${xList[i]} ${xList[i]} -y ${yList[i]} ${yList[i]} --date 20160801 1>>log/log.diff  2>>log/logerr.diff

  echo "python3 ../../pyal2/validation/check_tests_msg.py --old ./valid-data --new output-point${i} -x ${xList[i]} ${xList[i]} -y ${yList[i]} ${yList[i]} --date 20160802" 1>>log/log.diff  2>>log/logerr.diff
  python3 ../../pyal2/validation/check_tests_msg.py --old ./reference-data --new output-point${i} -x ${xList[i]} ${xList[i]} -y ${yList[i]} ${yList[i]} --date 20160802 1>>log/log.diff  2>>log/logerr.diff

done

