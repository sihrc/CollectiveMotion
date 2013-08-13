"""
Contains tasks relating to rendering graphical visualizations of the data and results.

:Edited: August 13, 2013 - contact(sihrc.c.lee@gmail.com)
"""

from subprocess import call
import scaffold, sys
import particles as pt
import images as im
import analysis as an
import density_analysis as an_dens
import numpy as np
import gc, csv, math, cv2, os, colorsys
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.backends.backend_agg import FigureCanvasAgg

_TO_DEGREES = 180/math.pi

def _formatOutput(task, param):
    return task._param(param).format(task.context.root._v_name)

class _RenderTask(scaffold.Task):
    _outputParam = None

    def _render(self, images, mapping=lambda image: image, num = ""):
        if self._outputParam is None: raise NotImplemented
        output = _formatOutput(self, self._outputParam)
        seq = im.ImageSeq(map(mapping, images))
        path = output[:-4] + "_" + num + output[-4:]
        seq.writeMovie(path)
        self.context.log("Rendered to {0}.", path)

    def _joinParts(self,count):
        output = _formatOutput(self, self._outputParam)
        index = output.find("Sweep")
        concat = ""
        for i in range(count):
            path = output[:-4] + "_" + str(i+1) + output[-4:]
            concat += path + "|"
        if os.path.exists(output):
            os.remove(output)
        command = 'C:/ffmpeg/bin/ffmpeg.exe -i "concat:' + concat[:-1] + '" -c copy ' + "\"" + output + "\""
        os.system(command)
        for i in range(count):
            path = output[:-4] + "_" + str(i+1) + output[-4:]
            os.remove(path)
                
PLOT_PIV_FIELD_OUTPUT = scaffold.registerParameter("plotPIVFieldOutput","../plots/{0}-PIVField.avi")
"""The file path to render the toutput animation of PlotPIVField to."""

class PlotPIVField(scaffold.Task):
    name = "Plot PIV Field"
    dependencies = [pt.PIVTracking]
    _outputParam = PLOT_PIV_FIELD_OUTPUT

    def run(self):
        import shutil
        lenstr = self._import(pt.PIVTracking,"lenstr")
        output = _formatOutput(self,self._outputParam)
        cmd = "ffmpeg -f image2 -r 20 -i .\\images\\image%0" + lenstr + "d.png -c:v libx264 -r 20 .\\images\\output.mp4"
        os.system(cmd)
        shutil.copy(".\\images\\output.mp4",output)
        [os.remove(os.path.join('.\\images',filename)) for filename in os.listdir(".\\images")]


RENDER_MASKS_OUTPUT = scaffold.registerParameter("renderMasksOutput", "../videos/{0}-masks.avi")
"""The file path to render the output video of RenderForegroundMasks to."""

class RenderForegroundMasks(_RenderTask):

    name = "Render Foreground Masks"
    dependencies = [im.ComputeForegroundMasks]
    _outputParam = RENDER_MASKS_OUTPUT

    def run(self):
        images = self._import(im.ComputeForegroundMasks, "masks")
        self._render(images, im.binaryToGray)   

RENDER_DIFFS_OUTPUT = scaffold.registerParameter("renderDiffsOutput", "../videos/{0}-diffs.avi")
"""The file path to render the output video of RenderDifferences to."""

class RenderDifferences(_RenderTask):

    name = "Render Differences"
    dependencies = [im.ComputeForegroundMasks]
    _outputParam = RENDER_DIFFS_OUTPUT

    def run(self):
        diffs = self._import(im.ComputeForegroundMasks, "diffs")
        mapping = lambda image: im.forceRange(image*(image > 0), 0, 255)\
                                .astype(np.uint8)
        self._render(diffs, mapping)


RENDER_REMOVED_BACKGROUND_OUTPUT = scaffold.registerParameter("renderRemovedBackgroundOutput", "../videos/{0}-removedBackground.avi")
"""The file path to render the output video of RenderRemovedBackground to."""

