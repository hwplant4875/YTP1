"""846 "RETAKE WALL MARIA" OPERATION: 250,000 refugees marched out of Trost's outer gate and swallowed by titans.
EP1 shot 10, THE key 3D scene (HANDOFF 17:41). Seen from the sky by one moving camera, ~18 s of video.

Everything is a pure function of the video time t (seconds, 0 .. T_END):
    setup()           once per Blender session: simulates the whole story on a 0.1 s grid with vectorized numpy
                      (column slots, panic, flight, titan hunting, kills, wagons, dust) and builds the instancers
    update(t, cam)    every frame: interpolates the grid, picks LODs by camera distance and writes vertex positions /
                      point attributes of a few point-cloud meshes that geometry nodes instance (fast in Cycles/Eevee)
    alive(t)          number shown by the counter overlay (250,000 -> ~100); also written to a JSON sidecar
    cam_at(t)         the one-take camera (loc, look-at, lens); CAM_IN / CAM_OUT = boundary keys + velocities for the
                      flight bridges (in: after the Trost/Rose scenes of 846; out: rising north over Wall Rose)

Story (video seconds):
    0-3    camera low over Trost just inside the outer gate: the avenue is a packed river of people pouring out of the
           gate onto the plain (on foot, handcarts, horse wagons, a thin escort of Scouts / Garrison in cloaks, riders)
    3-8    the camera rises and travels south along the column that stretches km over the lost Maria territory;
           titans become visible on the horizon ahead and on both flanks
    6-12   waves hit: the head first, then both flanks, then the rear by the wall; panic ripples along the column,
           people break off sideways, wagons overturn, figures are grabbed and gone (lifted to the mouth, no gore),
           dust rises; pockets get encircled
    12-15  the column thins into islands and vanishes
    15-18  high over the emptied plain: ~100 stragglers stumble back toward the gate, titans wander; the camera rises
           and turns north toward Trost / Wall Rose
Agents: N_PEOPLE (default 60,000; each stands for ~4 people) + N_WAGONS carts/wagons + N_TITANS (default 420, 4-15 m).
LOD per frame by camera distance: near (< 230 m) minimal posed figures (two walk poses, panic pose, cloaked soldiers,
tool carriers, riders), mid (< 750 m) two-tone capsules, far tiny boxes; far figures are drawn larger than life (x1..4)
so the column still reads from 600 m.

Gate: Trost's outer gate (trost.OUTER_GATE, gate heading south). Override with MARCH_GATE="x,y" and
MARCH_GATE_HEADING=<deg of the outward direction, -90 = south>. Without the Trost set (AOT_SET=march846) a placeholder
wall + flush gatehouse is built (build_set below).
Env: MARCH_N, MARCH_WAGONS, MARCH_TITANS, MARCH_SEED, MARCH_TEND.
"""
import math, os, sys, time, json, random
import numpy as np
import bpy, bmesh
from mathutils import Vector

import aotlib as L

E = os.environ.get
SEED = int(E("MARCH_SEED", "846"))
T_END = float(E("MARCH_TEND", "18.0"))
DT = 0.1
N_PEOPLE = int(E("MARCH_N", "60000"))
N_WAGONS = int(E("MARCH_WAGONS", "1600"))
N_TITANS = int(E("MARCH_TITANS", "420"))
N_SURV = 100
TOTAL = 250000
LIFT = 0.6                  # grabbed -> gone (video seconds)
T_RET = 10.5                # stragglers turn back
T_DOOM = 13.0               # whoever is still out there after this is taken by T_DOOM + 1.8
STATE = {}

# ---------------------------------------------------------------- gate + road
def _gate():
    tr = sys.modules.get("trost")
    if E("MARCH_GATE"):
        x, y = map(float, E("MARCH_GATE").split(","))
    elif tr is not None:
        x, y = tr.OUTER_GATE
    else:
        x, y = L.OUTER_GATE
    return np.array([x, y], float), math.radians(float(E("MARCH_GATE_HEADING", "-90")))

GATE, HEADING = _gate()
FWD = np.array([math.cos(HEADING), math.sin(HEADING)])      # outward (onto the plain)
RGT = np.array([-FWD[1], FWD[0]])                            # lateral axis of the road formula
S_IN = 860.0                                                 # queue depth inside the town that is drawn

def _road_polyline():
    """(x, y) samples from deep inside the town (s < 0) through the gate (s = 0) out onto the plain (s > 0)."""
    tr = sys.modules.get("trost")
    inside = []
    if tr is not None and not E("MARCH_GATE"):
        av = [np.array(p, float) for p in tr.AVENUE]           # outer gate -> inner gate
        inside = av[::-1]
    else:
        inside = [GATE - FWD * d for d in np.arange(S_IN + 40, 2, -6.0)]
    out = []
    for k in np.arange(0.0, 52.0, 0.05):                      # same formula as trost.py's "RoadOut" strip
        lat = math.sin(k / 7) * 90 * (k / 30)
        out.append(GATE + FWD * (k * 120.0) + RGT * lat)
    P = np.array(inside + out)
    seg = np.hypot(*np.diff(P, axis=0).T)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    s -= s[len(inside)]                                        # s = 0 at the gate
    # resample every 2 m
    S = np.arange(math.ceil(s[0]), s[-1], 2.0)
    X = np.interp(S, s, P[:, 0]); Y = np.interp(S, s, P[:, 1])
    # smooth the polyline corners (5-tap)
    for _ in range(6):
        X[1:-1] = 0.25 * X[:-2] + 0.5 * X[1:-1] + 0.25 * X[2:]
        Y[1:-1] = 0.25 * Y[:-2] + 0.5 * Y[1:-1] + 0.25 * Y[2:]
    TX = np.gradient(X); TY = np.gradient(Y); n = np.hypot(TX, TY) + 1e-9
    return S, X, Y, TX / n, TY / n

RS, RX, RY, RTX, RTY = _road_polyline()

def road(s):
    """s (array) -> x, y, tx, ty on the road centre line."""
    return (np.interp(s, RS, RX), np.interp(s, RS, RY), np.interp(s, RS, RTX), np.interp(s, RS, RTY))

def width(s):
    s = np.asarray(s, float)
    wp = 58.0 + 16.0 * np.sin(s / 280.0 + 1.0) + 8.0 * np.sin(s / 97.0)
    u = np.clip((s - 6.0) / 220.0, 0.0, 1.0); u = u * u * (3 - 2 * u)
    return np.where(s < -6.0, 12.0, np.where(s < 6.0, 10.0, 10.0 + (wp - 10.0) * u))

# column advance D(t): flow speed ramps up (timelapse), stalls once the titans hit
V0, V1, V2 = 70.0, 330.0, 25.0
KS = 0.38                   # the head walks faster -> the column stretches
T_TAIL = 8.6                # the last of them leave the gate
_TF = np.arange(0.0, T_END + 2.0, 0.01)

def _sm(a, b, t):
    u = np.clip((np.asarray(t, float) - a) / (b - a), 0.0, 1.0); return u * u * (3 - 2 * u)

_VF = V0 + (V1 - V0) * _sm(0.0, 5.0, _TF) - (V1 - V2) * _sm(7.0, 10.5, _TF)
D0 = 650.0 / (1 + KS)
_DF = D0 + np.concatenate([[0.0], np.cumsum(0.5 * (_VF[1:] + _VF[:-1]) * 0.01)])
def D(t):
    return np.interp(t, _TF, _DF)
LC = float(D(T_TAIL)) - 30.0

def slot_s(q, t, spd):
    return D(t) * (1 + KS * (1 - q)) * spd - LC * q

def slot_xy(q, u, t, spd, wob):
    s = slot_s(q, t, spd)
    x, y, tx, ty = road(s)
    w = width(s) * 0.5
    lat = u * w + wob * np.sin(t * 1.7 + q * 9000.0)
    return x - ty * lat, y + tx * lat, s, tx, ty

# ---------------------------------------------------------------- walls / district (titans stay outside)
def _district():
    tr = sys.modules.get("trost")
    if tr is not None and not E("MARCH_GATE"):
        return dict(W=tr.W, S=tr.S, R=tr.R)
    return None

DIST = _district()

