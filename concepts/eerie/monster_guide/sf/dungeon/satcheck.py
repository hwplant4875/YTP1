"""Saturation budget + contrast probe for the dungeon plates.
usage: python3 satcheck.py <png> [x,y ...]   (probe points print colour and contrast vs cast colours)
budget: share of pixels with HSV S > 0.35 and V > 0.25 (plan 3-1: wide shots <= 15 %)."""
import sys
import numpy as np
from PIL import Image

def lum(rgb):
    c = np.asarray(rgb, dtype=float) / 255.0
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]

def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

im = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float) / 255.0
mx, mn = im.max(axis=2), im.min(axis=2)
S = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
sat = (S > 0.35) & (mx > 0.25)
print(f'{sys.argv[1]}: saturated pixels (S>0.35, V>0.25) = {sat.mean() * 100:.2f} %   mean V = {mx.mean():.3f}')
cast = {'wood #A0866B': (0xA0, 0x86, 0x6B), 'woodShade #7A6652': (0x7A, 0x66, 0x52), 'blazer #8E8699': (0x8E, 0x86, 0x99), 'knight #7A7E86': (0x7A, 0x7E, 0x86)}
for arg in sys.argv[2:]:
    x, y = map(int, arg.split(','))
    patch = (im[max(0, y - 6):y + 7, max(0, x - 6):x + 7] * 255).reshape(-1, 3).mean(axis=0)
    hexc = '#%02X%02X%02X' % tuple(int(round(v)) for v in patch)
    print(f'  ({x},{y}) {hexc}  ' + '  '.join(f'{k}: {contrast(v, patch):.2f}:1' for k, v in cast.items()))
