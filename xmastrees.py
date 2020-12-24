from collections import namedtuple  # for Point data structure
import pygame  # for virtual tree visuals


class XmasTree:
    def __init__(self, coord_filename):

        import board
        import neopixel  # pip install rpi_ws281x adafruit-circuitpython-neopixel adafruit-blinka

        self.coords = self.read_coordinates(coord_filename)
        self.min_x = min(coord.x for coord in self.coords)
        self.max_x = max(coord.x for coord in self.coords)
        self.min_y = min(coord.y for coord in self.coords)
        self.max_y = max(coord.y for coord in self.coords)
        self.min_z = min(coord.z for coord in self.coords)
        self.max_z = max(coord.z for coord in self.coords)

        self.PIXEL_COUNT = len(self.coords)
        assert (self.PIXEL_COUNT == 500)
        self.pixels = neopixel.NeoPixel(board.D18, self.PIXEL_COUNT, auto_write=False)

    def read_coordinates(self, coord_filename):
        Point = namedtuple("Point", ["x", "y", "z"])  # so we can address point coordinates like humans
        with open(coord_filename, 'r') as fin:
            coords_raw = fin.readlines()
        return list(map(lambda line: Point(*map(lambda item: int(item.strip()), line[1:-2].split(","))), coords_raw))

    def display(self):
        self.pixels.show()

    def set_led_RGB(self, n, RGBcolor):
        self.pixels[n] = [RGBcolor[1], RGBcolor[0], RGBcolor[2]]


class VirtualXmasTree:
    def __init__(self, coord_filename):
        self.coords = self.read_coordinates(coord_filename)
        self.min_x = min(coord.x for coord in self.coords)
        self.max_x = max(coord.x for coord in self.coords)
        self.min_y = min(coord.y for coord in self.coords)
        self.max_y = max(coord.y for coord in self.coords)
        self.min_z = min(coord.z for coord in self.coords)
        self.max_z = max(coord.z for coord in self.coords)

        self.PIXEL_COUNT = len(self.coords)
        assert (self.PIXEL_COUNT == 500)
        self.pixels = [[0, 0, 0]] * self.PIXEL_COUNT

        self.tree_size = self.max_z - self.min_z
        self.max_light_size = 10
        self.min_light_size = 4
        self.margin = self.tree_size * 0.1
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 800, 800
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Virtual Xmas Tree")

    def read_coordinates(self, coord_filename):
        Point = namedtuple("Point", ["x", "y", "z"])  # so we can address point coordinates like humans
        with open(coord_filename, 'r') as fin:
            coords_raw = fin.readlines()
        return list(map(lambda line: Point(*map(lambda item: int(item.strip()), line[1:-2].split(","))), coords_raw))

    def display(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)

        self.screen.fill((10, 10, 10))  # background color

        for p in range(len(self.coords)):
            # x is depth, y is x and z is height
            screen_x = int(self.margin + self.WINDOW_WIDTH * ((self.coords[p].y - self.min_y) / self.tree_size))
            screen_y = int(self.WINDOW_HEIGHT - self.margin - self.WINDOW_HEIGHT * ((self.coords[p].z - self.min_z) / self.tree_size))
            on_screen_size = int(self.min_light_size + (self.coords[p].x - self.min_x) / (self.max_x - self.min_x) * (self.max_light_size - self.min_light_size))
            pygame.draw.circle(self.screen, self.pixels[p], (screen_x, screen_y), on_screen_size)

        pygame.display.flip()
        self.clock.tick(60)

    def set_led_RGB(self, n, RGBcolor):
        self.pixels[n] = RGBcolor
