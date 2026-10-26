import os; HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # pfp_v3/ (base.py, render.js)
import sys; sys.path.insert(0, HERE); from base import *
import math, random

# v2 "Slashed tier list": ONE big diagonal torn slash rips through the six TierMaker rows (with their dark gaps),
# opening onto the dark board beneath. The lower lip is a bright #E01020 cut face over an inner wall shaded
# #C8101C -> near-black; the upper lip peels back in a curl of the band colour; one fat tapered drip hangs off the lower lip.
OUT = HERE + '/tier_slash/'

GAP = 8                       # #1A1A17 gap between tier rows (units of 1000)
LIPC = '#E01020'              # bright cut face on the lower lip
HOLE = '#0C0708'              # the dark board seen through the cut
DEEP = (0x16, 0x05, 0x07)     # wall colour at the bottom of the gradient
RIM_W, RIM_OP = 20, 0.75      # dark inner rim: keeps the circle's edge on white YouTube

A = (200, 815)                # bottom-left tip of the slash
B = (794, 175)                # top-right tip
BEND = 12                     # the slash arcs towards the upper-left
W = 184                       # full width of the opening at its widest
PK = (1.1, 1.05)              # width profile exponents t^a (1-t)^b: long thin tail at the bottom-left, fat near the top
FU = 0.52                     # share of the width above the axis
LIP = 19                      # cut-face band (about 1.5% of the diameter)
WALL = 0.17                   # share of the local width that is shaded inner wall (below the lip band)
JAG_U = (12, 6, 26)           # upper lip tears: (seed, notches, notch depth)
JAG_L = (5, 5, 20)            # lower lip tears
CURL = (0.34, 0.80, 36)       # curl on the upper lip: (t start, t end, max width)
PINCH = [(0.30, 0.07, 0.22), (0.80, 0.05, 0.10)]   # (t, spread, depth): the tear opens unevenly along its length
DRIP_T = 0.56                 # where on the lower lip the drip hangs (0 = bottom-left tip)
DRIP = dict(w0=88, wn=40, rb=44, ln=250, sway=-10, fr=22, fl=48)   # fr: right fillet radius, fl: left sweep length along the lip
DRIPSH = '#9A0914'; DSH = 9      # drip's shaded right edge
PULL = (0.62, 70)             # the sheet is pulled apart: rows bend away from the cut by PULL[0]*half-width, decaying over PULL[1] units

VARIANTS = {'nopull': dict(PULL=(0, 1))}   # python3 make.py nopull -> straight rows, for comparison
VAR = next((v for v in sys.argv[1:] if v in VARIANTS), None)
if VAR: globals().update(VARIANTS[VAR])


def mix(c, d, f):
    c = [int(c[i:i + 2], 16) for i in (1, 3, 5)] if isinstance(c, str) else c
    d = [int(d[i:i + 2], 16) for i in (1, 3, 5)] if isinstance(d, str) else d
    return '#%02X%02X%02X' % tuple(round(c[i] + (d[i] - c[i]) * f) for i in range(3))


def rows():
    h = (1000 - 5 * GAP) / 6
    return [(i * (h + GAP), h) for i in range(6)]


U = ((B[0] - A[0]), (B[1] - A[1])); LEN = math.hypot(*U); U = (U[0] / LEN, U[1] / LEN)
NU = (U[1], -U[0])            # unit normal towards the upper-left lip
NL = (-U[1], U[0])            # towards the lower-right lip
PMAX = max((t ** PK[0]) * (1 - t) ** PK[1] for t in [i / 1000 for i in range(1001)])




def prof(t):
    t = min(max(t, 0), 1); p = (t ** PK[0]) * (1 - t) ** PK[1] / PMAX
    for c, s_, dpt in PINCH: p *= 1 - dpt * math.exp(-((t - c) / s_) ** 2)
    return p


def axis(t):
    s = BEND * math.sin(math.pi * t)
    return (A[0] + U[0] * LEN * t + NU[0] * s, A[1] + U[1] * LEN * t + NU[1] * s)


def at(t, v):
    """point at signed offset v from the axis (v>0: upper-left side)"""
    a = axis(t); return (a[0] + NU[0] * v, a[1] + NU[1] * v)


