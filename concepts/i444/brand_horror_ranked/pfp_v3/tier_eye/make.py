import os; HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # pfp_v3/ (base.py, render.js)
import sys; sys.path.insert(0, HERE); from base import *
# "tier eye" v2: a huge bloodshot staring eye that fills the avatar. Its iris IS the tier list: six horizontal
# rows (Slaughtered on top -> Easy at the bottom) clipped to a circle, with board-coloured gaps between them.
# The upper lid cuts into the top of the iris for a predatory stare; big black pupil with one white catchlight.
import math

OUT = HERE + '/tier_eye/tier_eye'

# ---------------- geometry ----------------
CX = 500
IY = 444          # iris centre y
IR = 315          # iris radius (limbus)
PR = 118          # pupil radius (v1 ratio 0.30 -> 0.37)
LID_CUT = 0.15    # upper lid covers this fraction of the iris diameter
GAP = 15          # #1A1A17 gap between tier rows inside the iris
OUTLINE = 26      # same dark outline on both lids
LIMBUS = 18       # dark ring round the iris

LX, LY = 20, 478  # inner corner (left)
RX, RY = 980, 460 # outer corner (right)
SLANT = 20        # upper lid dips toward the inner corner: a glare, not a sleepy droop
TOPY = IY - IR + 2 * IR * LID_CUT     # lid height over the iris centre
BOTY = IY + IR + 58                   # lower lid low point (white shows under the iris: wide, staring)

UP = [((LX, LY), (110, 310), (320, TOPY + SLANT), (500, TOPY)),
      ((500, TOPY), (680, TOPY - SLANT), (880, 262), (RX, RY))]
LO = [((RX, RY), (880, 720), (700, BOTY), (500, BOTY)),
      ((500, BOTY), (300, BOTY), (120, 730), (LX, LY))]


def cpath(segs):
    s = f'M {segs[0][0][0]:.1f} {segs[0][0][1]:.1f} '
    for _, a, b, c in segs:
        s += f'C {a[0]:.1f} {a[1]:.1f}, {b[0]:.1f} {b[1]:.1f}, {c[0]:.1f} {c[1]:.1f} '
    return s


EYE = cpath(UP) + cpath(LO)[cpath(LO).index('C'):] + 'Z'


def bez(p0, p1, p2, p3, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        pts.append((u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                    u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]))
    return pts


def taper(pts, w0, w1):
    """filled ribbon along a polyline, width w0 -> w1, rounded start"""
    left, right = [], []; n = len(pts)
    for i, (x, y) in enumerate(pts):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = (w0 + (w1 - w0) * (i / (n - 1)) ** 0.9) / 2
        left.append((x + nx * w, y + ny * w)); right.append((x - nx * w, y - ny * w))
    return 'M ' + ' L '.join(f'{x:.1f} {y:.1f}' for x, y in left + right[::-1]) + ' Z'


def vein(start, end, bend, w0, w1=2, branches=(), col='#B0101A', op=0.95):
    """a tapered, gently curved blood vessel with optional branches (t, angle, length, width)"""
    sx, sy = start; ex, ey = end
    dx, dy = ex - sx, ey - sy; d = math.hypot(dx, dy); nx, ny = -dy / d, dx / d
    c1 = (sx + dx * 0.33 + nx * bend, sy + dy * 0.33 + ny * bend)
    c2 = (sx + dx * 0.66 - nx * bend * 0.4, sy + dy * 0.66 - ny * bend * 0.4)
    pts = bez(start, c1, c2, end)
    out = f'<path d="{taper(pts, w0, w1)}" fill="{col}" opacity="{op}"/>'
    for t, ang, ln, bw in branches:
        i = int(t * (len(pts) - 1)); bx, by = pts[i]
        a = math.atan2(dy, dx) + math.radians(ang)
        out += vein((bx, by), (bx + math.cos(a) * ln, by + math.sin(a) * ln), ln * 0.15 * (1 if ang > 0 else -1), bw, 1.5, (), col, op)
    return out


# ---- six veins (v1 had twelve + fibre texture), ~1.7x thicker ----
veins = ''
veins += vein((8, 470), (190, 400), 30, 30, 3, [(0.45, -50, 80, 13), (0.62, 40, 70, 10)])
veins += vein((12, 505), (196, 572), -24, 26, 3, [(0.5, 42, 70, 11)])
veins += vein((120, 712), (262, 604), -22, 18, 2.5, [(0.5, -48, 50, 9)])
veins += vein((992, 460), (810, 392), -30, 30, 3, [(0.45, 50, 80, 13), (0.62, -40, 70, 10)])
veins += vein((988, 492), (804, 565), 24, 26, 3, [(0.5, -42, 70, 11)])
veins += vein((880, 700), (740, 596), 22, 18, 2.5, [(0.5, 48, 50, 9)])

