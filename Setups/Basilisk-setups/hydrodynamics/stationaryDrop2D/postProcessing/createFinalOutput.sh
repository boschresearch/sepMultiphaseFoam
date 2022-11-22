#!/bin/bash

rm 2DstatDrop_basilisk.csv

cp ../stationaryDroplet_res*/stationaryDrop2D_res*.basiliskDat .

#create result file
touch 2DstatDrop_basilisk.csv

#write header
awk NR==1 stationaryDrop2D_res64_water-air.basiliskDat > 2DstatDrop_basilisk.csv
#append all files except for the header line
awk FNR!=1 stationaryDrop2D_res* >> 2DstatDrop_basilisk.csv
