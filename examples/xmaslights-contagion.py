def xmaslight():
    # This is the code from my 
    
    #NOTE THE LEDS ARE GRB COLOUR (NOT RGB)
    
    # Here are the libraries I am currently using:
    import time
    import board
    import neopixel
    import re
    import math
    
    # You are welcome to add any of these:
    import random
    # import numpy
    # import scipy
    # import sys
    
    # If you want to have user changable values, they need to be entered from the command line
    # so import sys sys and use sys.argv[0] etc
    # some_value = int(sys.argv[0])
    
    # IMPORT THE COORDINATES (please don't break this bit)
    
    coordfilename = "coords.txt"
	
    fin = open(coordfilename,'r')
    coords_raw = fin.readlines()
    
    coords_bits = [i.split(",") for i in coords_raw]
    
    coords = []
    
    for slab in coords_bits:
        new_coord = []
        for i in slab:
            new_coord.append(int(re.sub(r'[^-\d]','', i)))
        coords.append(new_coord)
    
    #set up the pixels (AKA 'LEDs')
    PIXEL_COUNT = len(coords) # this should be 500
    
    pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)
    
    
    # YOU CAN EDIT FROM HERE DOWN
    
    #maxes = [max(c[i] for c in coords) for i in range(0, 3)]
    #mins = [min(c[i] for c in coords) for i in range(0, 3)]

    # Construct a k-d tree to make finding nearby lights easier
    # Maybe overkill for only 500 lights but should avoid O(n^2) if more are added

    treeBuildOrder = random.sample(range(0, PIXEL_COUNT), k=PIXEL_COUNT)
    tree = []

    def addToTree(i):
        newNode = dict(i=i, left=-1, right=-1)
        newNodeIndex = len(tree)
        tree.append(newNode)
        if newNodeIndex > 0:
            nodeIndex = 0
            dim = 0
            while True:
                node = tree[nodeIndex]
                branch = "right" if coords[i][dim] > coords[node["i"]][dim] else "left"
                if node[branch] >= 0:
                    nodeIndex = node[branch]
                else:
                    node[branch] = newNodeIndex
                    return
                dim = (dim + 1) % 3

    def findWithinBox(minCoords, maxCoords):
        foundIndices = []
        def search(nodeIndex, dim):
            if nodeIndex >= 0:
                node = tree[nodeIndex]
                nodeCoords = coords[node["i"]]
                if all(nodeCoords[d] > minCoords[d] and nodeCoords[d] < maxCoords[d] for d in range(0, 3)):
                    foundIndices.append(node["i"])
                if nodeCoords[dim] > minCoords[dim]:
                    search(node["left"], (dim + 1) % 3)
                if nodeCoords[dim] < maxCoords[dim]:
                    search(node["right"], (dim + 1) % 3)
        search(0, 0)
        return foundIndices

    def norm2(p1, p2):
        return sum((p1[d] - p2[d]) * (p1[d] - p2[d]) for d in range(0, 3))

    def findWithinRadius(centre, radius):
        withinBox = findWithinBox([c - radius for c in centre], [c + radius for c in centre])
        return [i for i in withinBox if norm2(centre, coords[i]) < radius * radius]

    for i in treeBuildOrder:
        addToTree(i)

    def colourFade(c1, c2, fade):
        return [c1[c] * fade + c2[c] * (1 - fade) for c in range(0, 3)]

    # VARIOUS SETTINGS

    slow = 0

    maxInfectRadius = 80

    # probability of infection at zero distance
    maxInfectProb = 0.1
    # multiply by maxInfectProb to get probability of infection at distance maxInfectRadius
    infectProbMultiplierAtRadius = 0.5

    # how many iterations an infection last for (and can be passed on)
    infectionDuration = 5

    # how many iterations with no infections to wait before resetting
    inactivityIterationsBeforeReset = 10
    # how many iterations the reset transition lasts
    resetTransitionDuration = 40

    # colour for uninfected lights
    uninfectedColour = [10, 10, 10]
    # colour for infected lights is different each cycle, this number controls
    # the brightness (max 256)
    infectedColourBrightness = 150
    # colour for recovered lights is chosen by combining uninfected and infected colours using this weighting
    recoveredColourFade = 0.2

    # INITIALISATION

    colours = dict(uninfected=uninfectedColour)

    resetCountdown = inactivityIterationsBeforeReset
    infectionStatus = []

    def reset():
        infectionStatus.clear()
        infectionStatus.extend(("uninfected", 0) for _ in coords)
        infectionStatus[random.randrange(0, PIXEL_COUNT)] = ("infected", 1)
        # choose a new colour for infected lights
        g = random.randrange(0, infectedColourBrightness)
        r = random.randrange(0, infectedColourBrightness - g)
        b = infectedColourBrightness - g - r
        infectedColour = [g, r, b]
        colours["infected"] = infectedColour
        colours["recovered"] = colourFade(infectedColour, uninfectedColour, recoveredColourFade)

    # CONTAGION CALCULATIONS

    distanceFactor = (1 / infectProbMultiplierAtRadius) - 1
    def infectionProbability(p1, p2):
        return maxInfectProb / (1 + distanceFactor * (norm2(p1, p2) / (maxInfectRadius * maxInfectRadius)))

    def isSusceptible(i):
        (currentStatus, _) = infectionStatus[i]
        return currentStatus == "uninfected"

    # yes, I just run which run is true
    reset()

    run = 1
    while run == 1:
        
        time.sleep(slow)

        if resetCountdown <= -resetTransitionDuration:
            resetCountdown = inactivityIterationsBeforeReset
            reset()

        newInfections = []

        if resetCountdown <= 0:
            resetProb = -resetCountdown / resetTransitionDuration
            resetProb *= resetProb
            for i in range(0, PIXEL_COUNT):
                if random.random() < resetProb:
                    infectionStatus[i] = ("uninfected", 0)
                (currentStatus, _) = infectionStatus[i]
                pixels[i] = colours[currentStatus]
        else:
            for i in range(0, PIXEL_COUNT):
                (currentStatus, iterationsInfected) = infectionStatus[i]
                if currentStatus == "infected":
                    if iterationsInfected >= infectionDuration:
                        infectionStatus[i] = ("recovered", 0)
                    else:
                        infectionStatus[i] = ("infected", iterationsInfected + 1)
                        newInfections.extend(j for j in findWithinRadius(coords[i], maxInfectRadius) if isSusceptible(j) and random.random() < infectionProbability(coords[i], coords[j]))

            for j in newInfections:
                infectionStatus[j] = ("infected", 0)

            for i in range(0, PIXEL_COUNT):
                (currentStatus, _) = infectionStatus[i]
                pixels[i] = colours[currentStatus]

        if len(newInfections) > 0:
            resetCountdown = inactivityIterationsBeforeReset
        else:
            resetCountdown -= 1

        # use the show() option as rarely as possible as it takes ages
        # do not use show() each time you change a LED but rather wait until you have changed them all
        pixels.show()

    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
