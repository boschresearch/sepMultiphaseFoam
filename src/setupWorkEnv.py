#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 13:00:58 2024

@author: npa7si
"""

import os
from pathlib import Path

class WorkEnvPath:
    def __init__(self, path, is_dir=True):
        self._is_dir = is_dir
        self._path = self.create_path(path)
        
    def __call__(self):
        return self._path
    
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, path):
        self._path = self.create_path(path)
    
    def create_path(self, path):
        if not os.path.exists(path):
            if self._is_dir:
                print(f'Directory {os.path.basename(path)} created.')
                Path(path).mkdir(parents=True, exist_ok=True)
            else:
                print(f'File {os.path.basename(path)} created.')
                if not path.endswith('.pd'):
                    open(path, 'a').close()
                else:
                    with open(path, 'w') as f:
                        pdDfltText = "{\n\'PARAMETER_PLACEHOLDER\': {\'vals\': [0,1,2,3,...], \'prog_flag\':0},\n\'PARAMETER_PLACEHOLDER\': {\'vals\': [0,1,2,3,...], \'prog_flag\':'se'}\n}"
                        f.write(pdDfltText)
        return path
    
    @property
    def is_dir(self):
        return self._is_dir
    
    @is_dir.setter
    def is_dir(self, is_dir):
        assert isinstance(is_dir, bool), 'is_dir must be boolean'
        self._is_dir = is_dir

class WorkEnv:
    '''
    Creates file structure and assigns names to paths. Non-existing directories
    and files are created.
    '''
    def __init__(self, case_name, debug_flag):
        self.case_name = case_name
        
        # Initialize paths
        if debug_flag == 0:
            # working directory where program is executed
            self.work_dir = WorkEnvPath(f'{os.getcwd()}')
        elif debug_flag == 1:
            # fixed working directory for debugging!
            self.work_dir = WorkEnvPath(f'{os.environ["FESIGPATH"]}/tutorials/RoundCapillary')
        
        # system paths
        self.home_path = WorkEnvPath(os.path.expanduser('~'))
        self.calc_routine_path = WorkEnvPath(f'{self.home_path()}/evolver-2.70/lib')
        self.create_enclosure_stl_path = WorkEnvPath(f'{os.environ["FESIGPATH"]}/src/createEnclosureSTL')
        
        # parent directories in working directory
        self.input_path = WorkEnvPath(f'{self.work_dir()}/INPUT')
        self.sim_path = WorkEnvPath(f'{self.work_dir()}/SIM')
        self.output_path = WorkEnvPath(f'{self.work_dir()}/OUTPUT')
        
        # child directories/files in INPUT directory
        self.param_dict_path = WorkEnvPath(f'{self.input_path()}/{self.case_name}.pd', False)
        self.fes_template_path = WorkEnvPath(f'{self.input_path()}/{self.case_name}.fes', False)
        self.of_template_path = WorkEnvPath(f'{self.input_path()}/{self.case_name}_OF')
        
        # child directories/files in SIM directory
        self.dec_file_path = WorkEnvPath(f'{self.sim_path()}/{self.case_name}.dec', False)
        self.sim_status_dict_path = WorkEnvPath(f'{self.sim_path()}/simStatus', False)
        self.fes_files_path = WorkEnvPath(f'{self.sim_path()}/fesFiles')
        self.stl_files_path_sim = WorkEnvPath(f'{self.sim_path()}/stlFiles')
        self.se_out_files_path = WorkEnvPath(f'{self.sim_path()}/seOutFiles')
        self.of_sims_path = WorkEnvPath(f'{self.sim_path()}/ofSims')
        
        # child directories/files in OUTPUT directory
        self.stl_files_path_output = WorkEnvPath(f'{self.output_path()}/stlFiles')
        self.of_results_path = WorkEnvPath(f'{self.output_path()}/ofResults')
        self.evap_rate_csv_path = WorkEnvPath(f'{self.output_path()}/ofResults')