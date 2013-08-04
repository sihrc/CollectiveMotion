import csv, os, sys, shutil, time
import numpy as np

def MergeSweeps():
	path = "..\\..\\Analysis\\"
	destfolder = 'Sweep ' + sys.argv[1]
	for folder in os.listdir(path):
		folderpath = os.path.join(path,folder)
		if 'Sweep' in folder and folder!=destfolder:
			for dirs, subdirs, files in os.walk(folderpath):
				for filename in files:
					src_file = os.path.join(dirs,folderpath)
					dst_dirs = dirs.replace(folder,destfolder)
					dst_file = os.path.join(dst_dirs, filename)
					if os.path.exists(dst_file):
						if "Analysis" in filename:
							i = 1
							while os.path.exists(dst_file):
								filename = "Analysis" + str(i) + '.avi'
								dst_file = os.path.join(dst_dirs,filename)
								i += 1
							print "Creating Analysis File:", dst_file
							shutil.copy(src_file, dst_file)
					else:
						if not os.path.exists(dst_dirs):
							os.makedirs(dst_dirs)
						print "Creating file:", dst_file
						shutil.copy(src_file,dst_file)
	print 'Done Merging Folders\n Commencing CSV Merge'
	time.sleep(5)			

def Merge(path):
	for csvFile in os.listdir(path):
		if "Analysis" in csvFile:
			currFile = os.path.join(path,csvfile)
			print "Found Analysis File:",currFile
			if os.stat(currFile).st_size == 0:
				print "File is empty!"
				os.remove(currFile)
				continue
			with open(currFile,'rb') as f:
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
	print "Done compiling NumPy Array.\n Sorting and Writing..."
	if 'final' in locals():
		final = final[np.lexsort((final[:,7],final[:,6]))]
		writer = csv.writer(open(os.path.join(path,"Analysis.csv"),'wb'))
		writer.writerows(final)

		for files in os.listdir(path):
			if "Analysis" in files and files != "Analysis.csv":
				print "Removed:", files
				os.remove(os.path.join(path,files))
	else:
		print "No Data Found!"


if __name__ == "__main__":
	path = "..\\..\\Code\\Analysis\\Sweep " + sys.argv[1]

	dataset = dict()
	dataset["High"] = ["080","082","084","086","088","090","092","094","096"]
	dataset["TwoThirds"] = ["100","102","104","106","108","110","112","114","115","117","118"]
	dataset["OneThird"] = ["120","122","124","126","128","130","131","133","134","135","137","139"]
	dataset["OneQuarter"] = ["141","143","144","145","146","147","148","149","150","151","152"]
	dataset["OneEighth"] = ["154","155","156","157","159","160","162","163","164","165","166","168","169","170","171","172"]

	print "Merging Sweep Folders\n"
	MergeSweeps()
	sys.exit()

	for key,values in dataset.items():
		for value in values:
			filepath = os.path.join(path,key,value)
			if not os.path.exists(filepath):
				continue
			else:
				print "Merging Analysis Files in %s,%s\n"%(key,value)
				Merge(filepath)

