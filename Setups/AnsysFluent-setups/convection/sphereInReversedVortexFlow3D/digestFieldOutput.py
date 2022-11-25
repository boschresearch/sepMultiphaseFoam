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

def rms(x,x0=0):
    return np.sqrt(np.mean(np.square(x-x0)))

# script is supposed to be executed from the respective "fluid pairing" directory
# output directories are inside this directory

if len(sys.argv) == 1:
    print("Wrong number of arguments! Need a <resolutionString>")
    sys.exit(1)
else:
    resolutionString = sys.argv[1]
    print(resolutionString)

domainLengths = [1., 1., 1.]
resolutions = [int(x) for x in resolutionString.split("x")]
numberOfCells = np.prod(resolutions)
cellVolume = np.prod(domainLengths)/numberOfCells
numberOfOutputValues = 5

def importFluentASCII(file):
    '''
    Read Fluent results from an ASCII file and return data.
    
    cellnumber,    x-coordinate,    y-coordinate,    z-coordinate,     droplet-vof
         1, 8.359375000E-01, 5.234375000E-01, 7.812500000E-03, 1.018168405E-06
         2, 8.515625000E-01, 5.234375000E-01, 7.812500000E-03, 1.011416316E-06
         3, 8.359375000E-01, 5.390625000E-01, 7.812500000E-03, 1.015607268E-06
    '''
    names = []
    values = np.zeros((numberOfCells,numberOfOutputValues))
    values[:] = np.nan
    with open(file,'r') as f:
        for count, line in enumerate(f):
            if count == 0:
                names = line.replace(',',' ').split()
            else:
                values[count-1,:] = np.fromstring(line, sep=',')
    
    return names, values

rootDirectory = os.getcwd()#os.path.abspath(os.path.dirname(__file__))
print(rootDirectory)
outputDirectory = "output" + resolutionString

regexLogFileName = re.compile(r"out-(\S*).log") # regular expression for log file base names

# rename the initial output because it would be harder to do in Fluent
if os.path.isfile(os.path.join(rootDirectory,outputDirectory,"out.log")):
    os.rename(os.path.join(rootDirectory,outputDirectory,"out.log"),os.path.join(rootDirectory,outputDirectory,"out-0.0.log"))

outfileFullPath = os.path.join(rootDirectory,"data_"+resolutionString+".log")

with open(outfileFullPath,'w') as outfile:
    outfile.write("L1_SHAPE_ERROR\n")

    for root, dirs, files in os.walk(os.path.join(rootDirectory,outputDirectory)):
        #print([dir for dir in dirs])
        print([file for file in files])
        values = np.zeros((2,numberOfCells,numberOfOutputValues))
        for count, infile in enumerate(sorted(files)): # sorting yields ascending time stamps
            infileFullPath = os.path.join(rootDirectory,outputDirectory,infile)
            if regexLogFileName.match(infile):
                found = regexLogFileName.findall(infile) # get time from file name
                if found == []:
                    currentTime = 0.
                else:
                    currentTime = float(found[0])
                
                names, values[count] = importFluentASCII(infileFullPath)
                
                #print(names)
                #print(values)
                values[count] = (values[count])[(values[count])[:, 0].argsort()] # sort by cell number

                nRows, nColumns = values[count].shape
                
                if not np.isnan(values[count]).any(): # file completed?
                    '''
                    print("removing " + infileFullPath)
                    try:
                        os.remove(infileFullPath)
                    except FileNotFoundError:
                        # not clear why this occurs but the
                        # file is gone afterwards, so it makes
                        # sense to accept the error
                        print("file " + infileFullPath + " could apparently not be deleted.")
                    '''

                    if count==0:
                        idx = {k:v for v, k in enumerate(names)} # build an index dict
                    elif count==1:
                        volumeError = 0.
                        for vals in zip(values[0],values[1]):
                            volumeError += cellVolume * abs(vals[1][4]-vals[0][4])

                        outfile.write(str(volumeError))
                        outfile.write("\n")  
                    else:
                        print("Found too many output files!")

  

                else:
                    print("file " + infile + " not completed.")
            else:
                    print("skipped " + infile)
