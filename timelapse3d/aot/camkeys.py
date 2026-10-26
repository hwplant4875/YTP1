"""Camera key tables of SCENE_BIBLE_v2 section B (g1..g8), TIGHT times, transcribed as written (do not "fix" them here; run
`python aot/camchan.py --check all` and compare with the bible).  Pure data + path(); no bpy.

KEYS[seg] = dict(frame="W"|"M", keys=[(t, cam_xyz, look_xyz, lens_mm), ...], v_in=m/s|None, v_out=m/s|None,
                 look_v_in, look_v_out)         t = SEGMENT-LOCAL seconds; v_in / v_out = the A2 seam velocities
KEYS["g3"] has groups (flight W, camps M, to_camp M); march846 keeps its own spline (CAM_IN / CAM_OUT below).
Per-segment modules build CamPath(**camkeys.cam(seg)) in M (g1/g2 in W) -- see cam().
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import segtime as ST
from camchan import CamPath, speed_profile

# ---------------------------------------------------------------- g1 (W)  guide key 33.0 = K12 (rest at the seam)
# K0 / K1: the locked tree shots (not numbers in the bible): K1 = render_fast fallback flight_at(900); K0 = close on the kids,
# 3 m from them on the same line of sight (render_fast: c0 = l0 + (k0 - l0) * 0.74, lens 0.9 * 50)
G1 = [
    (0.00, (-476, 330.5, 2.4), (-474.6, 327.9, 1.2), 45),
    (2.00, (-480, 338, 7.2), (-300, 0, 10.6), 50),
    (2.05, (-480, 338, 7.2), (-300, 0, 10.6), 50),
    # v2 (lead QA 10/26, owner rules 06:05 / 15:07 / 00:44 beat the bible keys): swoosh over the inner wall onto the
    # plaza side so the head + both gripping hands are ~10-15 % of the frame at 5-10 s (camera ~190-220 m from the head,
    # 48-50 mm), the kick framed from the town side (gate ~13 % of the frame width), then a calm observer 92-105 m up,
    # pitch 23-37 deg, then ~145 m NW of the Yeager ruin (Carla's street side; pour behind, frame-left).  The old bible K2-K12 are in G1_BIBLE below.
    (3.4,  (-380, 220, 105), (-40, -560, 0),  30),
    (4.8,  (-250, 20, 112),  (-20, -640, 10), 32),
    (6.2,  (-140, -235, 108), (-8, -722, 45), 40),     # v2b (owner 16:51 "distant is better"): far calm observer,
    (7.4,  (-70, -420, 95),   (-7, -728, 52), 48),     # head + hands ~6-10 % of the frame from ~290-320 m
    (9.2,  (-55, -445, 92),   (-6, -728, 50), 50),
    (10.6, (20, -470, 100),   (0, -712, 14),  40),     # kick from the town side at ~250 m: dust dome + arcs readable
    (12.2, (20, -460, 110),   (0, -700, 20),  36),
    (14.5, (-25, -450, 110),  (-12, -690, 14), 34),
    (18.0, (-40, -480, 105),  (-55, -665, 6),  32),
    (21.5, (-130, -482, 100), (-120, -622, 4), 30),
    (25.0, (-232, -480, 96),  (-168, -590, 3), 30),    # NW of the ruin: Carla / the Smiling Titan face this way, pour behind
    (28.5, (-246, -472, 95),  (-168, -589, 4), 28),
    (32.0, (-254, -468, 95),  (-167, -590, 2), 28),     # = SEAM_IN v2 (render_fall2, segtime g1_g2, g2 K0)
    (33.0, (-100, -680, 94), (-166, -588, 2), 28),     # guide key (seam at rest)
]
G1_BIBLE = [
    (3.9,  (-456, 298, 92),  (-40, -600, 40), 30),
    (5.8,  (-330, 135, 106), (-15, -700, 50), 34),
    (7.8,  (-185, -60, 116), (-8, -700, 55),  42),
    (10.0, (-78, -215, 124), (-5, -705, 45),  50),
    (13.0, (-62, -250, 124), (-10, -680, 30), 45),
    (16.5, (-60, -320, 125), (-15, -690, 15), 40),
    (20.0, (-78, -425, 121), (-60, -650, 8),  36),
    (23.0, (-92, -478, 119), (-140, -600, 4), 32),
    (26.0, (-86, -545, 117), (-160, -592, 3), 30),
    (29.0, (-98, -625, 115), (-165, -593, 2), 29),
    (32.0, (-130, -686, 114), (-165, -594, 0), 28),
    (33.0, (-130, -686, 114), (-165, -594, 0), 28),      # guide key (seam at rest)
]
# ---------------------------------------------------------------- g2 (W)
G2 = [
    (0.0,  (-254, -468, 95),  (-167, -590, 2), 28),            # SEAM_IN v2 (was (-130, -686, 114) -> (-165, -594, 0))
    (3.5,  (-180, -590, 118), (0, -310, 10),   32),
    (7.5,  (-215, -440, 120), (0, -190, 10),   35),
    (11.0, (-225, -275, 118), (0, -80, 14),    38),
    (13.5, (-215, -185, 118), (0, -8, 18),     38),
    (16.0, (-195, -140, 132), (10, 30, 12),    35),
    (20.0, (-110, -5, 170),   (45, 125, 0),    32),
    (24.0, (-15, 130, 205),   (160, 290, 0),   30),
    (28.0, (105, 300, 222),   (228, 580, 0),   30),
    (32.0, (175, 480, 240),   (228, 1050, 0),  28),
]
# ---------------------------------------------------------------- g3  (group-local seconds)
G3_FLIGHT_W = [                                                       # FA0..FA3, frame W
    (0.0,  (175, 480, 240),  (228, 1050, 0), 28),
    (3.7,  (300, 1250, 320), (330, 2000, 0), 28),
    (7.3,  (380, 2600, 380), (250, 3700, 0), 28),
    (10.6, (200, 3750, 320), (-100, 4600, 0), 30),
]
# camps, frame M.  Lens: the bible gives H2 "28->40" (ease 17.7-21) and H3 "40->28": H2..H3 are held at 40, CAM_IN is 27 (assumption).
G3_CAMPS_M = [
    (12.9,  (60, 170, 300),    (-268, 805, 0),   30),             # FA4 = W (60, 4300, 300)
    (17.7,  (-145, 605, 250),  (-330, 1020, 0),  28),             # H (at rest)
    (21.0,  (-150, 620, 255),  (-300, 1430, 0),  40),             # H2
    (22.55, (-145.5, 613, 253), (-686, 1058, 0), 40),             # P1
    (24.1,  (-132, 592, 248),  (-732, 582, 0),   40),             # P2
    (25.65, (-105, 550, 238),  (-464, 232, 0),   40),             # P3
    (27.2,  (-60, 480, 220),   (-110, 130, 0),   40),             # H3
    (31.3,  (170, 170, 125),   (-10, -60, 0),    27),             # CAM_IN
    (31.8,  (178.4, 139.5, 127.8), (-10, -115.5, 0), 27),         # guide = CAM_IN + 0.5 v (look: + 0.5 look-velocity)
]
CAM_IN = dict(frame="M", t=31.3, pos=(170, 170, 125), look=(-10, -60, 0), lens=27.0, vel=(16.7, -61.1, 5.6), look_vel=(0, -111.1, 0))
CAM_OUT = dict(frame="M", t=49.3, pos=(260, -1050, 640), look=(0, 150, 40), lens=28.0, vel=(0, 95, 22), look_vel=(0, 283.3, 13.3))
G3_TO_CAMP_M = [
    (49.3, (260, -1050, 640),  (0, 150, 40),     28),             # FT0 = march846.CAM_OUT
    (55.8, (-350, 370, 520),   (-900, 1270, 0),  28),             # FT1
    (60.2, (-1250, 1020, 260), (-1450, 1520, 0), 30),             # FT2
    (63.4, (-1410, 1260, 95),  (-1450, 1530, 0), 32),             # FT3
    (66.7, (-1425, 1320, 85),  (-1445, 1520, 0), 32),             # FT4
    (69.2, (-1480, 1410, 70),  (-1430, 1558, 4), 40),             # FT5
    (74.0, (-1660, 1350, 150), (-1450, 1530, 0), 30),             # FT6
    (78.4, (-1570, 1190, 170), (-1450, 1490, 0), 30),             # FT7 = g4 G0
]
# ---------------------------------------------------------------- g4 (M)
G4 = [
    (0.0,  (-1570, 1190, 170), (-1450, 1490, 0), 30),             # G0
    (1.8,  (-1495, 1135, 192), (-1100, 1320, 0), 30),             # G0b
    (4.1,  (-1380, 1060, 230), (-860, 760, 0),   29),             # G1
    (9.1,  (-760, 1010, 320),  (-80, 480, 0),    28),             # G2
    (12.4, (-400, 760, 290),   (-20, 260, 0),    28),             # G3
    (16.8, (-110, 430, 200),   (0, 40, 20),      30),             # G4
    (20.0, (-40, 330, 170),    (0, 0, 30),       32),             # G5
]
# ---------------------------------------------------------------- g5 (M), tight times
G5 = [
    (0.0,  (-40, 330, 170),   (0, 0, 30),       32),              # C0
    (4.0,  (-33, 290, 166),   (0, 5, 26),       32),              # C1
    (12.0, (-75, 370, 200),   (0, 40, 8),       28),              # C2
    (18.0, (-20, 470, 205),   (-15, 150, 0),    28),              # C3
    (22.0, (10, 530, 200),    (-330, 420, 5),   29),              # C3b
    (26.0, (40, 590, 195),    (-170, 790, 10),  30),              # C4
    (30.0, (10, 600, 170),    (-130, 815, 8),   32),              # C5
    (39.0, (-45, 690, 125),   (-138, 838, 6),   34),              # C6
    (42.0, (-48, 693, 125),   (-139, 837, 6),   34),              # C7
    (46.0, (-165, 690, 140),  (-400, 600, 5),   32),              # C7b
    (50.0, (-275, 655, 155),  (-262, 425, 0),   30),              # C8
    (56.5, (-270, 640, 150),  (-262, 422, 0),   33),              # C9
    (59.5, (-280, 655, 148),  (-258, 440, 0),   33),              # C9'
    (66.5, (-420, 455, 140),  (-236, 505, 10),  32),              # C9b
    (70.0, (-345, 455, 175),  (-185, 640, 15),  30),              # C10
]
# ---------------------------------------------------------------- g6 (M), tight times
G6 = [
    (0.0,  (-345, 455, 175), (-185, 640, 15),  30),               # H0
    (7.0,  (-330, 470, 150), (-225, 605, 10),  30),               # H1
    (14.5, (-255, 470, 120), (-205, 600, 6),   32),               # H2
    (19.5, (-198, 565, 100), (-187, 643, 1),   38),               # H3 (pitch 51 deg, cutaway)
    (33.5, (-194, 562, 100), (-186, 642, 1),   38),               # H3b
    (38.5, (-150, 495, 110), (-185, 620, 8),   32),               # H4
    (46.5, (-110, 515, 105), (-182, 617, 4),   35),               # H5
    (52.5, (-130, 540, 90),  (-180, 619, 4),   40),               # H6
    (59.5, (-90, 560, 115),  (-215, 615, 18),  32),               # H7
    (69.5, (220, 650, 130),  (345, 810, 0),    32),               # H8
]
# ---------------------------------------------------------------- g7 (M), PACE table
G7 = [
    (0.0,  (220, 650, 130),  (345, 810, 0),   32),
    (3.0,  (283, 740, 96),   (361, 850, 4),   38),
    (8.0,  (266, 720, 122),  (363, 855, 24),  32),
    (11.0, (296, 752, 90),   (360, 842, -1),  40),
    (13.0, (297, 753, 90),   (360, 842, -1),  40),
    (16.0, (330, 742, 105),  (350, 852, 10),  38),
    (19.5, (450, 805, 150),  (343, 862, 40),  36),
    (23.5, (250, 1010, 230), (20, 867, 48),   34),
    (27.0, (-20, 1046, 190), (-118, 846, 28), 34),
    (30.0, (-14, 1050, 188), (-118, 846, 28), 34),
    (33.0, (15, 1090, 165),  (-20, 905, 28),  33),
    (38.0, (30, 1100, 150),  (-20, 900, 32),  36),
    (42.0, (-20, 1000, 190), (-35, 730, 5),   32),
    (45.0, (-40, 960, 205),  (40, 540, 0),    30),                # = C15 = g8 K0
]
# ---------------------------------------------------------------- g8 (M), TIGHT column (B1 and E1 use the tight look-at variants)
G8 = [
    (0.0,  (-40, 960, 205),  (40, 540, 0),     30),               # K0
    (6.0,  (-40, 760, 210),  (230, 320, 0),    28),               # K2
    (12.0, (120, 470, 150),  (290, 262, 8),    35),               # K3
    (15.5, (160, 420, 120),  (288, 262, 10),   42),               # K4
    (19.0, (175, 395, 105),  (282, 215, 12),   40),               # K5
    (28.0, (95, 290, 105),   (275, 150, 12),   38),               # C1
    (38.0, (40, 230, 100),   (180, 62, 12),    38),               # C2
    (45.0, (-60, 175, 95),   (40, 24, 12),     40),               # C3
    (49.5, (-75, 150, 90),   (3, 14, 12),      42),               # S1
    (54.0, (-95, 225, 135),  (0, 20, 40),      32),               # S2
    (58.0, (-105, 245, 140), (0, 30, 15),      34),               # L1
    (62.0, (-60, 330, 200),  (-280, 170, 10),  30),               # B1 (new), tight look-at
    (66.0, (-60, 430, 290),  (-410, 800, 20),  28),               # M1
    (71.0, (150, 600, 190),  (-120, 420, 0),   30),               # E1, tight look-at
    (75.0, (200, 760, 240),  (-20, 300, 0),    28),               # E2 = END
    (76.0, (200, 760, 240),  (-20, 300, 0),    28),               # guide key +1 s
]

S = ST.seam
KEYS = {
    "g1": dict(frame="W", keys=G1, v_in=None, v_out=None),
    "g2": dict(frame="W", keys=G2, v_in=(0, 0, 0), v_out=S("g2_g3")["vel"]),
    "g3": dict(frame="M", groups=dict(
        flight=dict(frame="W", keys=G3_FLIGHT_W, t=(0.0, 12.9)),
        camps=dict(frame="M", keys=G3_CAMPS_M, v_in=None, v_out=None, t=(12.9, 31.3)),
        march=dict(frame="M", cam_in=CAM_IN, cam_out=CAM_OUT, t=(31.3, 49.3)),
        to_camp=dict(frame="M", keys=G3_TO_CAMP_M, v_in=CAM_OUT["vel"], look_v_in=CAM_OUT["look_vel"], v_out=S("g3_g4")["vel"], t=(49.3, 78.4)))),
    "g4": dict(frame="M", keys=G4, v_in=S("g3_g4")["vel"], v_out=S("g4_g5")["vel"]),
    "g5": dict(frame="M", keys=G5, v_in=S("g4_g5")["vel"], v_out=S("g5_g6")["vel"]),
    "g6": dict(frame="M", keys=G6, v_in=S("g5_g6")["vel"], v_out=S("g6_g7")["vel"]),
    "g7": dict(frame="M", keys=G7, v_in=S("g6_g7")["vel"], v_out=S("g7_g8")["vel"]),
    "g8": dict(frame="M", keys=G8, v_in=S("g7_g8")["vel"], v_out=None),       # ends via the guide key at 76.0
}

def cam(seg, **over):
    """kwargs for CamPath for a flat segment (g1, g2, g4..g8) in its own frame; over = overrides (e.g. v_in=None)."""
    k = KEYS[seg]; d = dict(keys=k["keys"], v_in=k.get("v_in"), v_out=k.get("v_out"), look_v_in=k.get("look_v_in"), look_v_out=k.get("look_v_out"))
    d.update(over); return d

# ---------------------------------------------------------------- runs (global-time channels) for A3
def _M(keys, frame, dt=0.0):
    out = []
    for t, c, l, ln in keys:
        if frame == "W": c, l = ST.W_to_M(c), ST.W_to_M(l)
        out.append((round(t + dt, 6), tuple(c), tuple(l), ln))
    return out

def _join(parts):
    """Concatenate key lists, dropping a first key that duplicates the previous list's last key (same time)."""
    out = []
    for p in parts:
        for k in p:
            if out and abs(k[0] - out[-1][0]) < 1e-6:
                continue
            out.append(k)
    return out

