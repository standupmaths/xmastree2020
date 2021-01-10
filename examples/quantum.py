'''
This file is written by James R. Wootton (@quantumjim).

=== Dependencies ===

To run this file you'll need MicroQiskit. This is a minimal version of the 'Qiskit' framework for quantum computing.
It just needs you to download the microqiskit.py from the following link
https://github.com/qiskit-community/MicroQiskit/blob/master/microqiskit.py
and then put it somewhere importable (such as in the same folder as this file).

=== Inputs ===

Two optional inputs can be supplied when running the file.
The first is a 1 or 0, to determine whether to implement a quantum interference pattern or just use random bit flips.
The second is the maxmimum pixel brightness. By default, quantum is on and the max brightness is 128.

==== Summary of the Method ====

Quantum computers output bit strings, so to control the lights with a (simulation of) a quantum computer,
we need to assign a bit string to each light. For 500 lights we'll use 9 bits (since that allows 512)

Now imagine a graph for which each vertex is labelled by a bit string, and vertices are connected by an
edge if their bit strings differ on only a single bit. This is a graph on which a random walk can be
implemented simply by randomly choosing and flipping one of the bits.

Unfortunately, this graph is a 9-dimensional hypercube and not a Christmas tree. Nethertheless, we can
try to assign bit strings to the lights on the tree such that those for neighbouring lights differ on as
few bits as possible.
Once we've done this, we can implement an approximation of a random walk on the tree by implementing a
random walk on the hypercube, simply by randomly choosing and flipping a bit. That's what this program
will do if `quantum=False`, but it's not really what this program is about. After all, there are easier
and better ways a random walk could be run on the tree.

Instead we implement a continuous quantum analogue of a random walk, a simple form of so-called 'quantum walk'.
There are multiple forms of quantum walk that people have looked at, for multiple different reasons. The one
we use is the one that requires the least resources to to simulate. I won't go on about it here. See
https://github.com/qiskit-community/Quantumblur
if you are interested. The important point is that it naturally runs on a hypercube, which is why we need to do
hypercube stuff.

The method to project the hypercube onto a Christmas tree is fairly simple, but it seems to work okay.
First we sort the points by height into32 bins, and then sort the 16 elements in each bin by radius.
This gives a nice pair of coordinates to convert into binary, which should preserve some degree of locality.
'''

# First get user supplied parameters
import  sys
if len(sys.argv)>1:
    quantum = sys.argv[1]=='1'
else:
    quantum = True
if len(sys.argv)>2:
    max_brightness = int(sys.argv[2])
else:
    max_brightness = 128

# Now let's import everything we need
import time
try:
    import board
    import neopixel
except: # use a simulator when the actual hardware is not present
    from sim import board
    from sim import neopixel
import re
import math
from microqiskit import *

# We'll also use a `make_line` function which does the same job as the one from QuantumBlur
# see https://github.com/qiskit-community/QuantumBlur/blob/master/README.md for more info
def make_line ( length ):
    # number of bits required
    n = int(math.ceil(math.log(length)/math.log(2)))
    # iteratively build list
    line = ['0','1']
    for j in range(n-1):
        # first append a reverse-ordered version of the current list
        line = line + line[::-1]
        # then add a '0' onto the end of all bit strings in the first half
        for j in range(int(float(len(line))/2)):
            line[j] += '0'
        # and a '1' for the second half
        for j in range(int(float(len(line))/2),int(len(line))):
            line[j] += '1'     
    return line


# Before we finally get on with actually doing something, we need to take the coordinates for the lights from Matt's file
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

# And also set up the pixels (AKA 'LEDs')
PIXEL_COUNT = len(coords) # this should be 500
pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)


# Finally we can get on with making a Christmas tree effect with some quantum simulations!