class RenderRemovedBackground(_RenderTask):

    name = "Render Removed Background"
    dependencies = [im.RemoveBackground]
    _outputParam = RENDER_REMOVED_BACKGROUND_OUTPUT

    def run(self):
        images = self._import(im.RemoveBackground, "images")
        self._render(images)


RENDER_SEED_IMAGES_OUTPUT = scaffold.registerParameter("renderSeedImagesOutput", "../videos/{0}-seedImages.avi")
"""The file path to render the output video of RenderSeedImages to."""

class RenderSeedImages(_RenderTask):

    name = "Render Seed Images"
    dependencies = [pt.FindParticlesViaEdges]
    _outputParam = RENDER_SEED_IMAGES_OUTPUT

    def run(self):
        images = self._import(pt.FindParticlesViaEdges, "seedImages")
        self._render(images, im.binaryToGray)

RENDER_WATERSHED_OUTPUT = scaffold.registerParameter("renderWatershedOutput", "../videos/{0}-watershed.avi")
"""The file path to render the output video of RenderWatershed to."""

class RenderWatershed(_RenderTask):

    name = "Render Watershed"
    dependencies = [im.Watershed]
    _outputParam = RENDER_WATERSHED_OUTPUT

    def run(self):
        images = self._import(im.Watershed, "isolated")
        self._render(images)


RENDER_REGIONS_OUTPUT = scaffold.registerParameter("renderRegionsOutput", "../videos/{0}-regions.avi")
"""The file path to render the output video of RenderRegions to."""

class RenderRegions(_RenderTask):

    name = "Render Regions"
    dependencies = [im.MergeStatisticalRegions]
    _outputParam = RENDER_REGIONS_OUTPUT

    def run(self):
        images = self._import(im.MergeStatisticalRegions, "masks")
        self._render(images, im.binaryToGray)

RENDER_MORPHED_IMAGES_OUTPUT = scaffold.registerParameter("renderMorphedImagesOutput", "../videos/{0}-morphImages.avi")
"""The file path to render the output video of RenderMorphImages to."""

class RenderMorphImages(_RenderTask):

    name = "Render Morph Images"
    dependencies = [pt.FindParticlesViaMorph]
    _outputParam = RENDER_MORPHED_IMAGES_OUTPUT

    def run(self):
        images = self._import(pt.FindParticlesViaMorph, "images")
        self._render(images)

RENDER_ELLIPSES_OUTPUT = scaffold.registerParameter("renderEllipsesOutput", "../videos/{0}-ellipses.avi")
"""The file path to render the output video of RenderEllipses to."""
RENDER_ELLIPSES_COLOR = scaffold.registerParameter("renderEllipsesColor", (0, 0, 255))
"""The RGB color used to draw the ellipses."""

class RenderEllipses(_RenderTask):

    name = "Render Ellipses"
    dependencies = [pt.FindParticlesViaMorph, im.LoadImages]
    _outputParam = RENDER_ELLIPSES_OUTPUT

    def _save(self,drawn):
        path = self._param(IMAGE_PATH)
        for num in range(len(drawn)):
            cv2.imwrite(path[:-4] + "__" +str(num) + path[-4:],drawn[num])

    def run(self):
        images = self._import(im.LoadImages, "images")
        ellipses = self._import(pt.FindParticlesViaMorph, "ellipses")
        color = self._param(RENDER_ELLIPSES_COLOR)

        drawn = []
        drawn2 = []
        for image, group in zip(images, pt.groupEllipsesByFrame(ellipses)):
            self.context.debug("Group len={0}", len(group))
            canvas = cv2.imread(".\\Misc\\Base.tif")
            canvas2 = im.toColor(im.forceRange(image, 0, 255))

            for row in group:
                cv2.ellipse(canvas2, 
                            tuple(map(int, ellipses[row]["position"])),
                            tuple(map(int, ellipses[row]["axes"])),
                            ellipses[row]["angle"]*_TO_DEGREES,
                            0, 360,
                            color,
                            1,
                            cv2.CV_AA,
                            0)
                cv2.ellipse(canvas, 
                            tuple(map(int, ellipses[row]["position"])),
                            tuple(map(int, ellipses[row]["axes"])),
                            ellipses[row]["angle"]*_TO_DEGREES,
                            0, 360,
                            color,
                            1,
                            cv2.CV_AA,
                            0)
            drawn.append(canvas)
            drawn2.append(canvas2)
        self._save(drawn)
        self._render(drawn2)

