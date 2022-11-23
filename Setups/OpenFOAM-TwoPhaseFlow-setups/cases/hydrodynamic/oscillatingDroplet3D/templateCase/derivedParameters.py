# Documentation on how to use derivedParameters.py can be found in the
# NFDI4Ing knowledge base:
# https://nfdi4ing.pages.rwth-aachen.de/knowledge-base/how-tos/how_to_set_dependent_parameters_in_a_parameter_study_using_pyfoam_with_derivedparameters_py/

def computeDeltaT(values):
    import math
    import sys

    # Give explicitly prescribed time step sizes precedence over
    # computed values
    if "DELTA_T" in values:
        return values["DELTA_T"]

    
    domainLength = values["DOMAIN_LENGTH"]
    resolution = values["RESOLUTION"]
    h = domainLength/resolution

    # rho_ambient might be expressed in terms of rho_droplet
    rho_ambient = 0.0
    rho_droplet = 0.0
    sigma = 0.0

    # Fluid properties at T=20 degree Celsius as reported
    # in table x in benchmark paper (add DOI)
    rho_water = 998.2
    rho_air = 1.19
    rho_gearoil = 888.0
    rho_oil_novec7500 = 1614.0

    if values["FLUID_PAIRING"] == "water-air":
        rho_ambient = rho_air
        rho_droplet = rho_water
        sigma = 72.74e-3
    elif values["FLUID_PAIRING"] == "oil_novec7500-water": 
        rho_ambient = rho_water
        rho_droplet = rho_oil_novec7500
        sigma = 49.5e-3
    elif values["FLUID_PAIRING"] == "gearoil-air":
        rho_ambient = rho_air
        rho_droplet = rho_gearoil
        sigma = 32.9e-3
    else:
        sys.exit("Error: unknown FLUID PAIRING:" + values["FLUID_PAIRING"])

    # Coefficient to scale the capillary time step size
    sf = values["SCALE_CAPILLARY_DELTA_T"]

    # The computation follows eq. (18) in Popinet 2009 and
    # eq. in (43) Denner & van Wachem 2015, respectively.
    capillary_delta_t = 1e15
    if sigma > 0.0:
        capillary_delta_t = sf*math.sqrt((rho_droplet + rho_ambient)*math.pow(h,3.0)/(2.0*math.pi*sigma))

    return capillary_delta_t


def compute_ncells(values):
    return values["RESOLUTION"]**3


def domain_decomposition(values):
    import sys

    # Return the number of subdomains along x, y and z direction.
    if values["RESOLUTION"] == 50:
        return 3,1,1
    elif values["RESOLUTION"] == 100:
        return 2,3,3
    elif values["RESOLUTION"] == 200:
        return 4,5,5
    else:
        print("Error: decomposition available for resolution", res, ".")
        print("\tPlease provide an entry in 'derivedParameters.py', compute_cores.")
        sys.exit()


def compute_cores(n_sub_domains):
    # Computing a number of cores based on a target number of cells/core
    # and using scotch for decomposition does not work for this test case
    # due a bug in the interfaceHeight function object. Thus,
    # another approach based on OpenFOAM's 'simple' decompostion strategy
    # is used ensuring that the sample line of the interfaceHeight function
    # object does not coincide with faces on processor boundaries.
    if n_sub_domains == 3:
        return 3,3
    elif n_sub_domains == 18:
        return 18,18
    elif n_sub_domains == 100:
        return 100,25


def compute_memory(cells_per_core, values):
    from math import ceil

    # Give explicitly prescribed values precedence over computed values
    if "MEMORY_PER_CORE" in values:
        return values["MEMORY_PER_CORE"]

    # Heuristic guess to compute memory requirement in Megabyte
    return str(int(ceil(1200*cells_per_core/1e5)))+"M"


ncells = compute_ncells(locals())
NDX, NDY, NDZ = domain_decomposition(locals())
N_CORES_TOTAL, N_CORES_PER_NODE = compute_cores(NDX*NDY*NDZ)
MEMORY_PER_CORE = compute_memory(ncells/N_CORES_TOTAL, locals())

DELTA_T = computeDeltaT(locals())

# This dummy is required to avoid a PyFoam error if DELTA_T is given explicitly in the
# parameter file
dummy = 0
