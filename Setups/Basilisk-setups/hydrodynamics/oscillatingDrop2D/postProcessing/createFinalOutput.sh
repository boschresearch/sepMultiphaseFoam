#!/bin/bash

rm 2DoscDrop_basilisk.csv

cp ../oscDrop2D_res*/oscillatingDrop2D_res*.basiliskDat .

#create result file
touch 2DoscDrop_basilisk.csv

#write header
awk NR==1  oscillatingDrop2D_res64_water-air.basiliskDat > 2DoscDrop_basilisk.csv
#append all files except for the header line
awk FNR!=1 oscillatingDrop2D_res* >> 2DoscDrop_basilisk.csv
