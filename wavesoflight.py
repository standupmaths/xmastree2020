import math
from random import randint


# function by pikuch
def wavesoflight(tree):
    """Draws waves of light starting at random points"""
    # current wave radius
    radius = 0
    # maximum wave radius, after which it resets
    max_radius = 800
    # the speed at which the wave spreads
    wave_speed = 7
    # maximum intensity of any one colour channel
    max_intensity = 100
    # wave source (led index)
    source = randint(0, len(tree.coords))
    # led colors
    leds = [[0, 0, 0]] * len(tree.coords)
    # wave color
    color = [randint(0, max_intensity), randint(0, max_intensity), randint(0, max_intensity)]
    # color persistance (1 = stays forever, 0 = instantly off
    persistance = 0.98

    while True:
        if radius > max_radius:
            # create another wave
            radius = 0
            source = randint(0, len(tree.coords))
            color = [randint(0, max_intensity), randint(0, max_intensity), randint(0, max_intensity)]

        radius += wave_speed

        # wave drawing
        for led in range(len(tree.coords)):
            distance_from_source = math.dist(tree.coords[led], tree.coords[source])
            if radius - wave_speed <= distance_from_source <= radius:
                leds[led] = color

        # color dimming
        for led in range(len(tree.coords)):
            leds[led] = [leds[led][0] * persistance, leds[led][1] * persistance, leds[led][2] * persistance]

        # writing the new color data
        for led in range(len(tree.coords)):
            tree.set_led_RGB(led, [int(leds[led][0]), int(leds[led][1]), int(leds[led][2])])

        tree.display()
