'''
This file contains
* MicroQiskit (https://github.com/qiskit-community/MicroQiskit/blob/master/README.md)
* `make_line` from QuantumBlur (https://github.com/qiskit-community/QuantumBlur/blob/master/README.md)
Both are licensed under Apache 2.0, copyright of IBM Research and written by James R. Wootton (@quantumjim)
Everything else here is under the same license as the rest of the repo.

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

# We also need MicroQiskit, a minimal version of the 'Qiskit' framework for quantum computing.
# Since external files aren't allowed, I'll just dump it here
# See https://github.com/qiskit-community/MicroQiskit/blob/master/README.md for more info
######## MicroQiskit starts here
import random
from math import cos,sin,pi

r2=0.70710678118 # 1/sqrt(2) will come in handy

class QuantumCircuit:
  
  def __init__(self,n,m=0):
    '''Defines and initializes the attributes'''
    # The number of qubits and the number of output bits are attributes of QuantumCircuit objects.
    self.num_qubits=n
    self.num_clbits=m
    # It is possible to set a name for a circuit
    self.name = ''
    # Like Qiskit, QuantumCircuit objects in MicroQiskit have a `data` attribute, which is essentially a list of gates.
    # The contents of this in MicroQiskit are tailored to the needs of the `simulate` function.
    self.data=[]
  
  def __add__(self,self2):
    '''Allows QuantumCircuit objects to be added, as in Qiskit.'''
    self3=QuantumCircuit(max(self.num_qubits,self2.num_qubits),max(self.num_clbits,self2.num_clbits))
    self3.data=self.data+self2.data
    self3.name = self.name
    return self3
  
  def initialize(self,k):
    '''Initializes the qubits in a given state.'''
    self.data[:] = [] # Clear existing gates.
    self.data.append(('init',[e for e in k])) # Add the instruction to initialize, including the required state.
  
  def x(self,q):
    '''Applies an x gate to the given qubit.'''
    self.data.append(('x',q))
  
  def rx(self,theta,q):
    '''Applies an rx gate to the given qubit by the given angle.'''
    self.data.append(('rx',theta,q))
  
  def h(self,q):
    '''Applies an h gate to the given qubit.'''
    self.data.append(('h',q))
  
  def cx(self,s,t):
    '''Applies a cx gate to the given source and target qubits.'''
    self.data.append(('cx',s,t))
  
  def crx(self,theta,s,t):
    '''Applies a crx gate to the given source and target qubits.'''
    self.data.append(('crx',theta,s,t))
  
  def measure(self,q,b):
    '''Applies an measure gate to the given qubit and bit.'''
    assert b<self.num_clbits, 'Index for output bit out of range.'
    assert q<self.num_qubits, 'Index for qubit out of range.'
    self.data.append(('m',q,b))
  
  def rz(self,theta,q):
    '''Applies an rz gate to the given qubit by the given angle.'''
    # This gate is constructed from `h` and `rx`.
    self.h(q)
    self.rx(theta,q)
    self.h(q)
  
  def ry(self,theta,q):
    '''Applies an ry gate to the given qubit by the given angle.'''
    # This gate is constructed from `rx` and `rz`.
    self.rx(pi/2,q)
    self.rz(theta,q)
    self.rx(-pi/2,q)
  
  def z(self,q):
    # This gate is constructed from `rz`.
    '''Applies a z gate to the given qubit.'''
    self.rz(pi,q)
  
  def y(self,q):
    '''Applies an y gate to the given qubit.'''
    # This gate is constructed from `rz` and `x`.
    self.rz(pi,q)
    self.x(q)


def simulate(qc,shots=1024,get='counts',noise_model=[]):
  '''Simulates the given circuit `qc`, and outputs the results in the form specified by `shots` and `get`.'''
  
  def superpose(x,y):
    '''For two elements of the statevector, x and y, return (x+y)/sqrt(2) and (x-y)/sqrt(2)'''
    return [r2*(x[j]+y[j])for j in range(2)],[r2*(x[j]-y[j])for j in range(2)]
  
  def turn(x,y,theta):
    '''For two elements of the statevector, x and y, return cos(theta/2)*x - i*sin(theta/2)*y and cos(theta/2)*y - i*sin(theta/2)*x'''
    theta = float(theta)
    return [x[0]*cos(theta/2)+y[1]*sin(theta/2),x[1]*cos(theta/2)-y[0]*sin(theta/2)],[y[0]*cos(theta/2)+x[1]*sin(theta/2),y[1]*cos(theta/2)-x[0]*sin(theta/2)]
  
  # Initialize a 2^n element statevector. Complex numbers are expressed as a list of two real numbers.
  k = [[0,0] for _ in range(2**qc.num_qubits)] # First with zeros everywhere.
  k[0] = [1.0,0.0] # Then a single 1 to create the all |0> state.

  # if there is a noise model, it should be a list of qc.num_qubits measurement error probabilities
  # if it is just a singe probability, turn it into such a list
  if noise_model:
    if type(noise_model)==float:
       noise_model = [noise_model]*qc.num_qubits

  # The `outputnum_clbitsap` dictionary keeps track of which qubits are read out to which output bits
  outputnum_clbitsap = {}

  # Now we go through the gates and apply them to the statevector.
  # Each gate is specified by a tuple, as defined in the QuantumCircuit class
  for gate in qc.data:
    
    if gate[0]=='init': # For initializion, copy in the given statevector.
      if type(gate[1][0])==list:
        k = [e for e in gate[1]]
      else: # This allows for simple lists of real numbers to be accepted as input.
        k = [[e,0] for e in gate[1]]
        
    elif gate[0]=='m': # For measurement, keep a record of which bit goes with which qubit.
      outputnum_clbitsap[gate[2]] = gate[1]
    
    elif gate[0] in ['x','h','rx']: # These are the only single qubit gates recognized by the simulator.
      
      j = gate[-1] # The qubit on which these gates act is the final element of the tuple.
  
      # These gates affect elements of the statevector in pairs.
      # These pairs are the elements whose corresponding bit strings differ only on bit `j`.
      # The following loops allow us to loop over all of these pairs.
      for i0 in range(2**j):
        for i1 in range(2**(qc.num_qubits-j-1)):
          b0=i0+2**(j+1)*i1 # Index corresponding to bit string for which the `j`th digit is '0'.
          b1=b0+2**j # Index corresponding to the same bit string except that the `j`th digit is '1'.
          if gate[0]=='x': # For x, just flip the values
            k[b0],k[b1]=k[b1],k[b0]
          elif gate[0]=='h': # For x, superpose them
            k[b0],k[b1]=superpose(k[b0],k[b1])
          else: # For rx, construct the superposition required for the given angle
            theta = gate[1]
            k[b0],k[b1]=turn(k[b0],k[b1],theta)
    
    elif gate[0] in ['cx','crx']: # These are the only two qubit gates recognized by the simulator.
      
      # Get the source and target qubits
      if gate[0]=='cx': 
        [s,t] = gate[1:]
      else:
        theta = gate[1]
        [s,t] = gate[2:]


      # Also get them sorted as highest and lowest
      [l,h] = sorted([s,t])
      
      # This gate only effects elements whose corresponding bit strings have a '1' on bit 's'.
      # Of those, it effects elements in pairs whose corresponding bit strings differ only on bit `t`.
      # The following loops allow us to loop over all of these pairs.
      for i0 in range(2**l):
        for i1 in range(2**(h-l-1)):
          for i2 in range(2**(qc.num_qubits-h-1)):
            b0=i0+2**(l+1)*i1+2**(h+1)*i2+2**s # Index corresponding to bit string for which digit `s` is `1` and digit `t` is '0'.
            b1=b0+2**t  # Index corresponding to the same bit string except that digit `t` is '1'.
            if gate[0]=='cx':
                k[b0],k[b1]=k[b1],k[b0] # Flip the values.
            else:
                k[b0],k[b1]=turn(k[b0],k[b1],theta) # Perform the rotation.
  
  # Now for the outputs.
    
  # For the statevector output, simply return the statevector.
  if get=='statevector':
    return k

  else:
        
    # To calculate outputs, we convert the statevector into a list of probabilities.
    # Here `probs[j]` is the probability for the output bit string to be the n bit representation of j.
    probs = [e[0]**2+e[1]**2 for e in k]
    
    # If there is a noise model, apply its effects
    if noise_model:
      for j in range(qc.num_qubits):
        p_meas = noise_model[j]
        for i0 in range(2**j):
          for i1 in range(2**(qc.num_qubits-j-1)):
            b0=i0+2**(j+1)*i1 # Index corresponding to bit string for which the `j`th digit is '0'.
            b1=b0+2**j # Index corresponding to the same bit string except that the `j`th digit is '1'.
            # change the probs to reproduce the effect of a measurement error
            p0 = probs[b0]
            p1 = probs[b1]
            probs[b0] = (1-p_meas)*p0 + p_meas*p1
            probs[b1] = (1-p_meas)*p1 + p_meas*p0
        
    # This can be output directly (as with Statevector or DensityMatrix in Qiskit
    if get=='probabilities_dict':
      # For each p=probs[j], the key is the n bit representation of j, and the value is p.
      return {('{0:0'+str(qc.num_qubits)+'b}').format(j):p for j,p in enumerate(probs)}
    # Otherwise, we need to sample
    elif get in ['counts', 'memory']:
      # When using these kinds of outputs in MicroQiskit, we demand that no gates are applied to a qubit after its measure command.
      # The following block raises an error if this is not obeyed.
      m = [False for _ in range(qc.num_qubits)]
      for gate in qc.data:
        for j in range(qc.num_qubits):
          assert  not ((gate[-1]==j) and m[j]), 'Incorrect or missing measure command.'
          m[j] = (gate==('m',j,j))
        
      # The `shots` samples that result are then collected in the list `m`.
      m=[]
      for _ in range(shots):
        cumu=0
        un=True
        r=random.random()
        for j,p in enumerate(probs):
          cumu += p
          if r<cumu and un:    
            # When the `j`th element is chosen, get the n bit representation of j.
            raw_out=('{0:0'+str(qc.num_qubits)+'b}').format(j)
            # Convert this into an m bit string, with the order specified by the measure commands
            out_list = ['0']*qc.num_clbits
            for bit in outputnum_clbitsap:
              out_list[qc.num_clbits-1-bit] = raw_out[qc.num_qubits-1-outputnum_clbitsap[bit]]
            out = ''.join(out_list)
            # Add this to the list of samples
            m.append(out)
            un=False
            
      # For the memory output, we simply return `m`
      if get=='memory':
        return m
      # For the counts output, we turn it into a counts dictionary first
      else:
        counts = {}
        for out in m:
          if out in counts:
            counts[out] += 1
          else:
            counts[out] = 1
        return counts  
######## MicroQiskit ends here

# We'll also use the `make_line` function from QuantumBlur
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
                qc.rx(theta[j],j)
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