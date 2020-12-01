
Overview
========


The package pyal2 uses the fortran code from LSA-SAF.

Fortran vs python
-----------------

- Fortran code is the **scientific code** (Kalman filter and security keys). The fortran code has not been recoded to make it more modular or efficient in order to be as close as the original code as possible. Many things could potentially be improved in this code. See :doc:`todo`.

- Python is used to **read and write data** : it uses netCDF, and HDF5. Xarray input would be better to use but has not been do yet. See :doc:`todo`.

- Python code is also used to **manage dates**, to run several dates in a row.

- **Exception management** (when something goes wrong, crashes, missing file, cannot write, or an error in the code) is also handled in python.

- **Parallelisation** (multiprocessor) and **chunking** (splitting the zone to process in rectangular chunks) is also done with python.

- **Visualisation tools** have been developped in python (see :doc:`visualisation`). But some more work could be done to make them easy to use.



Running one time step
---------------------

Assuming the data have been loaded correctly in an object of type :class:`pyal2.al2_runner.Al2Runner`, the methods wrapping the fortran functions can be called :

- :func:`run_model_fit() <\pyal2.al2_runner.Al2Runner.run_model_fit>` is wrapping :download:`fortran_src/model_fit.f90`
- :func:`run_angular_integration() <\pyal2.al2_runner.Al2Runner.run_angular_integration>` is wrapping :download:`fortran_src/albedo_angular_integration.f90`
- :func:`run_spectral_integration() <\pyal2.al2_runner.Al2Runner.run_spectral_integration>` is wrapping :download:`fortran_src/albedo_spectral_integration.f90`

:func:`pyal2.al2_runner.lib.al2.model_fit()` 


Reading input files into numpy arrays
-------------------------------------
All the code reading input data is located in pyal2/readers : for instance reading msg latitude is done with :mod:`pyal2.readers.msg.latitude`

These files have all the same structure : a class with two function *load* and *to_xr*.

The *load* function with the required parameters (xslice, yslice, scenes_dates, dataloc) and some additional parameters (that are declared in 'data_params'
The load function is responsible to return a object with the relevant data in self.values.

The *to_xr* function, not used, untested, to provide data as xarray.


:note: On exception is lwcs mask where the bad quality data is saved in self.badquality. This is bad design and can be confusing.


Writing output data
-------------------
The code writing the data output is located in :mod:`pyal2.writers`. Which writer to use is defined in the initial config file, in the output section, next to the output filenames.


DataStore and dataBox : Running several time steps
--------------------------------------------------
Running the code involves 3 main components :

- DataStore (to know the location of the data)
- DataBox (to load the data)
- Al2Runner (to run the code).

**First, in the main script is created a DataStore to load the config**
The config files are read (acf -- algorithm config file and pcf -- product config file). These config are loaded into a DataStore object. A DataStore object knows which date(s) to run, it knows all what is needed to find the right files for the right dates and which code should be run to read these data.

**Second, Al2Runner objects are created to run the date loop** (one for each tile of data, tiles are called chunk, see below for chunking and parallelisation)
For each date to run, the object Al2Runner asks the DataStore object to provide a DataBox.
The DataBox knows everything that is required to provide inputdata for a given timestep.

**Third, the DataBox provides actual numpy arrays** when the Al2Runner needs it.



Checkpoint : Initialisation of the first time step
--------------------------------------------------
The algorithm relies on the value of the current BRDF state. For each time step a BRDF is saved and used for the next steps. As there are several possible ways to run the code, choosing the brdf file to load at each time step has multiple if-then-else tests. This logic is mainly witten in :func:`pyal2.al2_runner.Al2Runner.get_checkpoint_data()` and :func:`pyal2.data_store.DataStore.create_data_box()`.


Chunking and parallelisation
----------------------------
The **chunking** refers to processing the data by "chunks" (sometimes called "tiles") : parts of the full spatial zone. The chunks are computed at the very beginning of the process, in `wrapper.py`, it uses :func:`pyal2.chunking.chunk_2D()` to split the dimensions of the zone to process. Then each chunk is processed through an object Al2Runner. Note that chunking does not imply any parallelisation, it merely consists in loading and processing only part of the data in order to save memory. The drawback is that the input files are read multiple times, depending on the internal chunking scheme of the input files, chunking may waste lots of time reading and uncompressing data.

**Parallel processing** of can be done with multithreading, multiprocessing or multiple machines. Multithreading should be avoided if we are unsure that the hdf or netcdf libraries are thread-safe. We choosed multiprocessing and implemented it in the main python script wrapper.py. It uses functions and classes defined in :mod:`pyal2.parallel`.


Config Files
------------
Config files are written in yaml. The reason for using yaml instead of fortran namelist is that it easier to edit, it allows nested configuration, and is more consistent regarding the data type in the config file (for instance fortran namelists have troubles to handle lists of one elements).

Nevertheless, fortran namelist config files are somehow supported to be able to compare easily with previous version of code, for msg and c3s. They are transformed into standard yaml file using function in :mod:`pyal2.config_utils`




