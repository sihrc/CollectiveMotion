import csv
import numpy as np
reader = csv.reader(open("animation.csv",'rb'), delimiter = ",")
#my_data = np.genfromtxt('animation.csv',delimiter = ",")
#print my_data

i = 0
for row in reader:
	i+=1	
print i
