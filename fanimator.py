# Stateless functional animator
# https://github.com/qt1/xmastree2020
# Written by baruch@ibn-labs.com
# Enjoy!

import sys
import time
import re
import math
from math import sin, cos, pi

# activate simulation if he "--sim" flag is set
if '--sim' in sys.argv:
    print("Simulation Mode - starting")
    from sim import board
    from sim import neopixel
else:
    print("The real tree shopuld light up now!")
    import board
    import neopixel


# utility functions for converting float 0..1 color components into [0..255] :

def clamp(v, low, hi):
    "clamp a value to limits "
    return [max(low, min(hi, x)) for x in v]


def clamp_scale(v, low, hi, scale):
    "clamp a value to limits "
    return [max(low, min(hi, x))*scale for x in v]


def clamp_scale_0_255(v):
    "clamp a value to [0..1] then scale to 0..255"
    return clamp_scale(v, 0, 1, 255)


# the animation loop
coords = []
pixels = {}

def init_xmaslight():
    global coords, pixels

    # This is the code from my

    # NOTE THE LEDS ARE GRB COLOUR (NOT RGB)

    # If you want to have user changable values, they need to be entered from the command line
    # so import sys sys and use sys.argv[0] etc
    # some_value = int(sys.argv[0])

    # IMPORT THE COORDINATES (please don't break this bit)

    coordfilename = "coords.txt"

    fin = open(coordfilename, 'r')
    coords_raw = fin.readlines()

    coords_bits = [i.split(",") for i in coords_raw]

    coords = []

    for slab in coords_bits:
        new_coord = []
        for i in slab:
            new_coord.append(int(re.sub(r'[^-\d]', '', i)))
        coords.append(new_coord)

    # set up the pixels (AKA 'LEDs')
    PIXEL_COUNT = len(coords)  # this should be 500

    pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)


def xmaslight(fx, duration=0, **kwargs):
    "run space+time animation function fx for a given duration (0=forever) "
    global coords, pixels

    # YOU CAN EDIT FROM HERE DOWN

    t0 = time.time()
    t = 0
    while duration <= 0 or duration >= t:
        t_now = time.time()-t0
        dt = t_now-t
        t = t_now
        # debug - print the interval between shows
        #print(f"dt {dt:.0f} ms")

        for LED in range(len(coords)):
            pixels[LED] = clamp_scale_0_255(fx(coords[LED] + [t], **kwargs)) # evaluate and scale

        pixels.show()


# Functions and arguments that make up animations
# all functions take a 4 dimension space+time coordinate and some additional optional named parameters


# the two colours in GRB order
# if you are turning a lot of them on at once, keep their brightness down please
colourA = [0, 50, 50]  # purple
colourB = [50, 50, 0]  # yellow

# wave plane vector moving both in time and in z
W = (0, 0, 0.005, 3)


# some helpfull utility functions

def inter(a, b, r):
    "interpolate vectors between a and b : (r-1)*a + r*b "
    return [r*b[i]+(1-r)*a[i] for i in range(min(len(a), len(b)))]


def vsum(a, b):
    "vector addition"  # could use numpy..
    return [a[i]+b[i] for i in range(min(len(a), len(b)))]


def vdiff(a, b):
    "vector difference b-a"
    return [b[i]-a[i] for i in range(min(len(a), len(b)))]


def mult(a, b):
    "element by element multiplication"
    return [a[i]+b[i] for i in range(min(len(a), len(b)))]


def dot(a, b):
    "dot product"
    s = 0
    for i in range(min(len(a), len(b))):
        s += a[i]*b[i]
    return s


def catesian_to_spherical(p):
    return [
        math.sqrt(p[0]*p[0] + p[1]*p[1] + p[2]*p[2]),
        math.atan2(p[1], p[0]),
        math.atan2(p[2], math.sqrt(p[0]*p[0]+p[1]*p[1])),
        p[3]  # preserve time coordinate
    ]


