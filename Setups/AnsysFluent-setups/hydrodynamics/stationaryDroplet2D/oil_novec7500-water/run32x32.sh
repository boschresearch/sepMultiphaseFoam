#!/bin/bash

rm -rf output32x32/*
mv data_32x32.log data_32x32_old.log
pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_32x32.log
rm $pythonlogfile


fluent 2ddp -g -i case_2D-32x32.jou

python $pythonscriptfile 32x32 >> $pythonlogfile
