--------
README
--------
Last Updated: 8/13/2013

--------
Summary
--------
This package performs particle detection and tracking on provided images from
the confocal. It also contains some analysis code to interpret results.
Contained in this package is a set of python script files that contain the
actual algorithms and a set of script files that run these algorithms. This
structure is listed under "Contents" of this document.

Getting started -
    The first step of using this package is to fully understand the structure
    of the code. There are several classes implemented in this package. There
    are "scaffolding" classes inside scaffold.py that hold the general structure
    for all the "tasks" (image proc- essing/detection/tracking/analysis/etc) and
    how each of them run/depend on one another. These are like the templates for
    any new classes in the future. Knowing this, there shouldn't be much to edit
    under scaffold.py itself; it would be best to just leave this file alone.

    The actual algorithms are held in particles.py with particle detection
    followed by particle tracking. Notice now that base "tasks" inherit
    scaffold.task ( which is the structure for tasks that the scaffold will
    recognize and run. To create a new task, it is best to follow the guidelines
    for scaffold.task - include dependencies = [], run(), export(),
    isComplete()). Notice that classes also inherit each other, not just
    scaffold.Task. Generally, if a class inherits another class, running those
    classes will automatically run the classes that are inherited/included in
    dependencies (defined with each task). As a result, there are several "final
    result" tasks that are listed in singleRun.py. These tasks are the ones that
    are explicitly run; the scaffold will take care of running any dependent
    tasks they require.

    With general knowledge of python classes, it shouldn't be too hard to
    add/modify the existing code. There are methods of saving variables
    globally, accessing functions globally, and sharing results globally. These
    are all detailed and blueprinted under scaffold.py.

Quick RoadMap -
    Here's a quick roadmap to running the package once:
        I. python runSweep.py [density-data-folder-name][destination-sweep-
        folder-name]
            Here you can determine what you want to run.
            Set parameters you want to run under setParams()
            Only need run runSweep.py to call everything else.

        II. singleRun.py
            Here is where you decide what tasks you want run. Under runSeq()

        III. Tasks
            From here on, the scaffold context scheduler looks at what you set
            under runSeq() and looks for those tasks in the respective scripts.
            [particles.py, analysis.py, density_analysis.py, visual.py,
            images.py]

        IV.  Subsequent Tasks
            The scaffold context scheduler looks at the dependencies of these
            tasks - which are more tasks and runs those as well. For tasks that
            inherit other tasks, the greatest parent class that inherits
            scaffold.Task is whats run.

            After everything is done running,the program exits. You might have
            some results depending on what tasks you ran (normally under
            analysis.py/density_analysis.py or viewData in SingleRun.py).
