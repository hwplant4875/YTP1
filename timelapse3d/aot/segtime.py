"""EP1 segment table (SCENE_BIBLE_v2 A1 TIGHT, owner 10:52 UTC 7:02 cut, every scene kept) + seams (A2) + frame helpers.
Pure Python.  Re-time = edit DUR here (global starts follow); every segment module reads its own length from here.

    SEG["g8"] -> dict(id, dur, start, end, content);  start("g5");  global_t("g3", 12.0)
    seam("g4_g5") / seam("g4","g5") -> dict(frame, pos, look, lens, vel, t) ; seam names listed in SEAMS
Frames: W = Shiganshina world (inner gate (0,0), +y north); M = Trost master (outer gate O (0,0), Rose Y 870); M = W - (0, 4130);
trost.py set frame = (X, Y - 870, Z).
"""
ORDER = ["g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8"]
DUR = dict(g1=32.0, g2=32.0, g3=61.8, g4=20.0, g5=70.0, g6=69.5, g7=45.0, g8=75.0)      # TIGHT (A1); full: 32 32 78.4 20 84 74 116 136
FULL = dict(g1=32.0, g2=32.0, g3=78.4, g4=20.0, g5=84.0, g6=74.0, g7=116.0, g8=136.0)
CONTENT = dict(
    g1="Opening + Shiganshina fall", g2="Armored ram + ferries", g3="Flight north, camps, march846, flight to camp, 104th camp",
    g4="Trost 850 establishing", g5="Trost breach, evacuation, Mikasa, Attack Titan", g6="Supply HQ, lift op, Eren emerges",
    g7="Cannon basin, half-shift, salute, Pyxis", g8="Boulder, seal, Levi, mop-up, pyres")
# g3 internal groups (local s).  g3 v5 (owner 10/27 07:34: farm faster, NO winter, the ORIGINAL march846 camera at its own
# real-time speed): flight 0-17.7, farm + 846 17.7-26.6, march846 26.6-44.6 (played at slope 1, see TMAP below), flight to
# the camp 44.6-54.6, 104th camp 54.6-61.8.  G3_MARCH is the ONE place the march span lives (seg_g3.BEATS reads it).
G3_MARCH = (26.6, 44.6)
G3 = dict(flight=(0.0, 17.7), camps=(17.7, G3_MARCH[0]), march=G3_MARCH, to_camp=(G3_MARCH[1], 61.8), camp104=(54.6, 61.8))

def _starts():
    s, t = {}, 0.0
    for g in ORDER:
        s[g] = round(t, 6); t += DUR[g]
    return s, t
START, TOTAL = _starts()
SEG = {g: dict(id=g, dur=DUR[g], start=START[g], end=START[g] + DUR[g], content=CONTENT[g]) for g in ORDER}

