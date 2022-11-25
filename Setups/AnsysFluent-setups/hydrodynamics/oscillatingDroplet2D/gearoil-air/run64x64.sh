#!/bin/bash

rm -rf output64x64/*
mv data_64x64.log data_64x64_old.log
pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_64x64.log
rm $pythonlogfile


fluent 2ddp -g -i case_2D-64x64.jou

python $pythonscriptfile 64x64 >> $pythonlogfile
