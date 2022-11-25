#!/bin/bash

rm -rf output50x50x50/*
mv data_50x50x50.log data_50x50x50_old.log
pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_50x50x50.log
rm $pythonlogfile


rm processed_files_50x50x50.log
fluent 3ddp -g -i case_3D-50x50x50.jou

python $pythonscriptfile 50x50x50 >> $pythonlogfile
