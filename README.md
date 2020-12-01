# Pyalus
This sofware applies BRDF kernels models on (Top-Of-Canopy) TOC reflectance data. We  named  it PYALUS  (PYthon  code  for  ALbedo  retrieval  Using Satellite data).
It generates a brdf model output (using semi-empirical kernels), includes a Kalman filter. It also applies angular and spectral integrations to generate albedos output.
The detailed description of the algorithm and discussion on its outputs in various project can be found in the following article :

"Surface  albedo retrieval from 40-years of Earth observations through  the EUMETSAT/LSA-SAF  and  EU/C3S  programmes: methods, common  features and differences between the operations from 11 Earth observing systems", Dominique Carrer, Florian Pinault, Gabriel Lellouch, Isabel F. Trigo, Iskander Benhadj, Roselyne Lacaze, Fernando Camacho, Xavier Ceamanos,Suman Moparthy, Michael Parde, Didier Ramon, Lothar Schuüllr, and Jorge Sanchez Zaper.

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
Requirement are defined in the file requirement.txt. This may no be up to date.

## Usage

See in test/testmsg_pointwise for an example. The script test/testmsg_pointwise/run_albedos.sh uses the configurations files in test/testmsg_pointwise/. It reads its input in test/testmsg_pointwise/input/ and generates files in  test/testmsg_pointwise/output/.

A simple run command is:
`wrapper.py acf.algorithm.configuration.file.yaml pcf.product.configuration.file.yaml`

A more eleborate command using options : (run "wrapper.py -h" to see the list of options)

`wrapper.py acf.algorithm.configuration.file.yaml pcf.product.configuration.file.yaml -i MSG -f yaml --outputdates 2016-08-01 --keywords name onepoint --loglevel debug -x 1500 1500 -y 1500 1500 --debuglevel 10000 1>log/log.1  2>log/logerr.1`

- Configuration file
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
Contributors to the code : Bernard Geiger, Florian Pinault, Mickael Parde, Chloe Vincent, and others (Older contributors __to the code__ please contact us to be added the this list).
Funding : Eumetsat (LSA-SAF), ECMWF/Copernicus (C3S), Meteo-France
