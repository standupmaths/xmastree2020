import matplotlib.pyplot as plt
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
            self.pixels[index] = (color[1] / 255.0, color[0] / 255.0, color[2] / 255.0, 1)

        def show(self):
            self.ax.scatter(x, y, z, c=self.pixels)
            plt.pause(1 / 1000)
            self.ax.cla()