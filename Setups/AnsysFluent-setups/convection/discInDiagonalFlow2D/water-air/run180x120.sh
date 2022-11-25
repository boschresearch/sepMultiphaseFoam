#!/bin/bash

rm -rf output180x120/*
mv data_180x120.log data_180x120_old.log


pythonscriptfile=../digestFieldOutput.py
fluent 2ddp -g -i case_2D-180x120.jou

python $pythonscriptfile
