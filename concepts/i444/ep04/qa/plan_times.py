# Lists every shot line of shots_v3.py with its start time in the voice and the screen time it needs (to the next cut).
# usage: python qa/plan_times.py [prefix]   -> prints sec | idx | t | need_s | clip | anchor | comment (only clips starting with prefix)
import json, re, sys, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
W = json.load(open(D + 'voice/words.json'))
def norm(s): return re.sub(r"[^a-z0-9']", '', s.lower())
def at(seg, phrase):
    phrase, _, k = phrase.partition('#'); k = int(k or 1)
    ws = [norm(w[2]) for w in W[seg]]; ph = [norm(p) for p in phrase.split()]
    for i in range(len(ws) - len(ph) + 1):
        if ws[i:i + len(ph)] == ph:
            k -= 1
            if k == 0: return W[seg][i][0]
    raise KeyError((seg, phrase))
pre = sys.argv[1] if len(sys.argv) > 1 else ''
sec = None; rows = {}
for line in open(D + 'shots_v3.py', encoding='utf-8'):
    m = re.match(r"X\.append\(sec\('(s\d\d)'", line)
    if m: sec = m.group(1); rows[sec] = []; continue
    m = re.match(r"\s*\((0|'[^']*'|\"[^\"]*\"), '([^']+)', ([^,]+), ([^,)]+)(.*?)\),?\s*#\s*(.*)$", line)
    if m and sec:
        a = m.group(1).strip('\'"'); rows[sec].append((a, m.group(2), m.group(6).strip(), ', L' in m.group(5)))
for s, sh in rows.items():
    end = W[s][-1][1] + (2.0 if s == 's11' else 0.15)
    ts = [0.0 if a == '0' else max(0, at(s, a) - 0.08) for a, *_ in sh]
    for k, (a, c, com, L) in enumerate(sh):
        d = (ts[k + 1] if k + 1 < len(sh) else end) - ts[k]
        if c.startswith(pre): print(f'{s} | {k:2d} | {ts[k]:6.2f} | {d:5.2f} | {c} | {a} | {"L " if L else ""}{com}')