def start(g): return START[g]
def global_t(g, t): return START[g] + t
def fmt(t): return "%d:%04.1f" % (int(t // 60), t % 60)

# ---------------------------------------------------------------- frame helpers
M_OFF_Y = 4130.0                      # M = W - (0, 4130)
SET_OFF_Y = 870.0                     # trost.py set frame = (X, Y - 870, Z)
def M_to_set(x, y=None, z=None):
    if y is None: x, y, z = x
    return (x, y - SET_OFF_Y, z)
def set_to_M(x, y=None, z=None):
    if y is None: x, y, z = x
    return (x, y + SET_OFF_Y, z)
def W_to_M(x, y=None, z=None):
    if y is None: x, y, z = x
    return (x, y - M_OFF_Y, z)
def M_to_W(x, y=None, z=None):
    if y is None: x, y, z = x
    return (x, y + M_OFF_Y, z)
def W_to_set(x, y=None, z=None): return M_to_set(*W_to_M(x, y, z))

# ---------------------------------------------------------------- A2 seams (exact; position / look-at / lens / velocity m/s)
# t = global time of the seam (None: inside g3's march846 span)
SEAMS = {
    "g1_g2":     dict(frame="W", pos=(-254, -468, 95), look=(-167, -590, 2), lens=28.0, vel=(0, 0, 0), t=START["g2"],
                      note="g1 K12 = g2 K0 = render_fall2.SEAM_IN, at rest (g1 adds a guide key 1 s later); v2 10/26 lead QA (was (-130,-686,114)->(-165,-594,0))"),
    "g2_g3":     dict(frame="W", pos=(175, 480, 240), look=(228, 1050, 0), lens=28.0, vel=(0, 45, 8), t=START["g3"],
                      note="g2 K9 = g3 FA0, 45 m/s heading N, vz +8"),
    "g3_in":     dict(frame="M", pos=(-780, -200, 880), look=(0, -300, 0), lens=40.0, vel=(-20, -41.7, 20), t=START["g3"] + G3_MARCH[0],
                      note="g3 CAM_IN = march846.CAM_IN (set: (170, -700, 125)); guide key 31.8 = (178.4, 139.5, 127.8)"),
    "march_out": dict(frame="M", pos=(-1080, -760, 1150), look=(-900, -300, 0), lens=26.0, vel=(0, 50, -15), t=START["g3"] + G3_MARCH[1],
                      note="march846.CAM_OUT = g3 FT0 (set: (260, -1920, 640)); lead-in guide FT0-1 s = (260, -1145, 618)"),
    "g3_g4":     dict(frame="M", pos=(-1570, 1190, 170), look=(-1450, 1490, 0), lens=30.0, vel=(14.1, -14.1, 0), t=START["g4"],
                      note="g3 FT7 = g4 G0 (set: (-1570, 320, 170)); 20 m/s heading SE, vz 0"),
    "g4_g5":     dict(frame="M", pos=(-40, 330, 170), look=(0, 0, 30), lens=32.0, vel=(1.3, -8, -1), t=START["g5"], note="g4 G5 = g5 C0"),
    "g5_g6":     dict(frame="M", pos=(-345, 455, 175), look=(-185, 640, 15), lens=30.0, vel=(3, 5, 0), t=START["g6"], note="g5 C10 = g6 H0"),
    "g6_g7":     dict(frame="M", pos=(220, 650, 130), look=(345, 810, 0), lens=32.0, vel=(25, 8, 0), t=START["g7"], note="g6 H8 = g7 C0"),
    "g7_g8":     dict(frame="M", pos=(-40, 960, 205), look=(40, 540, 0), lens=30.0, vel=(-2.5, -5, 2), t=START["g8"], note="g7 C15 = g8 K0"),
    "g8_end":    dict(frame="M", pos=(200, 760, 240), look=(-20, 300, 0), lens=28.0, vel=(0, 0, 0), t=TOTAL, note="g8 E2 (END), guide key +1 s"),
}
_BY_PAIR = {tuple(k.split("_")): k for k in ("g1_g2", "g2_g3", "g3_g4", "g4_g5", "g5_g6", "g6_g7", "g7_g8", "g8_end")}

def seam(name, b=None):
    """Seam dict (copy): seam("g4_g5") or seam("g4", "g5"); also "g3_in", "march_out", "g8_end"."""
    if b is not None: name = _BY_PAIR[(name, b)]
    return dict(SEAMS[name], name=name)

def seam_in(g):
    """The seam entering segment g (None for g1)."""
    i = ORDER.index(g)
    return seam(ORDER[i - 1], g) if i else None

def seam_out(g):
    i = ORDER.index(g)
    return seam(g, ORDER[i + 1]) if i + 1 < len(ORDER) else seam("g8_end")

# ---------------------------------------------------------------- VIDEO CLOCK (owner 10/27 07:34: "everything 2x faster", 30 fps)
# Segment modules keep their own LOCAL time t (BEATS, CAM, update(t)) running 0..DUR[g].  The video plays each segment
# through a piecewise-linear map  video tv -> local t  (TMAP), default  t = SPEED * tv.  render_seg.py --vclock renders
# frames on the VIDEO clock (f = round(tv * fps)) and evaluates the segment at seg_t(g, tv).
#   - Re-time a stretch of a segment: give TMAP[g] knots [(tv, t), ...] from (0, 0) to (VDUR, DUR[g]); slope = local
#     speed factor (2 = double speed, 1 = real time).  SEAM RULE: the slope at both ends must stay SPEED (=2) unless the
#     neighbour's adjacent end is changed to match, otherwise camera speed jumps at the seam.
#   - HUD tag JSONs are on the video clock: convert with to_video(g, t).
SPEED = 2.0
TMAP = {}                              # g -> [(tv, t), ...] knots; missing = linear SPEED
# g2 (agent 10/27, owner 07:34): DUR stays 32.0 local (g3 part A continues at g2 t 32 = seg_g3.G2_T); Reiner's 3x-on-screen
# speed-up lives in seg_g2's BEATS / run law (1.5x local), so the map stays linear at SPEED: 16.0 s of video, slope 2 at both
# seams.  To stretch a stretch, add knots here, e.g. [(0,0), (4.2,8.4), (4.8,9.4), (16.1,32)] = slope 1.67 around the impact (video 16.1 s).
TMAP["g2"] = [(0.0, 0.0), (16.0, 32.0)]

def _g2_v5():   # v5 (owner 10/27 09:41): the empty steam stand at 3x, burning-town aerial ~3 s at 2, then an ULTRA-fast move
    return slope_knots(DUR["g2"], [(0.0, 2.0, 0.0), (12.2, 2.6, 0.4), (14.8, 2.0, 0.4), (21.5, 1.55, 0.3),
                                        (26.6, 4.5, 0.4), (30.6, 2.0, 0.35)])

def ramp_knots(dur, holds, ramp=1.2, n=12, speed=None):
    """TMAP knots for a segment played at `speed` (default SPEED) except local spans holds = [(t_a, t_b, slope), ...]
    played at `slope`.  The slope eases speed -> slope over `ramp` VIDEO seconds ending exactly at t_a, and back over
    `ramp` video s starting at t_b (cosine ease, sampled as n linear pieces: slope steps <= ~5 %).  Ends stay at speed."""
    import math
    sp = SPEED if speed is None else speed
    K = [(0.0, 0.0)]
    def lin_to(t):                                       # advance at sp to local t
        tv, t0 = K[-1]
        if t > t0 + 1e-9: K.append((tv + (t - t0) / sp, t))
    def ease(s0, s1):                                    # ramp from the last knot
        tv0, t0 = K[-1]
        F = lambda u: s0 * u + (s1 - s0) * (u - math.sin(math.pi * u) / math.pi) / 2
        for k in range(1, n + 1):
            u = k / n; K.append((tv0 + ramp * u, t0 + ramp * F(u)))
    for a, b, s in holds:
        lin_to(a - ramp * (sp + s) / 2); ease(sp, s)
        tv, t0 = K[-1]; K.append((tv + (b - t0) / s, b))
        ease(s, sp)
    lin_to(dur)
    return [(round(tv, 6), round(t, 6)) for tv, t in K]
# g3 v5: march846 (G3_MARCH) at real time (slope 1 = march846's own tuned speed), eased 2 -> 1 -> 2 over 1.0 video s each side
# v7 (QA batch1 P1: march ~25 s -> ~10 s): the march plays at 1.8 (18 local s -> ~10 video s)
TMAP["g3"] = ramp_knots(DUR["g3"], [(G3_MARCH[0], G3_MARCH[1], 1.8)], ramp=1.0)

def slope_knots(dur, plan, n=8):
    """TMAP knots from a slope PLAN = [(t_a, slope, ramp), ...] (local t_a ascending, plan[0] = (0, s0, 0)): play at the
    previous slope up to local t_a, then ease (cosine, n linear pieces) to `slope` over `ramp` VIDEO seconds, and so on to
    local `dur`.  The slope at local dur is the last plan slope (keep it = SPEED for the seam rule)."""
    import math
    K = [(0.0, 0.0)]; cur = plan[0][1]
    def lin_to(t, s):
        tv, t0 = K[-1]
        if t > t0 + 1e-9: K.append((tv + (t - t0) / s, t))
    for t_a, s, ramp in plan[1:]:
        lin_to(t_a, cur)
        tv0, t0 = K[-1]
        F = lambda u: cur * u + (s - cur) * (u - math.sin(math.pi * u) / math.pi) / 2
        for k in range(1, n + 1):
            u = k / n; K.append((tv0 + ramp * u, t0 + ramp * F(u)))
        cur = s
    lin_to(dur, cur)
    return [(round(tv, 6), round(t, 6)) for tv, t in K]
# g1 v4 (owner 10/27 07:34: the opening = renders/opening_preview_v4.mp4 at its REAL-TIME pace, then everything fast):
# local 0-11.0 at slope 1 (tree, swoosh over the inner wall, avenue, bolt 4.62, head rise + zoom-in to 8.0, pull-back,
# kick 11.0) -> 2 over 0.7 s -> 5.5 (Colossal vanishes, smoke columns, the pour, Dina runs from the gate, fly west)
# -> 1.7 for Carla (BEND 25.5 -> gone 28.9 = 2.0 video s) -> 3 -> 2 at the g1|g2 seam (at rest).  Video ~17.9 s.
G1_PLAN = [(0.0, 1.0, 0.0), (11.0, 2.0, 0.7), (12.05, 5.5, 0.9), (23.4, 1.7, 0.5), (28.9, 3.0, 0.3), (31.15, 2.0, 0.3)]
TMAP["g1"] = slope_knots(DUR["g1"], G1_PLAN)
TMAP["g2"] = _g2_v5()
# g4 v4 (owner 10/27: 2nd Colossal, faster camera): the establishing approach at 3.2x (local 1.0-15.0), back to 2 for
# Eren's fist on the wall top above O and the g4|g5 seam.  Video ~7.9 s.
TMAP["g4"] = slope_knots(DUR["g4"], [(0.0, 2.0, 0.0), (1.0, 3.2, 0.6), (15.0, 2.0, 0.6)])
# g7 v3 (owner 10/27: camera to the cannon basin MUCH faster): transit local 0.3-5.0 at 4.5x, back to 2 before FIRE 6.0.
TMAP["g7"] = slope_knots(DUR["g7"], [(0.0, 2.0, 0.0), (0.3, 4.5, 0.4), (4.9, 2.0, 0.35)])
# g8 v4 (owner 10/27: carry a bit faster): the carry (local 19.5-37.5) at 2.6x, back to 2 before the slam.
# v4 (QA batch1: "closer, slower moment"): the lift + first carry steps at 1.5, then the fast carry
TMAP["g8"] = slope_knots(DUR["g8"], [(0.0, 2.0, 0.0), (16.5, 1.5, 0.4), (21.5, 2.6, 0.4), (37.0, 2.0, 0.4)])
def knots(g):
    k = TMAP.get(g)
    return list(k) if k else [(0.0, 0.0), (DUR[g] / SPEED, DUR[g])]
def vdur(g): return knots(g)[-1][0]
def seg_t(g, tv):
    k = knots(g)
    if tv <= k[0][0]: return k[0][1]
    for (a, ta), (b, tb) in zip(k, k[1:]):
        if tv <= b:
            return ta + (tb - ta) * (tv - a) / (b - a) if b > a else tb
    return k[-1][1]
def to_video(g, t):
    k = knots(g)
    if t <= k[0][1]: return k[0][0]
    for (a, ta), (b, tb) in zip(k, k[1:]):
        if t <= tb:
            return a + (b - a) * (t - ta) / (tb - ta) if tb > ta else a
    return k[-1][0]
def slope(g, tv):
    k = knots(g)
    for (a, ta), (b, tb) in zip(k, k[1:]):
        if tv <= b + 1e-9 and b > a: return (tb - ta) / (b - a)
    return SPEED
def vstarts():
    s, t = {}, 0.0
    for g in ORDER:
        s[g] = round(t, 6); t += vdur(g)
    return s, t

if __name__ == "__main__":
    for g in ORDER:
        s = SEG[g]; print("%s %6.1f s  %s -> %s  %s" % (g, s["dur"], fmt(s["start"]), fmt(s["end"]), s["content"]))
    print("total %.1f s (%s)" % (TOTAL, fmt(TOTAL)))
    VS, VT = vstarts()
    for g in ORDER:
        print("video %s %6.2f s  %s  slope in %.2f out %.2f" % (g, vdur(g), fmt(VS[g]), slope(g, 0.0), slope(g, vdur(g))))
    print("video total %.1f s (%s)" % (VT, fmt(VT)))
