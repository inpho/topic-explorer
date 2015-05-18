import brewer2mpl as brewer

def brew(N, n_cls, reverse=True):
    b = [
        brewer.get_map('Blues', 'Sequential', N+1, reverse=reverse).hex_colors[:N],
        brewer.get_map('Oranges', 'Sequential', N+1, reverse=reverse).hex_colors[:N],
        brewer.get_map('Greens', 'Sequential', N+1, reverse=reverse).hex_colors[:N],
        brewer.get_map('Purples', 'Sequential', N+1, reverse=reverse).hex_colors[:N],
        brewer.get_map('Reds', 'Sequential', N+1, reverse=reverse).hex_colors[:N],
        brewer.get_map('Greys', 'Sequential', N+1, reverse=reverse).hex_colors[:N],
    ]
    return b[:n_cls]

# d3.category20c()
category20c = [
    ['#3182bd','#6baed6','#9ecae1','#c6dbef'],
    ['#e6550d','#fd8d3c','#fdae6b','#fdd0a2'],
    ['#31a354','#74c476','#a1d99b','#c7e9c0'],
    ['#756bb1','#9e9ac8','#bcbddc','#dadaeb'],
    ['#636363','#969696','#bdbdbd','#d9d9d9']
]
