import os; HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # pfp_v3/ (base.py, render.js)
import sys; sys.path.insert(0, HERE); from base import *

# "Melting tier list" v2: the six TierMaker rows (exact colours, thin #1A1A17 gaps) fill the top of the circle and melt
# down onto a dark blood-maroon board. One hero drip, centred on x=500, carries the whole list bent into it as nested
# U-shaped layers with the same dark gaps (green outermost, Slaughtered red in the core). The red core is a wide blood
# stream (15 % of the width) that deepens to #C8101C by mid-drip and darker at its tip, and lets one big drop fall
# towards a small blood pool. Minor drips (two per side) are flat green: only the Easy row melts there.
# Also writes <OUT>_mono.svg: a one-colour (white) silhouette for the watermark / merch.

OUT = HERE + '/melting_tiers/melting_tiers'
MAROON = '#2A070C'
GAP = 7                                  # dark gap between rows and between nested layers (units of 1000)

B0, P = 124, 66                          # bottom of the red row, row pitch (row + gap)
B = [B0 + k * P for k in range(6)]       # bottom edge of each tier row: 124 ... 454
HX, HT = 500, 748                        # hero drip centre and outer (green) tip, ~75 % of the height
CORE = 75                                # half-width of the red core -> 150 = 15 % of the width
L = 18                                   # one nested layer = 11 colour + 7 gap
MINOR = [(136, 596, 35), (258, 664, 27), (744, 634, 33), (866, 584, 28)]   # flat green drips: (cx, tip, half-width)
DROP_Y, DROP_R = 770, 33                 # falling drop: tip y, belly radius (2x v1)
POOL_Y = 900


def f(v):
    return f'{v:.1f}'


def drip(cx, y0, tip, a, b, rx, ry, top_pad=3):
    """drip hanging from baseline y0: soft funnel shoulders (reach rx, ry), a straight column of half-width a and a round
    bulb of radius b (b >= a) whose lowest point is `tip`. Every joint has a vertical tangent, so there are no kinks.
    The path starts top_pad px above y0 so it fuses with its own bar."""
    top = y0 - top_pad
    ys = y0 + ry                      # shoulder ends, column starts
    yc = tip - b                      # bulb centre
    neck = max(ys, yc - b * 1.25)     # column ends, bulb flare starts
    h = yc - neck
    return ''.join([
        f'M{f(cx - a - rx)},{f(top)}', f'L{f(cx + a + rx)},{f(top)}', f'L{f(cx + a + rx)},{f(y0)}',
        f'C{f(cx + a + rx * .45)},{f(y0)} {f(cx + a)},{f(y0 + ry * .5)} {f(cx + a)},{f(ys)}',
        f'L{f(cx + a)},{f(neck)}',
        f'C{f(cx + a)},{f(neck + h * .55)} {f(cx + b)},{f(yc - h * .45)} {f(cx + b)},{f(yc)}',
        f'A{f(b)},{f(b)} 0 0 1 {f(cx - b)},{f(yc)}',
        f'C{f(cx - b)},{f(yc - h * .45)} {f(cx - a)},{f(neck + h * .55)} {f(cx - a)},{f(neck)}',
        f'L{f(cx - a)},{f(ys)}',
        f'C{f(cx - a)},{f(y0 + ry * .5)} {f(cx - a - rx * .45)},{f(y0)} {f(cx - a - rx)},{f(y0)}', 'Z'])


def drop(cx, yt, R):
    """a falling teardrop: point at yt, round belly of radius R"""
    yc = yt + R * 2.1
    return (f'M{f(cx)},{f(yt)} C{f(cx + R * .25)},{f(yt + R * .8)} {f(cx + R)},{f(yc - R * .6)} {f(cx + R)},{f(yc)} '
            f'A{f(R)},{f(R)} 0 0 1 {f(cx - R)},{f(yc)} C{f(cx - R)},{f(yc - R * .6)} {f(cx - R * .25)},{f(yt + R * .8)} {f(cx)},{f(yt)}Z')


def pool(cx, y):
    """a small flat blood pool: one wide lens with two lazy lobes"""
    return (f'<ellipse cx="{cx}" cy="{y}" rx="100" ry="17"/><ellipse cx="{cx - 74}" cy="{y + 6}" rx="42" ry="12"/>'
            f'<ellipse cx="{cx + 80}" cy="{y + 5}" rx="46" ry="12"/>')


