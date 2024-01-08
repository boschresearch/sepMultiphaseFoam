# Artificial Viscosity / Wisp Correction for OpenFOAM

This branch contains the implementations and test cases discussed in the publication "Stabilizing the unstructured Volume-of-Fluid method for capillary flows in micro-structures using artificial viscosity" [(Preprint on ArXiV)](https://arxiv.org/abs/2306.11532).

Based on OpenFOAM-v2212 + TwoPhaseFlow-of2206.
Also tested with OpenFOAM-v2112 + TwoPhaseFlow-of2112.

TwoPhaseFlow is found here: https://github.com/DLR-RY/TwoPhaseFlow/tree/of2206

## Contents 
- An fvOption with an artificial viscosity model
- A modified version of the isoAdvector class from TwoPhaseFlow with wisp correction
- Three wetting test cases: 
	- Horizontal capillary rise
	- Forced channel wetting
	- 3x3 Microcavity array wetting

All three test cases contain the artificial viscosity model, configuration can be found in the system/fvOptions files.
The third test case contains the wisp correction, configuration is seen in the system/fvSolution file.
Note: the wisp correction is currently only implemented for the interFlow solver.

For the test cases of the oscillating wave and translating droplet, refer to https://github.com/boschresearch/sepMultiphaseFoam/tree/publications/ST-VoF-benchmark. 

For more details refer to paper [source].

## Installation
Source your OpenFOAM environment with `source ~/OpenFOAM-v2212/etc/bashrc` .

To compile the libraries, run `./Allwmake` in the `src` directory.

Depending on where you installed the TwoPhaseFlow library, and which version you are using, you might need to adapt line 10 in file `src/isoAdvection_wispCorrParallel/Make/options` to
`-I/<path-to-TwoPhaseFlow>/src/VoF/lnInclude`.

Default is `-I/home/$(USER)/OpenFOAM/TwoPhaseFlow-of2206/src/VoF/lnInclude`.

## Usage
### Artificial viscosity model
Include the library in the controlDict:

`libs            ( "libfvOptionArtificialViscousInterfaceForce.so" );`

and specify the parameters in the fvOptions file.
Please refer to the three test cases for details.

### Wisp correction
Include the library in the controlDict:

`libs            ( "libisoAdvection_wispCorr.so" );`

Change the advection scheme and set a wisp tolerance in fvSolutions:

`advectionScheme isoAdvection_wispCorrParallel;`

`wispTol         1e-3;`

For an example please refer to test case 03.
Note: the wisp correction is currently only implemented for the interFlow solver.

## Authors
Robert Bosch GmbH

