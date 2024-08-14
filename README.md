# Data and Code for Publication "Fluid penetration and wetting characteristics in T-shaped microchannels"

This branch contains the data and the jupyter notebooks to reproduce the results in the publication "Fluid penetration and wetting characteristics in T-shaped microchannels" ([Preprint on arXiv](LINK)).

## Contents

### 1. Image processing directory: ***Image_processing***
- Jupyter notebooks for automated image analysis: `Image_processing_horizontal.ipynb` for horizontal ROI, `Image_processing_vertical.ipynb` for vertical ROI
- Python script for defined functions used in image processing: `shared_funcitons.py`
- Experimental results (images): a subset of images from experimental results is provided in `Images` for users to test the proposed automated image analysis procedure. The `Images` is structured as four directories for four channel variations with sub-directories for each volumetric flow rate. Each sub-directory includes:
    - original images
    - directory *processed*: post-processed images with interface fitting and calculated contact angle information
    - directory  *results*: saved data in CSV files, figures for temporal evolution of dynamic contact angle and interface displacement

### 2. Plots directory: ***Plots***
- Jupyter notebooks for plots in the publication: `Plots_contact_angle.ipynb` for contact angle plot, `Plots_others.ipynb` for all other plots (flow rate distribution, penetration depth, interface pinning effect).
- Experimental results (data): all CSV files used in the plots are provided in directory `Data`.

For more details please refer to the publication and the separate scripts.

## Packages

- opencv-python: 4.8.0.76
- numpy: 1.25.2
- pandas: 1.3.4
- scikit-learn: 1.2.2    

## Authors
Robert Bosch GmbHPu