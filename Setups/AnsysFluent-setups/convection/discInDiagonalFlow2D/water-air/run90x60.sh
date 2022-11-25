#!/bin/bash

rm -rf output90x60/*
mv data_90x60.log data_90x60_old.log


pythonscriptfile=../digestFieldOutput.py
fluent 2ddp -g -i case_2D-90x60.jou

python $pythonscriptfile
