#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 10:34:48 2024

@author: npa7si
"""

from matplotlib import pyplot as plt
import modules as md
from ast import literal_eval

class Visualization:
    def __init__(self, evap_rate_csv_path, dec_file_path):
        self.evap_rate_csv_path = evap_rate_csv_path
        self.dec_file_path = dec_file_path
        self.fig, self.ax = plt.subplots()
    
    def __call__(self, vars_to_plot='X_M,m_dot'):
        vars_to_plot = [var_to_plot for var_to_plot in vars_to_plot.split(',')]
        self.eval_data = md.get_eval_data(self.evap_rate_csv_path, self.dec_file_path)
        self._plot(vars_to_plot)
        
    def _plot(self, vars_to_plot):
        self.ax.plot(self.eval_data[vars_to_plot[0]],self.eval_data[vars_to_plot[1]], marker='o')
        self.ax.set_xlabel(vars_to_plot[0])
        self.ax.set_ylabel(vars_to_plot[1])
        plt.show()