""" This code merges sweep results across several sweep folders into a sweep folder with all the analysis.csv and .avi files """
import csv, os, sys, shutil, time
import numpy as np
def MergeSweeps():
	path = "..\\..\\Analysis\\"
	dest = os.path.join(path,'Sweep ' + sys.argv[1])
	for folder in os.listdir(path):
		if 'Sweep' in folder and folder != 'Sweep ' + sys.argv[1]:
			for dirs, subdirs, files in os.walk(os.path.join(path,folder)):
				for filename in files:
					filepath = os.path.join(dirs,filename)
					print filepath
					sweepindex = filepath.find('Sweep ')
					endindex = sweepindex + filepath[sweepindex:].find("\\")
					destpath = filepath[:sweepindex] +'Sweep ' + sys.argv[1] + filepath[endindex:]
					if os.path.exists(destpath):
						if 'Analysis' in filename:
							i = 1
							while os.path.exists(destpath):
								destpath = destpath[:-4] + str(i) + '.avi'
								i += 1
							shutil.copy(filepath,destpath)
	print 'Done Merging Folders'
	time.sleep(5)



def Merge(path):
	csvFiles = []
	for files in os.listdir(path):
		if "Analysis" in files:
			csvFiles.append(files)
	if len(csvFiles) < 2:
		return None
	for csvfile in csvFiles:
		currFile = os.path.join(path,csvfile)
		print currFile
		if os.stat(currFile).st_size == 0:
			os.remove(currFile)
		else:
			with open(os.path.join(path,csvfile),'rb') as f:
				reader = csv.reader(f)
				for line in reader:
					if 'final' not in locals():
						print "Initialized Combined Data Set"
						final = np.array([line])
					if line not in final.tolist():
						print "Appended to Combined Data Set"
						final = np.concatenate((final,np.array([line])))
					else:
						print "Already Exists in Combined Data Set"

	if 'final' in locals():
		final = final[np.lexsort((final[:,7],final[:,6]))]
		writer = csv.writer(open(os.path.join(path,"Analysis.csv"),'wb'))
		writer.writerows(final)

	for files in csvFiles:
		if files != "Analysis.csv":
			if os.path.exists(os.path.join(path,files)):
				print "Removed:", files
				os.remove(os.path.join(path,files))
	return 1

if __name__ == "__main__":
	path = "C:\\Users\\clee2\\Documents\\2013 Summer\\Code\\Analysis\\Sweep " + sys.argv[1]

	dataset = dict()
	dataset["High"] = ["080","082","084","086","088","090","092","094","096"]
	dataset["TwoThirds"] = ["100","102","104","106","108","110","112","114","115","117","118"]
	dataset["OneThird"] = ["120","122","124","126","128","130","131","133","134","135","137","139"]
	dataset["OneQuarter"] = ["141","143","144","145","146","147","148","149","150","151","152"]
	dataset["OneEighth"] = ["154","155","156","157","159","160","162","163","164","165","166","168","169","170","171","172"]
	if len(os.listdir("..\\..\\Analysis\\")) > 1:
		print "Merging Sweep Folders\n"
		MergeSweeps()

	for key,values in dataset.items():
		for value in values:
			filepath = os.path.join(path,key,value)
			if not os.path.exists(filepath):
				print filepath, "does not exist!"
			else:
				print "Merging Analysis Files\n"
				Merge(filepath)

