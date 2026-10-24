"""Opening continuation (user, 2026-10-24): from the hill tree the camera flies through Shiganshina's inner gate, down the
main avenue, and the Colossal's head rises over the outer wall; then the camera climbs to a sky view, swings round
behind the Colossal (outside the wall), the kick blows in the outer gate (blocks arc into the town), the Colossal
vanishes into steam and the pure titans walk in through the breach.

List this module FIRST and LAST so it can set the other plug-ins' state flags before they import and then finish
the scene after they have built:
  SEQ_F=1500 AOT_PLUGINS=seq_colossal,flight,cast845,states845,colossal_asset,seq_colossal \
      bash render.sh seq out.png 640x360 16
Frames continue the flight module's numbering (flight frame 900 = Eren standing, end of the hill shot).
Mostly high / sky-angle views, no close-ups (user's direction).
"""
import math, os
from mathutils import Vector, noise

F = int(os.environ.get("SEQ_F", "900"))

# ---------------------------------------------------------------- timeline (30 fps)
T_RISE = (1170, 1290)      # Colossal head comes up over the outer wall
T_WIND = (1650, 1700)      # right leg drawn far back (anime S1E1)
T_KICK = (1700, 1728)      # swing forward through the gate; impact at the end
T_FADE = (1760, 1840)      # vanishes into steam
T_INFLOW = 1800            # pure titans start walking in

def _ramp(a, b, f=F):
    t = min(1.0, max(0.0, (f - a) / (b - a)))
    return t * t * (3 - 2 * t)

def flags(f=F):
    """Environment flags for the other plug-ins at sequence frame f."""
    e = {}
    e["COL_SHOW"] = "1" if T_RISE[0] <= f < T_FADE[1] else "0"
    e["COL_RISE"] = f"{_ramp(*T_RISE, f):.3f}"
    if f < T_WIND[1]:
        kick = -_ramp(*T_WIND, f)
    elif f < T_FADE[0]:
        kick = -1.0 + 2.0 * _ramp(*T_KICK, f)
    else:
        kick = 1.0
    e["COL_KICK"] = f"{kick:.3f}"
    e["COL_FADE"] = f"{_ramp(*T_FADE, f):.3f}"
    e["COL_DX"] = os.environ.get("COL_DX", "-7")      # right foot lines up with the gate
    if f >= T_KICK[1]:
        e["AOT_STATE"] = "kicked"
        e["AOT_ARC_T"] = f"{min(1.0, (f - T_KICK[1]) / 55.0):.3f}"
    else:
        e["AOT_STATE"] = "intact"
    e["AOT_EVENT"] = "armored" if f >= T_INFLOW else "intact"       # cast845: wanderers outside / inflow after the kick
    e.setdefault("SUN_AZ", os.environ.get("SUN_AZ", "-102"))
    return e

_FIRST = "SEQ_ENV_DONE" not in os.environ
if _FIRST:
    for k, v in flags().items():
        if k in ("SUN_AZ", "COL_DX") or k not in os.environ:
            os.environ[k] = v
    os.environ["SEQ_ENV_DONE"] = "1"

# ---------------------------------------------------------------- camera keys: (frame, loc, look_at, lens)
def keys():
    import flight
    l0, t0, n0 = flight.flight_at(900)
    return [
        (900, l0, t0, n0),
        (965, (-440, 300, 24), (-210, 120, 14), 32),
        (1050, (-150, 190, 24), (0, 0, 10), 30),
        (1112, (-4, 70, 12), (0, -40, 10), 28),
        (1140, (0, 14, 10), (0, -80, 11), 28),           # into the inner gate tunnel (14 m wide, 20 m high)
        (1162, (0, -16, 10.5), (0, -140, 16), 28),        # out on the gate square
        (1270, (0, -225, 30), (-6, -738, 62), 70),        # down the avenue; tight on the head rising over the wall
        (1380, (-6, -290, 36), (-6, -738, 64), 85),
        (1500, (230, -380, 270), (0, -700, 30), 28),      # climb to the sky view
        (1620, (190, -1130, 240), (0, -720, 40), 28),     # swing round behind the Colossal, outside the wall
        (1650, (110, -1000, 120), (-4, -730, 24), 45),    # closing in from behind for the kick
        (1700, (95, -960, 80), (-2, -725, 22), 55),       # legs + gate fill the frame: wind-up, strike
        (1760, (95, -960, 80), (0, -715, 22), 55),
        (1900, (70, -930, 230), (0, -470, 0), 28),        # rise and look north over the breach: titans walk in
        (2100, (40, -840, 200), (0, -360, 0), 28),
    ]

