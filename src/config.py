#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 07:17:05 2025

@author: npa7si
"""


class SimParam:
    def __init__(self, name, val):
        self._name = name
        self._val = val

    @property
    def val(self):
        return self._val

    @property
    def name(self):
        return self._name


class Config:
    # General parameter placeholders that are used internally.

    def __init__(self):
        self._config = [
            # computational resources Surface Evolver
            SimParam('N_CORES_SE', 1),
            SimParam('N_CORESPERNODE_SE', 1),
            SimParam('MEMORY_SE', 0.5),
            SimParam('RUNTIME_SE', 2),

            # computational resources pre meshing script
            SimParam('N_CORES_PREMESHING', 1),
            SimParam('N_CORESPERNODE_PREMESHING', 1),
            SimParam('MEMORY_PREMESHING', 16),
            SimParam('RUNTIME_PREMESHING', 0.5),

            # computational resources meshing script (snappyHexMesh)
            SimParam('N_CORES_SHM', 4),
            SimParam('N_CORESPERNODE_SHM', 4),
            SimParam('MEMORY_SHM', 8),
            SimParam('RUNTIME_SHM', 1),

            # computational resources OpenFOAM
            SimParam('N_CORES_OF', 1),
            SimParam('N_CORESPERNODE_OF', 1),
            SimParam('MEMORY_OF', 16),
            SimParam('RUNTIME_OF', 0.5)]

    @property
    def config(self):
        return self._config

    def get_val(self, name):
        for sim_param in self._config:
            if sim_param.name == name:
                return sim_param.val

    def get_names(self):
        return [param.name for param in self._config]

    def get_vals(self):
        return [param.val for param in self._config]

    def as_dict(self):
        d = {}
        for param in self._config:
            d |= {param.name: param.val}
        return d
