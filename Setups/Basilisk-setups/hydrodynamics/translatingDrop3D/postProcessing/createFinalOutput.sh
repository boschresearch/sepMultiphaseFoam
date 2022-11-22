#!/bin/bash

rm 3DtranslatingDrop_basilisk.csv

cp ../translatingDroplet_res*/translatingDrop3D_*.basiliskDat .

#create result file
touch 3DtranslatingDrop_basilisk.csv

#write header
awk NR==1 translatingDrop3D_res64_water-air.basiliskDat > 3DtranslatingDrop_basilisk.csv
#append all files except for the header line
awk FNR!=1 translatingDrop3D_res* >> 3DtranslatingDrop_basilisk.csv
