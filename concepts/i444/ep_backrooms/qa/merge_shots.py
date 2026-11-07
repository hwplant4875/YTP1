# Backrooms copy of ../../ep04/qa/merge_shots.py: fill shots.py from the per-group verified shot lines (1_work/beats/<group>.md, lines "sNN | (shot tuple),  # comment").
# Skeleton TODO rows are replaced by the verified row with the same section + anchor; NEW CUT rows are inserted in time order.
# usage: python qa/merge_shots.py <beats dir> [extra.txt ...]   -> rewrites shots.py, lists any TODO left
import ast, glob, json, os, re, sys
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
W = json.load(open(D + 'voice/words.json'))
def norm(s): return re.sub(r"[^a-z0-9']", '', s.lower().replace('-', ''))
def at(seg, phrase):
    phrase, _, k = phrase.partition('#'); k = int(k or 1)
    ws = [norm(w[2]) for w in W[seg]]; ph = [norm(p) for p in phrase.split()]
    for i in range(len(ws) - len(ph) + 1):
        if ws[i:i + len(ph)] == ph:
            k -= 1
            if k == 0: return W[seg][i][0]
    raise KeyError((seg, phrase))
rows = {}   # sec -> list of (anchor, text)
files = sorted(glob.glob(os.path.join(sys.argv[1], '*.md'))) + sys.argv[2:]
for f in files:
    for line in open(f, encoding='utf-8'):
        m = re.match(r"\s*`?(s\d\d)\s*\|\s*((?:\(|SKIP).*)$", line.rstrip().rstrip('`'))
        if not m: continue
        s, rest = m.groups()
        code, _, com = rest.partition('#')
        if code.strip().startswith('SKIP'):   # override file: "sNN | SKIP 'anchor'" drops that row
            a = ast.literal_eval(code.strip()[4:].strip()); rows[s] = [r for r in rows.get(s, []) if r[1] != a]; continue
        code = code.strip().rstrip(',')
        L = 'L'
        tup = ast.literal_eval(code.replace(', L)', ", 'L')").replace('T4', "'z=1.333'"))
        a = 0 if tup[0] in (0, '0') else tup[0]
        if tup[0] == '0': code = code.replace("('0',", '(0,', 1)
        rows[s] = [r for r in rows.get(s, []) if r[1] != a]   # a later file overrides the same section + anchor
        try:
            t = 0 if a == 0 else at(s, a)
        except KeyError:
            print('BAD ANCHOR', f, s, a); continue
        rows.setdefault(s, []).append((t, a, code, com.strip(), os.path.basename(f)))
src = open(D + 'shots.py', encoding='utf-8').read().split('\n')
out = []; sec = None; left = 0
for line in src:
    m = re.match(r"X\.append\(sec\('(s\d\d)', \[", line)
    if m:
        sec = m.group(1); out.append(line); pending = []; continue
    if sec and re.match(r"\s*\((0|'[^']*'|\"[^\"]*\"), '[^']+', ", line):
        a = re.match(r"\s*\((0|'[^']*'|\"[^\"]*\")", line).group(1); a = 0 if a == '0' else a[1:-1]
        pending.append((a, line)); continue
    if sec and line.startswith('  ]'):
        got = rows.get(sec, []); have = {r[1] for r in got}; merged = []
        for a, ln in pending:
            if a in have: continue
            if 'TODO' in ln: left += 1; print('TODO left', sec, a)
            merged.append((0 if a == 0 else at(sec, a), ln))
        for t, a, code, com, fn in got:
            merged.append((t, f'  {code},  # {com}'))
        merged.sort(key=lambda x: x[0])
        out += [ln for _, ln in merged]; out.append(line); sec = None; continue
    out.append(line)
open(D + 'shots.py', 'w', encoding='utf-8').write('\n'.join(out))
print('merged', sum(len(v) for v in rows.values()), 'rows;', left, 'TODO left')
