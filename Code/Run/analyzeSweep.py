"""
This script reads the results of the runs and compiles the data
into a csv file named sweepresults.csv. It also runs additional 
analysis calculations and creates optional plots to reflect the
results of the data.

:Edited: August 13, 2013 - contact(sihrc.c.lee@gmail.com)
"""
import itertools as it
import numpy as np
import csv, sys, os, collections
import matplotlib.pyplot as plt
from subprocess import call
def retrieveData(path):
	""" Returns a dictionary of data for densities"""
	print "-----------------------------------------"
	print "             Retrieving Data"
	print "-----------------------------------------"
	data = dict()
	for dirs,subdirs,files in os.walk(path):
		for filename in files:
			if "Analysis.csv" == filename:
				sweep = "Sweep " + sys.argv[1] + "\\"
				grandparent = dirs.find(sweep) + len(sweep)
				parent = dirs[grandparent:].find("\\")
				dens = dirs[grandparent:grandparent + parent]
				velocity = dirs[grandparent + parent + 1:]
				currAnalysis = csv.reader(open(os.path.join(dirs,filename),"r"))
				curr = np.array(list(currAnalysis)).astype('float')
				data[dens+velocity] = curr
				print "Retrieved", len(curr), "from", dens, "Density at velocity:", velocity
	return data


def writeCSV(data):
	#Sweep Path
	path = "..\\Analysis\\Sweep " + sys.argv[1] + "\\"
	#Opening CSV file
	writer = csv.writer(open(path + "Sweepresults.csv",'wb'))
	keys = [key for key,values in data.items()]
	keys.sort()
	for key in keys:
		print key
		if len(data[key]) > 0:
			writer.writerow([key])
			#writer.writerow(["maskLowThresh","maskHighThresh","dilationRadius","morphThreshold","blurSigma","expThreshold","Size:46","Size:43","Size: 39","Population Size","STD Percent"])
			writer.writerow(["maskLowThresh","maskHighThresh","dilationRadius","morphThreshold","blurSigma","expThreshold","trackSearchRadius","trackMemory","Mean Track Length","Mean Track Count"])
			for line in data[key]:
				writer.writerow(line)
	print "Finished Writing new CSV File."
	return path + "Sweepresults.csv"

def plotWizard(data):
	varname = ["maskLowThresh","maskHighThresh","dilationRadius","morphThreshold","blurSigma","expThreshold"]
	for key,value in data.items():
		paramSet = value[:,:6]
		print "------------------------------------------------------------"
		print "   Currently Running Plot Sequence for", key, "Density"
		print "------------------------------------------------------------"
		print "==Starting=="
		counter = 0
		for currParams in paramSet:
			counter += plotSearch(currParams, paramSet, varname, key, value)
		print "\nFound", counter, "plots that exists in this Directory\n"
		print "==Completed=="

def plotSearch(currParams, paramSet, varname, key, value):
	counter = 0
	for n in range(len(varname)):
		indices = np.where(np.prod(np.concatenate(((currParams[:n] == paramSet[:,:n]),(currParams[n+1:] == paramSet[:,n+1:])),axis = 1), axis = 1))[0]
		path = "..\\Analysis\\Plots\\Sweep " + sys.argv[1] + "\\"+ key + "\\" + str(varname[n]) + "\\"
		if not os.path.exists(path):
			os.makedirs(path)
		if len(indices) > 1:
			name = [str(f) for f in currParams]
			name[n] = 'var'
			name = "_".join(name)
			if os.path.exists(path+name+".png"):
				counter =+ 1
			else:
				createPlots(value,indices,path,name,n,varname)
	return counter


def createPlots(value,indices,path,name,n, varname):
	plotdata = value[indices,:-2]
	f, axarr = plt.subplots(4, sharex=True)
	f.tight_layout()
	f.figsize = (8.0,11.0)
	axarr[0].set_title("Inaccuracy")
	axarr[2].set_title("STD Percentage of Population")
	axarr[1].set_title("Population")
	axarr[3].set_title("Particle Size Frequencies")
	axarr[0].plot(plotdata[:,n],plotdata[:,-1])
	axarr[1].plot(plotdata[:,n],plotdata[:,-2])
	axarr[2].plot(plotdata[:,n],plotdata[:,-3])
	for i in [-6,-5,-4]:
		axarr[3].plot(plotdata[:,n],plotdata[:,i])
	axarr[3].legend(["Size39", "Size43", "Size46"])
	axarr[3].set_xlabel(varname[n])
	f.savefig(path+name+".png",bbox_inches='tight',dpi=100)
	print "Saved figure to ", path+name+".png"
	plt.clf()

def sidebyside(path):
	filepath = path + "Sweepresults.csv"
	index = int(raw_input("Enter Integer Line Number:"))
	reader = csv.reader(open(filepath,'rb'))
	for row in reader:
		if len(row) == 1:
			densCount = row[0]
		if reader.line_num == index:
			dens = densCount[:-3]
			vel = densCount[-3:]
			video1 = "..\\..\\TrackingVideos\\" + dens + "\\" + vel + "\\" + dens+vel+'.avi'
			video2 = "..\\Analysis\\Sweep " + sys.argv[1] + "\\" + dens + "\\" + vel + "\\renderTracksOutput\\" + "_".join(row[6:9]) + '_.avi'
			break
	lines = []
	lines.append('video1=DirectShowSource("' + video1 + '")')
	lines.append('video2=DirectShowSource("' + video2 + '")')
	lines.append("StackHorizontal(video1,video2).AssumeFPS(.1)")

	with open("play.avs",'wb') as f:
		for line in lines:
			f.write(line)

	call(["mplayer",'play.avs'],shell=True)

def playvideo(path):
	filepath = path + "Sweepresults.csv"
	index = int(raw_input("Enter Integer Line Number:"))
	reader = csv.reader(open(filepath,'rb'))
	for row in reader:
		if len(row) == 1:
			densCount = row[0]
		if reader.line_num == index:
			dens = densCount[:-3]
			vel = densCount[-3:]
			video1 = path + dens + "\\" + vel + "\\" + "renderTracksOutput\\" + "_".join(row[6:9])+'_.avi'
			video2 = path + dens + "\\" + vel + "\\" + "plotVelocityFieldOutput\\" + "_".join(row[6:9])+'.avi'
			print "Playing Video:", video1, video2 
			break
	lines = []
	#lines.append('video1=DirectShowSource("' + video + '").AssumeFPS(1.0)')
	#lines.append('video1=DirectShowSource("' + video + '")')
	#lines.append('video1')
	#with open("play.avs",'wb') as f:
	#	for line in lines:
	#		f.write(line)
	command = 'vlc --rate .1 ' + '"'+video1+'"'
	command2 = 'vlc --rate .1 ' + '"'+video2+'"'
	os.system(command)
	os.system(command2)
	

if __name__ == "__main__":
	path = "..\Analysis\Sweep " + sys.argv[1] + "\\"
	if not os.path.exists(path + "Sweepresults.csv"):
		data = retrieveData(path)
		compiled = writeCSV(data)
	else:
		ans = raw_input('Rewrite CSV file?')
		if ans == "y":
			data = retrieveData(path)
			compiled = writeCSV(data)
	#sidebyside(path)
	playvideo(path)
	#plotWizard(data)