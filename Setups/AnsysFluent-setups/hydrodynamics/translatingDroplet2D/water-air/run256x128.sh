#!/bin/bash

rm -rf output256x128/*
mv data_256x128.log data_256x128_old.log


pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_256x128.log
rm $pythonlogfile
fluent 2ddp -g -i case_2D-256x128.jou

python $pythonscriptfile 256x128 >> $pythonlogfile
