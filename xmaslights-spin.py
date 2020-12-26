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
    import numpy as np
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
    
    # I get a list of the coordinates which is not overly useful here other than to set the max and min coordinates
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

    slow = 0


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
        coordmat = np.asmatrix(coords,dtype=np.float64).transpose()
        pixels = [[0,0,0] for i in range(len(coords))] ## just a placeholder for now; remove later
        RotMat = np.matrix(
            [
                [1., 0., 0.],
                [0., 1., 0.],
                [0., 0., 1.]
            ]
        ) #Identity Matrix for now
        coordmat = np.matmul(RotMat,coordmat)
        while LED < len(coords):
            if coordmat[0, LED] < 0:
                if coordmat[1, LED] < 0:
                    if coordmat[2, LED] < 0:
                        pixels[LED] = colourA
                    else:
                        pixels[LED] = colourB
                else:
                    if coordmat[2, LED] < 0:
                        pixels[LED] = colourC
                    else:
                        pixels[LED] = colourD
            else:
                if coordmat[1, LED] < 0:
                    if coordmat[2,LED] < 0:
                        pixels[LED] = colourE
                    else:
                        pixels[LED] = colourF
                else:
                    if coordmat[2, LED] < 0:
                        pixels[LED] = colourG
                    else:
                        pixels[LED] = colourH
            LED += 1
        # use the show() option as rarely as possible as it takes ages
        # do not use show() each time you change a LED but rather wait until you have changed them all
        ##pixels.show()
        
        # now we get ready for the next cycle
        # We do this similarly to how Matt did his translating plane effect: use a static spatial coloring function,
        # but rotate all of the LEDs!

        #Do rotate-y stuff here
        print(coordmat)
        
    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
