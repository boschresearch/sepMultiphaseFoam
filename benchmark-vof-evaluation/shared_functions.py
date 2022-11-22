# shared_functions.py

import itertools
import math
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import os
import sys

# Set material properties at a single place and look them up.
# Properties are given at 20 degree Celsius in SI units
# gearoil refers to Ravenol CLP 220
surface_tension_coeffs = {'water-air' : 72.74e-3,
                          'gearoil-air' : 32.9e-3,
                          'oil_novec7500-water' : 49.5e-3}
kinematic_viscosities = {'water' : 1.0e-6,
                         'air' : 1.53e-5,
                         'oil_novec7500' : 0.77e-6,
                         'gearoil' : 2.71e-4}
densities = {'water' : 998.2,
             'air' : 1.19,
             'oil_novec7500' : 1614.0,
             'gearoil' : 888.0}

# Set plotting parameters as figure size and font size here to avoid
# duplication in notebooks and ensure consistency
figure_suffix = ".pdf"
figure_directory = "figures"

# Set plot style to either 'notebook' or 'publication'
# to set the corresponding plotting parameters
plot_style = 'notebook'

#--- Settings for viewing notebooks in browser
if plot_style == 'notebook':
    figureSize=(15,10)
    DPI=300
    plotfontsize=15
    latex_settings = {}
elif plot_style == 'publication':
# Settings to generate PDF plots for publication
    figureSize=(3.5, 3.5)
    DPI=300
    plotfontsize=8
    latex_settings = {
                "text.usetex": True,
                "font.family": "serif",
                "font.serif": ["Palatino"]
            }
else:
    sys.exit("Error: unknown plot_style: ", plot_style, ". Exiting.")


def assign_styles_to_solvers(solvers):
    """
    Assign each solver in 'solvers' a marker and line style.
    Returns mappings as two dictionaries.
    """
    solvers.sort()

    markers = itertools.cycle(['o', 'x', '+', 's', 'd', '*', '^', 'v'])
    # Reserve solid line style for reference solutions
    lines = itertools.cycle(['dotted', 'dashed', 'dashdot', (0, (3, 1, 1, 1))])

    solver_markers = dict()
    solver_lines = dict()

    for solver in solvers:
        solver_markers[solver] = next(markers)
        solver_lines[solver] = next(lines)

    return solver_markers, solver_lines


def title_from_parameters(names, values, case_name=""):
    """
    Create a plot tile from parameters and parameter values.
    Optionally, add the case name to the title.
    """
    title = case_name
    if case_name:
        title = title + "\n"
    for param, value in zip(names, values):
        title = title + param + ": " + str(value) + "\n"

    return title 


def format_for_filename(plot_title):
    """
    Replace characters not suited for filenames by underscores.
    """
    replace_chars = [":", " ", "\n"]
    for char in replace_chars:
        plot_title = plot_title.replace(char, "_")

    return plot_title


def solver_data_table(data_files, columns_to_keep, data_dir="",  solver_subset=['all']):
    """
    Read solver data from different CSV files into a single
    dataframe with linear index.

    Positional arguments:
    - data_files:       list of CSV files; ',' is assumed as separator.
    - columns_to_keep:  list of columns to keep in the dataframe.
    Keyword arguments:
    - data_dir:       common path to directory containing CSV files.
                      default: currect directory
    - solver_subset:  list of solver names for which to load the data.
                      If an element 'all' is in the list, data for all
                      solvers is loaded.
                      default: ['all']
    """
    dataframes = []
    
    for file_name in data_files:
        df = pd.read_csv(os.path.join(data_dir, file_name), sep=',', header=0)
        
        # Convert column names to lowercase for consistency
        df.columns = df.columns.str.lower()
        
        # Discard additional data
        df = df[columns_to_keep]

        dataframes.append(df)

    # Combine data into single dataframe. Create new, integer based index
    df = pd.concat(dataframes, ignore_index=True)

    # Discard solvers not in the subset
    if not 'all' in solver_subset:
        dataframes = []
        for solver in solver_subset:
            dataframes.append(df.loc[df['solver'] == solver])

    # Combine data into single dataframe. Create new, integer based index
    df = pd.concat(dataframes, ignore_index=True)

    return df