def wu(t): return W * FU * prof(t)
def wl(t): return W * (1 - FU) * prof(t)


def torn(seed, notches, namp, jit=(40, 2.2), wave=4.0, bias=0.0):
    """torn-edge offset function f(t) and its corner t's: fine fibre jitter + a slow wave + a few bold triangular notches"""
    r = random.Random(seed); jt = [0.0]; jv = [0.0]
    while jt[-1] < 1:
        jt.append(min(1.0, jt[-1] + r.uniform(0.5, 1.5) / jit[0])); jv.append(r.uniform(-1, 1) * jit[1])
    jv[-1] = 0.0
    ph = r.uniform(0, 6.3); fq = r.uniform(2.2, 3.2)
    ns = []
    for i in range(notches):
        c = (i + r.uniform(0.25, 0.75)) / notches; hw = r.uniform(0.018, 0.04)
        a = namp * r.uniform(0.55, 1.0) * (1 if r.random() < 0.7 else -0.6); sk = r.uniform(0.35, 0.65)
        ns.append((c - hw * 2 * sk, c, c + hw * 2 * (1 - sk), a))
    def f(t):
        v = interp(jt, jv, t) + wave * math.sin(2 * math.pi * fq * t + ph) + bias
        for a0, c, a1, a in ns:
            if a0 < t < c: v += a * (t - a0) / (c - a0)
            elif c <= t < a1: v += a * (a1 - t) / (a1 - c)
        return v
    keys = jt + [k for n in ns for k in n[:3]]
    return f, [k for k in keys if 0 <= k <= 1]


def interp(ts, vs, t):
    for i in range(len(ts) - 1):
        if ts[i] <= t <= ts[i + 1]:
            f = (t - ts[i]) / (ts[i + 1] - ts[i] or 1); return vs[i] + (vs[i + 1] - vs[i]) * f
    return 0.0


def env(t): return min(1.0, prof(t) / 0.45)


def bump(t, a, b):
    if t <= a or t >= b: return 0.0
    x = (t - a) / (b - a); return math.sin(math.pi * x) ** 0.8


def pull(p):
    """displace a point of the tier sheet away from the cut, so the row lines kink into the tear"""
    if not PULL[0]: return p
    t = ((p[0] - A[0]) * U[0] + (p[1] - A[1]) * U[1]) / LEN
    if not 0 < t < 1: return p
    a = axis(t); v = (p[0] - a[0]) * NU[0] + (p[1] - a[1]) * NU[1]
    w = wu(t) if v >= 0 else -wl(t)
    m = PULL[0] * w * math.exp(-abs(v) / PULL[1])
    return (p[0] + NU[0] * m, p[1] + NU[1] * m)


def band_paths():
    out = []
    for y, h in rows():
        xs = [x * 4 - 40 for x in range(271)]
        top = [pull((x, y)) for x in xs]; bot = [pull((x, y + h)) for x in xs]
        out.append(P(top + bot[::-1]))
    return out


def P(pts, close=True):
    return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ('Z' if close else '')


