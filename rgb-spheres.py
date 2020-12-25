def xmaslight():
	# This is the code from my 
	
	#NOTE THE LEDS ARE GRB COLOUR (NOT RGB)
	
	# Here are the libraries I am currently using:
	import time
	#from sim import board
	#from sim import neopixel
	import board
	import neopixel
	import re
	import math
	import random
	import numpy
	
	# You are welcome to add any of these:
	# import scipy
	# import sys
	
	# If you want to have user changable values, they need to be entered from the command line
	# so import sys sys and use sys.argv[0] etc
	# some_value = int(sys.argv[0])
	
	# IMPORT THE COORDINATES (please don't break this bit)
	
	#coordfilename = "./coords.txt"
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

	# Calculates the distance of 2 vectors
	def vdist(v1, v2):
		if len(v1) != len(v2):
			return -1

		result = 0
		for i in range(len(v1)):
			result += (v1[i] - v2[i]) ** 2
		return math.sqrt(result)

	# init the spheres. Each sphere originates at a random LED
	sphere_origins = [ coords[random.randint(0, PIXEL_COUNT)],
	                   coords[random.randint(0, PIXEL_COUNT)],
					   coords[random.randint(0, PIXEL_COUNT)] ]
	radii = [0, 0, 0]

	# calculate maximum distance of any LED for each sphere's origin.
	# Used to determine the max radius each sphere will ever receive
	max_dists = [0, 0, 0]
	for i in range(PIXEL_COUNT):
		for s in range(3):
			dist = vdist(coords[i], sphere_origins[s])
			if max_dists[s] < dist:
				max_dists[s] = dist

	# The rate in which each sphere enlargens. When negative, the sphere is currently shrinking
	increment_rates = [0, 0, 0]
	for i in range(3):
		increment_rates[i] = max_dists[i] / (40 + random.random() * 60) # between 40 and 100 frames

	# infinitly many frames. Wohoo.
	while True:
		for i in range(PIXEL_COUNT):

			# calculate color for current pixel. Each rgb (grb) color value is 255 * dist / max_dist
			color = [0, 0, 0]
			for s in range(3):
				dist = abs(vdist(sphere_origins[s], coords[i]) - radii[s])
				color[s] = int(255 * dist / max_dists[s])

			pixels[i] = color
		pixels.show()
		
		# calculate radii for next iteration.
		for s in range(3):
			# Switch from enlarging to shrinking and vice versa, when needed
			new_radius = radii[s] + increment_rates[s]
			if new_radius >= max_dists[s] or new_radius <= 0:
				increment_rates[s] = -increment_rates[s]

			radii[s] += increment_rates[s]
	
	return 'DONE'

# yes, I just put this at the bottom so it auto runs
xmaslight()
