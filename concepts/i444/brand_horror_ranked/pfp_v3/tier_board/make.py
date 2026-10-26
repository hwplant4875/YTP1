import os; HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # pfp_v3/ (base.py, render.js)
import sys; sys.path.insert(0, HERE); from base import *
import math
D = HERE + '/tier_board/'

# v2: zoomed-in avatar crop of the tier board. Slaughtered row fills the circle, a cream skull tile is slammed into it
# (8 deg tilt, hard shadow), thick red-core fractures run out from under all four edges, one into the red label block.

CELL = '#2A2A26'      # lightened TierMaker cell so the circle keeps its edge on dark YouTube
GAPC = '#0B0B0A'      # row gaps / board seams
HOT = '#FF2A36'       # bright red fracture core
SEAM = '#0A0A0A'      # dark fracture lip
RIMC = '#3A0D11'      # blood-maroon inner rim: holds the edge on white and on dark YouTube

# original skull in a 100x100 box: ink mass on the tile, holes in tile colour
SKULL = ('M50 7 C25 7 9 23 9 45 C9 57 14 64 21 68 L23 79 C23 85 27 89 33 89 L67 89 C73 89 77 85 77 79 L79 68 '
         'C86 64 91 57 91 45 C91 23 75 7 50 7 Z')
EYE_L = 'M18.5 43 C19.5 35 31 34 45.5 42 C47.5 52.5 42.5 60.5 33 60.5 C24 60.5 17.5 52.5 18.5 43 Z'
EYE_R = 'M81.5 43 C80.5 35 69 34 54.5 42 C52.5 52.5 57.5 60.5 67 60.5 C76 60.5 82.5 52.5 81.5 43 Z'
NOSE = 'M50 60 L44 71 Q50 74 56 71 Z'
NOTCH = 'M57 4 L63 22.5 L71 5 Z'                       # cleaver chop into the crown
SK_CRACK = [(63, 17), (59.2, 28), (64.6, 32.4), (60.6, 41)]   # from the chop down into the right socket
CHIP = 'M43.9 77 L54.1 77 L54.1 91 L43.9 91 Z M54 91 L54 86.2 L60 82.6 L60 91 Z'   # knocked-out tooth + a snapped one


def tapered(pts, w0, w1=0.0):
    """polygon around a polyline, width w0 at the start tapering to w1 at the end"""
    L = len(pts); left = []; right = []
    for i, (x, y) in enumerate(pts):
        if i == 0: dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == L - 1: dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else: dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        m = math.hypot(dx, dy) or 1; nx, ny = -dy / m, dx / m
        w = (w0 + (w1 - w0) * i / (L - 1)) / 2
        left.append((x + nx * w, y + ny * w)); right.append((x - nx * w, y - ny * w))
    return ' '.join(f'{x:.1f},{y:.1f}' for x, y in left + right[::-1])


def fracture(pts, w0, core=.5, lip=SEAM, hot=HOT):
    return (f'<polygon points="{tapered(pts, w0)}" fill="{lip}"/>'
            f'<polygon points="{tapered(pts[:-1] + [pts[-1]], w0 * core)}" fill="{hot}"/>')


def skull(cx, cy, s, ink=INK):
    """holes are cut with a mask so the tile's own shading shows through the sockets, chop, crack and teeth"""
    k = s / 100
    teeth = ''.join(f'<rect x="{x - 2.1}" y="78" width="4.2" height="13" fill="#000"/>' for x in (38, 46, 54, 62))
    holes = (f'<path d="{EYE_L}"/><path d="{EYE_R}"/><path d="{NOSE}"/>{teeth}<path d="{CHIP}"/><path d="{NOTCH}"/>'
             f'<polygon points="{tapered(SK_CRACK, 7, 1.4)}"/>')
    return (f'<g transform="translate({cx - 50 * k:.1f} {cy - 50 * k:.1f}) scale({k:.4f})">'
            f'<mask id="skm"><rect x="-10" y="-10" width="120" height="120" fill="#fff"/><g fill="#000">{holes}</g></mask>'
            f'<path d="{SKULL}" fill="{ink}" mask="url(#skm)"/>'
            f'<polygon points="{tapered(SK_CRACK, 3.4, 0)}" fill="{HOT}"/></g>')