----------
CONTENTS
----------
    > ./Dependencies
        Contains all the dependencies needed to run these scripts as windows
        binaries.(easy to install)
    > ./Data
        Contains data with structure ./Data/Density/Series###_##_##.xml with
        .tifs
    > ./Code
	>./Code/Run
            >analyzeSweep.py
                Run to access data results. Compiles all analysis.csv files into
                sweepresults.csv. From sweepresults.csv, specific sweep results
                can be accessed by inputting line number of their locations in
                sweepresults.csv
            >automatedRun.py
               	Called by remoteCommand.py. Calls notification.py,
               	synchronize.py, and runSweep.py
            >notification.py
               	Send email notifications to specified email address. Email
               	account must allow SMTP (Gmail).Messages can be added/modified
               	based on single message list within the script.
	    >remoteCommand.py
               	Run by remote computers. Waits and listens for specific command
               	before launching automatedRun.py
            >runSweep.py
               	Runs singleRun.py. Run by onsite computer. Controls sweep
               	configurations. i.e. what values/what parameters/what data
            >sendCommands.py
               	Sends messages in parsable syntax accepted by remoteCommand.py
            >singleRun.py
               	Contains the context/scheduler of the entire package. Controls
               	what scaffold.Tasks are run. Talks to runSweep.py for parameter
               	changes. List of tasks available - uncomment to include in
               	scheduler.
            >synchronize.py
               	Synchronizes parent directory of Code (./Code) to another
               	directory, making an exact copy. Capable of overwritting or
               	choosing not to copy based on arguments and use of methods
               	(filecmp,cmphashes)
        >./Code/Run/Misc
            >dispConfigs.py
            	Displays the configurations set by config file (.xml) of the
               	 data.
            >mergeCSV.py
            	Merges sweep results across several sweep folders into a sweep
              	folder with all the analysis.csv and .avi files. Prepares for
               	analyzeSweep.py in the event of several sweep folders
            >synchroVideos.py
               	Saves all videos and names them after density and velocity of
               	the data in specified directory. (Does not render them).
        >./Code/Run/trackpy
            	Contains tracking algorithm currently implemented. This is currently
            	not working optimally. The alternative, OpenPIV, is used.
	>./Code/Run/TIF_stack_reading
		>tifffile.py
			TIF File reader by Christopher Gohlke. Used in TIFStackReader.py
		>TIFStackReader.py
			Reads specified image stack by pages. Cannot load all at once
			due to memory error.
        >./Code/pivtools
            	Contains the OpenPIV implementation. The open-piv package must be
            	installed. These are only the files that were edited from the
            	original to work with our code.
        >analysis.py
            	Contains the analysis tasks to be run in the context.
            	Provides most of the results. New tasks can be implemented,
            	following similar structure under class scaffold.Task
        >images.py
            	Contains all scaffold.Tasks that deal with the data images.
        >particles.py
            	Contains all detection and tracking scaffold.Tasks (core package)
        >scaffold.py
            	Contains the scaffold class. Handles the running of all the
            	scaffold.Tasks
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
        maskLowThresh    -10
        maskHighThresh    3
        dilationRadius    3.0
        morphThreshold    .2
        blurSigma         1.25
        expThreshold      .0005
        featureRadius    Not Swept - If detection needs to be improved,
        featureRadius may need to be swept.

    - TRACKING:
        via trackpy :: INCOMPLETE
            trackMemory
                Determines how long a track is remembered (in frames) once it
                disappears from frame (it can come back later).If obvious tracks
                are interrupted due to dropping out of the frame, increase this
                parameter.
            trackSearchRadius
                Determines how far a particle can go to be included in the same
                track. Basically, this controls how fast the particles are
                allowed to travel.

        -CURRENT PROBLEMS-
            For higher densities and higher velocities, trackSearchRadius
            must increase in value in order to obtain meaningful tracks, but
            this requires a high amount of computation time and power.
            Currently, another method OpenPIV (Python Particle Image
            Velocimetry) module is being restored for use in this project
            (located on GitHub under user:sihrc)

        via PIV Tracking :: COMPLETE
            sig2noise_method        'peak2peak'
            subpixel_method         'gaussian'
            tolerance               0.0
            validation_iter         1
            overlap_ratio           0.5
            coarse_factor           2

ANALYSIS:
    - VELOCITY CORRELATION
        The velocity correlation algorithm is working and can be accessed in
        singleRun.py. To scale results, change the RADII parameter set in
        analysis.py. These must be scaled accordingly with the scaling_factor
        for PIV. Some issues that this will solve are sudden drops in
        correlation due to bad resolution of PIV.
    - DENSITY FIELD
        This now works without using PIV. This is located under
        density_analysis. The problem with this before was that it was included
        under GriddedField which depends on PIVTracking, but PIV does not do
        particle detection; therefore, particle density is unknown. Density
        field is now routed through density_analysis.py which uses
        FindParticlesViaMorph (the original particel detection algorithm). This
        code works.



------------
 HOW TO USE
------------

SUMMARY:
    Everything works thus far. Some may be dependent on how its working/parent
    directory are structured, but other than manually locating the data and
    editing the path, the rest of the directories should be automatically
    created.

    Some common issues are located in "COMMON ISSUES" section.

