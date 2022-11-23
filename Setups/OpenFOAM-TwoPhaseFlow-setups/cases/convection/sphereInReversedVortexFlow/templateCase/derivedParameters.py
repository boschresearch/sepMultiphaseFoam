# Documentation on how to use derivedParameters.py can be found in the
# NFDI4Ing knowledge base:
# https://nfdi4ing.pages.rwth-aachen.de/knowledge-base/how-tos/how_to_set_dependent_parameters_in_a_parameter_study_using_pyfoam_with_derivedparameters_py/

def compute_ncells(values):
    return values["RESOLUTION"]**3


def compute_cores(values):
    import sys
    
    # Give explicitly prescribed values precedence over computed values
    if "N_CORES_TOTAL" in values:
        return values["N_CORES_TOTAL"]
            
    res = values['RESOLUTION']
              
    # Resolution - core number map
    res_to_cores = {64 : 3,
                    128 : 24,
                    256 : 192}

    if res not in res_to_cores.keys():
        print("Error: decomposition not available for resolution", res, ".")
        print("\tPlease provide an entry in 'derivedParameters.py', compute_cores.")
        sys.exit()

    return res_to_cores[res]


def compute_memory(cells_per_core, values):
    from math import ceil

    # Give explicitly prescribed values precedence over computed values
    if "MEMORY_PER_CORE" in values:
        return values["MEMORY_PER_CORE"]

    # Heuristic guess to compute memory requirement in Megabyte
    return str(int(ceil(1200*cells_per_core/1e5)))+"M"


ncells = compute_ncells(locals())

N_CORES_TOTAL = compute_cores(locals())
MEMORY_PER_CORE = compute_memory(ncells/N_CORES_TOTAL, locals())

# This dummy is required to avoid a PyFoam error if DELTA_T is given explicitly in the
# parameter file
dummy = 0
