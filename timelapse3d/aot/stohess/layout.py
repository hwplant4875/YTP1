"""PART 3 Stohess layout (pure python).  Frame S: origin = Wall Sina EAST district centre on the ring, W (12500, 24000);
+x outward (east), +y north.  STOHESS_SCENE_BIBLE.md B."""
import math

SO = (12500.0, 24000.0)
def S(x, y=0.0, z=0.0):
    return (x + SO[0], y + SO[1], z)
def toS(x, y, z=0.0):
    return (x - SO[0], y - SO[1], z)

BULGE_C = (300.0, 0.0); BULGE_R = 420.0; HALF_W = 420.0; GATE = (720.0, 0.0)
CANAL_X = 200.0
SQUARE = (-40.0, -60.0)
CHURCH = (80.0, -170.0)
MPHQ = (-200.0, -120.0)
STAIRS = (-150.0, 60.0)
EREN_UP = (-60.0, 40.0)
CLIMB_ANG = math.radians(-30.0)
def wall_inner(ang=CLIMB_ANG, inset=0.0):
    """point on the bulge wall's INNER face (r 415 - inset) and the inward normal."""
    r = BULGE_R - 5.0 - inset
    p = (BULGE_C[0] + r * math.cos(ang), BULGE_C[1] + r * math.sin(ang))
    return p, (-math.cos(ang), -math.sin(ang))
CLIMB, CLIMB_N = wall_inner()
CRYSTAL = (CLIMB[0] + 16 * CLIMB_N[0], CLIMB[1] + 16 * CLIMB_N[1])
FACE_Z = 40.0

def in_town(x, y):
    """inside the district bulge (and the 350 m of town inside the ring)."""
    if abs(y) > HALF_W - 12:
        return False
    if x < -350:
        return False
    if x > BULGE_C[0] and math.hypot(x - BULGE_C[0], y - BULGE_C[1]) > BULGE_R - 14:
        return False
    if -8 < x < 8:                                      # the old ring wall line is open inside the district (no wall built there)
        return True
    return True

def street(x, y):
    """streets / canal / squares to keep clear of houses."""
    if abs(y) < 11:                                      # main avenue
        return True
    if abs(x - CANAL_X) < 16:                            # canal + quays
        return True
    if abs((x + 350) % 80 - 40) < 4.5 or abs((y + 420) % 64 - 32) < 4.0:
        return True
    for (cx, cy), r in ((SQUARE, 34), (CHURCH, 30), (STAIRS, 14), (EREN_UP, 18)):
        if math.hypot(x - cx, y - cy) < r:
            return True
    return False

# titan paths (frame S) - houses within PATH_CLEAR m are not instanced (the segments place collapsing ones / rubble there)
FEM_PATH = [(-150.0, 60.0), (-90.0, 32.0), (-20.0, 18.0), (60.0, 10.0), (80.0, -125.0), (200.0, -140.0), (330.0, -150.0),
            (560.0, -190.0), (CLIMB[0] - 6.0, CLIMB[1] + 2.0)]
PATH_CLEAR = 16.0
def path_dist(x, y, P=FEM_PATH):
    best = 1e9
    for (ax, ay), (bx, by) in zip(P, P[1:]):
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
        u = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2)) if L2 else 0.0
        best = min(best, math.hypot(x - ax - u * dx, y - ay - u * dy))
    return best
