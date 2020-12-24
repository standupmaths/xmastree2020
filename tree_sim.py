import threading
import numpy as np
import time
import colorsys

from matplotlib import pyplot, animation
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D


class TreeSimulator2000:
    """ Tree simulator that plots the LEDS in matplotlib """

    def __init__(self, coords):
        """
        coords: [x,y,z] coordinate for each LED in order
        colors: optional, initial colors for each LED in order
        """
        self.x_vals = [c[0] for c in coords]
        self.y_vals = [c[1] for c in coords]
        self.z_vals = [c[2] for c in coords]
        self.led_count = len(coords)

        self.colors = np.random.random((self.led_count, 4))

        # Starts the matplotlib in a different thread
        self.plot_thread = threading.Thread(target=self._animate, daemon=True)
        self.plot_thread.start()
        # True to make update get called once
        self.changed = True
        self.should_update = True

    def set_pixel(self, led_i, r, g, b):
        self.colors[led_i] = self._rgb_to_rgba(r, g, b)
        self.changed = True

    def show(self):
        # I just adjusted this number until the simulation matched the video pretty well
        time.sleep(0.034)
        self.should_update = True

    def _animate(self):
        self.fig = pyplot.figure()
        self.ax = Axes3D(self.fig)
        self.ax.set_facecolor((0.0, 0.27, 0.10))
        self.ax.view_init(azim=18.0, elev=12.0)
        self.h = self.ax.scatter(self.x_vals, self.y_vals, self.z_vals, c=self.colors)
        self.ani = FuncAnimation(self.fig, self._update, interval=16)
        pyplot.show()

    def _update(self, i):
        if not self.changed or not self.should_update: return

        self.changed = False
        self.should_update = False

        self.ax.clear()
        self.h = self.ax.scatter(self.x_vals, self.y_vals, self.z_vals, c=self.colors)
        # Make x,y,z proportional
        self.ax.set_xlim3d(-400, 400)
        self.ax.set_ylim3d(-400, 400)
        self.ax.set_zlim3d(-400, 400)

    def _rgb_to_rgba(self, r, g, b):
        """
        converts an rgb color into an rgba color. where darker rgb colors become transparent, not black.
        this is to better emulate an LED
        """
        # r, g, b must be out of 255
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        r, g, b = colorsys.hsv_to_rgb(h, s, max(v, 240))

        return [r / 255, g / 255, b / 255, min(v + 20, 255) / 255]

    def __setitem__(self, key, value):
        """
        The magic sauce, lets you set pixels by doing tree_sim[i] = [g,r,b]
        """
        if not isinstance(key, int):
            raise TypeError(f"Expected an int for index, not {type(key)}")

        if not (0 <= key < self.led_count):
            raise ValueError("Index is out of range")

        # value is GRB
        g = value[0]
        r = value[1]
        b = value[2]

        self.set_pixel(key, r, g, b)