def push_out(x, y, margin=12.0):
    """Push points out of the walled district (vectorized). Rose itself (y > 0) is closed too."""
    if DIST is None:
        a = (x - GATE[0]) * FWD[0] + (y - GATE[1]) * FWD[1]
        bad = a < margin
        x = np.where(bad, x + FWD[0] * (margin - a), x); y = np.where(bad, y + FWD[1] * (margin - a), y)
        return x, y
    W, S, R = DIST["W"], DIST["S"], DIST["R"]
    cy = -S
    y = np.minimum(y, -margin)                                   # Wall Rose (y = 0): its interior is closed
    strip = (y >= cy) & (np.abs(x) < W + margin)                 # beside the straight sides of the bulge
    x = np.where(strip, np.sign(x + 1e-9) * (W + margin), x)
    dx, dy = x, y - cy
    d = np.hypot(dx, dy) + 1e-6
    rnd_ = (y < cy) & (d < R + margin)                           # the round end
    k = (R + margin) / d
    x = np.where(rnd_, dx * k, x); y = np.where(rnd_, cy + dy * k, y)
    return x, y

# ---------------------------------------------------------------- ground height (bilinear on the terrain mesh grid)
GROUND = {}
def ground_setup():
    ob = bpy.data.objects.get("Terrain")
    if ob is not None and len(ob.data.vertices) == 321 * 321:
        co = np.empty(len(ob.data.vertices) * 3, np.float32); ob.data.vertices.foreach_get("co", co)
        co = co.reshape(321, 321, 3)
        GROUND.update(xs=co[:, 0, 0].astype(float), ys=co[0, :, 1].astype(float), z=co[:, :, 2].astype(float))
    else:
        xs = np.linspace(-6000, 6000, 241); ys = np.linspace(-9000, 3000, 241)
        z = np.array([[L.height(x, y) for y in ys] for x in xs])
        GROUND.update(xs=xs, ys=ys, z=z)

def ground(x, y):
    xs, ys, z = GROUND["xs"], GROUND["ys"], GROUND["z"]
    i = np.clip(np.searchsorted(xs, x) - 1, 0, len(xs) - 2); j = np.clip(np.searchsorted(ys, y) - 1, 0, len(ys) - 2)
    fx = np.clip((x - xs[i]) / (xs[i + 1] - xs[i]), 0, 1); fy = np.clip((y - ys[j]) / (ys[j + 1] - ys[j]), 0, 1)
    return (z[i, j] * (1 - fx) * (1 - fy) + z[i + 1, j] * fx * (1 - fy) + z[i, j + 1] * (1 - fx) * fy + z[i + 1, j + 1] * fx * fy)

# ---------------------------------------------------------------- palettes (linear RGB)
SHIRTS = [(0.80, 0.07, 0.05), (0.05, 0.18, 0.75), (0.92, 0.68, 0.04), (0.08, 0.48, 0.12), (0.88, 0.88, 0.82),
          (0.92, 0.32, 0.04), (0.42, 0.10, 0.58), (0.03, 0.50, 0.52), (0.88, 0.32, 0.50), (0.30, 0.62, 0.92),
          (0.60, 0.80, 0.10), (0.70, 0.12, 0.25), (0.55, 0.40, 0.22), (0.62, 0.55, 0.42), (0.35, 0.22, 0.12)]
PANTS = [(0.10, 0.06, 0.03), (0.04, 0.05, 0.14), (0.20, 0.20, 0.22), (0.40, 0.30, 0.17), (0.30, 0.10, 0.06)]
HAIRS = [(0.02, 0.016, 0.012), (0.12, 0.06, 0.03), (0.55, 0.40, 0.12), (0.45, 0.12, 0.04), (0.50, 0.50, 0.50)]
CLOAK_SCOUT = (0.045, 0.16, 0.06)
CLOAK_GARRISON = (0.03, 0.05, 0.11)       # dark navy cloak, red rose patch is too small to read from the sky

# ---------------------------------------------------------------- simulation
def _smooth(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)

