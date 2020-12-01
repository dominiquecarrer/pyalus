from distutils.core import setup
import subprocess

# make sure some version of numpy is installed because we need it for the installation
try:
    import numpy
except ImportError:
    raise Exception('Please install numpy version > 1.x.x before installing this')
if int((numpy.__version__).split('.')[0]) < 1 : # numpy at least version 1.x.x
    raise Exception('Please install numpy version > 1.x.x before installing this')

#import netCDF4
#if int((netCDF4.__version__).split('.')[0]) < 1 : # numpy at least version 1.x.x
#    raise Exception('Please install netcdf version > 1.2.4 before installing this')

with open('version') as version_file:
        version = version_file.read().strip()

from setuptools.command.install import install
class MyInstall(install):
    def run(self):
        make_process = subprocess.Popen(["make"], stderr=subprocess.STDOUT)
        if make_process.wait() != 0:
             raise Exception('Make fortran pyal2 failed')
        install.run(self)

setup(name = 'pyal2',
      description       = "BRDF and albedo from TOC computation",
      author            = "Florian Pinault",
      packages = ["pyal2"],
      scripts = ["pyal2/wrapper.py"],
      version = version,
      cmdclass={'install': MyInstall},
      install_requires=['numpy', 'f90nml', 'coloredlogs', 'tblib'],
      extras_require={'msg': 'h5py', 'c3s':'netCDF4'},
      include_package_data=True,
      package_data={'pyal2': ['c3s/*','msg/*','pyal2/al2.cpython-36m-x86_64-linux-gnu.so','pyal2/brdfwrapper.cpython-36m-x86_64-linux-gnu.so']}
      )
