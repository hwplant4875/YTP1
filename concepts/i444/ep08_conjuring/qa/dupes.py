# EP08 QA: the same moment shown twice. Lists every pair of shots in edl.json whose source spans overlap by more than 0.15 s (same
# clip, or the two clips that hold the same footage, e.g. lr_end t = lr_exorcism t - 330). A shot that build_edl.py resumes after an
# insert continues its own span and is not a repeat. usage: python qa/dupes.py [edl.json]
import json, sys
E = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'edl.json'))
SAME = {'lr_end': ('lr_exorcism', 330.0)}   # clip -> (the clip it repeats, offset): lr_end t == lr_exorcism t - 330
spans = []
for S in E['sections']:
    sh = S['shots']
    for k, s in enumerate(sh):
        t, name, tin, sp = s[:4]
        d = (sh[k + 1][0] if k + 1 < len(sh) else S['len']) - t
        a, b = tin, tin + d * (sp or 1.0)
        if name in SAME: name, off = SAME[name]; a, b = a + off, b + off
        spans.append((name, a, b, S['voice'], round(t, 2), s[1]))
n = 0
for i in range(len(spans)):
    for j in range(i + 1, len(spans)):
        p, q = spans[i], spans[j]
        if p[0] != q[0] or p[0].startswith('still_'): continue   # a still (the poster wall) may come back as a callback
        ov = min(p[2], q[2]) - max(p[1], q[1])
        if ov <= 0.15: continue
        if p[3] == q[3] and abs(p[2] - q[1]) < 0.3: continue   # a running shot resumed after an insert
        print(f'REPEAT {p[0]} {max(p[1], q[1]):.1f}-{min(p[2], q[2]):.1f} ({ov:.1f} s): {p[3]} {p[4]} s ({p[5]}) and {q[3]} {q[4]} s ({q[5]})'); n += 1
print(n, 'repeated spans' if n else 'no repeated spans')
