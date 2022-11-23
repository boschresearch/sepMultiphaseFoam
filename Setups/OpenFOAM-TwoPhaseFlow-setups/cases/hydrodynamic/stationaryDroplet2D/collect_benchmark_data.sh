#!/usr/bin/env bash

# Fuse data from different function objects into a single csv file for
# further agglomeration
for DIR in benchmark*/;
do
    cd $DIR/postProcessing
    python -c "import pandas as pd; \
        dfmax = pd.read_csv('minMaxU/0/fieldMinMax.dat', delim_whitespace=True, \
                            comment='#', header=None, names=['time', 'min_error_velocity', 'max_error_velocity']); \
        dfl1 = pd.read_csv('l1normU/0/volFieldValue.dat', delim_whitespace=True, comment='#', header=None); \
        dfl2 = pd.read_csv('l2normU/0/volFieldValue.dat', delim_whitespace=True, comment='#', header=None); \
        dfmax['mean_absolute_error_velocity'] = dfl1[1]; \
        dfmax['root_mean_square_deviation_velocity'] = dfl2[1]; \
        dfmax.to_csv('velocity_data.csv', index=False)"
    cd ../../
done

gather-study-data.py benchmarkpaper_00000_templateCase/postProcessing/velocity_data.csv -v benchmarkpaper.variations -f stationary_droplet_2D_openfoam
