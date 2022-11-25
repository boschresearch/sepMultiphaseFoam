#!/bin/bash

rm -rf output256x128x128/*
mv data_256x128x128.log data_256x128x128_old.log


pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_256x128x128.log
rm $pythonlogfile
fluent 3ddp -g -i case_3D-256x128x128.jou

python $pythonscriptfile 256x128x128 >> $pythonlogfile
