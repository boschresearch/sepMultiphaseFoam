# OpenFOAM / TwoPhaseFlow setups: interFoam, interIsoFoam, interFlow

## Getting started

### Software prerequisites
To use the test cases preparation scripts described below you need a working Linux environment with the following software packages installed:
* OpenFOAM v2112 from www.openfoam.com
* [TwoPhaseFlow](https://github.com/DLR-RY/TwoPhaseFlow) (only for the interFlow solver)
* Python3.x
* [Pandas](https://pandas.pydata.org/) (only for the script `gather-study-data.py`) 
* [PyFoam](https://pypi.org/project/PyFoam/) (scripts have been tested with version 2021.6) 

### Prepare your shell environment
Two points have to be configured before you can actually use the test suite:
* Make the test suite scripts available in a shell/terminal.
* For some scripts: provide a Python 3.x environment with additional Python modules like [Pandas](https://pandas.pydata.org/).
For the first point - making the test suite scripts available on the terminal - go into the root directory of the test suite repository and source `scripts/bashrc`:
```
cd path/to/the/repository
cd scripts
source bashrc
```
Again, this assumes you are using BASH as shell. Sourcing this file also works for ZSH as long as you are within the `scripts` directory when calling `source bashrc`.  
For the second point, making a Python 3.x enviroment including the Pandas module available: this is only necessary when you want to run the `gather-study-data.py` script.



### Using the test cases

With the shell environment prepared, you should now be able to setup and run thr test cases. Within the `cases` directory, there are currently two groups of test cases:

* `convection` test cases, meaning only the movement of the interface is tested using prescribed velocity fields.
* `hydrodynamic` test cases, assessing the accuracy of the hydrodynamics for incompressible, isothermal flows without wall contact.


### A simple example

If you are on the highest level, switch to one of the cases, e.g.
```
cd cases/convection/discInDiagonalFlow
```
Here you should find a `templateCase` and a `benchmarkpaper.parameter` file.

The `benchmarkpaper.parameter` defines your parameter space. In this example
```
values
{
        DELTA_T     ( 1e-5 );
        RESOLUTION  ( 60 120 240 );
        solver      ( interFoam interIsoFoam );

    // Fixed parameters for job script setup
    MESHER              ( blockMesh );
}
```
the time step, the mesh resolution and two different solvers are defined.  
Within `templateCase`, there is a file named `job-init-and-solve.sh.template`. This
file contains the applications to create the mesh, execute preprocessing and
finally run the solver. This script template is setup to run locally on your machine.
You can adapt it, e.g. so it is a proper job script for a cluster system
available to you. 


To SET UP this parameter variation, simply run
```
create-parameter-study.py benchmarkpaper.parameter -d ~/scratch/pathToWhereYouWantTheStudy/
```

Switching to your `~/scratch/pathToWhereYouWantTheStudy/` folder should present you with the ready-to-run parameter study: `$ ls`
```
benchmarkpaper_00000_templateCase  benchmarkpaper_00004_templateCase
benchmarkpaper_00001_templateCase  benchmarkpaper_00005_templateCase
benchmarkpaper_00002_templateCase  benchmarkpaper.variations
benchmarkpaper_00003_templateCase  run_benchmarkpaper_study.sh
```

To now run the entire study, execute
```
run_benchmarkpaper_study.sh
```
However, if you haven't modified ``job-init-and-solve.sh.template` to submit cluster jobs,
it makes more sense to execute the `job-init-and-solve.sh` script within each
variant individually. Otherwise, you will probably overburden your machine.



### General structure

Within each test case folder, e.g. `cases/hydrodynamic/stationaryDroplet2D`, you find a `run_benchmarkpaper.sh` script. Executing this script creates a subfolder `study-benchmarkpaper`
in which the parameter study is prepared. In addition, it will trigger execution of each single study variant. Be sure to properly modify `job-init-and-solve.sh.template` in `templateCase`.
Within the `study-benchmarkpaper` folder, you'll also find a `collect_benchmark_data.sh` script. Once the solver jobs have finished, call this script to agglomerate the secondary data from the
`postProcessing` directory found in each study variant into a single CSV file.  
The `run_benchmarkpaper.sh` is a convenience wrapper around the script `create-parameter-study.py` located inside `scripts`. If you followed the steps above for preparing the shell environment,
it should be available in your terminal. This script, along with a so-called parameter file and a template case, is at the heart of preparing a parameter study. Call it with the option `-h` to see
the full list of mandatory and optional arguments:
```
create-parameter-study.py -h
```
Running this script, e.g. inside `cases/hydrodynamic/stationaryDroplet2D`,
```
create-parameter-study.py benchmarkpaper.parameter
```
only prepares a parameter study, defined by the file `benchmarkpaper.parameter`. No computation (meshin, preprocessing, solver) is triggered yet. However, there is a list of numbered directories
`benchmarkpaper_000*` now, each containing a valid
OpenFOAM case. Inside each of these directories, there is a `job-init-and-solve.sh` script. This script usually executes meshing, preprocessing and finally the solver.
If you want to submit jobs for all cases created, you can run the `run_benchmark_paper.sh` script, which has been created by running `create-parameter-study.py`. This is again a convenience script that
loops over all directories belonging to a study and executes the aforementioned `job-init-and-solve.sh` script. Using this convenience script is only recommended if you have adapted `job-init-and-solve.sh.template`
as a job submission script. Otherwise, as mentioned above, running all variants at once will probably overburden your machine.  
If you want to know which number corresponds to which parameter vector, e.g. to see which variants use a certain resolution, open `benchmarkpaper.variations` with a text editor. You should see something similar to this:
```
===============================
36 variations with 3 parameters
===============================


==================
Listing variations
==================

Variation 0 : {'FLUID_PAIRING': 'water-air', 'RESOLUTION': 32, 'solver': 'interFoam'}
Variation 1 : {'FLUID_PAIRING': 'water-air', 'RESOLUTION': 64, 'solver': 'interFoam'}
Variation 2 : {'FLUID_PAIRING': 'water-air', 'RESOLUTION': 128, 'solver': 'interFoam'}
...
```
An alternative to obtain this mapping is to use PyFoam directly:
```
pyFoamRunParameterVariation.py --list-variations templateCase benchmarkpaper.parameter
```
In case you only want a subset of a study, use this command, pick the variations (meaning numbers) you are interested in and use the `-v` option from `create-parameter-study.py` to create
the desired subset.  

The second script available is `gather-study-data.py`. Its purpose is to agglomerate secondary data of a study into a single CSV or JSON file. Use the option `-h` to get an overview
of the mandatory and optional arguments:
```
gather-study-data.py -h
```