RENDER_TRACKS_COLOR = scaffold.registerParameter("renderTracksColor", (0, 255, 0))
"""The RGB color used to draw the tracks."""
RENDER_ARROW_COLOR = scaffold.registerParameter("renderArrowColor", (255, 0, 0))
"""The RGB color used to draw the track arrows."""
RENDER_TRACKS_OUTPUT = scaffold.registerParameter("renderTracksOutput", "../videos/{0}-ellipses.avi")
"""The file path to render the output video of RenderTracks to."""

class RenderTracks(_RenderTask):
    name = "Render Tracks"
    dependencies = [pt.TrackParticles, im.LoadImages, pt.FindParticlesViaMorph]
    _outputParam = RENDER_TRACKS_OUTPUT

    def run(self):
        images = self._import(im.LoadImages, "images")
        ellipses = self._import(pt.FindParticlesViaMorph, "ellipses")
        tracks = self._import(pt.TrackParticles,"tracksrender")

        ellipse_color = self._param(RENDER_ELLIPSES_COLOR)
        N = 200#np.max(tracks[:]["trackID"])
        HSV_tuples = [(x*1.0/N, 0.99, 0.99) for x in range(N)]
        tracks_color = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
        #print tracks_color
        arrow_color = self._param(RENDER_TRACKS_COLOR)

        drawn = []
        for image, group_ellipse, group_tracks in zip(images, pt.groupEllipsesByFrame(ellipses),pt.groupEllipsesByFrame(tracks)):
            self.context.debug("Ellipse len={0}", len(group_ellipse))
            self.context.debug("Track len={0}", len(group_tracks))
            canvas = im.toColor(im.forceRange(image, 0, 255))

            for row in group_ellipse:
                cv2.ellipse(canvas, 
                            tuple(map(int, ellipses[row]["position"])),
                            tuple(map(int, ellipses[row]["axes"])),
                            ellipses[row]["angle"]*_TO_DEGREES,
                            0, 360,
                            ellipse_color,
                            1,
                            cv2.CV_AA,
                            0)
            for row in group_tracks:
                angle = tracks[row]["angle"]
                radius = tracks[row]["axes"][0]
                color = tracks_color[int(tracks[row]["trackID"]-1)%200]
                color = map(lambda x: 255*x,color)
                #print int(tracks[row]["trackID"]%200),color
                cv2.ellipse(canvas, 
                            tuple(map(int, tracks[row]["position"])),
                            tuple(map(int, [radius,radius])),
                            tracks[row]["angle"]*_TO_DEGREES,
                            0, 360,
                            color,
                            2,
                            cv2.CV_AA,
                            0)
                cv2.line(canvas, 
                            tuple(map(int, tracks[row]["position"])),
                            tuple(map(int, tracks[row]["position"] + 10*np.array([math.cos(angle), math.sin(angle)]))),
                            (arrow_color),
                            1,
                            cv2.CV_AA,
                            0)
            drawn.append(canvas)

        self._render(drawn)

class _AnimationTask(_RenderTask):

    _outputParam = None

    def _animate(self, frames, func, **animArgs):
        if self._outputParam is None: raise NotImplemented
        figure = plt.Figure(figsize=(6,6), dpi=300, facecolor='w')
        axes = figure.add_subplot(111)
        canvas = FigureCanvasAgg(figure) 
        chunks = 10
        multiframes = [frames[i:i+chunks] for i in xrange(0,len(frames),chunks)]
        count = 0
        for frames in multiframes:
            count += 1
            images = []
            for frame in frames:
                axes.clear()
                func(frame, axes)
                canvas.draw()

                image = np.fromstring(canvas.tostring_rgb(), dtype=np.uint8)
                image.shape = canvas.get_width_height() + (3,)
                images.append(image)
            self._render(images,num = str(count))
        if count > 1:
            self._joinParts(count)

