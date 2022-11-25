#!/bin/bash

rm -rf output32x32x32/*
mv data_32x32x32.log data_32x32x32_old.log
pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_32x32x32.log
rm $pythonlogfile


fluent 3ddp -g -i case_3D-32x32x32.jou

python $pythonscriptfile 32x32x32 >> $pythonlogfile
