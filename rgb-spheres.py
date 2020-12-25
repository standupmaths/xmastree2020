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
	
	# You are welcome to add any of these:
	# import numpy
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
	def vdist(v1: list, v2: list):
		if len(v1) != len(v2):
			return -1

		result = 0
		for i in range(len(v1)):
			result += (v1[i] - v2[i]) ** 2
		return math.sqrt(result)

	# Find coordinate that maximizes the distance for a given sez of other coords
	def find_furthest(points: list):
		max_dist = 0
		cur_pnt = points[0]
		for coord in coords:
			dist = math.inf
			for p in points:
				p_dist = vdist(p, coord)
				if p_dist < dist:
					dist = p_dist

			if (dist > max_dist):
				max_dist = dist
				cur_pnt = coord
		return cur_pnt


	# init sphere origins.
	# First sphere's origin is furthest from the coordinate system's origin
	# Second sphere's origin is the LED with the greatest distance from the first sphere's origin
	# Third sphere's origin is the LED where the distance for both other spheres is maximized.
	sphere_origins = []
	sphere_origins.append(find_furthest([[0, 0, 0]]))
	sphere_origins.append(find_furthest(sphere_origins))
	sphere_origins.append(find_furthest(sphere_origins))

	# calculate maximum distance of any LED for each sphere's origin.
	# Used to determine the max radius each sphere will ever receive
	max_dists = [0, 0, 0]
	for coord in coords:
		for i in range(3):
			dist = vdist(coord, sphere_origins[i])
			if max_dists[i] < dist:
				max_dists[i] = dist

	# The rate in which each sphere enlargens. When negative, the sphere is currently shrinking.
	increment_rates = [0, 0, 0]
	# The radius of each sphere. Initial value is randomized
	radii = [0, 0, 0]

	# set initial increment rates and radii 
	for i in range(3):
		# Frames per cycle for current sphere
		frames = i * 40 + 120
		increment_rates[i] = max_dists[i] / frames

		# Random start radius 
		radii[i] = random.random() * frames * increment_rates[i]

	# infinitly many frames. Wohoo.
	while True:
		for i in range(PIXEL_COUNT):

			# calculate color for current pixel. Each rgb (grb) color value is 255 * dist / max_dist
			color = [0, 0, 0]
			for s in range(3):
				dist = abs(vdist(sphere_origins[s], coords[i]) - radii[s])
				color[s] = int(255 * (1 - dist / max_dists[s]) ** 3)

			pixels[i] = color
		pixels.show()
		# calculate radii for next iteration.
		for s in range(3):
			# Switch from enlarging to shrinking and vice versa, as needed
			new_radius = radii[s] + increment_rates[s]
			if new_radius >= max_dists[s] or new_radius <= 0:
				increment_rates[s] = -increment_rates[s]

			radii[s] += increment_rates[s]
	return 'DONE'

# yes, I just put this at the bottom so it auto runs
xmaslight()
