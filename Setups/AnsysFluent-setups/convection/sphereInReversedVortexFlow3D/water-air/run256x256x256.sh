#!/bin/bash

rm -rf output256x256x256/*
mv data_256x256x256.log data_256x256x256_old.log
pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_256x256x256.log
rm $pythonlogfile


fluent 3ddp -g -i case_3D-256x256x256.jou

python $pythonscriptfile 256x256x256