def tier_shapes(k):
    """every shape that tier k (0 = red ... 5 = green) paints: its row plus its layer of the hero drip
    (plus the flat minor drips for the green row)"""
    n = 5 - k                                          # 0 = green (outermost) ... 5 = red (core)
    a = CORE + (5 - n) * L
    tip = HT - n * L
    ry = 34 + n * 20
    b = min(a + 8 + 10 * (1 - n / 5), max(a, tip - B[k] - ry - 6))   # bulb flare, clamped so it fits below the shoulders
    shapes = [f'<rect x="-60" y="{B[k] - 1400}" width="1120" height="1400"/>',
              f'<path d="{drip(HX, B[k], tip, a, b, 26 + n * 11, ry)}"/>']
    if k == 5:
        shapes += [f'<path d="{drip(cx, B[5], t, w, w + 7, 20, 26)}"/>' for cx, t, w in MINOR]
    return shapes


def tiers(fill_for, gap_col=BOARD):
    """painter's order green -> red; each tier first lays a dark outline (the TierMaker gap) then its fill,
    so the visible gap is the outer half of the stroke"""
    out = ''
    for k in range(5, -1, -1):
        s = ''.join(tier_shapes(k))
        out += f'<g fill="none" stroke="{gap_col}" stroke-width="{GAP * 2}" stroke-linejoin="round">{s}</g>'
        out += f'<g fill="{fill_for(k)}">{s}</g>'
    return out


def build():
    red_tip = HT - 5 * L
    defs = (f'<linearGradient id="blood" gradientUnits="userSpaceOnUse" x1="0" y1="{B[0]}" x2="0" y2="{red_tip}">'
            f'<stop offset="0" stop-color="{TM[0]}"/><stop offset=".18" stop-color="#EE4450"/>'
            f'<stop offset=".45" stop-color="{BLOOD}"/><stop offset="1" stop-color="#8C0814"/></linearGradient>'
            f'<radialGradient id="glow" cx="500" cy="930" r="520" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#4C0C14"/><stop offset="1" stop-color="{MAROON}"/></radialGradient>')
    body = '<rect width="1000" height="1000" fill="url(#glow)"/>'
    body += tiers(lambda k: 'url(#blood)' if k == 0 else TM[k])
    body += f'<g fill="{BLOOD}">{pool(HX, POOL_Y)}</g>'
    body += f'<ellipse cx="{HX - 14}" cy="{POOL_Y - 6}" rx="58" ry="5" fill="#F0505A" fill-opacity=".55"/>'
    body += f'<path d="{drop(HX, DROP_Y, DROP_R)}" fill="{BLOOD}"/>'
    R = DROP_R
    body += (f'<path d="M{HX - R * .55},{DROP_Y + R * 2.0} a{R * .62},{R * .62} 0 0 1 {R * .3},-{R * .5}" fill="none" '
             f'stroke="#FF9A9A" stroke-opacity=".6" stroke-width="{R * .16}" stroke-linecap="round"/>')
    # thin dark inner rim so the pale top keeps the circle's edge on white YouTube
    body += f'<circle cx="500" cy="500" r="490" fill="none" stroke="{BOARD}" stroke-opacity=".72" stroke-width="20"/>'
    return svg(body, defs)


def build_mono(col='#FFFFFF'):
    """one-colour silhouette: the same rows, gaps and drips knocked out of a single fill, cropped to the circle"""
    m = '<rect width="1000" height="1000" fill="#000"/>' + tiers(lambda k: '#FFF', gap_col='#000')
    m += f'<g fill="#FFF">{pool(HX, POOL_Y)}<path d="{drop(HX, DROP_Y, DROP_R)}"/></g>'
    defs = (f'<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="1000" height="1000">{m}</mask>'
            '<clipPath id="c"><circle cx="500" cy="500" r="500"/></clipPath>')
    return svg(f'<g clip-path="url(#c)"><rect width="1000" height="1000" fill="{col}" mask="url(#m)"/></g>', defs)


if __name__ == '__main__':
    render(build(), OUT)
    render(build_mono(), OUT + '_mono')
