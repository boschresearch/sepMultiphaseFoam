#!/bin/bash

# Script creates based on a _baseCase Basilisk-cases with different resolution, compiles them and starts the simulation 



echo "This script will delete all previous data, before setting up the new study. Proceed ? y n";
read answer;

if [[ "$answer" == "y" ]];
then
    rm -fr revVortFlow3D*
else
    exit 0
fi



resList='64 128 256' 



for RES in $resList
do
    cp -r _baseCase revVortFlow3D_res${RES}
    cd revVortFlow3D_res${RES}
    
    sed -i "s/_GRID_/$RES/g"   3DreversedVortexFlow.c
    qcc -O2 -Wall -grid=octree 3DreversedVortexFlow.c -o 3DreversedVortexFlow -lm 
    ./3DreversedVortexFlow
    cd ..
done


