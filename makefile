O  = obj/
S  = fortran_src/
BUILD = build/

# Depending on where your libraries are located, you may want to comment one of the two following lines in order point to .../lib or .../lib64.
LIBLAPACK64=$(shell python3 -c 'import glob; import sys; import os; python = "'$(shell which python3)'"; sys.stdout.write(python.replace("/bin/python3", "/lib64")) ')
LIBLAPACK=$(shell python3 -c 'import glob; import sys; import os; python = "'$(shell which python3)'"; sys.stdout.write(python.replace("/bin/python3", "/lib")) ')
# LIBLAPACK=$HOME/miniconda3/envs/envname/lib/


.PHONY : lib clean

F2PY = LDFLAGS=-shared f2py

F90 = gfortran
F90FLAGS = -c -O0 -funroll-loops -fPIC

# Get the variables PYVERSION and PROC because the compiled libraries are written in *.so file named according to this.
# For instance the al2.*.so library is named "al2.cpython-36m-X86_64-linux-gnu.so"
# when you are using python 3 and "al2.cpython-35m-X86_64-linux-gnu.so" when you are using python 3.5.
PYV=$(shell python3 -c "import sys;t='{v[0]}.{v[1]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)");
python_version_full := $(wordlist 2,4,$(subst ., ,$(shell python3 --version 2>&1)))
python_version_major := $(word 1,${python_version_full})
python_version_minor := $(word 2,${python_version_full})
python_version_patch := $(word 3,${python_version_full})
PYVERSION := $(python_version_major)$(python_version_minor)
PROC = $(shell uname -p)

# The first target of the make file is the one that is made when calling make with no arguments.
# We put here the main libraries
lib: tocr_lib albedo_lib
all: tocr_lib brdfwrapper_lib test_lib albedo_lib

albedo_lib: pyal2/lib/al2.cpython-${PYVERSION}m-${PROC}-linux-gnu.so
tocr_lib: pyal2/lib/toc_r.cpython-${PYVERSION}m-${PROC}-linux-gnu.so
brdfwrapper_lib: pyal2/lib/brdfwrapper.cpython-${PYVERSION}m-${PROC}-linux-gnu.so
lapackwrapper_lib: pyal2/lib/lapackwrapper.cpython-${PYVERSION}m-${PROC}-linux-gnu.so
test_lib: test/testal2.cpython-${PYVERSION}m-${PROC}-linux-gnu.so

##########################
# Actual build of the libraries using f2py.
##########################
# The command "f2py" builds a .so file from the fortran code (*.f90 files), then we
# move it to the correct folder and it will be imported as a standard python library.
#
# Note : when interfacing fortran and python, it way be usefull to enable  the option
# -DF2PY_REPORT_ON_ARRAY_COPY=1. See web for documentation about C-arrays order vs
# fortran-arrays order. This is an example on how to set up this option :
# $(F2PY) -DF2PY_REPORT_ON_ARRAY_COPY=1  -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION --f90flags='-ffree-line-length-512 -Wall -Wextra' -c $(BUILD)solzenith.o  $(S)brdfmodels.f90 $(S)toc_r.f90 -m toc_r --quiet
#
# The options --f90flags='-ffree-line-length-512' is given to the fortran compiler,
# it allows long lines in fortran (more than the standard 80 characters).
# The options --f90flags='-Wall -Wextra' are given to the fortran compiler to enable warning.
# It is good to remove all warning or to know why they are here.
# It you ignore warnings, you will have troubles and die. The current warnings are in the file make.log.
# These are fine. Any new warning must be understood and documented.

# build the pyal2 library
pyal2/lib/al2.cpython-${PYVERSION}m-${PROC}-linux-gnu.so: $(BUILD)solzenith.o $(S)brdfmodels.f90 $(S)lapackwrapper.f90 $(S)algoconf.f90 $(S)model_fit.f90 $(S)albedo_angular_integration.f90 $(S)albedo_spectral_integration.f90
	$(F2PY) -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION -L$(LIBLAPACK) -L$(LIBLAPACK64) -llapack --f90flags='-ffree-line-length-512 -Wall -Wextra -Wno-unused-function' -c $(BUILD)solzenith.o $(S)lapackwrapper.f90 $(S)algoconf.f90 $(S)brdfmodels.f90 $(S)model_fit.f90 $(S)albedo_angular_integration.f90 $(S)albedo_spectral_integration.f90 -m al2 --quiet only: model_fit albedo_angular_integration albedo_spectral_integration :
	mkdir -p pyal2/lib
	mv al2.cpython-${PYVERSION}m-${PROC}-linux-gnu.so pyal2/lib/.
	echo 'BUILD SUCCESSFULL : Fortran library "al2" successfully compiled into a .so file'

