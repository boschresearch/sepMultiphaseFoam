## Ansys Fluent Setups

Ansys-Fluent-based test-suite including tests for convection and hydrodynamics.
These include for *convection*
* 2D droplet in reversed diagonal flow
* 2D droplet in reversed vortex flow
* 3D droplet in reversed vortex flow

and for *hydrodynamics*
* 2D stationary droplet
* 3D stationary droplet
* 2D translating droplet
* 3D translating droplet
* 2D oscillating droplet (not used for paper)
* 3D oscillating droplet
* 2D oscillating wave

Please check out the Journal paper for detailed test case description or look into the case setups.

All cases are setup the similar.
They contain a `meshing` directory containing geometry source files and Ansys Workbench project files used during mesh generation. 
The actual test cases are located in folders named after the fluid pairing. 
For each resolution, a case setup is given in the form of a journal file (`*.jou`). 
Initialization of the volume fraction field is based on custom field functions defined in a file `patch-functions.scm` in each fluid-pairing directory.
 
### Getting Started
*We are assuming here that you work in a Linux environment* (On Windows, the bash script content can be used in quite the same way, though)

You need a license for Ansys Fluent (setups were built with 2020 R1) and a meshing tool. 
After installation, simply switch to one of the test cases, e.g.

 `cd fluent-setups/hydrodynamics/stationaryDroplet2D`

Make sure you create the meshes first. Most of the cases contain a source for creating STEP files for the geometry. The case setups are based on Ansys Workbench projects for convenience while the actual meshing has been performed in Ansys Mechanical Meshing. Whatever your choice of tools, in the end you need to provide a `*.msh` file with the correct naming of domain and boundaries as well as location (including file name) as required by the journal files. 

In order to execute a case, run the respective bash script. 
Most cases comprise a Python file `digestFieldOutput.py` which parses the output field written by Fluent (as specified in the respective journal file) and which is invoked by the bash file. The Python script creates a `*.csv` result file that can be used with the evaluation routines in `publications/ST-VoF-benchmark/benchmark-vof-evaluation` (check out the ReadMe.md there for further information)
It is advised to run the Python script simultaneously with the case in order to reduce storage space consumed by the field output files (the Python script deletes parsed files). The way to achieve this depends on your system configuration.
