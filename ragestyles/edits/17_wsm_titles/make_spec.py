"""Classic ranked list: most World's Strongest Man titles (official WSM channel footage)."""
import json
D = '/home/user/rs_work/src/wsm/'
W_, Y_ = '#ffffff', '#ffd400'
SEGS = [
 ('FI3z2MSrBFQ.mkv', 183.4, 190.0, [0.55, 0.5, 1.0, 1.1], 'BRIAN SHAW', [(0, 1.0, [("BRIAN SHAW", W_)]), (1.0, 6.6, [("4 TITLES", Y_)], 130)], [1.0]),
 ('Ova-z04LRn8.mkv', 201.0, 208.5, [0.5, 0.5, 1.0, 1.1], 'SAVICKAS', [(0, 2.0, [("ZYDRUNAS SAVICKAS", W_)]), (2.0, 7.5, [("4 TITLES", Y_)], 130)], [2.0]),
 ('UJqeN6Kv5V0.mkv', 212.5, 220.5, [0.5, 0.5, 1.0, 1.12], 'MAGNUSSON', [(0, 4.3, [("MAGNUS VER MAGNUSSON", W_)]), (4.3, 8.0, [("4 TITLES", Y_)], 130)], [4.3]),
 ('I1Hx7GZByxk.webm', 21.8, 25.4, [0.5, 0.45, 1.0, 1.1], 'SIGMARSSON', [(0, 1.8, [("\"I'M NOT AN ESKIMO!", W_)]), (1.8, 3.6, [("I'M A VIKING!\"", Y_)])], []),
 ('I1Hx7GZByxk.webm', 37.5, 41.8, [0.5, 0.45, 1.0, 1.1], None, [(0, 1.6, [("JON PALL SIGMARSSON", W_)]), (1.6, 4.3, [("4 TITLES", Y_)], 130)], [1.6]),
 ('eWbiMIsgJqk.mkv', 214.0, 228.5, [0.5, 0.48, 1.0, 1.15], 'PUDZIANOWSKI', [(0, 4.0, [("MARIUSZ PUDZIANOWSKI", W_)]), (4.0, 12.3, [("5 TITLES", Y_)], 140), (12.3, 14.5, [("THE ONLY ONE", W_)])], [4.0, 12.3]),
]
segs, caps, hits, items, t = [], [], [], [], 0.0
for f, a, b, z, lab, cs, hs in SEGS:
    segs.append({"src": D + f, "in": a, "out": b, "zoom": z})
    if lab:
        items.append({"n": f"{5 - len(items)}.", "label": lab, "at": round(t + 0.3, 2)})
    for c in cs:
        caps.append({"t": c[2], "in": round(t + c[0], 2), "out": round(t + c[1], 2), "y": 1320, **({"size": c[3]} if len(c) > 3 else {})})
    hits += [round(t + h, 2) for h in hs]
    t += b - a
items.reverse()
json.dump({"title": [[["Most World's Strongest", W_]], [["Man Titles", Y_]]], "titleSize": 76,
           "list": {"x": 44, "y": 640, "gap": 104, "size": 60, "items": items},
           "segs": segs, "caps": caps, "hits": hits}, open('17_wsm_titles/spec.json', 'w'), indent=1)
print(round(t, 1))
