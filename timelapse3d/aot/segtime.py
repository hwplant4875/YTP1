"""EP1 segment table (SCENE_BIBLE_v2 A1 TIGHT, owner 10:52 UTC 7:02 cut, every scene kept) + seams (A2) + frame helpers.
Pure Python.  Re-time = edit DUR here (global starts follow); every segment module reads its own length from here.

    SEG["g8"] -> dict(id, dur, start, end, content);  start("g5");  global_t("g3", 12.0)
    seam("g4_g5") / seam("g4","g5") -> dict(frame, pos, look, lens, vel, t) ; seam names listed in SEAMS
Frames: W = Shiganshina world (inner gate (0,0), +y north); M = Trost master (outer gate O (0,0), Rose Y 870); M = W - (0, 4130);
trost.py set frame = (X, Y - 870, Z).
"""
ORDER = ["g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8"]
DUR = dict(g1=32.0, g2=32.0, g3=78.4, g4=20.0, g5=70.0, g6=69.5, g7=45.0, g8=75.0)      # TIGHT (A1); full: 32 32 78.4 20 84 74 116 136
FULL = dict(g1=32.0, g2=32.0, g3=78.4, g4=20.0, g5=84.0, g6=74.0, g7=116.0, g8=136.0)
CONTENT = dict(
    g1="Opening + Shiganshina fall", g2="Armored ram + ferries", g3="Flight north, camps, march846, flight to camp, 104th camp",
    g4="Trost 850 establishing", g5="Trost breach, evacuation, Mikasa, Attack Titan", g6="Supply HQ, lift op, Eren emerges",
    g7="Cannon basin, half-shift, salute, Pyxis", g8="Boulder, seal, Levi, mop-up, pyres")
# g3 internal groups (local s): flight 0-12.9, camps 12.9-31.3, march846 31.3-49.3, flight to camp 49.3-63.4, 104th camp 63.4-78.4
G3 = dict(flight=(0.0, 12.9), camps=(12.9, 31.3), march=(31.3, 49.3), to_camp=(49.3, 78.4), camp104=(63.4, 78.4))

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
    "g3_in":     dict(frame="M", pos=(170, 170, 125), look=(-10, -60, 0), lens=27.0, vel=(16.7, -61.1, 5.6), t=START["g3"] + 31.3,
                      note="g3 CAM_IN = march846.CAM_IN (set: (170, -700, 125)); guide key 31.8 = (178.4, 139.5, 127.8)"),
    "march_out": dict(frame="M", pos=(260, -1050, 640), look=(0, 150, 40), lens=28.0, vel=(0, 95, 22), t=START["g3"] + 49.3,
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
