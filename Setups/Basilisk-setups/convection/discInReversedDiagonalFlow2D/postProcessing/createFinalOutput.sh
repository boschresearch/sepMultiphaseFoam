#!/bin/bash

rm discInReversedDiagFlow2D_basilisk.csv

cp ../reversedDiagFlow_res*/discInReversedDiagonalFlow2D-res*.basiliskDat .

#create result file
touch discInReversedDiagFlow2D_basilisk.csv

#write header
awk NR==1 discInReversedDiagonalFlow2D-res60.basiliskDat > discInReversedDiagFlow2D_basilisk.csv  
#append all files except for the header line
awk FNR!=1 discInReversedDiagonalFlow2D-res* >> discInReversedDiagFlow2D_basilisk.csv
