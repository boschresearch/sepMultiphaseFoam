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
numberOfOutputValues = 4
domainLength = 0.0026
centerCoordinate = domainLength/2

def find_nearest_idx(array, value, numIdcs=5):
    array = np.asarray(array)
    idcs = (np.abs(array - value)).argsort()
    return idcs[:numIdcs]

def findPositionByInterpolation(values, idx, centerCoordinate=centerCoordinate, normalCoordinateKey="y-coordinate", alphaKey="wave-vof"):
    posIdcs = find_nearest_idx(values[:,idx[alphaKey]],0.5,10)

    posIdx = posIdcs[find_nearest_idx(values[posIdcs,idx[normalCoordinateKey]],centerCoordinate,1)][0]

    posList = [posIdx+x for x in range(-3,4)]
    posList = [x for x in posList if (x >= 0 and x < len(values))]
    if not (np.all(np.diff(values[posList,idx[alphaKey]]) > 0)):# values must be increasing!
        posList = np.flip(posList,axis=0)

    return np.interp(0.5,values[posList,idx[alphaKey]],values[posList,idx[normalCoordinateKey]]) - centerCoordinate

def zeroAtInterface(y, values, normalCoordinateKey="y-coordinate", alphaKey="wave-vof"):
    '''
    Function returns zero at the y coordinate where alpha = 0.5
    '''
    return np.interp(y,values[:,idx[normalCoordinateKey]],values[:,idx[alphaKey]]) - 0.5

import scipy.optimize as opt
def findPositionByRoot(values, idx, offset=centerCoordinate, normalCoordinateKey="y-coordinate", alphaKey="wave-vof", minCoordinate=0, maxCoordinate=domainLength):
    sol, r = opt.brentq(lambda x : zeroAtInterface(x, values=values), minCoordinate, maxCoordinate, full_output=True)

    return sol - offset if r.converged else 0

def findPositionBySummation(values, idx, alphaKey="wave-vof", sliceLength = domainLength, offset=centerCoordinate):
    '''
    Apply Tobi's suggestion and do an "integral" of alpha over a line of cells
    '''
    return -(sliceLength*(1 - 1/len(values)*np.sum(values[:,idx[alphaKey]]))-offset)

def importFluentASCII(file):
    '''
    Read Fluent results from an ASCII file and return data.
    
        cellnumber,    x-coordinate,    y-coordinate,        wave-vof
         1, 2.559375000E-03, 4.062500000E-05, 9.999867687E-01
         2, 2.559375000E-03, 1.218750000E-04, 9.999858653E-01
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
if not os.path.isfile(outfileFullPath):
    firstCall = True
else:
    firstCall = False

lastTimeStepFile = os.path.join(rootDirectory,"last_"+resolutionString+".log")
with open(outfileFullPath,'a') as outfile:
    if firstCall:
        outfile.write("time,amplitude_at_center,amplitude_at_center_root,amplitude_at_center_interp\n")
    for root, dirs, files in os.walk(os.path.join(rootDirectory,outputDirectory)):
        #print([dir for dir in dirs])
        print([file for file in files])
        for count, infile in enumerate(sorted(files)): # sorting yields ascending time stamps
            infileFullPath = os.path.join(rootDirectory,outputDirectory,infile)
            if regexLogFileName.match(infile):
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
                        #pass
                        os.remove(infileFullPath)
                    except FileNotFoundError:
                        # not clear why this occurs but the
                        # file is gone afterwards, so it makes
                        # sense to accept the error
                        print("file " + infileFullPath + " could apparently not be deleted.")
                
                    idx = {k:v for v, k in enumerate(names)} # build an index dict

                    # recursively construct an index of relevant rows
                    masks = [-domainLength/resolutions[0] < values[:,idx["x-coordinate"]]-centerCoordinate,
                        values[:,idx["x-coordinate"]]-centerCoordinate<0#,
                        #values[:,idx["y-coordinate"]]<centerCoordinate+20e-5,
                        #values[:,idx["y-coordinate"]]>centerCoordinate-20e-5
                        #values[:,idx["wave-vof"]] > 1e-1,
                        #values[:,idx["wave-vof"]] < 0.9
                     ]             

                    for n, m in enumerate(masks):
                        if n == 0:
                            mask = m
                        else:
                            mask = np.logical_and(mask,m)
                    # 
                    values = values[mask,:]
                    values = values[values[:,idx["y-coordinate"]].argsort()]
                    
                    outfile.write(",".join((str(x) for x in [currentTime,findPositionBySummation(values=values, idx=idx),findPositionByRoot(values=values, idx=idx),findPositionByInterpolation(values=values, idx=idx)])))
                    outfile.write("\n")    

                    if (not noLimit) and count == maxFilesProcessed-1: 
                        break
                else:
                    print("file " + infile + " not completed.")
            else:
                    print("skipped " + infile)
