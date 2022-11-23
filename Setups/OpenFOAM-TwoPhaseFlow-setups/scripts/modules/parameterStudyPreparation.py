# parameterStudyPreparation.py

import subprocess

def create_variant_vector(variantArgument):
    """ Parse the string of the variants to be set up and return it as a list.
        The given string may contain integer numbers separated by ',' or by
        '-' to indicate a range which includes the given start and end value.
    """

    variants = list()

    # No need for additional parsing if all variants shall be set up
    if variantArgument == "all":
        variants.append(variantArgument)
        return variants

    splittedArgument = variantArgument.split(',')

    for element in splittedArgument:
        if '-' in element:
            start = int(float(element.split("-")[0]))
            end = int(float(element.split("-")[1]))
            for number in range(start, end+1):
                variants.append(str(number))
        else:
            if element.isdigit():
                variants.append(str(element))
            else:
                print("Error: ",element," is not a number."
                        " Only ',' and '-' are allowed as non-digit characters.")

    return variants


def setup_variants(command, variants):
    """ Execute the command (should be pyFoamRunParameterVariation.py) for
        all variants.
    """

    if variants[0] == "all":
        status = subprocess.run(command)
        print(status.stdout)
    else:
        command.append("--single-variation=")
        for variant in variants:
            command[-1] = "--single-variation="+variant
            status = subprocess.run(command)
            print(status.stdout)
