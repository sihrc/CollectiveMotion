"""
This script is run on alternate computers to allow for distributed 
computing. This script is called by remoteCommand.py. 

:Edited: August 13, 2013 - contact(sihrc.c.lee@gmail.com)
"""
from subprocess import call
import sys, os, shutil

def checkDir(sweep):
	""" 
	Checks for sweep Directory. It is best not to make a directory 
	manually and simply allow this function to create the directories
	as necessary.
	"""
	if not os.path.exists("Z:\\2013 Summer\\Code\\Analysis\\STD\\Sweep " + sweep + "\\") or not os.path.exists("..\\Analysis\\STD\\Sweep " + sweep + "\\"):
		call(["python","makeDirs.py", sweep])
		print "Made new sweep directories."
	if not os.path.exists("..\\..\\Data"):
		shutil.copy("Z:\\2013 Summer\\Data\\","..\\..\\Data")
def clearSweepFiles(sweep):
	path = "..\\Analysis\\Sweep " + sweep + "\\"
	print "Removing Sweep Files"
	shutil.rmtree(path)
	return
if __name__ == "__main__":
	sweep = sys.argv[1]
	computer = int(sys.argv[2])
	runs = ["High", "TwoThirds", "OneThird", "OneQuarter", "OneEighth","ACCOMP"]
	print "-------------------- Beginning Automated Run --------------------"
	print "Computer: ", computer, runs[computer-1], " Density"
	print "Running Sweep: ", sweep
	print "Command Issued by:\nChris Lee - christopher.lee@students.olin.edu\n\n"

	"""
	The following is the process through which each computer runs
	before completion.
	"""
	if computer == 6:
		call(["python", "notification.py", 'ACCOMP',"0"])
		call(["python", "synchronize.py", "pull", "[.py]"])
		call(["python", "runSweep.py", runs[0],'HighPIV'])
		call(["python", "notification.py", 'ACCOMP',"m","FINISHED HIGH"])
		call(["python", "runSweep.py", runs[1],'TwoThirdsPIV'])
		call(["python", "notification.py", 'ACCOMP',"3"])
	else:
		checkDir(sweep)
		call(["python", "notification.py", runs[computer - 1],"0"])
		call(["python", "synchronize.py", "pull", "[.py]"])
		call(["python", "notification.py", runs[computer - 1],"1"])
		call(["python", "runSweep.py", runs[computer - 1],sweep])
		call(["python", "notification.py", runs[computer - 1],"2"])
		call(["python", "synchronize.py", "push", "[.avi,.csv]"])
		clearSweepFiles(sweep)
		call(["python", "notification.py", runs[computer - 1],"3"])
	
	
