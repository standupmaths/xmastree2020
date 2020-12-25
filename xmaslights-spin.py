# Here are the libraries I am currently using:
import time
import board
import re
import math

# You are welcome to add any of these:
# import random
import numpy as np
# import scipy
# import sys

USE_PLOT = False

if (USE_PLOT):
    import matplotlib.pyplot as plt
else:
    import neopixel


# plotting for testing


# Superior cylindrical coordinate system
class cyl_coords:
    def __init__(self,coords, idx):
        self.r = math.sqrt(coords[0]**2 + coords[1]**2)
        self.theta = math.atan2(coords[0],coords[1])
        self.z = coords[2]
        self.color = [0,0,0]
        self.idx = idx
    def rotate(self,rotation):
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
        return [x,y,z]
    def get_color(self):
        hex_name = hex((int(self.color[1]) << 16) | (int(self.color[0]) << 8) | int(self.color[2]))
        # Transform hex number into string format plot accepts
        return "#" + (8-len(hex_name))*"0" + hex_name[2:]


def xmaslight():
    # This is the code from my 
    
    #NOTE THE LEDS ARE GRB COLOUR (NOT RGB)
    
    # If you want to have user changable values, they need to be entered from the command line
    # so import sys sys and use sys.argv[0] etc
    # some_value = int(sys.argv[0])
    
    # IMPORT THE COORDINATES (please don't break this bit)
    
    #coordfilename = "Python/coords.txt"
    coordfilename = "coords.txt" # path just coords in git repo
	
    fin = open(coordfilename,'r')
    coords_raw = fin.readlines()
    
    coords_bits = [i.split(",") for i in coords_raw]
    
    coords = []
    
    for slab in coords_bits:
        new_coord = []
        for i in slab:
            new_coord.append(int(re.sub(r'[^-\d]','', i)))
        coords.append(new_coord)
    
    #set up the pixels (AKA 'LEDs')
    PIXEL_COUNT = len(coords) # this should be 500
    
    if (USE_PLOT):
        pixels = coords # set for local testing
    else:
        pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)
    
    
    # YOU CAN EDIT FROM HERE DOWN
    #matts_lights(pixels, coords)
    teals_lights(pixels, coords)
        
    return 'DONE'

def teals_lights(pixels, coords):
    # Convert to cylindrical coordinates because who needs x,y,z
    cyl_coords_set = []
    max_z = -10000
    min_z = 10000
    for i in range(len(coords)):
        cyl = cyl_coords(coords[i],i)
        cyl_coords_set.append(cyl)
        max_z = max(max_z, cyl.z)
        min_z = min(min_z, cyl.z)
    
    # GRB Colors
    colors = [[0,30,0], [15,15,0], [30,0,0], [0,15,15], [0,0,30], [15, 0, 15]]
    # Scale for plot visualization, probably too high for LEDs
    if (USE_PLOT):
        colors = np.array(colors) * 4
    # Separate heights into discrete rings
    ring_height = (max_z - min_z) / (len(colors) - 1);
    
    
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
            z_bin = max(min(z_bin,len(colors)-1),0) # ensure no out of bounds
            c.rotate(rot) # rotate all points
            # Get intensity scaling by rotation
            adjusted_rotation = (c.theta + np.pi/6.0 * z_bin) % (2.0 * np.pi)
            while (adjusted_rotation < 0):
                adjusted_rotation += 2.0*np.pi
            intensity = adjusted_rotation / (np.pi) # Scale from 0 to 2
            colors_update = np.array(colors[z_bin]) * intensity
            c.color = np.rint(colors_update) # rounds to nearest int
        
        inc += 1 % len(colors)

        # plotting the points
        if (USE_PLOT):
            plt.pause(0.1)
            ax.clear()
            for c in cyl_coords_set:
                p = c.get_coords()
                ax.scatter(p[0], p[1], p[2], zdir='z', c=c.get_color())
            plt.draw()


def matts_lights(pixels, coords):
    # I get a list of the heights which is not overly useful here other than to set the max and min altitudes
    heights = []
    for i in coords:
        heights.append(i[2])
    
    min_alt = min(heights)
    max_alt = max(heights)
    
    # VARIOUS SETTINGS
    
    # how much the rotation points moves each time
    dinc = 1
    
    # a buffer so it does not hit to extreme top or bottom of the tree
    buffer = 200
    
    # pause between cycles (normally zero as it is already quite slow)
    slow = 0
    
    # startin angle (in radians)
    angle = 0
    
    # how much the angle changes per cycle
    inc = 0.1
    
    # the two colours in GRB order
    # if you are turning a lot of them on at once, keep their brightness down please
    colourA = [0,50,50] # purple
    colourB = [50,50,0] # yellow
    
    
    # INITIALISE SOME VALUES
    
    swap01 = 0
    swap02 = 0
    
    # direct it move in
    direction = -1
    
    # the starting point on the vertical axis
    c = 100 
    
    # yes, I just run which run is true
    run = 1
    while run == 1:
        
        time.sleep(slow)
        
        LED = 0
        while LED < len(coords):
            if math.tan(angle)*coords[LED][1] <= coords[LED][2]+c:
                pixels[LED] = colourA
            else:
                pixels[LED] = colourB
            LED += 1
        
        # use the show() option as rarely as possible as it takes ages
        # do not use show() each time you change a LED but rather wait until you have changed them all
        pixels.show()
        
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
                colourA =[i for i in colourB]
                colourB = [i for i in colour_hold]
                swap01 = 1
                
        if angle >= 1.5*math.pi:
            if swap02 == 0:
                colour_hold = [i for i in colourA]
                colourA =[i for i in colourB]
                colourB = [i for i in colour_hold]
                swap02 = 1
        
        # and we move the rotation point
        c += direction*dinc
        
        if c <= min_alt+buffer:
            direction = 1
        if c >= max_alt-buffer:
            direction = -1

# yes, I just put this at the bottom so it auto runs
if __name__ == "__main__":
    xmaslight()
