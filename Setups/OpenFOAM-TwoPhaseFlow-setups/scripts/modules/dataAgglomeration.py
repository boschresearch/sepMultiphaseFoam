# dataAgglomeration.py

import pandas as pd
import numpy as np
import ast
import itertools
import os
import re
import sys


class data_collector:
    """
    Collect data from text files in directories matching a user-prescribed pattern.

    This class uses a regular expression pattern to find all directories belonging to a study.
    From each directory a text file containing the data is read.
    The primary
    responsibility of this class is to create a dict of Pandas DataFrames where
    each dataframe represents data from a file. The variation ID (from PyFoam)
    is used as dict key. This is accompanied
    by some additional information which is required to create a
    Pandas multiindex for the collected data.

    Data collected by this class:
        - study_dataframes: dictionary of Pandas DataFrames containing the data read from files.
                                The variation ID is used as dictionary key.
        - valid_variations: list of variation numbers. Only those with valid data are considered.
        - invalid_variations: dictionary of all failed variations that maps the variation number
                                to the reason why it is considered failed.
        - datapoints_per_variant_: dictionary mapping the IDs of valid variations to their
                                    corresponding number of datapoints.
                                    Required for constructing the Pandas Multiindex.
    """

    def __init__(self, directory_pattern, path_to_file, subdirectory=""):
        """
        Instantiate a data_collector with a directory- and file pattern.

        This constructor requires two arguments:
            - directory_pattern: string containing a regular expression. All directories
                matching this pattern are considered for data collection.
            - path_to_file: path to the text file within a study directory containing the
                data to be collected, e.g. 'postProcessing/minMaxU/0/fieldMinMax.dat'.

            Keyword arguments:
            - subdirectory: name of the subdirectory where the studydirectories are located. (default: current directory)
        """
        self.subdirectory = subdirectory

        # Regular expressions patterns for finding directories
        # associated with a study and the files containing the data
        self.directory_pattern = re.compile(directory_pattern)
        self.path_to_file = path_to_file
        self.variation_number_pattern = re.compile("[0-9]{5}")

        # Collected data
        self.study_dataframes = dict()
        self.valid_variations = list()
        self.invalid_variations = dict()
        self.datapoints_per_variant_ = dict()

        # Avoid duplicated colection of data
        self.already_collected = False

    def set_directory_pattern(self, pattern):
        """Set the pattern of the directories which shall be considered for collection."""
        self.directory_pattern = re.compile(pattern)

    def study_directories(self):
        """Find all directories in the current folder matching the pattern and return their names as a list."""
        study_folders = []
        study_directory = os.path.join(os.getcwd(), self.subdirectory)

        for file in os.listdir(study_directory):
            belongs_to_study = self.directory_pattern.match(file)
            if belongs_to_study and os.path.isdir(os.path.join(self.subdirectory,file)):
                study_folders.append(os.path.join(study_directory, file))

        # Ensure that the folders are sorted so the data can correctly
        # be matched with the multiindex later (TT)
        study_folders.sort()

        return study_folders

    def extract_variation_number(self, directory):
        """Extract the PyFoam variation number from the directory name and return it as an integer."""
        # Only consider the last folder of the given path
        variation_folder = directory.split('/')[-1]
        return int(self.variation_number_pattern.search(variation_folder).group())

    def has_valid_results(self, directory):
        """
        Search the given directory for a valid data file.

        Checks if the given directory contains a data file as specified by
        the user. Returns False if either the file does not exist
        or it is empty.
        """
        # Check if a data file exists
        variation_number = self.extract_variation_number(directory)
        full_file_path = os.path.join(directory, self.path_to_file)

        if not os.path.isfile(full_file_path):
            self.invalid_variations[variation_number] = "No data file"
            return False

        if os.stat(full_file_path).st_size == 0:
            self.invalid_variations[variation_number] = "File empty"
            return False
        else:
            return True


    def read_dataframe_from_file(self, file_name):
        """
        Read Pandas DataFrame from text file, ignore columns with empty header.

        Distinguish two formats:
        - *.csv: written by function objects/applications of the argo project. Use ','
            as separator.
        - *.dat: written by OpenFOAM function object. Uses tab '\t' as separator.

        """
        # Remember: by default, pandas names a headerless column 'Unnamed N' 
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_name, usecols=lambda x: not ('Unnamed' in x), comment='#')
        elif file_name.endswith('.dat'):
            df = pd.read_csv(file_name, header=0, delim_whitespace=True)
            df.columns = [column.strip('#') for column in df.columns]
        else:
            sys.exit("Error: unknown file extension", file_name.rsplit('.')[0],
                     ". Valid extensions are .csv and .dat.")

        return df

        
    def collect_data(self):
        """Performs the actual data collection process."""
        if self.already_collected:
            return
        # Create study associated folder list
        directories = self.study_directories()

        # Iterate folders:
        for directory in directories:
            if self.has_valid_results(directory):
                full_file_path = os.path.join(directory, self.path_to_file)
                variation_dataframe = self.read_dataframe_from_file(full_file_path)
                variation_id = self.extract_variation_number(directory)
                self.valid_variations.append(variation_id)
                self.datapoints_per_variant_[variation_id] = len(variation_dataframe.index)
                self.study_dataframes[variation_id] = variation_dataframe

        self.already_collected = True

    #--------------------------------------------------------------------------
    # Interface member functions
    #--------------------------------------------------------------------------
    def agglomerated_study_data(self):
        """Returns collected data as a dictionary containing Pandas DataFrames as values."""
        self.collect_data()

        return self.study_dataframes

    def existing_variations(self):
        """Returns all valid variation numbers as a list of integers."""
        self.collect_data()

        return self.valid_variations

    def datapoints_per_variant(self):
        """Returns a dictionary mapping variation IDs to the number of datapoints."""
        self.collect_data()

        return self.datapoints_per_variant_

    def failed_variations(self):
        """
        Returns information about failed variations as a dictionary.
        
        The dictionary uses the variation number of the failed variations as keys
        and maps these to the reason why the variation is considered failed.
        NOTE: missing variation directories are not considered at all, meaning
        neither successful or failed.
        """
        self.collect_data()

        return self.invalid_variations