# the following magic numbers define the quadrant boundaries
# they were found semi manually, and split the points evenly
theta0 = [-math.pi/2+0.39,0+0.07,math.pi/2+0.025]
x0,y0 = -21,-26
# with this, we create four lists of points, one for each quadrant
quadrants = [[] for _ in range(4)]
for x,y,z in coords:
    theta = math.atan2(y-y0,x-x0)
    q = (theta>theta0[0]) + (theta>theta0[1]) + (theta>theta0[2])
    quadrants[q].append((x,y,z))
    
# we'll sort the 125 coords of each quadrant into 16 bins with a max of 8 items each
bin_size = 8
bin_num = 16
bins = [[[] for _ in range(bin_num)] for _ in range(4)]

for q,quadrant in enumerate(quadrants):
    
    # for each coordinate, get the height and radius
    radii = {}
    heights = {}
    for x,y,z in quadrant:
        radii[x,y,z] = math.sqrt(x**2+y**2)
        heights[x,y,z] = z
    
    # first we sort by height
    for j,coord in enumerate(sorted(heights, key=heights.get)):
        bins[q][int(j/bin_size)].append(coord)

    # then the bins are sorted by radius
    for b in range(bin_num):

        bin_radii = {}
        for coord in bins[q][b]:
            bin_radii[coord] = radii[coord]

        new_bin = []
        for coord in sorted(bin_radii, key=bin_radii.get):
            new_bin.append(coord)

        bins[q][b] = new_bin
        
# now we make lists of bit strings in which neighbouring strings have a Hamming distance of 1

# for the four quadrants we need the four strings of 2 bits
# quadrant 1 neighbours 0 and 2, so its string should differ from theirs by one bit
# we do that by assigning 01 to quarant 1, 00 to quadrant 0 and 11 to quadrant 1
# this also works for all the other sets of neighbours
quadrants_line = ['00','01','11','10']

# a similar list of bit strings will be used to assign bit strings to bins, and other for entries in bins
# we'll use `make_line` to generate these for us
bins_line = make_line(bin_num)
bin_line = make_line(bin_size)

# with these we assign a bit string to each coord
bit_strings = {}
for q in range(4):
    for b in range(bin_num):
         for j,coord in enumerate(bins[q][b]):
                bit_strings[quadrants_line[q] + bins_line[b] + bin_line[j]] = coord
           
        
# Now we are all set up, we can twinkle some Christmas lights!
def xmaslight():

    # Here's where we do the quantum stuff!
    # We'll create an entangled GHZ state on 9 qubits and then loop continually add single qubit rotations to the circuit.
    # After each set of rotations, the quantum circuit is run and probabilities for each output string are extracted.
    # These probabilities are used to set the brightness the corresponding lights.

    # initialize 9 qubits in a GHZ state
    n = 9
    qc = QuantumCircuit(n)
    qc.h(0)
    for j in range(n-1):
        qc.cx(j,j+1)

    # pick random rotation angles for each run
    theta = [random.random()*math.pi/32 for _ in range(n)] 

    # iterate through the process of addin rotations
    run = 1
    while run == 1:

        # get current state vector
        ket = simulate(qc,get='statevector')
        # reinitialize circuit with that (to prevent circuits getting long)
        ket = simulate(qc,get='statevector')
        qc = QuantumCircuit(n)
        qc.initialize(ket)
        
        if quantum:
            # add rotations for each qubit (with the random angles)
            for j in range(n):
                qc.ry(theta[j],j)
        else:
            # just do a random bit flip
            j = random.choice(range(n))
            qc.x(j)

        # get probs for each output bit string
        probs = simulate(qc,get='probabilities_dict')

        # use probs to assign a brightness to each light
        max_prob = max(probs.values())
        colour = {}
        for bit_string,coord in bit_strings.items():
            c = int(probs[bit_string]*max_brightness/max_prob)
            colour[coord] = (0,c,c)

        # update all the pixels
        for j,coord in enumerate(coords):
            pixels[j] = colour[tuple(coord)]
        pixels.show()
        
        
xmaslight()