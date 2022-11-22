#!/bin/bash

rm 3DstatDrop_basilisk.csv

cp ../stationaryDroplet_res*/stationaryDrop3D_res*.basiliskDat .

#create result file
touch 3DstatDrop_basilisk.csv

#write header
awk NR==1 stationaryDrop3D_res32_water-air.basiliskDat > 3DstatDrop_basilisk.csv
#append all files except for the header line
awk FNR!=1 stationaryDrop3D_res* >> 3DstatDrop_basilisk.csv