def read_solver_data(data_files, index_columns, data_columns, data_dir="",
                     solver_subset=['all']):
    """
    Read data of different solvers from CSV files and combine them
    into a single, multiindexed dataframe.

    Positional arguments:
    - data_files:     list of CSV files; ',' is assumed as separator.
    - index_columns:  list of column names used for multiindex construction,
                      e.g. ["solver", "resolution"]
    - data_columns:   list of column names containing simulation data,
                      e.g. ["time", "velocity_error"]
    Keyword arguments:
    - data_dir:       common path to directory containing CSV files.
                      default: currect directory
    - solver_subset:  list of solver names for which to load the data.
                      If an element 'all' is in the list, data for all
                      solvers is loaded.
                      default: ['all']
    """
    columns_to_keep = list(index_columns) + list(data_columns)
    
    df = solver_data_table(data_files, columns_to_keep, data_dir=data_dir,
                           solver_subset=solver_subset)

    # Build multiindex from index columns
    df.set_index(index_columns, inplace=True)
    df.sort_index(inplace=True)

    return df


def create_tick_labels(solvers, resolutions):
    """
    For violin plots, create tick labels for x-axis. Each label is composed
    of the employed mesh resolutions and a solver name.
    """
    res_label = ""
    for res in resolutions:
        res_label = res_label + str(res) + ' '
    res_label = res_label.replace(' ', '$\quad\quad$') + '\n'
    tick_labels = [res_label + solver for solver in solvers]
    return tick_labels


def create_violin_plots(df, test_case, error_metrics, yscale='log',
                        ylabel='', file_name_addendum=''):
    """
    Plot time-dependent error metrics as distributions in so-called violin plots.

    Positional arguments:
    - df:   a multiindexed Pandas dataframe. The multiindex has to contain the levels
            'solver', 'fluid_pairing' and 'resolution'.
    - test_case: string with the name of the test case the data comes from.
    - error_metrics:    a list of column names contained in 'df' to be plotted.

    Keyword arguments:
    - yscale:   scaling of the plot's y-axis, 'linear' or 'log'. (default: 'log')
    - ylabel:   label of the y-axis. (default: '')
    - file_name_addendum: suffix for the file name the plot is saved as. (default: '')
    """
    # Prepare color dictionaries for consistent coloring
    color_list = ['steelblue', 'red', 'mediumseagreen', 'gold', 'hotpink', 'sandybrown'] + \
                 [color for color in mcolors.CSS4_COLORS]
    darker_color_list = ['darkblue', 'darkred', 'darkgreen', 'darkgoldenrod', 'mediumvioletred', 'sienna'] + \
                        [color for color in mcolors.CSS4_COLORS][1:]
    
    # Group by fluid combinations
    for params, subsetdf in df.groupby(level=["fluid_pairing"]):
        fig, ax = plt.subplots(figsize=(10.5, 3.5), dpi=DPI)
        ax.set_yscale(yscale)        
        
        # Clip color lists to match solver list length
        solver_list = ([solver for solver, _ in subsetdf.groupby(level=["solver"])]) 
        color_list = color_list[:len(solver_list)] 
        darker_color_list = darker_color_list[:len(solver_list)]
        color_dict = {k:[v1,v2] for k,v1,v2 in zip(solver_list,color_list,darker_color_list)}
        
        tick_vector = []
        resolutions = []
        for solver, solverdf in subsetdf.groupby(level=["solver"]):
            # Number of different resolutions by creating a set as intermediate step
            nres = len(set(solverdf.index.get_level_values('resolution')))
            tick_vector.append(solver)
            xpos = [x + nres*(len(tick_vector)-1) for x in range(1,nres+1)]
            error_metrics.sort() # make sure the order is always the same
            for metric_count, error_metric in enumerate(error_metrics):
                plotcolumns = []
                resolutions = []
                for res, resdf in solverdf.groupby(level=["resolution"]):
                    plotcolumns.append(resdf[error_metric])
                    resolutions.append(res)
                violin_parts = ax.violinplot(plotcolumns, positions=xpos, showmeans=True,
                                             widths=0.8, showmedians=False)
                current_color = color_dict[solver][metric_count % 2] # modulus repeats colors for more than two metrics
                for partname in ('cbars','cmins','cmaxes','cmeans'):
                    vp = violin_parts[partname]
                    vp.set_edgecolor(current_color)
                    vp.set_linewidth(1)
                for pc in violin_parts['bodies']:
                    pc.set_facecolor(current_color)
                    pc.set_edgecolor(current_color)

        tick_positions = [nres*x+2 for x in range(len(tick_vector))]
        tick_labels = create_tick_labels(tick_vector, resolutions)
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels)
        ax.set_xticks(range(1, nres*len(tick_vector)+1), minor=True)
        ax.grid(which="major")
        ax.set_ylabel(ylabel, fontsize=plotfontsize)
        
        title = title_from_parameters(["fluid_pairing"], [params], test_case)

        if not os.path.isdir(figure_directory):
            os.mkdir(figure_directory)
        fig.savefig(os.path.join(figure_directory, "violin_" + format_for_filename(title) + 
                                 file_name_addendum + figure_suffix), bbox_inches="tight")
        ax.set_title(title, fontsize=plotfontsize)


