import os; HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # pfp_v3/ (base.py, render.js)
import sys; sys.path.insert(0, HERE); from base import *
import math
OUT = HERE + '/scream_face/scream_face'

# v2: tight crop (head + hands ~80% of the height), gaunt grey-blue face, pure-black O mouth, slender hands with thumbs
# and cuffs, and a calm tier-list sky: six exact tier rows with thin board-coloured gaps that are flat at the edges and
# only swirl up around the head; a blood-red halo (the Slaughtered row "bleeding" behind the head) is the villain cue.

def f(v): return f'{v:.1f}'

def catmull(pts, closed=False):
    n = len(pts); d = f'M{f(pts[0][0])},{f(pts[0][1])}'
    for i in range(n if closed else n - 1):
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]; p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f' C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}'
    return d + (' Z' if closed else '')

def mirror_close(right, cx=500):
    left = [(2 * cx - x, y) for x, y in reversed(right[1:-1])]
    return right + left

def poly(pts): return 'M' + ' L'.join(f'{f(x)},{f(y)}' for x, y in pts) + ' Z'

# ---------- sky: six tier rows, flat at the rim, sweeping up around the head ----------
T = [212, 356, 500, 644, 788]               # row boundaries where the rows are flat (edges of the circle)
BEND = [-170, -230, -190, 60, 90]           # how far each boundary is pulled up (-) / pushed down (+) near the head
SIG = 205
GAP = 9                                     # board-coloured gap between rows (TierMaker)
def boundary(i, x):
    return T[i] + BEND[i] * math.exp(-((x - 500) / SIG) ** 2)

XS = list(range(-40, 1041, 20))
def sky():
    out = [f'<rect width="1000" height="1000" fill="{TM[5]}"/>']
    for i in range(4, -1, -1):
        d = catmull([(x, boundary(i, x)) for x in XS]) + ' L1040,-40 L-40,-40 Z'
        out.append(f'<path d="{d}" fill="{TM[i]}"/>')
    for i in range(5):
        out.append(f'<path d="{catmull([(x, boundary(i, x)) for x in XS])}" fill="none" stroke="{BOARD}" stroke-width="{GAP}"/>')
    return ''.join(out)

# ---------- head: a bulb with hollow cheeks and a narrow jaw ----------
HEAD_R = [(500, 88), (586, 98), (655, 142), (694, 222), (702, 318), (686, 412), (656, 488), (636, 552),
          (630, 622), (614, 704), (580, 778), (538, 826), (500, 838)]
HEAD = mirror_close(HEAD_R)
HEAD_D = catmull(HEAD, closed=True)

def offset(pts, d, cx=500, cy=470):
    # crude radial offset of the head outline (good enough for a halo behind it)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy; L = math.hypot(dx, dy) or 1
        out.append((x + dx / L * d, y + dy / L * d))
    return out

# ---------- hands ----------
def xf(pts, ox, oy, ang, mirror=False):
    # local (u,v): v runs from wrist to fingertips, u points toward the face; ang leans the fingers toward the face
    a = math.radians(ang); V = (-math.sin(a), -math.cos(a)); U = (-math.cos(a), math.sin(a)); out = []
    for u, v in pts:
        x, y = ox + u * U[0] + v * V[0], oy + u * U[1] + v * V[1]
        out.append((1000 - x, y) if mirror else (x, y))
    return out

def capsule(u0, v0, u1, v1, r, n=10):
    ang = math.atan2(v1 - v0, u1 - u0); pts = []
    for k in range(n + 1):
        t = ang - math.pi / 2 + math.pi * k / n; pts.append((u1 + r * math.cos(t), v1 + r * math.sin(t)))
    for k in range(n + 1):
        t = ang + math.pi / 2 + math.pi * k / n; pts.append((u0 + r * math.cos(t), v0 + r * math.sin(t)))
    return pts