def simulate():
    t_start = time.time()
    rng = np.random.default_rng(SEED)
    K = int(round(T_END / DT)) + 1
    N, NW, NT = N_PEOPLE, N_WAGONS, N_TITANS
    # ---- people attributes
    q = np.sort(rng.random(N)); u = rng.uniform(-1, 1, N) * 0.97
    spd = 1.0 + rng.normal(0, 0.012, N)
    wob = rng.uniform(0.2, 1.2, N)
    kind = np.zeros(N, np.int8)                         # 0 civilian, 1 scout, 2 garrison, 3 rider, 4 civilian w/ tool
    kind[rng.random(N) < 0.22] = 4
    ns = int(N * 0.012)
    esc = rng.choice(N, ns, replace=False)
    kind[esc] = np.where(rng.random(ns) < 0.6, 1, 2)
    u[esc] = np.sign(u[esc] + 1e-6) * rng.uniform(1.02, 1.22, ns)          # escort walks the flanks
    nr = max(40, N // 400)
    rid = rng.choice(np.where(kind == 0)[0], nr, replace=False)
    kind[rid] = 3; u[rid] = np.sign(u[rid] + 1e-6) * rng.uniform(1.25, 1.5, nr)
    head = np.where(q < 0.004)[0]; kind[head[: len(head) // 2]] = 3       # mounted Scouts lead the column
    hgt = np.where(rng.random(N) < 0.1, rng.uniform(1.05, 1.35, N), rng.uniform(1.55, 1.9, N))
    hgt[kind == 3] = 1.75
    # ---- stragglers who make it back: from the rear half of the column
    cand = np.where((kind == 0) & (q > 0.62) & (q < 0.97))[0]
    surv = np.zeros(N, bool); surv[rng.choice(cand, N_SURV, replace=False)] = True
    # ---- wagons
    wq = np.sort(rng.random(NW)); wu = rng.uniform(-0.8, 0.8, NW); wkind = (rng.random(NW) < 0.45).astype(np.int8)  # 1 = horse wagon
    wspd = 1.0 + rng.normal(0, 0.008, NW)
    w_to = np.full(NW, np.inf); w_roll = rng.choice([-1.0, 1.0], NW) * rng.uniform(1.35, 1.75, NW)

    # ---- titans: waves, spawned so they reach the column around their contact time
    NA, NB, NC = int(NT * 0.26), int(NT * 0.29), int(NT * 0.29)
    ND = NT - NA - NB - NC
    wave = np.array([0] * NA + [1] * NB + [2] * NC + [3] * ND)
    H = np.clip(rng.gamma(5.0, 1.75, NT), 4.0, 15.0)
    abn = rng.random(NT) < 0.1
    vt = np.where(abn, rng.uniform(300, 380, NT), rng.uniform(150, 250, NT))
    tst = np.select([wave == 0, wave == 1, wave == 2, wave == 3],
                    [rng.uniform(0.5, 2.5, NT), rng.uniform(2.5, 5.0, NT), rng.uniform(3.0, 5.5, NT), rng.uniform(5.5, 8.0, NT)])
    tcon = np.select([wave == 0, wave == 1, wave == 2, wave == 3],
                     [rng.uniform(6.0, 7.5, NT), rng.uniform(7.2, 9.5, NT), rng.uniform(7.6, 10.0, NT), rng.uniform(9.0, 11.0, NT)])
    TXY = np.zeros((NT, 2))
    for j in range(NT):
        tc = tcon[j]
        sh = float(D(tc) * (1 + KS)); stl = max(60.0, float(D(tc) - LC))
        if wave[j] == 0:
            s = sh - rng.uniform(0, 500); side = rng.uniform(-1, 1)
        elif wave[j] == 3:
            s = rng.uniform(80, 1100); side = rng.choice([-1, 1])
        else:
            s = rng.uniform(stl + 100, sh); side = 1.0 if wave[j] == 1 else -1.0
        x, y, tx, ty = road(np.array([s]))
        p = np.array([x[0], y[0]])
        fw = np.array([tx[0], ty[0]]); nm = np.array([-ty[0], tx[0]])
        dist = vt[j] * 0.55 * (tc - tst[j]) + rng.uniform(150, 600)
        if wave[j] == 0:
            ang = side * 0.9
            d = fw * math.cos(ang) + nm * math.sin(ang)
        else:
            ang = rng.uniform(-0.45, 0.45)
            d = nm * side * math.cos(ang) + fw * math.sin(ang)
        TXY[j] = p + d * dist
    TXY[:, 0], TXY[:, 1] = push_out(TXY[:, 0], TXY[:, 1], 40.0)
    tyaw = np.arctan2(-(GATE[0] - TXY[:, 0]), GATE[1] - TXY[:, 1])         # facing roughly toward the column
    Rk = 6.0 + 1.4 * H
    Rf = 70.0 + 4.0 * H
    rate = 14.0 + 3.0 * H                                # grabs per video second (timelapse: each agent ~ 4 people)

    # ---- outputs
    PX = np.zeros((K, N), np.float32); PY = np.zeros((K, N), np.float32)
    TXk = np.zeros((K, NT), np.float32); TYk = np.zeros((K, NT), np.float32); TYAWk = np.zeros((K, NT), np.float32)
    TGR = np.full((K, NT), -100.0, np.float32)          # start time of the current / last grab
    TSPD = np.zeros((K, NT), np.float32)
    mode = np.zeros(N, np.int8)                         # 0 march, 1 flee, 2 dead, 3 retreat
    td = np.full(N, np.inf); tf = np.full(N, np.inf); vj = np.full(N, -1, np.int32)
    pos = np.zeros((N, 2)); fdir = np.zeros((N, 2)); vf = rng.uniform(22, 45, N)
    vr = rng.uniform(55, 95, N)
    rdir = rng.normal(0, 1, (N, 2)); rdir /= np.linalg.norm(rdir, axis=1, keepdims=True)
    ret_goal = GATE[None, :] + FWD[None, :] * rng.uniform(30, 90, (N, 1)) + RGT[None, :] * rng.uniform(-35, 35, (N, 1))
    grab = np.full(NT, -100.0)
    dust = []                                           # (t0, x, y, size, dur, alpha)
    foot_next = rng.uniform(0, 0.5, NT)
    doom_td = None
    C = 40.0
    stats = []
    for k in range(K):
        t = k * DT
        # ---------------- marchers on their slots
        m0 = mode == 0
        x, y, s, tx, ty = slot_xy(q[m0], u[m0], t, spd[m0], wob[m0])
        pos[m0, 0] = x; pos[m0, 1] = y
        s_all = np.full(N, 1e9); s_all[m0] = s
        outside = (mode != 0) | (s_all > 4.0)
        alive = mode != 2
        # ---------------- titans move
        act = t >= tst
        if k > 0:
            cand_idx = np.where(alive & outside & ~surv)[0]
            if len(cand_idx):
                sub = cand_idx if len(cand_idx) <= 3500 else rng.choice(cand_idx, 3500, replace=False)
                P = pos[sub]
                dd = (TXY[:, None, 0] - P[None, :, 0]) ** 2 + (TXY[:, None, 1] - P[None, :, 1]) ** 2
                nn = np.argmin(dd, axis=1)
                tgt = P[nn]; dist = np.sqrt(dd[np.arange(NT), nn])
            else:                                      # nobody left: wander toward the gate / mill around
                tgt = GATE[None, :] + FWD[None, :] * 400 + RGT[None, :] * (np.sin(np.arange(NT) * 1.7) * 900)[:, None]
                dist = np.hypot(*(tgt - TXY).T)
            dvec = tgt - TXY
            dn = dvec / (np.linalg.norm(dvec, axis=1, keepdims=True) + 1e-6)
            feeding = dist < Rk * 0.9
            sp = np.where(feeding, 0.22, 1.0) * vt
            sp = np.where(len(cand_idx) == 0, 0.08 * vt, sp)
            sp = np.minimum(sp, dist / DT * 0.9 + 2.0)
            vel = dn * sp[:, None]
            # separation
            dx = TXY[:, None, 0] - TXY[None, :, 0]; dy = TXY[:, None, 1] - TXY[None, :, 1]
            dr = np.hypot(dx, dy) + np.eye(NT) * 1e6
            mind = 0.55 * (H[:, None] + H[None, :])
            push = np.clip((mind - dr) / mind, 0, 1)
            vel[:, 0] += (push * dx / dr).sum(1) * 60.0; vel[:, 1] += (push * dy / dr).sum(1) * 60.0
            vel[~act] *= 0.0
            newp = TXY + vel * DT
            newp[:, 0], newp[:, 1] = push_out(newp[:, 0], newp[:, 1], 25.0)
            mv = newp - TXY
            spd_t = np.hypot(*mv.T) / DT
            want = np.arctan2(-mv[:, 0], mv[:, 1])
            dyaw = (want - tyaw + np.pi) % (2 * np.pi) - np.pi
            tyaw = np.where(spd_t > 3.0, tyaw + np.clip(dyaw, -0.6, 0.6), tyaw)
            TXY = newp
            TSPD[k] = spd_t
            # footfall dust
            for j in np.where(act & (spd_t > 20) & (t >= foot_next))[0]:
                dust.append((t, TXY[j, 0], TXY[j, 1], 2.5 + 0.55 * H[j], 2.0, 0.45))
                foot_next[j] = t + rng.uniform(0.35, 0.6)
        TXk[k] = TXY[:, 0]; TYk[k] = TXY[:, 1]; TYAWk[k] = tyaw
        # ---------------- fear + kills (agent grid)
        elig = np.where(alive & outside)[0]
        rep = np.zeros((N, 2)); repn = np.zeros(N)
        newly_dead = []
        if len(elig) and k > 0:
            gx = np.floor(pos[elig, 0] / C).astype(np.int64); gy = np.floor(pos[elig, 1] / C).astype(np.int64)
            key = gx * 100003 + gy
            order = np.argsort(key, kind="stable"); ks = key[order]
            for j in np.where(act)[0]:
                cx, cy = TXY[j]
                r = Rf[j]
                ix0, ix1 = int(math.floor((cx - r) / C)), int(math.floor((cx + r) / C))
                iy0, iy1 = int(math.floor((cy - r) / C)), int(math.floor((cy + r) / C))
                idx = []
                for ix in range(ix0, ix1 + 1):
                    a = np.searchsorted(ks, ix * 100003 + iy0); b = np.searchsorted(ks, ix * 100003 + iy1, side="right")
                    if b > a:
                        idx.append(order[a:b])
                if not idx:
                    continue
                ii = elig[np.concatenate(idx)]
                ii = ii[mode[ii] != 2]
                if not len(ii):
                    continue
                d = np.hypot(pos[ii, 0] - cx, pos[ii, 1] - cy) + 1e-3
                near = d < r
                ii, d = ii[near], d[near]
                if not len(ii):
                    continue
                w = (1 - d / r)
                np.add.at(rep, ii, ((pos[ii] - TXY[j]) / d[:, None]) * w[:, None])
                np.add.at(repn, ii, w)
                # grabs
                kk = (d < Rk[j]) & ~surv[ii]
                if kk.any():
                    cap = rate[j] * DT
                    n = int(cap) + (1 if rng.random() < cap - int(cap) else 0)
                    if n:
                        ci = ii[kk][np.argsort(d[kk])[:n]]
                        mode[ci] = 2; td[ci] = t; vj[ci] = j
                        newly_dead.append(ci)
                        if t - grab[j] > 1.1:
                            grab[j] = t
                            fx = TXY[j] + np.array([-math.sin(tyaw[j]), math.cos(tyaw[j])]) * H[j] * 0.3
                            dust.append((t, fx[0], fx[1], 3.0 + 0.35 * H[j], 1.5, 0.35))
        TGR[k] = grab
        # ---------------- panic: titans near, or contagion through the crowd
        scared = (repn > 0) & ((mode == 0) | (mode == 1))
        startle = scared & (mode == 0)
        if k > 0:
            fle = np.where(((mode == 1) & (tf > t - 1.2)) | (td == t))[0]
            if len(fle):
                pk = np.unique(np.floor(pos[fle, 0] / C).astype(np.int64) * 100003 + np.floor(pos[fle, 1] / C).astype(np.int64))
                pk = np.unique((pk[:, None] + np.array([o1 * 100003 + o2 for o1 in (-1, 0, 1) for o2 in (-1, 0, 1)])[None, :]).ravel())
                mi = np.where((mode == 0) & outside)[0]
                mk = np.floor(pos[mi, 0] / C).astype(np.int64) * 100003 + np.floor(pos[mi, 1] / C).astype(np.int64)
                hit = mi[np.isin(mk, pk) & (rng.random(len(mi)) < 0.06)]
                startle[hit] = True
        st = np.where(startle)[0]
        if len(st):
            mode[st] = np.where(surv[st], 3, 1); tf[st] = t
            # break off sideways (away from the column axis), a bit backward
            sx, sy, stx, sty = road(slot_s(q[st], t, spd[st]))
            side = np.sign(u[st] + rng.normal(0, 0.3, len(st)))
            fdir[st, 0] = -sty * side * 0.8 - stx * 0.3 + rdir[st, 0] * 0.4
            fdir[st, 1] = stx * side * 0.8 - sty * 0.3 + rdir[st, 1] * 0.4
        # stragglers turn back
        if t >= T_RET:
            rr = np.where(surv & (mode != 3) & (mode != 2) & outside)[0]
            mode[rr] = 3; tf[rr] = np.minimum(tf[rr], t)
        # wagons overturn when a titan is close or the crowd around them panics
        if k > 0:
            wm = np.isinf(w_to)
            if wm.any():
                wi = np.where(wm)[0]
                wx, wy, ws, _, _ = slot_xy(wq[wi], wu[wi], t, wspd[wi], np.zeros(len(wi)))
                okw = ws > 4.0
                wi, wx, wy = wi[okw], wx[okw], wy[okw]
                if len(wi):
                    dd = (wx[:, None] - TXY[None, act, 0]) ** 2 + (wy[:, None] - TXY[None, act, 1]) ** 2 if act.any() else None
                    if dd is not None:
                        hitw = (dd < (1.7 * Rk[act][None, :]) ** 2).any(1)
                        panicw = (dd < (Rf[act][None, :] * 0.8) ** 2).any(1) & (rng.random(len(wi)) < 0.08)
                        fl = wi[hitw | panicw]
                        w_to[fl] = t
                        for a in fl[:: max(1, len(fl) // 30)]:
                            xx, yy, _, _, _ = slot_xy(wq[a:a + 1], wu[a:a + 1], t, wspd[a:a + 1], np.zeros(1))
                            dust.append((t, xx[0], yy[0], 9.0, 2.6, 0.5))
        # ---------------- move fleeing / retreating people
        m1 = np.where(mode == 1)[0]
        if len(m1):
            rv = rep[m1]; rn = np.linalg.norm(rv, axis=1)
            has = rn > 1e-6
            new = fdir[m1].copy()
            new[has] = 0.45 * new[has] / (np.linalg.norm(new[has], axis=1, keepdims=True) + 1e-6) + rv[has] / rn[has, None]
            g = GATE[None, :] - pos[m1]; g /= np.linalg.norm(g, axis=1, keepdims=True) + 1e-6
            new += 0.12 * g + 0.15 * rdir[m1]
            new /= np.linalg.norm(new, axis=1, keepdims=True) + 1e-6
            fdir[m1] = new
            age = t - tf[m1]
            v = vf[m1] * np.where(has, 1.0, 0.55) * np.clip(0.4 + age * 2.0, 0.4, 1.0) * np.exp(-age / 3.5)
            pos[m1] += new * (v * DT)[:, None]
            pos[m1, 0], pos[m1, 1] = push_out(pos[m1, 0], pos[m1, 1], 6.0)
        m3 = np.where(mode == 3)[0]
        if len(m3):
            g = ret_goal[m3] - pos[m3]; gd = np.linalg.norm(g, axis=1)
            dirr = g / (gd[:, None] + 1e-6)
            zig = np.stack([-dirr[:, 1], dirr[:, 0]], 1) * (0.35 * np.sin(t * 2.3 + np.arange(len(m3)) * 1.3))[:, None]
            stumble = 0.45 + 0.55 * np.abs(np.sin(t * 2.9 + m3 * 0.37))
            v = vr[m3] * stumble * np.clip(gd / 40.0, 0.0, 1.0)
            pos[m3] += (dirr + zig) * (v * DT)[:, None]
        # ---------------- the end: nobody else gets away
        if t >= T_DOOM and doom_td is None:
            rest = np.where((mode != 2) & ~surv)[0]
            doom_td = np.full(N, np.inf)
            if len(rest):
                dd = (pos[rest, None, 0] - TXY[None, :, 0]) ** 2 + (pos[rest, None, 1] - TXY[None, :, 1]) ** 2
                nn = np.argmin(dd, axis=1); dmin = np.sqrt(dd[np.arange(len(rest)), nn])
                rk = np.argsort(np.argsort(dmin)) / max(1, len(rest) - 1)
                doom_td[rest] = t + 0.1 + rk * 2.1
                vj[rest] = np.where(dmin < 4.0 * Rk[nn], nn, -1)     # far from any titan: just gone
        if doom_td is not None:
            dn_ = np.where((doom_td <= t) & (mode != 2))[0]
            mode[dn_] = 2; td[dn_] = t
        PX[k] = pos[:, 0]; PY[k] = pos[:, 1]
        # march dust: kicked up along the moving column
        if t < 10.0:
            mi = np.where((mode == 0) & (s_all > 30))[0]
            if len(mi):
                for a in rng.choice(mi, min(14, len(mi)), replace=False):
                    dust.append((t, pos[a, 0], pos[a, 1], 11.0, 2.4, 0.11))
        stats.append((t, int((mode != 2).sum()), int((mode == 1).sum()), int((mode == 2).sum())))
    # ---- alive table for the counter
    tt = np.arange(K) * DT
    nons = ~surv
    alive_ns = np.array([(td[nons] > ti).sum() for ti in tt])
    shown = N_SURV + (TOTAL - N_SURV) * alive_ns / nons.sum()
    D_ = np.array(dust, float) if dust else np.zeros((0, 6))
    print(f"[march846] sim {time.time() - t_start:.1f}s  people {N} wagons {NW} titans {NT} dust {len(D_)}  "
          + "  ".join(f"t{a:.0f}:alive{b}/flee{c}" for a, b, c, _ in stats[::20]))
    STATE.update(K=K, N=N, NW=NW, NT=NT, q=q, u=u, spd=spd, wob=wob, kind=kind, hgt=hgt, surv=surv,
                 PX=PX, PY=PY, td=td, tf=tf, vj=vj, wq=wq, wu=wu, wspd=wspd, wkind=wkind, w_to=w_to, w_roll=w_roll,
                 TX=TXk, TY=TYk, TYAW=TYAWk, TGR=TGR, TSPD=TSPD, H=H, abn=abn, dust=D_, alive_t=tt, alive_v=shown,
                 sim_s=time.time() - t_start)

def alive(t):
    """Counter value at video time t (250,000 -> ~100). Needs setup() (or load_alive())."""
    if "alive_t" not in STATE:
        return TOTAL
    return int(round(float(np.interp(t, STATE["alive_t"], STATE["alive_v"]))))

def write_alive_json(path, fps=30.0):
    n = int(round(T_END * fps)) + 1
    rec = {"segment": "march846", "fps": fps, "total": TOTAL, "end": N_SURV,
           "frames": [{"i": i, "t": round(i / fps, 4), "alive": alive(i / fps)} for i in range(n)]}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(rec, f)
    return path

# ---------------------------------------------------------------- prototypes (meshes instanced by geometry nodes)
def _inst_mat(name, attr, rough=0.75, fallback=(0.5, 0.5, 0.5)):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*fallback, 1); b.inputs["Roughness"].default_value = rough
    a = nt.nodes.new("ShaderNodeAttribute"); a.attribute_type = "INSTANCER"; a.attribute_name = attr
    nt.links.new(a.outputs["Color"], b.inputs["Base Color"])
    return m

def _mesh_from(name, V, F, fmat, mats):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in V], [], F)
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", np.asarray(fmat, np.int32))
    me.update()
    return me

def _person_proto(name, pose, mats, cloak=False, tool=False, dress=False):
    import swarm845 as SW
    g = SW.Geo()
    s = 1.0
    SW.person_geo(g, 0, 1.7, dress, random.Random(1))
    hip = 0.82
    if cloak:   # cloak hanging from the shoulders down the back (cat 4)
        g.box((0, -0.17, 0.98), (0.50, 0.05, 0.80), 4, 0, 0, hip=hip, taper=0.78)
        g.box((0, -0.05, 1.37), (0.46, 0.26, 0.07), 4, 0, 0, hip=hip)
    if tool:    # pitchfork / spear over the shoulder (cat 5)
        g.box((0.22, -0.05, 1.25), (0.05, 0.05, 1.9), 5, 0, 4, (0, 1.36), (0, 0), hip)
    R = g.finish()
    Ar = np.zeros((1, 7)); Ae = np.zeros((1, 7)); lean = np.zeros(1)
    if pose == "a":
        Ar[0, 1], Ar[0, 2], Ar[0, 3], Ar[0, 4] = 0.55, -0.55, -0.5, 0.5
        lean[0] = -0.12
    elif pose == "b":
        Ar[0, 1], Ar[0, 2], Ar[0, 3], Ar[0, 4] = -0.55, 0.55, 0.5, -0.5
        lean[0] = -0.12
    elif pose == "panic":
        Ar[0, 1], Ar[0, 2] = 0.7, -0.7
        Ar[0, 3] = Ar[0, 4] = 2.6; Ae[0, 3] = Ae[0, 4] = 0.3; lean[0] = 0.05
    if tool:
        Ar[0, 4] = 0.0
    Ar[0, 5] = Ar[0, 4]; Ar[0, 6] = Ar[0, 3]
    V = SW._deform(R, Ar, Ae, lean, np.ones(1), np.zeros(1), np.zeros((1, 3)))
    me = _mesh_from(name, V, g.f, g.fc, mats)
    return bpy.data.objects.new(name, me)

def _bm_obj(name, bm, mats):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats:
        me.materials.append(m)
    return bpy.data.objects.new(name, me)

def build_protos():
    M = {}
    M["col"] = _inst_mat("MR_col", "col"); M["col2"] = _inst_mat("MR_col2", "col2", 0.85); M["hair"] = _inst_mat("MR_hair", "hair", 0.7)
    M["skin"] = L.mat("MR_skin", (0.78, 0.53, 0.40), 0.6)
    M["jacket"] = L.mat("MR_jacket", (0.42, 0.28, 0.13), 0.8)
    M["white"] = L.mat("MR_white", (0.80, 0.78, 0.72), 0.85)
    M["wood"] = L.mat("MR_wood", (0.30, 0.19, 0.09), 0.85)
    M["wood2"] = L.mat("MR_wood2", (0.20, 0.12, 0.06), 0.85)
    M["canvas"] = L.mat("MR_canvas", (0.78, 0.74, 0.62), 0.9)
    M["horse"] = L.mat("MR_horse", (0.28, 0.15, 0.07), 0.7)
    M["sack"] = L.mat("MR_sack", (0.55, 0.45, 0.30), 0.9)
    M["iron"] = L.mat("MR_iron", (0.35, 0.35, 0.36), 0.5)
    civ = [M["col"], M["col2"], M["skin"], M["hair"], M["col"], M["wood"]]
    sol = [M["jacket"], M["white"], M["skin"], M["hair"], M["col"], M["iron"]]
    coll = bpy.data.collections.new("MarchProtos")          # NOT linked to the scene: only instanced
    P = [
        _person_proto("P00_civA", "a", civ), _person_proto("P01_civB", "b", civ), _person_proto("P02_civPanic", "panic", civ),
        _person_proto("P03_solA", "a", sol, cloak=True), _person_proto("P04_solB", "b", sol, cloak=True),
    ]
    # P05 mid: two-tone capsule (body = shirt colour, head = hair colour)
    bm = bmesh.new()
    L.cyl(bm, (0, 0, 0.0), (0, 0, 1.38), 0.27, 0.22, seg=6, mi=0)
    sp = bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=4, radius=0.2)
    for v in sp["verts"]:
        v.co.z += 1.55
    for f in {f for v in sp["verts"] for f in v.link_faces}:
        f.material_index = 1
    P.append(_bm_obj("P05_mid", bm, [M["col"], M["hair"]]))
    # P06 far: tiny box
    bm = bmesh.new(); L.box(bm, (0, 0, 0.85), (0.6, 0.6, 1.7), mi=0)
    P.append(_bm_obj("P06_far", bm, [M["col"]]))
    # P07 rider: horse + cloaked rider
    bm = bmesh.new()
    L.box(bm, (0, 0, 1.25), (0.62, 1.7, 0.62), mi=0)                     # barrel
    L.box(bm, (0, 1.05, 1.62), (0.32, 0.55, 0.42), rot=0, mi=0)           # neck
    L.box(bm, (0, 1.38, 1.85), (0.26, 0.5, 0.26), mi=0)                   # head
    for xx in (-0.2, 0.2):
        for yy in (-0.62, 0.62):
            L.box(bm, (xx, yy, 0.47), (0.14, 0.14, 0.94), mi=0)
    L.box(bm, (0, -0.95, 1.0), (0.1, 0.12, 0.7), mi=4)                   # tail
    L.box(bm, (0, -0.05, 1.95), (0.42, 0.3, 0.68), mi=1)                  # rider torso (jacket)
    L.box(bm, (0, -0.22, 1.85), (0.5, 0.06, 0.8), mi=2)                   # cloak
    sp = bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=4, radius=0.14)
    for v in sp["verts"]:
        v.co += Vector((0, -0.05, 2.45))
    for f in {f for v in sp["verts"] for f in v.link_faces}:
        f.material_index = 3
    P.append(_bm_obj("P07_rider", bm, [M["horse"], M["jacket"], M["col"], M["hair"], M["wood2"]]))
    P.append(_person_proto("P08_civToolA", "a", civ, tool=True)); P.append(_person_proto("P09_civToolB", "b", civ, tool=True))
    for o in P:
        coll.objects.link(o)
    # wagons
    wcoll = bpy.data.collections.new("MarchWagonProtos")
    bm = bmesh.new()                                                       # W0 handcart with sacks
    L.box(bm, (0, 0, 0.75), (1.3, 2.0, 0.25), mi=0)
    L.box(bm, (0, 0, 0.98), (1.2, 1.9, 0.3), mi=0)
    for sx in (-1, 1):
        L.cyl(bm, (sx * 0.72, 0, 0.5), (sx * 0.82, 0, 0.5), 0.5, 0.5, seg=10, mi=1)
        L.box(bm, (sx * 0.45, 1.55, 0.85), (0.07, 1.4, 0.07), mi=1)
    for k in range(3):
        L.box(bm, ((k - 1) * 0.38, (k % 2) * 0.4 - 0.2, 1.3), (0.4, 0.55, 0.4), mi=2)
    W0 = _bm_obj("W00_cart", bm, [M["wood"], M["wood2"], M["sack"]])
    bm = bmesh.new()                                                       # W1 covered wagon + horse
    L.box(bm, (0, 0, 1.05), (1.7, 3.6, 0.35), mi=0)
    for sx in (-1, 1):
        for yy in (-1.25, 1.25):
            L.cyl(bm, (sx * 0.9, yy, 0.6), (sx * 1.0, yy, 0.6), 0.6, 0.6, seg=10, mi=1)
    seg = 8
    vs = []
    for yy in (-1.7, 1.7):
        ring = []
        for i in range(seg + 1):
            a = math.pi * i / seg
            ring.append(bm.verts.new((math.cos(a) * 0.9, yy, 1.25 + math.sin(a) * 1.0)))
        vs.append(ring)
    for i in range(seg):
        f = bm.faces.new((vs[0][i], vs[0][i + 1], vs[1][i + 1], vs[1][i])); f.material_index = 2
    L.box(bm, (0, 2.6, 0.85), (0.08, 1.8, 0.08), mi=1)                    # shaft
    L.box(bm, (0, 3.6, 1.25), (0.6, 1.6, 0.6), mi=3)                      # horse
    L.box(bm, (0, 4.55, 1.65), (0.3, 0.6, 0.4), mi=3)
    for xx in (-0.2, 0.2):
        for yy in (3.0, 4.15):
            L.box(bm, (xx, yy, 0.47), (0.14, 0.14, 0.94), mi=3)
    W1 = _bm_obj("W01_wagon", bm, [M["wood"], M["wood2"], M["canvas"], M["horse"]])
    wcoll.objects.link(W0); wcoll.objects.link(W1)
    return coll, wcoll

