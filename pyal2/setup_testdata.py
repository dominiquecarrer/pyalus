#!/usr/bin/env python
import os
import socket
import logging
hostname = socket.gethostname()

logging.basicConfig(level=logging.INFO)


def main():
    """ This script sets up the link to the relevant test directories. """
    missing = 0

    if hostname == 'sxvgo1' or hostname[:5] == 'lxvgo': # if we are running

        # C3S data
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/', './test/testc3s_full_avhrr/data_c3s')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/', './test/testc3s_full/data_c3s')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA_LINK/', './test/testc3s_full/data_c3s_alldata')
       # VGT/C3S/TOC/PER_SITE/Avignon/2006/10/11/c3s_L2B_20061011_Avignon_097_1KM_VGT_V1.0.1.nc
       #AVHRR/C3S/TOC/PER_SITE_SNOW/Avignon/1981/08/30/c3s_L2B_19810830_Avignon_120726_4KM_AVHRR_NOAA7_V1.0.1.nc

        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/', './test/testc3s_full_probav/data_c3s')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/', './test/testc3s_onepoint_diff/data_c3s')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/', './test/testc3s_onepoint/data_c3s')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/', './test/testc3s_multi_sensor/data_c3s')

        # MSG data
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/msg/', './test/testmsg_full_f90/data_msg')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/msg/', './test/testmsg_pointwise_f90/data_msg')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/msg/', './test/testmsg_pointwise/data_msg')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/msg/input-checkpoint/', './test/testmsg_full/input')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/msg/', './test/testmsg_full/data_msg')

        #missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/msg/', './test/testmsg_onepoint/data_msg')
        # multipoint comparison : link to the reference
        #missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/msg/', './test/testmsg_multipoints/data_msg')

        # BRDF climato
        _makedir('./test/testc3s_multi_sensor/brdf_climatic')
        #missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/brdf_climato/BRDF_climato_Avignon_4KM_AVHRR_V1.0.nc', './test/testc3s_multi_sensor/brdf_climatic/BRDF_climato_Avignon_4KM_AVHRR_V1.0.nc')
        #missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/brdf_climato/BRDF_climato_Avignon_1KM_VGT_V1.0.nc', './test/testc3s_multi_sensor/brdf_climatic/BRDF_climato_Avignon_1KM_VGT_V1.0.nc')
        # ~ missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/brdf_climato/BRDF_climato_Avignon_4KM_AVHRR_V1.0.nc', './test/testc3s_multi_sensor/brdf_climatic/BRDF_climato_Avignon_4KM_AVHRR_V1.0.nc')
        # ~ missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/brdf_climato/BRDF_climato_Avignon_1KM_VGT_V1.0.nc', './test/testc3s_multi_sensor/brdf_climatic/BRDF_climato_Avignon_1KM_VGT_V1.0.nc')

        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/brdf_climato/BRDF_climato_Avignon_0710_1KM_VGT_V1.0.nc', './test/testc3s_multi_sensor/brdf_climatic/BRDF_climato_Avignon_0710_1KM_VGT_V1.0.nc')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/brdf_climato/BRDF_climato_Avignon_0720_1KM_VGT_V1.0.nc', './test/testc3s_multi_sensor/brdf_climatic/BRDF_climato_Avignon_0720_1KM_VGT_V1.0.nc')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/brdf_climato/BRDF_climato_Avignon_0710_4KM_AVHRR_V1.0.nc', './test/testc3s_multi_sensor/brdf_climatic/BRDF_climato_Avignon_0710_4KM_AVHRR_V1.0.nc')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/brdf_climato/BRDF_climato_Avignon_0720_4KM_AVHRR_V1.0.nc', './test/testc3s_multi_sensor/brdf_climatic/BRDF_climato_Avignon_0720_4KM_AVHRR_V1.0.nc')
        _makedir('./test/testc3s_onepoint//brdf_climatic')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/brdf_climato/BRDF_climato_Avignon_0710_1KM_VGT_V1.0.nc', './test/testc3s_onepoint//brdf_climatic/BRDF_climato_Avignon_0710_1KM_VGT_V1.0.nc')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/brdf_climato/BRDF_climato_Avignon_0720_1KM_VGT_V1.0.nc', './test/testc3s_onepoint//brdf_climatic/BRDF_climato_Avignon_0720_1KM_VGT_V1.0.nc')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/brdf_climato/BRDF_climato_Avignon_0710_4KM_AVHRR_V1.0.nc', './test/testc3s_onepoint/brdf_climatic/BRDF_climato_Avignon_0710_4KM_AVHRR_V1.0.nc')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/brdf_climato/BRDF_climato_Avignon_0720_4KM_AVHRR_V1.0.nc', './test/testc3s_onepoint//brdf_climatic/BRDF_climato_Avignon_0720_4KM_AVHRR_V1.0.nc')

        # DATA for comparisons
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-neo/output-ref-v0.10.5-model3/testc3s_full/','./test/testc3s_full/valid-data')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-neo/output-ref-v0.10.5-model3/testc3s_onepoint_diff','./test/testc3s_onepoint_diff/valid-data')
        #missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-neo/output-ref-v0.10.5-model0/','./test/testmsg_onepoint/valid-data')
        #missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-neo/output-ref-v0.10.5-model0/','./test/testmsg_full_f90/valid-data')
        #missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-neo/output-ref-v0.10.5-model0', './test/testmsg_onepoint_f90/valid-data')
        #missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-neo/output-ref-v0.10.5-model0_old/test/testmsg_multipoints/', './test/testmsg_multipoints/ref_output')
        #missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-neo/', './test/testmsg_full/output-ref')

        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data/pyal2/output-ref-daniel/testmsg_full/', './test/testmsg_pointwise/reference-data')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data/pyal2/output-ref-daniel/testmsg_full_f90/','./test/testmsg_pointwise_f90/reference-data')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data/pyal2/output-ref-daniel/testmsg_full_f90/', './test/testmsg_full_f90/reference-data')
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data/pyal2/output-ref-daniel/testmsg_full/', './test/testmsg_full/reference-data')

        # C3S notebook tutorial for the use of pyal2
        missing = missing + _makelink('/cnrm/vegeo/SAT/DATA/test-data-input/c3s/vgt/jupyter-avignon', './doc/notebook/data_c3s')

    else:
        raise Exception(f'Unknown host name {hostname}. Cannot setup test links on your system. Please update setup_testdata.py')

    logging.info(f'All links to data are ready ({missing} are pointing to non-existent data)')

def _makedir(d):
    if os.path.isdir(d):
        return
    os.makedirs(d)

def _makelink(to, lnk):
    if os.path.exists(to):
        missing = 0
    else:
        missing = 1
    if os.path.realpath(lnk) == os.path.realpath(to):
        logging.debug(f'Ok. Not creating symlink because link already exists : {lnk} -> {os.path.realpath(to)}')
        return missing
    logging.info(f'Ok. Creating link to test data : {lnk} -> {os.path.realpath(to)}')
    os.symlink(to, lnk)
    return missing

if __name__ == "__main__":
    main()
