--------
 README
--------
Last Updated: 8/16/2013

----------
 CONTENTS
----------
	> ./Dependencies
		Contains all the dependencies needed to run these scripts as windows binaries.(easy to install)
	> ./Data
		Contains data with structure ./Data/Density/Series###_##_##.xml with .tifs
        > ./Code
		>./Code/Run
			>analysis.py
				Contains the analysis tasks to be run in the context.
				Provides most of the results. New tasks can be implemented, 
				following similar structure under class scaffold.Task
			>analyzeSweep.py
				Run to access data. Compiles all analysis.csv files into sweepresults.csv. 
				From sweepresults.csv, specific sweep results can be accessed by inputting 
				line number of their locations in sweepresults.csv
			>automatedRun.py
				Called by remoteCommand.py. Calls notification.py, synchronize.py, 
				and runSweep.py
			>notification.py
				Send email notifications to specified email address. Email account must 
				allow SMTP (Gmail).Messages can be added/modified based on single message 
				list within the script.
			>remoteCommand.py
				Run by remote computers. Waits and listens for specific command before 
				launching automatedRun.py
			>runSweep.py
				Runs singleRun.py. Run by onsite computer. Controls sweep configurations.
				i.e. what values/what parameters/what data
			>sendCommands.py
				Sends messages in parsable syntax accepted by remoteCommand.py
			>singleRun.py
				Contains the context/scheduler of the entire package. Controls what 
				scaffold.Tasks are run. Talks to runSweep.py for parameter changes. List
				of tasks available - uncomment to include in scheduler.
			>synchronize.py
				Synchronizes parent directory of Code (./Code) to another directory,
				making an exact copy. Capable of overwritting or choosing not to copy
				based on arguments and use of methods (filecmp,cmphashes)
		>./Code/Run/Misc
			>dispConfigs.py
				Displays the configurations set by config file (.xml) of the data. 
			>mergeCSV.py
				Merges sweep results across several sweep folders into a sweep folder
				with all the analysis.csv and .avi files. Prepares for analyzeSweep.py
				in the event of several sweep folders
			>synchroVideos.py
				Saves all videos and names them after density and velocity of the data
				in specified directory. (Does not render them).
		>./Code/Run/trackpy
			Contains tracking algorithm currently implemented.
		>images.py
			Contains all scaffold.Tasks that deal with the data images.
		>particles.py
			Contains all detection and tracking scaffold.Tasks (core package)
		>scaffold.py
			Contains the scaffold class. Handles the running of all the scaffold.Tasks
		>storage.py
			Contains methods for hashTable storage.
		>utils.py
			Contains utility methods
		>visual.py
			Contains all scaffold.Tasks that deal renders (videos/plots)
----------------
 PROJECT STATUS
----------------

PARAMETER SWEEPING:
 - DETECTION: COMPLETE
	maskLowThresh 	-10.0
	maskHighThresh 	  3.0
	dilationRadius 	  3.0
	morphThreshold 	   .2
	blurSigma 	  1.25
	expThreshold 	   .0005	
	featureRadius	 Not Swept - If detection needs to be improved, featureRadius may need to be swept.

 - TRACKING: INCOMPLETE
	trackMemory		
		Determines how long a track is remembered (in frames) once it disappears 
		from frame (it can come back later).If obvious tracks are interrupted due to 
		dropping out of the frame, increase this parameter. 
	trackSearchRadius
		Determines how far a particle can go to be included in the same track. 
		Basically, this controls how fast the particles are allowed to travel.

	-CURRENT PROBLEMS-
		For higher densities and higher velocities, trackSearchRadius
		must increase in value in order to obtain meaningful tracks, but
		this requires a high amount of computation time and power. Currently,
		another method OpenPIV (Python Particle Image Velocimetry) module is 
		being restored for use in this project (located on GitHub under user:sihrc)

------------
 HOW TO USE
------------

SUMMARY:
	Everything works thus far. Some may be dependent on how its working/parent directory
	are structured, but other than manually locating the data and editing the path, the rest
	of the directories should be automatically created.

	Some common issues will be located in a later section.

BASIC USE:
	To add or remove tasks, simply find the list of tasks that are mostly commented out
	under singleRun.py and add/remove via commenting.
	In runSweep.py there are a list of parameters and corresponding values. Add/remove
	parameters and values there. The last 3 parameters added should be the changing values.
	The program names results based on the last 3 parameters. (the number of parameters can
	be changed by locating within singleRun.py valueChange[-3:] and changing it to 
	valueChange[-n:]).
	runSweep.py also controls which velocities are swept and which densities are swept.
	When on your own computer (not remote distributive computer), simply run runSweep.py.
	Upon completion, run analyzeSweep.py to collect results.

DISTRIBUTIVE COMPUTING:
	To use several computers at once, make sure to install all dependencies, add Python27 to 
	path, and copy all data onto local drive in similar structure as this.

	Run remoteCommand.py and it will wait for a command. Edit account info within sendCommands.py
	and remoteCommand.py and notification.py to use an accessible email account. (Gmail preferred).

	By simply editing singleRun and runSweep on shared directory (where synchronize.py push and pulls
	, can be the olin student drive, dropbox, or any other type of filesharing system), the remote
	computers will synchronizing python files with the shared directory and push results to the shared
	directory upon completion.

COMMON ISSUES:
	Video Rendering
		If there is an issue with video rendering where the code outputs a MemoryError, either
		the output filename for the video is invalid, or the codec specified for openCV's movie
		writer is missing/wrong. A quick online search for a codec parameter that is compatible
		with your system will resolve that issue. (Switching back and forth sometimes solves the
		issue.)

If there are issues not mentioned here, contact:
[1]christopher.lee@students.olin.edu/sihrc.c.lee@gmail.com
[2]chase.kernan@gmail.com


