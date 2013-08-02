""" Prints all the current configs and parameters for the context """
import sys, tables
sys.path.insert(0,'../')
import images, particles, visual, scaffold, analysis

def setParams():
    """ Sets the parameters for the Run """
    density = sys.argv[1]
    filename = sys.argv[2]
    params = dict()
    params["configFile"] = "..\\..\\Data\\July292011\\" + density + "\Series" + str(filename) + "_Properties.xml"
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
    s = scaffold.Scheduler()
    s.addTask(printConfig)
    s.run(context, forceRedo=False)

class printConfig(scaffold.Task):
    name = "Printing Configs"
    dependencies = [images.ParseConfig]

    def run(self):
        a = self.context.attrs
        listattr = [a.name,a.seriesNum,a.length,a.pixel,a.shape,a.duration,a.timeString,a.startTime,a.dt,a.imageSize,a.channel]
        stringattr = ["name","seriesNum","length","pixel","shape","duration","timeString","startTime","dt","imageSize","channel"]
        with open('configFile.txt','wb') as f:
            for item in range(len(listattr)):
                print stringattr[item].upper(), ": ",listattr[item]
                f.write(stringattr[item].upper() + ":" + str(listattr[item]) + "\r\r\n")

    def isComplete(self):
        return None

    def export(self):
        return None

def extractId(context):
    scaffold.Scheduler([images.ExtractUniqueId]).run(context)

if __name__ == "__main__":
    c = makeContext()
    try:
        extractId(c)
        runSeq(c)
    finally:
        c.hdf5.close()
