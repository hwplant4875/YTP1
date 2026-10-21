"""Classic ranked list: heaviest Atlas Stones ever lifted (Rogue / Stoltman Brothers originals)."""
import json
D = '/home/user/rs_work/src/atlas/'
W_, Y_ = '#ffffff', '#ffd400'
# (file, in, out, zoom [cx, cy, z0, z1], list label or None (same entry continues), caps [(t0, t1, parts, size)], hits)
SEGS = [
 ('69m9QvTogMg.mkv', 44.5, 56.5, [0.5, 0.5, 1.25, 1.35], 'SHAW 252', [(0, 4.0, [("BRIAN SHAW, 2016", W_)]), (4.0, 8.5, [("STONE OVER THE BAR", W_)]), (8.5, 12.0, [("252 KG", Y_)], 130)], [8.5]),
 ('LFhZ5tPaCpc.webm', 90.5, 101.0, [0.5, 0.5, 1.0, 1.1], 'SHAW 254', [(0, 6.5, [("ONE YEAR LATER", W_)]), (6.5, 10.5, [("254 KG", Y_)], 130)], [6.5]),
 ('AtjiOAlsEQM.webm', 8.5, 17.5, [0.5, 0.5, 1.0, 1.08], 'STOLTMAN 273', [(0, 6.5, [("TOM STOLTMAN, 2020", W_)]), (6.5, 9.0, [("273 KG", Y_)], 130)], [6.5]),
 ('99ilJlZHb9Y.webm', 3.0, 15.0, [0.5, 0.5, 1.0, 1.06], 'STOLTMAN 286', [(0, 9.5, [("HEAVIER STILL", W_)]), (9.5, 12.0, [("286 KG", Y_)], 130)], [9.5]),
 ('nQwo4gehqNw.webm', 2.5, 11.5, [0.5, 0.55, 1.0, 1.08], 'STOLTMAN 300', [(0, 5.5, [("THEN THIS", W_)]), (5.5, 9.0, [("300 KG", Y_)], 140)], [5.5]),
 ('nQwo4gehqNw.webm', 15.5, 18.6, [0.5, 0.55, 1.08, 1.12], None, [(0, 1.4, [("TO THE LAP", W_)]), (1.4, 3.1, [("NOT OVER A BAR", Y_)])], []),
]
segs, caps, hits, items, t = [], [], [], [], 0.0
for f, a, b, z, lab, cs, hs in SEGS:
    segs.append({"src": D + f, "in": a, "out": b, "zoom": z})
    if lab:
        items.append({"n": f"{5 - len(items)}.", "label": lab, "at": round(t + 0.3, 2)})
    for c in cs:
        caps.append({"t": c[2], "in": round(t + c[0], 2), "out": round(t + c[1], 2), "y": 1430, **({"size": c[3]} if len(c) > 3 else {})})
    hits += [round(t + h, 2) for h in hs]
    t += b - a
items.reverse()
json.dump({"title": [[["Heaviest Atlas Stones", W_]], [["Ever Lifted", Y_]]], "titleSize": 76,
           "list": {"x": 44, "y": 640, "gap": 104, "size": 64, "items": items},
           "segs": segs, "caps": caps, "hits": hits}, open('16_atlas/spec.json', 'w'), indent=1)
print(round(t, 1))