class _PlotField(_AnimationTask):

    dependencies = [an.GridParticles]
    _fieldType = None # Options are "scalar", "vector"

    def run(self):
        points = self._import(an.GridParticles, "cellCenters")

        def doPlot(row, axes):
            axes.set_title("t = {0}".format(row['time']))
            if self._fieldType == 'scalar':
                shape = self._param(an.NUM_GRID_CELLS)
                axes.pcolormesh(points[:, 0].reshape(shape), 
                                points[:, 1].reshape(shape), 
                                row['data'].reshape(shape))
                                
            elif self._fieldType == 'vector':
                axes.quiver(points[:, 0], points[:, 1], 
                            row['data'][:, 0], row['data'][:, 1])
            else:
                raise NotImplemented
            
        self._animate(self._getTable(), doPlot)

    def _getTable(self): raise NotImplemented


PLOT_VELOCITY_FIELD_OUTPUT = scaffold.registerParameter("plotVelocityFieldOutput", "../plots/{0}-velocityField.avi")
"""The file path to render the output animation of PlotVelocityField to."""

class PlotVelocityField(_PlotField):
    name = "Plot Velocities"
    dependencies = _PlotField.dependencies + [an.CalculateVelocityField]
    _outputParam = PLOT_VELOCITY_FIELD_OUTPUT
    _fieldType = "vector"
    def _getTable(self): return self._import(an.CalculateVelocityField, "field")

PLOT_DENSITY_FIELD_OUTPUT = scaffold.registerParameter("plotDensityFieldOutput", "../plots/{0}-densityField.avi")
"""The file path to render the output animation of PlotDensityField to."""

class PlotDensityField(_AnimationTask):
    name = "Plot Densities"
    dependencies = [an_dens.GridParticles, an_dens.CalculateDensityField]
    _outputParam = PLOT_DENSITY_FIELD_OUTPUT
    _fieldType = "scalar"


    def run(self):
        points = self._import(an_dens.GridParticles, "cellCenters")

        def doPlot(row, axes):
            axes.set_title("t = {0}".format(row['time']))
            if self._fieldType == 'scalar':
                shape = self._param(an.NUM_GRID_CELLS)
                axes.pcolormesh(points[:, 0].reshape(shape), 
                                points[:, 1].reshape(shape), 
                                row['data'].reshape(shape))
            elif self._fieldType == 'vector':
                axes.quiver(points[:, 0], points[:, 1], 
                            row['data'][:, 0], row['data'][:, 1])
            else:
                raise NotImplemented
            
        self._animate(self._getTable(), doPlot)
   

    def _getTable(self): return self._import(an_dens.CalculateDensityField, "field")


class _PlotCorrelation(scaffold.Task):

    def run(self):
        radii = self._param(an.RADII)
        table = self._getTable()

        plt.figure()
        mean = np.empty_like(radii, float)
        for row in table.iterrows():
            plt.plot(radii, row['data'], '.k', markersize=3, label='_nolegend_')
            mean += row['data']

        mean /= table.nrows
        plt.plot(radii, mean, linewidth=3)

        output = _formatOutput(self, self._outputParam)
        plt.savefig(output, dpi=600)


PLOT_PARTICLE_DISTANCE_OUTPUT = scaffold.registerParameter("plotParticleDistanceOutput", "../plots/{0}-particleDistance.png")
"""The file path to render the output plot of PlotParticleDistance to."""

class PlotParticleDistance(_PlotCorrelation):

    name = "Plot Particle Distance"
    dependencies = [an.CorrelateParticleDistance]
    _outputParam = PLOT_PARTICLE_DISTANCE_OUTPUT

    def _getTable(self): 
        return self._import(an.CorrelateParticleDistance, "table")
