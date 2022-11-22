#!/bin/bash

# Script creates based on a _baseCase Basilisk-cases with different resolution, compiles them and starts the simulation 



echo "This script will delete all previous data, before setting up the new study. Proceed ? y n";
read answer;

if [[ "$answer" == "y" ]];
then
    rm -fr reversedDiagFlow*
else
    exit 0
fi



resList='60 120 240' #for the longer axis



for RES in $resList
do
    cp -r _baseCase reversedDiagFlow_res${RES}
    cd reversedDiagFlow_res${RES}
    
    sed -i "s/_GRID_/$RES/g"   2DreversedDiagonalFlow.c
    qcc -O2 -Wall 2DreversedDiagonalFlow.c -o 2DreversedDiagonalFlow -lm  
    ./2DreversedDiagonalFlow
    cd ..
done