HX, HY, HA = 706, 734, 5          # right wrist (viewer's right); left hand is mirrored
FR = 12.5                           # finger radius
FINGERS = [(-33, 126, -40, 246), (-11, 134, -13, 284), (11, 134, 13, 290), (33, 124, 38, 264)]   # outer -> inner (u>0 is the face side)
THUMB = (34, 46, 66, 156)
PALM = [(-34, -6), (-44, 60), (-46, 132), (-28, 148), (28, 148), (46, 128), (44, 56), (32, -6)]
SLEEVE = [(-54, -24), (-84, -320), (84, -320), (50, -24)]
CUFF = [(-52, 6), (-56, -44), (52, -44), (48, 6)]

def hand_shapes(mirror):
    palm = xf(PALM, HX, HY, HA, mirror)
    fingers = [xf(capsule(*fg, FR), HX, HY, HA, mirror) for fg in FINGERS]
    thumb = xf(capsule(*THUMB, 15), HX, HY, HA, mirror)
    sleeve = xf(SLEEVE, HX, HY, HA, mirror); cuff = xf(CUFF, HX, HY, HA, mirror)
    seams = [xf([(u0 + (u1 - u0) * 0.06 + s * 12, v0 + 6), (u0 + (u1 - u0) * 0.75 + s * 12, v0 + (v1 - v0) * 0.75)], HX, HY, HA, mirror)
             for s, (u0, v0, u1, v1) in zip((1, 1, 1), FINGERS[:3])]
    fold = xf([(14, -70), (22, -300)], HX, HY, HA, mirror)
    return palm, fingers, thumb, sleeve, cuff, seams, fold

COAT, FOLD = '#3A151A', '#6A2F37'
SKIN_TOP, SKIN_BOT = '#B3BBCE', '#919BB2'
HOLLOW = '#7A849D'
SOCKET = '#4C5570'
S = 24          # head outline width

def eye(cx, cy, rx=72, ry=92):
    return (f'<ellipse cx="{cx}" cy="{cy + 12}" rx="{rx + 14}" ry="{ry + 22}" fill="{SOCKET}"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#FFFFFF" stroke="{INK}" stroke-width="16"/>'
            f'<circle cx="{cx}" cy="{cy + 8}" r="17" fill="{BLOOD}"/>'
            f'<circle cx="{cx}" cy="{cy + 8}" r="10" fill="{INK}"/>')