def build():
    fu, ku = torn(*JAG_U); fl, kl = torn(*JAG_L, bias=2.0)
    T = sorted(set([i / 300 for i in range(301)] + ku + kl))
    c0, c1, cw = CURL
    dr, ddef, (s0, s1) = drip()
    sc, sw = (s0 - 0.03 + s1) / 2, (s1 - s0) / 2 + 0.075
    dmask = lambda t: math.exp(-((t - sc) / sw) ** 6)                # liquid smooths the lower lip around the drip
    cmask = lambda t: min(1.0, 1.6 * bump(t, c0 - 0.02, c1 + 0.02))  # the fold line is clean where the lip peels back

    up = [at(t, wu(t) + fu(t) * env(t) * (1 - cmask(t))) for t in T]       # opening's upper boundary
    lo = [at(t, -wl(t) - fl(t) * env(t) * (1 - dmask(t))) for t in T]      # opening's lower boundary (jagged lip)
    jl = lambda t: fl(t) * env(t) * (1 - dmask(t))
    loi = [at(t, -wl(t) - jl(t) + min(2.0, wl(t) * 0.1)) for t in T]
    hole = P(up + loi[::-1])

    # inner wall: lip band (#E01020) over a stepped gradient #C8101C -> near-black that follows the lip
    lipw = lambda t: min(LIP, 0.30 * (wu(t) + wl(t)))
    walld = lambda t: WALL * (wu(t) + wl(t))
    wall = ''; K = 26
    for k in range(K):
        f = 1 - k / K                                  # 1 = deepest strip
        col = mix(BLOOD, DEEP, f ** 0.85)
        inner = [at(t, -wl(t) - 0.5 * jl(t) + lipw(t) + walld(t) * f) for t in T]   # wall follows the torn lip
        wall += f'<path d="{P(loi + inner[::-1])}" fill="{col}"/>'
    lipin = [at(t, -wl(t) - 0.5 * jl(t) + lipw(t)) for t in T]
    wall += f'<path d="{P(lo + lipin[::-1])}" fill="{LIPC}"/>'

    # curl: the upper lip peels back over the surface as a lighter ribbon of the band colour, torn on its outer edge
    TC = [t for t in T if c0 <= t <= c1]
    fc, kc = torn(11, 4, 10, jit=(40, 4.0), wave=0)
    TC = sorted(set(TC + [k for k in kc if c0 <= k <= c1]))
    fold = [at(t, wu(t)) for t in TC]
    outer = [at(t, wu(t) + cw * bump(t, c0, c1) + fc(t) * bump(t, c0, c1)) for t in TC]
    rib = P(fold + outer[::-1])
    hl = [at(t, wu(t) + cw * bump(t, c0, c1) * 0.22) for t in TC]
    ribhl = P(fold + hl[::-1])
    BP = band_paths()
    defs = ''.join(f'<clipPath id="r{i}"><path d="{d_}"/></clipPath>' for i, d_ in enumerate(BP))
    sh = (NU[0] * 8, NU[1] * 8 + 5)
    curl = f'<path d="{rib}" transform="translate({sh[0]:.1f},{sh[1]:.1f})" fill="#000" fill-opacity=".16"/>'
    for i in range(6):
        curl += (f'<g clip-path="url(#r{i})"><path d="{rib}" fill="{mix(TM[i], "#FFFFFF", .48)}"/>'
                 f'<path d="{ribhl}" fill="{mix(TM[i], "#000000", .10)}"/></g>')

    # the drip
    defs += ddef
    board = f'<rect width="1000" height="1000" fill="{BOARD}"/>' + ''.join(f'<path d="{d_}" fill="{TM[i]}"/>' for i, d_ in enumerate(BP))
    rim = f'<circle cx="500" cy="500" r="{500 - RIM_W / 2}" fill="none" stroke="{BOARD}" stroke-opacity="{RIM_OP}" stroke-width="{RIM_W}"/>'
    return svg(board + curl + dr + f'<path d="{hole}" fill="{HOLE}"/>' + wall + rim, defs)


