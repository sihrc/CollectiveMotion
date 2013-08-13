"""
Tasks related to analyzing particle tracks for density calculations.

:Edited: August 13, 2013 - contact(sihrc.c.lee@gmail.com)
"""

import numpy as np
from numpy.linalg import norm
import math
import tables as tb
import images
import scaffold
import particles

NUM_GRID_CELLS = scaffold.registerParameter("numGridCells_density", [20, 20])
"""The number of rows and columns in the particle grid."""

def _griddedPath(task, path):
    return "{0}{1}_{2}".format(path, *task._param(NUM_GRID_CELLS))

class GridParticles(scaffold.Task):
    """
    Creates an NxM grid and assigns a cell number to each particle at each 
    frame, which is useful for local correlations and general optimizations.
    """

    name = "Grid Particles"
    dependencies = [particles.FindParticlesViaMorph, images.ParseConfig]

    def isComplete(self):
        return self.context.hasNode(self._cellsPath)

    def export(self):
        self._loadCellSize()
        return dict(cellMap=self.context.node(self._cellMapPath),
                    cells=self.context.node(self._cellsPath),
                    cellCenters=self.context.node(self._cellCentersPath),
                    shape=(np.prod(self._param(NUM_GRID_CELLS)),),
                    cellSize=self._cellSize)

    def run(self):
        numGridCells = self._param(NUM_GRID_CELLS)
        self._loadCellSize()
        tracks = self._import(particles.FindParticlesViaMorph, "ellipses")
        
        cellMap, cellCenters = self._buildCellMap(numGridCells)
        cells = self._assignCells(tracks, cellMap)
        
        self.context.createChunkArray(self._cellMapPath, cellMap)
        self.context.createChunkArray(self._cellCentersPath, cellCenters)
        self.context.createChunkArray(self._cellsPath, cells)
        self.context.flush()

    def _loadCellSize(self):
        self._imageSize = self._import(images.ParseConfig, "info").imageSize
        self._cellSize = self._imageSize/self._param(NUM_GRID_CELLS)
        
    def _buildCellMap(self, numGridCells):
        numRows, numCols = numGridCells
        cellMap = np.empty(numGridCells, np.uint32)
        cellCenters = []
        halfSize = self._cellSize/2.0

        for row in range(numRows):
            for col in range(numCols):
                cellMap[row, col] = row*numCols + col
                cellCenters.append([row, col]*self._cellSize + halfSize)

        return cellMap, np.array(cellCenters, float)
        
    def _assignCells(self, tracks, cellMap):
        cells = np.empty((tracks.nrows, 1), np.uint32)
        for row, track in enumerate(tracks):
            i, j = track['position']*self.context.attrs.pixel // self._cellSize
            cells[row] = int(cellMap[_index(i), _index(j)]) 
        return cells

    @property
    def _cellsPath(self): return _griddedPath(self, "cells")
    @property
    def _cellMapPath(self): return _griddedPath(self, "cellMap")
    @property
    def _cellCentersPath(self): return _griddedPath(self, "cellCenters")


class CalculateByTime(scaffold.Task):

    dependencies = [particles.FindParticlesViaMorph]
    _tablePath = None

    def isComplete(self):
        return self.context.hasNode(self._tablePath)

    def export(self):
        return dict(table=self.context.node(self._tablePath))

    def run(self):
        if self._tablePath is None: raise NotImplemented

        self._tracks = self._import(particles.FindParticlesViaMorph, "ellipses")
        assert self._tracks.nrows > 0

        self._table = self._setupTable()
        currentTime = self._tracks[0]['frame'] * self.context.attrs.dt
        startRow = 0

        for row, time in enumerate(self._tracks.col('frame')):
            if time != currentTime:
                self._onTime(time, startRow, row)
                startRow = row
                currentTime = time
        self._onTime(currentTime, startRow, self._tracks.nrows)

        self._table.flush()

    def _setupTable(self):
        class TimeTable(tb.IsDescription):
            time = tb.Float32Col(pos=0)
            data = self._makeDataCol()
        return self.context.createTable(self._tablePath, TimeTable)

    def _makeDataCol(self): raise NotImplemented
    def _onTime(self, time, startRow, stopRow): raise NotImplemented


class GriddedField(CalculateByTime):

    dependencies = CalculateByTime.dependencies + [GridParticles]

    def export(self):
        return dict(field=self.context.node(self._tablePath))

    def run(self):
        self._shape = self._import(GridParticles, "shape")
        self._cells = self._import(GridParticles, "cells")
        CalculateByTime.run(self)

    def _onTime(self, time, start, stop):
        self._resetBuckets()
        for offset, track in enumerate(self._tracks.iterrows(start, stop)):
            row = start + offset
            self._addToBuckets(row, track, self._cells[row])
        self._appendBuckets(time)

    def _makeDataCol(self):
        return tb.Float32Col(shape=self._shape)

    def _resetBuckets(self):
        self._sums = np.zeros(self._shape, np.float32)
        self._counts = np.zeros(self._shape, np.uint16)

    def _appendBuckets(self, time):
        self._finalizeSums()
        self._table.row['time'] = time
        self._table.row['data'] = self._sums
        self._table.row.append()

    def _finalizeSums(self):
        nonzero = self._counts > 0
        self._sums[nonzero] /= self._counts[nonzero]

    def _addToBuckets(self, row, track, cell):
        self._counts[cell] += 1

    @property
    def _tablePath(self): return _griddedPath(self, self._tableName)

def _index(i): 
    return max([int(i), 0])

class CalculateDensityField(GriddedField):

    name = "Calculate Density Field"
    dependencies = GriddedField.dependencies + []
    _tableName = "densityField"

    def _finalizeSums(self):
        area = np.prod(self._import(GridParticles, "cellSize"))
        self._sums = self._counts/area
        np.savetxt('exportData.txt',self._sums)