# ---- iris: horizontal tier rows over the VISIBLE part (lid line -> bottom of the iris) ----
y0 = TOPY + OUTLINE / 2 - 4
y1 = IY + IR - LIMBUS / 2
H = (y1 - y0) / 6
rows = ''.join(f'<rect x="{CX - IR - 5}" y="{(y0 - 60 if i == 0 else y0 + i * H):.1f}" width="{2 * IR + 10}" '
               f'height="{(H + 60 if i == 0 else H) + 1:.1f}" fill="{c}"/>' for i, c in enumerate(TM))
gaps = ''.join(f'<rect x="{CX - IR - 5}" y="{y0 + i * H - GAP / 2:.1f}" width="{2 * IR + 10}" height="{GAP}" fill="{BOARD}"/>'
               for i in range(1, 6))

catch = (f'<ellipse cx="{CX - PR * 0.42:.1f}" cy="{IY - PR * 0.48:.1f}" rx="44" ry="32" '
         f'transform="rotate(-28 {CX - PR * 0.42:.1f} {IY - PR * 0.48:.1f})" fill="#FFFFFF"/>')

defs = f'''
<clipPath id="eye"><path d="{EYE}"/></clipPath>
<clipPath id="iris"><circle cx="{CX}" cy="{IY}" r="{IR}"/></clipPath>
<clipPath id="disc"><circle cx="500" cy="500" r="500"/></clipPath>
<radialGradient id="bg" cx="500" cy="500" r="500" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#3A0A0E"/><stop offset="0.7" stop-color="#3A0A0E"/><stop offset="1" stop-color="#120305"/>
</radialGradient>
<radialGradient id="scl" cx="500" cy="{IY}" r="500" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#FFFDF8"/><stop offset="0.62" stop-color="#F4EEE4"/>
  <stop offset="0.85" stop-color="#EBCFC8"/><stop offset="1" stop-color="#D08A88"/>
</radialGradient>
<clipPath id="pup"><circle cx="{CX}" cy="{IY}" r="{PR}"/></clipPath>
<filter id="halo" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="30"/></filter>
<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="soft" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="18"/></filter>
'''

body = f'''
<g clip-path="url(#disc)">
<rect width="1000" height="1000" fill="url(#bg)"/>
<path d="{EYE}" fill="none" stroke="#7A141C" stroke-width="70" opacity="0.6" filter="url(#halo)"/>
<g clip-path="url(#eye)">
  <rect width="1000" height="1000" fill="url(#scl)"/>
  {veins}
  <path d="{EYE}" fill="none" stroke="#3A0E10" stroke-width="70" opacity="0.4" filter="url(#soft)"/>
  <g clip-path="url(#iris)">{rows}{gaps}</g>
  <circle cx="{CX}" cy="{IY}" r="{IR}" fill="none" stroke="{BOARD}" stroke-width="{LIMBUS}"/>
  <circle cx="{CX}" cy="{IY}" r="{PR}" fill="{PAGE}"/>
  <g clip-path="url(#pup)">
    <path d="M {CX - PR} {IY} a {PR} {PR} 0 1 0 {2 * PR} 0 a {PR} {PR} 0 1 0 {-2 * PR} 0 Z
             M {CX - PR} {IY - 16} a {PR} {PR} 0 1 0 {2 * PR} 0 a {PR} {PR} 0 1 0 {-2 * PR} 0 Z"
          fill-rule="evenodd" fill="{TM[0]}" opacity="0.75" filter="url(#glow)"/>
  </g>
  <circle cx="{CX}" cy="{IY}" r="{PR}" fill="none" stroke="{BOARD}" stroke-width="6"/>
  {catch}
</g>
<path d="{EYE}" fill="none" stroke="{PAGE}" stroke-width="{OUTLINE}" stroke-linejoin="round"/>
<circle cx="500" cy="500" r="490" fill="none" stroke="{BOARD}" stroke-width="20" opacity="0.75"/>
<circle cx="500" cy="500" r="497" fill="none" stroke="#6E141B" stroke-width="6"/>
</g>
'''

render(svg(body, defs), OUT)
