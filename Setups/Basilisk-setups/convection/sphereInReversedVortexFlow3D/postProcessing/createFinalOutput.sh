#!/bin/bash

rm 3DsphereInReversedVortexFlow_basilisk.csv

cp ../rev*/sphereIn*.basiliskDat .

#create result file
touch 3DsphereInReversedVortexFlow_basilisk.csv

#write header
awk NR==1  sphereInReversedVortexFlow3D-res64.basiliskDat > 3DsphereInReversedVortexFlow_basilisk.csv  
#append all files except for the header line
awk FNR!=1 sphereInReversedVortexFlow3D-res* >> 3DsphereInReversedVortexFlow_basilisk.csv