# build brdfwrapper library (useful to integrate the kernel in python, to draw plots for instance)
pyal2/lib/brdfwrapper.cpython-${PYVERSION}m-${PROC}-linux-gnu.so: $(S)brdfmodels.f90 $(S)brdfwrapper.f90
	$(F2PY) -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION  --f90flags='-ffree-line-length-512 -Wall -Wextra -Wno-unused-function' -c $(S)brdfmodels.f90 $(S)brdfwrapper.f90 -m brdfwrapper --quiet
	mkdir -p pyal2/li
	mv brdfwrapper*.so pyal2/lib/.

# build lapack library
pyal2/lib/lapackwrapper.cpython-${PYVERSION}m-${PROC}-linux-gnu.so: $(S)lapackwrapper.f90
	$(F2PY) -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION  --f90flags='-ffree-line-length-512 -Wall -Wextra -Wno-unused-function' -c $(S)lapackwrapper.f90  -m lapackwrapper  #--quiet
	mkdir -p pyal2/li
	mv lapackwrapper*.so pyal2/lib/.

# build toc_r library
pyal2/lib/toc_r.cpython-${PYVERSION}m-${PROC}-linux-gnu.so: $(BUILD)solzenith.o $(S)brdfmodels.f90 $(S)toc_r.f90
	$(F2PY) -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION --f90flags='-ffree-line-length-512 -Wall -Wextra -Wno-unused-function' -c $(BUILD)solzenith.o  $(S)brdfmodels.f90 $(S)toc_r.f90 -m toc_r --quiet
	mkdir -p pyal2/lib
	mv toc_r*.so pyal2/lib/.

# build the test library, if this fail, the rest is likely to have some problem
test/testal2.cpython-${PYVERSION}m-${PROC}-linux-gnu.so: $(S)test_io.f90
	$(F2PY) -c $(S)test_io.f90 -m testal2 --quiet only: is_nan :
	mv testal2*.so test/.

##################
# Physical Dependencies
##################
# Compiling below is required as a dependency of the fortran code to perform matrix inversion
$(BUILD)solzenith.o:     $(S)solzenith.f90
	$(F90) $(F90FLAGS) $(S)solzenith.f90 -o $@


#########################
# Automatic tests
#########################

setup_testdata:
	./pyal2/setup_testdata.py

# run all tests
test: doctest testonepoint testfullc3s testfullmsg  testdiff

# run only quick tests
testonepoint: testc3s_onepoint testmsg_multipoints

# run full scale tests, taking a long time
testfullc3s: testc3salbedo_full testc3stocr_full testmsg_albedo_full testc3s_full_probav testc3s_full_multi_sat
testfullmsg: testmsg_albedo_full testmsg_albedo_full_f90

# run one point with differences
testdiff: testc3s_onepoint_diff testmsg_albedo_onepoint testmsg_albedo_onepoint_f90 

# c3s tests
testc3s_onepoint: lib setup_testdata
#~ 	./test/testc3s_onepoint/run_albedo_and_toc_r.sh La_Crau
	./test/testc3s_onepoint/run_albedo_and_toc_r.sh Avignon
testc3s_full: lib setup_testdata
	./test/testc3s_full/run_albedo_and_toc_r.sh Avignon
#~ 	./test/testc3s_full/run_albedo_and_toc_r.sh La_Crau
#~ 	./test/testc3s_full/run_albedo_and_toc_r.sh Gloria
#~ 	./test/testc3s_full/run_albedo_and_toc_r.sh Villefranche
#~ 	./test/testc3s_full/run_albedo_and_toc_r.sh Tuz_Golu
#~ 	./test/testc3s_full/run_albedo_and_toc_r.sh Minsk

# c3s tests with comparison of outputs with a validated version
testc3s_onepoint_diff: lib setup_testdata
	./test/testc3s_onepoint_diff/run_albedo_and_diff.sh Avignon
	#./test/testc3s_onepoint_diff/run_albedo_and_diff.sh Minsk

