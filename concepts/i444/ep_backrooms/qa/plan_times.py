# Lists every shot row of shots.py with its cut time (take time) and the seconds of picture it needs: the take time to the next row,
# plus any choice pause in between (the running shot keeps playing under TURN BACK / KEEP GOING). Film/hum/thud inserts cut away and
# the shot resumes after them, so they add nothing.
# usage: python qa/plan_times.py [clip prefix or section]   -> sec | idx | t | need | clip | anchor | comment
import json, re, sys, os, subprocess
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
W = json.load(open(D + 'voice/words.json'))
def norm(s): return re.sub(r"[^a-z0-9']", '', s.lower().replace('-', ''))
def find(seg, phrase):
    phrase, _, k = phrase.partition('#'); k = int(k or 1)
    ws = [norm(w[2]) for w in W[seg]]; ph = [norm(p) for p in phrase.split()]
    for i in range(len(ws) - len(ph) + 1):
        if ws[i:i + len(ph)] == ph:
            k -= 1
            if k == 0: return i, i + len(ph) - 1
    raise KeyError((seg, phrase))
def at(seg, p): return W[seg][find(seg, p)[0]][0]
def split_after(seg, p):
    j = find(seg, p)[1]; ws = W[seg]
    return (ws[j][1] + ws[j + 1][0]) / 2 if j + 1 < len(ws) else ws[-1][1]
pre = sys.argv[1] if len(sys.argv) > 1 else ''
sec = None; rows = {}; choice = {}
src = open(D + 'shots.py', encoding='utf-8').read().split('\n')
for line in src:
    m = re.match(r"X\.append\(sec\('(s\d\d)'", line)
    if m: sec = m.group(1); rows[sec] = []; choice[sec] = []; continue
    for q in re.findall(r"ins\('([^']+)', 0\.9, 'choice'", line): choice[sec].append(split_after(sec, q))
    m = re.match(r"\s*\((0|'[^']*'|\"[^\"]*\"), '([^']+)', ([^,]+), ([^,)]+)(.*?)\),?\s*#\s*(.*)$", line)
    if m and sec: rows[sec].append((m.group(1).strip('\'"'), m.group(2), m.group(3).strip(), m.group(6).strip()))
for s, sh in rows.items():
    end = W[s][-1][1] + 0.1
    ts = [0.0 if a == '0' else max(0, at(s, a) - 0.08) for a, *_ in sh]
    for k, (a, c, tin, com) in enumerate(sh):
        t1 = ts[k + 1] if k + 1 < len(sh) else end
        need = t1 - ts[k] + 0.9 * sum(1 for x in choice[s] if ts[k] <= x < t1)
        if c.startswith(pre) or s == pre:
            print(f'{s} | {k:2d} | {ts[k]:6.2f} | {need:5.2f} | {c} | {a} | {"" if tin == "TODO" else "SET " + tin + " "}{com}')
