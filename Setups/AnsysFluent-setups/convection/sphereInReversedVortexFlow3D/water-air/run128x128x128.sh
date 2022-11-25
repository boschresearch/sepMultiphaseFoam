#!/bin/bash

rm -rf output128x128x128/*
mv data_128x128x128.log data_128x128x128_old.log
pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_128x128x128.log
rm $pythonlogfile


fluent 3ddp -g -i case_3D-128x128x128.jou

python $pythonscriptfile 128x128x128