def _gn_instancer(name, coll, rot_attr=True):
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, Lk = ng.nodes, ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    sA = N.new("GeometryNodeInputNamedAttribute"); sA.data_type = "FLOAT"; sA.inputs["Name"].default_value = "s"
    cmp = N.new("ShaderNodeMath"); cmp.operation = "GREATER_THAN"; cmp.inputs[1].default_value = 0.001
    Lk.new(sA.outputs["Attribute"], cmp.inputs[0])
    iop = N.new("GeometryNodeInstanceOnPoints")
    Lk.new(gi.outputs[0], iop.inputs["Points"])
    Lk.new(cmp.outputs[0], iop.inputs["Selection"])
    ci = N.new("GeometryNodeCollectionInfo"); ci.transform_space = "ORIGINAL"
    ci.inputs["Collection"].default_value = coll
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    Lk.new(ci.outputs[0], iop.inputs["Instance"])
    iop.inputs["Pick Instance"].default_value = True
    lA = N.new("GeometryNodeInputNamedAttribute"); lA.data_type = "INT"; lA.inputs["Name"].default_value = "lod"
    Lk.new(lA.outputs["Attribute"], iop.inputs["Instance Index"])
    rA = N.new("GeometryNodeInputNamedAttribute"); rA.data_type = "FLOAT_VECTOR"; rA.inputs["Name"].default_value = "rot"
    e2r = N.new("FunctionNodeEulerToRotation")
    Lk.new(rA.outputs["Attribute"], e2r.inputs[0]); Lk.new(e2r.outputs[0], iop.inputs["Rotation"])
    Lk.new(sA.outputs["Attribute"], iop.inputs["Scale"])
    Lk.new(iop.outputs[0], go.inputs[0])
    return ng