def run_B_keys(guide=True):
    """FT0 -> g8 E2 as ONE channel, global seconds (FT0 = g3 start + 49.3).  Lead-in guide at FT0 - 1 s per bible A3."""
    g3 = ST.START["g3"]; ks = []
    ks.append(_M([(49.3, *G3_TO_CAMP_M[0][1:])], "M", g3))
    parts = [_M(G3_TO_CAMP_M[1:], "M", g3)]
    for g, K in (("g4", G4), ("g5", G5), ("g6", G6), ("g7", G7), ("g8", G8)):
        parts.append(_M(K, "M", ST.START[g]))
    keys = _join(ks + parts)
    if guide:
        t, c, l, ln = keys[0]
        keys.insert(0, (t - 1.0, (260, -1145, 618), l, ln))
    return keys

def run_A2_keys():
    """g2 K0 .. g3 CAM_IN + guide 31.8 as ONE channel, global seconds."""
    g2, g3 = ST.START["g2"], ST.START["g3"]
    return _join([_M(G2, "W", g2), _M(G3_FLIGHT_W, "W", g3), _M(G3_CAMPS_M, "M", g3)])

BIBLE = {   # bible-quoted peaks (A3 and per-segment 'Verified' lines): m/s, deg/s
    "g1": (246, 22), "g2": (78, 30), "g3_flight": (412, None), "g3_to_camp": (298, None), "g4": (141, 32), "g5": (43, 29),
    "g6": (39, 25), "g7": (104, 26), "g8": (67, 30), "g3_camps": (None, 32), "A2": (78, 30), "B": (141, 32)}

