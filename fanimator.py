# Stateless functional animator
# https://github.com/qt1/xmastree2020
# Written by baruch@ibn-labs.com
# Enjoy!

import time
from sim import board
from sim import neopixel
import re
import math
from math import sin, pi

# some utility functions:


def clamp(v, low, hi):
    "clamp a value to limits "
    return [max(low, min(hi, x)) for x in v]


def clamp_scale(v, low, hi, scale):
    "clamp a value to limits "
    return [max(low, min(hi, x))*scale for x in v]


def clamp_scale_0_255(v):
    "clamp a value to [0..1] then scale to 0..255"
    return clamp_scale(v, 0, 1, 255)


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

# the animation loop


def xmaslight(f, duration=0, **kwargs):
    "run space+time animation function f for a given duration (0=forever) "
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

    # YOU CAN EDIT FROM HERE DOWN

    t0 = time.time()
    t = 0
    while duration <= 0 or duration >= t:
        t_now = time.time()-t0
        dt = t_now-t
        t = t_now
        # debug - print the interval between shows
        print(f"dt {dt:.0f} ms")

        for LED in range(len(coords)):
            # pixels[LED] = clamp01([sin(t), sin(t), sin(t)])
            pixels[LED] = clamp_scale_0_255(f(coords[LED] + [t], **kwargs))

        pixels.show()


# Functions and arguments that make up animations
# all functions take a 4 dimension space+time coordinate and some additional optional named parameters


# the two colours in GRB order
# if you are turning a lot of them on at once, keep their brightness down please
colourA = [0, 50, 50]  # purple
colourB = [50, 50, 0]  # yellow

# wave plane vector moving both in time and in z
W = (0, 0, 0.01, 2)


def blink(X, c0=[0, 0, 0], c1=[1, 1, 1], **kwargs):
    "The simplest animation - on-off as a function of time"
    t = X[3]  # time component of space+time 
    return c1 if t % 2 > 1 else c0


def sin_t(X, c0=[0, 0, 0], c1=[1, 1, 1], **kwargs):
    "Fade by a sine. Note that negative values are clamped to c0 (black)"
    t = X[3]
    r = sin(t)
    return inter(c0, c1, r)


def sin_x(X, W=(0, 0, 0, 2), p0=0, c0=[0, 0, 0], c1=[1, 1, 1], **kwargs):
    "sine wave - in arbitrary space+time coordinates"
    p = dot(X, W) + p0    # phase (starting with phase 0)
    return inter(c0, c1, 0.5+0.5*sin(p))


def planar_wave(X, W=(0, 0, -0.01, 2), f1d=lambda p: 0.5+0.5*sin(p), p0=0, c0=[0, 0, 0], c1=[1, 1, 1], **kwargs):
    "A planar wave modulated by a 1d function f1d"
    p = dot(X, W) + p0    # phase (starting with phase 0)
    return inter(c0, c1, f1d(p))


def planar_wave_multicolor(X, W=(0, 0, -0.01, 2), f1d=lambda p: 0.5+0.5*sin(p), p0=0, colors=[[0, 0, 0], [0, 1, 0], [0,0,0], [0, 0, 1]], **kwargs):
    "  A planar wave modulated by a 1d function f1d, the scalar value is used to interpolate from colors"
    p = dot(X, W) + p0    # phase (starting with phase 0)
    s = f1d(p)            # scalar value
    n = len(colors)       # number of colors in color map
    c0 = colors[math.floor(s) % n]
    c1 = colors[(math.floor(s)+1) % n]
    r = s - math.floor(s) # fraction for interpolation
    return inter(c0, c1, r)

def coord_transformer(X, T, ff, **kwargs):
    "Chain - apply a function f on coordinates transformed by function T"
    XX = T(X, **kwargs)
    return ff(XX, **kwargs)


def add_f(fA, fB, **kwargs):
    "Combunation - addition of two animations"
    return fA(**kwargs) + fB(**kwargs)


def mult_f(fA, fB, **kwargs):
    "Combunation - multiplication of two animations"
    return fA(**kwargs) * fB(**kwargs)


# yes, I just put this at the bottom so it auto runs
print("blink")
xmaslight(blink, duration=10)

print("blink with different colors")
xmaslight(blink, duration=7, c0=colourA, c1=colourB)

print("Soft blink with sin(wt) (negative is black)")
xmaslight(sin_t, c0=[0, 0, 0], c1=[1, 1, 0], duration=10)

print("sine of [x,y,z,t]")
xmaslight(sin_x, W=W, c0=colourA, duration=15)

print("sine of [x,y,z,t] using a general plannar wave function")
xmaslight(planar_wave, W=(0, 0.01, 0.01, 4), c0=colourB, duration=15)

print("a linear wave interpolated with multiple colors")
xmaslight(planar_wave_multicolor, f1d=lambda x:x, W=(0, 0.01, 0.01, 4), colors=[[1,0,0],[1,1,0],[0,1,0],[0,1,1],[0,0,1],[1,0,1]], duration=25)

print("A square wave on spherical coordinates using coordinates transformer")
xmaslight(coord_transformer,
          T=lambda X, TC, **kwargs: catesian_to_spherical(vdiff(TC,X)),  
          ff=planar_wave,
          f1d=lambda p: sin(p)*4,
          TC=[0,0, -150, 0], # center
          W=(-0.008, 0, 0, 5), c0=[0,0,0], c1=[1,1,0.4], 
          duration=15)

print("A cylindrical sharp cutoff 4 color wave - spherical coordinates using coordinates transformer")
xmaslight(coord_transformer,
          T=lambda X, TC, **kwargs: catesian_to_spherical(vdiff(TC,X)),  
          ff=planar_wave_multicolor,
          f1d=lambda x: math.floor(x),
          TC=[0,0, -150, 0], # center
          W=(0.0, 2/pi, 0, 5), 
          colors=[[0,0,0], [0,1,0], [0,0,0], [0,0,1]],
          duration=0)
