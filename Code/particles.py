"""
Tasks related to processing an image sequence to idenfity and track particles.

:Edited: August 13, 2013 - contact(sihrc.c.lee@gmail.com)
"""
from subprocess import call
import cv, cv2, math, scaffold, utils, sys
import numpy as np
import tables as tb
import images as im
from scipy import stats
from trackpy import tracking
from matplotlib import pyplot as plt

ELLIPSE_TABLE_PATH = "ellipses"

ELLIPSE_MIN_AREA = scaffold.registerParameter("ellipseMinArea", 4.0)
"""The minimum area required to identify an ellipse."""
ELLIPSE_MAX_AREA = scaffold.registerParameter("ellipseMaxArea", 200.0)
"""The maximum area required to identify an ellipse."""
EXPECTED_ELLIPSES_PER_FRAME = scaffold.registerParameter("expectedEllipsesPerFrame", 200)
"""The mean number of ellipses we expect to find. It's used to optimize memory
allocation."""

class ParticleFinder(scaffold.Task):
    """Base class for all of the different ways to find particles."""

    def _findEllipsesViaContours(self, masks):
        """Dumps the ellipses found in ``masks`` into the ellipse table.

        ``masks`` should be an iterable of binary images.
        """
        minArea = self._param(ELLIPSE_MIN_AREA)
        maxArea = self._param(ELLIPSE_MAX_AREA)
        expectedPerFrame = self._param(EXPECTED_ELLIPSES_PER_FRAME)
        
        table = self.context.createTable("ellipses", EllipseTable,
                                         expectedrows=expectedPerFrame*len(masks))
        ellipse = table.row # shortcut

        # use OpenCV to identify contours -> ellipses
        for frameNum, mask in enumerate(masks):
            contours, _ = cv2.findContours(mask.astype(np.uint8), 
                                           cv2.RETR_LIST, 
                                           cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                # Need at least 5 points for ellipses
                #if len(contour) <= 5: continue
                if len(contour) <= 1: continue

                area = cv2.contourArea(contour)
                if area < minArea or area > maxArea: continue

                ellipse['frame'] = frameNum
                ellipse['position'] = estimatePositionFromContour(contour)
                ellipse['angle'] = estimateAngleFromContour(contour)
                ellipse['axes'] = estimateEllipseAxesFromContour(contour)
                ellipse.append()

        table.flush()

class FindParticlesViaMasks(ParticleFinder):
    """
    Identifies ellipses in a binary image and dumps them into an ellipses
    table in the HDF5 file.
    """

    name = "Find Ellipses"
    dependencies = [im.ParseConfig, im.ComputeForegroundMasks]

    def isComplete(self):
        return self.context.hasNode("ellipses")

    def run(self):
        masks = self._import(im.ComputeForegroundMasks, "masks")
        self._findEllipsesViaContours(masks)

    def export(self):
        return dict(ellipses=self.context.node(ELLIPSE_TABLE_PATH))


DILATION_RADIUS = scaffold.registerParameter("dilationRadius", 3)
"""Amount (in pixels) to dilate each image."""
MORPH_THRESHOLD = scaffold.registerParameter("morphThreshold", 0.2)
"""Threshold for pixel values (0-1) after morphological procedures."""
BLUR_SIGMA = scaffold.registerParameter("blurSigma", 1.25)
"""The std. dev. (in pixels) for the gaussian blur."""
EXP_THRESHOLD = scaffold.registerParameter("expThreshold", 0.0005)
"""Threshold for pixel values after final dilation."""

class FindParticlesViaMorph(ParticleFinder):
    """
    Identify particles using a combination of foreground masks and the 
    algorithm described at https://github.com/tacaswell/tracking
    """

    name = "Find Particles via Morphological Operations"
    dependencies = [im.LoadImages, im.ComputeForegroundMasks]

    def run(self):
        self._images = self._import(im.LoadImages, "images")
        self._masks = self._import(im.ComputeForegroundMasks, "masks")
        self._imageSize = self._images[0].shape

        self._featureRadius = self._param(im.FEATURE_RADIUS)
        self._dilationRadius = self._param(DILATION_RADIUS)
        self._morphThreshold = self._param(MORPH_THRESHOLD)
        self._blurSigma = self._param(BLUR_SIGMA)
        self._expThreshold = self._param(EXP_THRESHOLD)

        # apply the foreground masks to the original images
        #self._images = [i*m.astype(np.uint8) for i, m in zip(self._images, self._masks)]

        self._doMorph()
        self._findLocalMax()
        self._findEllipsesViaContours(self._maxed)

    def export(self):
        return dict(images=im.ImageSeq(self._maxed),
                    ellipses=self.context.node(ELLIPSE_TABLE_PATH))

    def _doMorph(self):
        """Apply a gaussian blur and then a tophat."""
        tophatKernel = im.makeCircularKernel(self._featureRadius)

        morphed = []
        for image in self._images:
            scaled = im.forceRange(image, 0.0, 1.0) # scale pixel values to 0-1
            blurred = cv2.GaussianBlur(scaled, (0, 0), self._blurSigma)
            tophat = cv2.morphologyEx(blurred, cv2.MORPH_TOPHAT, tophatKernel)
            # maximize contrast by forcing the range to be 0-1 again
            morphed.append(im.forceRange(tophat, 0.0, 1.0))

        self._morphed = morphed

    def _findLocalMax(self):
        """Find the centers of particles by thresholding and dilating."""
        dilationKernel = im.makeCircularKernel(self._dilationRadius)

        maxed = []
        for image in self._morphed:
            # set pixels below morph thresh to 0
            threshed = stats.threshold(image, self._morphThreshold, newval=0.0)
            dilated = cv2.dilate(threshed, dilationKernel)
            # expThreshold is so named because the original algorithm 
            # originally exponentiated and then thresholded, which is the same
            # as flipping the sign and exponentiating the threshold.
            binary = (dilated - threshed) >= self._expThreshold
            maxed.append(binary)
        self._maxed = maxed

# An HDF5 table for storing identified ellipses
class EllipseTable(tb.IsDescription):
    frame    = tb.UInt32Col(pos=0)
    position = tb.Float32Col(pos=1, shape=2)
    angle    = tb.Float32Col(pos=2)
    axes     = tb.Float32Col(pos=3, shape=2)

class Particle(object):

    @staticmethod
    def fromContour(contour, majorMinorAxesRatio=4.0):
        return Particle(estimatePositionFromContour(contour),
                        estimateAngleFromContour(contour),
                        estimateEllipseAxesFromContour(contour, 
                                                       majorMinorAxesRatio),
                        estimateBoundsFromContour(contour))

    def __init__(self, position, angle, axes, bounds):
        self.position = position
        self.angle = angle
        self.axes = axes
        self.area = math.pi*axes.prod()
        self.bounds = bounds

    def drawOn(self, canvas, color=(0, 0, 255), degreeDelta=20):
        points = cv2.ellipse2Poly(tuple(map(int, self.position)),
                                  tuple(map(int, self.axes)),
                                  self.angle*180/math.pi,
                                  0, 360,
                                  degreeDelta)
        cv2.fillConvexPoly(canvas, points, color, cv2.CV_AA)

PARTICLE_AXES = scaffold.registerParameter("particleAxes", [6.0, 1.5])
"""The default assumed axes for elliptical particles."""

EDGE_THRESHOLD = scaffold.registerParameter("edgeThreshold", 200)
"""The minimum pixel value for the Sobel edge computation in particle
seeding."""

FRAGMENT_ANGLE_MAX = scaffold.registerParameter("fragmentAngleMax", math.pi/6)
"""The maximum angle difference between two fragments for them to be considered
to be from the same particle."""

FRAGMENT_DISTANCE_MAX = scaffold.registerParameter("fragmentDistanceMax", 2)
"""The maximum distance between two fragments for them to be considered
to be from the same particle."""

FRAGMENT_AREA_MAX = scaffold.registerParameter("fragmentAreaMax", 0.25)
"""The maximum relative area difference between two fragments for them to be
considered to be from the same particle."""
PARTICLE_TOO_SMALL = scaffold.registerParameter("particleTooSmall", 0.5)
"""Reject the particle as probably noise if its area is below this value."""
PARTICLE_FRAGMENT = scaffold.registerParameter("particleFragment", 5)
"""Probably a fragment of a particle if the area is below this value."""
CONJOINED_PARTICLES = scaffold.registerParameter("conjoinedParticles", 25)
"""Probably conjoined particles if the area is above this value."""

class FindParticlesViaEdges(scaffold.Task):

    name = "Fit Model to Images"
    dependencies = [im.ParseConfig, im.RemoveBackground]

    def isComplete(self):
        return self.context.hasNode("ellipsesViaEdges")

    def export(self):
        return dict(ellipses=self.context.node("ellipsesViaEdges"),
                    seedImages=self.context.node("edgesSeedImages"))

    def run(self):
        images = self._import(im.RemoveBackground, "images")
        self._seedImages = [] #debug

        perFrame = self._param(EXPECTED_ELLIPSES_PER_FRAME)
        self._table = self.context.createTable("ellipsesViaEdges", EllipseTable,
                                               expectedrows=perFrame*images.nrows)
        self._seedImages = im.createImageArray(self, "edgesSeedImages",
                                               dtype=np.bool, 
                                               shape=images[0].shape,
                                               expectedrows=len(images))

        for i, image in enumerate(images):
            particles = self._seedParticles(image)
            particles = self._refineParticles(particles, image)
            self._render(i, particles)

        self._table.flush()
        self._seedImages.flush()

    def _seedParticles(self, image):
        #compute edges
        def derivativeSquared(dx, dy):
            deriv = np.empty(image.shape, dtype=np.float32)
            cv2.Sobel(image, cv2.CV_32F, dx, dy, deriv, 3)
            return deriv**2
        edges = np.sqrt(derivativeSquared(1, 0) + derivativeSquared(0, 1))
        seedImage = (edges > self._param(EDGE_THRESHOLD)).astype(np.uint8)

        #despeckle
        despeckleKernel = np.array([[1, 1, 1],
                                    [1, 0, 1],
                                    [1, 1, 1]], dtype=np.uint8)
        speckles = cv2.filter2D(seedImage, -1, despeckleKernel) == 0
        seedImage[speckles] = 0

        #debug
        self._seedImages.append([seedImage])

        contours, _ = cv2.findContours(seedImage, 
                                       cv2.RETR_LIST, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        return map(Particle.fromContour, contours)

    def _refineParticles(self, particles, image):
        tooSmall = self._param(PARTICLE_TOO_SMALL)
        probablyFragment = self._param(PARTICLE_FRAGMENT)
        probablyConjoined = self._param(CONJOINED_PARTICLES)

        # filter into categories
        refined = [] # no work necessary
        fragments = []
        conjoined = []
        for particle in particles:
            if particle.area <= tooSmall:
                pass
            elif particle.area <= probablyFragment:
                fragments.append(particle)
            elif particle.area >= probablyConjoined:
                conjoined.append(particle)
            else:
                refined.append(particle)

        refined.extend(self._mergeFragments(fragments))
        refined.extend(self._splitConjoined(conjoined))
        return refined
    
    def _mergeFragments(self, fragments):
        removed = set()
        merged = []

        # find nearby fragments using grid
        dimensions = self._import(im.ParseConfig, "info").shape
        cellSize = 2*max(self._param(PARTICLE_AXES))
        grid = utils.GridMap(dimensions, np.array([cellSize, cellSize]))
        for particle in fragments: grid.add(particle)

        angleMax = self._param(FRAGMENT_ANGLE_MAX)
        distanceMax = self._param(FRAGMENT_DISTANCE_MAX)
        areaMax = self._param(FRAGMENT_AREA_MAX)

        # go through groups to see if fragments are nearby and aligned
        for group in grid.iterateCellGroups():
            for i, p1 in enumerate(group[:-1]):
                if p1 in removed: continue

                for p2 in group[i+1:]:
                    if p2 in removed: continue

                    angleDiff = abs(p1.angle - p2.angle)
                    # adjust for angle pi -> -pi wraparounds
                    realDiff = min(2*math.pi - angleDiff, angleDiff)
                    if realDiff > angleMax: continue

                    areaDiff = abs(p1.area - p2.area)/max(p1.area, p2.area)
                    if areaDiff > areaMax: continue

                    distance = np.linalg.norm(p1.position - p2.position)
                    if distance > distanceMax: continue

                    # actually merge aligned fragments
                    major = max(p1.axes[0], p2.axes[0])
                    minor = p1.axes[1] + p2.axes[1]
                    merged.append(Particle((p1.position + p2.position)/2,
                                           p1.angle,
                                           np.array([major, minor]),
                                           p1.bounds.merge(p2.bounds)))
                    removed.add(p1)
                    removed.add(p2)

        for fragment in fragments:
            if fragment not in removed:
                merged.append(fragment)
        return merged

    def _splitConjoined(self, conjoined):
        # TODO: implement me!
        return conjoined

    def _render(self, frameNum, particles):
        ellipse = self._table.row
        for particle in particles:
            ellipse['frame'] = frameNum
            ellipse['position'] = particle.position
            ellipse['angle'] = particle.angle
            ellipse['axes'] = particle.axes
            ellipse.append()

_TO_RADIANS = math.pi/180

def groupEllipsesByFrame(ellipses):
    group = []
    current = ellipses[0]['frame']
    
    for row, frame in enumerate(ellipses.col("frame")):
        if frame != current:
            yield group
            group = []
            current = frame
        
        group.append(row)

def estimateAngleFromContour(contour):
    vx, vy, _, _ = cv2.fitLine(contour, cv.CV_DIST_L2, 0, 0.01, 0.01)
    # don't use atan2 since we don't actually know signs anyways
    return math.atan(vy/vx)

def estimatePositionFromContour(contour):
    try:
        moments = cv2.moments(contour)
        x = moments['m10']/moments['m00']
        y = moments['m01']/moments['m00']
    except:
        bounds = cv2.boundingRect(contour)
        x = bounds[0] + bounds[2]/2
        y = bounds[1] + bounds[3]/2
    return np.array([x, y])

def estimateEllipseAxesFromContour(contour, majorMinorAxesRatio=4.0):
    area = cv2.contourArea(contour)
    major = math.sqrt(area/math.pi*majorMinorAxesRatio)
    minor = major/majorMinorAxesRatio
    return np.array([major, minor])

def estimateBoundsFromContour(contour):
    points = cv2.boundingRect(contour)
    return utils.Rectangle(np.array(points[0:2]), np.array(points[2:4]))

# An HDF5 table for storing tracks
class TracksTable(tb.IsDescription):
    time     = tb.Float32Col(pos=0)
    position = tb.Float32Col(pos=1, shape=2)
    velocity = tb.Float32Col(pos=2, shape=2)
    angle    = tb.Float32Col(pos=3)
    axes     = tb.Float32Col(pos=4, shape=2)

# An HDF5 table for storing tracks
class RenderTable(tb.IsDescription):
    frame    = tb.Float32Col(pos=0)
    position = tb.Float32Col(pos=1, shape=2)
    velocity = tb.Float32Col(pos=2, shape=2)
    angle    = tb.Float32Col(pos=3)
    axes     = tb.Float32Col(pos=4, shape=2)
    time     = tb.Float32Col(pos=5)
    trackID  = tb.Float32Col(pos=6)
    

SIG2NOISE_METHOD = scaffold.registerParameter("sig2noise_method",'peak2peak')
"""WiDIM Parameter for sig2noise_method"""
SUBPIXEL_METHOD = scaffold.registerParameter("subpixel_method",'gaussian')
"""WiDIM Parameter for subpixel_method"""
TOLERANCE = scaffold.registerParameter("tolerance",0.0)
"""WiDIM Parameter for tolerance"""
VALIDATION_ITER = scaffold.registerParameter("validation_iter",1)
"""WiDIM Parameter for validation_iter"""
OVERLAP_RATIO = scaffold.registerParameter("overlap_ratio",0.5)
"""WiDIM Parameter for overlap_ratio"""
COARSE_FACTOR = scaffold.registerParameter("coarse_factor",2)
"""WiDIM Parameter for coarse_factor"""

class PIVTracking(scaffold.Task):
    """ 
    Tracks particles uses the OpenPIV Python module 
    Saves velocity field data in a table similar to a
    tracks table.
    """
    name = "Run PIV"
    dependencies = [im.LoadImages]

    def export(self):
        return dict(pivtable=self.context.node("pivtable"),lenstr = self.lenstr)

    def run(self):
        self.frames = self._import(im.LoadImages, "images")
        self.dt = self.context.attrs.dt
        self._buildTable()
  

    def _buildTable(self):
        table = self.context.createTable("pivdata", TracksTable, 
                                         expectedrows=self.frames.nrows) # max
        table.cols.time.createCSIndex()
        track = table.row # shortcut

        #self.iters = len(self.frames)
        self.iters = self.context.attrs.iters  #Quick Debugging purposes

        self.lenstr = str(len(str(self.iters-1)))
        for i in range(self.iters - 1):
            self.shutup()
            data = self.runPIV(i)
            self.talk()
            for ellipse in data:
                track['time']     = i*self.dt
                track['position'] = ellipse[0:2]
                try:
                    track['angle'] = math.atan(ellipse[3]/ellipse[2])
                except:
                    track['angle'] = math.pi/2
                track['axes']     = np.array([1,1])
                track['velocity'] = ellipse[2:4]
                track.append()
            print "\nProgress:",(i+1)/float(self.iters-1)*100,"%\n"
        # TODO: include more points in velocity
        table.flush()
        newTable = table.copy(newname="pivtable", sortby="time")
        newTable.flush()  

    class NullDevice():
        """ Captures STDOUT and passes it nothing """
        def write(self, s):
            pass
    def shutup(self):
        """ Shuts the standard output """
        self.orig = sys.stdout
        sys.stdout = self.NullDevice()
    def talk(self):
        """ Releases the standard output """
        sys.stdout = self.orig

    def runPIV(self,i):
        """
        Running the actual PIV. Imports necessary modules
        """
        from pivtools import quivertools
        import openpiv.process
        import openpiv.scaling
        from time import time
        import warnings, os

        scaling_factor = 50 #Unit conversion from pixels to desired unit.
        frame_a = self.frames[i].astype(np.int32) #Image 1 of 2
        frame_b = self.frames[i+1].astype(np.int32) #Image 2 of 2

        density = self.context.attrs.folder #File Naming purposes
        velocity = self.context.attrs.name[-3:] #File Naming purposes
        density = density[density.rfind('\\'):] 
        currParams = scaffold._registeredParams["valueChange"].defaultValue

        path = "..\\..\\PIVData\\" +density + "\\" + velocity + "\\" + "_".join(currParams).replace(".","") + "\\"
        print "Writing Data Files to",path
        

        if not os.path.exists(path):
            os.makedirs(path)

        #main algorithm
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            x,y,u,v, mask=openpiv.process.WiDIM( frame_a, frame_b, np.ones(frame_a.shape, dtype=np.int32),subpixel_method = self._param(SUBPIXEL_METHOD), min_window_size=20, overlap_ratio=float(self._param(OVERLAP_RATIO)), coarse_factor = int(self._param(COARSE_FACTOR)), dt= self.dt, validation_method='mean_velocity', trust_1st_iter=0, validation_iter=int(self._param(VALIDATION_ITER)), tolerance=float(self._param(TOLERANCE)), nb_iter_max=3, sig2noise_method=self._param(SIG2NOISE_METHOD))
            quivertools.save(x, y, u, v, mask, path + '\\PIVpreprocess' + str(i) +'.txt')

        #display results
        x, y, u, v = openpiv.scaling.uniform(x, y, u, v, scaling_factor = scaling_factor )
        out = quivertools.save(x, y, u, v, mask,path + '\\PIVdata' + str(i) + '.txt')
        fig = quivertools.display_vector_field(path + '\\PIVdata'+str(i) + '.txt',title = 't='+str((i+1)*self.dt),scale=scaling_factor, width=0.001)

        fig.savefig('images\\' + 'image'+ ('{0:0'+str(len(str(self.iters)))+'}').format(i)+'.png')
        #fig.savefig('images\\' + "_".join(currParams).replace(".","")+".png")
        
        return out

TRACK_SEARCH_RADIUS = scaffold.registerParameter("trackSearchRadius", 0.75)
"""The maximum distance to look for the next particle in a track."""
TRACK_MEMORY = scaffold.registerParameter("trackMemory", 0)
"""The maximum number of frame to 'remember' a particle for tracking."""
TRACK_CUTOFF = scaffold.registerParameter("trackcutoff", 2)
"""Cut off for track length"""
class TrackParticles(scaffold.Task):
    """
    Track the identified ellipses across frames, generating a table of 
    velocities.
    """
    
    class Point(tracking.PointND):
        """
        Custom point subclass so that we can store the ellipse row 
        information with it.
        """
        
        def __init__(self, frame, position, row):
            tracking.PointND.__init__(self, frame, position)
            self.row = row

    name = "Track Ellipses"
    dependencies = [im.ParseConfig, FindParticlesViaMorph]

    def isComplete(self):
        return self.context.hasNode("tracks")

    def export(self):
        return dict(tracks=self.context.node("tracks"),trackLength = self.trackLength, tracksrender = self.context.node('tracksrender'))

    def run(self):
        self._ellipses = self._import(FindParticlesViaMorph, "ellipses")

        info = self._import(im.ParseConfig, "info")
        self._frameDimensions = info.imageSize
        self._dt = info.dt
        self._pixel = info.pixel
        self._searchRadius = self._param(TRACK_SEARCH_RADIUS)
        self._memory = self._param(TRACK_MEMORY)
        
        self._buildLevels()
        self._track()
        self._buildTable()
        self._renderTable()

        
    def _buildLevels(self):
        # Each 'level' consists of a list of all of the points in a single image
        # frame
        levels = []
        counter = 0

        ellipses = self._ellipses # shortcut
        for rows in groupEllipsesByFrame(ellipses):
            currentLevel = []
            for row in rows:
                position = self._pixel*ellipses[row]["position"]##############
                point = TrackParticles.Point(ellipses[row]['frame'], position, counter)
                currentLevel.append(point)
                counter += 1
            levels.append(currentLevel)
        
        self._levels = levels
        
    def _track(self):
        self._links = tracking.link_full(self._levels, 
                                         self._frameDimensions, 
                                         self._searchRadius, 
                                         tracking.Hash_table, 
                                         self._memory)
    def _buildTable(self):
        table = self.context.createTable("tracks_unsorted", TracksTable, 
                                         expectedrows=self._ellipses.nrows) # max
        table.cols.time.createCSIndex()
        track = table.row # shortcut
        
        for link in self._links:
            ellipses = [self._ellipses[p.row] for p in link.points]
            for ellipse, nextEllipse in zip(ellipses, ellipses[1:]):
                track['time']     = ellipse['frame']*self._dt
                track['position'] = ellipse['position']*self._pixel
                track['angle']    = ellipse['angle']
                track['axes']     = ellipse['axes']
                
                dt = (nextEllipse['frame'] - ellipse['frame'])*self._dt
                dx = nextEllipse['position'] - ellipse['position']
                track['velocity'] = dx/dt
                track.append()
        # TODO: include more points in velocity
        table.flush()
        newTable = table.copy(newname="tracks", sortby="time")
        newTable.flush()

    def _renderTable(self):
        table = self.context.createTable("render_unsorted", RenderTable, 
                                         expectedrows=self._ellipses.nrows) # max
        table.cols.frame.createCSIndex()
        track = table.row 
        trackID = 0
        flag = False
        for link in self._links:
            ellipses = [self._ellipses[p.row] for p in link.points]
            trackID += 1
            if len(ellipses) > self._param(TRACK_CUTOFF):
                print "Recording Track of Length:", len(ellipses)
                for ellipse, nextEllipse in zip(ellipses, ellipses[1:]):
                    track['frame']    = ellipse['frame']
                    track['time']     = ellipse['frame']*self._dt
                    track['position'] = ellipse['position']#*self._pixel
                    track['angle']    = ellipse['angle']
                    track['axes']     = ellipse['axes']
                    dt = (nextEllipse['frame'] - ellipse['frame'])*self._dt
                    dx = nextEllipse['position'] - ellipse['position']
                    track['velocity'] = dx/dt
                    track['trackID'] = trackID
                    track.append()
        # TODO: include more points in velocity
        table.flush()
        newTable = table.copy(newname="tracksrender", sortby="frame")
        newTable.flush()