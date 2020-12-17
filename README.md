# Pyalus
This sofware is named PYALUS: PYthon  code  for  ALbedo  retrieval  Using Satellite data.

It generates, from (Top-Of-Canopy) TOC reflectance data, brdf model output (using semi-empirical kernels). The mathematic inversion is done by a Kalman filter. It also applies angular and spectral integrations to generate albedo outputs.
The detailed description of the algorithm and discussion on its outputs in various project can be found in the following article :
"Surface albedo retrieval from 40-years of Earth observations through the EUMETSAT/LSA SAF and EU/C3S programmes: the versatile algorithm of Pyalus, common features and differences between its operations from 11 Earth observing systems", Dominique Carrer et al., Remote Sensing (Submitted).

This code has been thoroughly tested in Meteo-France and used extensively for research on linux. Previous versions have been running on IPMA premises and also used on another system (VITO).

## Licence
The code is made available in open source under the CeCILL-C  license <https://cecill.info/>.  Users shall therefore follow the principles of this license and, in particular, the rules for the exploitation of the code. In addition, users are kindly requested to duly acknowledge authors of the code: "The Pyalus code (Carrer et al., 2020) was made available to the community by CNRM/Meteo-France thanks to the support of EUMETSAT."

## Installation

`git clone ...`

A part of the code is written in fortran. This part should be compiled before starting.
`cd pyalus`
`make all`

The make process will output loads of warnings, but as long as the .so files is generated in the pyal2/lib folder, the compilation is successful.

- Alternate installation
`pip install pyal2`

Note : numpy must be installed (error message will be raised).
Requirements are defined in the file requirements.txt. This file may not be up to date.

## Usage

See in test/testmsg_pointwise for an example. The script test/testmsg_pointwise/run_albedos.sh uses the configurations files in test/testmsg_pointwise/. It reads its input in test/testmsg_pointwise/input/ and generates files in  test/testmsg_pointwise/output/.

A simple run command is:

`wrapper.py acf.algorithm.configuration.file.yaml pcf.product.configuration.file.yaml`

A more elaborate command using options : (run "wrapper.py -h" to see the list of options)

`wrapper.py acf.algorithm.configuration.file.yaml pcf.product.configuration.file.yaml -i MSG -f yaml --outputdates 2016-08-01 --keywords name onepoint --loglevel debug -x 1500 1500 -y 1500 1500 --debuglevel 10000 1>log/log.1  2>log/logerr.1`

**Configuration files**
The configuration files are written in yaml. Support for legacy fortran90 namelist file is also provided.

## Testing

`make test` will run all tests. Nevertheless, running all test way take a while (several hours). It is recommeded to run tests.

`makefile testmsg_pointwise` will run one test.

Note that the data need to be staged before running any test : `make setup_testdata` will use the appropriate script to create symbolink links to the data. Running the tests on a new platform would require to adapt this script to point to the correct data location.

## Documentation

- The main paper cited above and the related publications should be the reference point to understand the algorithm. Moreover, an extensive documentation of the scientific algorithm can be found in the ATBD (Algorithm Theorical Base Document), available the LSA-SAF (Eumetsat) website <http://lsa-saf.eumetsat.int/>.
- A draft of documentation related to the python code is located in pyalus/doc. An appropriate installation of sphinx and add-ons will allow you to run `make doc` and generate an html documentation in pyalys/doc/.

## Roadmap - How to contribute

See the TODO list.

## Acknowledgements
Contributors to the code : Dominique Carrer and Bernard Geiger (most of the fortran code and scientific developments), Florian Pinault (most of the python code), and others (older contributors __to the code__ please contact us if you wish to be added to this list).
Funding : Eumetsat (LSA-SAF), ECMWF/Copernicus (C3S), Meteo-France, CNRS
