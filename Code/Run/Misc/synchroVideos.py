""" 
This script grabs video files from a parent directory and copies 
them all into a single directory that has all the videos by density 
and velocity

:Edited: August 13, 2013 - contact(sihrc.c.lee@gmail.com)

"""
import sys,os,shutil

source = "..\\2013 Summer\\Code\\Analysis\\Sweep " +sys.argv[1]
dest = "Z:\\2013 Summer\\OriginalVideos\\"

paths = dict()
density = os.listdir(source)
for folder in density:
	paths[folder] = os.listdir(os.path.join(source,folder))

for density,velocity in paths.items():
	for folder in velocity:
		srcpath = os.path.join(source,density,folder,"renderSeedImagesOutput")
		if len(os.listdir(srcpath)) > 0:
			video = os.path.join(srcpath,os.listdir(srcpath)[0])
			dstpath = os.path.join(dest,density,folder)
			name = density+folder+".avi"
			if not os.path.exists(dstpath):
				os.makedirs(dstpath)
			shutil.copy(video,os.path.join(dstpath,name))
			print 'Copied:' + video,"as",name
		else:
			print 'Nothing located in:',srcpath

