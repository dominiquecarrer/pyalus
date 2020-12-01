#!eusr/bin/env python 

import logging
import sys
import numpy as np
import time

import tblib.pickling_support
tblib.pickling_support.install()
import traceback

def chunk_init(_lock):
    """ Initialise the shared variable for a give chunk. Only the write lock semaphore for now."""
    # this write_lock is a semaphore when using multplit processes/threads in order to
    # make sure that only one is writing at the same time. HDF5 and netcdf4
    # libraries are not thread safe. The Zarr format will be better to use.
    global write_lock
    write_lock = _lock
    ## We could introduce a random delay between 0 and 5 sec to prevent
    ##process to read the same file simultaneously
    ## This does not seem to be required. This code has been commented.
    #np.random.seed()
    #delay = np.random.random() * 5
    ##print(str(chunk) + str(delay))
    #time.sleep(delay)

class ExceptionInSubprocessWrapper(object):
    """ This part of the code may be cryptic to python begginners.
    You may not need to understand what is here.

    The traceback is the list of filename and line numbers displayed
    when an Exception happens (usually when a python program crashes).
    It is required to debug efficiently and identify the code causing
    the problem. When an Exception happens in a subprocess (or maybe a
    thread), the information about the stacktrace is lost. This is
    because the exception traceback cannot be "pickled" to be transferred.
    Here, we are making use of tblib pickling_support, in order to be
    able to save the stacktrace in the object ExceptionInSubprocessWrapper.
    The important point is that the function called by the parallelisation
    call ("starmap" or "map" called on each process in the Pool) must
    return an object of type ExceptionInSubprocessWrapper. Such object
    is transfered to the parent process and contains the traceback
    information. This object can be used to display the traceback
    information with the log_error() method.

    Example :
    >>> def f(x): return 1/x

    >>> try:
    ...     f(0)
    ... except Exception as e:
    ...     print(e)
    division by zero

    >>> try:
    ...     f(0)
    ... except Exception as e:
    ...     wrapped = ExceptionInSubprocessWrapper(e, print_now=False)
    >>> wrapped.log_error(print_func=print)
      File "<doctest parallel.ExceptionInSubprocessWrapper[2]>", line 2, in <module>
        f(0)
      File "<doctest parallel.ExceptionInSubprocessWrapper[0]>", line 1, in f
        def f(x): return 1/x
    division by zero
    """

    def __init__(self, exception, info='', print_now=True):
        """ Save trace back information in self.traceback and some additional string in self.info. """
        self.exception = exception
        self.info = info
        self.traceback = self.exception.__traceback__
        # in case something goes wrong in the serialisation, also print the error in standard output
        if print_now: traceback.print_tb(self.traceback)

    def log_error(self, print_func=None):
        """ Display the exception with traceback information using bu default 'logging.error' """
        if print_func is None: print_func=logging.critical
        t = traceback.format_tb(self.traceback)
        for l in t:
            for ll in l.split("\n"):
                if len(ll.strip()):
                    print_func(ll.rstrip())
        print_func(self.exception)

class FakeLock():
    """ The code uses a write lock (to avoid multiple simultaneous writes on the same file).
    When running without multiprocessing, we do not need a lock. In this case,
    we can use this fake lock instead.

    >>> l = FakeLock()
    >>> l.acquire()
    >>> l.release()

    We could also have added a parameter "multiprocessing_enabled" everywhere in the code,
    but this would make the code more complex the handle. Good practice is to hide technical
    details when they are irrelevant to the code."""
    def acquire(self, boolean=None):
        pass
    def release(self):
        pass

if __name__ == "__main__":
    # this doctest allows some automated testing of the funcions based on the comments (called docstring)
    # in triple quotes below the function. See https://docs.python.org/2/library/doctest.html fro details.
    import doctest
    doctest.testmod()
