"""Shiganshina layout (anime S1E1 aerial reference): an elongated U-shaped outcrop south of Wall Maria.

Wall Maria runs along the x axis (y = 0). The district sticks out to the south (y < 0):
straight sides at x = +-WD from y = 0 to y = -LS, closed by a half circle of radius WD
centred at (0, -LS). Outer gate at the tip (0, -LS - WD); inner gate in Wall Maria at (0, 0).
A canal runs inside along the EAST wall (SCENE_BIBLE_v2 g1 / D5: canal east at x = +228 in scene.py, here +WD - 42),
passing both walls through arched water gates.  The layout is generated in a west-canal frame (_CW) and mirrored in x
on output, so every public function returns east-canal coordinates.
"""
import math, random
from mathutils import Vector, noise

WD = 380.0                    # half width of the district
LS = 700.0                    # length of the straight sides
TIP = LS + WD                 # distance from Wall Maria to the outer gate
_CW = -WD + 42.0              # canal centre line in the internal (west) generation frame
CANAL_X = -_CW                # public: canal centre line inside the EAST wall
CANAL_W = 28.0
PLAZA = (0.0, -540.0)         # central plaza with the monument

def outline(step=8.0):
    """District wall path from the west end at Wall Maria, round the tip, to the east end."""
    pts = []
    y = 0.0
    while y > -LS:
        pts.append((-WD, y)); y -= step
    n = int(math.pi * WD / step)
    for i in range(n + 1):
        a = math.pi + i / n * math.pi
        pts.append((math.cos(a) * WD, -LS + math.sin(a) * WD))
    y = -LS + step
    while y < 0:
        pts.append((WD, y)); y += step
    pts.append((WD, 0.0))
    return pts

def in_district(x, y, margin=0.0):
    if y > -margin:
        return False
    if y > -LS:
        return abs(x) < WD - margin
    return math.hypot(x, y + LS) < WD - margin

def canal_exit_y():
    return -LS - math.sqrt(WD ** 2 - CANAL_X ** 2)

def canal_path():
    """Inside the district (south to north) and on through Wall Maria toward Trost."""
    pts = [(_CW, canal_exit_y() - 260 + k * 10) for k in range(0, 27)]          # outside, beyond the outer wall
    y = canal_exit_y() + 10
    while y < 0:
        pts.append((_CW, y)); y += 10
    for k in range(1, 400):                                                        # north into Wall Maria land
        yy = k * 25.0
        pts.append((_CW + math.sin(yy / 900) * 160 + noise.noise(Vector((0, yy / 600, 3))) * 60, yy))
    return [(-x, y) for x, y in pts]

def street_network():
    """(polyline, half width) list: main avenue, canal-side road, spokes from the plaza, cross streets."""
    rnd = random.Random(4)
    S = []
    px, py = PLAZA
    S.append(([(noise.noise(Vector((0, y / 260, 7))) * 4, y) for y in range(-int(TIP) + 10, -8, 6)], 9.0))   # main avenue
    S.append(([(_CW + CANAL_W / 2 + 9, y) for y in range(int(canal_exit_y()) + 20, -12, 8)], 6.0))   # canal road
    for ang in (15, 38, 62, 118, 142, 165, 200, 225, 250, 290, 315, 340):
        a = math.radians(ang)
        pts = []
        for r in range(40, 1200, 6):
            x, y = px + math.cos(a) * r, py + math.sin(a) * r
            x += noise.noise(Vector((r / 160, ang, 1))) * 8
            if not in_district(x, y, 16) or x < _CW + CANAL_W / 2 + 18:
                break
            pts.append((x, y))
        if len(pts) > 3:
            S.append((pts, 4.5))
    for yy in (-150, -330, -760, -900):                                         # cross streets
        pts = [(x, yy + noise.noise(Vector((x / 140, yy, 2))) * 10) for x in range(int(_CW + CANAL_W / 2 + 18), int(WD) - 16, 6)
               if in_district(x, yy, 16)]
        if len(pts) > 3:
            S.append((pts, 4.0))
    # short lanes
    for _ in range(70):
        x0, y0 = rnd.uniform(-WD, WD), rnd.uniform(-TIP, 0)
        if not in_district(x0, y0, 30) or x0 < _CW + 40:
            continue
        a = rnd.uniform(0, math.pi)
        pts = [(x0 + math.cos(a) * t, y0 + math.sin(a) * t) for t in range(-60, 61, 6)]
        pts = [p for p in pts if in_district(p[0], p[1], 16) and p[0] > _CW + CANAL_W / 2 + 18]
        if len(pts) > 4:
            S.append((pts, 2.8))
    return [([(-x, y) for x, y in pts], hw) for pts, hw in S]
