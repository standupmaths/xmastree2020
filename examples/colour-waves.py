import math
import random
import sys

def usage():
	print( sys.argv[0] + " maximum_brightness(Default 100,  10-254) maximum_number_of_spheres(Default 5, 1-10)")
# if you are turning a lot of them on at once, keep their brightness down please
max_brightness = 100
min_brightness = math.floor(max_brightness/2)   #Min brightness for creating a new colour
number_of_spheres = 5 # Works quite good up til 10, but not much more, quite noisy even then.
# If you want to have user changable values, they need to be entered from the command line
	# so import sys sys and use sys.argv[0] etc
	# some_value = int(sys.argv[0])
if (len(sys.argv) == 2 or len(sys.argv) == 3) and sys.argv[1].isnumeric(): # Can be a float, so just go with numeric
	max_brightness = int(sys.argv[1], 10)
	if max_brightness > 254 or max_brightness < 10:
		print("Error with arguments, brightness not valid: "+str(sys.argv))
		usage()
		quit()

	if len(sys.argv) == 3 and sys.argv[2].isdigit(): #Can't be a float...
		number_of_spheres = int(sys.argv[2], 10)
		if number_of_spheres > 10 or number_of_spheres < 1:
			print("Error with arguments, number of spheres not valid: "+str(sys.argv))
			usage()
			quit()
else:
	if len(sys.argv) > 1: # And also since it's neither 2 nor 3 :)
		print("Error with arguments, unknown arguments: "+str(sys.argv))
		usage()
		quit()


def random3DValues(min_values, max_values, not_like_this = []):
	"""
	Create a random 3D values, min and max. 
	"""
	if type(min_values) == int or type(min_values) == float:
		min_values = [min_values,min_values,min_values]
	if type(max_values) == int or type(max_values) == float:
		max_values = [max_values,max_values,max_values]
	if hasattr(min_values, "__len__") and hasattr(max_values, "__len__") and (len(min_values) == len(max_values) == 3):
		index = 0
		new_values = []
		while index < len(min_values):
			diff = max_values[index]-min_values[index]
			# edge_limit_gauss_value = min_values[index]+diff*(random.gauss(1, 0.5)%1) 
			# new_values.append(edge_limit_gauss_value)

			new_values.append(random.randint(min_values[index],max_values[index]))

			# middle_gauss_value = min_values[index]+diff*(random.gauss(0.5, 0.5)%1) 
			# new_values.append(middle_gauss_value)
			if len(not_like_this) == 3 and abs(new_values[index] - not_like_this[index]) < diff*0.1:
				# invert colour strength.
				new_values[index] = min_values[index] + (new_values[index] + diff/2) % diff
			index += 1
		return new_values

def createRandomGRBColour(not_like_this=[]): # Now that I look at this right in the end, I don't know why I didn't just use random 3D values here also.
	"""
	Create a random GRB, with brightness between min and max. 
	"""
	index = 0
	new_colour = []
	brightness = 0
	while index < 3:
		new_colour.append(random.randint(0, max_brightness))
		if len(not_like_this) == 3 and abs(new_colour[index] - not_like_this[index]) < max_brightness*0.1:
			# invert colour strength.
			new_colour[index] = (new_colour[index] + max_brightness/2) % max_brightness
		brightness += new_colour[index]
		index += 1
	if brightness > max_brightness:
		index = 0
		while index < len(new_colour):
			new_colour[index] *= max_brightness/brightness
			index += 1
	if brightness < min_brightness:
		if brightness <= 0:
			new_colour[random.randint(0,2)] = random.randint(1, max_brightness)
		else:
			index = 0
			while index < len(new_colour):
				new_colour[index] *= min_brightness/brightness
				index += 1
	return new_colour


def addColours(colour1, colour2):
	"""
	Add colour 1 and colour 2 with a limit on brightness.
	"""
	if hasattr(colour1, "__len__") and hasattr(colour2, "__len__") and (len(colour1) == len(colour2)):
		index = 0
		new_colour = []
		brightness = 0
		while index < len(colour1):
			new_colour.append((colour1[index]*colour1[index] + colour2[index]*colour2[index]))
			brightness += new_colour[index]
			index += 1
		if brightness > max_brightness:
			index = 0
			while index < len(colour1):
				new_colour[index] *= max_brightness/brightness
				index += 1
		return new_colour


def fadeColours(currentColour, fadeToColour, fadePerCycle = 1.0):
	if hasattr(currentColour, "__len__"):
		new_colour = currentColour.copy()
		index = 0
		while index < len(currentColour):
			if currentColour[index] > fadeToColour[index]+fadePerCycle:
				new_colour[index] -= fadePerCycle
			else:
				if currentColour[index] < fadeToColour[index]-fadePerCycle:
					new_colour[index] += fadePerCycle
				else:
					new_colour[index] = fadeToColour[index]
			index += 1
		return new_colour


def vectorNorm(vector1, vector2 = [0,0,0]):
	if hasattr(vector1, "__len__") and hasattr(vector2, "__len__") and (len(vector1) == len(vector2)):
		norm = 0
		index = 0
		while index < len(vector1):
			norm += (vector1[index] - vector2[index])*(vector1[index] - vector2[index])
			index += 1
		# print(norm)
		return math.sqrt(norm)


