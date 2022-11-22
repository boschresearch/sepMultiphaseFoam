#!/bin/bash

# Script creates based on a _baseCase Basilisk-cases with different resolution, compiles them and starts the simulation 



echo "This script will delete all previous data, before setting up the new study. Proceed ? y n";
read answer;

if [[ "$answer" == "y" ]];
then
    rm -fr revVortFlow2D*
else
    exit 0
fi



resList='32 64 128' 



for RES in $resList
do
    cp -r _baseCase revVortFlow2D_res${RES}
    cd revVortFlow2D_res${RES}
    
    sed -i "s/_GRID_/$RES/g"   2DreversedVortexFlow.c
    qcc -O2 -Wall 2DreversedVortexFlow.c -o 2DreversedVortexFlow -lm 
    ./2DreversedVortexFlow
    cd ..
done


