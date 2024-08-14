
# Data and Code for Publication "Experimental and Numerical Study of Microcavity Filling Regimes for Lab-on-a-Chip Applications"

This branch contains all postprocessing scripts necessary to reproduce the results in the publication "Experimental and Numerical Study of Microcavity Filling Regimes for Lab-on-a-Chip Applications" by L. Nagel, A. Lippert, R. Leonhardt, T. Tolle, H. Zhang, and T. Maric ([Preprint on arXiv](https://doi.org/10.48550/arXiv.2407.18068)).

**Important note: Due to storage limitations, only a minimal sample of the experimental and numerical datasets are stored here to enable quick tests of the image processing scripts. The complete dataset necessary for reproducing all results is publicly available [here at TUdatalib](https://doi.org/10.48328/tudatalib-1497)**.

The contents and installation instructions are given below. They refer to the complete dataset given at [TUdatalib](https://doi.org/10.48328/tudatalib-1497).

## Contents

**Experimental data**
All experimental datasets and results are given in *data_experiments*, including
- an Excel file *case_parameters.xlsx* containing an overview of all experimental cases and the respective experimental settings (velocity, frame rate, etc.)
-  a directory for each fluid with sub-directories for each processing step, including the postprocessing results stored as .csv files.

**Simulation data**
The OpenFOAM cases given in *data_simulations* contain
- a directory for each fluid, each containing all simulation configurations used in the studies, including results
- a directory containing the simulations used for the contact angle calibration study for Novec, including bash scripts to create the screenshots that are used for image processing.
Note that the results of these studies were manually copied into *data_experiments* to be processed with the same workflow as the experimental images.


**Postprocessing scripts**
The directory *postprocessing_scripts* contains the Jupyter notebooks used for image processing and plot generation. \
An overview of the scripts is given here, a more detailed documentation can be found in the respective notebooks.
| Script |      Contents|
|----------|:-------------:|
|*image_processing_channel_edge_detection.ipynb*|Detection of the channel edges in the images |
| *image_processing_water_tween.ipynb* |Contact angle measurement and interface tracking for water and Tween |
| *image_processing_novec.ipynb* | Contact angle measurement and interface tracking for Novec|
|*plot_statistical_analysis.ipynb* |Plot generation for data analysis of contact angle measurements
|*plot_interface_tracking.ipynb* |Plot generation for line tracking results
|*plot_filling_regimes.ipynb* |  Plot generation for filling regime results|
|*shared_functions.py* |  Python script containing functions necessary for multiple notebooks|

Note: when testing the notebooks, it can be beneficial to set `step_images=1000` in the image processing scripts. This leads to processing every 1000th image (only 1 image per case), therefore reducing run time significantly. For reproducing the results, `step_images=1` is necessary.
## Installation
For running the postprocessing scripts, [Python 3.11.5](https://www.python.org/downloads/release/python-3115/) is used. Necessary packages include
- opencv-python             4.8.0.76
- pandas                    2.1.1
- scikit-learn              1.2.2

A list of all used modules and their respective versions can be found in the file *postprocessing_scripts/requirements.txt*.


To run the simulations, [OpenFOAM v2212](https://www.openfoam.com/news/main-news/openfoam-v2212) and [TwoPhaseFlow-of2206](https://github.com/DLR-RY/TwoPhaseFlow/tree/of2206) are required. Furthermore, an installation of additional OpenFOAM libraries is necessary for the use of the artificial viscosity model and the wisp correction used in the simulations. The source code and installation instructions are found [here](https://github.com/boschresearch/sepMultiphaseFoam/tree/publications/ArtificialInterfaceViscosity). More information about these libraries is given in the journal article:

>Nagel, L., Lippert, A., Tolle, T. et al. Stabilizing the unstructured Volume-of-Fluid method for capillary flows in microstructures using artificial viscosity. Exp. Comput. Multiph. Flow 6, 140–153 (2024). https://doi.org/10.1007/s42757-023-0181-y

## Authors
Robert Bosch GmbH