NOTES = [   # appended to design_specs/camcheck_report.md
    "Agree with the bible within rounding: g1 129 m/s; g3 flight pure PCHIP 412 m/s (profile run 372 vs the profile's 369); g3 flight-to-camp 298 m/s; g4 141 m/s / 31.5 deg/s (bible 32); g5 43 / 29; g7 104 / 26.5 (26); g8 67 / 29.9 (30), min height 89 m (bible says 89 too); g3 camps pan 31.9 deg/s (bible 32).",
    "Disagree: g2 alone peaks at 54 m/s (bible 78): the bible figure comes from the A2 run where g2 is one channel with the g3 flight keys; with the A2 seam as v_out (0,45,8) g2 ends smoothly at 46 m/s. g6 yaw peaks at 18.8 deg/s (bible 25): the bible number is from the single run B; with seam tangents g6 alone is calmer.",
    "Over the A3 limits (flags in the table): YAW > 30 deg/s: g3 camps P2->P3 pan 31.9 (26.4 s local), g4 G0b swing 31.5 (2.6 s), run A2 32.0, run B 31.7 (the same two spots; the bible itself quotes 32). All are < 3 % over; none is a flip.",
    "g2: pitch 49 deg in the first 0.7 s (K0 aimed at the Yeager house from 114 m, A3 allows 45); g7: pitch 46 deg at 20.1 s (a 0.07 s window); g8: height 89 m at 49.3 s (A3 minimum 90, 1 m short at S1); g1: pitch -1..57 deg: the tree shots K0/K1 are locked close-ups and K5 (pitch 9 deg, 50 mm hold on the Colossal at 500 m) is below the 17 deg pitch rule; flag kept for the record.",
    "g3_to_camp with the march846 CAM_OUT velocity as v_in (0,95,22) overshoots to 681 m (> 650) at 50-53 s because the 640 m start key climbs at 22 m/s into FT1 (520 m); the bible's lead-in guide key at FT0-1 s (run B) peaks at 640 m. Use the guide key, or lower FT0/FT1 height by ~40 m.",
    "A2/B as ONE channel also match the per-segment numbers (g2 + flight: 412 m/s is the flight); g3 flight 0-17.7 must be driven with camchan.speed_profile (45 -> 369 m/s ramp over 0-3.7, cruise to 9.0, constant decel to rest at 17.7), as the bible says.",
    "Assumptions in the transcription: g1 K0 (3 m from the kids, same line of sight as K1, 45 mm) and K1 (render_fast fallback flight_at(900): cam (-480, 338, 7.2), look (-300, 0, 10.6), 50 mm) are not numbers in the bible; g3 lens at H2..H3 held at 40 (bible: '28->40' then '40->28'), CAM_IN 27; g3 look-at rate at CAM_IN (0,-111,0) and at CAM_OUT (0,283,13) from march846.CAM_KEYS secants (the bible gives only the camera velocities); the g1 guide key at 33.0 duplicates K12 (v_out is left unset: PCHIP gives rest at 32.0).",
]