def build(LW=185, G=12, rows=((-40, 700), (712, 850), (862, 1040)), tx=548, ty=440, tile=490, rot=8,
          sh=(22, 30), sh_op=.8, rim=True, glow=True, crack_w=1.25):
    b = [f'<rect width="1000" height="1000" fill="{PAGE}"/><g clip-path="url(#av)"><rect width="1000" height="1000" fill="{GAPC}"/>']
    for i, (y0, y1) in enumerate(rows):
        b.append(f'<rect x="-10" y="{y0}" width="{LW + 10}" height="{y1 - y0 - G}" fill="{TM[i]}"/>')
        b.append(f'<rect x="{LW + G}" y="{y0}" width="{1010 - LW - G}" height="{y1 - y0 - G}" fill="{CELL}"/>')
    if glow:  # hot red bloom in the Slaughtered cell around the impact
        y0, y1 = rows[0]
        b.append(f'<rect x="{LW + G}" y="{y0}" width="{1010 - LW - G}" height="{y1 - y0 - G}" fill="url(#bloom)"/>')
    # fractures, defined in tile space (u right, v down, origin = tile centre) and rotated with the tile
    s2 = tile / 2; a = math.radians(rot); ca, sa = math.cos(a), math.sin(a)
    T = lambda u, v: (tx + u * ca - v * sa, ty + u * sa + v * ca)
    W = 60 * crack_w
    F = [  # right edge
        ([(s2 - 30, -70), (s2 + 55, -105), (s2 + 105, -62), (s2 + 190, -96), (s2 + 275, -70)], W),
        ([(s2 - 30, 60), (s2 + 70, 82), (s2 + 120, 146), (s2 + 215, 162)], W * .85),
        # top edge
        ([(-30, -s2 + 30), (-62, -s2 - 55), (-18, -s2 - 112), (-52, -s2 - 205)], W * .85),
        ([(110, -s2 + 30), (140, -s2 - 45), (215, -s2 - 78)], W * .55),
        # left edge, through the gap into the red label block
        ([(-s2 + 30, 25), (-s2 - 55, 2), (-s2 - 110, 48), (-s2 - 190, 28), (-s2 - 285, 62)], W * .9),
        # bottom edge, down through the row gap into Almost Dead
        ([(40, s2 - 30), (78, s2 + 48), (40, s2 + 115), (88, s2 + 190), (66, s2 + 270)], W * .9),
        ([(-130, s2 - 30), (-160, s2 + 40), (-232, s2 + 70), (-268, s2 + 120)], W * .6),
    ]
    for pts, w in F: b.append(fracture([T(u, v) for u, v in pts], w))
    b.append(f'<g transform="rotate({rot} {tx} {ty})">'
             f'<rect x="{tx - s2 + 4}" y="{ty - s2 + 10}" width="{tile}" height="{tile}" fill="#000" opacity=".55" filter="url(#soft)"/>'
             f'<rect x="{tx - s2 + sh[0]}" y="{ty - s2 + sh[1]}" width="{tile + 6}" height="{tile + 6}" fill="#000" opacity="{sh_op}"/>'
             f'<rect x="{tx - s2}" y="{ty - s2}" width="{tile}" height="{tile}" fill="url(#tileg)" stroke="#C9BEAA" stroke-width="3"/>'
             f'{skull(tx, ty + 8, tile * .93)}</g>')
    b.append('</g>')
    if rim:
        b.append(f'<circle cx="500" cy="500" r="490" fill="none" stroke="{RIMC}" stroke-opacity=".9" stroke-width="20"/>')
    defs = ('<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="16"/></filter>'
            '<clipPath id="av"><circle cx="500" cy="500" r="500"/></clipPath>'
            f'<radialGradient id="tileg" cx=".5" cy=".42" r=".75"><stop offset="0" stop-color="#FBF8F1"/>'
            f'<stop offset=".7" stop-color="{CREAM}"/><stop offset="1" stop-color="#DCD3C3"/></radialGradient>'
            f'<radialGradient id="bloom" gradientUnits="userSpaceOnUse" cx="{tx}" cy="{ty}" r="520">'
            f'<stop offset=".3" stop-color="{BLOOD}" stop-opacity=".32"/><stop offset="1" stop-color="{BLOOD}" stop-opacity=".16"/></radialGradient>')
    return svg(''.join(b), defs)


if __name__ == '__main__':
    render(build(), D + 'tier_board')
