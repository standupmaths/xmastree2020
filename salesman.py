import time
import math


# I used this class to simulate the neopixel board, since I do not have
# a customizable christmas tree... yet.
class BoardSimulator(list):
    def show(self):
        print(self)


# The order for the Traveling Salesman path. Computing it takes a while
# so I'm hardcoding the solution instead.
_ORDER = [462, 460, 459, 461, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 480, 479, 478, 477, 476, 481, 482, 483, 484, 485, 486, 456, 457, 458, 455, 454, 452, 453, 451, 450, 432, 431, 430, 429, 428, 447, 427, 425, 426, 424, 422, 423, 421, 420, 419, 399, 418, 400, 401, 402, 403, 404, 405, 406, 407, 408, 410, 409, 411, 412, 414, 413, 222, 415, 416, 417, 398, 397, 396, 395, 394, 393, 392, 391, 354, 355, 356, 357, 358, 359, 360, 383, 367, 361, 362, 368, 369, 370, 371, 372, 375, 373, 374, 376, 377, 366, 379, 364, 378, 365, 380, 363, 382, 381, 385, 384, 386, 387, 388, 389, 390, 351, 352, 353, 348, 350, 347, 344, 342, 343, 341, 340, 339, 345, 349, 338, 346, 337, 336, 334, 335, 331, 329, 330, 328, 327, 326, 324, 325, 323, 322, 321, 441, 440, 442, 499, 497, 498, 496, 495, 492, 494, 493, 491, 488, 489, 487, 490, 449, 448, 446, 444, 445, 443, 320, 319, 316, 315, 311, 310, 309, 312, 307, 308, 306, 305, 304, 303, 302, 62, 63, 61, 67, 301, 68, 69, 70, 296, 299, 298, 297, 294, 295, 72, 71, 66, 300, 65, 64, 60, 59, 52, 56, 57, 58, 53, 51, 50, 0, 54, 1, 55, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 12, 118, 117, 208, 108, 207, 206, 205, 203, 209, 107, 106, 105, 104, 97, 102, 99, 251, 100, 101, 98, 96, 95, 94, 93, 92, 91, 90, 290, 293, 289, 291, 292, 73, 288, 74, 287, 87, 88, 89, 84, 83, 82, 81, 103, 80, 79, 78, 76, 77, 75, 85, 86, 286, 284, 283, 313, 285, 314, 282, 281, 280, 318, 317, 277, 279, 278, 276, 275, 265, 274, 267, 273, 272, 270, 433, 434, 271, 436, 435, 437, 438, 439, 269, 268, 266, 264, 263, 262, 258, 250, 260, 256, 261, 257, 254, 255, 253, 252, 248, 249, 247, 246, 245, 244, 243, 242, 241, 240, 239, 238, 237, 230, 229, 228, 227, 226, 225, 224, 223, 221, 220, 219, 218, 217, 235, 233, 231, 236, 232, 234, 216, 215, 259, 214, 213, 212, 211, 210, 204, 202, 201, 200, 194, 195, 193, 192, 190, 189, 188, 186, 187, 185, 180, 181, 182, 184, 196, 199, 198, 179, 197, 183, 178, 177, 176, 175, 174, 173, 172, 171, 170, 168, 130, 133, 140, 139, 138, 137, 167, 132, 136, 131, 135, 169, 129, 134, 128, 127, 126, 125, 124, 123, 122, 121, 120, 191, 119, 116, 109, 115, 13, 15, 16, 17, 18, 19, 111, 110, 113, 114, 20, 112, 21, 22, 150, 147, 148, 149, 146, 145, 144, 152, 154, 155, 156, 153, 157, 158, 159, 161, 142, 165, 164, 166, 163, 162, 160, 143, 141, 151, 24, 23, 25, 26, 27, 28, 29, 30, 32, 33, 31, 34, 35, 36, 37, 38, 40, 39, 41, 42, 333, 332, 44, 43, 45, 46, 47, 48, 49]


if __name__ == "__main__":
    try:
        import neopixel
        pixels = neopixel.NeoPixel(board.D18, len(_ORDER), auto_write=False)
    except ImportError:
        print("Failed to import neopixel. Creating a simulated set of pixels.")
        input("Press Enter to continue in this debug mode.")
        pixels = BoardSimulator(range(len(_ORDER)))

    # You mentioned the bulbs are too bright if they are set to 255, so this
    # number configures the max brightness of each RGB value. Change this
    # value to make them all brighter or dimmer.
    _max_shade = 50

    _white = [255, 255, 255]

    # Casting to float in case you run this on Python 2
    _max_shade_scaled = float(_max_shade) / (len(_ORDER) - 1)

    while True:

        # First we turn off all the lights
        for i in _ORDER:
            pixels[i] = [0, 0, 0]
        pixels.show()

        # Prepare the salesman (or Santa)
        pixels[_ORDER[0]] = _white
        pixels.show()
        time.sleep(1)

        for i, (previous, current) in enumerate(zip(_ORDER, _ORDER[1:])):
            
            # Not sure how long pixels.show() takes, putting the delay here just in case.
            # With 500 bulbs and 0.1 second delay this loop should take about a minute
            # to complete with pixels.show().
            time.sleep(0.1)

            pixels[previous] = [
                math.trunc(_max_shade_scaled * i),
                math.trunc(_max_shade - _max_shade_scaled * i),
                0
            ]
            pixels[current] = _white
            pixels.show()

        time.sleep(3)
