# Here are the libraries I am currently using:
import time
import board
import re
import math

# You are welcome to add any of these:
import numpy as np

USE_PLOT = False

if (USE_PLOT):
    import matplotlib.pyplot as plt
else:
    import neopixel


# plotting for testing


# Superior cylindrical coordinate system
class cyl_coords:
    def __init__(self, coords, idx):
        self.r = math.sqrt(coords[0]**2 + coords[1]**2)
        self.theta = math.atan2(coords[0], coords[1])
        self.z = coords[2]
        self.color = [0, 0, 0]
        self.idx = idx

    def rotate(self, rotation):
        new_rotation = (self.theta + rotation)
        while (new_rotation > np.pi):
            new_rotation -= 2*np.pi
        while (new_rotation < -np.pi):
            new_rotation += 2*np.pi
        self.theta = new_rotation
    # For plotting tests

    def get_coords(self):
        x = self.r * math.cos(self.theta)
        y = self.r * math.sin(self.theta)
        z = self.z
        return [x, y, z]

    def get_color(self):
        hex_name = hex((int(self.color[1]) << 16) | (
            int(self.color[0]) << 8) | int(self.color[2]))
        # Transform hex number into string format plot accepts
        return "#" + (8-len(hex_name))*"0" + hex_name[2:]


def xmaslight():
    # This is the code from my

    # NOTE THE LEDS ARE GRB COLOUR (NOT RGB)

    # If you want to have user changable values, they need to be entered from the command line
    # so import sys sys and use sys.argv[0] etc
    # some_value = int(sys.argv[0])

    # IMPORT THE COORDINATES (please don't break this bit)

    # coordfilename = "Python/coords.txt"
    coordfilename = "coords.txt"  # path just coords in git repo

    fin = open(coordfilename, 'r')
    coords_raw = fin.readlines()

    coords_bits = [i.split(",") for i in coords_raw]

    coords = []

    for slab in coords_bits:
        new_coord = []
        for i in slab:
            new_coord.append(int(re.sub(r'[^-\d]', '', i)))
        coords.append(new_coord)

    # set up the pixels (AKA 'LEDs')
    PIXEL_COUNT = len(coords)  # this should be 500

    if (USE_PLOT):
        pixels = coords  # set for local testing
    else:
        pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)

    rainbow_lights(pixels, coords)

    return 'DONE'


def rainbow_lights(pixels, coords):
    # Convert to cylindrical coordinates because who needs x,y,z
    cyl_coords_set = []
    max_z = -10000
    min_z = 10000
    for i in range(len(coords)):
        cyl = cyl_coords(coords[i], i)
        cyl_coords_set.append(cyl)
        max_z = max(max_z, cyl.z)
        min_z = min(min_z, cyl.z)

    # GRB Colors
    colors = [[0, 30, 0], [15, 15, 0], [30, 0, 0],
              [0, 15, 15], [0, 0, 30], [15, 0, 15]]
    # Scale for plot visualization, probably too high for LEDs
    if (USE_PLOT):
        colors = np.array(colors) * 4
    # Separate heights into discrete rings
    ring_height = (max_z - min_z) / (len(colors) - 1)

    inc = 0
    # Rotate 10 degrees each iteration
    rot = np.pi / 18.0

    # Setup interactive plotting
    if (USE_PLOT):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        plt.ion()

    while(True):
        # Get LEDs & colors
        for led_idx in range(len(pixels)):
            c = cyl_coords_set[led_idx]
            pixels[led_idx] = c.color

        # Show
        if (not USE_PLOT):
            pixels.show()

        # Update
        for c in cyl_coords_set:
            z_bin = (round((c.z - min_z)/ring_height) + inc) % len(colors)
            # ensure no out of bounds
            z_bin = max(min(z_bin, len(colors)-1), 0)
            c.rotate(rot)  # rotate all points
            # Get intensity scaling by rotation
            adjusted_rotation = (c.theta + np.pi/6.0 * z_bin) % (2.0 * np.pi)
            while (adjusted_rotation < 0):
                adjusted_rotation += 2.0*np.pi
            intensity = adjusted_rotation / (np.pi)  # Scale from 0 to 2
            colors_update = np.array(colors[z_bin]) * intensity
            c.color = np.rint(colors_update)  # rounds to nearest int

        inc += 1 % len(colors)

        # plotting the points
        if (USE_PLOT):
            plt.pause(0.1)
            ax.clear()
            for c in cyl_coords_set:
                p = c.get_coords()
                ax.scatter(p[0], p[1], p[2], zdir='z', c=c.get_color())
            plt.draw()


# yes, I just put this at the bottom so it auto runs
if __name__ == "__main__":
    xmaslight()
