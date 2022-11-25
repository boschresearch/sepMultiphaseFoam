#!/bin/bash

rm -rf output360x240/*
mv data_360x240.log data_360x240_old.log


pythonscriptfile=../digestFieldOutput.py
fluent 2ddp -g -i case_2D-360x240.jou

python $pythonscriptfile
