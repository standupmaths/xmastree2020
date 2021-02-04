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
    # import random
    # import numpy
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

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    # Authors: Calvin Keats, Matt Parker, Eugénie von Tunzelmann
    # Date: 12/23/2020
    #
    # A spinning tetrahedron to light up Matt Parker's Christmas Tree!
    # Code modified from: https://github.com/standupmaths/xmastree2020/blob/main/xmaslights-spin.py
    # 
    # Watch Matt's video: https://www.youtube.com/watch?v=TvlpIojusBE
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    import numpy as np

    # This function tells you if a given point is on the same side of a triangle (v1, v2, v3) as the point v4
    def sameSide(v1, v2, v3, v4, point):

        normal = np.cross(np.subtract(v2, v1), np.subtract(v3, v1))
        dotv4 = np.dot(normal, np.subtract(v4, v1))
        dotpoint = np.dot(normal, np.subtract(point, v1))

        return (np.sign(dotv4) == np.sign(dotpoint))

    # By checking a point against all the faces of a tetrahedron, we can tell if the point is inside or outside
    def pointInsideTetrahedron(v1, v2, v3, v4, point):
        return (sameSide(v1, v2, v3, v4, point) and
                sameSide(v2, v3, v4, v1, point) and
                sameSide(v3, v4, v1, v2, point) and
                sameSide(v4, v1, v2, v3, point))

    # This function rotates a point by 3 angles from their respective axes
    def matrixRotate(point, xAngle, yAngle, zAngle):
        v1 = np.array([[point[0]], [point[1]], [point[2]]])

        xAngle = math.radians(xAngle)
        yAngle = math.radians(yAngle)
        zAngle = math.radians(zAngle)

        xRotation = np.array([
            [1, 0, 0],
            [0, np.cos(xAngle), -np.sin(xAngle)],
            [0, np.sin(xAngle), np.cos(xAngle)]
        ])

        yRotation = np.array([
            [np.cos(yAngle), 0, np.sin(yAngle)],
            [0, 1, 0],
            [-np.sin(yAngle), 0, np.cos(yAngle)]
        ])

        zRotation = np.array([
            [np.cos(zAngle), -np.sin(zAngle), 0],
            [np.sin(zAngle), np.cos(zAngle), 0],
            [0, 0, 1]
        ])

        v2 = zRotation.dot(yRotation.dot(xRotation.dot(v1)))
        return v2[0][0], v2[1][0], v2[2][0]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    # Adjust these values to change the effect!
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Inside and outside colors in GRB
    insideColor = [115, 230, 0] # orange
    outsideColor = [0, 31, 77] # dark purple

    # Scale of the tetrahedron
    scale = 400

    # Offset of the tetrahedron. (0, 0, 0) will make it centered on the origin
    # Note that the tetrahedron does not rotate about its own center, but uses the various axes
    #   and so offsetting it means it won't rotate in-place
    xOffset = 0
    yOffset = 0
    zOffset = .4

    # The change of the angle per update in DEGREES
    # Rotations apply in the order X -> Y -> Z because I'm bad at quaternions
    xAngleChange = 5
    yAngleChange = 10
    zAngleChange = 15

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    # Update the LEDs!
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    frame = 0

    run = 1
    while run == 1:
        
        tetrahedron = [
            [(-1 + xOffset) * scale, (0 + yOffset) * scale, (-1/1.414 + zOffset) * scale],
            [(1 + xOffset) * scale, (0 + yOffset) * scale, (-1/1.414 + zOffset) * scale],
            [(0 + xOffset) * scale, (-1 + yOffset) * scale, (1/1.414 + zOffset) * scale],
            [(0 + xOffset) * scale, (1 + yOffset) * scale, (1/1.414 + zOffset) * scale]
        ]

        # Vertices of our tetrahedron, with the applied rotation
        tetrahedron = [
            matrixRotate(tetrahedron[0], xAngleChange * frame, yAngleChange * frame , zAngleChange * frame),
            matrixRotate(tetrahedron[1], xAngleChange * frame, yAngleChange * frame , zAngleChange * frame),
            matrixRotate(tetrahedron[2],  xAngleChange * frame, yAngleChange * frame , zAngleChange * frame),
            matrixRotate(tetrahedron[3],  xAngleChange * frame , yAngleChange * frame , zAngleChange * frame)
        ]
        
        LED = 0
        for coord in coords:
            if (pointInsideTetrahedron(tetrahedron[0], tetrahedron[1], tetrahedron[2], tetrahedron[3], coord)):
                pixels[LED] = insideColor
            else:
                pixels[LED] = outsideColor
            LED += 1
        
        # Send out the updates to the lights
        pixels.show()
        
        frame += 1
    
    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()