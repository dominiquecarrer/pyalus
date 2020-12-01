Installation
============

Make sure you are using python 3.6 or above.

Generally speaking, do not ignore compilation errors or warnings.

In this pyal2 package, there is a file named :file:`make.log`. It provides a reference log output to double check that the compilation went well. If you have different compilation messages, make sure you understand why.


Install as pip package (will take care of the dependencies) :
-------------------------------------------------------------

    
    This is a pip package. Install it with pip : ``git clone path/to/pyal2; pip install ./pyal2``
    
    This will install pyal2 and all the required dependencies in your environment (if you are neither using virtualenv nor conda, you need to be root to install this. And this is not advisable).
    
    Then, the scripts will be in your path you can run :file:`wrapper.py` and :file:`wrapper_toc_r.py` from anywhere. You can also import pyal2 (and pyal2.brdf and pyal2.visualisation, etc) in your python scripts.



Without full installation.
----------------------------

  Make sure all the dependencies are installed, with correct versions number.

  Just create the libraries with : ``git clone path/to/pyal2; cd pyal2 ; make``

  Then, if you provide absolute path to the scripts, you can run the scripts :file:`pyal2/wrapper.py` and :file:`pyal2/wrapper_toc_r.py` from anywhere.


Generating the documentation
----------------------------
Running ``make html`` should create the documentation in doc/build/html. Open in your browser doc/build/html/index.html