def build():
    defs = (
        f'<linearGradient id="skin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SKIN_TOP}"/><stop offset="1" stop-color="{SKIN_BOT}"/></linearGradient>'
        f'<linearGradient id="hskin" gradientUnits="userSpaceOnUse" x1="0" y1="440" x2="0" y2="760"><stop offset="0" stop-color="#BCC3D4"/><stop offset="1" stop-color="#97A1B7"/></linearGradient>'
        '<filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="16"/></filter>'
        f'<linearGradient id="bleed" gradientUnits="userSpaceOnUse" x1="0" y1="40" x2="0" y2="640"><stop offset="0" stop-color="{BLOOD}"/>'
        f'<stop offset="0.6" stop-color="{BLOOD}" stop-opacity="0.8"/><stop offset="1" stop-color="{BLOOD}" stop-opacity="0"/></linearGradient>'
        f'<clipPath id="headclip"><path d="{HEAD_D}"/></clipPath>'
    )
    out = [sky()]
    # blood halo behind the head (the Slaughtered row bleeding down around the scream)
    out.append(f'<path d="{catmull(offset(HEAD, 46), closed=True)}" fill="url(#bleed)" filter="url(#glow)"/>')
    # neck + collar
    out.append(f'<path d="M462,780 L464,900 L536,900 L538,780 Z" fill="{HOLLOW}" stroke="{INK}" stroke-width="20"/>')
    out.append(f'<path d="M190,1010 C230,920 330,872 444,864 L500,914 L556,864 C670,872 770,920 810,1010 Z" fill="{COAT}" stroke="{INK}" stroke-width="14"/>')
    hr = hand_shapes(False); hl = hand_shapes(True)
    for palm, fingers, thumb, sleeve, cuff, seams, fold in (hr, hl):
        out.append(f'<path d="{poly(sleeve)}" fill="{COAT}" stroke="{INK}" stroke-width="14" stroke-linejoin="round"/>')
        a, b = fold; out.append(f'<path d="M{f(a[0])},{f(a[1])} L{f(b[0])},{f(b[1])}" stroke="{FOLD}" stroke-width="14" stroke-linecap="round"/>')
    # head
    out.append(f'<path d="{HEAD_D}" fill="url(#skin)" stroke="{INK}" stroke-width="{S}" stroke-linejoin="round"/>')
    # gaunt shading inside the head: hollow cheeks + temples
    sh = []
    for sgn in (1, -1):
        X = lambda x: 500 + sgn * (x - 500)
        cheek = [(X(650), 430), (X(612), 470), (X(590), 560), (X(596), 660), (X(620), 720), (X(650), 640), (X(660), 520)]
        sh.append(f'<path d="{catmull(cheek, closed=True)}" fill="{HOLLOW}"/>')
        temple = [(X(690), 190), (X(660), 230), (X(668), 300), (X(705), 330)]
        sh.append(f'<path d="{catmull(temple, closed=True)}" fill="{HOLLOW}" opacity="0.6"/>')
    out.append(f'<g clip-path="url(#headclip)">{"".join(sh)}</g>')
    out.append(f'<path d="{HEAD_D}" fill="none" stroke="{INK}" stroke-width="{S}" stroke-linejoin="round"/>')
    out.append('<ellipse cx="430" cy="168" rx="70" ry="30" transform="rotate(-20 430 168)" fill="#FFFFFF" opacity="0.35"/>')
    # face
    for sgn in (1, -1):   # anguished brows: inner ends pulled up
        X = lambda x: 500 + sgn * (x - 500)
        out.append(f'<path d="M{X(478)},{196} Q{X(420)},{196} {X(362)},{224}" fill="none" stroke="{SOCKET}" stroke-width="20" stroke-linecap="round"/>')
    out.append(eye(417, 322) + eye(583, 322))
    out.append(f'<path d="M484,446 q-12,18 4,26" fill="none" stroke="{SOCKET}" stroke-width="11" stroke-linecap="round"/>')
    out.append(f'<path d="M516,446 q12,18 -4,26" fill="none" stroke="{SOCKET}" stroke-width="11" stroke-linecap="round"/>')
    out.append('<path d="M500,512 C552,512 570,580 570,646 C570,724 540,772 500,772 C460,772 430,724 430,646 C430,580 448,512 500,512 Z" fill="#000000"/>')
    # hands: thick dark outline first (keeps a clear dark gap to the head), then skin
    for palm, fingers, thumb, sleeve, cuff, seams, fold in (hr, hl):
        for p in [palm, thumb] + fingers + [cuff]:
            out.append(f'<path d="{poly(p)}" fill="{INK}" stroke="{INK}" stroke-width="40" stroke-linejoin="round"/>')
    for palm, fingers, thumb, sleeve, cuff, seams, fold in (hr, hl):
        for p in [palm, thumb] + fingers:
            out.append(f'<path d="{poly(p)}" fill="url(#hskin)"/>')
        out.append(f'<path d="{poly(cuff)}" fill="{FOLD}"/>')
        for a, b in seams:
            out.append(f'<path d="M{f(a[0])},{f(a[1])} L{f(b[0])},{f(b[1])}" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>')
    # dark inner rim so pale rows keep the circle's edge on white YouTube
    out.append(f'<circle cx="500" cy="500" r="490" fill="none" stroke="{BOARD}" stroke-width="20" opacity="0.75"/>')
    return svg(''.join(out), defs)

render(build(), OUT)
