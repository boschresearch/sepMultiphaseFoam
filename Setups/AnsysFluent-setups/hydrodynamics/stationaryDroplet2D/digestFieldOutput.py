'''
Parse Fluent ASCII output files which include complete field data,
extract the required information, write this information to a result file, 
and delete the ASCII file. This serves the purpose of minimizing disk
space usage while still allowing for flexible analysis. The script is 
called repeatedly during a simulation run and eats the files it finds at
each instant, provided they are complete.

Note that the output file is to be removed outside this script to avoid
appending to old results.
'''

import os
import sys
import re
import numpy as np

vxref = 0.
vyref = 0.

def rms(x,x0=0):
    return np.sqrt(np.mean(np.square(x-x0)))

# script is supposed to be executed from the respective "fluid pairing" directory
# output directories are inside this directory

if len(sys.argv) != 2:
    print("Wrong number of arguments! Need a <resolutionString>")
    sys.exit(1)
else:
    resolutionString = sys.argv[1]
    print(resolutionString)

numberOfCells = np.prod([int(x) for x in resolutionString.split("x")])

def importFluentASCII(file):
    '''
    Read Fluent results from an ASCII file and return headers and data.
    
    cellnumber,    x-coordinate,    y-coordinate,      y-velocity,      x-velocity
             1, 9.921875000E-03, 7.812500000E-05, 1.684623799E-08,-1.830643063E-08
             2, 9.921875000E-03, 2.343750000E-04,-2.629973565E-07,-3.100260964E-07
    '''
    names = []
    values = []
    with open(file,'r') as f:
        for count, line in enumerate(f):
            if count == 0:
                names = line.replace(',',' ').split()
            else:
                values.append([eval(x) for x in (line.replace(',',' ').split())])
    values = np.array(values)
    
    return names, values

rootDirectory = os.getcwd()#os.path.abspath(os.path.dirname(__file__))
print(rootDirectory)
outputDirectory = "output" + resolutionString

regexLogFileName = re.compile(r"out-(\S*).log") # regular expression for log file base names
regexResolution = re.compile(r"(\d+)x(\d+)") # regular expression to find <nx>x<ny> strings to extract resolution (2D only for now)
regexOutputDirectory = re.compile(r"output(\d+)x(\d+)") # regular expression to find <nx>x<ny> strings to extract resolution (2D only for now)

# rename the initial output because it would be harder to do in Fluent
if os.path.isfile(os.path.join(rootDirectory,outputDirectory,"out.log")):
    os.rename(os.path.join(rootDirectory,outputDirectory,"out.log"),os.path.join(rootDirectory,outputDirectory,"out-0.0.log"))

outfileFullPath = os.path.join(rootDirectory,"data_"+resolutionString+".log")
if not os.path.isfile(outfileFullPath):
    firstCall = True
else:
    firstCall = False

with open(outfileFullPath,'a') as outfile:
    if firstCall:
        outfile.write("time,max_error_velocity,mean_absolute_error_velocity,root_mean_square_deviation_velocity\n")
    for root, dirs, files in os.walk(os.path.join(rootDirectory,outputDirectory)):
        print([dir for dir in dirs])
        print([file for file in files])
        for infile in sorted(files): # sorting yields ascending time stamps
            infileFullPath = os.path.join(rootDirectory,outputDirectory,infile)
            if regexLogFileName.match(infile):
                found = regexLogFileName.findall(infile) # get time from file name
                if found == []:
                    currentTime = 0.
                else:
                    currentTime = float(found[0])
                
                names, values = importFluentASCII(infileFullPath)
                
                nRows, nColumns = values.shape
                
                if nColumns == len(names) and nRows == numberOfCells: # file completed?
                    print("removing " + infileFullPath)
                    try:
                        os.remove(infileFullPath)
                    except FileNotFoundError:
                        # not clear why this occurs but the
                        # file is gone afterwards, so it makes
                        # sense to accept the error
                        print("file " + infileFullPath + " could apparently not be deleted.")
                
                    idx = {k:v for v, k in enumerate(names)} # build an index dict

                    vx = values[:,idx["x-velocity"]] - vxref
                    vy = values[:,idx["y-velocity"]] - vyref
                    normOfDifferences=np.sqrt(vx**2+vy**2)
                    outfile.write(",".join((str(x) for x in [currentTime,np.amax(normOfDifferences),np.mean(normOfDifferences),rms(normOfDifferences)])))
                    outfile.write("\n")    
                else:
                    print("file " + infile + " not completed.")
            else:
                    print("skipped " + infile)
