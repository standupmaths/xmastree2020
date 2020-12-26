def xmaslight():
    # This is the code from my 
    
    #NOTE THE LEDS ARE GRB COLOUR (NOT RGB)
    
    # Here are the libraries I am currently using:
    import time
    ##import board
    ##import neopixel
    import re
    import math
    
    # You are welcome to add any of these:
    # import random
    # import numpy
    # import scipy
    # import sys
    
    # If you want to have user changable values, they need to be entered from the command line
    # so import sys sys and use sys.argv[0] etc
    # some_value = int(sys.argv[0])
    
    # IMPORT THE COORDINATES (please don't break this bit)
    
    coordfilename = "coords.txt"
	
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
    
    ##pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)
    
    
    # YOU CAN EDIT FROM HERE DOWN
    
    # I get a list of the heights which is not overly useful here other than to set the max and min altitudes
    xs = []
    ys = []
    zs = []
    for i in coords:
        xs.append(i[0])
        ys.append(i[1])
        zs.append(i[2])

    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
    min_z = min(zs)
    max_z = max(zs)
    
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
    colourA = [0,100,0] # red
    colourB = [25,75,0] # orange
    colourC = [90, 90, 0]  # yellow
    colourD = [75, 0, 0]  # green
    colourE = [75, 0, 75]  # teal
    colourF = [0, 0, 75]  # blue
    colourG = [0, 25, 75]  # indigo
    colourH = [0, 50, 75]  # violet
    run = 1
    while run == 1:
        
        time.sleep(slow)
        
        LED = 0
        pixels = [[0,0,0] for i in range(len(coords))] ## just a placeholder for now
        while LED < len(coords):
            if coords[LED][0] < 0:
                if coords[LED][1] < 0:
                    if coords[LED][2] < 0:
                        pass
                        pixels[LED] = colourA
                    else:
                        pass
                        pixels[LED] = colourB
                else:
                    if coords[LED][2] < 0:
                        pass
                        pixels[LED] = colourC
                    else:
                        pass
                        pixels[LED] = colourD
            else:
                if coords[LED][1] < 0:
                    if coords[LED][2] < 0:
                        pass
                        pixels[LED] = colourE
                    else:
                        pass
                        pixels[LED] = colourF
                else:
                    if coords[LED][2] < 0:
                        pass
                        pixels[LED] = colourG
                    else:
                        pass
                        pixels[LED] = colourH
            LED += 1
            print(pixels)
        # use the show() option as rarely as possible as it takes ages
        # do not use show() each time you change a LED but rather wait until you have changed them all
        ##pixels.show()
        
        # now we get ready for the next cycle
        # We do this similarly to how Matt did his translating plane effect: use a static spatial coloring function,
        # but rotate all of the LEDs!

        #Do rotate-y stuff here
        
    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
