#!/bin/bash

rm 3DoscDrop_basilisk.csv

cp ../oscDrop3D_res*/oscillatingDrop3D_res*.basiliskDat .

#create result file
touch 3DoscDrop_basilisk.csv

#write header
awk NR==1  oscillatingDrop3D_res50_water-air.basiliskDat > 3DoscDrop_basilisk.csv
#append all files except for the header line
awk FNR!=1 oscillatingDrop3D_res* >> 3DoscDrop_basilisk.csv
