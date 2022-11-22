#!/bin/bash

rm 2DtranslatingDrop_basilisk.csv

cp ../translatingDroplet_res*/translatingDrop2D_*.basiliskDat .



#create result file
touch 2DtranslatingDrop_basilisk.csv

#write header
awk NR==1 translatingDrop2D_res64_water-air.basiliskDat > 2DtranslatingDrop_basilisk.csv
#append all files except for the header line
awk FNR!=1 translatingDrop2D_res* >> 2DtranslatingDrop_basilisk.csv