def drip():
    """one fat drip off the lower lip: true circular fillets into the lip on both sides (a big one in the acute corner,
    a small one in the obtuse corner), a stem that narrows with a slight sway, then a teardrop bulb.
    the root closes inside the opening, which is drawn on top and hides the seam. returns (svg, defs, (t0, t1) lip span)."""
    d = DRIP; N = 3000; TT = [i / N for i in range(N + 1)]
    L = [at(t, -wl(t)) for t in TT]                      # smooth lower lip, bottom-left -> top-right
    td = DRIP_T; x0 = at(td, -wl(td))[0]
    a, b = at(td - 0.01, -wl(td - 0.01)), at(td + 0.01, -wl(td + 0.01))
    m = math.hypot(b[0] - a[0], b[1] - a[1]); du = ((b[0] - a[0]) / m, (b[1] - a[1]) / m)   # local lip direction (up-right)
    xl, xr = x0 - d['w0'] / 2, x0 + d['w0'] / 2

    def ycross(x):
        for i in range(N):
            if (L[i][0] - x) * (L[i + 1][0] - x) <= 0 and L[i][0] != L[i + 1][0]:
                f = (x - L[i][0]) / (L[i + 1][0] - L[i][0]); return L[i][1] + (L[i + 1][1] - L[i][1]) * f
    def tnear(p):
        return min(range(N + 1), key=lambda i: (L[i][0] - p[0]) ** 2 + (L[i][1] - p[1]) ** 2) / N
    def fillet(V, e1, e2, r):
        """corner V between unit directions e1, e2: tangent points and bezier handle length for radius r"""
        th = math.acos(max(-1, min(1, e1[0] * e2[0] + e1[1] * e2[1])))
        tl = r / math.tan(th / 2); k = 4 / 3 * math.tan((math.pi - th) / 4) * r
        return (V[0] + e1[0] * tl, V[1] + e1[1] * tl), (V[0] + e2[0] * tl, V[1] + e2[1] * tl), k
    VR = (xr, ycross(xr)); VL = (xl, ycross(xl)); y0 = ycross(x0)
    Rs, Rl, kR = fillet(VR, (0, 1), du, d['fr'])                 # small fillet in the obtuse corner on the right
    Ll = (VL[0] - du[0] * d['fl'], VL[1] - du[1] * d['fl'])      # left: one concave sweep from the lip down to the neck
    inn = lambda p: (p[0] + NU[0] * 45, p[1] + NU[1] * 45)
    up = lambda p: (p[0] + NU[0] * 1.5, p[1] + NU[1] * 1.5)
    rb = d['rb']; yb = y0 + d['ln']; yc = yb - rb; yn = y0 + (yc - y0) * 0.56
    xn = x0 + d['sway'] * 0.55; xc = x0 + d['sway']; wn = d['wn']
    nr, nl = xn + wn / 2, xn - wn / 2
    Rl2, Ll2 = up(Rl), up(Ll)
    path = (f'M{inn(Rl2)[0]:.1f},{inn(Rl2)[1]:.1f} L{Rl2[0]:.1f},{Rl2[1]:.1f} '
            f'C{Rl[0] - du[0] * kR:.1f},{Rl[1] - du[1] * kR:.1f} {Rs[0]:.1f},{Rs[1] - kR:.1f} {Rs[0]:.1f},{Rs[1]:.1f} '
            f'C{xr:.1f},{Rs[1] + (yn - Rs[1]) * 0.5:.1f} {nr:.1f},{yn - (yn - Rs[1]) * 0.3:.1f} {nr:.1f},{yn:.1f} '
            f'C{nr:.1f},{yn + (yc - yn) * 0.5:.1f} {xc + rb:.1f},{yc - rb * 0.8:.1f} {xc + rb:.1f},{yc:.1f} '
            f'A{rb:.1f},{rb:.1f} 0 0 1 {xc - rb:.1f},{yc:.1f} '
            f'C{xc - rb:.1f},{yc - rb * 0.8:.1f} {nl:.1f},{yn + (yc - yn) * 0.5:.1f} {nl:.1f},{yn:.1f} '
            f'C{nl:.1f},{yn - (yn - Ll[1]) * 0.6:.1f} {Ll[0] + du[0] * d["fl"] * 0.75:.1f},{Ll[1] + du[1] * d["fl"] * 0.75:.1f} {Ll2[0]:.1f},{Ll2[1]:.1f} '
            f'L{inn(Ll2)[0]:.1f},{inn(Ll2)[1]:.1f} Z')
    defs = (f'<clipPath id="dc"><path d="{path}"/></clipPath>'
            f'<clipPath id="dr"><path d="M{x0 - 4:.1f},0 H1000 V1000 H0 V{yn:.1f} H{x0 - 4:.1f} Z"/></clipPath>')
    hx, hy = xc - rb * 0.4, yc - rb * 0.32
    body = (f'<path d="{path}" fill="{LIPC}"/>'
            f'<g clip-path="url(#dc)"><path d="{path}" fill="{DRIPSH}" clip-path="url(#dr)"/>'
            f'<path d="{path}" transform="translate({-DSH:.1f},{-DSH * 0.45:.1f})" fill="{LIPC}"/></g>'
            f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="{rb * 0.2:.1f}" ry="{rb * 0.36:.1f}" transform="rotate(28 {hx:.1f} {hy:.1f})" fill="#FFFFFF" fill-opacity=".85"/>')
    return body, defs, (tnear(Ll), tnear(Rl))


if __name__ == '__main__':
    render(build(), OUT + 'tier_slash' + ('_' + VAR if VAR else ''))
