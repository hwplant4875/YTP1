# EP04 v3: every anchor in shot_plan_v3.md must be an exact phrase of voice/words.json, in time order; prints shot lengths
import json, re, os, sys
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
W = json.load(open(D + 'voice/words.json'))
def norm(s): return re.sub(r"[^a-z0-9']", '', s.lower())
def at(seg, phrase):
    ws = [norm(w[2]) for w in W[seg]]; ph = [norm(p) for p in phrase.split()]
    for i in range(len(ws) - len(ph) + 1):
        if ws[i:i + len(ph)] == ph: return W[seg][i][0]
    raise KeyError((seg, phrase))
txt = open(D + 'shot_plan_v3.md', encoding='utf-8').read()
bad = 0
for m in re.finditer(r'^## (s\d\d)[^\n]*\n(.*?)(?=^## |\Z)', txt, re.S | re.M):
    seg, body = m.group(1), m.group(2)
    end = W[seg][-1][1]
    for blk in re.findall(r'```\n(.*?)```', body, re.S):
        rows = [l.split(' | ') for l in blk.strip().splitlines()]
        ts = []
        for r in rows:
            a = r[0].strip()
            try: t = 0.0 if a == '0' else at(seg, a)
            except KeyError: print('MISSING', seg, repr(a)); bad += 1; continue
            ts.append((t, a))
        for (t, a), nxt in zip(ts, ts[1:] + [(end, 'END')]):
            d = nxt[0] - t
            flag = ' <-- SHORT' if d < 0.5 else (' <-- LONG' if d > 3.6 else '')
            if d <= 0: flag = ' <-- ORDER'; bad += 1
            if flag: print(f'{seg} {t:6.2f} {d:5.2f}s {a}{flag}')
        print(seg, len(ts), 'shots, mean', round(end / max(1, len(ts)), 2), 's')
    for c in re.findall(r'^\| ([^|]+) \| ([^|]+) \| ([^|]+) \|$', body, re.M):
        if c[0].strip() in ('Caption', '---'): continue
        for a in c[1:]:
            a = a.strip()
            if a in ('0', '999', 'From', 'To') or set(a) <= set('-'): continue
            try: at(seg, a)
            except KeyError: print('MISSING caption anchor', seg, repr(a)); bad += 1
print('anchors', 'OK' if not bad else f'{bad} problems')
