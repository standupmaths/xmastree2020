import math
from os import fork
import random
import sys




# if you are turning a lot of them on at once, keep their brightness down please
default_max_brightness = 100
max_brightness = default_max_brightness
min_max_brightness = 10
max_max_brightness = 254
# Min brightness for creating a new colour
min_brightness = math.floor(max_brightness*0.8)
# Works quite good up til 10, but not much more, quite noisy even then.
default_number_of_forks = 5
number_of_forks = default_number_of_forks
min_number_of_forks = 2
max_number_of_forks = 15

default_speed = 5
speed = default_speed
min_speed = 1
max_speed = 10

black = [0,0,0]

def usage():
	print(sys.argv[0] + " maximum_brightness(Default "+str(default_max_brightness)+", Range "+str(min_max_brightness)+"-"+str(max_max_brightness)+") maximum_number_of_forks(Default "+str(default_number_of_forks)+", Range "+str(min_number_of_forks)+"-"+str(max_number_of_forks)+") speed(Default "+str(default_speed)+", Range "+str(min_speed)+"-"+str(max_speed)+")")
# If you want to have user changable values, they need to be entered from the command line
	# so import sys sys and use sys.argv[0] etc
	# some_value = int(sys.argv[0])
# Can be a float, so just go with numeric
if (len(sys.argv) > 1 and len(sys.argv) < 5) and sys.argv[1].isnumeric():
	max_brightness = float(sys.argv[1])
	if max_brightness > max_max_brightness or max_brightness < min_max_brightness:
		print("Error with arguments, brightness not valid: "+str(sys.argv))
		usage()
		quit()

	if len(sys.argv) >= 3 and sys.argv[2].isdigit():  # Can't be a float...
		number_of_forks = int(sys.argv[2], 10)
		if number_of_forks > max_number_of_forks or number_of_forks < min_number_of_forks:
			print("Error with arguments, number of forks not valid: "+str(sys.argv))
			usage()
			quit()
	if len(sys.argv) >= 4 and sys.argv[3].isnumeric():
		speed = float(sys.argv[3])
		print(str(speed))
		if speed > max_speed or speed < min_speed:
			print("Error with arguments, speed not valid: "+str(sys.argv))
			usage()
			quit()
else:
	if len(sys.argv) > 1:  # And also since it's neither 2 nor 3 :)
		print("Error with arguments, unknown arguments: "+str(sys.argv))
		usage()
		quit()


def random3DValues(min_values, max_values, not_like_this=[]):
	"""
	Create a random 3D values, min and max.
	"""
	if type(min_values) == int or type(min_values) == float:
		min_values = [min_values, min_values, min_values]
	if type(max_values) == int or type(max_values) == float:
		max_values = [max_values, max_values, max_values]
	if hasattr(min_values, "__len__") and hasattr(max_values, "__len__") and (len(min_values) == len(max_values) == 3):
		index = 0
		new_values = []
		while index < len(min_values):
			diff = max_values[index]-min_values[index]
			# edge_limit_gauss_value = min_values[index]+diff*(random.gauss(1, 0.5)%1)
			# new_values.append(edge_limit_gauss_value)

			new_values.append(random.randint(min_values[index], max_values[index]))

			# middle_gauss_value = min_values[index]+diff*(random.gauss(0.5, 0.5)%1)
			# new_values.append(middle_gauss_value)
			if len(not_like_this) == 3 and abs(new_values[index] - not_like_this[index]) < diff*0.1:
				# invert colour strength.
				new_values[index] = min_values[index] + (new_values[index] + diff/2) % diff
			index += 1
		return new_values


# Now that I look at this right in the end, I don't know why I didn't just use random 3D values here also.
def createRandomGRBColour(not_like_this=[]):
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
			new_colour[random.randint(0, 2)] = random.randint(1, max_brightness)
		else:
			index = 0
			while index < len(new_colour):
				new_colour[index] *= min_brightness/brightness
				index += 1
	return new_colour


