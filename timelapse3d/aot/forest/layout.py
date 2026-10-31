"""PART 2 layout constants (frame F, pure python; fset.py builds them, seg_f*.py read them)."""
import math

# ---------------------------------------------------------------- layout (frame F)
FOREST_X = (-1500.0, 700.0)
FOREST_Y = (0.0, 3000.0)
ROAD_F = [(270.0, -9000.0), (520.0, -8700.0), (640.0, -8250.0), (560.0, -7200.0), (380.0, -5600.0), (300.0, -4000.0),
          (180.0, -2400.0), (60.0, -900.0), (0.0, 0.0), (-25.0, 300.0), (10.0, 600.0), (0.0, 900.0), (0.0, 1050.0),
          (30.0, 1300.0), (-40.0, 1800.0), (-120.0, 2400.0), (-160.0, 3000.0)]
TRAP_F = (0.0, 900.0); TRAP_R = 22.0
EXIT_F = (0.0, 1050.0)
SWAMP_F = (300.0, 1600.0); SWAMP_R = 16.0
KICK_F = (380.0, 1700.0)
RESCUE_F = (500.0, 2000.0)
OLDTOWN_F = (650.0, -8300.0)
VILLAGE_F = (650.0, -4880.0)          # where f1 has the Female cross it (dome-relative path, t 34-40)
CLEAR = [(TRAP_F, TRAP_R + 4), (SWAMP_F, SWAMP_R + 3), ((0.0, -20.0), 26.0)]
# v14 frozen tableaux (seg_f3): open ground round the face-off and the high kick so trunks do not hide the titans
CLEAR += [((318.0, 1575.0), 34.0), ((KICK_F[0] - 14.0, KICK_F[1] - 10.0), 26.0)]

def road_dist_F(x, y, pts=None):
    pts = pts or ROAD_F
    best = 1e9
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
        u = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2)) if L2 > 0 else 0.0
        best = min(best, math.hypot(x - ax - u * dx, y - ay - u * dy))
    return best

