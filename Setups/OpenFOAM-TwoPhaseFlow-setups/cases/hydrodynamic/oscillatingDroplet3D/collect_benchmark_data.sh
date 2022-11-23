#!/usr/bin/env bash

# Header of interface height function object is broken. Add it manually before
# agglomeration.
# Add major semi axis length as additional column.
for DIR in benchmark*/;
do
    cd $DIR/postProcessing/interfaceHeight1/0
    python -c "import pandas as pd; \
        df = pd.read_csv('height.dat', delim_whitespace=True, comment='#', header=None, \
                          names=['time', 'height_above_boundary', 'height_above_location']); \
        df['major_semi_axis_length'] = df['height_above_boundary'] / 2.0; \
        df.to_csv('interface_data.csv', index=False)"
    cd ../../../../
done

gather-study-data.py benchmarkpaper_00000_templateCase/postProcessing/velocity_data.csv -v benchmarkpaper.variations -f oscillating_droplet_3D_openfoam
