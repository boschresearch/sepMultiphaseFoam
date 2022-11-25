#!/bin/bash

rm -rf output128x64x64/*
mv data_128x64x64.log data_128x64x64_old.log


pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_128x64x64.log
rm $pythonlogfile
fluent 3ddp -g -i case_3D-128x64x64.jou

python $pythonscriptfile 128x64x64 >> $pythonlogfile
