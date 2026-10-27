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
# g1 v4 (owner 10/27 07:34): 0-11 s = renders/opening_preview_v4.mp4 (render_fast.py @ 791f565, keys() 2.6-5.45 verbatim:
# tree, swoosh over the inner wall, down the avenue at 60-72 m), then the Colossal zoom-in as a DOLLY (lens cap 60 mm; the
# reference zoomed 46 -> 95 -> 210 mm from ~290 m): ~80 m from the head at 8.0 s so head + gripping hands fill ~1/3 of the
# frame; pull back to the reference's kick framing (10.0 / 11.0 verbatim, plus a small zoom-in at the kick).  After the kick
# the video clock runs 2 -> 5.5 (segtime G1_PLAN): fly west over the pour to the Yeager ruin, small zoom-in on Carla, seam.
# Times are g1 LOCAL seconds (= video seconds up to 11.0).  The v3 keys are kept below as G1_V3 (record only).
G1 = [
    (0.0, (-476, 330.5, 2.4), (-474.6, 327.9, 1.2), 45),
    (2.0, (-480, 338, 7.2), (-300, 0, 10.6), 50),
    (2.05, (-480, 338, 7.2), (-300, 0, 10.6), 50),
    (2.6, (-430, 290, 28), (-150, 120, 14), 32),      # ref: leave the tree, up and toward the gate
    (3.2, (-220, 170, 46), (0, 0, 45), 28),           # ref: over the meadow / road, climbing (swoosh)
    (3.55, (-85, 85, 63), (0, -150, 40), 27),
    (3.8, (-15, 18, 72), (-2, -450, 30), 27),         # ref: up and over the inner wall top
    (4.35, (-3, -200, 65), (-7, -700, 42), 30),       # ref: gliding down along the avenue
    (4.9, (-6, -385, 60), (-7, -720, 52), 46),        # ref: past the plaza, down the gate street (bolt 4.62)
    (5.45, (-6, -510, 57.5), (-7, -732, 55), 54),     # dolly toward the wall while the head rises (ref: 95 mm from 307 m)
    (6.6, (-6, -628, 55.5), (-7, -733, 54.5), 58),
    (7.45, (-6, -648, 54), (-7, -733, 54.5), 60),     # head + both hands ~1/3 of the frame (ref 8.0 framing; COL_HEAD 1.3)
    (8.0, (-6, -651, 54), (-7, -733, 54), 60),
    (10.0, (20, -330, 120), (0, -690, 18), 40),       # ref: pull back, gate and wall in frame
    (11.0, (25, -325, 128), (0, -690, 24), 43),       # ref: the kick (11.0); small zoom-in 40 -> 47 (look a bit higher: the Colossal stays in frame)
    (12.0, (22, -328, 136), (-4, -684, 20), 47),
    (13.6, (-2, -345, 146), (-30, -652, 6), 42),      # dust dome, the Colossal vanishes, Dina runs in from the breach
    (16.3, (-70, -368, 144), (-85, -640, 4), 36),     # smoke columns, the pour
    (20.0, (-160, -402, 126), (-150, -615, 3), 33),
    (23.7, (-214, -446, 108), (-163, -598, 3), 33),
    (25.5, (-228, -458, 102), (-165, -592, 4), 37),   # Carla: small zoom-in (bend 25.5, grab 26.6, bite 28.4)
    (27.0, (-236, -463, 99), (-168, -590, 6), 48),
    (28.9, (-244, -466, 97), (-168, -590, 5), 48),
    (32.0, (-254, -468, 95), (-167, -590, 2), 28),    # = SEAM_IN (g2 K0), at rest
    (33.0, (-254, -468, 95), (-167, -590, 2), 28),    # guide key (seam at rest)
]
G1_V3 = [   # g1 v3 (master v1), superseded by v4
    (0.0, (-476, 330.5, 2.4), (-474.6, 327.9, 1.2), 45),
    (2.0, (-480, 338, 7.2), (-300, 0, 10.6), 50),
    (2.05, (-480, 338, 7.2), (-300, 0, 10.6), 50),
    (3.17, (-455, 300, 45), (-150, -400, 10), 40),   # v3 (cloud QA 18:10): constant-speed swoosh (accel 1.4 s, cruise ~132 m/s, decel 1.6 s), peak 147 m/s
    (4.05, (-400, 215, 95), (-40, -560, 0), 31),
    (5.45, (-300, 60, 112), (-25, -620, 8), 32),
    (7.38, (-190, -170, 108), (-12, -700, 35), 38),
    (8.74, (-120, -330, 100), (-8, -724, 48), 46),
    (10.0, (-95, -390, 98), (-7, -728, 52), 50),   # hold ~360 m from the head (far observer, owner 16:51): head + hands ~6-8 % of the frame
    (10.55, (-72, -414, 96), (-6, -728, 50), 50),
    (11.25, (-58, -428, 98), (-3, -715, 20), 42),   # kick from the town side ~290 m: dust dome + debris arcs
    (12.5, (-45, -440, 105), (0, -705, 20), 36),
    (14.5, (-25, -450, 110), (-12, -690, 14), 34),
    (18.0, (-40, -480, 105), (-55, -665, 6), 32),
    (22.0, (-222, -500, 97), (-168, -592, 3), 30),   # fly left, then a slow drift 3-6 m/s NW of the Yeager ruin (Carla's street side, pour behind / frame-left)
    (27.0, (-240, -484, 96), (-168, -590, 3), 29),
    (32.0, (-254, -468, 95), (-167, -590, 2), 28),   # = SEAM_IN (unchanged since v2: g2 builds against it)
    (33.0, (-254, -468, 95), (-167, -590, 2), 28),   # guide key (seam at rest)
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
def _lk(c, yaw, R):                    # look-at point on the ground at horizontal range R, compass-free yaw (deg, math)
    import math as _m
    return (round(c[0] + R * _m.cos(_m.radians(yaw)), 1), round(c[1] + R * _m.sin(_m.radians(yaw)), 1), 0.0)
G2 = [   # v5 (owner 10/27 07:34): Reiner 1.5x faster in local time (3x on screen with the 2x video clock), impact 9.0;
         # the run keys keep v4's framing relative to him (front 3/4 lock ~150 m, side 3/4 from the W/SW at the hit with a
         # small zoom-in 50 -> 58 mm); after the steaming stand the camera climbs NW for an AERIAL of burning Shiganshina at
         # dusk (19.2-22.4), then swings east over the quays / ferries and north to the unchanged g3 seam (yaw spread evenly).
         # Video clock (segtime.TMAP g2, slope 2): <= 252 m/s, <= 57 deg/s, pitch 22-46, lens 28-58 (seg_g2.vcheck()).
    (0, (-254, -468, 95), (-167, -590, 2), 28),   # SEAM_IN v2 (= g1 K12, at rest)
    (2.4, (-180, -322, 108), (-45, -360, 6), 37),   # swoop NE over the roofs, he enters frame from the right
    (4.4, (-86, -158, 114), (0, -215, 9), 48),   # LOCK: front three-quarter (ahead + west of him), ~150 m, ~115 px
    (6.0, (-95, -75, 115), (0, -146, 9), 49),   # the face ricochet at 6.15 seen from the front
    (7.6, (-130, -82, 104), (0, -74, 9), 50),   # he runs past the camera: front 3/4 -> side
    (9.0, (-150, -80, 96), (0, -13, 11), 58),   # IMPACT: side three-quarter from the W/SW, 27 deg down, small zoom-in
    (10.3, (-150, -10, 140), (0, 28, 9), 48),   # rise over the wall line: he bursts out of the north face
    (11.3, (-140, 40, 128), (0, 46, 9), 46),   # north side: the slide ends at y +46
    (13.6, (-85, 140, 118), (0, 40, 11), 50),   # from the north: him steaming + the dark arch breach behind (small zoom-in)
    (15.6, (-95, 170, 135), (0, 30, 12), 48),   # slow drift, then climb
    (19.2, (-230, 330, 400), (-5, -240, 0), 28),   # AERIAL: burning Shiganshina beyond the wall, the breach in the foreground
    (22.4, (-185, 350, 395), (40, -235, 0), 28),   # drift east over the burning town
    (25.0, (-90, 360, 350), _lk((-90, 360), -38, 640), 29),   # swing east: the canal, quays and ferries
    (27.6, (25, 385, 300), _lk((25, 385), 10, 360), 29),   # the canal, quays and ferries below
    (30.0, (118, 425, 262), _lk((118, 425), 58, 520), 28.5),   # turning north toward Trost
    (32, (175, 480, 240), (228, 1050, 0), 28),   # = g2->g3 seam (segtime g2_g3), unchanged
]
# ---------------------------------------------------------------- g3  (group-local seconds)
G3_FLIGHT_W = [                                                       # FA0..FA3, frame W
    (0.0,  (175, 480, 240),  (228, 1050, 0), 28),
    (3.7,  (300, 1250, 320), (330, 2000, 0), 28),
    (7.3,  (380, 2600, 380), (250, 3700, 0), 28),
    (10.6, (200, 3750, 320), (-100, 4600, 0), 30),
]
# camps, frame M.  g3 v5 (owner 10/27 07:34: farm faster + clearer, NO winter, straight to 846): H looks out at the clearing
# beyond Rose (the farm time-lapse), H2 a small zoom-in on it (38 mm), then ONE turn via the west (~115 deg, was 160) over
# the relief complex and the 846 avenue to CAM_IN.  seg_g3.py builds its camera from these rows (times = seg_g3.BEATS).
G3_CAMPS_M = [
    (12.9,  (60, 170, 300),    (-268, 805, 0),   30),             # FA4 = W (60, 4300, 300)
    (17.7,  (-145, 605, 250),  (-420, 1250, 0),  28),             # H  (drift 5 m/s), looking out at the clearing
    (20.0,  (-170, 640, 262),  (-480, 1330, 0),  38),             # H2 small zoom-in: the clearing planted
    (21.5,  (-160, 620, 256),  (-760, 1000, 0),  35),             # P1 the turn via the west (look-at direction monotonic)
    (22.9,  (-110, 550, 245),  (-760, 420, 0),   32),             # P2 the relief complex / west quarter
    (24.2,  (-20, 440, 220),   (-400, 60, 0),    30),             # P3 the avenue fills with the 846 crowd
    (26.6,  (170, 170, 125),   (-10, -60, 0),    27),             # CAM_IN (= segtime.G3_MARCH[0])
    (27.1,  (178.4, 139.5, 127.8), (-10, -115.5, 0), 27),         # guide = CAM_IN + 0.5 v (look: + 0.5 look-velocity)
]
CAM_IN = dict(frame="M", t=ST.G3_MARCH[0], pos=(170, 170, 125), look=(-10, -60, 0), lens=27.0, vel=(16.7, -61.1, 5.6), look_vel=(0, -111.1, 0))
# g3 v5: march846's ORIGINAL spline is restored inside g3 (owner), so CAM_OUT leaves with its original climb (0, 95, 22) and
# its look-at rate (0, 283.3, 13.3) (march846.CAM_KEYS secant).
CAM_OUT = dict(frame="M", t=ST.G3_MARCH[1], pos=(260, -1050, 640), look=(0, 150, 40), lens=28.0, vel=(0, 95, 22), look_vel=(0, 283.3, 13.3))
G3_TO_CAMP_M = [   # g3 v5: a shorter, higher crossing (the video clock eases 1 -> 2 over its first 1.2 video s), FT4 a small zoom-in on
                   # the enlistment + rigs, FT6 (the seasons orbit) dropped; FT7 = g4 G0 unchanged.  Times = seg_g3.BEATS FT*.
    (44.6, (260, -1050, 640),  (0, 150, 40),     28),             # FT0 = march846.CAM_OUT
    (49.4, (-250, 260, 540),   (-950, 1300, 0),  28),             # FT1
    (52.6, (-1160, 980, 320),  (-1450, 1520, 0), 30),             # FT2
    (55.0, (-1395, 1185, 185), (-1452, 1512, 0), 34),             # FT3 the camp: enlistment + rigs
    (57.0, (-1420, 1250, 168), (-1448, 1530, 0), 44),             # FT4 small zoom-in (Shadis, Eren upside down, Mikasa)
    (58.4, (-1480, 1290, 155), (-1442, 1548, 4), 34),             # FT5 seasons (no winter) -> dusk
    (61.8, (-1570, 1190, 170), (-1450, 1490, 0), 30),             # FT7 = g4 G0
]
# ---------------------------------------------------------------- g4 (M)
G4 = [
    (0.0,  (-1570, 1190, 170), (-1450, 1490, 0), 30),             # G0
    (2.0,  (-1495, 1135, 192), (-1120, 1330, 0), 30),             # G0b (g4 agent 10/27: 1.8 -> 2.0 s, look (-1100,1320) -> (-1120,1330))
    (4.1,  (-1380, 1060, 230), (-900, 880, 0),   29),             # G1  (look (-860,760) -> (-900,880)): opening swing 31.5 -> 27.7 deg/s
    (9.1,  (-770, 870, 330),   (-40, 330, 0),    34),             # G2  (g4 v2, coordinator 10/27: high oblique (pitch up to 36)
    (12.6, (-380, 615, 365),   (-5, 40, 0),      40),             # G3   over the avenue + outer gate + south road while the
    (15.0, (-210, 435, 330),   (0, 10, 5),       42),             # G3b  Survey Corps passes 10-15 s; was G2 (-760,1010,320)->(-80,480) 28,
                                                                  #      G3 12.4 (-400,760,290)->(-20,260) 28)
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
G6 = [   # g6 agent 10/27: owner 16:51 "FAR is better" -> the whole segment stays at the g5 seam distance (230-290 m, 30-34 mm);
         # bible look-at targets kept, positions pulled back (bible H3 was 127 m / 38 mm at 51 deg pitch, H6 90 m / 40 mm)
    (0.0,  (-345, 455, 175), (-185, 640, 15),  30),               # H0 = g5 C10
    (7.0,  (-332, 478, 169), (-225, 605, 10),  30),               # H1 approach, Jean's squad, climbers
    (14.5, (-318, 484, 158), (-210, 605, 6),   31),               # H2 tackle aftermath, rampage
    (19.5, (-282, 482, 165), (-190, 630, 3),   33),               # H3 cutaway from the SW (41 deg; sees the ring over the cut wall)
    (33.5, (-272, 479, 165), (-188, 636, 2),   33),               # H3b drift through the lift op, swarm in the lower frame
    (38.5, (-215, 440, 170), (-188, 622, 8),   32),               # H4 roar before the wing, cadets on the wing roof
    (46.5, (-150, 450, 165), (-183, 617, 4),   33),               # H5 collapse + skid along the wing base (owner wing ref, from the sky)
    (52.5, (-150, 455, 160), (-180, 619, 4),   34),               # H6 Eren on the nape, Mikasa drops in
    (59.5, (-110, 470, 170), (-215, 615, 18),  31),               # H7 tableau on the keep roof walk + corpses
    (64.5, (40, 560, 165),   (-5, 745, 12),    32),               # H7b look-at guide (exit pitch <= 45)
    (69.5, (220, 650, 130),  (345, 810, 0),    32),               # H8 = g7 C0
]
# ---------------------------------------------------------------- g7 (M), PACE table
# g7 agent 10/27: the basin is on Rose's NORTH face (owner 15:25 10/26), so 0-23.5 s is re-keyed on the north side (the
# bible keys mirrored Y' = 1740 - Y, then smoothed): C1 crosses the wall WEST of the basin, FIRE moves 3.0 -> 6.0 (a 3 s
# transit cannot turn the view 100 deg under 30 deg/s), no push-in (FIRE/salute 166-170 m at 38 mm, steam 196 m at 34 mm).
# Look-at: enters with g6's look-at velocity (look_v_in, computed below) and arrives at rest at C15 (g8 K0 starts at rest).
G7 = [
    (0.0,  (220, 650, 130),  (345, 810, 0),   32),                # C0 = g6 H8 (seam, v_in (25, 8, 0))
    (3.0,  (236, 840, 148),  (398, 880, 0),   33),                # C1 over the Rose top west of the basin
    (6.0,  (266, 992, 102),  (361, 890, 4),   38),                # C2 FIRE, from the Garrison side (canal + gate on the LEFT)
    (10.0, (252, 1012, 122), (363, 885, 22),  34),                # C3 steam burst + column (eases back, no push-in)
    (12.5, (272, 996, 102),  (360, 893, 0),   38),                # C4 salute hold
    (15.0, (275, 997, 102),  (358, 896, 0),   38),                # C5 Pyxis catches the arm, walks down the bank
    (17.0, (318, 1012, 112), (346, 886, 10),  38),                # C6 to the basket
    (20.0, (330, 1052, 160), (338, 878, 42),  36),                # C7 rising with the basket to the Rose top
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
    "g2": dict(frame="W", keys=G2, v_in=(0, 0, 0), v_out=S("g2_g3")["vel"], look_v_out=(0.0, 0.0, 0.0)),   # look-at at rest = g3 FA0 (g3 has no look_v_in)
    "g3": dict(frame="M", groups=dict(
        flight=dict(frame="W", keys=G3_FLIGHT_W, t=(0.0, 12.9)),
        camps=dict(frame="M", keys=G3_CAMPS_M, v_in=None, v_out=None, t=(12.9, CAM_IN["t"])),
        march=dict(frame="M", cam_in=CAM_IN, cam_out=CAM_OUT, t=(CAM_IN["t"], CAM_OUT["t"])),
        to_camp=dict(frame="M", keys=G3_TO_CAMP_M, v_in=CAM_OUT["vel"], look_v_in=CAM_OUT["look_vel"], v_out=S("g3_g4")["vel"],
                     look_v_out=(0.0, 0.0, 0.0), t=(CAM_OUT["t"], ST.DUR["g3"])))),   # g4 agent 10/27: look-at at rest at FT7 = g4 G0 (g4 starts its look-at from rest)
    "g4": dict(frame="M", keys=G4, v_in=S("g3_g4")["vel"], v_out=S("g4_g5")["vel"], look_v_out=(0.0, 0.0, 0.0)),   # look-at at rest = g5 C0 (g5 has no look_v_in)
    "g5": dict(frame="M", keys=G5, v_in=S("g4_g5")["vel"], v_out=S("g5_g6")["vel"]),
    "g6": dict(frame="M", keys=G6, v_in=S("g5_g6")["vel"], v_out=S("g6_g7")["vel"]),
    "g7": dict(frame="M", keys=G7, v_in=S("g6_g7")["vel"], v_out=S("g7_g8")["vel"]),
    "g8": dict(frame="M", keys=G8, v_in=S("g7_g8")["vel"], v_out=None),       # ends via the guide key at 76.0
}

def cam(seg, **over):
    """kwargs for CamPath for a flat segment (g1, g2, g4..g8) in its own frame; over = overrides (e.g. v_in=None)."""
    k = KEYS[seg]; d = dict(keys=k["keys"], v_in=k.get("v_in"), v_out=k.get("v_out"), look_v_in=k.get("look_v_in"), look_v_out=k.get("look_v_out"))
    d.update(over); return d

def _look_vel_end(seg, h=1e-3):
    """Look-at velocity (m/s) at a segment's last key (the A2 table only gives the camera's)."""
    p = CamPath(**cam(seg)); t1 = KEYS[seg]["keys"][-1][0]
    return tuple(float(x) for x in (p.eval(t1)[1] - p.eval(t1 - h)[1]) / h)

KEYS["g7"]["look_v_in"] = _look_vel_end("g6")      # g7 agent: the look-at crosses the g6/g7 seam without a jerk
KEYS["g7"]["look_v_out"] = (0.0, 0.0, 0.0)          # g8 K0's look-at starts at rest (g8 has no look_v_in)

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
    """FT0 -> g8 E2 as ONE channel, global seconds (FT0 = g3 start + CAM_OUT t).  Lead-in guide at FT0 - 1 s per bible A3."""
    g3 = ST.START["g3"]; ks = []
    ks.append(_M([(CAM_OUT["t"], *G3_TO_CAMP_M[0][1:])], "M", g3))
    parts = [_M(G3_TO_CAMP_M[1:], "M", g3)]
    for g, K in (("g4", G4), ("g5", G5), ("g6", G6), ("g7", G7), ("g8", G8)):
        parts.append(_M(K, "M", ST.START[g]))
    keys = _join(ks + parts)
    if guide:
        t, c, l, ln = keys[0]
        keys.insert(0, (t - 1.0, (260, -1145, 618), l, ln))
    return keys

def run_A2_keys():
    """g2 K0 .. g3 CAM_IN + guide (CAM_IN + 0.5 s) as ONE channel, global seconds."""
    g2, g3 = ST.START["g2"], ST.START["g3"]
    return _join([_M(G2, "W", g2), _M(G3_FLIGHT_W, "W", g3), _M(G3_CAMPS_M, "M", g3)])

BIBLE = {   # bible-quoted peaks (A3 and per-segment 'Verified' lines): m/s, deg/s
    "g1": (246, 22), "g2": (78, 30), "g3_flight": (412, None), "g3_to_camp": (298, None), "g4": (141, 32), "g5": (43, 29),
    "g6": (39, 25), "g7": (104, 26), "g8": (67, 30), "g3_camps": (None, 32), "A2": (78, 30), "B": (141, 32)}

NOTES = [   # appended to design_specs/camcheck_report.md
    "g3 v5 (agent 10/27 PM, owner feedback): the rendered camera is seg_g3.CAM_M on the VIDEO clock segtime.TMAP['g3'] (python aot/seg_g3.py prints the local and the video checks): flight 0-17.7 unchanged; farm hold + one ~120 deg turn to CAM_IN (66 deg/s video, 33 local); march846's ORIGINAL spline restored at real time (owner: 458 m/s, 57 deg/s, 81 m, pitch 11 accepted); CAM_OUT climbs (0,95,22) again (to camp peaks 677 m, 858 m/s video at ~500 m, v/h 2.0 < the flight north's 2.5); camp 155-185 m.",
    "Agree with the bible within rounding: g1 129 m/s; g3 flight pure PCHIP 412 m/s (profile run 372 vs the profile's 369); g3 flight-to-camp 298 m/s; g4 141 m/s / 31.5 deg/s (bible 32); g5 43 / 29; g7 104 / 26.5 (26); g8 67 / 29.9 (30), min height 89 m (bible says 89 too); g3 camps pan 31.9 deg/s (bible 32).",
    "Disagree: g2 alone peaks at 54 m/s (bible 78): the bible figure comes from the A2 run where g2 is one channel with the g3 flight keys; with the A2 seam as v_out (0,45,8) g2 ends smoothly at 46 m/s. g6 yaw peaks at 18.8 deg/s (bible 25): the bible number is from the single run B; with seam tangents g6 alone is calmer.",
    "Over the A3 limits (flags in the table): YAW > 30 deg/s: g3 camps P2->P3 pan 31.9 (26.4 s local), g4 G0b swing 31.5 (2.6 s), run A2 32.0, run B 31.7 (the same two spots; the bible itself quotes 32). All are < 3 % over; none is a flip.",
    "g2 (v2 10/27): new seam K0 (-254,-468,95), K1 a 3.0 s pan, lock from 6.0 s: peak yaw 68 -> <30 deg/s (see camchan --check g2). g7: pitch 46 deg at 20.1 s (a 0.07 s window); g8: height 89 m at 49.3 s (A3 minimum 90, 1 m short at S1); g1: pitch -1..57 deg: the tree shots K0/K1 are locked close-ups and K5 (pitch 9 deg, 50 mm hold on the Colossal at 500 m) is below the 17 deg pitch rule; flag kept for the record.",
    "g3_to_camp with the march846 CAM_OUT velocity as v_in (0,95,22) overshoots to 681 m (> 650) at 50-53 s because the 640 m start key climbs at 22 m/s into FT1 (520 m); the bible's lead-in guide key at FT0-1 s (run B) peaks at 640 m. Use the guide key, or lower FT0/FT1 height by ~40 m.",
    "A2/B as ONE channel also match the per-segment numbers (g2 + flight: 412 m/s is the flight); g3 flight 0-17.7 must be driven with camchan.speed_profile (45 -> 369 m/s ramp over 0-3.7, cruise to 9.0, constant decel to rest at 17.7), as the bible says.",
    "Assumptions in the transcription: g1 K0 (3 m from the kids, same line of sight as K1, 45 mm) and K1 (render_fast fallback flight_at(900): cam (-480, 338, 7.2), look (-300, 0, 10.6), 50 mm) are not numbers in the bible; g3 lens at H2..H3 held at 40 (bible: '28->40' then '40->28'), CAM_IN 27; g3 look-at rate at CAM_IN (0,-111,0) and at CAM_OUT (0,283,13) from march846.CAM_KEYS secants (the bible gives only the camera velocities); the g1 guide key at 33.0 duplicates K12 (v_out is left unset: PCHIP gives rest at 32.0).",
]

ALL_CHECKS = ["g1", "g2", "g3", "g3_flight", "g3_flight_prof", "g3_camps", "g3_march", "g3_to_camp", "g4", "g5", "g6", "g7", "g8", "A2", "B", "B_vin"]

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
            lim.update(pitch=(17, 45)); q["comment"] = "H3/H3b cutaway pulled back to <= 45 deg pitch (owner limit 17-45, g6 agent 10/27)."
        return p, kw, q
    if name in ("g3", "g3_march"):
        import seg_g3 as G3                                  # the segment's own camera (pure python): flight profile | camps |
        if name == "g3":                                     # re-driven march846 | to camp, frame M
            kw.update(t0=0.0, t1=ST.DUR["g3"]); lim.update(speed=400)
            q["comment"] = ("seg_g3.CAM_M, the whole segment as rendered: flight 0-17.7 on its explicit speed profile (369 m/s, the "
                            "bible's speed exception; limit 400 here), camps, march846 re-driven (<= 289 m/s), to camp (<= 294 m/s). "
                            "Per-run limits: python aot/seg_g3.py")
        else:
            kw.update(t0=G3.B["march"][0], t1=G3.B["march"][1]); lim.update(speed=300)
            q["comment"] = ("march846 inside g3, re-driven by seg_g3 on march846's route (arc-length channels + explicit speed profile, "
                            "low pass raised to 140 m): march846.py's own spline gives 458 m/s, 57 deg/s, 81 m, pitch 11.")
        return G3.CAM_M, kw, q
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
        kw.update(t0=17.7, t1=CAM_IN["t"])
        q["comment"] = "H (17.7, at rest) to CAM_IN with v_out = (16.7,-61.1,5.6) and the look-point rate of march846 CAM_KEYS[0..1]. FA4->H (12.9-17.7) is inside the flight profile."
        return p, kw, q
    if name == "g3_to_camp":
        import seg_g3 as G3                                  # g3 agent 10/27: the rendered path (level CAM_OUT, march look-at rate in)
        p = G3.TOCAMP
        kw.update(t0=CAM_OUT["t"], t1=ST.DUR["g3"]); lim.update(speed=300)
        q["comment"] = ("FT0..FT7 as rendered by seg_g3: v_in = CAM_OUT (0,95,0) (level; the old climb (0,95,22) overshot to 681 m), "
                        "look_v_in = the re-driven march camera's look-at rate, v_out = g3_g4 seam, look-at at rest at FT7 (g4). "
                        "FT3-FT5 now 185/165/150 m (height floor 90 holds); speed limit 300 (flight exception, bible 298).")
        return p, kw, q
    if name == "A2":
        p = CamPath(run_A2_keys(), v_in=(0, 0, 0))
        kw.update(t0=ST.START["g2"], t1=ST.START["g3"] + CAM_IN["t"])
        q["comment"] = "g2 + g3 flight + camps up to CAM_IN as ONE pure-PCHIP channel (bible A2 run), guide key 31.8; the flight part is the 412 m/s case (g3 drives it with the explicit profile)."
        lim.update(speed=None)
        return p, kw, q
    if name in ("B", "B_vin"):
        keys = run_B_keys(guide=(name == "B"))
        if name == "B":
            p = CamPath(keys)
        else:
            p = CamPath(keys, v_in=CAM_OUT["vel"], look_v_in=CAM_OUT["look_vel"])
        kw.update(t0=ST.START["g3"] + CAM_OUT["t"], t1=ST.TOTAL)
        q["comment"] = ("FT0 -> g8 E2 as ONE channel, " + ("lead-in guide key at FT0-1 s (look-at = FT0 look), bible A3." if name == "B" else "with v_in = march846 CAM_OUT velocity instead of the guide key.") +
                        " Heights: FT3-FT5 low by design (70-95 m); the bible quotes the peaks per segment (g4 141/32 ... g8 67/30).")
        lim.update(hmin=65, speed=300)
        return p, kw, q
    raise KeyError(name)

if __name__ == "__main__":
    for n in ST.ORDER:
        print(n, ST.DUR[n], len(KEYS[n].get("keys", [])) if "keys" in KEYS[n] else "groups")
