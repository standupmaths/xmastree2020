import math


# function by pikuch
def spirolight(tree):
    """Draws three color waves (RGB) going around the tree at different speeds"""
    # starting angle for each color channel (in radians)
    angles = [0.0] * 3
    # how quickly the color waves go around the tree
    delta_angles = [1/5, 1/7, 1/9]
    # maximum intensity of any one colour channel
    max_intensity = 100

    while True:
        for led in range(len(tree.coords)):
            rotation = math.atan2(tree.coords[led].y, tree.coords[led].x)
            colour = [max_intensity * (math.sin(angles[0] + rotation) + 1) / 2,
                      max_intensity * (math.sin(angles[1] + rotation) + 1) / 2,
                      max_intensity * (math.sin(angles[2] + rotation) + 1) / 2]
            tree.set_led_RGB(led, colour)

        tree.display()

        # update angles
        for i in range(len(angles)):
            angles[i] = math.fmod(angles[i] + delta_angles[i], 2 * math.pi)