ALL_CHECKS = ["g1", "g2", "g3_flight", "g3_flight_prof", "g3_camps", "g3_to_camp", "g4", "g5", "g6", "g7", "g8", "A2", "B", "B_vin"]

def path(name):
    """(CamPath, check kwargs, info) for a check name."""
    q = dict(bible_speed=BIBLE.get(name, (None, None))[0], bible_yaw=BIBLE.get(name, (None, None))[1])
    kw = dict(limits={}); lim = kw["limits"]
    if name in ("g1", "g2", "g4", "g5", "g6", "g7", "g8"):
        p = CamPath(**cam(name))
        kw["t0"], kw["t1"] = 0.0, ST.DUR[name]
        if name == "g1":
            lim.update(hmin_from=3.9, under=1.0)
            q["comment"] = "K0/K1 locked tree framing are not numbers in the bible (K1 = render_fast fallback, K0 approximated); height rule applied from K2 (3.9 s); look-under test off (K0 look is 3 m ahead of the camera on purpose, same bearing as K1)."
        if name == "g6":
            lim.update(pitch=(17, 52)); q["comment"] = "H3/H3b are the 51 deg cutaway: pitch allowed to 52."
        return p, kw, q
    if name == "g3_flight":
        p = CamPath(_M(G3_FLIGHT_W, "W") + _M(G3_CAMPS_M[:2], "M"), v_in=S("g2_g3")["vel"])
        kw.update(t0=0.0, t1=17.7); lim.update(hmin=90)
        q["comment"] = "FA0..FA3, FA4, H as pure PCHIP key timing (v_in = g2 seam 45 m/s). The bible says to drive this with the explicit profile instead (g3_flight_prof)."
        return p, kw, q
    if name == "g3_flight_prof":
        ks = _M(G3_FLIGHT_W, "W") + _M(G3_CAMPS_M[:2], "M")
        p = CamPath(ks, profile=speed_profile(45.0, 369.0, 3.7, 9.0, 17.7))
        kw.update(t0=0.0, t1=17.7); lim.update(speed=400)
        q["bible_speed"] = 369; q["comment"] = "explicit g3 profile: ramp 45->369 m/s over 0-3.7, cruise to 9.0, constant deceleration to rest at H (17.7); speed limit set to 400 for this run."
        return p, kw, q
    if name == "g3_camps":
        k = G3_CAMPS_M[:-1]   # up to CAM_IN, seam tangents instead of the guide key
        p = CamPath(k, v_in=(0, 0, 0), v_out=CAM_IN["vel"], look_v_out=CAM_IN["look_vel"])
        kw.update(t0=17.7, t1=31.3)
        q["comment"] = "H (17.7, at rest) to CAM_IN with v_out = (16.7,-61.1,5.6) and the look-point rate of march846 CAM_KEYS[0..1]. FA4->H (12.9-17.7) is inside the flight profile."
        return p, kw, q
    if name == "g3_to_camp":
        p = CamPath(**dict(keys=G3_TO_CAMP_M, v_in=CAM_OUT["vel"], look_v_in=CAM_OUT["look_vel"], v_out=S("g3_g4")["vel"]))
        kw.update(t0=49.3, t1=78.4); lim.update(hmin=65, speed=300)
        q["comment"] = "FT3-FT5 sit at 95/85/70 m over the 104th camp by design: height floor 65, speed limit 300 (bible quotes 298 m/s for this flight)."
        return p, kw, q
    if name == "A2":
        p = CamPath(run_A2_keys(), v_in=(0, 0, 0))
        kw.update(t0=ST.START["g2"], t1=ST.START["g3"] + 31.3)
        q["comment"] = "g2 + g3 flight + camps up to CAM_IN as ONE pure-PCHIP channel (bible A2 run), guide key 31.8; the flight part is the 412 m/s case (g3 drives it with the explicit profile)."
        lim.update(speed=None)
        return p, kw, q
    if name in ("B", "B_vin"):
        keys = run_B_keys(guide=(name == "B"))
        if name == "B":
            p = CamPath(keys)
        else:
            p = CamPath(keys, v_in=CAM_OUT["vel"], look_v_in=CAM_OUT["look_vel"])
        kw.update(t0=ST.START["g3"] + 49.3, t1=ST.TOTAL)
        q["comment"] = ("FT0 -> g8 E2 as ONE channel, " + ("lead-in guide key at FT0-1 s (look-at = FT0 look), bible A3." if name == "B" else "with v_in = march846 CAM_OUT velocity instead of the guide key.") +
                        " Heights: FT3-FT5 low by design (70-95 m); the bible quotes the peaks per segment (g4 141/32 ... g8 67/30).")
        lim.update(hmin=65, speed=300)
        return p, kw, q
    raise KeyError(name)

if __name__ == "__main__":
    for n in ST.ORDER:
        print(n, ST.DUR[n], len(KEYS[n].get("keys", [])) if "keys" in KEYS[n] else "groups")