def _point_cloud(name, n, attrs, ng, coll):
    me = bpy.data.meshes.new(name)
    me.vertices.add(n)
    for a, (typ, dom) in attrs.items():
        me.attributes.new(a, typ, dom)
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    md = ob.modifiers.new("Inst", "NODES"); md.node_group = ng
    return ob

# ---------------------------------------------------------------- titans (swarm845's minimal titan look)
def build_titans(coll):
    import swarm845 as SW
    S = STATE; rng = random.Random(SEED + 1)
    specs = []
    for j in range(S["NT"]):
        H = float(S["H"][j])
        g = rng.uniform(0.72, 1.05)
        if rng.random() < 0.12:
            g = rng.uniform(1.3, 1.75)                   # fat ones
        sp = dict(name=f"t{j}", H=H, g=g, al=rng.uniform(0.9, 1.25), hs=rng.uniform(0.85, 1.35),
                  skin=rng.randrange(len(SW.T_SKINS)), hair=rng.choice([None, 0, 1, 1, 2, 3]))
        if S["abn"][j]:
            sp["al"] *= 1.2; sp["hs"] *= 1.15
        specs.append(sp)
    gt = SW.Geo(); tmat = []
    for j, sp in enumerate(specs):
        n0 = len(gt.fc)
        sx, sh, la, hip, hc, hr = SW.titan_geo(gt, j, sp)
        sp.update(sx=sx, sh=sh, la=la, hip=hip, hc=hc, hr=hr)
        hb = len(SW.T_SKINS)
        base = [sp["skin"], hb + (sp["hair"] if sp.get("hair") is not None else 0), hb + len(SW.T_HAIRS)]
        tmat += [base[c] for c in gt.fc[n0:]]
    tm = [L.mat(f"MR_tskin{i}", c, 0.65) for i, c in enumerate(SW.T_SKINS)] + [L.mat(f"MR_thair{i}", c, 0.7) for i, c in enumerate(SW.T_HAIRS)] \
        + [L.mat("MR_teeth", (0.85, 0.80, 0.70), 0.5)]
    RT = gt.finish()
    tob = SW._mesh("MarchTitans", RT, gt.f, tmat, tm, coll)
    S.update(specs=specs, RT=RT, tob=tob)

