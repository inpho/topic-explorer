import numpy as np
from matplotlib import colormaps
from matplotlib.colors import to_hex


def _sequential(name, N, reverse=True):
    """Sample the ColorBrewer ramp ``name`` at N evenly spaced points."""
    cmap = colormaps[name]
    if reverse:
        cmap = cmap.reversed()
    return [to_hex(cmap(i)) for i in np.linspace(0, 1, N + 1)][:N]


def brew(N, n_cls, reverse=True):
    b = [_sequential(name, N, reverse=reverse)
         for name in ('Blues', 'Oranges', 'Greens', 'Purples', 'Reds', 'Greys')]
    return b[:n_cls]

# d3.category20c()
category20c = [
    ['#3182bd', '#6baed6', '#9ecae1', '#c6dbef'],
    ['#e6550d', '#fd8d3c', '#fdae6b', '#fdd0a2'],
    ['#31a354', '#74c476', '#a1d99b', '#c7e9c0'],
    ['#756bb1', '#9e9ac8', '#bcbddc', '#dadaeb'],
    ['#636363', '#969696', '#bdbdbd', '#d9d9d9']
]


def rgb2hex(rgb):
    'Given an rgb or rgba sequence of 0-1 floats, return the hex string'
    a = '#%02x%02x%02x' % tuple([int(np.round(val * 255)) for val in rgb[:3]])
    return a

def get_topic_colors(v):
    ncolors = 8
    dark2 = colormaps['Dark2']

    topic_colors = [(n, dark2((n % ncolors) / (ncolors - 1)))
                    for n in range(v.model.K)]

    topic_colors.sort(key=lambda x: x[0])
    return topic_colors