BASIC USE:
    To add or remove tasks, simply find the list of tasks that are mostly
    commented out under singleRun.py and add/remove via commenting.
    In runSweep.py there are a list of parameters and corresponding values.
    Add/remove parameters and values there. The last 3 parameters added should
    be the changing values. The program names results based on the last 3
    parameters. (the number of parameters can be changed by locating within
    singleRun.py valueChange[-3:] and changing it to valueChange[-n:]).
    runSweep.py also controls which velocities are swept and which densities are
    swept. When on your own computer (not remote distributive computer), simply
    run runSweep.py. Upon completion, run analyzeSweep.py to collect results.

DISTRIBUTIVE COMPUTING:
    To use several computers at once, make sure to install all dependencies, add
    Python27 to path, and copy all data onto local drive in similar structure as
    this.

    Run remoteCommand.py and it will wait for a command. Edit account info
    within sendCommands.py and remoteCommand.py and notification.py to use an
    accessible email account. (Gmail preferred).

    By simply editing singleRun and runSweep on shared directory (where
    synchronize.py push and pulls , can be the olin student drive, dropbox, or
    any other type of filesharing system), the remote computers will
    synchronizing python files with the shared directory and push results to the
    shared directory upon completion.

COMMON ISSUES:
    Video Rendering
        If there is an issue with video rendering where the code outputs a
        MemoryError, either the output filename for the video is invalid, or the
        codec specified for openCV's movie writer is missing/wrong. A quick
        online search for a codec parameter that is compatible with your system
        will resolve that issue. (Switching back and forth sometimes solves the
        issue.)
    Using GriddedFields
        When trying to use GriddedFields, a common issue is an index error in
        cellMap. This happens because the units of the table that is imported is
        not in microns. To fix this, multiply data in pixels by
        self.context.attrs.pixel (the conversion factor between pixels and
        microns as set by the config file provided by the raw images - .xml
        file).
    Installing Dependencies
        A common issue with running the code for the first time is incorrectly
        installed dependencies. There is a README within the dependencies folder
        that detail the steps that should be taken. Because of "out-of-date"
        configuration settings of OpenPIV, it is recommended to setup OpenPIV
        first, install PythonXY to appease OpenPIV, and then reinstall any other
        dependencies in the folder as the program errors call for them.

If there are issues not mentioned here, contact:
[1]christopher.lee@students.olin.edu/sihrc.c.lee@gmail.com
[2]chase.kernan@gmail.com


