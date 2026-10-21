"""#5 giants in daily life: Samson Dauda (source bfIT_4vdZ7k, Jesse James West). Captions are per segment."""
import json
SRC = '/home/user/rs_work/src/test5/bfIT_4vdZ7k.mp4'
W_, Y_ = '#ffffff', '#ffd400'
R_ = '#ff3b3b'
# (in, out, crop x0, [(t0, t1, parts, size)], hits)
SEGS = [
 (542.0, 548.0, 300, [(0, 1.4, [("HIS ARM", W_)]), (1.4, 2.7, [("VS HIS HEAD", W_)]),
                      (2.7, 4.9, [("SAME SIZE", Y_)]), (4.9, 6.0, [("MAYBE BIGGER", Y_)])], [2.7]),
 (304.6, 314.6, 350, [(0, 1.6, [("AIRPLANE SEATS?", W_)]), (1.6, 3.2, [("\"DEFINE ", W_), ("AIRPLANE SEATS\"", Y_)]),
                      (3.2, 5.8, [("NORMAL ECONOMY?", W_)]), (5.8, 6.4, [("NO.", R_)], 120),
                      (6.4, 7.7, [("FAVORITE AIRLINE?", W_)]), (7.7, 8.8, [("BRITISH AIRWAYS", Y_)]),
                      (8.8, 10.0, [("BUSINESS CLASS", Y_)])], [7.7]),
 (285.0, 292.6, 460, [(0, 2.2, [("GYM MACHINES", W_)]), (2.2, 5.8, [("HE CAN DO THE SET", W_)]),
                      (5.8, 7.6, [("BUT HAS TO ", W_), ("SLIP OUT", Y_)])], []),
 (449.3, 455.9, 400, [(0, 1.8, [("CALORIES A DAY?", W_)]), (1.8, 3.0, [("7,500", Y_)], 140),
                      (3.0, 4.2, [("\"7,500?!\"", W_)]), (4.2, 6.6, [("TO MAINTAIN ", W_), ("300+ LB", Y_)])], [1.8]),
 (684.0, 691.4, 330, [(0, 1.4, [("HIS ARM", W_)]), (1.4, 3.6, [("RELAXED", Y_)]),
                      (3.6, 5.7, [("\"CARRY ME AROUND\"", W_)]), (5.7, 7.4, [("HE DOES. ", W_), ("ALL DAY", Y_)])], [1.4]),
 (818.0, 825.0, 500, [(0, 1.5, [("SIDE TRICEP POSE", W_)]), (1.5, 3.7, [("MR. OLYMPIA TRIES", W_)]),
                      (3.7, 5.2, [("CAN'T REACH", Y_)]), (5.2, 7.0, [("LOSES BY DEFAULT", R_)])], [3.7]),
]
segs, caps, hits, t = [], [], [], 0.0
for a, b, x0, cs, hs in SEGS:
    segs.append({"src": SRC, "in": a, "out": b, "fit": "blur", "pre": f"1100:880:{x0}:0", "bandH": 864, "bandY": 520})
    for c in cs:
        caps.append({"t": c[2], "in": round(t + c[0], 2), "out": round(t + c[1], 2), "y": 1500, **({"size": c[3]} if len(c) > 3 else {})})
    hits += [round(t + h, 2) for h in hs]
    t += b - a
json.dump({"title": [[["Life as a 350 lb", W_]], [["Mr. Olympia", Y_]]], "titleSize": 76,
           "segs": segs, "caps": caps, "hits": hits}, open('14_samson/spec.json', 'w'), indent=1)
print(round(t, 1))
