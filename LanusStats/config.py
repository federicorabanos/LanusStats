import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
}

colors_bordo_to_white = [
    '#6f1b28',
    '#83202f',
    '#942435',
    '#a0273a',
    '#a8293d',
    '#b92d42',
    '#cd324a',
    '#d34a60',
    '#ffadad',
    '#ffb8b8',
    '#ffd1d1',
    '#ffe0e0',
    '#fff5f5',
    '#FFFFFF'
]

colors_bordo_to_white.reverse()

granate_blanco_cmap = LinearSegmentedColormap.from_list('bordo_to_white', colors_bordo_to_white, N=50)
mpl.colormaps.register(name='granate_blanco', cmap=granate_blanco_cmap)

colors = [
    '#d0d6d4',
    '#c5d0cd',
    '#bbcac7',
    '#b0c3c1',
    '#a6bdbb',
    '#9bb7b5',
    '#91b1af',
    '#86aaa8',
    '#7ca4a2',
    '#719e9c',
    '#679896',
    '#5c9190',
    '#528b8a',
    '#478583',
    '#3d7f7d',
    '#327877',
    '#287271',
]
soc_cm = LinearSegmentedColormap.from_list('colors', colors, N=50)
mpl.colormaps.register(name='SOC', cmap=soc_cm)