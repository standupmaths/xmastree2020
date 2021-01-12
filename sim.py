import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d
plt.style.use("dark_background")

coords = list(map(eval, open("coords.txt").readlines()))
x = list(c[0] for c in coords)
y = list(c[1] for c in coords)
z = list(c[2] for c in coords)

class board:
    D18 = None

class neopixel:
    class NeoPixel:
        def __init__(self, _pin, n, *args, **kwargs):
            self.pixels = [(0, 0, 0)] * n
            self.ax = plt.axes(projection="3d")
        
        def __setitem__(self, index, color):
            self.pixels[index] = (2*color[1] / 255.0, 2*color[0] / 255.0, 2*color[2] / 255.0, 1)

        def show(self):
            self.ax.scatter(x, y, z, c=self.pixels)
        
            X,Y,Z = np.array(x),np.array(y),np.array(z) 
            max_range = np.array([X.max()-X.min(), Y.max()-Y.min(), Z.max()-Z.min()]).max()
            Xb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][0].flatten() + 0.5*(X.max()+X.min())
            Yb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][1].flatten() + 0.5*(Y.max()+Y.min())
            Zb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][2].flatten() + 0.5*(Z.max()+Z.min())
            # Comment or uncomment following both lines to test the fake bounding box:
            for xb, yb, zb in zip(Xb, Yb, Zb):
                self.ax.plot([xb], [yb], [zb], 'w')
            plt.pause(1 / 1000)
            self.ax.cla()
