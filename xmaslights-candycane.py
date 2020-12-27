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

	# configurable parameters
	stripes = [[50,0,0], [0,50,0], [50,50,50]]
	num_twists = 5
	spin_rate = math.pi/100
	
	# state variables
	step = 0

	# loop
	while True:
		step += spin_rate
		swirl = math.sin(step/5)*num_twists # total swirl from top to bottom
		for index,c in enumerate(coords):
			theta = math.atan2(c[1],c[0]) # angle to Z axis
			theta += step # spin everything
			theta += swirl * (c[2]+450)/-900 # apply swirl from the top down
			stripe = int(theta%math.pi/math.pi*len(stripes))
			colour = stripes[stripe % len(stripes)] # misspelled color on purpouse
			pixels[index] = colour
		
		pixels.show()

# yes, I just put this at the bottom so it auto runs
xmaslight()
