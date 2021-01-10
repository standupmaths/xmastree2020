    
def area(x1, y1, x2, y2, x3, y3):
    """ A utility function to calculate area of triangle formed by (x1, y1), (x2, y2) and (x3, y3)

    Downloaded from: https://www.geeksforgeeks.org/check-whether-a-given-point-lies-inside-a-triangle-or-not/
    """
    return abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0)
  
  

def isInside(x1, y1, x2, y2, x3, y3, x, y):
    """
    A function to check whether point P(x, y) lies inside the triangle formed by A(x1, y1), B(x2, y2) and C(x3, y3)
    
    Function downloaded from: https://www.geeksforgeeks.org/check-whether-a-given-point-lies-inside-a-triangle-or-not/
    """
    # Calculate area of triangle ABC
    A = area (x1, y1, x2, y2, x3, y3)
  
    # Calculate area of triangle PBC
    A1 = area (x, y, x2, y2, x3, y3)
      
    # Calculate area of triangle PAC
    A2 = area (x1, y1, x, y, x3, y3)
      
    # Calculate area of triangle PAB
    A3 = area (x1, y1, x2, y2, x, y)
      
    # Check if sum of A1, A2 and A3
    # is same as A
    if(A == A1 + A2 + A3):
        return True
    else:
        return False

    
def point_inside_triangle(triangle, point):
    """
    Checks if a 3D point lies inside a 3D triangle shape
    """
    p1, p2, p3, p4 = triangle
    
    p1x, p1y, p1z = p1
    p2x, p2y, p2z = p2
    p3x, p3y, p3z = p3
    p4x, p4y, p4z = p4
    
    px, py, pz = point
    
    # I don't know if this is mathematically correct for all cases of triangle, but it works well enough for my simple triangle
    # in a non-safety critical cristmas tree
    xz =isInside(p1x, p1z, p2x, p2z, p4x, p4z, px, pz) # projection on the x-z plane
    xy =isInside(p1x, p1y, p2x, p2y, p3x, p3y, px, py) # projection on the xy plane
    yz = isInside(p3y, p3z, p1y, p1z, p4y, p4z, py, pz) # projection on the yz plane
    return xz and xy and yz
    

def mid(p1, p2):
    """ Returns the midpoint between 2 3D points """
    return (p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2

def draw_triangle(coords, triangle, colour):
    """ A debug function I initially used for a 2D triangle approach. can be removed now """
    # Draw the matplotlib stuff
    x = [line[0] for line in triangle]
    y = [line[1] for line in triangle]
    plt.fill(x, y, c=[a/255.0 for a in colour])
    

def draw_triangle_xmastree(coords, pixels, triangle, colour):
    for LED, coordinate in enumerate(coords):
        x, y, z = coordinate
        if point_inside_triangle(triangle, (x, y,z)):
            pixels[LED] = colour
    # TODO perhaps we want to not show it here sometimes, or do actually show it here for longer than is currently happening
    pixels.show()
    

def sierpinsky(coords, pixels, triangle, depth, maxdepth):
    # Only draw the sierpinsky triangle up to a maximum depth
    if depth > maxdepth:
        return
    
    # Draw the current triangle on the christmas tree
    draw_triangle_xmastree(coords, pixels, triangle, colours[depth])
    
    # Each triangle consists of four ordered points (x,y,z).
    # In my case I like them counterclockwise starting with the bottom-left point, bottom first
    p1, p2, p3, p4 = triangle
    
    # Find the new bottom midpoints of this 3D triangle
    mid1 = mid(p1, p2)
    mid2 = mid(p2, p3)
    mid3 = mid(p3,p1)
    
    # Find the new top midpoints of this 3D triangle
    mid4 = mid(p1, p4)
    mid5 = mid(p2, p4)
    mid6 = mid(p3, p4)
    
    # Recursively update the triangle with the next depth
    sierpinsky(coords, pixels, [p1, mid1, mid3, mid4], depth+1, maxdepth)
    sierpinsky(coords, pixels, [mid1, p2, mid2, mid5], depth+1, maxdepth)
    sierpinsky(coords, pixels, [mid3, mid2, p3, mid6], depth+1, maxdepth)
    sierpinsky(coords, pixels, [mid4, mid5, mid6, p4], depth+1, maxdepth)
    
    
    
# Global colours to be used in the christmas tree function
colours = [[250,250,250], [250,0,0], [0,0,250], [0,250,0]]
    
    
def xmaslight():
    # This is the code from my
    
    #NOTE THE LEDS ARE GRB COLOUR (NOT RGB)
    
    # Here are the libraries I am currently using:
    import time
    import re
    import math
    
    # use real leds
    import board
    import neopixel
    
    # You are welcome to add any of these:
    # import random
    # import numpy as np
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
    
    # I get a list of the heights which is not overly useful here other than to set the max and min altitudes
    heights = []
    for i in coords:
        heights.append(i[2])
    
    min_alt = min(heights)
    max_alt = max(heights)
    
    # VARIOUS SETTINGS
    # yes, I just run which run is true
    run = 1
    while run == 1:
    
        # The initial triangle. You can change the coordinates here a bit if you want the triangle bigger or smaller
        triangle = [
            [-300, -300, -400],
            [300, -300, -400],
            [0, 300, -400],
            [0, 0, 400],
        ]
        
        # You can recurse all you want, but a max depth of 3 is already slow enough...
        # At some point the christmas tree is simply not dense enough to appreciate more recursion.
        for maxdepth in range(3):
            sierpinsky(coords, pixels, triangle, 0, maxdepth)
            
        # To be honest, I don't know if I should let the christmas tree sleep at some point or not. The initial phases (not too much recursion) go a bit too fast, while the final phase (very deep recursion) is a bit too slow IMO.
#        time.sleep(1)
        
        
    return 'DONE'

# yes, I just put this at the bottom so it auto runs
xmaslight()
