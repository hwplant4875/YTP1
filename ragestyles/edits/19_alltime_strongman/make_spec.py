"""Most WSM titles edit (1:1): highlights first, then the title moment, fixed name reveal."""
import json
D = '/home/user/rs_work/src/wsm/'
A = [
 (5, 'MAGNUSSON  4x', 'UJqeN6Kv5V0.mkv', [(193.0, 196.0), (206.0, 208.5), (217.0, 219.8)]),
 (4, 'SIGMARSSON  4x', 'I1Hx7GZByxk.webm', [(34.8, 36.8), (21.8, 25.4), (37.0, 40.8)]),
 (3, 'SHAW  4x', 'FI3z2MSrBFQ.mkv', [(157.4, 159.3), (141.5, 142.4), (146.0, 147.4), (183.4, 188.0)]),
 (2, 'SAVICKAS  4x', 'Ova-z04LRn8.mkv', [(218.4, 222.8), (201.2, 206.0)]),
 (1, 'PUDZIANOWSKI  5x', 'eWbiMIsgJqk.mkv', [(176.6, 179.8), (182.6, 184.1), (197.0, 201.0), (206.5, 208.4), (297.0, 300.5)]),
]
spec = {"title": [["MOST WORLD'S STRONGEST", "#ffffff"], ["MAN TITLES", "#ffd400"]], "font": "/home/user/rs_work/gfonts/Kanit-BlackItalic.ttf",
        "list": {"x": 36, "y": 110, "gap": 86, "size": 54, "titleSize": 72},
        "reveal": {"dur": 1.4, "zoom": 1.22, "bright": 0.3},
        "athletes": [{"rank": r, "name": n, "shots": [{"src": D + f, "in": a, "out": b, "cx": 0.5} for a, b in sh]}
                     for r, n, f, sh in A]}
json.dump(spec, open('spec.json', 'w'), indent=1)
