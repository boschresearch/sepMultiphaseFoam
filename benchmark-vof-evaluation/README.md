# Benchmark VOF Evaluation
The purpose of this repository is two-fold. First, collect data from different volume-of-fluid solvers
for a range of canonical two-phase test cases. At the moment, this includes advection/convection test
cases assessing the accuracy of the interface advection using prescribed velocity fields and hydrodynamic
test cases without wall contact. Second purpose of this repository is to provide means to
visualize the data to compare the performance of the different solvers. Visualization is done by
Jupyter notebooks.


## Usage
### Software prerequisites
The following software packages and Python modules are required. The version in brackets is the version
the notebooks have been tested with and not necessarily the minimum required version.
* Python3 (3.10.5)
* [jupyter-notebook](https://jupyter.org/) (6.4.12-1)
* [matplotlib](https://matplotlib.org/) (3.4.3)
* [pandas](https://pandas.pydata.org/) (1.4.3-1)

### Getting started
To create plots with the data already available within the repository, start Jupyter notebook 
within the root directory of the repository
```
jupter notebook
```
and open the notebook of the test cases you are interested (`*.ipynb`). They should run out-of-box
and create the plots shown in the paper.

### Adding a solver to the comparison
If you want to see how your own solver compares to the benchmarked ones, here are the principal
steps:
* Adapt the test case setup to your solver and evaluate the relevant metrics as described in the
    paper, e.g. the `maximum_velocity_error` for a stationary droplet.
* For each case you are interested in, summarize the data in a CSV file. Please see the section
    _CSV file format_ for the details of the format. In priciple, your data can be spread over
    multiple files as long as they adhere to the format described further below.
* For each test case, place the CSV file(s) in the appropriate data directory, see section
    `Data organisation` below.
* Start the test case's Jupyter notebook and use `Restart kernel and run all`. You should see
    an additional entry in the plots for your solver now.
* If the plots are cluttered or you want to compare specific solvers, you can prescribe a solver
    subset to compare. This is described in each notebook.

### Notebooks
For each test case or group of test cases, there is a Jupyter notebook containing a short description
on its usage and the code visualizing the solver data. Functionality shared by all notebooks is located in
`shared_function.py`. Within `shared_function.py`, you also find some global options affecting the notebooks:
* `figure_suffix`: determines the file format the figures are saved as. Default is `.pdf`, alternatively
    `.png` can also be used.
* `figure_directory`: location where to store the figures. Default: `figures`
* `plot_style`: determines the figure style in terms of size and font size. You can choose between
    `notebook` and `publication`. The former gives you larger figures suited for inspection within a
    notebook, the latter gives you a figure format suited for papers.

### Data organisation
The `data` directory mirrors the structure of the test cases. Thus, on the first level you find the
different test case families, currently `convection` and `hydrodynamic`. On the next level, you find
the specific test cases, e.g. `stationaryDroplet2D` or `discInDiagonalFlow2D`. Within each
of these test case directories, there are several CSV files containing the data obtained with different
solvers for this test case.  
The default behaviour of a notebook is to read all CSV files from its corresponding test case data directory.
For example, `oscillating_wave_2D.ipynb` reads all CSV files located in `data/hydrodynamic/oscillatingWave2D`.  
Currently, the file names usually contain the name of the test case and the solver. However, this is mainly
for clarity. It is _not_ used to assign data to a solver. This is done through a dedicated column
within the CSV file.

### CSV file format
The CSV files use `,` as a separator and a header is expected in the first line. The column names are not
case sensitive as they are all converted to lower-case when read.  

Two groups of columns can be distinguished independent of test case: data columns storing the evaluated
error metrics and time in case time dependent metrics are observed. An example for such a column
is the `max_velocity_error` from the stationary and translating droplet test. Within the other group are
metadata columns that help to uniquely identify to with what settings the error metrics have been obtained.  

There are two meta data columns that are required in every CSV file regardless of
test case: `solver` and `resolution`. The former obviously identifies the solver and the latter
the spatial resolution along an axis.  

For the hydrodynamic test cases, there is a third mandatory meta data column named `fluid_pairing`. It 
identifies the fluid/fluid combination used. Currently, there are three combinations that have been used
for benchmarking:
* `water-air`
* `gearoil-air`
* `oil_novec7500-water`
The term before the dash refers to the fluid of the dispersed phase and the term after the dash to the
continuous phase. For example, `water-air` refers to a water droplet surrounded by air. To properly group the
data for visualization, please use the terms above exactly as they are spelled. Otherwise, they are interpreted
as a new fluid/fluid pairing. In addition, visualization for the `oscillatingWave2D` and the
`oscillatingDropelt3D` will fail.  
You can find the corresponding fluid properties either in the publication (table 2) or in
`shared_function.py` as Python dictionaries.  
Further information which columns are required for a test case can be found in its associated notebook.
