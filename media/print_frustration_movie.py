# FOR MORE INFO VISIT:
# https://matplotlib.org/api/_as_gen/matplotlib.animation.FuncAnimation.html#matplotlib.animation.FuncAnimation

import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
import os


##################################################
#                 AUX. PARAMS                    #
##################################################
__BASE_DIR = os.path.dirname(os.path.abspath(__file__))
moods_file = os.path.join(__BASE_DIR, 'moods.data')
mood_data = []

#NAGENTS = 4
NAGENTS = 2
ymin, ymax = 0, 0 # initial values used to plot


##################################################
#               AUX. FUNCTIONS                   #
##################################################
def read_moods():
	''' Reads moods from file '''
	with open(moods_file) as fr:
		for line in fr:
			mood_data.append(np.fromstring( line, dtype=np.float, 
											sep=',' ))
			
def animate(i):
	'''
		Modifies the height of the bars because it is called for each 
		frame of the mp4
	'''
	y=mood_data[i+1]
	for i, b in enumerate(barcollection):
		b.set_height(y[i])


##################################################
#                   MAIN CODE                    #
##################################################
if __name__ == "__main__":
	# STEP 1: read the input file
	read_moods()
	nframes= len(mood_data) - 1

	# STEP 2: prepare the plot
	fig = plt.figure()
	plt.ylim([np.min(mood_data),np.max(mood_data)])
	x_coord=range(1,NAGENTS+1)
	barcollection = plt.bar(x_coord,mood_data[0])

	# STEP 3: call the animator. It will update the plot.
	anim=animation.FuncAnimation(fig,animate,repeat=False,blit=False, 
								 frames=nframes,interval=500) 

	# STEP 4: save the movie and plot
	anim.save('mymovie.mp4',writer=animation.FFMpegWriter(fps=10))

	plt.show()
