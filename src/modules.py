#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 09:15:55 2024

@author: npa7si
"""
import itertools
import numpy as np
import trimesh as tm
from ast import literal_eval
import argparse
import re, os
import pandas as pd

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def get_combinations(D):
    '''
    DESCRIPTION:
        Generate all combinations of values from a dictionary.
        This function takes a dictionary as input and returns a list of dictionaries.
        Each dictionary in the list represents a unique combination of values from the input dictionary.

    INPUT:
        D [dict]: A dictionary containing keys and corresponding lists of values.

    OUTPUT:
        result [list]: A list of dictionaries, where each dictionary represents a unique combination of values from the input dictionary.
    '''
    keys = D.keys()
    values = D.values()
    combinations = list(itertools.product(*values))
    result = [dict(zip(keys, combination)) for combination in combinations]
    return result

def get_param_vectors(param_dict_path, dec_file_path, case_name, sim_status_dict_path):
    '''
    Subdivides parameter dictionary into parameters that are necessary for
    the Surface Evolver and parameters that are necessary for OpenFOAM.
    All combinations between the different parameters are generated and
    written to a new dictionary.

    Returns
    -------
    seParamVectors : dictionary
        Contains all parameter vectors for Surface Evolver. This parameter
        set is written seperately to avoid equal simulations for different
        OpenFOAM parameter sets.
    paramVectors : dictionary
        Contains all possible combinations between any SE and OF parameters.
        A unique case name and the related stl file name are given in this

    '''
    with open(param_dict_path, 'r') as f:
        content = f.read()
        params = literal_eval(content)
    
    # Subdivide parameter dictionary into SE parameters and OF parameters
    se_params = {k: v['vals'] for k,v in params.items() if v['prog_flag']=='se'}
    of_params = {k: v['vals'] for k,v in params.items() if v['prog_flag']=='of'}
    se_param_vectors = get_combinations(se_params)
    of_param_vectors = get_combinations(of_params)
    
    # initialize dictionaries for simulation status and parameter vectors
    sim_status_dict = {
        'SE':{
            'se_filename':[],
            'sim_finished':[],
            'sim_status_code':[],
            'sim_success':[]},
        'OF':{
            'of_dirname':[],
            'sim_finished':[],
            'sim_status_code':[],
            'sim_success':[]
            }
        }
    
    param_vectors = {}
    
    for i, se_param_vector in enumerate(se_param_vectors):
        se_param_vector |= {'se_filename': f'{case_name}_{i}'}
        sim_status_dict['SE']['se_filename'].append(f'{case_name}_{i}')
        sim_status_dict['SE']['sim_finished'].append(False)
        sim_status_dict['SE']['sim_status_code'].append(None)
        sim_status_dict['SE']['sim_success'].append(False)
        
        for ii, of_param_vector in enumerate(of_param_vectors):
            tmp_dict = se_param_vector | of_param_vector
            param_vectors[f'{case_name}_{i}_{ii}'] = tmp_dict
            sim_status_dict['OF']['of_dirname'].append(f'{case_name}_{i}_{ii}')
            sim_status_dict['OF']['sim_finished'].append(False)
            sim_status_dict['OF']['sim_status_code'].append(None)
            sim_status_dict['OF']['sim_success'].append(False)
    
    # decode file
    dec_file_content = str(param_vectors)
    dec_file_content = re.sub('\A\{', '{\n',dec_file_content)
    dec_file_content = re.sub('\}, ', '},\n',dec_file_content)
    dec_file_content = re.sub('\}\}', '}\n}',dec_file_content)
    with open(dec_file_path, 'w') as f:
        f.write(dec_file_content)
    
    # sim_status_dict file
    with open(sim_status_dict_path, 'w') as f:
        f.write(str(sim_status_dict))
        
    return param_vectors, se_param_vectors, of_param_vectors

def update_sim_status_dict(sim_path, sim_status_dict_path):
    '''
    Update simulation status dict
    '''
    with open(f'{sim_path}/simStatus', 'r') as f:
        content = f.read()
        sim_status_dict = literal_eval(content)
        
    # get finish files from SIM directory
    sim_finish_files = os.listdir(sim_path)
    se_finish_files = [sim_finish_file for sim_finish_file in sim_finish_files if sim_finish_file.endswith('SE_finished')]
    of_finish_files = [sim_finish_file for sim_finish_file in sim_finish_files if sim_finish_file.endswith('OF_finished')]
    stl_files = os.listdir(f'{sim_path}/stlFiles')
    
    for se_finish_file in se_finish_files:
        with open(f'{sim_path}/{se_finish_file}', 'r') as f:
            sim_status_code = int(f.read())
        idx = sim_status_dict['SE']['se_filename'].index(se_finish_file[:-12])
        sim_status_dict['SE']['sim_finished'][idx] = True
        sim_status_dict['SE']['sim_status_code'][idx] = sim_status_code
        if f'{se_finish_file[:-12]}.stl' not in stl_files:
            sim_status_dict['SE']['sim_status_code'][idx] = 1
        if sim_status_code==0:
            sim_status_dict['SE']['sim_success'][idx] = True
    
    for of_finish_file in of_finish_files:
        with open(f'{sim_path}/{of_finish_file}', 'r') as f:
            sim_status_code = int(f.read())
        idx = sim_status_dict['OF']['of_dirname'].index(of_finish_file[:-12])
        sim_status_dict['OF']['sim_finished'][idx] = True
        sim_status_dict['OF']['sim_status_code'][idx] = sim_status_code
        if sim_status_code==0:
            sim_status_dict['OF']['sim_success'][idx] = True
            
    # write sim_status_dict back to file
    with open(sim_status_dict_path, 'w') as f:
        f.write(str(sim_status_dict))
    
    return sim_status_dict

def eval_sim_status(sim_status_dict, program, sim_started):
    # get total number of simulations, finished sims and faulty sims
    sim_finished = np.array(sim_status_dict['sim_finished'])
    sim_success = np.array(sim_status_dict['sim_success'])
    n_sims = len(sim_finished)
    n_finished_sims = list(sim_finished & sim_success).count(True)
    n_faulty_sims = list(sim_finished & np.logical_not(sim_success)).count(True)
    
    match n_finished_sims:
        case 0:
            if sim_started:
                status_code = 1
                status_msg = f'{program} simulations started but no simulation finished yet.'
            else:
                status_code = 0
                status_msg = f'{program} simulations not initialized. Continuing with initialization.'
        case n_finished_sims if n_finished_sims > 0 and n_finished_sims < n_sims:
            status_code = 2
            status_msg = f'{program}: Current progress {n_finished_sims}/{n_sims} ({n_finished_sims/n_sims*100:.1f}%)'
        case n_stl_files_tot:
            status_code = 3
            status_msg = f'{program} simulations finished.'
    return status_code, status_msg

def get_sim_status(sim_path, sim_status_dictPath, se_sim_started, of_sim_started):
    # check if simulations already started based on protokoll files
    sim_status_dict = update_sim_status_dict(sim_path, sim_status_dictPath)
    se_status_code, se_status_msg = eval_sim_status(sim_status_dict['SE'], 'SE', se_sim_started)
    of_status_code, of_status_msg = eval_sim_status(sim_status_dict['OF'], 'OF', of_sim_started)
    return (se_status_code, se_status_msg, of_status_code, of_status_msg)


class ThermodynamicalProperties:
    def __init__(self, T, RH, p=101325, M_v=0.018015275, M_a=0.0289586):
        self._T = T
        self._RH = self._test_RH_input(RH)
        self._p = p
        self._M_v = M_v
        self._M_a = M_a
        
        # universal gas constant [J/mol/K]
        self._R = 8.31446261815324
    
    def get_mass_fractions(self):
        '''
        Calculates the current vapor mass fraction (Y_v), the saturation vapor
        mass fraction (Y_v_sat) and their average value (Y_v_avg)
        '''
        p_sat = self._p_sat()
        X_v_sat = p_sat/self._p
        X_v = X_v_sat*self._RH
        
        Y_v_sat = self._X_to_Y(X_v_sat)
        Y_v = self._X_to_Y(X_v)
        Y_v_avg = (Y_v+Y_v_sat)/2
        return Y_v, Y_v_sat, Y_v_avg
    
    def get_diff_coeff(self):
        '''
        Calculates the diffusion coefficient in m^2/s for vapor in air for a
        specified temperature and pressure according to the Fuller method from
        VDI-Waermeatlas.
        '''
        # diffusion volumes according to VDI-Waermeatlas for water vapor and air
        del_v = 13.1
        del_a = 19.7
        D = 0.0143*self._T**1.75 * np.sqrt(1/(self._M_v*1e3)+1/(self._M_a*1e3))/(self._p*np.sqrt(2)*(del_v**(1/3)+del_a**(1/3))**2)
        return D
    
    def get_density(self, Y_v):
        '''
        Calculates density in kg/m^3 for any arbitrary vapor mass fraction in
        air according to the ideal gas law.
        '''
        X_v = self._Y_to_X(Y_v)
        M_mxd = X_v*self._M_v+(1-X_v)*self._M_a
        return self._p*M_mxd/(self._R*self._T)
        
    def _test_RH_input(self, RH):
        if type(RH) == float:
            if RH > 1 and RH < 100:
                # convert RH to float if given in percentage
                return RH / 100
            elif RH < 0 or RH > 100:
                raise ValueError('RH must be between 0 and 100. 0<=RH<=1 are treated as floats and 1<RH<100 are treated as percentages.')
            else:
                return RH
        else:
            if RH.all() > 1 and RH.all() < 100:
                # convert RH to float if given in percentage
                return RH / 100
            elif RH.any() < 0 or RH.any() > 100:
                raise ValueError('RH must be between 0 and 100. 0<=RH<=1 are treated as floats and 1<RH<100 are treated as percentages.')
            else:
                return RH
    
    def _test_T_input(self, T):
        if type(T) == float:
            if T >= 0 and T <= 100:
                return T + 273.15
            elif T < 273.15 or T > 373.15:
                raise ValueError('T must be between 0 °C/273.15 K and 100 °C/373.15 K')
            else:
                return T
        else:
            if T.all() >= 0 and T.all() <= 100:
                return T + 273.15
            elif T.any() < 273.15 or T.any() > 373.15:
                raise ValueError('T must be between 0 °C/273.15 K and 100 °C/373.15 K')
            else:
                return T
    
    def _p_sat(self, A = 23.4751, B = 3978.205, C = -39.801):
        '''
        calculate saturation vapor pressure at given temperature T
        according to \cite[p.209]{reid_properties_1987}. Antoine coefficients
        are default for water.
        '''
        pSat = np.exp(A-B/(self._T+C))
        return pSat
    
    def _Y_to_X(self, Y):
        '''
        Convert mass fraction to mole fraction.
        '''
        return Y/self._M_v/(Y/self._M_v+(1-Y)/self._M_a)
    
    def _X_to_Y(self, X):
        '''
        Convert mole fraction to mass fraction.
        '''
        return X*self._M_v/((1-X)*self._M_a+X*self._M_v)


def mesh_scale_and_export(work_dir, out_dir, stl_filename, scale):
    '''
    Scale stl mesh according to scale factor and save the scaled mesh in
    different file.

    Parameters
    ----------
    work_dir : string
        Working directory.
    out_dir : string
        Output directory.
    stl_filename : string
        STL filename.
    scale : float
        Scale factor.

    Returns
    -------
    bool
        True if scaling was successful. False if scaling failed.
    '''
    try:
        # load STL file and mesh
        mesh = tm.load_mesh(f'{work_dir}/{stl_filename}.stl')
        
        # translate stl to (0,0,0)
        translation_matrix = np.eye(4)
        stl_origin = mesh.centroid
        translation_matrix[:2,3] = -stl_origin[:2]
        
        # scale stl around (0,0,0)
        scale_matrix = np.eye(4)
        scale_vector = np.array([scale, scale, 1])
        scale_matrix[:3, :3] = scale_matrix[:3, :3]*scale_vector
        
        # translate stl back to original centroid
        back_translation_matrix = np.eye(4)
        back_translation_matrix[:2,3] = stl_origin[:2]
        
        # combine translation and scaling matrices
        transformation_matrix = np.dot(
            np.dot(back_translation_matrix, scale_matrix), translation_matrix
            )
        
        # apply transformation matrix
        mesh_scld = mesh.apply_transform(transformation_matrix)
        mesh_scld.export(f'{out_dir}/{stl_filename}.stl', file_type='stl')
        
        return True
    except:
        return False

# set argument either to True if no argument is passed and to the given string if string is passed
class TrueOrString(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            setattr(namespace, self.dest, True)
        else:
            setattr(namespace, self.dest, values)

def init_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '-d', '--debug', 
        type=int, default=0, 
        help='0=no debug, 1=debug tutorial case'
        )
    
    parser.add_argument(
        '-s', '--sim', 
        nargs='?', const=True, default=False, action=TrueOrString, 
        help='Start simulation. Add SE or OF flag to start either Surface Evolver or OpenFOAM seperately.'
        )
    
    parser.add_argument(
        '-n', '--new', action='store_true', 
        help='Create new case and directories with given name.'
        )
    
    parser.add_argument(
        '-c', '--clear', action='store_true', 
        help='Clear case (deletes SIM and OUTPUT folder)'
        )
    
    parser.add_argument(
        '-e', '--eval', nargs='?', const=True, default=False, action=TrueOrString, 
        help='Evaluate evaporation rate and runtime, optional: csv filename where results are written'
        )
    
    parser.add_argument(
        '-v', '--vis',
        nargs='?', const=True, default=False, action=TrueOrString, 
        help='Visualize variables that were previously evaluated. Argument must be variable names to be plotted from the corresponding csv file, separated by commas.'
        )
    
    return parser

def print_info_msg(msg):
    print(f'***INFO: {msg}')
    
def print_dbg_msg(msg):
    print(f'\n***DEBUG: {msg}\n')
    
def print_prog_header():
    header = '''
*******************************************************
***** Fast evaporation simulation in gaps (FESiG) *****
*******************************************************
** Author: Phil Namesnik
** Copyright: Copyright 2024, FESiG
** Version: 1.0.0
** Maintainer: Phil Namesnik
** Email: phil.namesnik@de.bosch.com
** Status: alpha
*******************************************************
** Arguments:
    -n, --new: Create new case and directories with given name
    -s, --sim: Start simulation
    -d, --debug: 0=no debug, 1=debug tutorial case
    -c, --clear: Clear case (deletes SIM and OUTPUT folder)
    -e, --eval: Evaluate evaporation rate and runtime, optional: csv filename where results are written
    -v, --vis: Visualize variables that were previously evaluated. Argument must be variable names to be plotted from the corresponding csv file, separated by commas. Default is "X_M,m_dot/rho_env"
    '''
    print(header)

def get_eval_data(evap_rate_csv_path, dec_file_path):
    path_content = os.listdir(evap_rate_csv_path)
    csv_files = [file for file in path_content if file.endswith('.csv')]
    
    if len(csv_files) == 1:
        print_info_msg(f'Found existing file {evap_rate_csv_path}/{csv_files[0]}. File is updated!')
        return pd.read_csv(f'{evap_rate_csv_path}/{csv_files[0]}')
    
    elif len(csv_files) > 1:
        print('Multiple csv files found.')
        for idx, csvFile in enumerate(csv_files):
            print(f'{idx+1}) {csvFile}')
            
        valid_file_idxs = list(range(len(csv_files)+1))[1:]
        file_idx = 0
        while file_idx not in valid_file_idxs:
            file_idx = input('Choose csv file to load: ')
        
        return pd.read_csv(f'{evap_rate_csv_path}/{csv_files[file_idx-1]}')
    else:
        print_info_msg('No saved csv files found. Continuing with new evaluation.')
        
        with open(dec_file_path, 'r') as f:
            content = f.read()
            sim_cases = literal_eval(content)
        
        eval_data = pd.DataFrame({'sim_case': sim_cases.keys()})
        
        for sim_case_name, sim_case_params in sim_cases.items():
            for sim_case_param, param_val in sim_case_params.items():
                eval_data.loc[eval_data['sim_case'] == sim_case_name, sim_case_param] = param_val
        
        return eval_data