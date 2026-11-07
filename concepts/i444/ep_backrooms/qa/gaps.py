# QA from the EDL: the longest stretch with no narration and no film line anywhere in the episode (owner rule: never over 1.5 s
# between voice lines), measured from the word timings moved through each section's pieces, across section joins.
# usage: python qa/gaps.py   (exit code 1 when a gap is over 1.5 s)
import json, os, sys
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
E = json.load(open(D + 'edl.json')); W = json.load(open(D + 'voice/words.json')); FPS = 30
spans, tg = [], 0.0
for S in E['sections']:
    t0 = round(tg * FPS) / FPS
    def place(t):   # the piece that holds t (the last word may end a few ms after the take's measured end)
        p0, p1, at = [p for p in S['pieces'] if p[0] <= t + 1e-6][-1]
        return at + (t - p0)
    spans += [(t0 + place(a), t0 + place(b), S['voice'] + ' ' + w) for a, b, w in W[S['voice']]]
    spans += [(t0 + x['s0'], t0 + x['s1'], S['voice'] + ' [' + x['kind'] + ']') for x in S['inserts'] if x['kind'] == 'film']
    tg += S['len']
spans.sort(); bad = 0; worst = []
for (a0, b0, w0), (a1, b1, w1) in zip(spans, spans[1:]):
    g = a1 - b0
    worst.append((g, b0, w0, w1))
    if g > 1.5: print(f'FAIL {g:.2f}s of silence at {b0:.2f}s between "{w0}" and "{w1}"'); bad += 1
for g, t, w0, w1 in sorted(worst, reverse=True)[:8]: print(f'{g:5.2f}s at {int(t // 60)}:{t % 60:05.2f}  {w0} -> {w1}')
print('gaps', 'OK' if not bad else f'{bad} FAIL'); sys.exit(1 if bad else 0)
