def xmaslight():
    # This is the code from my 
    
    #NOTE THE LEDS ARE GRB COLOUR (NOT RGB)
    
    # Here are the libraries I am currently using:
    import time
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
    
    pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)
    
    
    # YOU CAN EDIT FROM HERE DOWN
    
    # I get a list of the coordinates which is not overly useful here other than to set the max and min coordinates
    xs = []
    ys = []
    zs = []
    for i in coords:
        xs.append(i[0])
        ys.append(i[1])
        zs.append(i[2])

    slow = 0

    ballradius = 220

    # the eight colours in GRB order
    # if you are turning a lot of them on at once, keep their brightness down please
    colourA = [0,50,0] # red
    colourB = [40,60,0] # orange
    colourC = [45, 45, 0]  # yellow
    colourD = [38, 0, 0]  # green
    colourE = [38, 0, 38]  # teal
    colourF = [0, 0, 38]  # blue
    colourG = [0, 13, 38]  # indigo
    colourH = [0, 25, 38]  # violet

    run = 1
    coordmat = np.asmatrix(np.array(coords) + np.array([0.,0.,220]),
                           dtype=np.float64).transpose()  # Put LED coordinates into appropriate numpy matrix form to prepare for rotations.
    cnt = 0
    while run == 1:
        
        time.sleep(slow)
        
        LED = 0
        while LED < len(coords):
            # Check which octant LED lives in to generate colored octahedron
            if coordmat[0, LED]**2 + coordmat[1, LED]**2 + coordmat[2, LED]**2 < ballradius**2:
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
        pixels.show() ## Dan Walsh had to comment this out since he doesn't have LEDs. Won't work until hardware is available.
        
        # now we get ready for the next cycle
        # We do this similarly to how Matt did his translating plane effect: use a static spatial coloring function,
        # but rotate all of the LEDs!

        #Do rotate-y stuff here
        #Rotation Matrix

        # Small scalar amount (in radians) to rotate for one timestep of animation (plays role of "inc" variable in Matt's original code)
        theta = 0.2
        # UNIT vector axis about which to rotate for one timestep of animation
        if cnt%100 == 0: #Switch up the rotation axis every so often to keep things interesting
            ux = random.uniform(-1.0, 1.0)
            uy = random.uniform(-1.0, 1.0)
            uz = random.uniform(-1.0, 1.0)

            length = math.sqrt(ux**2+uy**2+uz**2)

            ux = ux / length
            uy = uy / length
            uz = uz / length

            u = np.matrix(
                [
                    [ux],
                    [uy],
                    [uz]
                ]
            )

        UX = np.matrix( #Cross Product Matrix
            [
                [0., -uz, uy],
                [uz, 0., -ux],
                [-uy, ux, 0.]
            ]
        )

        UXU = np.matmul(u,u.transpose()) #Generate Outer Product

        I = np.matrix( #Identity Matrix
            [
                [1., 0., 0.],
                [0., 1., 0.],
                [0., 0., 1.]
            ]
        )

        # Setup rotation matrix using R = \cos(\theta) I + \sin(\theta) UX + (1 - \cos(\theta)) UXU (Rodrigues' Rotation Formula)
        RotMat = np.cos(theta) * I + np.sin(theta) * UX + (1 - np.cos(theta)) * UXU

        coordmat = np.matmul(RotMat,coordmat) #Rotate all LEDs on tree according to RotMat
        cnt += 1
    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
