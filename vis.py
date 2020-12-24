import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
import pickle as pkl
from sklearn.neighbors import NearestNeighbors

# Fixing random state for reproducibility
np.random.seed(42)
with open("coords.pkl", "rb") as fp:
    coords = pkl.load(fp)

color_map = [((x)%255/255, (y)%255/255, (z)%255/255) for x, y, z in coords]
state_map = np.round(np.random.random(size=len(color_map)))
n_neighbors = 8
nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm='ball_tree').fit(coords)
distances, indices = nbrs.kneighbors(coords)
with open("nns.txt", "w") as fp:
    fp.write("[")
    for i in indices:
        fp.write('[' + ','.join([str(x) for x in i]) + "],\n")
    fp.write("]")
flatten = lambda t: [item for sublist in t for item in sublist] # Helper function
lines = flatten([list(zip([idx for _ in range(n_neighbors)], indices[idx])) for idx in range(len(indices))]) # In case you want to visualize the lines (slow)
mavg_window = 20
change_history = np.random.random(size=mavg_window)
change_history[-1] = np.mean(state_map)
reset_threshold = 0.01

def transition_function(rule_num_or_name, states, neighbors):
    new_states = states
    if isinstance(rule_num_or_name, str):
        if rule_num_or_name == "conway":
            for idx, (state, neigh) in enumerate(zip(states, neighbors)):
                neigh_sum = sum([states[n] for n in neigh])
                if (state and (neigh_sum == 2 or neigh_sum == 3)) or (not state and neigh_sum == 3):
                    new_states[idx] = 1
                else:
                    new_states[idx] = 0
            return new_states
    elif isinstance(rule_num_or_name, int):
        # find rule
        raise NotImplementedError("Haven't written this yet.")


def update_colors(num, points):
    global color_map, state_map, nbrs, change_mavg
    state_map = transition_function("conway", state_map, indices)
    change_mavg = change_history[-1] * ((mavg_window-1)/mavg_window) + np.mean(state_map)
    change_history[:-1] = change_history[1:] # Pop left
    change_history[-1] = change_mavg
    change_threshold = np.std(change_history)
    print(change_threshold)
    if change_threshold < reset_threshold:
        state_map = np.round(np.random.random(size=len(color_map)))
    new_colors = [(0, 0, 0) if not state else color_map[idx] for idx, state in enumerate(state_map)]
    points.set_color(new_colors)
    points._facecolor3d = points.get_facecolor()
    points._edgecolor3d = points.get_edgecolor()
    return points

fig = plt.figure()
ax = p3.Axes3D(fig)

x, y, z = np.transpose(coords)
points = ax.scatter(x, y, z, c=color_map)

line_coords = [np.transpose([coords[line[0]], coords[line[1]]]) for line in lines]
#plotted_lines = [ax.plot(*lc) for lc in line_coords]

get_range = lambda l: [min(l), max(l)]
ax.set_xlim3d(get_range(x))
ax.set_ylim3d(get_range(y))
ax.set_zlim3d(get_range(z))
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Tree')

# Creating the Animation object
line_ani = animation.FuncAnimation(fig, update_colors, 300, fargs=(points, ),
                                   interval=50, blit=False)
# line_ani.save('conway.gif', writer='imagemagick', fps=30) # uncomment to save

plt.show()