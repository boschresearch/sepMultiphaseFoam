#!/bin/bash

# Script creates based on a _baseCase Basilisk-cases with different resolution, compiles them and starts the simulation 
# We loop over different resolutions and fluid parings.


echo "This script will delete all previous data, before setting up the new study. Proceed ? y n";
read answer;

if [[ "$answer" == "y" ]];
then
    rm -fr translatingDroplet*
else
    exit 0
fi



resList='32 64 128'   #resolution of shorter axis
flPairingList=' water-air gearoil-air oil_novec7500-water'

for flPl in $flPairingList
do
  for RES in $resList
  do
      cp -r _baseCase translatingDroplet_res${RES}_${flPl}
      cd translatingDroplet_res${RES}_${flPl}
      
      sed -i "s/_GRID_/$RES/g"   translatingDrop3D.c
      sed -i "s/_FLUIDPAIR_/$flPl/g"   translatingDrop3D.c
      qcc -O2 -Wall -grid=octree translatingDrop3D.c -o translatingDrop3D -lm 
      ./translatingDrop3D
      cd ..
  done
done

