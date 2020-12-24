from xmastrees import VirtualXmasTree, XmasTree
from spirolight import spirolight
from xmaslights import xmaslights


def run_lights():
    coord_filename = "Python/coords.txt"
    # tree = XmasTree(coord_filename)
    tree = VirtualXmasTree(coord_filename)
    spirolight(tree)
    # xmaslights(tree)


if __name__ == "__main__":
    run_lights()
