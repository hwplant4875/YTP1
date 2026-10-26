import os; HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # pfp_v3/ (base.py, render.js)
import sys, math; sys.path.insert(0, HERE); from base import *

# Horror Ranked pfp, v2: our own glossy emoji-style skull on the six TierMaker rows.
# v2 changes: dark row gaps (tier list, not a flag), inner rim, skull shrunk so every row shows,
# original nose / sockets / teeth, a bold blood-red crack notched through the outline, red glow in the sockets.
OUT = HERE + '/skull_emoji/skull_emoji'
STEM = OUT + (sys.argv[1] if len(sys.argv) > 1 else '')

GAP = 8            # dark gap between tier rows (units of 1000)
SC = 0.92          # skull scale (v1 = 1.0)
TOP = 182          # where the outer edge of the cranium outline lands after scaling (orange row starts at ~171)
LINE = 22          # visible outline width
RIM_W, RIM_O = 20, 0.75

# ---------------------------------------------------------------------------------------------
# skull silhouette (drawn in v1 coordinates, then scaled): dome -> cheekbones -> jaw -> four
# teeth with uneven bottoms
# ---------------------------------------------------------------------------------------------
X0, X1, G, R = 322, 678, 20, 22
N = 4
TW = (X1 - X0 - G * (N - 1)) / N
BOT = [810, 832, 826, 812]
YT = 724

def xl(i): return X0 + i * (TW + G)
def xr(i): return xl(i) + TW

def skull_path():
    p = ['M500 128',
         'C694 128 832 252 832 428',
         'C832 522 806 586 752 622',
         'C722 642 692 652 682 690',
         f'L{X1} {BOT[-1] - R}']
    for i in range(N - 1, -1, -1):
        b = BOT[i]
        p.append(f'Q{xr(i):.1f} {b} {xr(i) - R:.1f} {b} L{xl(i) + R:.1f} {b} Q{xl(i):.1f} {b} {xl(i):.1f} {b - R}')
        if i > 0:
            ny = min(BOT[i], BOT[i - 1]) - R - 14
            p.append(f'L{xl(i):.1f} {ny} L{xr(i - 1):.1f} {ny} L{xr(i - 1):.1f} {BOT[i - 1] - R}')
    p += ['L318 690',
          'C308 652 278 642 248 622',
          'C194 586 168 522 168 428',
          'C168 252 306 128 500 128 Z']
    return ' '.join(p)
SKULL = skull_path()

SLOTS = ''.join(f'<rect x="{xr(i):.1f}" y="{YT}" width="{G}" height="{min(BOT[i], BOT[i + 1]) - YT}" rx="{G / 2}" fill="{INK}"/>'
                for i in range(N - 1))

def socket(cx, cy, s, k=1.0):
    # big rounded socket whose domed brow dips toward the nose (s=+1 left eye, -1 right eye); the inner-top
    # corner is pulled in so the pair reads as eye holes, not a pair of sunglasses
    P = lambda dx, dy: f'{cx + dx * s * k:.1f} {cy + dy * k:.1f}'
    return (f'M{P(-48, -114)} C{P(4, -120)} {P(64, -106)} {P(94, -80)} '
            f'C{P(120, -56)} {P(118, 30)} {P(92, 70)} '
            f'C{P(64, 110)} {P(20, 118)} {P(-14, 114)} '
            f'C{P(-78, 108)} {P(-120, 60)} {P(-120, -6)} '
            f'C{P(-120, -62)} {P(-96, -110)} {P(-48, -114)} Z')
EYE_L = socket(360, 470, 1)
EYE_R = socket(640, 474, -1, 1.04)               # crack side: a touch bigger and lower, so the face is not mirror-perfect

# nose: rounded inverted triangle (point down) with a small chip out of its upper-right corner
NOSE = ('M470 598 L516 596 L524 608 L532 600 '      # top edge, then the chip
        'C544 600 546 612 540 622 '                  # rounded upper-right corner
        'L510 664 C505 671 495 671 490 664 '         # rounded bottom point
        'L458 620 C452 610 458 598 470 598 Z')

