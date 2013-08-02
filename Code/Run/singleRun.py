"""
Runs through the application once. This script is called by runSweep.py. The scaffold.Task classes for analysis are located
in this analysis.py. The script also contains the initialization of scaffold Context and Scheduler.
args: [Density][Velocity #][Sweep #]
"""
import tables, os, csv, sys
import numpy as np
import matplotlib.pyplot as plt
from subprocess import call
sys.path.insert(0,'../')
import images, particles, visual, scaffold, analysis


global sweep, valueChange
sweep = "Sweep " + sys.argv[3]

class TrackingAnalysis(scaffold.Task):
    """ Grabs the results from the analysis tracks and does further calculations before sending them to General Analysis """
    name = "Tracking Analysis"
    dependencies = [particles.TrackParticles]

    def isComplete(self):
        return None

    def run(self):  
        #Loads ellipses and tracks    
        self.ellipses = self.context.node("ellipses")
        self.trackData = np.array(self._import(particles.TrackParticles,"tracks"))
        #Writes tracks to csv
        cols = ["Time","Position","Velocity","Angle","Axes"]
        self.valueChange = scaffold._registeredParams["valueChange"].defaultValue
        self.writeData("tracking",self.trackData,cols)
        #Writes ellipses to csv
        cols = ["frame","position","angle","axes"]
        self.writeData("ellipses",np.array(self.ellipses),cols)
        self.trackLength = np.array(self._import(particles.TrackParticles,"trackLength"))
        #Calculates mean track length and mean ellipses count
        self.mean = np.mean(self.trackLength)
        self.numEllipses = self._trackDetection()

    def _trackDetection(self):
        group = particles.groupEllipsesByFrame(self.ellipses)
        numEllipses = []
        trackFrame = dict()
        dt = self.context.attrs.dt

        for row in group:
            numEllipses.append(len(self.ellipses[row]))

        for row in self.trackData:
            frame = int(row[0]/dt)
            trackFrame[frame] = trackFrame.get(frame,0) + 1

        for frame in range(len(numEllipses)):
            numEllipses[frame] = float(trackFrame.get(frame,0))/numEllipses[frame]

        return np.max(np.array(numEllipses))


    def writeData(self,key,nparray,cols):
        path = "..\\Analysis\\Sweep "+sys.argv[3]+"\\"+str(sys.argv[1])+"\\"+sys.argv[2]+"\\" + key + "\\"
        if not os.path.exists(path):
            os.makedirs(path)
        print "Writing to", path
        writer = csv.writer(open(path + "_".join([str(x) for x in self.valueChange[-3:]]) + ".csv",'wb'))
        writer.writerow(cols)
        for row in nparray: 
            writer.writerow(row)

    def export(self):
        return dict(trackValues = [self.mean] + [self.numEllipses])

class DetectionAnalysis(scaffold.Task):
    name = "Detection Analysis"
    dependencies = [particles.FindParticlesViaMorph]
    
    def isComplete(self):
        return None

    def run(self):
        ellipses = self._import(particles.FindParticlesViaMorph, "ellipses")
        group = particles.groupEllipsesByFrame(ellipses)
        self.avg_freq, numEllipses = self.SizeFreq(ellipses,group)
        self.standardDev, self.mean = self.EllipsesSTD(numEllipses)
        self.export()

    def export(self):
        return dict(writeValues = list(self.avg_freq[-4:-1]) + [self.standardDev/self.mean,self.mean])

    def SizeFreq(self, ellipses, group):
        i = 0
        numEllipses= [] 
        bins = 15
        total_freq = np.zeros(bins)
        for row in group:
            i += 1
            numEllipses.append(len(ellipses[row]["angle"]))
            axes = np.array(ellipses[row]["axes"])
            area = .5*np.pi*axes[:,0]*axes[:,1]
            freq, axis = np.histogram(area, bins = bins, range = (2,50))
            total_freq += freq
        avg_freq = total_freq/i
        avg_freq = np.around(avg_freq,decimals = 4)
        return avg_freq, numEllipses

    def EllipsesSTD(self, numEllipses):
        """ Gets the mean and STD of ellipses detected """
        standardDev = np.std(np.array(numEllipses))
        mean = np.mean(np.array(numEllipses))
        return standardDev, mean

    def plotHistogram(self,freq,axis,i):    
        width = .7 * (axis[1] - axis[0])
        centers = (freq[:-1] + freq[1:])/2
        plt.bar(centers,freq, align = 'center', width = width)
        if not os.path.exists("..\\Exported\\EllipseSize\\Histogram\\"):
            os.makedirs("..\\Exported\\EllipseSize\\Histogram\\")
        plt.savefig("..\\Exported\\EllipseSize\\Histogram\\histogram.png")

    def plotStandardDeviation(self,numEllipses):
        dt = self.context.attrs.dt
        time = np.linspace(0,len(numEllipses)*dt,len(numEllipses))
        plt.plot(time,numEllipses)
        plt.axis([0,time[-1],0,max(numEllipses)])
        plt.xlabel("Time (s)")
        plt.ylabel("Number of Ellipses Detected")
        plt.title("Number Detected over Time")
        plt.savefig(filename)
        plt.clf()

