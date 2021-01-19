# Written by Logan Press

# Inspired by Westworld Season 3

def xmaslight():
    # This is the code from my 
    
    #NOTE THE LEDS ARE GRB COLOUR (NOT RGB)
    
    # Here are the libraries I am currently using:
    import time
    import board 
    import neopixel
    import re
    import math
    
    # You are welcome to add any of these:
    import random # Don't mind if I do!
    # import numpy
    # import scipy
    # import sys
    
    # If you want to have user changable values, they need to be entered from the command line
    # so import sys sys and use sys.argv[0] etc
    # some_value = int(sys.argv[0])
    
    # IMPORT THE COORDINATES (please don't break this bit)
    ## ok ;)
    
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
    
    # I get a list of the heights which is not overly useful here other than to set the max and min altitudes
    heights = []
    for i in coords:
        heights.append(i[2])
    
    min_alt = min(heights)
    max_alt = max(heights)
    
    # VARIOUS SETTINGS
    
    # a buffer so it does not hit to extreme top or bottom of the tree
    top_buffer = 100
    bottom_buffer = 50
    
    bottom = min_alt + bottom_buffer
    top = max_alt - top_buffer

    # coord list sorted ascending by height
    sortedCoords = sorted(coords, key=lambda coord: coord[2])

    # filter out the coords outside of the buffer
    usedCoords = list(filter(lambda c: c[2] >= bottom and c[2] <= top, sortedCoords))

    # to get correct angle from the arcsine
    def findAngle(coord):
        if (coord[1] < 0):
            return 2 * math.pi - math.acos(coord[0] / math.sqrt(coord[0] ** 2 + coord[1] ** 2))
        else:
            return math.acos(coord[0] / math.sqrt(coord[0] ** 2 + coord[1] ** 2))

    # brute-force searches the coord list to find the LED index (I know)
    def coordToLed(coord):
        for i in range(0, len(usedCoords)):
            c = coords[i]
            if coord[0] == c[0] and coord[1] == c[1] and coord[2] == c[2]:
                return i
    
    # separate usable lights into 20 bands; please tweak as needed
    bands = []
    numBands = 20
    bandHeight = (top - bottom) / numBands
    for i in range(0, numBands):
        # this makes the band fall within its required height range (from the bottom of the tree, up)
        newBand = list(filter(lambda c: c[2] >= bottom + i * bandHeight and c[2] < bottom + (i+1) * bandHeight and c[2] <= top, usedCoords))
        newBand = sorted(newBand, key=lambda c: findAngle(c))
        if len(newBand) > 0:
            bands.append(newBand)
    
    # the two colours in GRB order
    # if you are turning a lot of them on at once, keep their brightness down please
    color = [0, 145, 0] # hope this isn't too blinding; feel free to scale as needed
    

    # keep track of which bands are running
    bandsInUse = {}
    bandLimit = 15    # this many bands will have lights on at any one time; please tweak as needed
    currentBands = 0

    # initialize all bands to not be used
    for b in range(0, len(bands)):
        bandsInUse[b] = { "inUse": False }

    # tweak these as needed
    fadeTime = 1.0      # in seconds
    fadeInterval = 0.05  # in seconds; essentially the fade's time resolution

    # I update these every iteration below
    redValues = [0 for i in range(0, len(coords))]

    startTime = time.time()
    currentTime = startTime
    lastFade = 0

    while True:
        previousTime = currentTime
        currentTime = time.time() - startTime
        deltaTime = currentTime - previousTime
        if currentTime > (lastFade + fadeInterval): # fading first, so that the pixels get to light fully before fading
            for i in range(0, len(redValues)):
                # fade all the red lights after being lit
                if redValues[i] > 0:
                    redValues[i] -= int((color[1] / fadeTime) * (currentTime - lastFade))  # decrement red value based on amount of time since last decrement for smoothness
                    if redValues[i] < 0:
                        redValues[i] = 0   # just in case we accidentally dip below 0
            lastFade = currentTime
            # print(redValues)
        if currentBands < bandLimit:                     # add a random new band until we hit the limit
            bandIndex = random.randrange(0, len(bands))
            if not bandsInUse[bandIndex]["inUse"]:
                bandsInUse[bandIndex] = {
                    "inUse": True,
                    "currentAngle": random.uniform(0, 2 * math.pi - 0.01), # in radians
                    "startTime": currentTime,
                    "timeToRun": random.uniform(1, 2), # in seconds; this is the amount of time this band's lit
                    "speed": random.uniform(0.5, 2)    # in radians per second; the rotational speed at which the "band marker" travels
                }
                currentBands += 1
        for b in bandsInUse.keys():
            band = bandsInUse[b]
            if band["inUse"]:
                if currentTime - band["startTime"] <= band["timeToRun"]:    # if band hasn't yet run for its full duration
                    previousAngle = band["currentAngle"]
                    #   Add the increment to the angle below, based on time and rotation speed; wrap around if we hit 2pi:
                    band["currentAngle"] = (band["currentAngle"] + band["speed"] * deltaTime) % (math.pi * 2)
                    #   Get all lights which fall between the last angle and the current angle (all lights we've "hit" since last update)
                    coordsToLight = list(filter(lambda c: findAngle(c) <= band["currentAngle"] and findAngle(c) >= previousAngle, bands[b]))
                    # if len(coordsToLight) > 0:   # this is just debugging
                    #     print(coordsToLight)
                    for c in coordsToLight:
                        led = coordToLed(c)
                        if led != None:   # sometimes this happens, I guess it's finding coords outside the buffer
                            redValues[led] = color[1]
                    # print(band["currentAngle"])
                else:
                    # if we're done, set the band to not being used
                    band["inUse"] = False
                    currentBands -= 1
        for i in range(0, len(redValues)):
            pixels[i] = [0, redValues[i], 0] # setting all pixels before displaying
        # print(redValues)

        pixels.show()
        
        
    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
