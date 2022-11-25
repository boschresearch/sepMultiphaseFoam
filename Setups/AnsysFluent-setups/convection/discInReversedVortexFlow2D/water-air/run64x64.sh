#!/bin/bash

rm -rf output64x64/*
mv data_64x64.log data_64x64_old.log


pythonscriptfile=../digestFieldOutput.py
fluent 2ddp -g -i case_2D-64x64.jou

python $pythonscriptfile