class data_agglomerator:
    """
        Agglomerate the data of a parameter study in a multiindexed Pandas DataFrame.

        Intended to simplify further postprocessing of data and the generation
        of plots and tables from the data.
    """

    def __init__(self, variation_file_name, path_to_file, example_directory_path):
        """
        Construct data agglomerator from using a variation file, the path to
        the data file within a study directory and an example directory name
        from the study.
        """
        self.variation_file_name = variation_file_name

        study_subdirectory, example_dir = split_path_from_pattern(example_directory_path)
        directory_pattern = regex_from_study_directory_name(example_dir)

        self.data_collector = data_collector(directory_pattern, path_to_file, subdirectory=study_subdirectory) 
        self.dataframe = pd.DataFrame()
        self.already_computed = False

    def variation_number_parameter_mapping(self):
        """
        Read the variation file and return a dictionary mapping the variation
        number to the parameter dictionary.
        """
        var_map = {}
        var_lines = open(self.variation_file_name).readlines()

        for line in var_lines:
            # Skip lines without mapping
            if '{' not in line:
                continue
            var_num = int(line.split()[1])
            dict_start = line.find('{')
            # Mappings in variation file can directly be interpreted by Python
            var_map[var_num] = ast.literal_eval(line[dict_start:-1])
        return var_map

    def add_paramaters_to_dataframes(self, var_map, study_dfs):
        """
        Add parameter values from variation, e.g. resolution, as additional
        columns to their corresponding dataframes.
        """
        for var_num, df in study_dfs.items():
            parameter_vector = var_map[var_num]
            for parameter, value in parameter_vector.items():
                df[parameter] = value

    def merge_dataframes(self, study_dfs, parameter_columns):
        """
        Merge the separate study dataframes into a single dataframe and construct
        a multiindex from the parameter columns
        """
        self.dataframe = pd.concat(study_dfs)
        self.dataframe.set_index(parameter_columns, inplace=True)
        self.dataframe.sort_index(inplace=True)

    def assemble_dataframe(self, data, index):
        """Build the multiindexed dataframe from a dataframe and a multiindex."""
        self.dataframe = pd.concat(data)
        self.dataframe.index = index

    def compute_dataframe(self):
        """Toplevel function for dataframe assembly calling a set of lower-level member functions."""
        if self.already_computed:
            return

        # Get agglomerated data
        study_data = self.data_collector.agglomerated_study_data()
        existing_variations = self.data_collector.existing_variations()

        # Return an empty DataFrame for an empty parameter study. 
        if (len(existing_variations) == 0):
            raise ValueError("The number of existing variations equals 0, is the parameter study empty?")

        var_map = self.variation_number_parameter_mapping()
        self.add_paramaters_to_dataframes(var_map, study_data)
        self.merge_dataframes(study_data, list(var_map[0].keys()))
        ##----------------- old -------------
        #datapoints_per_variant = self.data_collector.datapoints_per_variant()

        ## Create a mutliindex for the collected data
        #study_index = self.multiindex_assembler.construct_multiindex(existing_variations, datapoints_per_variant)

        ## Create multiindexed dataframe
        #self.assemble_dataframe(study_data, study_index)
        ##-----------------------------------

        self.already_computed = True

    def assemble_output_name(self, file_name, path):
        """
        Assemble the output name for the multiindexed dataframe File name suffix is .csv.
        
        Uses the name of the variation file if an empty file name is passed.
        """
        if not file_name:
            file_name = self.variation_file_name.split('.')[0]

        return os.path.join(path, file_name)

    #--------------------------------------------------------------------------
    # Interface member functions
    #--------------------------------------------------------------------------
    def study_dataframe(self):
        """Return the multiindexed dataframe of the study."""
        self.compute_dataframe()

        return self.dataframe

    def write_agglomerated_study_data(self, file_name="", path=""):
        """
        Write the multiindexed dataframe to a CSV file.

        Without arguments, the file is written to the current folder using the name of the
        parameter study.
        Keyword arguments:
        file_name -- file name for the dataframe (default "")
        path      -- path for the dataframe file (default current_working_directory)
        """
        self.compute_dataframe()
        path_and_name = self.assemble_output_name(file_name, path)
        self.dataframe.to_csv(path_and_name + ".csv")
        self.dataframe.to_json(path_and_name + ".json", orient="table")


    def show_failed_variations(self):
        """Show a list of all variations present as directories but not containing valid data."""
        failed_variations = self.data_collector.failed_variations()

        # Only print if there failed variants
        if len(failed_variations) == 0:
            return

        print("Variants without valid data:")
        print("----------------------------")
        print("#Variation | Reason")
        print("----------------------------")

        for key, value in failed_variations.items():
            print(key, '\t', value)

def regex_from_study_directory_name(directory_name):
    """
    Generate a regular expression for the directory names of a study
    from a given example directory.
    """
    number_part = re.compile(r"_[0-9]{5}_")
    match = number_part.search(directory_name)
    directory_name = directory_name.replace(match.group(), r"_[0-9]{5}_")
    directory_name = directory_name.replace(".", r"\.")

    return r"^" + directory_name + r"$"

def split_path_from_pattern(directory_name):
    """
    Split the example directory name from the path to it.
    """
    if "/" not in directory_name:
        return ("", directory_name)
    else:
        return directory_name.rsplit("/", 1)
