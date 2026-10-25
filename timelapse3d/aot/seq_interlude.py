"""INTERLUDE 846-850 (EP1 plan v2 shots 9 + 11, user storyline feedback item 1): timeline and beats.
Pure Python (no bpy) so HUD code can import it outside Blender.  The 846 "retake Wall Maria" march (shot 10) is
NOT here: it is its own segment (aot/march846.py); this segment follows it in the one-take flight.

Timeline in VIDEO SECONDS (30 fps final, 15 fps previews), 20.5 s total:
   0.0- 6.5  camps     START KEY: the camera rises from the Maria plains south of Trost, north over the Trost bulge and
                       Wall Rose to the refugee camps (846).  Time-lapse 846 summer -> famine winter -> spring 847: the
                       forest north of the camps is cleared into fields by the refugees, storehouses rise
   6.5- 8.5  flight    climb and fly north-west to the 104th Training Corps camp
   8.5-10.3  enlist    847: ~200 cadets stand in rows on the drill field
  10.3-12.8  rig       Eren hangs UPSIDE DOWN on the balance rig; Mikasa (red scarf) and Armin (blond) beside him (hold)
  12.8-17.6  seasons   847-850: summer, autumn, snow, spring cycle over the camp (11 seasons in 4.8 s); laps and drill
  17.6-20.5  graduation 850 night: the cadets in rows saluting, torches round the field.  END KEY: low oblique on the rows
"""

DURATION = 307 / 15             # the last preview frame (i = 307) is seam S8 exactly
T_CAMPS_END = 5.2               # camps segment ends here (master_timeline: camps src_out); C2 bridges on from this state
T_FLY, T_ENL, T_RIG, T_SEA, T_GRAD = 5.2, 8.5, 10.3, 12.8, 17.6
T_S7 = 7.0                      # training segment starts here, exactly at seam S7 (5.2-7.0 is never used in the master)

BEATS = [
    (0.0, T_FLY, "camps", "846: rise over Wall Rose; refugee camps; fields cleared, storehouses (summer 846 -> spring 847)"),
    (T_FLY, T_ENL, "flight", "fly to the 104th Training Corps camp"),
    (T_ENL, T_RIG, "enlist", "847: ~200 cadets enlist, rows on the drill field"),
    (T_RIG, T_SEA, "rig", "Eren upside down on the balance rig; Mikasa and Armin beside him (hold)"),
    (T_SEA, T_GRAD, "seasons", "847-850: three years of seasons over the camp"),
    (T_GRAD, DURATION, "graduation", "850: graduation night, torches"),
]

CADETS = 200          # "about 200 enlist" (plan v2 shot 11)

def _smooth(a, b, t):
    u = min(1.0, max(0.0, (t - a) / (b - a)))
    return u * u * (3 - 2 * u)

def season_at(t):
    """Continuous season phase: 0 summer, 1 autumn, 2 winter (snow), 3 spring (wraps at 4)."""
    if t < T_FLY:                                   # summer 846 -> autumn -> a brief famine winter -> spring 847
        return 1.2 * _smooth(0.3, 2.5, t) + 1.5 * _smooth(2.7, 3.7, t) + 0.3 * _smooth(3.7, 4.9, t)
    if t < T_SEA:                                   # spring 847 enlist -> summer on the rig
        return (3.0 + 1.0 * _smooth(T_ENL, T_RIG + 1.0, t)) % 4.0
    if t < T_GRAD:                                  # summer 847 -> spring 850 = 11 seasons
        return ((t - T_SEA) / (T_GRAD - T_SEA) * 11.0) % 4.0
    return 3.0

def year_at(t):
    if t < 3.2:
        return 846
    if t < T_SEA:
        return 847
    return min(850, 847 + int((t - T_SEA) / ((T_GRAD - T_SEA) / 3.0) + 0.25))

def night_at(t):
    """0 day, 1 full night (graduation)."""
    return _smooth(T_GRAD - 0.5, T_GRAD + 0.4, t)

def cadets_at(t):
    return CADETS if t >= T_ENL else None

def hud_at(t):
    y = year_at(t)
    if t < T_FLY:
        place, cap = "WALL ROSE", "Refugees clear new fields; food runs short"
    elif t < T_SEA:
        place, cap = "104TH TRAINING CORPS", "About 200 enlist"
    elif t < T_GRAD:
        place, cap = "104TH TRAINING CORPS", "Three years of training"
    else:
        place, cap = "104TH TRAINING CORPS", "Graduation"
    beat = [k for a, b, k, _ in BEATS if a <= t < b]
    c = cadets_at(t)
    return dict(place=place, year=y, age=y - 835, caption=cap, counter=("Cadets", c) if c else None,
                beat=beat[-1] if beat else "")

if __name__ == "__main__":
    for t in (0, 3, 6, 7, 9, 11, 13, 15, 17, 18, 20):
        print(t, season_at(t), hud_at(t))
