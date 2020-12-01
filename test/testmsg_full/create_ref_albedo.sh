#!/bin/bash
set -e
# Any subsequent(*) commands which fail will cause the shell script to exit immediately
#
# This creates reference data for the tests of running the wrapper for the first time step, with startseries = True) and for the second (and other) time steps (when startseries = False)

# target directory, for now hardcoded (move to config file at some point?)
refDir=/cnrm/vegeo/SAT/DATA/test-data/pyal2/output-ref-daniel

codeDir=$(dirname $0)
testDir=${codeDir##*/}
refTestDir="$refDir/$testDir"

gitHashFile=git-commit-hash

# check if there are modifications respective to last commit
nModFiles=$(git status -s -uno | wc -l)
if [[ $nModFiles > 0 ]]; then 
    echo "GIT-Commit changes before creating reference datasets"
    exit 1 
fi

if [[ ( "${HOSTNAME:0:5}" == lxvgo )  || ( "${HOSTNAME:0:5}" == sxvgo ) ]]; then

  # get git commit hash
	gitSha1=$(git rev-parse --verify HEAD)
  # get version number
  versionNumber=$(cat version)

	if [[  -d "$refTestDir" ]]; then

    if [[ ( ! -s "${refTestDir}/${gitHashFile}" ) || ( ! -s "${refTestDir}/version" ) ]]; then
      echo "Reference directory exists, but incomplete. Will backup and create new reference."
      thisDate=$(date +"%Y%m%d")
      backupDir="$refDir/backup/$testDir/INCOMPLETE_${thisDate}"
      mkdir -p "$backupDir"
      rsync -a "${refTestDir}/" "$backupDir/"
      [ -d "$refTestDir" ] && rm -rf "$refTestDir"/* # checking reTestDir again is redundant but take no risk with rm...
    elif [[ ( $(< ${refTestDir}/${gitHashFile}) == "$gitSha1" ) ]] && [[ ( $(< ${refTestDir}/version) == "$versionNumber" ) ]]; then   #cmp -s "version"  "${refTestDir}/version" ; then
      echo "Reference data directory exists, and seems to have been created from identical build
      version. Do you want to overwrite? [y/n]"
      read userInput
      if [[ ${userInput,,} == "n"* ]]; then
        echo "Exiting.."
        exit 0
      else
        echo "Backing up and continuing..."
        backupDir="$refDir/backup/$testDir/${versionNumber}_ALT_$gitSha1"
        mkdir -p $backupDir
        #mv ${refTestDir}/* $backupDir           
        rsync -a "${refTestDir}/" "$backupDir/"
      fi
    else
      echo "Overwriting references and backing up..."
      backupDir="$refDir/backup/$testDir/${versionNumber}_$gitSha1"
      mkdir -p $backupDir
      #mv ${refTestDir}/* $backupDir          
      rsync -a "${refTestDir}/" "$backupDir/"
    fi
  else
    echo "Reference directory for this test does not exist. Creating.."
    mkdir -p $refTestDir
  fi

	echo $gitSha1 > ${refTestDir}/${gitHashFile}
	cp version $refTestDir

	# grep untracked files zip them and include them in ref dir
	if git status -s | grep "?" | grep -e "\.sh" -e "\.py" -e "\.f90" -q
	then
		git status -s | grep "?" | grep -e "\.sh" -e "\.py" -e "\.f90" | sed 's/?? //g' | zip ${refTestDir}/untrackedFiles.zip -@
	fi
	
  # cd to the script's directory
	cd "$(dirname "$0")"

	echo "creating msg reference albedo on full disk"
	
  mkdir -p log
	python3 ../../pyal2/wrapper.py acf.msg.model0.startserie.true.yaml pcf.msg.2016-08-01.yaml -i MSG --config-format yaml --outputdates 2016-08-01 --keywords name full --loglevel info --chunksize 500 --cpu 3 1>log/log.1  2>log/logerr.1
	echo "first step with startseries true ok"
	python3 ../../pyal2/wrapper.py acf.msg.model0.startserie.false.yaml pcf.msg.2016-08-02.yaml -i MSG --config-format yaml --outputdates 2016-08-02 --keywords name full --loglevel info --chunksize 500 --cpu 3  1>log/log.2  2>log/logerr.2

	cp output/* $refTestDir
	cp -r log $refTestDir

  chmod -R u=rwX,g=rwX,o=rX $refDir

fi

