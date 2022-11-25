#!/bin/bash

rm -rf output64x32/*
mv data_64x32.log data_64x32_old.log


pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_64x32.log
rm $pythonlogfile
fluent 2ddp -g -i case_2D-64x32.jou

python $pythonscriptfile 64x32 >> $pythonlogfile
