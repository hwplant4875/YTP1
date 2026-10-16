"""#1 classic ranked list: heaviest strongman world records (Giants Live / Eddie Hall originals)."""
import json
D = '/home/user/rs_work/src/strong/'
W_, Y_ = '#ffffff', '#ffd400'
# (file, in, out, zoom [cx, cy, z0, z1], list label, caps [(t0, t1, parts, size)], hits)
SEGS = [
 ('nQk41ZMc5oM.mkv', 127.0, 135.6, [0.55, 0.5, 1.0, 1.12], 'HOOPER', [(0, 2.6, [("AXLE PRESS", W_)]), (2.6, 8.6, [("218 KG", Y_)], 130)], [2.6]),
 ('1o3dQuT4Tfw.webm', 313.0, 323.2, [0.5, 0.5, 1.0, 1.08], 'IRON BIBY', [(0, 5.5, [("LOG PRESS", W_)]), (5.5, 10.2, [("231 KG", Y_)], 130)], [6.6]),
 ('IGaN66dcZEs.webm', 34.5, 50.5, [0.47, 0.45, 1.05, 1.2], 'EDDIE HALL', [(0, 2.0, [("DEADLIFT, 2016", W_)]), (2.0, 7.5, [("FIRST EVER ", W_), ("500 KG", Y_)]), (7.5, 11.0, [("HELD IT", W_)]), (11.0, 16.0, [("THEN ", W_), ("COLLAPSED", '#ff3b3b')])], [5.8]),
 ('ZHI7COyl6WA.webm', 87.0, 94.6, [0.5, 0.45, 1.0, 1.12], 'THOR', [(0, 2.5, [("DEADLIFT, 2025", W_)]), (2.5, 7.6, [("510 KG", Y_)], 130)], [3.6]),
 ('4oHrTDCgVAs.webm', 187.5, 199.6, [0.5, 0.52, 1.15, 1.35], 'RAUL FLORES', [(0, 2.5, [("DEADLIFT, SEPT 2026", W_)]), (2.5, 7.5, [("511 KG", Y_)], 140), (7.5, 12.1, [("1 KG ", Y_), ("MORE THAN THOR", W_)])], [3.2]),
]
segs, caps, hits, items, t = [], [], [], [], 0.0
for k, (f, a, b, z, lab, cs, hs) in enumerate(SEGS):
    segs.append({"src": D + f, "in": a, "out": b, "zoom": z})
    items.append({"n": f"{5 - k}.", "label": lab, "at": round(t + 0.3, 2)})
    for c in cs:
        caps.append({"t": c[2], "in": round(t + c[0], 2), "out": round(t + c[1], 2), "y": 1430, **({"size": c[3]} if len(c) > 3 else {})})
    hits += [round(t + h, 2) for h in hs]
    t += b - a
items.reverse()  # 1. on top
json.dump({"title": [[["Heaviest Strongman", W_]], [["World Records", Y_]]], "titleSize": 76,
           "list": {"x": 44, "y": 640, "gap": 104, "size": 64, "items": items},
           "segs": segs, "caps": caps, "hits": hits}, open('15_strongman/spec.json', 'w'), indent=1)
print(round(t, 1))
