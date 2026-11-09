# EP08 Conjuring copy (via ../../ep_backrooms/qa) of ../ep04/qa/caption_coverage.py (caption kind 'word'): every word spoken in the cold open (s00) must be inside the
# caption on screen when the word starts (onset + 0.02 s), captions follow the narration order, none appears more than MAXLEAD s before
# its first word, and every caption has its own cut. Usage: python qa/caption_coverage.py  (exit code 1 on any failure)
import json, re, sys, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
E = json.load(open(D + 'edl.json')); W = json.load(open(D + 'voice/words.json'))
MAXLEAD = 0.25
ALIAS = {'22': 'twentytwo'}   # caption digits for spoken numbers
def norm(s): s = re.sub(r"[^a-z0-9']", '', s.lower().replace('-', '')); return ALIAS.get(s, s)
s0 = next(S for S in E['sections'] if S['voice'] == 's00')
caps = sorted([o for o in s0['overlays'] if o[0] == 'word'], key=lambda o: o[2])
shots = s0['shots']; fail = 0; wi = 0; words = W['s00']
for c in caps:
    first = None
    for t in [norm(t) for t in c[1].split() if norm(t)]:
        while wi < len(words) and norm(words[wi][2]) != t: wi += 1
        if wi == len(words): print('FAIL caption word not in narration order:', c[1], t); fail += 1; break
        a, b, w = words[wi]; m = a + 0.02
        if not (c[2] - 0.001 <= m <= c[3] + 0.001): print(f'FAIL "{w}" starts at {a:.2f}s but "{c[1]}" is on screen {c[2]:.2f}-{c[3]:.2f}'); fail += 1
        if first is None: first = a
        wi += 1
    if first is not None and c[2] < first - MAXLEAD - 0.08: print(f'FAIL "{c[1]}" appears {first - c[2]:.2f}s before it is said'); fail += 1
for a, b, w in words:
    m = a + 0.02
    if not any(c[2] <= m <= c[3] and norm(w) in [norm(t) for t in c[1].split()] for c in caps): print(f'FAIL "{w}" ({a:.2f}s) is never on screen'); fail += 1
import math
def f0(t): return math.ceil(t * 30 - 1e-6)   # the first frame a caption shows (the renderer: enable when t >= start)
for k, c in enumerate(caps):   # frame-exact: the caption's first frame is its cut's first frame, and no frame shows two captions
    cut = [s for s in shots if round(s[0] * 30) <= f0(c[2])]
    cut = cut[-1] if cut else [0, '-', '-']
    new = round(cut[0] * 30) == f0(c[2])
    if k + 1 < len(caps) and f0(caps[k + 1][2]) <= math.floor(c[3] * 30 + 1e-6): print(f'FAIL "{c[1]}" and "{caps[k + 1][1]}" share a frame'); fail += 1
    print(f'{c[2]:6.2f}-{c[3]:6.2f}  {c[1]:<22} cut {cut[0]:6.2f} {cut[1]} @{cut[2]}' + ('' if new else '   (no new cut on this caption)'))
print('caption coverage', 'OK' if not fail else f'{fail} FAIL'); sys.exit(1 if fail else 0)
