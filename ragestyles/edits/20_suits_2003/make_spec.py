"""Bodybuilders in a suit pt.2: 2003 Mr. Olympia press conference, same format as the 100k-view 1999 short."""
import json
base = json.load(open('../01_suits/spec.json'))
spec = {k: v for k, v in base.items() if k != 'shots'}
spec['src'] = {'pc': '/home/user/rs_work/src/suit2/wf8rjH3M1vM.mp4'}
spec['srcFilter'] = {'pc': 'crop=516:358:16:2,hqdn3d=1.5:1.5:3:3'}
spec['titles'] = [{'from': 0, 'text': 'Bodybuilders in a suit pt.2 🔥'}]
P = [('1st', 'Lee Priest', (113.0, 115.8, 0.5), (101.2, 103.8, 0.5)),
     ('2nd', 'Dennis James', (1152.5, 1155.5, 0.5), (1175.0, 1177.6, 0.5)),
     ('3rd', 'Jay Cutler', (1300.6, 1303.6, 0.55), (1330.0, 1332.6, 0.5)),
     ('4th', 'Melvin Anthony', (1481.0, 1483.8, 0.5), (1495.0, 1497.6, 0.5)),
     ('5th', 'Ronnie Coleman', (468.0, 471.2, 0.5), (1417.0, 1420.2, 0.5))]
shots = []
for n, name, a, b in P:
    d = a[1] - a[0]
    shots.append({"src": "pc", "in": a[0], "out": a[1], "cx": a[2], "cy": 0.45, "zoom": 1.12, "kb": 0.06,
                  "hits": [{"t": 0.7, "zoom": 1.1, "amount": 0.4, "boom": -4}], "tr": "cut", "zout": 1.22,
                  "caps": [{"parts": [[n, "#FFFFFF"]], "in": 0, "out": 0.7},
                           {"parts": [[name, "#FFD60A"]], "in": 0.7, "out": d + (b[1] - b[0])}]})
    shots.append({"src": "pc", "in": b[0], "out": b[1], "cx": b[2], "cy": 0.45, "zoom": 1.18, "kb": -0.08, "hits": [], "tr": "cut", "zout": 1.22, "zin": 1.22})
spec['shots'] = shots
json.dump(spec, open('spec.json', 'w'), indent=1, ensure_ascii=False)
print(round(sum(s['out'] - s['in'] for s in shots), 1))