def wedge(pts, ws, dip=0):
    # filled polygon along a polyline with a width per point (sharp joints -> a jagged fracture, not a smooth stroke);
    # dip > 0 bites a V into the start edge (the notch the break leaves in the skull's silhouette)
    L, Rr = [], []
    for k, (x, y) in enumerate(pts):
        a, b = pts[max(k - 1, 0)], pts[min(k + 1, len(pts) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1
        w = ws[k] / 2
        L.append((x - dy / n * w, y + dx / n * w)); Rr.append((x + dy / n * w, y - dx / n * w))
    poly = L + Rr[::-1]
    if dip:
        (x0, y0), (x1, y1) = pts[0], pts[1]; n = math.hypot(x1 - x0, y1 - y0)
        poly.append((x0 + (x1 - x0) / n * dip, y0 + (y1 - y0) / n * dip))
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in poly) + ' Z'

# the break: starts outside the dome at ~1 o'clock and cuts straight through the outline (its V-shaped end leaves a
# notch in the silhouette), then zigzags in toward the right socket and splits once
_MAIN = [(730, 140), (706, 194), (688, 230), (700, 252), (675, 283), (684, 299), (664, 326)], [88, 74, 58, 46, 32, 20, 0]
_BRANCH = wedge([(694, 246), (716, 262), (722, 284)], [22, 13, 0])
CRACK0 = wedge(*_MAIN) + ' ' + _BRANCH                    # the break's full footprint (cut out of the skull, ink round it)
CRACK = wedge(*_MAIN, dip=50) + ' ' + _BRANCH             # the blood inside it, its end bitten into a V notch
CK = 10                                                         # ink border round the fissure

defs = f'''
<radialGradient id="bone" cx="0.38" cy="0.28" r="0.9">
  <stop offset="0" stop-color="#FAFAFC"/><stop offset="0.38" stop-color="#ECECF1"/>
  <stop offset="0.72" stop-color="#D3D5DE"/><stop offset="1" stop-color="#A9ACBB"/>
</radialGradient>
<radialGradient id="sock" cx="0.5" cy="0.52" r="0.62">
  <stop offset="0" stop-color="#B0121E"/><stop offset="0.16" stop-color="#6A0812"/>
  <stop offset="0.45" stop-color="#2E030A"/><stop offset="1" stop-color="#140306"/>
</radialGradient>
<radialGradient id="nos" cx="0.5" cy="0.4" r="0.7">
  <stop offset="0" stop-color="#2A0308"/><stop offset="1" stop-color="#120306"/>
</radialGradient>
<linearGradient id="blood" x1="0" y1="190" x2="0" y2="370" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="{BLOOD}"/><stop offset="1" stop-color="#8E0A14"/>
</linearGradient>
<filter id="drop" x="-20%" y="-20%" width="140%" height="150%">
  <feDropShadow dx="0" dy="18" stdDeviation="16" flood-color="#000" flood-opacity="0.32"/>
</filter>
<filter id="blur12" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>
<filter id="blur22" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
<clipPath id="sclip"><path d="{SKULL}"/></clipPath>
<mask id="cut" maskUnits="userSpaceOnUse" x="-300" y="-300" width="1600" height="1600">
  <rect x="-300" y="-300" width="1600" height="1600" fill="#fff"/>
  <path d="{CRACK0}" fill="#000" stroke="#000" stroke-width="{CK * 2}" stroke-linejoin="round"/>
</mask>
<mask id="outer" maskUnits="userSpaceOnUse" x="-300" y="-300" width="1600" height="1600">
  <path d="{SKULL}" fill="#fff" stroke="#fff" stroke-width="{LINE * 2}" stroke-linejoin="round"/>
</mask>
<mask id="border" maskUnits="userSpaceOnUse" x="-300" y="-300" width="1600" height="1600">
  <path d="{SKULL}" fill="#fff" stroke="#fff" stroke-width="{LINE * 2}" stroke-linejoin="round"/>
  <path d="{CRACK0}" fill="#000"/>
</mask>
'''

# tier rows with thin dark gaps (TierMaker board), inner rim for white YouTube
rows = f'<rect width="1000" height="1000" fill="{BOARD}"/>' + ''.join(
    f'<rect x="0" y="{max(0, 1000 * k / 6 + (GAP / 2 if k else 0)):.2f}" width="1000" '
    f'height="{1000 / 6 - (GAP / 2 if k else 0) - (GAP / 2 if k < 5 else 0):.2f}" fill="{c}"/>' for k, c in enumerate(TM))
rim = f'<circle cx="500" cy="500" r="{500 - RIM_W / 2}" fill="none" stroke="{BOARD}" stroke-width="{RIM_W}" opacity="{RIM_O}"/>'

TY = TOP - SC * (128 - LINE)
skull = f'''
<g transform="translate({500 - 500 * SC:.2f} {TY:.2f}) scale({SC})">
 <g mask="url(#cut)">
  <g filter="url(#drop)"><path d="{SKULL}" fill="{INK}" stroke="{INK}" stroke-width="{LINE * 2}" stroke-linejoin="round"/></g>
  <path d="{SKULL}" fill="url(#bone)"/>
  <g clip-path="url(#sclip)">
    <ellipse cx="246" cy="604" rx="80" ry="52" fill="#868899" opacity="0.45" filter="url(#blur22)"/>
    <ellipse cx="754" cy="604" rx="80" ry="52" fill="#868899" opacity="0.45" filter="url(#blur22)"/>
    <g filter="url(#blur22)" opacity="0.5" fill="#6E7184">
      <path d="{EYE_L}" transform="translate(0 -10)"/><path d="{EYE_R}" transform="translate(0 -10)"/>
    </g>
    <ellipse cx="372" cy="236" rx="118" ry="52" fill="#FFFFFF" opacity="0.95" transform="rotate(-24 372 236)" filter="url(#blur12)"/>
    <ellipse cx="262" cy="350" rx="22" ry="16" fill="#FFFFFF" opacity="0.9" filter="url(#blur12)"/>
  </g>
  {SLOTS}
  <path d="{EYE_L}" fill="url(#sock)"/>
  <path d="{EYE_R}" fill="url(#sock)"/>
  <path d="{NOSE}" fill="url(#nos)"/>
 </g>
 <!-- the break: the outline runs into it as an ink border; blood inside the bone, the gap in the outline left open -->
 <g mask="url(#border)"><path d="{CRACK0}" fill="none" stroke="{INK}" stroke-width="{CK * 2 + 4}" stroke-linejoin="round"/></g>
 <path d="{CRACK}" fill="url(#blood)" mask="url(#outer)"/>
</g>
'''

render(svg(rows + skull + rim, defs), STEM)
