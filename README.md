# xmastree2020
My 500 LED xmas tree

treeshow.py - runs the program

xmastrees.py - contains XmasTree (for running the hardware version) and VirtualXmasTree (for on-screen emulation)


user patterns taking a tree as an argument:

* xmaslights - original function (two colors spinning around a moving point)
* spirolight - draws three color waves (RGB) going around the tree at different speeds
* wavesoflight - draws waves of light starting at random points

Xmastree objects are initiated with a path to the file containing led coordinates and they let you set the led color using the set_led_RGB(led_id, RGBcolor) method and update the whole tree using the display() method.
