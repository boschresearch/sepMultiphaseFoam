#!/usr/bin/env bash

# Header of interface height function object is broken. Add it manually before
# agglomeration.
for DIR in benchmark*/;
do
    cd $DIR/postProcessing/interfaceHeight1/0
    # FIXME: ensure that the equilibrium interface height, 0.0013 currently, is set correctly.
    python -c "import pandas as pd; \
        df = pd.read_csv('height.dat', delim_whitespace=True, comment='#', header=None, \
                          names=['time', 'height_above_boundary', 'height_above_location']); \
        df['amplitude_at_center'] = df['height_above_location'] - 0.0013; \
        df.to_csv('interface_data.csv', index=False)"
    cd ../../../../
done

gather-study-data.py benchmarkpaper_00000_templateCase/postProcessing/velocity_data.csv -v benchmarkpaper.variations -f oscillating_wave_2D_openfoam
