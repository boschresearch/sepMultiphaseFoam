## Basilisk-Setups

Basilisk based test-suite including tests for convection and hydrodynamics.
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

All cases are setup the same.
They contain a `_baseCase` and a `setup_study.sh` to create all paper variations.
The `setup_study.sh` also compiles and runs the simulation.
Within the folder `postProcessing` you find an additional `createFinalOutput.sh` file, which will collect the data of your case variations and plot them into ONE single *csv-file.
This file has the corret formation to work with the evaluation routines in 
`publications/ST-VoF-benchmark/benchmark-vof-evaluation` (check out the ReadMe.md there for further information).


### Getting Started
*We are assuming here that you work in a Linux environment*

After installation, simply switch to one of the test cases, e.g.

 `cd Basilisk-setups/hydrodynamics/stationaryDrop2D`
 
To run the same cases as in the Paper, simply run `./setup_study.sh`. This script uses only bash-commands and should be self explanatory for anyone familiar with a terminal. 
For the *hydrodynamic*-cases two parameters are varied, namely:
* resolution
* fluid-pairing

For *convection* only the resolution is varied.

Feel free to manipulate the `setup_study.sh`-file to your liking.

When running the script, variants based on the `_baseCase` are created, compiled and ran (each in serial). 
After running the simulation, go to postProcessing and execute `./createFinalOutput.sh`.



### Installation
To install, you must first install Basilisk from [http://basilisk.fr/](http://basilisk.fr/).
Please follow the installation guide there to ensure a working Basilisk version.

Afterwards you can clone this complete repository by simply typing

`git clone https://github.com/boschresearch/sepMultiphaseFoam`



### About
Robert Bosch GmbH 

### Contribute
If you detect a bug or unexpected behavior while using this test suite, feel free to contact the authors. Since we benchmarked many solvers in which we are not proficient, we cannot guarantee the best performance. However, we are happy about all contributions since we aim to offer a reliable basis.

### License
Since these test cases use Basilisk, we comply with the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html) license.

### Bibliography