def catesian_to_cylindrical(p):
    return [
        math.sqrt(p[0]*p[0] + p[1]*p[1] + p[2]*p[2]),
        math.atan2(p[1], p[0]),
        p[2], # preserve z coordinate,
        p[3]  # preserve time coordinate
    ]

def u(x):
    "step function"
    return 1 if x>=0 else 0

def rot_ij(X,i,j,a):
    "Rotate on i,j coordinates by angle a"
    c = cos(a)
    s = sin(a)
    XX = [x for x in X] # make a copy
    XX[i] = c*X[i]+s*X[j]
    XX[j] = c*X[j]-s*X[i]
    return XX

def rot_xy(X,a):
    "Rotate on xy by angle a"
    return rot_ij(X,0,1,a)

def rot_xz(X,a):
    "Rotate on xz by angle a"
    return rot_ij(X,0,2,a)

def rot_yz(X,a):
    "Rotate on yz by angle a"
    return rot_ij(X,1,2,a)


##################  functions mapping X=[x,y,x,t] to color  #############

def u_of_x(X, c0=[0, 0, 0], c1=[1, 1, 0], **kwargs):
    "Step function on x"
    return c1 if 0<=x else c0


def blink(X, c0=[0, 0, 0], c1=[1, 1, 1], **kwargs):
    "The simplest animation - on-off as a function of time"
    t = X[3]  # time component of space+time
    return c1 if t % 2 > 1 else c0


def sin_t(X, c0=[0, 1, 0], c1=[1, 0, 1], **kwargs):
    "Interpolate between two colors as sine of t  - soft blink"
    t = X[3]
    ohmega = 2*pi
    return inter(c0, c1, 0.5 * 0.5*sin(ohmega * t))

def sin_x(X, W=(0, 0, 0, 2), p0=0, c0=[0, 0, 0], c1=[1, 1, 1], **kwargs):
    "sine wave - in arbitrary space+time coordinates"
    p = dot(X, W) + p0    # phase (starting with phase 0)
    return inter(c0, c1, 0.5+0.5*sin(p))


def planar_wave(X, W=(0, 0, -0.01, 2), f1d=lambda p: 0.5+0.5*sin(p), p0=0, c0=[0, 0, 0], c1=[1, 1, 1], **kwargs):
    "A planar wave modulated by a 1d function f1d"
    p = dot(X, W) + p0    # phase (starting with phase 0)
    return inter(c0, c1, f1d(p))


def planar_wave_multicolor(X, W=(0, 0, -0.01, 2), f1d=lambda p: 0.5+0.5*sin(p), p0=0, colors=[[0, 0, 0], [0, 1, 0], [0, 0, 0], [0, 0, 1]], **kwargs):
    "A planar wave modulated by a 1d function f1d, the scalar value is used to interpolate from colors"
    p = dot(X, W) + p0    # phase (starting with phase 0)
    s = f1d(p)            # scalar value
    n = len(colors)       # number of colors in color map
    c0 = colors[math.floor(s) % n]
    c1 = colors[(math.floor(s)+1) % n]
    r = s - math.floor(s)  # fraction for interpolation
    return inter(c0, c1, r)


def multicolor(X, f=lambda X: u(X[0]), colors=[[0, 0, 0], [0, 1, 0], [0, 0, 0], [0, 0, 1]], **kwargs):
    """
    map the value of a salr returned by f(X) to the color map
    this is a general function that can replace some of the functions above, but it seems more readable to start with less general examples
    """
    s = f(X)             # scalar value
    n = len(colors)      # number of colors in color map
    c0 = colors[math.floor(s) % n]
    c1 = colors[(math.floor(s)+1) % n]
    r = s - math.floor(s)  # fraction for interpolation
    return inter(c0, c1, r)


c = 299792458  # [m/s]


def gravitational_time_dilation(X, z0=-6378000, g=10, **kwargs):
    """
    approximation when gh << c^2
    z0 is the z coordinate of the center of mass (origin is the tip of the tree, z pointing down)
    g is the acceleration
    """
    global c
    h = X[2]-z0
    td = 1+g*h/c/c
    return [X[0], X[1], X[2], X[3]*td]


