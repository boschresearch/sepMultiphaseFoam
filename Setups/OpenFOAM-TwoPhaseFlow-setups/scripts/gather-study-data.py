#!/usr/bin/env python3

from argparse import ArgumentParser

import dataAgglomeration as da

def main():

    #---- Command line arguments ----------------------------------------------
    parser = ArgumentParser(description="Gather the data of a parameter study from its corresponding directories into a single, multiindexed pandas dataframe. Data is saved as CSV and JSON.")

    parser.add_argument("path_to_data_file")
    parser.add_argument("-v", "--variation-file",
                        help="Test file containing the mapping of variation number to parameter vector.",
                        required=True,
                        dest="variation_file_name"
                        )
    parser.add_argument("-f", "--file-name",
                        help="Write agglomerated data to this file. If not given, use name of variation file.",
                        required=False,
                        default="",
                        dest="target_file_name"
                        )

    args = parser.parse_args()

    example_directory, file_path_and_name = args.path_to_data_file.split('/', maxsplit=1)

    agglomerator = da.data_agglomerator(args.variation_file_name, file_path_and_name, example_directory)
    agglomerator.show_failed_variations()
    agglomerator.write_agglomerated_study_data(args.target_file_name)

if __name__ == "__main__":
    main()
