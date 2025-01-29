#!/bin/bash

echo "***INFO: Installing SE-FIT convergence algorithm"
cp -r ./src/installationFiles/lib ~/evolver-2.70/

echo "***INFO: Setting up calculation routine"
sed -i "s/|-USERNAME-|/$USER/g" ~/evolver-2.70/lib/calcRoutine

echo "***INFO: Installing OpenFOAM solver steadyMolecularDiffusionFoam to OpenFOAM/applications/solvers/basic"
cp -r ./src/installationFiles/steadyMolecularDiffusionFoam ~/OpenFOAM/OpenFOAM-v2212/applications/solvers/basic/
source ~/OpenFOAM/OpenFOAM-v2212/etc/bashrc
cd ~/OpenFOAM/OpenFOAM-v2212/applications/solvers/basic/steadyMolecularDiffusionFoam
wmake

echo "***INFO: Add alias and env vars to bashrc"
echo "alias of2212='source ~/OpenFOAM/OpenFOAM-v2212/etc/bashrc'" >> ~/.bashrc
SETUP_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo "export FESIGPATH=$SETUP_DIR" >> ~/.bashrc
echo -e "fesig() {\n\tpython $SETUP_DIR/src/fastEvaporationSimInGaps.py \"\$@\"\n}" >> ~/.bashrc

echo "***INFO: Installation finished successfully!"
