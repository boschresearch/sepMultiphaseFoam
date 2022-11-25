#!/bin/bash

rm -rf output100x100x100/*
mv data_100x100x100.log data_100x100x100_old.log
pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_100x100x100.log
rm $pythonlogfile


rm processed_files_100x100x100.log
fluent 3ddp -g -i case_3D-100x100x100.jou

python $pythonscriptfile 100x100x100 >> $pythonlogfile
