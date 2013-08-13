"""
Runs through the application once. This script is called by runSweep.py. The scaffold.Task classes for analysis are located
in this analysis.py. The script also contains the initialization of scaffold Context and Scheduler.
args: [Density][Velocity #][Sweep Folder Name]

:Edited: August 13, 2013 - contact(sihrc.c.lee@gmail.com)
"""
import tables, os, csv, sys
import numpy as np
sys.path.insert(0,'../') #Adds parent directory to PYTHONPATH to check for modules before STDLIBs
import images, particles, visual, scaffold, analysis

global sweep, valueChange
sweep = "Sweep " + sys.argv[3]

def onexit():
    """ Runs on exit to clean up files """
    [os.remove(os.path.join('.\\images',filename)) for filename in os.listdir(".\\images")]

def checkPrevRun():
    """ Checks for previous identical runs to prevent running identical sweeps"""
    path = "..\\Analysis\\"+sweep+"\\"+str(sys.argv[1])+"\\"+sys.argv[2]+"\\Analysis.csv"
    if not os.path.exists(path):
        csv.writer(open(path,'wb'))
    flag = 0
    if os.path.exists(path):
        checkFile = csv.reader(open(path,'r'))
        for line in checkFile:
            param = [str(num) for num in scaffold._registeredParams["valueChange"].defaultValue]
            if param == line[:len(param)]:
                return True
    return False



    scaffold.registerParameter("default_", 'default') 
    """ Default => no params are being swept """

    scaffold.registerParameter("valueChange", valueChange) 
    """Current parameter values swept."""   
    for i in range(len(keyChange)):
        print "Setting ", keyChange[i], " as ", params[keyChange[i]]
    print "\n"

    density = sys.argv[1]
    filename = sys.argv[2]

    outputs = ["renderRemovedBackgroundOutput.avi",
               "renderSeedImagesOutput.avi",
               "renderDiffsOutput.avi",
               "renderMasksOutput.avi",
               "renderMorphedImagesOutput.avi",
               "renderWatershedOutput.avi",
               "renderRegionsOutput.avi",
               "renderEllipsesOutput.avi",
               "renderTracksOutput.avi",
               "plotParticleDistanceOutput.png",
               "plotPIVFieldOutput.mp4",
               "plotDensityFieldOutput.avi",
               "plotVelocityFieldOutput.avi"]

    params["configFile"] = "..\\..\\Data\\July292011\\" + str(density) + "\Series" + str(filename) + "_Properties.xml"

    for key in outputs:
        filepath = "..\\Analysis\\"+sweep+"\\"+str(density) + "\\" + str(filename) + "\\" + key[:-4] +"\\" 
        name = "_".join(valueChange).replace(".","") + key[-4:]
        params[key[:-4]] =  filepath + name
        if not os.path.exists(filepath):
            os.makedirs(filepath)
    return params


class viewData(scaffold.Task):
    """
    Contains an example of how to call/view the analysis data
    As well as creating a simple task.
    """
    name = "Viewing Data"
    functions = [analysis.CorrelateParticleDistance,
                analysis.CorrelateDirectorVelocities,
                analysis.CorrelateDirectors,
                analysis.CorrelateVelocities]
    dependencies = [functions[3]]

    def run(self):
        data = np.array(self._import(self.dependencies[0],"table"))
        print data

def setParams():
    """ Sets the parameters for the Run
    This is done using file i/o for record and order 
    of parameters """

    with open("messenger.csv",'r') as f:
        """ Receives run parameters from sweepParams.py """
        inputs = list(csv.reader(f))
        keyChange = inputs[0]
        valueChange = inputs[1]
        params = dict(zip(keyChange,valueChange))

def makeContext():
    """ Creates the context for the application """
    f = tables.openFile("test.h5", "w")
    local = f.createGroup("/", "test")
    params = setParams()
    print "Currently Running Image Stack:", params['configFile'], "\n"
    return scaffold.Context(f, local, params)

def runSeq(context):
    """ Set up the Context and Scheduler 
    - Add Tasks in this function
    """
    if checkPrevRun():
        print "\nParameter Set has already been swept."
        print "-------------------------------------"
        #sys.exit()
    s = scaffold.Scheduler()
    #s.addTask(images.ComputeForegroundMasks)
    #s.addTask(images.RemoveBackground)
    #s.addTask(images.Watershed)

    #s.addTask(particles.PIVTracking)
    #s.addTask(visual.RenderSeedImages)
    #s.addTask(visual.RenderEllipses)
    #s.addTask(visual.RenderTracks)
    #s.addTask(visual.RenderDifferences)
    #s.addTask(visual.RenderForegroundMasks)
    #s.addTask(visual.RenderRemovedBackground)
    #s.addTask(visual.RenderWatershed)
    #s.addTask(visual.RenderRegions)

    #s.addTask(analysis.CalculateDensityField)
    #s.addTask(analysis.CalculateVelocityField)
    #s.addTask(analysis.CalculateLocalVelocityCorrelationField)

    #s.addTask(analysis.CorrelateParticleDistance)
    #s.addTask(analysis.CorrelateDirectorVelocities)
    #s.addTask(analysis.CorrelateDirectors)
    #s.addTask(analysis.CorrelateVelocities)
    
    #s.addTask(visual.PlotPIVField)
    #s.addTask(visual.PlotVelocityField)
    #s.addTask(visual.PlotDensityField)
    #s.addTask(visual.PlotParticleDistance)
    
    #s.addTask(viewData)
    s.run(context, forceRedo=False)



def extractId(context):
    scaffold.Scheduler([images.ExtractUniqueId]).run(context)
    #atexit.register(onexit)
if __name__ == "__main__":
    import atexit
    c = makeContext()
    try:
        extractId(c)
        runSeq(c)
    finally:
        c.hdf5.close()

   
    
        

                                
                                
                                

