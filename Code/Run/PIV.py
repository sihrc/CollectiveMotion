import openpiv.tools
import oppenpiv.process
import openpiv.scaling

import os

path = "..\\..\\Data\July292011\High"
save = "..\\Analysis\\PIV_results"
os.makedirs(save)
def _run(image1,image2,save):
	frame_a = openpiv.tools.imread(image1)
	frame_b = openpiv.tools.imread(image2)
	u, v, sig2noise = openpiv.process.extended_search_area_piv( frame_a, frame_b, window_size=24, overlap=12, dt=0.02, search_area_size=64, sig2noise_method='peak2peak' )
	x, y = openpiv.process.get_coordinates( image_size=frame_a.shape, window_size=24, overlap=12 )
	u, v, mask = openpiv.validation.sig2noise_val( u, v, sig2noise, threshold = 1.3 )
	u, v = openpiv.filters.replace_outliers( u, v, method='localmean', n_iter=10, kernel_size=2)
	x, y, u, v = openpiv.scaling.uniform(x, y, u, v, scaling_factor = 96.52 )
	openpiv.tools.save(x, y, u, v, 'exp1_001.txt' )

if __name__ == '__main__':
	_run('Series080_t013_ch00.tif','Series080_t014_ch00')





