# Here are the libraries I am currently using:
import time

import board
import neopixel
import re
import math

# You are welcome to add any of these:
import random
# import numpy
# import scipy
# import sys


# Play with these values to change how coarse the 3D Fire effect is.
# Smaller value == faster
MATWX = 20
MATWY = 20
MATWZ = 60

# Change that value to change colour brightness.
# May need to tweak the palette if changing that value
maxBrightness = 255

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
        self._list = [0] * lx * ly * lz
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

    def copy(self, other):
        self._list = other._list[:]

    def getTree(self, x, y, z):
        localX, localY, localZ = self._bb.normalize(x, y, z)
        localX = int(localX * (self._wX - 1))
        localY = int(localY * (self._wY - 1))
        localZ = int(localZ * (self._wZ - 1))
        return self.get(localX, localY, localZ)

def xmaslight():
    # This is the code from my 

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

    # Color are G R B
    palette = [0] * 256

    # Transition points
    palBST = 70
    palB2R = 86 # Black to Red
    palR2Y = 99 # Red to Yellow

    # Black only
    for i in range(0, palBST):
        palette[i] = (0, 0, 0)
    # Black to red
    for i in range(palBST, palB2R):
        palette[i] = (0, int((i - palBST) / (palB2R - palBST) * maxBrightness), 0)
    # red to yellow
    for i in range(palB2R, palR2Y):
        palette[i] = (int((i - palB2R) / (palR2Y - palB2R) * maxBrightness), maxBrightness, 0)
    # yellow to white
    for i in range(palR2Y, 256):
        palette[i] = (255, 255, int((i - (palR2Y)) / (256 - palR2Y) * maxBrightness))

    treeBB = boundingBox()
    for i in coords:
        treeBB.update(i[0], i[1], i[2])

    treeBB.finalize()

    # Our working area. We work with a non code/cylinder shape as it
    # would make thing too complicated
    workMat = matrix(MATWX, MATWY, MATWZ, treeBB)
    oldMat = matrix(MATWX, MATWY, MATWZ, treeBB)

    slow = 0

    # yes, I just run which run is true
    run = 1
    while run == 1:

        time.sleep(slow)

        for LED in range(0, PIXEL_COUNT):
            v = workMat.getTree(coords[LED][0], coords[LED][1], coords[LED][2])
            pixels[LED] = palette[v]

        pixels.show()

        oldMat.copy(workMat)

        # Update the matrix
        for x in range(1, MATWX-1):
            for y in range(1, MATWY-1):
                for z in range(2, MATWZ):
                    v = oldMat.get(x, y, z-2)
                    v = v + oldMat.get(x-1, y, z-1)
                    v = v + oldMat.get(x, y-1, z - 1)
                    v = v + oldMat.get(x, y, z - 1)
                    v = v + oldMat.get(x, y+1, z - 1)
                    v = v + oldMat.get(x+1, y, z - 1)
                    v = max(min(int(v / 6), 255), 0)

                    workMat.set(x, y, z, v)

        # light the fire!
        for x in range(0, MATWX):
            for y in range(0, MATWY):
                for z in range(0, 2):
                    if random.uniform(0, 1) < 0.35:
                        workMat.set(x, y, z, 255)
                    else:
                        workMat.set(x, y, z, 0)

    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
