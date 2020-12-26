def xmaslight():
    # This is the code from my 
    
    #NOTE THE LEDS ARE GRB COLOUR (NOT RGB)
    
    # Here are the libraries I am currently using:
    import time
    import board
    import neopixel
    #from sim import board
    #from sim import neopixel
    import re
    import math
    
    # You are welcome to add any of these:
    import random
    import numpy as np
    # import scipy
    # import sys
    
    # If you want to have user changable values, they need to be entered from the command line
    # so import sys sys and use sys.argv[0] etc
    # some_value = int(sys.argv[0])
    
    # IMPORT THE COORDINATES (please don't break this bit)
    
    coordfilename = "Python/coords.txt"
	
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
    
    pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)
    
    # YOU CAN EDIT FROM HERE DOWN
    np.random.seed(int(time.time()))

    def length(v):
        return np.sqrt(np.sum(np.square(v)))

    def normalize(v):
        return np.divide(v, length(v))

    def clamp(amin, amax, v):
        return np.maximum(amin, np.minimum(amax, v))

    def randomDirVec(components = 3):
        return normalize([2.0*np.random.random() - 1.0 for x in range(components)])

    def randomColorVec(components = 3):
        return normalize([np.random.random() for x in range(components)])

    # maximum brightness, to avoid catching trees on fire
    BRIGHTNESS = 192
    # brightness falloff (over distance to the plane, square)
    FALLOFF = 1000.0
    # how far to move each plane, +/-
    RADIUS = 225
    # how far to move each plane, +/-
    PLANE_DISTANCE = 125
    # how many "frames" to wait before adding a new plane
    PLANE_TIMER = 128
    # controls how fast planes move, "frames" / divider (in radians)
    TIME_DIVIDER = 16.0

    INNER_COLOR = normalize([0.33, 0, 1.0])
    OUTER_COLOR = normalize([0.4, 0.75, 0.1])

    # reusing run as "frame" counter here
    run = 1
    slow = 0
    while run:
        time.sleep(slow)
        run += 1

        LED = 0
        while LED < len(coords):
            dist = length(coords[LED]) - RADIUS + PLANE_DISTANCE*math.sin(run / TIME_DIVIDER)
            falloff = FALLOFF / max(1.0, dist ** 2.0)

            if dist >= 0:
                pixColor = np.multiply(OUTER_COLOR, falloff)
            else:
                pixColor = np.multiply(INNER_COLOR, falloff)

            linearColor = clamp(0.0, 1.0, pixColor)
            gammaCorrected = np.power(linearColor, 1.0 / 2.2)
            pixels[LED] = list(gammaCorrected * BRIGHTNESS)
            LED += 1

        # use the show() option as rarely as possible as it takes ages
        # do not use show() each time you change a LED but rather wait until you have changed them all
        pixels.show()

    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
