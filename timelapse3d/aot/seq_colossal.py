"""Opening continuation (user, 2026-10-24): from the hill tree the camera swooshes straight to the crowded plaza (no inner-gate pass),
and the Colossal's head rises over the outer wall; then the camera climbs to a sky view, swings round
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
# user's exact timing (10/24 09:06), video second v = (frame - 840) / 30: tree 0-2 s, swoosh to the plaza 2-5 s,
# head rises 5-8 s, kick 11 s, then steam and the inflow, briskly
T_RISE = (990, 1080)       # Colossal head comes up over the outer wall, hands on the wall top
T_WIND = (1092, 1142)      # right leg drawn far back (anime S1E1), real speed
T_KICK = (1142, 1170)      # swing forward through the gate; impact at the end (11 s)
T_FADE = (1200, 1260)      # vanishes into steam
T_INFLOW = 1215            # pure titans start walking in

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
        (935, (-300, 250, 90), (-60, 0, 40), 30),         # swoosh up off the hill, over the inner wall
        (965, (-40, -230, 60), (0, -620, 40), 30),
        (990, (0, -462, 6), (-6, -738, 58), 35),          # down among the plaza crowd: the head appears
        (1080, (-2, -520, 12), (-6, -738, 64), 75),       # zoom toward the head as it rises
        (1110, (200, -700, 200), (0, -730, 40), 30),      # swoop up over the outer wall
        (1135, (110, -1000, 120), (-4, -730, 24), 45),    # behind the Colossal for the kick
        (1170, (95, -960, 80), (-2, -725, 22), 55),       # legs + gate fill the frame: wind-up, strike
        (1200, (95, -960, 80), (0, -715, 22), 55),
        (1290, (70, -930, 230), (0, -470, 0), 28),        # rise and look north over the breach: titans walk in
        (1360, (40, -840, 200), (0, -360, 0), 28),
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
    # the plaza crowd looking south at the head (s1e1_plaza_crowd_colossal_head framing)
    try:
        import people_kit as PK
        PK.crowd(["civilian"], (0, -505, 14, 50), 160, "stand", yaw=math.pi, seed=7, jitter=0.6)
    except Exception:
        import traceback; traceback.print_exc()
    # the Armored Titan belongs to a later chapter: hide it during this sequence
    for o in bpy.data.objects:
        if "armored" in o.name.lower() and o.type in ("ARMATURE", "MESH", "EMPTY"):
            o.hide_render = True
            for ch in o.children_recursive:
                ch.hide_render = True
    # walk cycles advance with the sequence (titans start walking in after the kick)
    bpy.context.scene.frame_set(max(1, F - T_INFLOW + 1) if F >= T_INFLOW else 1)
    print(f"[seq_colossal] frame {F} flags {flags()}")
