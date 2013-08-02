"""
This script calls singleRun.py which runs the application. This script handles the changing parameters and is called by automateRun.py
"""

from subprocess import call
import numpy as np
import csv, sys, os, itertools, shutil

def delAnalysis():
    path = "..\\Analysis\\Sweep " + sys.argv[2] + "\\" + sys.argv[1] + "\\"
    if not os.path.exists(path):
        return
    for dirs, subdirs, files in os.walk(path):
        for filename in files:
            if "Analysis.csv" in filename:
                os.remove(os.path.join(dirs,filename))
                
def delAnalysisFolder():
    path = "..\\Analysis\\Sweep " + sys.argv[2] + "\\" + sys.argv[1] + "\\"
    if not os.path.exists(path):
            return
    shutil.rmtree(path)

def loadData():
    """ Loads Data from grandparent directory """
    """
    path = "../../Data/July292011/"
    folders = os.listdir(path)
    for folder in folders:
        dataset[folder] = os.listdir(folder)
    """
    density = sys.argv[1]
    velocity = 0#sys.argv[2]

    dataset = dict()
    dataset["High"] = ["080","082","084","086","088","090","092","094","096"]
    dataset["TwoThirds"] = ["100","102","104","106","108","110","112","114","115","117","118"]
    dataset["OneThird"] = ["120","122","124","126","128","130","131","133","134","135","137","139"]
    dataset["OneQuarter"] = ["141","143","144","145","146","147","148","149","150","151","152"]
    dataset["OneEighth"] = ["154","155","156","157","159","160","162","163","164","165","166","168","169","170","171","172"]

    return density, dataset[density]

def runSequence():
    params = setParams()
    sweep_num = sys.argv[2]
    comblist = []
    paramlist = []
    for key in params:
        comblist.append(key[1])
        paramlist.append(key[0])
    combs = list(itertools.product(*comblist))
    
    sequence = 0
    for comb in combs: 
        sequence += 1
        print "------------------------------------------------------------"
        print "Running Sequence: ", sequence, "of ", len(combs), "\n"
        print "------------------------------------------------------------\n"
        with open("messenger.csv",'w') as f:
            writer = csv.writer(f, delimiter = ",", lineterminator = "\n")
            writer.writerow(paramlist)
            writer.writerow(comb)
        density, velocities = loadData()
        velocities = velocities[0:3]
        count = 0
        for velocity in velocities:
            count += 1
            print "------------------------------------------------------------"
            print "Running Velocity: ", count, "of ", len(velocities), "\n"
            print "------------------------------------------------------------\n"
            try:
                call(["python","singleRun.py",density,velocity,sweep_num])
            except:
                call(["python","notification.py",sys.argv[1],'5'])
                time.sleep(5)
                sys.exit()

            
            
            

def setParams():
    params = list()
    params.append(["maskLowThresh",[-10.0]])
    params.append(["maskHighThresh",[3.0]])
    params.append(["dilationRadius",[3.0]])
    params.append(["morphThreshold",[.2]])
    params.append(["blurSigma",[1.25]])
    params.append(["expThreshold",[.0005]])
    if sys.argv[1] == 'High':
        params.append(["trackSearchRadius",[1,1.5]])
    if sys.argv[1] == "TwoThirds":
        params.append(["trackSearchRadius",[1.5,2]])
    else:
        params.append(["trackSearchRadius",[2]])
    params.append(["trackMemory",[1,3,5,9,11,13]])
    params.append(["trackcutoff",[5,7,9,12]])
    return params

if __name__ == "__main__":
    delAnalysisFolder()
    runSequence()

                        

