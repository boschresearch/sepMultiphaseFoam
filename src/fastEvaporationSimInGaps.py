#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 13:49:54 2024

@author: npa7si

Main script that starts the calculation.
"""

# basic imports
import os
import subprocess
import time

# import classes from other files
import setupWorkEnv as swe
import setupSims as ss
import evaluate as ev
import modules as md
import visualize as vis


class FastEvaporationSimInGaps:
    def __init__(self, case_name, debug_flag):
        # debug handling
        self.debug_flag = debug_flag
        if self.debug_flag == 0:
            self.case_name = case_name
        elif self.debug_flag == 1:
            # fixed case name from tutorials for debugging
            self.case_name = 'RoundCapillary'
        else:
            raise ValueError(
                'Debug flag is set to '
                + self.debug_flag
                + ' but can only have values 0, 1.'
                )

        # set up work envirnoment and set all necessary paths
        self.work_env = swe.WorkEnv(self.case_name, self.debug_flag)

        # get parameter vectors from parameter dictionary
        (self.param_vectors,
         self.se_param_vectors,
         self.of_param_vectors) = md.get_param_vectors(
             self.work_env.param_dict_path(),
             self.work_env.dec_file_path(),
             self.case_name,
             self.work_env.sim_status_dict_path()
             )

        # simulation status codes and messages
        self.se_status_code = 0
        self.se_status_msg = ''
        self.of_status_code = 0
        self.of_status_msg = ''
        self.se_sim_started = False
        self.of_sim_started = False

    def update_sim_status(self):
        '''
        Update current SE simulation status to decide when to continue with
        OpenFOAM simulations
        '''
        (self.se_status_code,
         self.se_status_msg,
         self.of_status_code,
         self.of_status_msg) = md.get_sim_status(
            self.work_env.sim_path(),
            self.work_env.sim_status_dict_path(),
            self.se_sim_started,
            self.of_sim_started)

    def __wait_state(self):
        self.update_sim_status()
        if self.se_status_code != 3 and self.se_sim_started:
            # SE simulations not finished
            md.print_info_msg(self.se_status_msg)
            time.sleep(10)
            self.__wait_state()
        else:
            if self.of_status_code != 3 and self.of_sim_started:
                # OF simulations not finished
                md.print_info_msg(self.of_status_msg)
                time.sleep(10)
                self.__wait_state()

    def run(self, sim_args):
        self.update_sim_status()

        if sim_args is True or sim_args == 'SE':
            if self.se_status_code == 0:
                md.print_info_msg(self.se_status_msg)

                # STEP 1: Create fes files from fes template file
                sse = ss.SetupSE(self)
                sse.run()

                # STEP 2: Start surface calculation and write STL files
                # to OUTPUT and SIM
                md.print_info_msg('Starting SE simulations')
                subprocess.run('./startSEsimulations.sh',
                               shell=True, cwd=self.work_env.sim_path()
                               )
                self.se_sim_started = True

            self.update_sim_status()

            # Wait for SE simulations to finish
            if self.se_status_code != 3:
                self.__wait_state()

        if sim_args is True or sim_args == 'OF':
            if self.se_status_code == 3 and self.of_status_code == 0:
                # STEP 3: Scale STL files by 1% to ensure cutting
                md.print_info_msg(
                    'Scaling STL files in x,y direction by 1% to ensure cutting.'
                    )
                ssf = ss.ScaleSTLFiles(self)
                ssf.run()

                # STEP 4: Create OpenFOAM cases from OpenFOAM case template
                md.print_info_msg(
                    'Creating OpenFOAM directories and setting up cases.'
                    )
                sof = ss.SetupOF(self)
                sof.run()

                # STEP 5: Start OpenFOAM simulations
                md.print_info_msg('Starting OF simulations')
                subprocess.run('./startOFsimulations.sh',
                               shell=True, cwd=self.work_env.sim_path()
                               )
                self.of_sim_started = True

            # Wait for OF simulations to finish
            if self.of_status_code != 3:
                self.__wait_state()

        md.print_info_msg('All simulations done')


if __name__ == '__main__':
    md.print_prog_header()
    parser = md.init_parser()
    args = parser.parse_args()
    case_name = os.path.basename(os.getcwd())
    fesig = FastEvaporationSimInGaps(case_name, args.debug)

    if args.sim:
        time_start = time.time()
        fesig.run(args.sim)
        time_end = time.time()
        delta_time = time_end-time_start
        hours, rest = divmod(delta_time, 3600)
        mins, secs = divmod(rest, 60)
        md.print_info_msg(
            f'Total simulation time: {hours}h:{mins}m:{int(secs)}:s'
            )

    if args.new:
        # TODO: implement create function for empty example case
        md.print_info_msg('Creates directories for new case study.')
        raise NotImplementedError('Part of future updates')

    if args.clear:
        subprocess.run('rm -r ./SIM ./OUTPUT', shell=True, cwd=os.getcwd())

    if args.eval:
        fesig.update_sim_status()
        if fesig.of_status_code == 3:
            md.print_info_msg('Starting evaluation.')
            evaluate = ev.evaluation(fesig.work_env, args.eval)
            evaluate()
        else:
            md.print_info_msg(
                'OF simulations not finished yet. '
                'Try again later or start simulations first!'
                )

    if args.vis:
        fesig.update_sim_status()
        if fesig.of_status_code == 3:
            md.print_info_msg('Starting visualization.')
            print(args.vis)
            visualize = vis.Visualization(
                fesig.work_env.evap_rate_csv_path(),
                fesig.work_env.dec_file_path()
                )
            if type(args.vis) == str:
                visualize(args.vis)
            else:
                visualize()
        else:
            md.print_info_msg(
                'OF simulations not finished yet. '
                'Try again later or start simulations first!'
                )
