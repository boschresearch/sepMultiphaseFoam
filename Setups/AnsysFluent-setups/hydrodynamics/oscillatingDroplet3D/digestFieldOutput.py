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

# script is supposed to be executed from the respective "fluid pairing" directory
# output directories are inside this directory

if len(sys.argv) == 1:
    print("Wrong number of arguments! Need a <resolutionString>")
    sys.exit(1)
else:
    resolutionString = sys.argv[1]
    print(resolutionString)
    if len(sys.argv) == 3:
        noLimit = False
        maxFilesProcessed = int(sys.argv[2])
    else:
        noLimit = True
        maxFilesProcessed = 42

resolutions = [int(x) for x in resolutionString.split("x")]
numberOfCells = np.prod(resolutions)
numberOfOutputValues = 5
domainLength = 0.005
centerCoordinate = domainLength/2

def importFluentASCII(file):
    '''
    Read Fluent results from an ASCII file and return data.
    
        cellnumber,    x-coordinate,    y-coordinate,    z-coordinate,     droplet-vof
         1, 2.550000000E-03, 4.950000000E-03, 4.950000000E-03, 5.369074643E-07
         2, 2.650000000E-03, 4.950000000E-03, 4.950000000E-03, 5.369074643E-07
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

def findPositionBySummation(values, idx, alphaKey="droplet-vof", sliceLength = domainLength/2):
    '''
    Apply Tobi's suggestion and do an "integral" of alpha over a line of cells
    '''
    return sliceLength*(1/len(values)*np.sum(values[:,idx[alphaKey]]))

rootDirectory = os.getcwd()#os.path.abspath(os.path.dirname(__file__))
print(rootDirectory)
outputDirectory = "output" + resolutionString

regexLogFileName = re.compile(r"out-(\S*).log") # regular expression for log file base names

# rename the initial output because it would be harder to do in Fluent
if os.path.isfile(os.path.join(rootDirectory,outputDirectory,"out.log")):
    os.rename(os.path.join(rootDirectory,outputDirectory,"out.log"),os.path.join(rootDirectory,outputDirectory,"out-0.0.log"))

outfileFullPath = os.path.join(rootDirectory,"data_"+resolutionString+".log")
if not os.path.isfile(outfileFullPath):
    firstCall = True
else:
    firstCall = False

fileListFullPath = os.path.join(rootDirectory,"processed_files_"+resolutionString+".log")
def rememberFile(infileFullPath):
    with open(fileListFullPath,'a') as f:
        f.write(infileFullPath+"\n")

def fileAlreadyProcessed(infileFullPath):
    if os.path.isfile(fileListFullPath):
        with open(fileListFullPath,'r') as f:
            return any(infileFullPath in x.strip() for x in f) 
    return False


with open(outfileFullPath,'a') as outfile:
    if firstCall:
        outfile.write("time,major_semi_axis_length\n")
    for root, dirs, files in os.walk(os.path.join(rootDirectory,outputDirectory)):
        #print([dir for dir in dirs])
        print([file for file in files])
        for count, infile in enumerate(sorted(files)): # sorting yields ascending time stamps
            infileFullPath = os.path.join(rootDirectory,outputDirectory,infile)
            if (not fileAlreadyProcessed(infileFullPath)) and regexLogFileName.match(infile) and os.path.isfile(infileFullPath):
                rememberFile(infileFullPath)
                found = regexLogFileName.findall(infile) # get time from file name
                if found == []:
                    currentTime = 0.
                else:
                    currentTime = float(found[0])
                
                names, values = importFluentASCII(infileFullPath)
                
                #print(names)
                #print(values)

                nRows, nColumns = values.shape
                
                if not np.isnan(values).any(): # file completed?
                    print("removing " + infileFullPath)
                    try:
                        os.remove(infileFullPath)
                    except FileNotFoundError:
                        # not clear why this occurs but the
                        # file is gone afterwards, so it makes
                        # sense to accept the error
                        print("file " + infileFullPath + " could apparently not be deleted.")
                
                    idx = {k:v for v, k in enumerate(names)} # build an index dict

                    # recursively construct an index of relevant rows
                    masks = [-domainLength/resolutions[0] < values[:,idx["y-coordinate"]]-centerCoordinate,
                        values[:,idx["y-coordinate"]]-centerCoordinate<0,
                        -domainLength/resolutions[0] < values[:,idx["z-coordinate"]]-centerCoordinate,
                        values[:,idx["z-coordinate"]]-centerCoordinate<0,
                        values[:,idx["x-coordinate"]]-centerCoordinate<0
                     ]             

                    for n, m in enumerate(masks):
                        if n == 0:
                            mask = m
                        else:
                            mask = np.logical_and(mask,m)
                    # 
                    values = values[mask,:]
                    values = values[values[:,idx["x-coordinate"]].argsort()]

                    outfile.write(",".join((str(x) for x in [currentTime,findPositionBySummation(values=values,idx=idx)])))
                    outfile.write("\n")    

                    if (not noLimit) and count == maxFilesProcessed-1: 
                        break
                else:
                    print("file " + infile + " not completed.")
            else:
                    print("skipped " + infile)
