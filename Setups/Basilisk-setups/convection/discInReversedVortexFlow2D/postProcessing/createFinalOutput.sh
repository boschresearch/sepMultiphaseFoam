#!/bin/bash

rm discInReversedVortexFlow2D_basilisk.csv

cp ../revVortFlow2D_res*/discIn*.basiliskDat .

#create result file
touch discInReversedVortexFlow2D_basilisk.csv

#write header
awk NR==1  discInReversedVortexFlow2D-res32.basiliskDat > discInReversedVortexFlow2D_basilisk.csv  
#append all files except for the header line
awk FNR!=1 discInReversedVortexFlow2D-res* >> discInReversedVortexFlow2D_basilisk.csv
