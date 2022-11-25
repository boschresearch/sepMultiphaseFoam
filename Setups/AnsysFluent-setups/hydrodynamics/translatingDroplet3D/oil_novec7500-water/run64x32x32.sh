#!/bin/bash

rm -rf output64x32x32/*
mv data_64x32x32.log data_64x32x32_old.log


pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_64x32x32.log
rm $pythonlogfile
fluent 3ddp -g -i case_3D-64x32x32.jou

python $pythonscriptfile 64x32x32 >> $pythonlogfile
