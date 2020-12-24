# Here are the libraries I am currently using:
import time
# import board
# import neopixel  # pip install rpi_ws281x adafruit-circuitpython-neopixel adafruit-blinka
import math
from collections import namedtuple  # for Point data structure
import pygame  # for virtual tree visuals


# You are welcome to add any of these:
# import random
# import numpy
# import scipy
# import sys

# If you want to have user changable values, they need to be entered from the command line
# so import sys sys and use sys.argv[0] etc
# some_value = int(sys.argv[0])


# class XmasTree:
#     def __init__(self, coord_filename):
#         self.coords = self.read_coordinates(coord_filename)
#         self.min_x = min(coord.x for coord in self.coords)
#         self.max_x = max(coord.x for coord in self.coords)
#         self.min_y = min(coord.y for coord in self.coords)
#         self.max_y = max(coord.y for coord in self.coords)
#         self.min_z = min(coord.z for coord in self.coords)
#         self.max_z = max(coord.z for coord in self.coords)
#
#         self.PIXEL_COUNT = len(self.coords)
#         assert (self.PIXEL_COUNT == 500)
#         self.pixels = neopixel.NeoPixel(board.D18, self.PIXEL_COUNT, auto_write=False)
#
#     def read_coordinates(self, coord_filename):
#         Point = namedtuple("Point", ["x", "y", "z"])  # so we can address point coordinates like humans
#         with open(coord_filename, 'r') as fin:
#             coords_raw = fin.readlines()
#         return list(map(lambda line: Point(*map(lambda item: int(item.strip()), line[1:-2].split(","))), coords_raw))
#
#     def display(self):
#         self.pixels.show()
#
#     def set_led_RGB(self, n, RGBcolor):
#         self.pixels[n] = [RGBcolor[1], RGBcolor[0], RGBcolor[2]]


class VirtualXmasTree:
    def __init__(self, coord_filename):
        self.coords = self.read_coordinates(coord_filename)
        self.min_x = min(coord.x for coord in self.coords)
        self.max_x = max(coord.x for coord in self.coords)
        self.min_y = min(coord.y for coord in self.coords)
        self.max_y = max(coord.y for coord in self.coords)
        self.min_z = min(coord.z for coord in self.coords)
        self.max_z = max(coord.z for coord in self.coords)

        self.PIXEL_COUNT = len(self.coords)
        assert (self.PIXEL_COUNT == 500)
        self.pixels = [[0, 0, 0]] * self.PIXEL_COUNT

        self.tree_size = self.max_z - self.min_z
        self.max_light_size = 10
        self.min_light_size = 4
        self.margin = self.tree_size * 0.1
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 800, 800
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Virtual Xmas Tree")

    def read_coordinates(self, coord_filename):
        Point = namedtuple("Point", ["x", "y", "z"])  # so we can address point coordinates like humans
        with open(coord_filename, 'r') as fin:
            coords_raw = fin.readlines()
        return list(map(lambda line: Point(*map(lambda item: int(item.strip()), line[1:-2].split(","))), coords_raw))

    def display(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)

        self.screen.fill((127, 127, 127))

        for p in range(len(self.coords)):
            screen_x = int(self.margin + self.WINDOW_WIDTH * ((self.coords[p].x - self.min_x) / self.tree_size))
            screen_y = int(self.WINDOW_HEIGHT - self.margin - self.WINDOW_HEIGHT * ((self.coords[p].z - self.min_z) / self.tree_size))
            on_screen_size = int(self.min_light_size + (self.coords[p].y - self.min_y) / (self.max_y - self.min_y) * (self.max_light_size - self.min_light_size))
            pygame.draw.circle(self.screen, self.pixels[p], (screen_x, screen_y), on_screen_size)

        pygame.display.flip()
        self.clock.tick(60)

    def set_led_RGB(self, n, RGBcolor):
        self.pixels[n] = RGBcolor


def xmaslight(tree):

    # VARIOUS SETTINGS
    
    # how much the rotation points moves each time
    dinc = 1
    
    # a buffer so it does not hit to extreme top or bottom of the tree
    buffer = 200
    
    # pause between cycles (normally zero as it is already quite slow)
    slow = 0
    
    # starting angle (in radians)
    angle = 0
    
    # how much the angle changes per cycle
    inc = 0.1
    
    # if you are turning a lot of lights on at once, keep their brightness down please
    colourA = [50, 0, 50]  # purple
    colourB = [50, 50, 0]  # yellow

    # INITIALISE SOME VALUES
    
    swap01 = 0
    swap02 = 0
    
    # direct it move in
    direction = -1
    
    # the starting point on the vertical axis
    c = 100 
    
    # run forever
    while True:

        time.sleep(slow)

        for led in range(len(tree.coords)):
            if math.tan(angle) * tree.coords[led].y <= tree.coords[led].z + c:
                tree.set_led_RGB(led, colourA)
            else:
                tree.set_led_RGB(led, colourB)

        # use the display() option as rarely as possible as it takes ages
        # do not use display() each time you change a LED but rather wait until you have changed them all
        tree.display()
        
        # now we get ready for the next cycle
        
        angle += inc
        if angle > 2*math.pi:
            angle -= 2*math.pi
            swap01 = 0
            swap02 = 0
        
        # this is all to keep track of which colour is 'on top'
        
        if angle >= 0.5*math.pi:
            if swap01 == 0:
                colour_hold = [i for i in colourA]
                colourA = [i for i in colourB]
                colourB = [i for i in colour_hold]
                swap01 = 1
                
        if angle >= 1.5*math.pi:
            if swap02 == 0:
                colour_hold = [i for i in colourA]
                colourA = [i for i in colourB]
                colourB = [i for i in colour_hold]
                swap02 = 1
        
        # and we move the rotation point
        c += direction * dinc
        
        if c <= tree.min_z + buffer:
            direction = 1
        if c >= tree.max_z - buffer:
            direction = -1


def run_lights():
    coord_filename = "Python/coords.txt"
    # tree = XmasTree(coord_filename)
    tree = VirtualXmasTree(coord_filename)
    xmaslight(tree)  # we pass the display to the function and let it run


if __name__ == "__main__":
    run_lights()