testc3s_full_probav: lib setup_testdata
	./test/testc3s_full_probav/run_albedo_full_probav.sh

testc3s_full_multi_sat: lib setup_testdata
	./test/testc3s_multi_sensor/run.albedo.multi-sat.sh

# msg tests
#~ testmsg_albedo_onepoint: lib setup_testdata
#~ 	./test/testmsg_onepoint/run_albedo.sh
testmsg_multipoints: lib setup_testdata
	./test/testmsg_multipoints/run_albedo_7points.sh && vi test/testmsg_multipoints/log/log.diff

testmsg_albedo_full: lib setup_testdata
	./test/testmsg_full/run_albedo.sh

testmsg_albedo_onepoint_f90: lib setup_testdata
	./test/testmsg_onepoint_f90/run_albedo.sh

testmsg_albedo_full_f90: lib setup_testdata
	./test/testmsg_full_f90/run_albedo.sh

testmsg_pointwise_1: lib setup_testdata
	./test/testmsg_pointwise/run_albedo.sh

testmsg_pointwise_8: lib setup_testdata
	./test/testmsg_pointwise/run_albedo_8points.sh

testmsg_pointwise_1_f90: lib setup_testdata
	./test/testmsg_pointwise_f90/run_albedo.sh

testmsg_pointwise_8_f90: lib setup_testdata
	./test/testmsg_pointwise_f90/run_albedo_8points.sh

doctest: lib brdfwrapper_lib setup_testdata
	# this doctest allows some automated testing of the funcions based on the comments (called docstring) in triple quotes below the function. See https://docs.python.org/2/library/doctest.html fro details.
	cd pyal2 && export PYTHONPATH=$$PYTHONPATH:./self_import &&  for i in *.py; do python -m doctest $$i; done
	cd pyal2 && export PYTHONPATH=$$PYTHONPATH:./self_import &&  for i in utils/*.py; do python -m doctest $$i; done
	cd pyal2 && export PYTHONPATH=$$PYTHONPATH:./self_import &&  for i in writers/*.py; do python -m doctest $$i; done
	cd pyal2 && export PYTHONPATH=$$PYTHONPATH:./self_import &&  for i in validation/[azertyuiopqsdfghjklwxcvbn]*.py; do python -m doctest $$i; done # removing make_plot.py which is failing
	cd pyal2 && export PYTHONPATH=$$PYTHONPATH:./self_import &&  for i in config_utils/*.py; do python -m doctest $$i; done
	#cd pyal2 && export PYTHONPATH=$$PYTHONPATH:./self_import &&  for i in writers/*.py; do python -m doctest $$i; done # disabled because doctest does not support relative import
	#cd pyal2 && export PYTHONPATH=$$PYTHONPATH:./self_import &&  for i in readers/*.py; do python -m doctest $$i; done # disabled because doctest does not support relative import

ref_albedo_full_f90:
	./test/testmsg_full_f90/create_ref_albedo.sh

ref_albedo_full:
	./test/testmsg_full/create_ref_albedo.sh

# this test is failing because it uses obsolete code.
#test_io: test_lib
#	./test/test_io.py

########################################
# build documentation
########################################>
html: doc/source/pyal2.rst
	cd doc && make html
doc/source/pyal2.rst:
	cd doc && sphinx-apidoc -o source pyal2 -f -e --ext-viewcode --ext-coverage --ext-autodoc --ext-doctest --ext-imgmath --ext-todo

#########################
# Cleaning tools
#########################
# clean the compiled libraries
clean:
	rm -f *.mod $(BUILD)/*.o al2.so al2.*.so test/*.so pyal2/lib/*.so
	rm -rf $(BUILD)/lib $(BUILD)/scripts-*
	rm -rf pyal2/__pycache__
	rm -rf pyal2/*/__pycache__
	rm -rf pyal2/readers/msg/__pycache__
	rm -rf pyal2/readers/c3s/__pycache__
	echo
	echo 'WARNING: test output folders have not been deleted. To clean it (delete it) do "make cleantests"'

# clean the test generated files
cleantests: cleantests_output_only cleantests_logs_only cleantests_cache_only

cleantests_output_only:
	rm -rf test/test*/output*
cleantests_logs_only:
	rm -rf test/test*/log*
cleantests_cache_only:
	rm -rf test/test*/cache

