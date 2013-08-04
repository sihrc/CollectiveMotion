import quivertools
import openpiv.process
import openpiv.scaling
import numpy as np
import os
from time import time
import warnings

def runPIV(frame_a,frame_b,dt):
	scaling_factor = 50
	#frame_a  = openpiv.tools.imread(image1)
	#frame_b  = openpiv.tools.imread(image2)

	#no background removal will be performed so 'mark' is initialized to 1 everywhere
	mark = np.zeros(frame_a.shape, dtype=np.int32)
	for I in range(mark.shape[0]):
	    for J in range(mark.shape[1]):
	        mark[I,J]=1

	#main algorithm
	with warnings.catch_warnings():
	    warnings.simplefilter("ignore")
	    x,y,u,v, mask=openpiv.process.WiDIM( frame_a, frame_b, mark, min_window_size=16, overlap_ratio=0.0, coarse_factor=2, dt=dt, validation_method='mean_velocity', trust_1st_iter=1, validation_iter=1, tolerance=0.7, nb_iter_max=3, sig2noise_method='peak2peak')
	
	#display results
	x, y, u, v = openpiv.scaling.uniform(x, y, u, v, scaling_factor = scaling_factor )
	openpiv.tools.save(x, y, u, v, mask,'PIVdata.txt')
	fig = quivertools.display_vector_field('PIVdata.txt',scale=scaling_factor, width=0.001)
	return fig
	#further validation can be performed to eliminate the few remaining wrong vectors

if __name__ == "__main__":
	print "Fill in."