def _cr(p0, p1, p2, p3, t):
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)

def cam_at(f=F):
    ks = keys()
    f = min(max(f, ks[0][0]), ks[-1][0])
    i = max(j for j in range(len(ks)) if ks[j][0] <= f)
    if i == len(ks) - 1:
        _, l, t, n = ks[-1]
        return tuple(l), tuple(t), n
    a, b = ks[i], ks[i + 1]
    u = (f - a[0]) / (b[0] - a[0])
    u = u * u * (3 - 2 * u) if i in (0, len(ks) - 2) else u      # ease only the first and last move
    P = [Vector(ks[max(0, min(len(ks) - 1, j))][1]) for j in (i - 1, i, i + 1, i + 2)]
    T = [Vector(ks[max(0, min(len(ks) - 1, j))][2]) for j in (i - 1, i, i + 1, i + 2)]
    loc = _cr(*P, u); tgt = _cr(*T, u)
    lens = a[3] + (b[3] - a[3]) * u
    if T_KICK[1] <= f < T_KICK[1] + 30:                          # impact shake
        k = (1 - (f - T_KICK[1]) / 30) * 2.5
        loc += Vector((noise.noise(Vector((f * 0.7, 0, 0))), noise.noise(Vector((0, f * 0.7, 3))), noise.noise(Vector((5, 1, f * 0.7))))) * k
    return tuple(loc), tuple(tgt), lens

CAMS = {"seq": lambda: cam_at(F)}

# ---------------------------------------------------------------- finishing touches after the other plug-ins
_BUILDS = [0]
def build(M, year, ctx):
    _BUILDS[0] += 1
    if _BUILDS[0] < 2:               # first listing: flags only
        return
    import bpy
    # the inner gate stands open on the 845 morning so the camera can fly through it
    for n in ("InnerGate_Door",):
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = True
    # keep the gate corridor clear (a few scattered houses sit in the tunnel and its mouths)
    town = bpy.data.objects.get("Town")
    if town:
        me = town.data; dead = me.attributes["dead"].data
        n = 0
        path = [Vector(k[1]).to_2d() for k in keys()[1:6]]          # the low approach to and through the gate
        def near_path(p, r=20.0):
            for a, b in zip(path, path[1:]):
                ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
                if (p - (a + ab * t)).length < r:
                    return True
            return False
        for i, v in enumerate(me.vertices):
            if (abs(v.co.x) < 16 and -24 < v.co.y < 40) or near_path(v.co.to_2d()):
                dead[i].value = year - 1; n += 1
        me.update()
        print(f"[seq_colossal] cleared {n} houses from the gate corridor")
    # the Armored Titan belongs to a later chapter: hide it during this sequence
    for o in bpy.data.objects:
        if "armored" in o.name.lower() and o.type in ("ARMATURE", "MESH", "EMPTY"):
            o.hide_render = True
            for ch in o.children_recursive:
                ch.hide_render = True
    # walk cycles advance with the sequence (titans start walking in after the kick)
    bpy.context.scene.frame_set(max(1, F - T_INFLOW + 1) if F >= T_INFLOW else 1)
    print(f"[seq_colossal] frame {F} flags {flags()}")
