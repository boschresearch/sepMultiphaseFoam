#!/usr/bin/env bash
mkdir study-benchmarkpaper
create-parameter-study.py benchmarkpaper.parameter -d study-benchmarkpaper
rm -f *.database
cp collect_benchmark_data.sh study-benchmarkpaper
cd study-benchmarkpaper
sh run_benchmarkpaper_study.sh
cd ..
