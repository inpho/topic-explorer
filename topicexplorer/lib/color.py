from __future__ import division
from __future__ import print_function
from builtins import zip
from builtins import range

from collections import defaultdict
import itertools

import brewer2mpl as brewer
import numpy as np


def brew(N, n_cls, reverse=True):
    b = [
        brewer.get_map('Blues', 'Sequential', N + 1, reverse=reverse).hex_colors[:N],
        brewer.get_map('Oranges', 'Sequential', N + 1, reverse=reverse).hex_colors[:N],
        brewer.get_map('Greens', 'Sequential', N + 1, reverse=reverse).hex_colors[:N],
        brewer.get_map('Purples', 'Sequential', N + 1, reverse=reverse).hex_colors[:N],
        brewer.get_map('Reds', 'Sequential', N + 1, reverse=reverse).hex_colors[:N],
        brewer.get_map('Greys', 'Sequential', N + 1, reverse=reverse).hex_colors[:N],
    ]
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
    bmap = brewer.get_map('Dark2', 'Qualitative', ncolors)

    topic_colors = [(n, bmap.mpl_colormap((n % ncolors) / (ncolors - 1)))
                    for n in range(v.model.K)]

    topic_colors.sort(key=lambda x: x[0])
    return topic_colors
