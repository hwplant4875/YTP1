# Check anchor phrases / list a section's words with onsets.
# usage: python qa/phrase.py s05            -> every word of s05 with its onset
#        python qa/phrase.py s05 "the last teenager" "onto a bed"   -> cut time (onset - 0.08) of each phrase, or NOT FOUND
import json, re, sys, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
W = json.load(open(D + 'voice/words.json'))
def norm(s): return re.sub(r"[^a-z0-9']", '', s.lower())
seg = sys.argv[1]
if len(sys.argv) == 2:
    print(' '.join(f'{w}@{a:.2f}' for a, b, w in W[seg]))
for p in sys.argv[2:]:
    ph, _, k = p.partition('#'); k = int(k or 1); ws = [norm(w[2]) for w in W[seg]]; pp = [norm(x) for x in ph.split()]; hit = None
    for i in range(len(ws) - len(pp) + 1):
        if ws[i:i + len(pp)] == pp:
            k -= 1
            if k == 0: hit = W[seg][i][0]; break
    print(f'{p!r}: ' + (f'cut at {max(0, hit - 0.08):.2f}' if hit is not None else 'NOT FOUND'))
