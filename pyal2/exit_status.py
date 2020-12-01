#!/usr/bin/env python 
import logging
import sys

def exit_status(typ, moreinfo_before='', moreinfo_after=''):
    """ Defines the exit status with appropriate error message. This complies with the APID document provided by the IPMA for the LSA-SAF project."""

    types = {
        'PROCESS_OK': {'exitcode': 0 ,'string': "The algorithm run has ended successfully and its output correctly generated."},
        'UNABLE_TO_PROCESS': {'exitcode': 1 ,'string': "The algorithm run has ended unsuccessfully. This error should be used when no other error code is able to represent the reason of the failure."},
        'UNABLE_TO_CONFIG': {'exitcode': 2 ,'string': "The algorithm was able to read the Algorithm Configuration File but unable to proceed with its own configuration while using its data."},
        'UNABLE_TO_LOG': {'exitcode': 3 ,'string': "The algorithm was unable to log a message using the reportLog function."},
        'LOG_OK': {'exitcode': 4 ,'string': "The algorithm has reported a log message successfully through the reportLog function."},
        'UNABLE_TO_CLEAN': {'exitcode': 5 ,'string': "The algorithm was unable to reset its state after a run. This error could be set, for instance if a created temporary file couldn't be found for deletion."},
        'CLEAN_OK': {'exitcode': 6 ,'string': "The algorithm was able to successfully reset its state after a run."},
        'ALGOCONF_FILE_NOT_FOUND': {'exitcode': 7 ,'string': "The algorithm was unable to open the Algorithm Configuration file provided by the path given as argument."},
        'PRODCONF_FILE_NOT_FOUND': {'exitcode': 8 ,'string': "The algorithm was unable to open the Product Configuration file provided by the path given as argument."},
        'INPUT_NOT_FOUND': {'exitcode': 9 ,'string': "The algorithm was unable to open at least one of its configured input files."},
        'CANT_WRITE_OUTPUT': {'exitcode': 10 ,'string': "The algorithm was unable to write on the provided output file path."},
        'CANT_ALLOCATE_MEM': {'exitcode': 11 ,'string': "The algorithm was unable to allocate needed memory to proceed with its run."},
    }
    exception = types[typ]
    exitcode = exception['exitcode']
    if typ == 'PROCESS_OK': # no error message if sucessfull exit
        logging.info(moreinfo_before + ' EXIT_STATUS ' + str(exitcode) + ' ' + typ + ': ' + exception['string'] + moreinfo_after)
    else:
        logging.critical(moreinfo_before + ' ERROR ' + str(exitcode) + ' ' + typ + ': ' + exception['string'] + moreinfo_after, exc_info=True)
    sys.exit(exitcode)