def coord_transformer(X, T, ff, **kwargs):
    "Chain - apply a function f on coordinates transformed by function T"
    XX = T(X, **kwargs)
    return ff(XX, **kwargs)


def add_f(fA, fB, **kwargs):
    "Combination - addition of two animations"
    return fA(**kwargs) + fB(**kwargs)


def mult_f(fA, fB, **kwargs):
    "Combination - multiplication of two animations"
    return fA(**kwargs) * fB(**kwargs)


########################## Calling Rendering  #########################
# yes, I just put this at the bottom so it auto runs

#first we init..
init_xmaslight()

print("blink")
xmaslight(blink, duration=7)


print("blink with different colors")
xmaslight(blink, duration=5, c0=colourA, c1=colourB)


print("Soft blink with sin(wt) (negative is black)")
xmaslight(sin_t, c0=[0, 0, 0], c1=[1, 1, 0], duration=7)


print("sine of dot(X , W)" )
xmaslight(sin_x, W=W, c0=colourA, duration=5)


print("sine of [x,y,z,t] using a general planar wave function")
xmaslight(planar_wave, W=(0, 0.01, -0.01, 4), c0=colourA, c1=colourB, duration=15)


print("Using a general function to do a selection of colors on x")
xmaslight(multicolor, f=lambda X:u(X[0]), colors=[[0.5,1,0],[1,0,5,1]], duration=7)


print("u(x+sin(t))")
xmaslight(multicolor, f=lambda X:u(X[0]-200*sin(X[3]*4)), colors=[[0.5,1,0],[1,0,5,1]], duration=10)


print("some rotation around y ")
xmaslight(multicolor, f=lambda X:u(rot_xz(X,3*X[3])[0]), colors=[[0.5,1,0],[1,0,5,1]], duration=15)


print("a linear wave interpolated with multiple colors")
xmaslight(planar_wave_multicolor, f1d=lambda x: x,
          W=(0, 0.01, 0.01, 4),                                       # direction of wavefront
          colors=[[1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1], [1, 0, 1]],   # color map
          duration=25)


print("A square wave on spherical coordinates using coordinate transformer")
xmaslight(coord_transformer,
          T=lambda X, TC, a=0, **kwargs: catesian_to_spherical(vdiff(TC, [X[0], X[1], X[2], X[3] + a*X[3]*X[3]])),
          ff=planar_wave,
          f1d=lambda p: sin(p)*4,
          TC=[0, 0, -150, 0],  # center
          W=(-0.008, 0, 0, 5), c0=[0, 0, 1], c1=[1, 1, 0.4],
          a = 0.08, # acceleration
          duration=20)


print("A cylindrical, sharp cutoff, 4 color wave - cylindrical coordinates")
xmaslight(coord_transformer,
          T=lambda X, TC, **kwargs: catesian_to_cylindrical(vdiff(TC, X)),
          ff=planar_wave_multicolor,
          f1d=lambda x: math.floor(x),
          TC=[0, 0, -150, 0],  # center
          W=(0.0, 2/pi, 0, 5),
          colors=[[0, 0, 0], [0, 1, 0], [0, 0, 0], [0, 0, 1]],
          duration=10)


print("A cylindrical, with time dilation, will spiral with time")
xmaslight(
    lambda X, **kwargs:
        planar_wave_multicolor(
            X=catesian_to_cylindrical( gravitational_time_dilation(X, **kwargs)), **kwargs),
    f1d=lambda x: math.floor(x),
    TC=[0, 0, -150, 0],  # center
    W=(0.0, 2/pi, 0, 1),
    colors=[[0, 0, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0]],
    z0= -3000, g = 5*c*c*1e-5, # bigger tree on a more massive planet
    duration=40)


print("Blink with time dilation, time is moving slightly faster at the top. Slowly evolves.")
xmaslight(
    lambda X, **kwargs:
        blink(
            X=catesian_to_cylindrical( gravitational_time_dilation(X, **kwargs)), **kwargs),
    z0= -3000, g = 5*c*c*1e-5, # bigger tree on a more massive planet
    duration=0)


