#!/bin/bash

rm -rf output128x64/*
mv data_128x64.log data_128x64_old.log


pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_128x64.log
rm $pythonlogfile
fluent 2ddp -g -i case_2D-128x64.jou

python $pythonscriptfile 128x64 >> $pythonlogfile