def plot_accumulated_errors(df, test_case, error_metric, yscale='log', ylabel='',
        solver_marker=None, xscale='log', file_name_addendum='', time_rel=False):
    """
    Integrate an error metric in time and plot it over different resolutions.

    Positional arguments:
    - df:   a Pandas dataframe with multiindex. The musltiindex has to contain the
            following levels: 'solver', 'fluid_pairing' and 'resolution'
    - test_case:    string with the name of th test case the data comes from.
    - error_metric: name of the column containing the error metric in 'df'.

    Keyword arguments:
    - yscale:   scale of the y-axis, either 'linear' or 'log'. (default: 'log')
    - ylabel:   label of the y-axis. (default: '')
    - solver_marker: dictionary mapping a solver name to a valid Matplotlib marker.
                     (default: None)
    - xscale:   scale of the x-axis, either 'linear' or 'log'. (default: 'log')
    - file_name_addendum: suffix for the file name the plot is saved as. (default: '')
    - time_rel: Boolean indicating whether to normalize the accumulated error with the
                time span. (default: False)
    """

    # Create plots with accumulated errors
    for params, subsetdf in df.groupby(level=['fluid_pairing']):
        fig, ax = plt.subplots(figsize=figureSize, dpi=DPI)

        ax.set_xscale(xscale)        
        ax.set_yscale(yscale)        

        time_span = max(subsetdf['time']) - min(subsetdf['time'])

        # Normalize total time to 1
        if time_rel:
            time_span = 1.0
        
        for solver, solverdf in subsetdf.groupby(level='solver'):
            resolutions = []
            errors = []
            
            # Compute accumulated error for specific solver and resolution
            for res, resdf in solverdf.groupby(level='resolution'):
                resolutions.append(res)
                err = resdf[error_metric].sum()
                delta_t = time_span / (resdf[error_metric].count() - 1)
                errors.append(err*delta_t)

            ax.plot(resolutions, errors, label=solver, marker=solver_marker[solver],
                    linestyle='')

        # Formatting
        ax.tick_params(axis='both', labelsize=plotfontsize)
    
        xticks = list(set(subsetdf.index.get_level_values('resolution')))
        xticks.sort()
        ax.set_xticks(xticks)
        ax.set_xticklabels([str(x) for x in xticks])
        ax.set_xticklabels([], minor=True)

        ax.set_ylabel(ylabel, fontsize=plotfontsize)
        ax.set_xlabel("resolution", fontsize=plotfontsize)
            
        ax.grid(which="major")
        ax.legend(fontsize=plotfontsize)
        title = title_from_parameters(["fluid_pairing"], [params], test_case)
        fig.savefig(os.path.join(figure_directory, format_for_filename(title)
                    + file_name_addendum + figure_suffix),
                    bbox_inches="tight")
        
        ax.set_title(title, fontsize=plotfontsize)


# TODO: double-check these functions to make sure we in fact get the analytical
# solution (TT)
def omega_n2_2d(radius0, fluid_pairing):
    drop_phase, ambient_phase = fluid_pairing.split('-')
    sigma = surface_tension_coeffs[fluid_pairing]
    rho_d = densities[drop_phase]
    rho_a = densities[ambient_phase]

    omega_squared = 6.0*sigma / ((rho_d + rho_a)*radius0**3.0)

    return math.sqrt(omega_squared)


def omega_n2_3d(radius0, fluid_pairing):
    drop_phase, ambient_phase = fluid_pairing.split('-')
    sigma = surface_tension_coeffs[fluid_pairing]
    rho_d = densities[drop_phase]
    rho_a = densities[ambient_phase]

    omega_squared = 24.0*sigma / ((3.0*rho_d + 2.0*rho_a)*radius0**3.0)

    return math.sqrt(omega_squared)


def amplitude_n2_3d(time, fluid_pairing, amplitude0, radius0):
    drop_phase, ambient_phase = fluid_pairing.split('-')
    nu_d = kinematic_viscosities[drop_phase]

    tau = radius0**2.0 / (5.0*nu_d)

    return amplitude0*math.exp(-time/tau)


def oscillation_n2_3d_series(times, fluid_pairing, amplitude0=None, radius0=None):
    w = omega_n2_3d(radius0, fluid_pairing)

    return [radius0 + amplitude_n2_3d(t, fluid_pairing, amplitude0, radius0)*math.cos(w*t) for t in times]


def oscillation_n2_3d(time, fluid_pairing, amplitude0=None, radius0=None):
    w = omega_n2_3d(radius0, fluid_pairing)

    return radius0 + amplitude_n2_3d(time, fluid_pairing, amplitude0, radius0)*math.cos(w*time)