External Tracking Modules - provided Documentation:
--------------
ABOUT OpenPIV
--------------
The main algorithm this code uses is openpiv.process.WiDIM: WiDIM

    Implementation of the WiDIM algorithm (Window Displacement Iterative
    Method). This is an iterative  method to cope with  the lost of pairs due to
    particles motion and get rid of the limitation in velocity range due to the
    window size. The possibility of window size coarsening is implemented.
    Example : minimum window size of 16*16 pixels and coarse_level of 2 gives a
    1st iteration with a window size of 64*64 pixels, then 32*32 then 16*16.
        ----Algorithm : At each step, a predictor of the displacement (dp) is
        applied based on the results of the previous iteration.
            Each window is correlated with a shifted window.
            The displacement obtained from this correlation is the residual
            displacement (dc) The new displacement (d) is obtained with dx = dpx
            + dcx and dy = dpy + dcy The velocity field is validated and wrong
            vectors are replaced by mean value of surrounding vectors from the
            previous iteration (or by bilinear interpolation if the window size
            of previous iteration was different) The new predictor is obtained
            by bilinear interpolation of the displacements of the previous
            iteration:
                dpx_k+1 = dx_k

    Reference:
        F. Scarano & M. L. Riethmuller, Iterative multigrid approach in PIV
        image processing with discrete window offset, Experiments in Fluids 26
        (1999) 513-523

    Parameters
    ----------
    frame_a : 2d np.ndarray, dtype=np.int32
        an two dimensions array of integers containing grey levels of
        the first frame.

    frame_b : 2d np.ndarray, dtype=np.int32
        an two dimensions array of integers containing grey levels of
        the second frame.

    mark : 2d np.ndarray, dtype=np.int32
        an two dimensions array of integers with values 0 for the background, 1
        for the flow-field. If the center of a window is on a 0 value the
        velocity is set to 0.

    min_window_size : int
        the size of the minimum (final) (square) interrogation window.

    overlap_ratio : float
        the ratio of overlap between two windows (between 0 and 1).

    dt : float
        the time delay separating the two frames.

    validation_method : string
        the method used for validation (in addition to the sig2noise method).
        Only the mean velocity method is implemented now

    trust_1st_iter : int = 0 or 1
        0 if the first iteration need to be validated. With a first window size
        following the 1/4 rule, the 1st iteration can be trusted and the value
        should be 1 (Default value)

    validation_iter : int
        number of iterations per validation cycle.

    tolerance : float
        the threshold for the validation method chosen. This does not concern
        the sig2noise for which the threshold is 1.5; [nb: this could change in
        the future]

    nb_iter_max : int
        global number of iterations.

    subpixel_method : string
        one of the following methods to estimate subpixel location of the peak:
        'centroid' [replaces default if correlation map is negative],
        'gaussian' [default if correlation map is positive],
        'parabolic'.

    sig2noise_method : string
        defines the method of signal-to-noise-ratio measure,
        ('peak2peak' or 'peak2mean'. If None, no measure is performed.)

    width : int
        the half size of the region around the first
        correlation peak to ignore for finding the second
        peak. [default: 2]. Only used if ``sig2noise_method==peak2peak``.

    nfftx   : int
        the size of the 2D FFT in x-direction,
        [default: 2 x windows_a.shape[0] is recommended]

    nffty   : int
        the size of the 2D FFT in y-direction,
        [default: 2 x windows_a.shape[1] is recommended]


    Returns
    -------

    x : 2d np.ndarray
        a two dimensional array containing the x-axis component of the
        interpolations locations.

    y : 2d np.ndarray
        a two dimensional array containing the y-axis component of the
        interpolations locations.

    u : 2d np.ndarray
        a two dimensional array containing the u velocity component,
        in pixels/seconds.

    v : 2d np.ndarray
        a two dimensional array containing the v velocity component,
        in pixels/seconds.

    mask : 2d np.ndarray
        a two dimensional array containing the boolean values (True for vectors
        interpolated from previous iteration)

    Example
    --------

    >>> x,y,u,v, mask = openpiv.process.WiDIM( frame_a, frame_b, mark,
    min_window_size=16, overlap_ratio=0.25, coarse_factor=2, dt=0.02,
    validation_method='mean_velocity', trust_1st_iter=1, validation_iter=2,
    tolerance=0.7, nb_iter_max=4, sig2noise_method='peak2peak')

    --------------------------------------
    Method of implementation : to improve the speed of the programm,
    all data have been placed in the same huge 4-dimensions 'F' array.
    (this prevent the definition of a new array for each iteration)
    However, during the coarsening process a large part of the array is not
    used. Structure of array F:
    --The 1st index is the main iteration (K)   --> length is nb_iter_max
        -- 2nd index (I) is row (of the map of the interpolations locations of
        iteration K) --> length (effectively used) is Nrow[K]
            --3rd index (J) is column  --> length (effectively used) is Ncol[K]
                --4th index represent the type of data stored at this point:
                    | 0 --> x         |
                    | 1 --> y         |
                    | 2 --> xb        |
                    | 3 --> yb        |
                    | 4 --> dx        |
                    | 5 --> dy        |
                    | 6 --> dpx       |
                    | 7 --> dpy       |
                    | 8 --> dcx       |
                    | 9 --> dcy       |
                    | 10 --> u        |
                    | 11 --> v        |
                    | 12 --> si2noise |
    Storage of data with indices is not good for comprehension so its very
    important to comment on each single operation. A python dictionary type
    could have been used (and would be much more intuitive) but its equivalent
    in c language (type map) is very slow compared to a numpy ndarray.