class Analysis(scaffold.Task):
    """ Grabs Data for Analysis and saves as .txt files"""
    name = "General Analysis"
    dependencies = [DetectionAnalysis,TrackingAnalysis]
    
    def isComplete(self):
        return None

    def run(self):
        """
        Data on ellipses: STD & Size
        Generates files named by parameters with data content.
        """
        analysisData = []
        valueChange = scaffold._registeredParams["valueChange"].defaultValue
        #analysisData += self._import(DetectionAnalysis,"writeValues")
        analysisData += self._import(TrackingAnalysis,"trackValues")
        print "analysisData",analysisData
        #Writer
        filename = "..\\Analysis\\Sweep "+sys.argv[3]+"\\"+str(sys.argv[1])+"\\"+sys.argv[2]+"/Analysis.csv"
        f = csv.writer(open(filename,'a'))
        f.writerow(valueChange+analysisData)

    def export(self):
        return None

def checkPrevRun():
    """ Checks for previous identical runs """
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

def setParams():
    """ Sets the parameters for the Run """
    with open("messenger.csv",'r') as f:
        """ Receives run parameters from sweepParams.py """
        inputs = list(csv.reader(f))
        keyChange = inputs[0]
        valueChange = np.array(inputs[1]).astype(float)
        valueChange = list(np.around(valueChange,5))
        params = dict(zip(keyChange,valueChange))
        for key in ["trackMemory", "maskLowThresh", "dilationRadius","trackcutoff"]:
            params[key] = int(params[key])

    scaffold.registerParameter("valueChange", valueChange) 
    """Current parameter values swept."""   
    for i in range(len(keyChange)):
        print "Setting ", keyChange[i], " as ", valueChange[i]  
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
               "plotDensityFieldOutput.avi",
               "plotVelocityFieldOutput.avi"]

    params["configFile"] = "..\\..\\Data\\July292011\\" + str(density) + "\Series" + str(filename) + "_Properties.xml"

    for key in outputs:
        filepath = "..\\Analysis\\"+sweep+"\\"+str(density) + "\\" + str(filename) + "\\" + key[:-4] +"\\" 
        name = "_".join([str(x) for x in valueChange[-3:]]) + key[-4:]
        params[key[:-4]] =  filepath + name
        if not os.path.exists(filepath):
            os.makedirs(filepath)
    return params

def makeContext():
    """ Creates the context for the application """
    f = tables.openFile("test.h5", "w")
    local = f.createGroup("/", "test")
    params = setParams()
    print "Currently Running Image Stack:", params['configFile'], "\n"
    return scaffold.Context(f, local, params)

def runSeq(context):
    """ Set up the Context and Scheduler """
    if checkPrevRun():
        print "\nParameter Set has already been swept."
        print "-------------------------------------"
        #sys.exit()
    s = scaffold.Scheduler()
    #s.addTask(images.ComputeForegroundMasks)
    #s.addTask(images.RemoveBackground)
    #s.addTask(images.Watershed)

    #s.addTask(visual.RenderSeedImages)
    s.addTask(visual.RenderEllipses)
    s.addTask(visual.RenderTracks)
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

    s.addTask(visual.PlotVelocityField)
    #s.addTask(visual.PlotDensityField)

    #s.addTask(printConfig)
    #s.addTask(visual.PlotParticleDistance)
    s.addTask(Analysis)
    s.run(context, forceRedo=False)



def extractId(context):
    scaffold.Scheduler([images.ExtractUniqueId]).run(context)

if __name__ == "__main__":
    c = makeContext()
    try:
        extractId(c)
        runSeq(c)
    finally:
        c.hdf5.close()

   
    
        

                                
                                
                                