# ---------------------------------------------------------------- dust
def _dust_mat():
    m = bpy.data.materials.new("MR_dust"); m.use_nodes = True
    nt = m.node_tree; N, Lk = nt.nodes, nt.links
    b = N["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.74, 0.66, 0.52, 1); b.inputs["Roughness"].default_value = 1.0
    a = N.new("ShaderNodeAttribute"); a.attribute_type = "INSTANCER"; a.attribute_name = "a"
    Lk.new(a.outputs["Fac"], b.inputs["Alpha"])
    for k, v in (("surface_render_method", "BLENDED"), ("use_transparent_shadow", False)):
        try:
            setattr(m, k, v)
        except Exception:
            pass
    return m

def build_dust(coll):
    dc = bpy.data.collections.new("MarchDustProtos")
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    for v in bm.verts:
        v.co.z *= 0.55
    for f in bm.faces:
        f.smooth = True
    o = _bm_obj("D00_puff", bm, [_dust_mat()]); dc.objects.link(o)
    ng = _gn_instancer("MarchDustGN", dc)
    S = STATE
    D_ = S["dust"]
    # max concurrency
    tt = np.arange(0, T_END + 0.01, 0.1)
    mx = max(1, max(int(((D_[:, 0] <= t) & (D_[:, 0] + D_[:, 4] > t)).sum()) for t in tt)) if len(D_) else 1
    cap = mx + 16
    ob = _point_cloud("MarchDust", cap, {"s": ("FLOAT", "POINT"), "lod": ("INT", "POINT"), "rot": ("FLOAT_VECTOR", "POINT"),
                                         "a": ("FLOAT", "POINT")}, ng, coll)
    ob.visible_shadow = False
    S.update(dob=ob, dcap=cap)

# ---------------------------------------------------------------- setup
def setup():
    t0 = time.time()
    ground_setup()
    simulate()
    S = STATE
    coll = bpy.data.collections.get("March846") or L.new_coll("March846")
    pcoll, wcoll = build_protos()
    ngp = _gn_instancer("MarchPeopleGN", pcoll)
    ngw = _gn_instancer("MarchWagonGN", wcoll)
    attrs = {"s": ("FLOAT", "POINT"), "lod": ("INT", "POINT"), "rot": ("FLOAT_VECTOR", "POINT"),
             "col": ("FLOAT_COLOR", "POINT"), "col2": ("FLOAT_COLOR", "POINT"), "hair": ("FLOAT_COLOR", "POINT")}
    pob = _point_cloud("MarchPeople", S["N"], attrs, ngp, coll)
    rng = np.random.default_rng(SEED + 7)
    N = S["N"]; kind = S["kind"]
    col = np.array(SHIRTS)[rng.integers(0, len(SHIRTS), N)]
    col = np.where((kind == 1)[:, None], np.array(CLOAK_SCOUT)[None, :], col)
    col = np.where((kind == 2)[:, None], np.array(CLOAK_GARRISON)[None, :], col)
    col = np.where((kind == 3)[:, None], np.array(CLOAK_SCOUT)[None, :], col)
    col2 = np.array(PANTS)[rng.integers(0, len(PANTS), N)]
    hair = np.array(HAIRS)[rng.choice(len(HAIRS), N, p=[0.28, 0.34, 0.16, 0.12, 0.10])]
    for nm, arr in (("col", col), ("col2", col2), ("hair", hair)):
        rgba = np.concatenate([arr, np.ones((N, 1))], 1).astype(np.float32)
        pob.data.attributes[nm].data.foreach_set("color", rgba.ravel())
    wob_ = _point_cloud("MarchWagons", S["NW"], {"s": ("FLOAT", "POINT"), "lod": ("INT", "POINT"), "rot": ("FLOAT_VECTOR", "POINT")}, ngw, coll)
    wob_.data.attributes["lod"].data.foreach_set("value", S["wkind"].astype(np.int32))
    build_titans(coll)
    build_dust(coll)
    S.update(pob=pob, wob=wob_, coll=coll, phase=rng.random(N), panicp=rng.random(N) < 0.35)
    open_gate()
    clear_plain()
    update(0.0, Vector((0, 0, 1000)))
    print(f"[march846] setup {time.time() - t0:.1f}s (sim {S['sim_s']:.1f}s)")
    return STATE

def clear_plain(ra=3400.0, rb=2600.0, a0=2400.0, grove=0.64):
    """The lost Maria plain is open grassland: thin scene.py's ForestGN to a few groves inside an ellipse around the
    march route (ra along the road, rb across it), so the column and the titans are not hidden by trees."""
    ng = bpy.data.node_groups.get("ForestGN")
    if ng is None:
        return
    N, Lk = ng.nodes, ng.links
    dp = next((n for n in N if n.bl_idname == "GeometryNodeDistributePointsOnFaces"), None)
    nz = next((n for n in N if n.bl_idname == "ShaderNodeTexNoise"), None)
    if dp is None or nz is None or not dp.inputs["Selection"].is_linked:
        return
    acc = dp.inputs["Selection"].links[0].from_socket
    pos = N.new("GeometryNodeInputPosition")
    c = GATE + FWD * a0
    sub = N.new("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = (c[0], c[1], 0)
    Lk.new(pos.outputs[0], sub.inputs[0])
    terms = []
    for axis, r in ((FWD, ra), (RGT, rb)):
        dt = N.new("ShaderNodeVectorMath"); dt.operation = "DOT_PRODUCT"; dt.inputs[1].default_value = (axis[0] / r, axis[1] / r, 0)
        Lk.new(sub.outputs[0], dt.inputs[0])
        sq = N.new("ShaderNodeMath"); sq.operation = "MULTIPLY"
        Lk.new(dt.outputs["Value"], sq.inputs[0]); Lk.new(dt.outputs["Value"], sq.inputs[1])
        terms.append(sq)
    add = N.new("ShaderNodeMath"); add.operation = "ADD"
    Lk.new(terms[0].outputs[0], add.inputs[0]); Lk.new(terms[1].outputs[0], add.inputs[1])
    out = N.new("FunctionNodeCompare"); out.operation = "GREATER_THAN"; out.inputs[1].default_value = 1.0
    Lk.new(add.outputs[0], out.inputs[0])
    gr = N.new("FunctionNodeCompare"); gr.operation = "GREATER_THAN"; gr.inputs[1].default_value = grove
    Lk.new(nz.outputs["Fac"], gr.inputs[0])
    o1 = N.new("FunctionNodeBooleanMath"); o1.operation = "OR"
    Lk.new(out.outputs[0], o1.inputs[0]); Lk.new(gr.outputs[0], o1.inputs[1])
    a1 = N.new("FunctionNodeBooleanMath"); a1.operation = "AND"
    Lk.new(acc, a1.inputs[0]); Lk.new(o1.outputs[0], a1.inputs[1])
    Lk.new(a1.outputs[0], dp.inputs["Selection"])

def open_gate():
    """The outer gate stands open for the march (door slid up into the gatehouse)."""
    d = bpy.data.objects.get("OuterGate_Door")
    if d is not None:
        d.location.z = 21.0

# ---------------------------------------------------------------- per frame
def _lerp_idx(t):
    S = STATE
    tt = min(max(t, 0.0), T_END)
    kf = tt / DT; k0 = min(int(kf), S["K"] - 1); k1 = min(k0 + 1, S["K"] - 1)
    return k0, k1, kf - k0

def _alerp(a, b, f):
    return a + (((b - a) + np.pi) % (2 * np.pi) - np.pi) * f

LOD_NEAR, LOD_MID = 230.0, 750.0

def _dscale(d, d0, mx):
    return np.clip((d / d0) ** 0.72, 1.0, mx)

def update(t, cam_loc):
    S = STATE
    if not S:
        return
    t = float(t); cam = np.array(cam_loc[:3], float)
    k0, k1, f = _lerp_idx(t)
    N = S["N"]
    # ---------------- titans
    NT = S["NT"]
    tx = S["TX"][k0] * (1 - f) + S["TX"][k1] * f; ty = S["TY"][k0] * (1 - f) + S["TY"][k1] * f
    tyaw = _alerp(S["TYAW"][k0].astype(float), S["TYAW"][k1].astype(float), f)
    tz = ground(tx.astype(float), ty.astype(float))
    H = S["H"]
    tspd = S["TSPD"][k1].astype(float)
    mv = np.clip(tspd / 40.0, 0.0, 1.0)
    ph = 2 * np.pi * (t * (1.6 + 0.8 * S["abn"]) + np.arange(NT) * 0.37)
    Ar = np.zeros((NT, 7)); Ae = np.zeros((NT, 7)); lean = np.zeros(NT)
    sw = np.sin(ph) * 0.5 * mv
    Ar[:, 1] = sw; Ar[:, 2] = -sw; Ar[:, 3] = -0.7 * sw; Ar[:, 4] = 0.7 * sw
    Ae[:, 5] = Ae[:, 6] = 0.25 + 0.15 * mv
    lean[:] = -0.06 - 0.12 * mv * (1 + S["abn"]) + 0.03 * np.sin(t * 0.7 + np.arange(NT))
    gr = np.where(S["TGR"][k1] <= t, S["TGR"][k1], S["TGR"][k0]).astype(float)
    e = t - gr
    for j in np.where((e >= 0) & (e < 1.2))[0]:          # grab: reach, lift to the mouth, lower (1.2 s)
        ej = e[j] / 1.2 * 3.4
        if ej < 0.7:
            uu = _smooth(ej / 0.7); a, b, l = 0.95 * uu, 0.3 * uu, -0.6 * uu
        elif ej < 1.0:
            a, b, l = 0.95, 0.3, -0.6
        elif ej < 2.0:
            uu = _smooth(ej - 1.0); a, b, l = 0.95 + 0.09 * uu, 0.3 + 2.115 * uu, -0.6 + 0.65 * uu
        elif ej < 2.4:
            a, b, l = 1.04, 2.415, 0.05
        else:
            uu = _smooth(ej - 2.4); a, b, l = 1.04 * (1 - uu), 2.415 * (1 - uu) + 0.25 * uu, 0.05 - 0.11 * uu
        Ar[j, 1] = Ar[j, 2] = 0.0; Ar[j, 3] = 0.15 * math.sin(ej * 6)
        Ar[j, 4] = a; Ae[j, 5] = b; lean[j] = l
    Ar[:, 5] = Ar[:, 4]; Ar[:, 6] = Ar[:, 3]
    bob = (0.5 - 0.5 * np.cos(2 * ph)) * 0.03 * H * mv
    tp = np.stack([tx, ty, tz + bob], 1)
    import swarm845 as SW
    dcam = np.sqrt((tx - cam[0]) ** 2 + (ty - cam[1]) ** 2 + (tz - cam[2]) ** 2)
    tsc = _dscale(dcam, 330.0, 2.6)                     # titans drawn larger far away (same idea as the people)
    co = SW._deform(S["RT"], Ar, Ae, lean, tsc, tyaw, tp)
    S["tob"].data.vertices.foreach_set("co", co.astype(np.float32).ravel()); S["tob"].data.update()
    # ---------------- people
    px = S["PX"][k0] * (1 - f) + S["PX"][k1] * f; py = S["PY"][k0] * (1 - f) + S["PY"][k1] * f
    px = px.astype(float); py = py.astype(float)
    dxm = (S["PX"][k1] - S["PX"][k0]).astype(float); dym = (S["PY"][k1] - S["PY"][k0]).astype(float)
    moving = dxm * dxm + dym * dym > 0.01
    td, tf = S["td"], S["tf"]
    marching = (tf > t) & (td > t)
    s_now = np.full(N, 1e9)
    s_now[marching] = slot_s(S["q"][marching], t, S["spd"][marching])
    # yaw: motion direction, else the road direction at the slot
    sx, sy, stx, sty = road(np.clip(s_now, RS[0], RS[-1]))
    yaw = np.where(moving, np.arctan2(dym, dxm), np.arctan2(sty, stx)) - np.pi / 2
    pz = ground(px, py)
    vis = np.ones(N)
    vis[marching & (s_now < -S_IN)] = 0.0
    # grabbed and gone: lifted toward the titan's mouth, shrinking
    vjj = S["vj"]
    dead = td <= t
    vis[dead & (t >= td + LIFT)] = 0.0
    lifting = np.where(dead & (t < td + LIFT) & (vjj >= 0))[0]
    if len(lifting):
        j = vjj[lifting]; ee = t - td[lifting]
        uu = np.clip((ee - 0.08) / 0.32, 0, 1); uu = uu * uu * (3 - 2 * uu)
        fw = np.stack([-np.sin(tyaw[j]), np.cos(tyaw[j])], 1)
        hx = tx[j] + fw[:, 0] * H[j] * 0.2; hy = ty[j] + fw[:, 1] * H[j] * 0.2
        hz = tz[j] + H[j] * (0.45 + 0.45 * uu)
        px[lifting] = px[lifting] * (1 - uu) + hx * uu; py[lifting] = py[lifting] * (1 - uu) + hy * uu
        pz[lifting] = pz[lifting] * (1 - uu) + hz * uu
        vis[lifting] *= 1.0 - np.clip((ee - 0.35) / (LIFT - 0.35), 0, 1)
    d = np.sqrt((px - cam[0]) ** 2 + (py - cam[1]) ** 2 + (pz - cam[2]) ** 2)
    kind = S["kind"]
    step = ((t * 2.6 + S["phase"]) % 1.0) < 0.5
    lod = np.where(step, 0, 1)
    fleeing = (tf <= t) & ~dead
    lod = np.where(fleeing & S["panicp"], 2, lod)
    lod = np.where(kind == 4, np.where(step, 8, 9), lod)
    lod = np.where(fleeing & S["panicp"], 2, lod)
    lod = np.where((kind == 1) | (kind == 2), np.where(step, 3, 4), lod)
    lod = np.where(kind == 3, 7, lod)
    lod = np.where(d > LOD_NEAR, np.where(kind == 3, 7, 5), lod)
    lod = np.where(d > LOD_MID, 6, lod)
    sc = _dscale(d, 150.0, 3.3) * (S["hgt"] / 1.7)
    sc = np.where(S["surv"] & (t > 14.0), sc * 1.25, sc)
    sc = sc * vis
    tilt = np.where(fleeing & moving, -0.25, 0.0)
    rot = np.stack([tilt * 0, np.zeros(N), yaw], 1)
    me = S["pob"].data
    me.vertices.foreach_set("co", np.stack([px, py, pz + 0.05], 1).astype(np.float32).ravel())
    me.attributes["s"].data.foreach_set("value", sc.astype(np.float32))
    me.attributes["lod"].data.foreach_set("value", lod.astype(np.int32))
    me.attributes["rot"].data.foreach_set("vector", rot.astype(np.float32).ravel())
    me.update()
    # ---------------- wagons
    NW = S["NW"]
    w_to = S["w_to"]
    tw = np.minimum(t, w_to)
    wx, wy, ws, wtx, wty = slot_xy(S["wq"], S["wu"], tw, S["wspd"], np.zeros(NW))
    over = t >= w_to
    a_ = np.clip((t - w_to) / 0.35, 0, 1); a_ = np.where(over, a_ * a_ * (3 - 2 * a_), 0.0)
    skid = np.where(over, 4.0 * a_, 0.0)
    wx = wx - wty * skid * np.sign(S["w_roll"]); wy = wy + wtx * skid * np.sign(S["w_roll"])
    wz = ground(wx, wy)
    wyaw = np.arctan2(wty, wtx) - np.pi / 2 + np.where(over, 0.4 * np.sign(S["w_roll"]), 0.0) * a_
    roll = S["w_roll"] * a_
    dw = np.sqrt((wx - cam[0]) ** 2 + (wy - cam[1]) ** 2 + (wz - cam[2]) ** 2)
    wsc = _dscale(dw, 220.0, 2.6) * np.where(ws < -S_IN, 0.0, 1.0)
    me = S["wob"].data
    me.vertices.foreach_set("co", np.stack([wx, wy, wz + 0.02], 1).astype(np.float32).ravel())
    me.attributes["s"].data.foreach_set("value", wsc.astype(np.float32))
    me.attributes["rot"].data.foreach_set("vector", np.stack([np.zeros(NW), roll, wyaw], 1).astype(np.float32).ravel())
    me.update()
    # ---------------- dust
    Dd = S["dust"]; cap = S["dcap"]
    sel = np.where((Dd[:, 0] <= t) & (Dd[:, 0] + Dd[:, 4] > t))[0][:cap] if len(Dd) else np.zeros(0, int)
    n = len(sel)
    co = np.zeros((cap, 3), np.float32); s_ = np.zeros(cap, np.float32); al = np.zeros(cap, np.float32)
    if n:
        ev = Dd[sel]; age = (t - ev[:, 0]) / ev[:, 4]
        size = ev[:, 3] * (0.45 + 0.9 * np.sqrt(age))
        gz = ground(ev[:, 1], ev[:, 2])
        co[:n] = np.stack([ev[:, 1], ev[:, 2], gz + size * 0.25 + age * ev[:, 3] * 0.4], 1)
        s_[:n] = size
        al[:n] = ev[:, 5] * (1 - age) ** 1.5 * np.clip(age * 8, 0, 1)
    me = S["dob"].data
    me.vertices.foreach_set("co", co.ravel())
    me.attributes["s"].data.foreach_set("value", s_)
    me.attributes["a"].data.foreach_set("value", al)
    me.update()
    S["last"] = dict(t=t, visible=int((sc > 0.001).sum()), near=int(((d < LOD_NEAR) & (sc > 0.001)).sum()),
                     mid=int(((d >= LOD_NEAR) & (d < LOD_MID) & (sc > 0.001)).sum()), dust=n, alive=alive(t))

# ---------------------------------------------------------------- the one-take camera
G = GATE
def _gp(a, b, z):
    """Point at a metres outward from the gate and b metres along the road's lateral axis (east for Trost)."""
    p = G + FWD * a + RGT * b
    return (float(p[0]), float(p[1]), float(z))

# (t, location, look-at, lens).  Outward = south for Trost; lateral +b = east.
CAM_KEYS = [
    (0.0,  _gp(-170, 170, 125),  _gp(60, -10, 0),    27),     # low, inside the outer gate: the avenue pours out
    (3.0,  _gp(200, 230, 170),   _gp(900, -20, 0),   27),     # over the wall, rising, along the column
    (6.0,  _gp(1100, 420, 280),  _gp(2300, -40, 0),  28),     # the column stretches to the horizon; titans ahead
    (9.0,  _gp(2000, 700, 230),  _gp(2300, -150, 0), 29),     # swing out to the east flank as the waves hit
    (12.0, _gp(2100, 950, 380),  _gp(1700, -100, 0), 28),     # higher: islands, encirclement
    (15.0, _gp(1500, 650, 560),  _gp(700, 0, 0),     28),     # emptied plain
    (18.0, _gp(1050, 260, 640),  _gp(-150, 0, 40),   28),     # turning north: stragglers -> gate, Trost, Wall Rose
]
CAM_OUT_VEL = (FWD * -95.0).tolist() + [22.0]   # leaves rising north (toward Wall Rose) at ~95 m/s

def _tangents(T, P, v_in=None, v_out=None):
    n = len(T); M = []
    for i in range(n):
        if i == 0:
            M.append(np.array(v_in) if v_in is not None else (P[1] - P[0]) / (T[1] - T[0]))
        elif i == n - 1:
            M.append(np.array(v_out) if v_out is not None else (P[-1] - P[-2]) / (T[-1] - T[-2]))
        else:
            d0 = (P[i] - P[i - 1]) / (T[i] - T[i - 1]); d1 = (P[i + 1] - P[i]) / (T[i + 1] - T[i])
            h0, h1 = T[i] - T[i - 1], T[i + 1] - T[i]
            M.append((d0 * h1 + d1 * h0) / (h0 + h1))
    return M

def _herm(T, P, M, t):
    t = min(max(t, T[0]), T[-1])
    i = min(len(T) - 2, int(np.searchsorted(T, t, side="right") - 1))
    h = T[i + 1] - T[i]; s = (t - T[i]) / h
    h00, h10, h01, h11 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s, -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
    return h00 * P[i] + h10 * h * M[i] + h01 * P[i + 1] + h11 * h * M[i + 1]

_CT = {}
def _cam_tab():
    if not _CT:
        T = np.array([k[0] for k in CAM_KEYS])
        PL = [np.array(k[1]) for k in CAM_KEYS]; PT = [np.array(k[2]) for k in CAM_KEYS]
        LN = [np.array([math.log(k[3])]) for k in CAM_KEYS]
        _CT.update(T=T, PL=PL, ML=_tangents(T, PL, v_out=np.array(CAM_OUT_VEL)), PT=PT, MT=_tangents(T, PT),
                   LN=LN, MN=_tangents(T, LN, v_in=np.zeros(1), v_out=np.zeros(1)))
    return _CT

def cam_at(t):
    c = _cam_tab()
    loc = _herm(c["T"], c["PL"], c["ML"], t); tgt = _herm(c["T"], c["PT"], c["MT"], t)
    lens = math.exp(float(_herm(c["T"], c["LN"], c["MN"], t)[0]))
    return Vector(loc), Vector(tgt), lens

def cam_velocity(t, h=1 / 60):
    a, _, _ = cam_at(t - h); b, _, _ = cam_at(t + h)
    return (b - a) / (2 * h)

CAM_IN = dict(t=0.0, loc=CAM_KEYS[0][1], look=CAM_KEYS[0][2], lens=CAM_KEYS[0][3])     # velocity: cam_velocity(0)
CAM_OUT = dict(t=T_END, loc=CAM_KEYS[-1][1], look=CAM_KEYS[-1][2], lens=CAM_KEYS[-1][3], vel=CAM_OUT_VEL)

# ---------------------------------------------------------------- placeholder set (AOT_SET=march846, no Trost)
SET_NAME = "march846_placeholder" if E("AOT_SET") == "march846" else None
if SET_NAME:
    def build_set(M, year):
        sc = bpy.context.scene
        terrain = L.build_terrain(M)
        bm = bmesh.new()
        ang = HEADING + math.pi / 2
        for side in (-1, 1):                    # straight wall either side of the gate, 3 km each way
            c = GATE + RGT * side * (1500 + L.GATE_W / 2 + 10)
            L.box(bm, (c[0], c[1], L.WALL_H / 2), (3000, L.WALL_T, L.WALL_H), rot=math.atan2(RGT[1], RGT[0]))
        L.obj_from_bm("PlaceholderWall", bm, [M["stone"]])
        L.gatehouse("OuterGate", tuple(GATE), ang, M, deep=8.0)
        w = bpy.data.worlds.new("Sky"); sc.world = w; w.use_nodes = True
        w.node_tree.nodes["Background"].inputs[0].default_value = (0.45, 0.6, 0.85, 1)
        sun = bpy.data.lights.new("Sun", "SUN"); sun.energy = 3.6
        so = bpy.data.objects.new("Sun", sun); sc.collection.objects.link(so); so.rotation_euler = (0.7, 0.2, 0.6)
        return M

CAMS = {"march_gate": lambda: (CAM_KEYS[0][1], CAM_KEYS[0][2], CAM_KEYS[0][3])}