def xmaslight():

	# NOTE THE LEDS ARE GRB COLOUR (NOT RGB)

	# Here are the libraries I am currently using:
	import time
	import board
	import neopixel
	import re

	# You are welcome to add any of these:
	# import numpy
	# import scipy
	# import sys
	
	# use simulator ( See https://github.com/DutChen18/xmastree2020 )
	# from sim import board
	# from sim import neopixel

	# IMPORT THE COORDINATES (please don't break this bit)
	coordfilename = "Python/coords.txt"

	fin = open(coordfilename, 'r')
	coords_raw = fin.readlines()

	coords_bits = [i.split(",") for i in coords_raw]

	coords = []
	pixel_colour = []
	
	for slab in coords_bits:
		new_coord = []
		for i in slab:
			new_coord.append(int(re.sub(r'[^-\d]', '', i)))
		coords.append(new_coord)
		new_colour = createRandomGRBColour()
		pixel_colour.append(new_colour.copy())

	max_coord = coords[0].copy()
	min_coord = coords[1].copy()
	for coord in coords:
		i = 0
		while i < len(coord):
			if coord[i] > max_coord[i]:
				max_coord[i] = coord[i]
			else:
				if coord[i] < min_coord[i]:
					min_coord[i] = coord[i]
			i += 1

	
	# set up the pixels (AKA 'LEDs')
	PIXEL_COUNT = len(coords)  # this should be 500

	pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)

	# YOU CAN EDIT FROM HERE DOWN

	# I get a list of the heights which is not overly useful here other than to set the max and min altitudes
	heights = []
	for i in coords:
		heights.append(i[2])

	min_alt = min(heights)
	max_alt = max(heights)
	max_size = abs(max_alt-min_alt)

	# VARIOUS SETTINGS

	# Step size in percentage
	standard_step_size = 7/max_size

	# If less than 2, not all lights will turn on.
	standard_wave_width = 3

	# pause between cycles (normally zero as it is already quite slow)
	slow = 0

	black = [0,0,0]
	number_of_spheres_to_use = 1
	index = 0
	sphere_colours = []
	sphere_rad_sizes = []
	sphere_coords = []
	sphere_step_size = []
	sphere_fade_modifier = []
	sphere_wave_width = []
	while index < number_of_spheres:
		sphere_colours.append( createRandomGRBColour() )
		sphere_rad_sizes.append( -index*max_size/number_of_spheres ) # First is 0, rest Negative sizes so it won't start straight away
		sphere_coords.append( random3DValues(min_coord, max_coord) )
		sphere_step_size.append(random.gauss(1,0.25)*standard_step_size)
		sphere_fade_modifier.append(random.gauss(1,0.25))
		sphere_wave_width.append(random.gauss(1,0.3)*standard_wave_width)
		index += 1

	cycles = 0

	# yes, I just run which run is... 1?
	run = True
	while run:

		time.sleep(slow)

		
		# Recalculate spheres
		index = 0
		while index < number_of_spheres_to_use:
			# For each sphere, recalc size and if size is too big, new colour and coord.
			sphere_rad_sizes[index] += max_size*sphere_step_size[index]
			if (sphere_rad_sizes[index] > max_size):
				sphere_rad_sizes[index] = -( 0.15*(random.random()+0.5)*(max_size)) # Negative sizes so it won't start straight away, and a bit random
				sphere_colours[index] = createRandomGRBColour(sphere_colours[(index+number_of_spheres_to_use-1)%number_of_spheres_to_use]) # Different from the previous
				sphere_coords[index] = random3DValues(min_coord,max_coord, sphere_coords[(index+number_of_spheres_to_use-1)%number_of_spheres_to_use])
				sphere_step_size[index] = random.gauss(1,0.25)*standard_step_size
				sphere_fade_modifier[index] = random.gauss(1,0.25)
				sphere_wave_width[index] = random.gauss(1,0.25)*standard_wave_width
				cycles += 1
			# sphere_colours[index] = fadeColours(sphere_colours[index],[255,255,255],5)

			LED = 0
			# For each sphere, recalc colours of each pixel
			while LED < len(coords):
				# If close to a growing sphere, add colour of the sphere ontop of existing colour
				norm = vectorNorm(coords[LED],sphere_coords[index])
				if sphere_rad_sizes[index]-norm < sphere_wave_width[index]*max_size*sphere_step_size[index] and sphere_rad_sizes[index]-norm > max_size*sphere_step_size[index]/sphere_wave_width[index]:
					pixel_colour[LED] = addColours(pixel_colour[LED],sphere_colours[index])
				# Else fade to black
				else:
					pixel_colour[LED] = fadeColours(pixel_colour[LED],black, sphere_fade_modifier[index]*number_of_spheres_to_use/2)

				LED += 1
			index += 1

		LED = 0
		# For each Pixel, finally set the pixel to it's colour.
		while LED < len(coords):
			
			pixels[LED] = [math.floor(pixel_colour[LED][0]),math.floor(pixel_colour[LED][1]), math.floor(pixel_colour[LED][2])]
			
			LED += 1
			
		# use the show() option as rarely as possible as it takes ages
		# do not use show() each time you change a LED but rather wait until you have changed them all
		pixels.show()

		#Once we shown all the spheres to use once, switch it up
		if cycles >= number_of_spheres_to_use:
			number_of_spheres_to_use = random.randint(1,number_of_spheres)
			cycles = 0

	return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
