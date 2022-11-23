#!/usr/bin/env python3

from argparse import ArgumentParser
from subprocess import run

import parameterStudyPreparation as psp

app_description="""Prepare the case directories for a given parameter study. Does not perform any
preprocessing steps like meshing or field initialization.
"""

def main():

    #---- Command line arguments ----------------------------------------------
    parser = ArgumentParser(description=app_description)

    parser.add_argument("parameter_file",
                        help="Name of the parameter file for the study")
    parser.add_argument("-p", "--prefix",
                        help="Prefix added to the name of the study folders. The result is prefix-parameter_file_00... etc.",
                        default="",
                        dest="studyprefix")
    parser.add_argument("-t", "--template-case",
                        help="Name of the template case directory. Default: templateCase",
                        default="templateCase",
                        dest="template_case")
    parser.add_argument("-v", "--variants",
                        help="Only use the specified variations. By default, all variations are used. Argument can either be a single number (e.g. 42), a list of numbers (e.g. '3,5,11') or a range ('3 - 10')",
                        default="all",
                        dest="variants")
    parser.add_argument("-d", "--directory",
                        help="Target directory where the study is moved to.",
                        default=None,
                        dest="target_dir")
    #--------------------------------------------------------------------------

    args = parser.parse_args()

    parameter_file = args.parameter_file
    case_name = args.template_case

    # Create vector of all variants to be set up
    variationNumbers = psp.create_variant_vector(args.variants)

    studyprefix = args.studyprefix
    if studyprefix:
        studyprefix = studyprefix + "-"
    full_prefix = studyprefix+args.parameter_file.rsplit('.', maxsplit=1)[0]

    # Create the variation file for the study
    var_file_name = full_prefix + ".variations"
    run("pyFoamRunParameterVariation.py --list-variations " \
        + case_name + " " + parameter_file + " > " + var_file_name, shell=True)

    # Assemble the parameter variation command according to the given options
    command =   ["pyFoamRunParameterVariation.py",
                 "--allow-derived-changes",
                 "--every-variant-one-case-execution",
                 "--create-database", 
                 "--no-server-process",
                 "--no-execute-solver",
                 "--no-post-templates",
                 "--no-final-templates",
                 "--no-mesh-create",
                 "--no-case-setup",
                 "--parameter-file=default.parameter",
                 "--cloned-case-prefix=" + full_prefix,
                 case_name,
                 parameter_file
                 ]

    # Finally, create the variations
    psp.setup_variants(command, variationNumbers)

    # Create shell script to submit the entire study
    script_content = \
    """
    #!/bin/bash

    for dir in DIRPATTERN*/ ; do
        cd $dir
        echo "Submitting case ${dir}"
        sh job-init-and-solve.sh
        cd ..

        # Don't overburden the job scheduler
        sleep .5
    done

    """
    script_content = script_content.replace("DIRPATTERN", full_prefix)
    script_name = "run_" + full_prefix + "_study.sh" 
    with open(script_name, 'w') as script_file:
        script_file.write(script_content)
    run("chmod +x " + script_name, shell=True)

    # Move study directories, variation file and run script to target location
    if args.target_dir:
        run("mv " + full_prefix + ".variations " + args.target_dir, shell=True)
        run("mv " + full_prefix + "_* " + args.target_dir, shell=True)
        run("mv " + script_name + " " + args.target_dir, shell=True)

    # Remove the *.database file
    run("rm -f *.parameter.database", shell=True)


if __name__ == "__main__":
    main()
