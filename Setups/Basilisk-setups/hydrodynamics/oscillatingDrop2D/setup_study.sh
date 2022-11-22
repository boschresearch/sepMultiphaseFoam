#!/bin/bash

# Script creates based on a _baseCase Basilisk-cases with different resolution, compiles them and starts the simulation 
# We loop over different resolutions and fluid parings.


echo "This script will delete all previous data, before setting up the new study. Proceed ? y n";
read answer;

if [[ "$answer" == "y" ]];
then
    rm -fr oscDrop2D*
else
    exit 0
fi



resList='64 128 256'
flPairingList=' water-air gearoil-air oil_novec7500-water'

for flPl in $flPairingList
do
  for RES in $resList
  do
      cp -r _baseCase oscDrop2D_res${RES}_${flPl}
      cd oscDrop2D_res${RES}_${flPl}
      
      sed -i "s/_GRID_/$RES/g"   oscillatingDrop2D.c
      sed -i "s/_FLUIDPAIR_/$flPl/g"   oscillatingDrop2D.c
      qcc -O2 -Wall oscillatingDrop2D.c -o oscillatingDrop2D -lm 
      ./oscillatingDrop2D
      cd ..
  done
done

