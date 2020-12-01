Todo list (regarding software)
==============================

TODO first
-----------
- Create jupyter notebooks to show how to run the code interactively.
- Setup output values for tests.
- Implement readers/writers for EPS.
- Implement readers/writers for MTG.
- Implement readers/writers for EPS-SG.
- Go through the fortran code and work on the TODOs written in the fortran code. There are unclear parts.
- The processing of the reflectance covariance is not right. There are hard-coded value in the code (in fortran_src/model_fit.f90).
- Make sure the pip package works. All recent tests have been made without proper installation in a separated environment.
- Improve tests, currently the variables types are not checked, neither are the attributes
- The parameter `n_channels_in` is duplicated in some places, need to clean this up when doing multisensor
- Generally speaking integrating multisensor is not done. We left space in the design to implement it whenever it was possible, but some work is needed to include multisensor I/O. Of course the fortran code would also need to be adapted. The fortran function model_fit.f90 may need to be splitted into two parts : normalisation + brdf model fitting.
- Some default values are set in the config because they are different for c3s and MSG (for instance "initial_value_brdf_age"). Eventually, we should set them to the same values or make sure that the code does not depend on these initial values.


TODO maybe
---------------------
- Proofread fortran code : Remove dead code (some part are here for historical reason and are not needed anymore), rename variables if needed, create function where needed, use another library to perform matrix inversion instead of nr/.

- Cleanup chunking and parallelisation, the current implementation is done in the main wrapper code, it is a quick patch that works but it has not been clearly designed. Perhaps using xarray will allow to use dask for chunking and parallelisation and have something already implemented, using dask should be robust, well-designed, easy to maintain.

- Use xarray for input and output.
    This would make everything shorter and simpler. Moreover, using xarray for writing will ensure that the output files honore the netcdf CF conventions.

- Use functions in the readers, not classes. The readers ID in the config files (such as 'msg_reflectance_toc' should be changed to 'msg.reflectance.toc'), and the function in `pyal2/readers/__init__.py` can be simplified a lot.

- Add kernel for Aerosols
    The scientific code of aerus could be integrated here. Generally speaking, if this framework works well, more algorithm could be developped using the same ideas. A question would be if we want to reuse parts of the package or develop another similar package. If we go too far in developping a generic package we will end up with something very similar to `pytroll <http://pytroll.github.io/>`_

- Variance sqrt in angular integration module :
    There is a unclear piece of code that may need to be cleaned up. It may create many issues (impossible to reproduce the same output, unclear definition of the brdf output covariances and of the brdf input covariance of the angular integration module, etc.).

    The brdf module (model_fit.f90) performs model fitting and get covariances in a "ck" variable. Then it processes this "ck" into a covariance by performing a strange element-by-element square-root-keeping-the-same-sign.
    It outputs this covariance (and covariance1 for one day output)
    "ck" is a internal variable (temporary).

    The angular integration module uses this covariance as input.
    In the angular integration module, the variable "ck" is recomputed from the
    variance.
    This does not make much sense and implies that we do not know what the input of angular integration module should be. It is called variance but it is a sort of sqrt(variance). Moreover there are two useless computation of sqrt and re-squared.

- rewrite the code regarding self.badquality in the files readers/\*/lwcs_mask.py to have a cleaner way to read input data quality. Make a choice : either add self.badquality to all object that are read, or remove this one.



Not urgent, not now, (not needed ?)
-----------------------------------

- Use zarr as output file format. Or as input.
    See documentation about zarr. Make sure the format is mature enough before switching to zarr. Make sure UCAR is using it.

- Optimize speed/memory
    Not useful in some operational chains, but useful for research, we could add multithreading. The fortran code is threadsafe. Reading hdf5 is not threadsafe (AFAIK in May 2017). NetCDF4 may not be threadsafe. See what is done on MDALN for multithreading. Perhaps read in parallel using several process ? Or use zarr which can read in parallel.

- Additional split of the very long fortran function.
    This could be interesting in order to avoid duplicated code (Kalman filters), to allow compilator optimisation, automatic parallelisation, easier debugging and python visualisation, etc.

- Improve tests, use a real test framework, like nose (nosetests https://nose.readthedocs.io/en/latest/testing.html)

