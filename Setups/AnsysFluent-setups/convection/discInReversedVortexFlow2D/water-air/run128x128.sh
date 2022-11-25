#!/bin/bash

rm -rf output128x128/*
mv data_128x128.log data_128x128_old.log


pythonscriptfile=../digestFieldOutput.py
fluent 2ddp -g -i case_2D-128x128.jou

python $pythonscriptfile
