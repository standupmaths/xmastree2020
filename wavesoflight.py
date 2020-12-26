import math
from random import randint


class Wave:
    def __init__(self, tree):
        self.radius = 0
        self.max_radius = 1000
        self.max_intensity = 100
        self.speed = 6
        self.source = randint(0, len(tree.coords))
        self.color = [randint(0, self.max_intensity), randint(0, self.max_intensity), randint(0, self.max_intensity)]

    def update(self, leds, tree):
        self.radius += self.speed
        # wave drawing
        for led in range(len(leds)):
            distance_from_source = math.dist(tree.coords[led], tree.coords[self.source])
            if self.radius - self.speed < distance_from_source <= self.radius:
                for i in range(3):
                    if leds[led][i] < self.color[i]:
                        leds[led][i] = self.color[i]


# function by pikuch
def wavesoflight(tree):
    """Draws waves of light starting at random points"""
    # list of waves
    waves = [Wave(tree)]
    # color persistance (1 = lasts forever)
    persistance = 0.99
    # time between waves
    wave_frequency = 60
    timer = wave_frequency
    # led colors
    leds = [[0, 0, 0]] * len(tree.coords)

    while True:
        timer -= 1
        if timer <= 0:
            timer = wave_frequency
            # create another wave
            waves.append(Wave(tree))

        for wave in waves:
            wave.update(leds, tree)

        # remove old waves
        to_remove = []
        for wave in waves:
            if wave.radius > wave.max_radius:
                to_remove.append(wave)
        for wave in to_remove:
            waves.remove(wave)

        # color dimming
        for led in range(len(tree.coords)):
            leds[led] = [leds[led][0] * persistance, leds[led][1] * persistance, leds[led][2] * persistance]

        # writing the new color data
        for led in range(len(tree.coords)):
            tree.set_led_RGB(led, [int(leds[led][0]), int(leds[led][1]), int(leds[led][2])])

        tree.display()
