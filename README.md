# xmastree2020 - Conway's Game of Life

Top level script is [xmaslights-cellular-automata.py](https://github.com/kevroy314/xmastree2020/blob/main/xmaslights-cellular-automata.py)

This implementation involves the following 3 steps (plus some initialization):

0. Initialize a color map (spatial modulus, in this case), random states, and a random "history" used for deciding when to stop
1. Comptue the K Nearest Neighbors (n=8, by default) for each LED on the christmas tree, define this as the "neighborhood" for each LED

The result looks like this:

![lines.png](https://github.com/kevroy314/xmastree2020/blob/main/lines.png?raw=true)

2. Run [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) rules over the states of the LEDs using the neighborhood from (1)
3. Compute the exponentially weighted moving average for a window of mean of the LED states and take its standard deviation - if it exceeds a threshold, reinitalize

The result looks like this (sped up substantially):

![conway.gif](https://github.com/kevroy314/xmastree2020/blob/main/conway.gif?raw=true)
