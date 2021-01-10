# Here are the libraries I am currently using:
import time

import board
import neopixel
import re
import math

# You are welcome to add any of these:
# import random
# import numpy
# import scipy
# import sys


# Play with these values to change how coarse the plasma effect is.
# Smaller value == faster
MATWX = 20
MATWY = 20
MATWZ = 60

# Set this value to lower the RGB (1 = full range, 0.5 = Half range, etc...)
dimLight = 0.2

class boundingBox():
    def __init__(self):
        self.minX = math.inf
        self.maxX = -math.inf
        self.minY = math.inf
        self.maxY = -math.inf
        self.minZ = math.inf
        self.maxZ = -math.inf
        self.wX = 0
        self.wY = 0
        self.wZ = 0

    def update(self, x, y, z):
        if self.minX > x:
            self.minX = x
        if self.maxX < x:
            self.maxX = x

        if self.minY > y:
            self.minY = y
        if self.maxY < y:
            self.maxY = y

        if self.minZ > z:
            self.minZ = z
        if self.maxZ < z:
            self.maxZ = z

    def finalize(self):
        self.wX = self.maxX - self.minX
        self.wY = self.maxY - self.minY
        self.wZ = self.maxZ - self.minZ

    def normalize(self, x, y, z):
        lx = (x - self.minX) / self.wX
        ly = (y - self.minY) / self.wY
        lz = (z - self.minZ) / self.wZ
        return lx, ly, lz


class matrix():
    def __init__(self, lx, ly, lz, bb):
        self._list = []
        for i in range(lx * ly * lz):
            self._list.append([0, 0, 0])

        self._strideX = 1
        self._strideY = self._strideX * lx
        self._strideZ = self._strideY * ly
        self._bb = bb
        self._wX = lx
        self._wY = ly
        self._wZ = lz

    def get(self,x, y, z):
        return self._list[x * self._strideX + y * self._strideY + z * self._strideZ]

    def set(self, x, y, z, val):
        self._list[x * self._strideX + y * self._strideY + z * self._strideZ] = val

    def getTree(self, x, y, z):
        localX, localY, localZ = self._bb.normalize(x, y, z)
        localX = int(localX * (self._wX - 1))
        localY = int(localY * (self._wY - 1))
        localZ = int(localZ * (self._wZ - 1))
        return self.get(localX, localY, localZ)


def dist(x, y, z, wx, wy, wz):
    return math.sqrt((x - wx) * (x - wx) + (y - wy) * (y - wy) + (z - wz) * (z - wz))


def xmaslight():
    # NOTE THE LEDS ARE GRB COLOUR (NOT RGB)

    # If you want to have user changable values, they need to be entered from the command line
    # so import sys sys and use sys.argv[0] etc
    # some_value = int(sys.argv[0])

    # IMPORT THE COORDINATES (please don't break this bit)

    coordfilename = "coords.txt"

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

    pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)

    # YOU CAN EDIT FROM HERE DOWN

    treeBB = boundingBox()
    for i in coords:
        treeBB.update(i[0], i[1], i[2])

    treeBB.finalize()

    # Our working area. We work with a non code/cylinder shape as it
    # would make thing too complicated
    workMat = matrix(MATWX, MATWY, MATWZ, treeBB)

    slow = 0

    t = 0

    # yes, I just run which run is true
    run = 1
    while run == 1:

        time.sleep(slow)

        for LED in range(0, PIXEL_COUNT):
            pixels[LED] = workMat.getTree(coords[LED][0], coords[LED][1], coords[LED][2])

        pixels.show()

        # Update the matrix
        for x in range(0, MATWX):
            for y in range(0, MATWY):
                for z in range(0, MATWZ):
                    d1 = dist(x + t, y, z, MATWX, MATWY, MATWZ)
                    d2 = dist(x, y, z,  MATWX/2, MATWY/2, MATWZ)
                    d3 = dist(x, y + t / 7, z, MATWX * 0.75, MATWY/2, MATWZ)
                    d4 = dist(x, y, z, MATWX*0.75, MATWY, MATWZ)

                    value = math.sin(d1 / 8) + math.sin(d2 / 8.0) + math.sin(d3 / 7.0) + math.sin(d4 / 8.0)

                    colour = int((4 + value)) * 32
                    r = min(colour, 255) * dimLight
                    g = min(colour * 2, 255) * dimLight
                    b = min(255 - colour, 255) * dimLight

                    workMat.set(x, y, z, (g, r, b))
        t = t + 1

    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
