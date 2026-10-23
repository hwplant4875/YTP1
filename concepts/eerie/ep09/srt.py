# Build English subtitles from the timeline's word timings: one sentence per cue, long ones split near the middle.
# python3 srt.py timeline.json out.srt
import json, sys
tl = json.load(open(sys.argv[1]))
FIX = [('four four four', '444'), ('Three oh two', '3:02'), ('three oh two', '3:02'), ('Three oh four', '3:04'), ('two thirty', '2:30'), ('four zero four', '404'), ('One hundred percent', '100%')]
def ts(x):
    ms = int(round(x * 1000)); return f'{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}'
cues = []
for s in tl['segments']:
    cut = s.get('cut', 99) + s['start']
    words = [w for w in s['words'] if w['s'] < cut]
    sent = []
    for w in words:
        sent.append(w)
        if w['w'].rstrip('"\'').endswith(('.', '?', '!', ':')) or w is words[-1]:
            line = ' '.join(x['w'] for x in sent)
            if len(line) > 42:   # split a long sentence in two
                commas = [j + 1 for j, x in enumerate(sent[:-1]) if x['w'].endswith(',') and 3 <= j + 1 <= len(sent) - 3]   # prefer a comma near the middle
                n = min(commas, key=lambda j: abs(j - len(sent) / 2)) if commas else len(sent) // 2
                cues += [sent[:n], sent[n:]]
            else: cues.append(sent)
            sent = []
out = []
for i, c in enumerate(cues):
    txt = ' '.join(x['w'] for x in c)
    for a, b in FIX: txt = txt.replace(a, b)
    end = c[-1]['e'] + 0.25
    if i + 1 < len(cues): end = min(end, cues[i + 1][0]['s'] - 0.02)
    out.append(f'{i + 1}\n{ts(c[0]["s"])} --> {ts(end)}\n{txt}\n')
open(sys.argv[2], 'w').write('\n'.join(out)); print(len(cues), 'cues')
