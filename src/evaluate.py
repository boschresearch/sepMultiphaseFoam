#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 14:13:28 2024

@author: npa7si
"""

import pandas as pd
import os, re
import numpy as np
import warnings
import modules as md
from ast import literal_eval

class evaluation:
    def __init__(self, work_env, csv_filename):
        self.case_name = work_env.case_name
        self.sim_path = work_env.sim_path()
        self.evap_rate_csv_path = work_env.evap_rate_csv_path()
        self.dec_file_path = work_env.dec_file_path()
        self.of_sims_path = work_env.of_sims_path()
        
        if isinstance(csv_filename, bool):
            self.csv_filename = f'evaluation_{os.path.basename(work_env.work_dir())}.csv'
        else:
            if csv_filename.lower().endswith('.csv'):
                self.csv_filename = csv_filename
            else:
                self.csv_filename = f'{csv_filename}.csv'
        
    def __call__(self):
        self.eval_data = md.get_eval_data(self.evap_rate_csv_path, self.dec_file_path)
        self._add_therm_props_to_dict()
        self._eval_evap_rate()
        self._eval_runtime()
        self._write_eval_data()
        
    def _add_therm_props_to_dict(self):
        therm_props = md.ThermodynamicalProperties(self.eval_data['T'], self.eval_data['RH'])
        _, _, Y_v_avg = therm_props.get_mass_fractions()
        self.eval_data['rho'] = therm_props.get_density(Y_v_avg)
    
    def _write_eval_data(self):
        self.eval_data.to_csv(f'{self.evap_rate_csv_path}/{self.csv_filename}', index=False)
    
    def _eval_evap_rate(self):
        for idx, sim_case_dir in enumerate(self.eval_data['sim_case']):
            sim_case_dir_path = f'{self.of_sims_path}/{sim_case_dir}'
            env_diff_flux_path = f'{sim_case_dir_path}/postProcessing/diffFluxRate/0/surfaceFieldValue.dat'
            
            try:
                with open(env_diff_flux_path, 'r') as f:
                    env_diff_flux_file_content = f.read()
                
                env_diff_flux = re.search('\((.*) (.*) (.*)\)', env_diff_flux_file_content)
                if env_diff_flux:
                    env_diff_flux = np.array([env_diff_flux.group(1), env_diff_flux.group(2), env_diff_flux.group(3)])
                    self.eval_data.loc[self.eval_data['sim_case'] == sim_case_dir, 'm_dot/rho_env'] = np.linalg.norm(env_diff_flux)
                    self.eval_data.loc[self.eval_data['sim_case'] == sim_case_dir, 'm_dot'] = np.linalg.norm(env_diff_flux)*self.eval_data.loc[self.eval_data['sim_case'] == sim_case_dir, 'rho']
                else:
                    warnings.warn(f'Couldnt find env_diff_flux in {env_diff_flux_path}')
            except:
                self.eval_data.loc[self.eval_data['sim_case'] == sim_case_dir, 'm_dot/rho_env'] = ''
                warnings.warn(f'Couldnt open {env_diff_flux_path}')
                continue
        
    def _eval_runtime(self):
        protocol_files = os.listdir(self.sim_path)
        
        # separate protocol files depending on executed program
        surfaceevolver_protocol_files = [file for file in protocol_files if 'evolver' in file and 'protokoll' in file]
        premeshing_protocol_files = [file for file in protocol_files if 'preMeshing' in file and 'protokoll' in file]
        snappyhexmesh_protocol_files = [file for file in protocol_files if 'snappyHexMesh' in file and 'protokoll' in file]
        allrun_protocol_files = [file for file in protocol_files if 'Allrun' in file and 'protokoll' in file]
        
        print()
        
        # get separate runtimes from protocol files
        self._add_protocol_runtime(
            surfaceevolver_protocol_files,
            'evolver')
        self._add_protocol_runtime(
            premeshing_protocol_files,
            'premeshing')
        self._add_protocol_runtime(
            snappyhexmesh_protocol_files,
            'snappyhexmesh')
        self._add_protocol_runtime(
            allrun_protocol_files,
            'allrun')
        
        try:
            self.eval_data['total_runtime'] = (
                self.eval_data['premeshing_runtime']
                + self.eval_data['snappyhexmesh_runtime']
                + self.eval_data['allrun_runtime'])
        
        except:
            warnings.warn('Couldnt retrieve runtimes from protocol files. Protocol files are either faulty or missing.')

    def _add_protocol_runtime(self, protocol_filenames, protocol_type):
        for protocol_filename in protocol_filenames:
            try:
                with open(f'{self.sim_path}/{protocol_filename}', 'r') as f:
                    protocol_file_content = f.read()
            except:
                warnings.warn(f'Couldnt open {self.sim_path}/{protocol_filename}')
                continue
            
            matching_groups = re.search(f'Application commands:(?:.*)({self.case_name}_\d+_?\d*)(?:.*)JOB SUMMARY(?:.*)RUN_TIME(?:.*)= (\d+) sec\.\nTURNAROUND', protocol_file_content, flags=re.DOTALL)
                
            if matching_groups:
                simCase = matching_groups.group(1)
                runtime = int(matching_groups.group(2))
                if protocol_type == 'evolver':
                    self.eval_data.loc[self.eval_data['se_filename'] == simCase, f'{protocol_type}_runtime'] = runtime
                else:
                    self.eval_data.loc[self.eval_data['sim_case'] == simCase, f'{protocol_type}_runtime'] = runtime
            else:
                raise LookupError(f'Couldnt find {protocol_type}_runtime in {self.sim_path}/{protocol_filename}')