#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 12:55:48 2024

@author: npa7si
"""

import re
import os
import modules as md
import setupWorkEnv as swe
import subprocess
import config


class SetupSims():
    # Constructor
    def __init__(self, fesig):
        # get reference to fastEvaporationSimInGaps class object
        # to access its attributes
        self.fesig = fesig
        self.config = config.Config()

        # get necessary path strings from working environment
        self.calc_routine_path = self.fesig.work_env.calc_routine_path()
        self.se_out_files_path = self.fesig.work_env.se_out_files_path()
        self.fes_files_path = self.fesig.work_env.fes_files_path()
        self.fes_template_path = self.fesig.work_env.fes_template_path()
        self.stl_files_path_sim = self.fesig.work_env.stl_files_path_sim()
        self.sim_path = self.fesig.work_env.sim_path()

    def _replace_param_in_str(self, param_name, param_val, str_old):
        '''
        Replace a parameter placeholder in a string with a specified value
        and return the changed string.
        '''
        str_new = re.sub(f'\|-{param_name}-\|', str(param_val), str_old)
        return str_new

    def _replace_params_in_files(
            self,
            path_old,
            path_new,
            param_name_set,
            param_vector
            ):
        with open(path_old, 'r') as f:
            file_content = f.read()

        for param_name in param_name_set:
            file_content = self._replace_param_in_str(
                param_name,
                param_vector[param_name],
                file_content
                )

        with open(path_new, 'w') as f:
            f.write(file_content)

    def atoi(self, text):
        return int(text) if text.isdigit() else text

    def natural_keys(self, text):
        '''
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        '''
        return [self.__atoi(c) for c in re.split(r'(\d+)', text)]

    def run(self):
        raise NotImplementedError


class SetupSE(SetupSims):
    # Constructor
    def __init__(self, fesig):
        super().__init__(fesig)

        # get Surface Evolver parameters from base class
        self.se_param_vectors = fesig.se_param_vectors

    def _create_se_cases(self):
        '''
        Creates Surface Evolver cases based on parameter combinations in parameter
        vector. Additionally creates start script to start SE simulations.

        Returns
        -------
        startscript : string
            Start script with all necessary commands to start the SE simulations.

        '''
        startscript = ''

        # get content of .fe template file
        with open(self.fes_template_path, 'r') as f:
            se_template_content = f.read()

        # main loop to create fes files and replace parameter placeholders
        # CHANGE STARTSCRIPT ACCORDING TO YOUR SYSTEM
        for se_param_vector in self.se_param_vectors:
            se_filename = se_param_vector['se_filename']
            startscript += (f'''subbin -n {self.config.get_val("N_CORES_SE")} '''
                            f'''-N {self.config.get_val("N_CORESPERNODE_SE")} '''
                            f'''-r {self.config.get_val("RUNTIME_SE")} '''
                            f'''-m "{self.config.get_val('MEMORY_SE')}G" '''
                            '''--write-end-file '''
                            f'''--end-file-name={se_filename}_SE_finished '''
                            f'''-I "evolver -f {self.calc_routine_path}/calcRoutine {self.fes_files_path}/{se_filename}.fes &> {self.se_out_files_path}/{se_filename}.out"\n'''
                            )
            se_template_content_tmp = se_template_content
            
            # parameters are changed in the given .fe file
            for k,v in se_param_vector.items():
                se_template_content_tmp = super()._replace_param_in_str(k, v, se_template_content_tmp)
            
            # add initial refinement at the start of simulation
            # SE-FIT algorithm shows bad behavior for round capillaries w/o
            # this initial refinement
            se_template_content_tmp += f'\nread\n\nstl_filename := "{se_filename}"\nr\nr\nr\ng100\n\n'
            
            # write .fes file
            with open(f'{self.fes_files_path}/{se_filename}.fes','w') as f:
                f.write(se_template_content_tmp)
        return startscript
    
    def _write_startscript(self, startscript):
        '''
        Write start script to file and change file mode to executable.
        '''
        with open(f'{self.sim_path}/startSEsimulations.sh','w') as f:
            f.write(startscript)
        subprocess.run(f'chmod +x {self.sim_path}/startSEsimulations.sh', shell=True)
    
    # run has to be implemented by child classes
    def run(self):
        startscript = self._create_se_cases()
        self._write_startscript(startscript)


class SetupOF(SetupSims):
    # Constructor
    def __init__(self, fesig):
        super().__init__(fesig)
        
        # startscript contains all commmands the shell has to execute
        self.startscript = '#!/bin/sh'
        
        # get names of OpenFOAM cases from parameter vectors dictionary
        self.of_case_names = fesig.param_vectors.keys()
        
        # get path to OpenFOAM case template and OpenFOAM simulation directory
        self.of_template_path = fesig.work_env.of_template_path()
        self.of_sims_path = fesig.work_env.of_sims_path()
        self.create_enclosure_stl_path = fesig.work_env.create_enclosure_stl_path()
    
    def _create_enclosure_stl(self, shape):
        md.print_info_msg(f'Creating enclosure STL for {shape} shape')
        params_in_template = self._get_of_template_params(f'{self.createEnclosureSTLPath}/{shape}')
        for filepath, params_in_file in params_in_template.items():
            path_to_file = f'{self.create_enclosure_stl_path}/{shape}/{filepath}'
        subprocess.run('./createGeomAndExportSTL.sh', shell=True, cwd=f'{self.create_enclosure_stl_path}/{shape}')
        
        # check if enclosure STL exists
        assert 'enclosure.stl' in os.listdir(f'{self.create_enclosure_stl_path}/{shape}'), f'enclosure.stl not found in {self.create_enclosure_stl_path}/{shape}'
        subprocess.run(f'cp {self.create_enclosure_stl_path}/{shape}/enclosure.stl {self.of_template_path}/constant/triSurface/enclosure.stl', shell=True)
        subprocess.run('./Allclean.sh', shell=True, cwd=f'{self.create_enclosure_stl_path}/{shape}')
        
    def _get_of_template_params(self, path_to_template):
        '''
        Searches for all parameters in the OpenFOAM template case.

        Returns
        -------
        paramsInTemplate : dict
            All parameters that occur in the OpenFOAM template case and the
            associated filepath where the parameter occurs.

        '''
        params_in_template_dict = {}
        
        # get files that contain parameter start character |-
        output = subprocess.run('grep -rn "." -e "|-"', shell=True, cwd=path_to_template, capture_output=True)
        output = output.stdout.decode('utf-8')
        for output_line in output.splitlines():
            filepath = re.search('(\.\/.*):(?:\d+):.*\|-(.*)-\|', output_line).group(1)
            params = re.findall('\|-(.*?)-\|', output_line)
            params_in_template_dict.setdefault(filepath,[]).append(params)
        
        # get a dictionary of shape: {filepath: [unique parameter list]} to know
        # in which file which parameters occur
        params_in_template_dict = {filepath: set([params for paramss in paramsss for params in paramss]) for (filepath, paramsss) in params_in_template_dict.items()}
        return params_in_template_dict
    
    def _create_of_cases(self):
        '''
        Creates a set of OpenFOAM dictionaries originating from the given OpenFOAM
        template case. Further, the corresponding SE STL files are copied to the
        dictionaries and a start script is created.

        Returns
        -------
        startscript : string
            Start script with all necessary commands to start the OF simulations.

        '''
        startscript = ''
        for of_case_name, param_vector in self.fesig.param_vectors.items():
            # get thermodynamical properties and append to global parameter vector
            therm_props = md.ThermodynamicalProperties(param_vector['T'], param_vector['RH'])
            Y_v, Y_v_sat, Y_v_avg = therm_props.get_mass_fractions()
            rho_avg = therm_props.get_density(Y_v_avg)
            D = therm_props.get_diff_coeff()
            param_vector['Y_V'] = Y_v
            param_vector['Y_V_SAT'] = Y_v_sat
            param_vector['RHO_AVG'] = rho_avg
            param_vector['D'] = D
            
            # temporary path to OpenFOAM case
            of_case_path = f'{self.of_sims_path}/{of_case_name}'
            of_case_se_filename = self.fesig.param_vectors[of_case_name]['se_filename']
            startscript += f'\n{of_case_path}/jobscript.sh'
            
            # copy template to various directories in SIM folder
            subprocess.run(f'cp -r {self.of_template_path}/. {of_case_path}', shell=True)
            
            # copy scaled STL files to specific OpenFOAM case directory
            subprocess.run(f'cp {self.fesig.work_env.stl_files_scld_path()}/{of_case_se_filename}.stl {of_case_path}/constant/triSurface/', shell=True)
        
        return startscript
    
    def _replace_params(self, params_in_template):
        '''
        Replace the parameters in the respective files according to the
        params_in_template dictionary.

        Parameters
        ----------
        params_in_template : dict
            All parameters that occur in the OpenFOAM template case and the
            associated filepath where the parameter occurs.

        Returns
        -------
        None.

        '''
        for of_case_name, param_vector in self.fesig.param_vectors.items():
            # parameter dictionary accounts for parameters that have different names
            # in parameter dictionary and template
            param_dict = {'STL_FILENAME': param_vector['se_filename'],
                          'OFDIRNAME': of_case_name}
            param_dict |= config.Config().as_dict()
            
            # temporary path to OpenFOAM case
            of_case_path = f'{self.of_sims_path}/{of_case_name}'
            
            for filepath, params_in_file in params_in_template.items():
                # paramInTemplate (tuple) = (path, params)
                path_to_file = f'{of_case_path}/{filepath}'
                
                with open(path_to_file,'r') as f:
                    file_content = f.read()
                
                for param_in_file in params_in_file:
                    try:
                        # executed if parameter in paramVector is the same as
                        # parameter in file
                        file_content = super()._replace_param_in_str(param_in_file, param_vector[param_in_file], file_content)
                    except:
                        # accounts for parameters that are not contained in parameter vector
                        file_content = super()._replace_param_in_str(param_in_file, param_dict[param_in_file], file_content)
                
                with open(path_to_file,'w') as f:
                    f.write(file_content)
    
    def _write_startscript(self, startscript):
        '''
        Write start script to file and change file mode to executable.
        '''
        # write startscript file
        with open(f'{self.sim_path}/startOFsimulations.sh','w') as f:
            f.write(startscript)
        subprocess.run(f'chmod +x {self.sim_path}/startOFsimulations.sh', shell=True)
    
    # run has to be implemented by child classes
    def run(self):
        # shape = 'round'
        # self.__createEnclosureSTL(shape)
        params_in_template = self._get_of_template_params(self.of_template_path)
        startscript = self._create_of_cases()
        self._replace_params(params_in_template)
        self._write_startscript(startscript)
        
class ScaleSTLFiles(SetupSims):
    def __init__(self, fesig, scale=1.01):
        super().__init__(fesig)
        self.scale = scale
        
    def _scale_stl(self):
        '''
        Scale STL from SE up by a small amount in order to assure that the surface
        cuts the outer geometry.
        '''
        stl_files = os.listdir(self.stl_files_path_sim)
        stl_files = [stl_file for stl_file in stl_files if stl_file.endswith('.stl')]
        self.fesig.work_env.stl_files_scld_path = swe.WorkEnvPath(f'{self.fesig.work_env.sim_path()}/stlFilesScld')
        self.stl_files_scld_path = self.fesig.work_env.stl_files_scld_path.path
        
        for stl_file in stl_files:
            stl_filename = stl_file[:-4]
            scale_status = md.mesh_scale_and_export(self.stl_files_path_sim, self.stl_files_scld_path, stl_filename, self.scale)
            if not scale_status:
                print(f'Error in STL scaling for file {stl_file}!')
    
    def run(self):
        self._scale_stl()
