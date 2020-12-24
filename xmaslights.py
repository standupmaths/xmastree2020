import time
import math

# You are welcome to add any of these:
# import random
# import numpy
# import scipy
# import sys

# If you want to have user changable values, they need to be entered from the command line
# so import sys sys and use sys.argv[0] etc
# some_value = int(sys.argv[0])


def xmaslights(tree):

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
