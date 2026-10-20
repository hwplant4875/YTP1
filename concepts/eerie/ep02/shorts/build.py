# Build a Short's output timeline from the full EP02 timeline.
# python3 build.py spec.json full_tl.json out_short.json
import json, sys, re
spec = json.load(open(sys.argv[1])); tl = json.load(open(sys.argv[2]))
pieces, out, acc = spec['pieces'], [], 0.0
offs = []
for a, b in pieces: offs.append((a, b, acc - a)); acc += b - a
T = acc + (2.4 if spec.get('outro') else 0)   # the outro question holds over the last frame
def mp(t):
    for a, b, o in offs:
        if a - 1e-6 <= t < b: return t + o
    return None
segs, words = [], []
for s in tl['segments']:
    st = mp(s['start'])
    if st is None or mp(min(s['end'], s.get('start') + s.get('cut', 99)) - 0.01) is None: continue
    o = st - s['start']; n = dict(s); n['start'] = st; n['end'] = s['end'] + o
    n['words'] = [{'w': w['w'], 's': w['s'] + o, 'e': w['e'] + o} for w in s['words']]
    segs.append(n)
evs = [dict(e, t=mp(e['t'])) for e in tl['events'] if mp(e['t']) is not None and e['type'] not in spec.get('mute', [])]
cuts0 = sorted({round(mp(c), 3) for c in tl.get('cuts', []) if mp(c) is not None and mp(c) > 0.5} | {round(o + a, 3) for a, b, o in offs[1:]})
cuts = []
for c in cuts0:
    if not cuts or c - cuts[-1] > 0.6: cuts.append(c)
# caption chunks: up to 3 words, break after punctuation
caps = []
for s in segs:
    phrase = []
    for w in s['words']:
        phrase.append(w)
        if re.search(r'[.,!?…]$', w['w']) or w is s['words'][-1]:
            n = len(phrase); k = (n + 2) // 3          # chunks of at most 3, balanced (4 -> 2+2, 5 -> 3+2)
            sz = [n // k + (1 if i < n % k else 0) for i in range(k)]; p = 0
            for z in sz: caps.append(phrase[p:p + z]); p += z
            phrase = []
caps = [{'s': c[0]['s'], 'e': c[-1]['e'], 'w': [[w['w'], w['s']] for w in c]} for c in caps]
json.dump({'total': T, 'segments': segs, 'events': evs, 'cuts': cuts, 'pieces': offs, 'caps': caps,
           'cams': spec['cams'], 'title': spec['title'], 'outro': spec.get('outro')}, open(sys.argv[3], 'w'))
print('short', round(T, 2), 'segs', [s['id'] for s in segs], 'cuts', cuts)
