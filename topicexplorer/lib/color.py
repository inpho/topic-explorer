from collections import defaultdict
import itertools

import brewer2mpl as brewer
import networkx as nx
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
    k = v.model.K
    mat = v.doc_topic_matrix(v.labels)

    rs = defaultdict(list)
    ss = np.zeros([len(mat), k, 2])
    adj = np.zeros([k, k])
    thresh = 0.1
    cs = 0

    # for each row add values to horizontal neighbors
    for row_num, row in enumerate(mat):
        order = row.argsort()[::-1]
        vals = np.cumsum(row[order])
        vals = np.insert(vals, 0, 0.)
        ranges = [np.array([vals[v], vals[v + 1]])
                  for v in range(len(vals) - 1) if (vals[v + 1] - vals[v]) > thresh]
        # add horizontal overlap
        for i, o in enumerate(order):
            ss[row_num][o][0] = vals[i]
            ss[row_num][o][1] = vals[i + 1]

        vals = np.delete(vals, 0)

        # successors
        for i, key, val in zip(range(k - 1), order[:-1], order[1:]):
            v = vals[i + 1] - vals[i]
            if v > thresh:
                adj[key][val] += 1
                cs += 1
        # predecessors
        for i, key, val in zip(range(1, k), order[1:], order[:-1]):
            v = vals[i] - vals[i - 1]
            if v > thresh:
                adj[key][val] += 1
                cs += 1
        # ranges
        for key, val in zip(order[:len(ranges)], ranges):
            rs[key].append(val)

    # for each entry within threshold, go through each and find overlapping topics.
    idxs = ss[:, :, 1] - ss[:, :, 0] > thresh
    cse = 0
    for row, topic in zip(*np.where(idxs)):
        # print ss[row, topic]
        # aggregate number of rows with overlap per topic
        # look for points that start or end within the same space, or span
        idxs2 = np.logical_not(np.logical_or(
            ss[:, :, 1] <= ss[row, topic, 0], ss[:, :, 0] >= ss[row, topic, 1]))
        candidates = np.logical_and(idxs, idxs2)
        for row_, topic2 in zip(*np.where(candidates)):
            v = min(ss[row][topic][1], ss[row_][topic2][1]) - \
                max(ss[row_][topic2][0], ss[row][topic][0])
            # print v > thresh, v, min(ss[row][topic][1] ,ss[row_][topic2][1]), '\t',
            # max(ss[row_][topic2][0], ss[row][topic][0])

            if v > thresh and row != row_:
                adj[topic][topic2] += min(1.0, v / mat[row][topic]) * 0.001
                # if v / mat[row][topic] > 0.5:
                #    print row, topic, v, mat[row][topic], mat[row_][topic2], v / mat[row][topic]
                cse += min(1.0, v / mat[row][topic]) * 0.001

    # build base graph
    G = nx.Graph()
    for i in range(k):
        G.add_node(i)

    # initialize base variables
    weight = int((cs + cse) / (4 * k * k))
    ncolors = None

    while ncolors is None or ncolors > 9:
        print weight, ncolors
        # clean previous color assignments and edges
        colors = defaultdict(int)
        G.remove_edges_from(G.edges())
        for e1, e2 in zip(*np.where(adj > weight)):
            G.add_edge(e1, e2, weight=adj[e1, e2])

        # assign colors
        for n in sorted(G.nodes(), key=G.degree, reverse=True):
            neighbor_colors = [colors[nbr] for nbr in G.neighbors(n)]
            # print colors[n], neighbor_colors
            colorgram = np.histogram(colors.values(), bins=range(max(colors.values()) + 2))
            available_colors = [c for c in colors.values() if c not in neighbor_colors]
            # print available_colors
            # try:
            if available_colors:
                colors[n] = min(available_colors, key=lambda i: colorgram[0][i])
            else:
                colors[n] = max(colors.values()) + 1
                # except ValueError:
                #    colors[n] = max(colors.values()) + 1

        ncolors = len(set(colors.values()))
        print ncolors

        weight += 1

    bmap = brewer.get_map('Set1', 'Qualitative', ncolors)

    topic_colors = [(n, bmap.mpl_colormap(color / float(ncolors - 1)))
                    for n, color in colors.iteritems()]

    topic_colors.sort(key=lambda x: x[0])
    return topic_colors
    # TODO: add bmap -> rgba format


def get_topic_colors(v):
    ncolors = 8
    bmap = brewer.get_map('Set1', 'Qualitative', ncolors)

    topic_colors = [(n, bmap.mpl_colormap(float(n % ncolors) / (ncolors - 1)))
                    for n in range(v.model.K)]

    topic_colors.sort(key=lambda x: x[0])
    return topic_colors
