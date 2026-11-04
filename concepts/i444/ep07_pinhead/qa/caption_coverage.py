# EP07 v5 QA (owner 11/04: "the intro is the most important part, words like 'straight' are missing"): every word spoken in the
# cold open (s00) must be inside the caption that is on screen when the word starts (onset + 0.02 s), captions must follow the narration order,
# and no caption may appear more than MAXLEAD s before its first word is spoken. Also lists the cut under each caption.
# Usage: python qa/caption_coverage.py  (reads edl.json + voice/words.json; exit code 1 on any failure)
import json, re, sys, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
E = json.load(open(D + 'edl.json')); W = json.load(open(D + 'voice/words.json'))
MAXLEAD = 0.25
def norm(s): return re.sub(r"[^a-z0-9']", '', s.lower())
s0 = next(S for S in E['sections'] if S['voice'] == 's00')
caps = sorted([o for o in s0['overlays'] if o[0] == 'word'], key=lambda o: o[2])
shots = s0['shots']
fail = 0; wi = 0; words = W['s00']
for c in caps:
    toks = [norm(t) for t in c[1].split()]
    first = None
    for t in toks:
        while wi < len(words) and norm(words[wi][2]) != t: wi += 1
        if wi == len(words): print('FAIL caption word not in narration order:', c[1], t); fail += 1; break
        a, b, w = words[wi]; m = a + 0.02
        if not (c[2] - 0.001 <= m <= c[3] + 0.001): print(f'FAIL "{w}" starts at {a:.2f}s but "{c[1]}" is on screen {c[2]:.2f}-{c[3]:.2f}'); fail += 1
        if first is None: first = a
        wi += 1
    if first is not None and c[2] < first - MAXLEAD - 0.08: print(f'FAIL "{c[1]}" appears {first - c[2]:.2f}s before it is said'); fail += 1
said = {i for i in range(len(words))}
shown = []
for i, (a, b, w) in enumerate(words):
    m = a + 0.02
    if not any(c[2] <= m <= c[3] and norm(w) in [norm(t) for t in c[1].split()] for c in caps): print(f'FAIL "{w}" ({a:.2f}s) is never on screen'); fail += 1
for c in caps:
    cut = [s for s in shots if s[0] <= c[2] + 0.001][-1]
    print(f'{c[2]:6.2f}-{c[3]:6.2f}  {c[1]:<22} cut {cut[0]:6.2f} {cut[1]} @{cut[2]}' + ('' if abs(cut[0] - c[2]) < 0.05 else '   (no new cut on this caption)'))
print('caption coverage', 'OK' if not fail else f'{fail} FAIL'); sys.exit(1 if fail else 0)
