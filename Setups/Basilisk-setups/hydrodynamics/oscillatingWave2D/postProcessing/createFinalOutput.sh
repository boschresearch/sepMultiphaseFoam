#!/bin/bash

rm 2DoscillatingWave_basilisk.csv

cp ../oscWave2D_res*/waveHeight*.basiliskDat .

#create result file
touch 2DoscillatingWave_basilisk.csv

#write header
awk NR==1 waveHeight_res64_water-air.basiliskDat > 2DoscillatingWave_basilisk.csv
#append all files except for the header line
awk FNR!=1 wave* >> 2DoscillatingWave_basilisk.csv
