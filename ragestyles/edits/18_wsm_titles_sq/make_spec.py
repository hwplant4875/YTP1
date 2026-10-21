"""1:1 clean remake of 17: each champion's lifts first, then his winning moment."""
import json
D = '/home/user/rs_work/src/wsm/'
A = [
 ('FI3z2MSrBFQ.mkv', '#5 BRIAN SHAW  4 TITLES', [(141.5, 142.4, .5), (146.0, 147.4, .5), (157.4, 159.3, .5), (183.4, 188.0, .5)]),
 ('Ova-z04LRn8.mkv', '#4 ZYDRUNAS SAVICKAS  4 TITLES', [(218.4, 222.8, .5), (201.2, 206.0, .5)]),
 ('UJqeN6Kv5V0.mkv', '#3 MAGNUS VER MAGNUSSON  4 TITLES', [(193.0, 196.0, .5), (206.0, 208.5, .5), (217.0, 219.8, .5)]),
 ('I1Hx7GZByxk.webm', '#2 JON PALL SIGMARSSON  4 TITLES', [(34.8, 36.8, .5), (21.8, 25.4, .5), (37.0, 40.8, .5)]),
 ('eWbiMIsgJqk.mkv', '#1 MARIUSZ PUDZIANOWSKI  5 TITLES', [(176.6, 179.8, .5), (182.6, 184.1, .5), (197.0, 201.0, .5), (206.5, 208.4, .5), (297.0, 300.5, .5)]),
]
segs = [{"src": D + f, "in": a, "out": b, "cx": c, "label": lab} for f, lab, cs in A for a, b, c in cs]
json.dump({"title": "MOST WORLD'S STRONGEST MAN TITLES", "segs": segs}, open('spec.json', 'w'), indent=1)
print(round(sum(s['out'] - s['in'] for s in segs), 1))
