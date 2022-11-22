#!/bin/bash

# Script creates based on a _baseCase Basilisk-cases with different resolution, compiles them and starts the simulation 
# We loop over different resolutions and fluid parings.


echo "This script will delete all previous data, before setting up the new study. Proceed ? y n";
read answer;

if [[ "$answer" == "y" ]];
then
    rm -fr oscDrop3D*
else
    exit 0
fi



resList='50 100 200'
flPairingList=' water-air gearoil-air oil_novec7500-water'

for flPl in $flPairingList
do
  for RES in $resList
  do
      cp -r _baseCase oscDrop3D_res${RES}_${flPl}
      cd oscDrop3D_res${RES}_${flPl}
      
      sed -i "s/_GRID_/$RES/g"   oscillatingDrop3D.c
      sed -i "s/_FLUIDPAIR_/$flPl/g"   oscillatingDrop3D.c
      qcc -O2 -Wall -grid=octree oscillatingDrop3D.c -o oscillatingDrop3D -lm 
      ./oscillatingDrop3D
      cd ..
  done
done

