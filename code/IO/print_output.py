import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
import os

__BASE_DIR = os.path.dirname(os.path.abspath(__file__))
moods_file = os.path.join(__BASE_DIR, 'moods.data')
mood_data = []
NMOODS = 100
NAGENTS = 4
ymin, ymax = 0, 0

def print_moods():
    with open(moods_file, 'w') as fp:
        for i in range(NMOODS):
            fp.write(str(np.random.normal()))
            for j in range(NAGENTS-1):
                fp.write(','+str(np.random.normal()))
            fp.write("\n")

def read_moods():
    with open(moods_file) as fr:
        for line in fr:
            mood_data.append(np.fromstring( line, dtype=np.float, sep=',' ))

read_moods()
fig = plt.figure()
plt.ylim([np.min(mood_data),np.max(mood_data)])

n=99 #Number of frames
x_coord=range(1,NAGENTS+1)
print(len(mood_data))
barcollection = plt.bar(x_coord,mood_data[0])

def animate(i):
    y=mood_data[i+1]
    for i, b in enumerate(barcollection):
        b.set_height(y[i])

# call the animator.
# https://matplotlib.org/api/_as_gen/matplotlib.animation.FuncAnimation.html#matplotlib.animation.FuncAnimation
anim=animation.FuncAnimation(fig,animate,repeat=False,blit=False,frames=n,interval=500)

# anim.save('mymovie.mp4',writer=animation.FFMpegWriter(fps=10))
plt.show()
