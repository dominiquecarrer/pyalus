This document aims at describing the code from a developper point of view, to allow easier update and debugging of the code.

# Code structure

The global structure consists in several python modules :

- `fortran_src/*` : scientific fortran code
- `pyal2/*.so` : compiled fortran libraries from `fortran_src` (must be created with "make")
- `pyal2/*.py` : generic code related to all project.
- `pyal2/msg` : code specific to the project msg
- `pyal2/eps` : code specific to the project eps
- `pyal2/c3s` : code specific to the project c3s
- `pyal2/X` : code specific to the project X


# Programming style

The name of each function should be explicit enough to know what the function is doing.

To ensure better modularity of the code, there is no unique 'start.f90' script. Instead the code is separated into functions (also called methods), belonging to classes (a class is a set of functions with additional properties). Note the omnipresent `self` variable which is not the same for each class : self depends on the class. It provides the object : the object is a set of variables that are relevant when executing a function. A semester of object oriented-programming would be useful to fully understand this (see online classes). Nevertheles, in practice considering that we have a set of functions and variables will be enough.


# Software Validation

For MSG, on Europe, BRDF coefficients are identical to the previous version of the software. This has been checked for K012, Cij, Qflag, Age on a three months run.


# Scientific Validation

Initial MSG code has been validated against the old pure-fortran MSG code (which had been validated, see the LSA-SAF validatation report).

# Reusability for analysis

## Load config file
cd /cnrm/vegeo/pinaultf/codes/lsasaf/pyal2
from pyal2.c3s.c3s_data_manager import C3SDataManager
dm=C3SDataManager('config/acf.c3s', 'config/pcf.c3s',startseries=True, dates=['2002-04-15','2002-04-30'])

## Use config to read reflectance
from pyal2.c3s.reflectance import Reflectance as C3SReflectance
from pyal2.c3s.lwcs_mask import LWCS_mask as C3SLWCS_mask
date = dm['dates'][0]
scenes_dates = dm.compute_scenes_dates(dm.dates_to_filename.keys(),date)
xslice, yslice = slice(0,dm.xfullsize), slice(0,dm.yfullsize)
reflectance = C3SReflectance('toc_reflectance', dm, xslice, yslice, scenes_dates)
lwcs_mask   = C3SLWCS_mask(  'lwcs_mask',       dm, xslice, yslice, scenes_dates)
plt.plot(reflectance.data[25,25,:,:].T)


## or more...

from pyal2.c3s.lwcs_mask import LWCS_mask as C3SLWCS_mask
from pyal2.c3s.angle import Angle as C3SAngle
from pyal2.c3s.latitude import Latitude as C3SLatitude
date = dm['dates'][0]
scenes_dates = dm.compute_scenes_dates(dm.dates_to_filename.keys(),date)
xslice, yslice = slice(0,dm.xfullsize), slice(0,dm.yfullsize)
reflectance = C3SReflectance('toc_reflectance', dm, xslice, yslice, scenes_dates)
lwcs_mask   = C3SLWCS_mask(  'lwcs_mask',       dm, xslice, yslice, scenes_dates)
zenith_sat  = C3SAngle('theta_view',dm, xslice, yslice, scenes_dates)
zenith_sol  = C3SAngle('theta_sun', dm, xslice, yslice, scenes_dates)
azimuth_sat = C3SAngle('phi_view',  dm, xslice, yslice, scenes_dates)
azimuth_sol = C3SAngle('phi_sun',   dm, xslice, yslice, scenes_dates)
latitude = C3SLatitude(dm, xslice, yslice, scenes_dates)
clear = (lwcs_mask.data == -123)
reflectance.data[~clear] = np.nan
f = plt.figure(facecolor='w',figsize=(8,8)) 
f.subplots_adjust(hspace=.3) 
a = f.add_subplot(321); a.plot(reflectance.data[25,25,:,:].T); a.set_title('Reflectance'); plt.grid()
a = f.add_subplot(322); a.plot(azimuth_sol.data[25,25,:].T); a.set_title('SAA'); plt.grid()
a = f.add_subplot(323); a.plot(zenith_sol.data[25,25,:].T); a.set_title('SZA'); plt.grid()
a = f.add_subplot(324); a.plot(azimuth_sat.data[25,25,:].T); a.set_title('VAA'); plt.grid()
a = f.add_subplot(325); a.plot(zenith_sat.data[25,25,:].T); a.set_title('VZA'); plt.grid()
a = f.add_subplot(326); a.plot(latitude.data[25,25]); a.set_title('Latitude = ' + str(latitude.data[25,25])); plt.grid()


