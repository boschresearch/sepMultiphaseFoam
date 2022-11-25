#!/bin/bash

rm -rf output200x200x200/*
mv data_200x200x200.log data_200x200x200_old.log
pythonscriptfile=../digestFieldOutput.py
pythonlogfile=py_200x200x200.log
rm $pythonlogfile


rm processed_files_200x200x200.log
fluent 3ddp -g -i case_3D-200x200x200.jou

python $pythonscriptfile 200x200x200 >> $pythonlogfile