def addColours(colour1, colour2, percentageOnSecond = 100):
	"""
	Add colour 1 and colour 2 with a limit on brightness.
	"""
	if hasattr(colour1, "__len__") and hasattr(colour2, "__len__") and (len(colour1) == len(colour2)):
		index = 0
		new_colour = []
		brightness = 0
		while index < len(colour1):
			new_colour.append( (colour1[index]*colour1[index] + colour2[index]*colour2[index]*percentageOnSecond/100) )
			brightness += new_colour[index]
			index += 1
		if brightness > max_brightness:
			index = 0
			while index < len(colour1):
				new_colour[index] *= max_brightness/brightness
				index += 1
		return new_colour


def fadeColours(currentColour, fadeToColour, fadePerCycle=1.0):
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
	# coordfilename = "coords.txt"

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
	min_coord = coords[0].copy()

	# Didnt work? max_width = vectorNorm([min_coord[0], min_coord[1]], [max_coord[0], max_coord[1]]) # max width coordinates on the xy plane

	#Each fork will have a different starting point to spread them a bit more
	top_coord_indicies = [0]

	index = 0
	while index < len(coords):
		coord = coords[index]
		if coord[2] > coords[top_coord_indicies[len(top_coord_indicies)-1]][2]:
			top_coord_indicies.insert(0,index)
			if (len(top_coord_indicies) >= max_number_of_forks):
				top_coord_indicies.pop();
		i = 0
		while i < len(coord):
			if coord[i] > max_coord[i]:
				max_coord[i] = coord[i]
			else:
				if coord[i] < min_coord[i]:
					min_coord[i] = coord[i]
			i += 1
		index+=1

	
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
	standard_step_size = PIXEL_COUNT*speed**1.8/300
	standard_fade_time = PIXEL_COUNT*speed**0.5/5000
	max_search_radius = max_size/(number_of_forks)

	# If less than 2, not all lights will turn on.
	# standard_wave_width = 3

	# pause between cycles (normally zero as it is already quite slow)
	slow = 0

	number_of_forks_to_use = number_of_forks
	fork_colours = []
	fork_search_sizes = []
	fork_coords_indices = []
	fork_step_size = []
	fork_fade_modifier = []
	# fork_wave_width = []
	index = 0
	while index < number_of_forks:
		fork_colours.append( createRandomGRBColour() )
		fork_search_sizes.append( -index*(random.random()+0.5)*(standard_step_size)) # First is 0, rest Negative sizes so it won't start straight away
		fork_coords_indices.append([top_coord_indicies[index]])
		fork_step_size.append(random.gauss(1,0.25)*standard_step_size)
		fork_fade_modifier.append(random.gauss(1,0.25)*standard_fade_time)
		# fork_wave_width.append(random.gauss(1,0.3)*standard_wave_width)
		index += 1

	cycles = 0

	# yes, I just run which run is... 1?
	run = 1
	while run:

		run += 1
		time.sleep(slow)
		
		max_search_radius = max_size/math.sqrt(number_of_forks_to_use)
		# print(str(fork_coords_indices[0]))
		# Recalculate forks
		index = 0
		while index < number_of_forks_to_use:
			
			# For each fork, recalc size and if there is no close neighbour below, new colour etc, and start over.
			fork_search_sizes[index] += fork_step_size[index]
			if fork_search_sizes[index] > max_search_radius:
				# if len(fork_coords_indices[index]) > 1:
				# 	pass
				fork_search_sizes[index] = -( (random.random()+0.5)*(standard_step_size)) # Negative sizes so it won't start straight away, and a bit random
				fork_colours[index] = createRandomGRBColour(fork_colours[(index+number_of_forks_to_use-1)%number_of_forks_to_use]) # Different from the previous
				i = 0
				while i < len(fork_coords_indices[index]):
					if fork_coords_indices[index][i] == top_coord_indicies[index]:
						fork_coords_indices[index].pop()
					else:
						i += 1
				fork_coords_indices[index].append(top_coord_indicies[index])
				pixel_colour[top_coord_indicies[index]] = addColours(pixel_colour[top_coord_indicies[index]],fork_colours[index])
				fork_step_size[index] = random.gauss(1,0.25)*standard_step_size
				fork_fade_modifier[index] = random.gauss(1,0.25)*number_of_forks_to_use*standard_fade_time
				# fork_wave_width[index] = random.gauss(1,0.25)*standard_wave_width
				cycles += 1
			# fork_colours[index] = fadeColours(fork_colours[index],[255,255,255],5)
			
			last_jump_index = fork_coords_indices[index][len(fork_coords_indices[index])-1]

			# For all the fork, fade to black
			LED = 0
			while LED < len(fork_coords_indices[index]):
				pixel_colour[fork_coords_indices[index][LED]] = fadeColours(pixel_colour[fork_coords_indices[index][LED]],black, fork_fade_modifier[index])
				# If almost black, pop (remove).
				if vectorNorm(pixel_colour[fork_coords_indices[index][LED]]) < 1:# or vectorNorm(pixel_colour[fork_coords_indices[index][LED]]) > vectorNorm(pixel_colour[last_jump_index]):
					fork_coords_indices[index].pop(LED)
				LED += 1

			LED = 0
			# For each fork, find the closest neighbours below current recalc colours of each pixel
			list_of_neighbour_indices = []
			while LED < len(coords):
				# If is below
				if coords[LED][2] < coords[last_jump_index][2] and LED != last_jump_index:
					norm = vectorNorm(coords[LED],coords[last_jump_index])
					if norm < fork_search_sizes[index]:
						list_of_neighbour_indices.append(LED)
						# print("Adding color:" + str(fork_colours[index]) + " with 15% on " + str(pixel_colour[LED]) )
						pixel_colour[LED] = addColours(pixel_colour[LED],fork_colours[index],5)
						# print("And got: "+ str(pixel_colour[LED]))
						fork_coords_indices[index].append(LED)

				LED += 1
			if len(list_of_neighbour_indices) > 10*min_number_of_forks/(number_of_forks_to_use*speed):
				while len(list_of_neighbour_indices) > 1:
					# Get the current color of the first 2 and divide by height to get not a semisphere norm, but a
					norm1 = vectorNorm(pixel_colour[list_of_neighbour_indices[0]])/(coords[list_of_neighbour_indices[0]][2]-min_coord[2]+1)
					norm2 = vectorNorm(pixel_colour[list_of_neighbour_indices[1]])/(coords[list_of_neighbour_indices[1]][2]-min_coord[2]+1)
					if norm1 == norm2 :
						list_of_neighbour_indices.pop(random.randint(0,1)) # Randomly pop
					else:
						pixel_colour[list_of_neighbour_indices[norm1 < norm2]] = addColours(pixel_colour[list_of_neighbour_indices[norm1 < norm2]],fork_colours[index]) # Relight it
						list_of_neighbour_indices.pop(norm1 < norm2) # But pop it. Will be faded anyway.

				# If part of a growing fork, add colour of the fork ontop of existing colour
				fork_search_sizes[index] = -( (random.random()+0.5)*(standard_step_size)) # Negative sizes so it won't start straight away, and a bit random
				pixel_colour[list_of_neighbour_indices[0]] = addColours(pixel_colour[list_of_neighbour_indices[0]],fork_colours[index])
				fork_coords_indices[index].remove(list_of_neighbour_indices[0]) # Remove from previous add
				fork_coords_indices[index].append(list_of_neighbour_indices[0]) # Add again to be last.
			else:
				neighbours = 0
				while neighbours < len(list_of_neighbour_indices):
					fork_coords_indices[index].remove(list_of_neighbour_indices[neighbours]) #Otherwise they will be added next cycle again and will be multiple.
					neighbours += 1
			
			LED = 0
			# For each fork, finally set the pixel to it's colour.
			while LED < len(fork_coords_indices[index]):
				
				pixels[fork_coords_indices[index][LED]] = [math.floor(pixel_colour[fork_coords_indices[index][LED]][0]),math.floor(pixel_colour[fork_coords_indices[index][LED]][1]), math.floor(pixel_colour[fork_coords_indices[index][LED]][2])]
				
				LED += 1
			index += 1

			
		# use the show() option as rarely as possible as it takes ages
		# do not use show() each time you change a LED but rather wait until you have changed them all
		pixels.show()

		# Once we shown all the forks to use once, switch it up
		if cycles >= number_of_forks_to_use:
			number_of_forks_to_use = random.randint(min_number_of_forks,number_of_forks)
			cycles = 0

	return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
