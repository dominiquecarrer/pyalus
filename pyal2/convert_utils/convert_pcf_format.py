#!/usr/bin/env python 


import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/self_import/.')

import yaml 
import argparse

# Test du wrapper yaml APID => 

try:
    import coloredlogs, logging
except ImportError:
    import logging


def parse_args():
        parser = argparse.ArgumentParser(
                description='Apply BRDF model fitting to reflectance, with various Kalman filters, and generate brdf and albedos.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
                
        parser.add_argument('-l', '--loglevel', help='log level. CRITICAL ERROR WARNING INFO or DEBUG', default='ERROR')
        parser.add_argument('-a','--pcf_apid_name', help='')
        parser.add_argument('-p','--pcf_pyal2_name', help='Product config file')
        parser.add_argument('-e','--empty_file', help='Empty file that we will fill')
        parser.add_argument('--apid2pyal2', action='store_true', help='')
        parser.add_argument('--pyal22apid', action='store_true', help='')
        args = parser.parse_args()
        
        print(args)
        # check presence of parameters
        if args.apid2pyal2 is False and args.pyal22apid is False:
            logging.error('You need to inform the way you want to transform the yaml ! ')
            return
        if  args.apid2pyal2 is True and args.pyal22apid is True:
            logging.error('You gave the two ways of transformation, are you sain ?')
            return
            
        coloredlogs.install(level=args.loglevel.upper())            
        return args

def pyal22apid(inputname, outputname, empty_file):
    """ """
    # reading pyal2_format
    with open(inputname) as f:
        pyal2 = yaml.load(f, Loader=yaml.FullLoader)
        
    logging.debug(f'Input file format open in {inputname}')
    
    lwc = dict()
    toc = dict()
    toccov = dict()
    vaa = dict(); vza = dict(); inputcheckpoint = dict()   
    output_albedo_sp = dict();output_albedo_sp_cov = dict()
    output_brdf_d01 = dict();output_brdf_d01_cov = dict()
    output_brdf= dict();output_brdf_cov = dict()
    list_band = ['band1', 'band2', 'band3']
    # extract relevant parameters
    try:
        
        sza = pyal2['input']['MTG']['zenith_sol']['filenames']
        saa = pyal2['input']['MTG']['azimuth_sol']['filenames']

        lon = pyal2['input']['MTG']['longitude']['filenames']
        lat = pyal2['input']['MTG']['latitude']['filenames']
        
        for band in list_band:
            print(band)
            lwc[band]  = pyal2['input']['MTG']['lwcs_mask'][band]['filenames']
            toc[band] = pyal2['input']['MTG']['toc_reflectance'][band]['filenames']
            toccov[band]  = pyal2['input']['MTG']['toc_reflectance_cov'][band]['filenames']      
            vaa[band] = pyal2['input']['MTG']['azimuth_sat'][band]['filenames']
            vza[band] = pyal2['input']['MTG']['zenith_sat'][band]['filenames']

            inputcheckpoint[band] = {}
            inputcheckpoint[band]['values']=pyal2['input']['MTG']['inputcheckpoint']['filenames'][band]['values']
            inputcheckpoint[band]['cov']=pyal2['input']['MTG']['inputcheckpoint']['filenames'][band]['cov']

            output_albedo_sp[band] = pyal2['input']['MTG']['output']['albedo-sp'][band]['filename']
            output_albedo_sp_cov[band] = pyal2['input']['MTG']['output']['albedo-sp'][band]['cov']
            
            output_brdf[band] = pyal2['input']['MTG']['output']['brdf'][band]['filename']
            output_brdf_cov[band] = pyal2['input']['MTG']['output']['brdf'][band]['cov']
            
            output_brdf_d01[band] = pyal2['input']['MTG']['output']['brdf-d01'][band]['filename']
            output_brdf_d01_cov[band] = pyal2['input']['MTG']['output']['brdf-d01'][band]['cov']
            
        output_albedo = pyal2['input']['MTG']['output']['albedo']['filename']
        output_albedo_cov = pyal2['input']['MTG']['output']['albedo']['cov']
    except :
        logging.error('One or more of the parameters are missing in the pyal2 file')

    # open the empty model
    try:
        with open(empty_file) as f:
            out=yaml.load(f, Loader=yaml.FullLoader)
    except:
        logging.error('No empty file found')
        return
        
    logging.debug(f'Output file format open in pcf.mtg.al2.apid.yml')
    
    out['INPUT_RESOURCES']['VAA']['file_paths'].append(vaa['band1'])    
    out['INPUT_RESOURCES']['VZA']['file_paths'].append(vza['band1'])    
    out['INPUT_RESOURCES']['SZA']['file_paths'].append(sza)    
    out['INPUT_RESOURCES']['SAA']['file_paths'].append(saa)    
    
    out['INPUT_RESOURCES']['LAT']['file_paths'].append(lat)    
    out['INPUT_RESOURCES']['LON']['file_paths'].append(lon)
        
    out['INPUT_RESOURCES']['TOC_REFLECTANCE_BAND1']['file_paths'].append(toc['band1'])
    out['INPUT_RESOURCES']['TOC_REFLECTANCE_BAND2']['file_paths'].append(toc['band2'])
    out['INPUT_RESOURCES']['TOC_REFLECTANCE_BAND3']['file_paths'].append(toc['band3'])
    out['INPUT_RESOURCES']['TOC_REFLECTANCE_COV_BAND1']['file_paths'].append(toccov['band1'])
    out['INPUT_RESOURCES']['TOC_REFLECTANCE_COV_BAND2']['file_paths'].append(toccov['band2'])
    out['INPUT_RESOURCES']['TOC_REFLECTANCE_COV_BAND3']['file_paths'].append(toccov['band3'])
       
    out['INPUT_RESOURCES']['INPUTCHECKPOINT_BAND1']['file_paths'].append(inputcheckpoint['band1']['values'])  
    out['INPUT_RESOURCES']['INPUTCHECKPOINT_BAND2']['file_paths'].append(inputcheckpoint['band2']['values'])  
    out['INPUT_RESOURCES']['INPUTCHECKPOINT_BAND3']['file_paths'].append(inputcheckpoint['band3']['values'])  
    
    out['INPUT_RESOURCES']['INPUTCHECKPOINT_BAND1_COV']['file_paths'].append(inputcheckpoint['band1']['cov'])  
    out['INPUT_RESOURCES']['INPUTCHECKPOINT_BAND2_COV']['file_paths'].append(inputcheckpoint['band2']['cov'])  
    out['INPUT_RESOURCES']['INPUTCHECKPOINT_BAND3_COV']['file_paths'].append(inputcheckpoint['band3']['cov'])  
    
    # Broadband
    out['OUTPUT_RESOURCES']['ALBEDO_BB']['file_paths'].append(output_albedo)
    out['OUTPUT_RESOURCES']['ALBEDO_BB_COV']['file_paths'].append(output_albedo_cov)
    
    # Spectral Albedo
    out['OUTPUT_RESOURCES']['RAD_VIS06']['file_paths'].append(output_albedo_sp['band1'])
    out['OUTPUT_RESOURCES']['RAD_VIS08']['file_paths'].append(output_albedo_sp['band2'])
    out['OUTPUT_RESOURCES']['RAD_NIR16']['file_paths'].append(output_albedo_sp['band3'])
    out['OUTPUT_RESOURCES']['RAD_VIS06_COV']['file_paths'].append(output_albedo_sp_cov['band1'])
    out['OUTPUT_RESOURCES']['RAD_VIS08_COV']['file_paths'].append(output_albedo_sp_cov['band2'])
    out['OUTPUT_RESOURCES']['RAD_NIR16_COV']['file_paths'].append(output_albedo_sp_cov['band3'])
    
    # BRDF
    out['OUTPUT_RESOURCES']['BRDF_VIS06']['file_paths'].append(output_brdf['band1'])
    out['OUTPUT_RESOURCES']['BRDF_VIS08']['file_paths'].append(output_brdf['band2'])
    out['OUTPUT_RESOURCES']['BRDF_NIR16']['file_paths'].append(output_brdf['band3'])
    out['OUTPUT_RESOURCES']['BRDF_VIS06-d01']['file_paths'].append(output_brdf_d01['band1'])
    out['OUTPUT_RESOURCES']['BRDF_VIS08-d01']['file_paths'].append(output_brdf_d01['band2'])
    out['OUTPUT_RESOURCES']['BRDF_NIR16-d01']['file_paths'].append(output_brdf_d01['band3'])
    
    # BRDF_COV
    out['OUTPUT_RESOURCES']['BRDF_VIS06_COV']['file_paths'].append(output_brdf_cov['band1'])
    out['OUTPUT_RESOURCES']['BRDF_VIS08_COV']['file_paths'].append(output_brdf_cov['band2'])
    out['OUTPUT_RESOURCES']['BRDF_NIR16_COV']['file_paths'].append(output_brdf_cov['band3'])
    out['OUTPUT_RESOURCES']['BRDF_VIS06-d01_COV']['file_paths'].append(output_brdf_d01_cov['band1'])
    out['OUTPUT_RESOURCES']['BRDF_VIS08-d01_COV']['file_paths'].append(output_brdf_d01_cov['band2'])
    out['OUTPUT_RESOURCES']['BRDF_NIR16-d01_COV']['file_paths'].append(output_brdf_d01_cov['band3'])    
    
    # write file lists in the outputname file
    logging.debug('we are about to write')
    with open('file_out_apid.yaml', 'w') as file:
        documents = yaml.dump(out, file)
    
def apid2pyal2(inputname, outputname, empty_file):
    """ Function converting APID formated file in a PYAL2 pcf file"""
    with open(inputname) as f:
        apid = yaml.load(f, Loader=yaml.FullLoader)
    
    if os.path.exists(empty_file):
        with open(empty_file) as out:
            pyal2 = yaml.load(out, Loader=yaml.FullLoader)
    else:
        logging.error('no pyal2 pcf file model found')
        return

    # Read and transfert all the apid fields in the pyal2 fields
    pyal2['input']['MTG']['azimuth_sat']['band1']['filenames'] = apid['INPUT_RESOURCES']['VAA']['file_paths']    
    pyal2['input']['MTG']['zenith_sat']['band1']['filenames'] = apid['INPUT_RESOURCES']['VZA']['file_paths']  
    pyal2['input']['MTG']['azimuth_sat']['band2']['filenames'] = apid['INPUT_RESOURCES']['VAA']['file_paths']    
    pyal2['input']['MTG']['zenith_sat']['band2']['filenames'] = apid['INPUT_RESOURCES']['VZA']['file_paths']  
    pyal2['input']['MTG']['azimuth_sat']['band3']['filenames'] = apid['INPUT_RESOURCES']['VAA']['file_paths']    
    pyal2['input']['MTG']['zenith_sat']['band3']['filenames'] = apid['INPUT_RESOURCES']['VZA']['file_paths']  
        
    pyal2['input']['MTG']['zenith_sol']['filenames'] = apid['INPUT_RESOURCES']['SZA']['file_paths']
    pyal2['input']['MTG']['azimuth_sol']['filenames'] = apid['INPUT_RESOURCES']['SAA']['file_paths'] 
    
    # LAT, LON
    pyal2['input']['MTG']['latitude']['filenames'] = apid['INPUT_RESOURCES']['LAT']['file_paths']   
    pyal2['input']['MTG']['longitude']['filenames'] = apid['INPUT_RESOURCES']['LON']['file_paths']
    
    # TOC    
    pyal2['input']['MTG']['toc_reflectance']['band1']['filenames'] = apid['INPUT_RESOURCES']['TOC_REFLECTANCE_BAND1']['file_paths']
    pyal2['input']['MTG']['toc_reflectance']['band2']['filenames'] = apid['INPUT_RESOURCES']['TOC_REFLECTANCE_BAND2']['file_paths']
    pyal2['input']['MTG']['toc_reflectance']['band3']['filenames'] = apid['INPUT_RESOURCES']['TOC_REFLECTANCE_BAND3']['file_paths']
    pyal2['input']['MTG']['toc_reflectance_cov']['band1']['filenames'] = apid['INPUT_RESOURCES']['TOC_REFLECTANCE_COV_BAND1']['file_paths']
    pyal2['input']['MTG']['toc_reflectance_cov']['band2']['filenames'] = apid['INPUT_RESOURCES']['TOC_REFLECTANCE_COV_BAND2']['file_paths']
    pyal2['input']['MTG']['toc_reflectance_cov']['band3']['filenames'] = apid['INPUT_RESOURCES']['TOC_REFLECTANCE_COV_BAND3']['file_paths']
       
    pyal2['input']['MTG']['inputcheckpoint']['filenames']['band1']['values'] = apid['INPUT_RESOURCES']['INPUTCHECKPOINT_BAND1']['file_paths']
    pyal2['input']['MTG']['inputcheckpoint']['filenames']['band2']['values'] = apid['INPUT_RESOURCES']['INPUTCHECKPOINT_BAND2']['file_paths']
    pyal2['input']['MTG']['inputcheckpoint']['filenames']['band3']['values'] = apid['INPUT_RESOURCES']['INPUTCHECKPOINT_BAND3']['file_paths']
    
    pyal2['input']['MTG']['inputcheckpoint']['filenames']['band1']['cov'] = apid['INPUT_RESOURCES']['INPUTCHECKPOINT_BAND1_COV']['file_paths']
    pyal2['input']['MTG']['inputcheckpoint']['filenames']['band2']['cov'] = apid['INPUT_RESOURCES']['INPUTCHECKPOINT_BAND2_COV']['file_paths']
    pyal2['input']['MTG']['inputcheckpoint']['filenames']['band3']['cov'] = apid['INPUT_RESOURCES']['INPUTCHECKPOINT_BAND3_COV']['file_paths']
    
    # Broadband
    pyal2['input']['MTG']['output']['albedo']['filename'] = apid['OUTPUT_RESOURCES']['ALBEDO_BB']['file_paths']
    pyal2['input']['MTG']['output']['albedo']['cov'] = apid['OUTPUT_RESOURCES']['ALBEDO_BB_COV']['file_paths']
    
    # Spectral Albedo
    pyal2['input']['MTG']['output']['albedo-sp']['band1']['filename'] = apid['OUTPUT_RESOURCES']['RAD_VIS06']['file_paths']
    pyal2['input']['MTG']['output']['albedo-sp']['band2']['filename'] = apid['OUTPUT_RESOURCES']['RAD_VIS08']['file_paths']
    pyal2['input']['MTG']['output']['albedo-sp']['band3']['filename'] = apid['OUTPUT_RESOURCES']['RAD_NIR16']['file_paths']
    pyal2['input']['MTG']['output']['albedo-sp']['band1']['cov'] = apid['OUTPUT_RESOURCES']['RAD_VIS06_COV']['file_paths']
    pyal2['input']['MTG']['output']['albedo-sp']['band2']['cov'] = apid['OUTPUT_RESOURCES']['RAD_VIS08_COV']['file_paths']
    pyal2['input']['MTG']['output']['albedo-sp']['band3']['cov'] = apid['OUTPUT_RESOURCES']['RAD_NIR16_COV']['file_paths']
    
    # BRDF
    pyal2['input']['MTG']['output']['brdf']['band1']['filename'] = apid['OUTPUT_RESOURCES']['BRDF_VIS06']['file_paths']
    pyal2['input']['MTG']['output']['brdf']['band2']['filename'] = apid['OUTPUT_RESOURCES']['BRDF_VIS08']['file_paths']
    pyal2['input']['MTG']['output']['brdf']['band3']['filename'] = apid['OUTPUT_RESOURCES']['BRDF_NIR16']['file_paths']
    pyal2['input']['MTG']['output']['brdf']['band1']['cov'] = apid['OUTPUT_RESOURCES']['BRDF_VIS06-d01']['file_paths']
    pyal2['input']['MTG']['output']['brdf']['band2']['cov'] = apid['OUTPUT_RESOURCES']['BRDF_VIS08-d01']['file_paths']
    pyal2['input']['MTG']['output']['brdf']['band3']['cov'] = apid['OUTPUT_RESOURCES']['BRDF_NIR16-d01']['file_paths']
    
    # BRDF_COV
    pyal2['input']['MTG']['output']['brdf-d01']['band1']['filename'] = apid['OUTPUT_RESOURCES']['BRDF_VIS06_COV']['file_paths']
    pyal2['input']['MTG']['output']['brdf-d01']['band2']['filename'] = apid['OUTPUT_RESOURCES']['BRDF_VIS08_COV']['file_paths']
    pyal2['input']['MTG']['output']['brdf-d01']['band3']['filename'] = apid['OUTPUT_RESOURCES']['BRDF_NIR16_COV']['file_paths']
    pyal2['input']['MTG']['output']['brdf-d01']['band1']['cov'] = apid['OUTPUT_RESOURCES']['BRDF_VIS06-d01_COV']['file_paths']
    pyal2['input']['MTG']['output']['brdf-d01']['band2']['cov'] = apid['OUTPUT_RESOURCES']['BRDF_VIS08-d01_COV']['file_paths']
    pyal2['input']['MTG']['output']['brdf-d01']['band3']['cov'] = apid['OUTPUT_RESOURCES']['BRDF_NIR16-d01_COV']['file_paths']
    
    # LWCS
    pyal2['input']['MTG']['lwcs_mask']['band1']['filenames'] = apid['INPUT_RESOURCES']['TOC_REFLECTANCE_BAND1']['file_paths']
    pyal2['input']['MTG']['lwcs_mask']['band2']['filenames'] = apid['INPUT_RESOURCES']['TOC_REFLECTANCE_BAND2']['file_paths']
    pyal2['input']['MTG']['lwcs_mask']['band3']['filenames'] = apid['INPUT_RESOURCES']['TOC_REFLECTANCE_BAND3']['file_paths']
                 
    # writing the new pcf file at the pyal2 format:

    logging.debug('we are about to write')
    
    with open(outputname, 'w') as file:
        documents = yaml.dump(pyal2, file)
        
    logging.info(' End of process ')
        
def main():
    args = parse_args()
    
    empty_file = args.empty_file
    
    # Transform format pyal2 to a pcf file format APID
    if args.pyal22apid:
        
        outputname = args.pcf_apid_name
        inputname = args.pcf_pyal2_name
        try:
            pyal22apid(inputname, outputname, empty_file)
        except:
            logging.error('reading pyal2 and writing the apid pcf file was problematic')
            
    # Transform apid format to pyal2 format
    elif args.apid2pyal2:
        
        inputname = args.pcf_apid_name
        outputname = args.pcf_pyal2_name
        try:
            apid2pyal2(inputname, outputname, empty_file)
        except:
            logging.error('reading apid and writing the pyal2 pcf file was problematic')
        
if __name__ == "__main__":
    main()

