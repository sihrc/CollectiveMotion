"""
Synchronization: Synchronizes files between a two directories. In this application,
it is syncing files between a network drive (student drive) and the local drive. This 
script is capable of handling "push" and "pull" with option [1,2] for with replacment 
or without replacement.

:Edited: August 13, 2013 - contact(sihrc.c.lee@gmail.com)
"""

import os, win32api, sys, shutil, filecmp, time, hashlib

def synchro(root_src_dir,root_dst_dir):
	"""
	Performs the actual Synchronization by sweeping the source and destination,
	checking for duplicates and differences.

	Mode 1 - grab the python files only
	Mode 2 - grab all missing files including pictures and videos
	"""
	#Check if source and destinations exist
	if not os.path.exists(root_src_dir):
		print "Source does not exist"
	if not os.path.exists(root_dst_dir):
		print "Destination does not exist"

	#Walking through the directory
	for src_dir, dirs, files in os.walk(root_src_dir):
		dst_dir = src_dir.replace(root_src_dir, root_dst_dir)
		for file_ in files:
			src_file = os.path.join(src_dir, file_)
			dst_file = os.path.join(dst_dir, file_)
			#Decides whether or not to replace files in the destination
			ext = "." + file_[-file_[::-1].find("."):]
			if  ext in arglist:
				if ext == '.avi' and os.path.exists(dst_file):
					continue
				if not os.path.exists(dst_dir):
					os.makedirs(dst_dir)
				print "Replacing", dst_file
				shutil.copy(src_file,dst_file)


def cmpHash(file1,file2):
	"""	Compares two files' hashes to determine duplicates. This doesn't work out so well, possibly due to different metadata"""
	hash1 = open(file1,'r').read()
	hash2 = open(file2,'r').read()
   	return  hashlib.sha512(file1).hexdigest() == hashlib.sha512(file2).hexdigest()

def getDrive():
	""" Finds and selects the network drive """
	drives = win32api.GetLogicalDriveStrings()
	drives = drives.split('\000')[:-1]

	for drive in drives:
		if "Z" in drive:
			network = drive

	netfilepath = network + "2013 Summer\\Code\\"
	localfilepath = "..\\"

	return netfilepath, localfilepath


if __name__ == "__main__":
	args = sys.argv[2]
	network, local = getDrive()
	print "Synchronization with replacing: Confirmed"
	global arglist
	arglist = args[1:-1].split(",")
	if ".py" in arglist:
		arglist.append('.pyc')
		arglist.append('.pyd')
		arglist.append('.pyx')
	print "Synchronizing Exts.:", arglist
	if sys.argv[1] == "push":
		synchro(local,network)
                
	if sys.argv[1] == "pull":
		synchro(network, local)
        
	
