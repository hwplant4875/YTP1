# Backrooms special English .srt from the EDL (11/7 KST): narration words from the ElevenLabs character alignment (voice/<s>.json,
# take time) moved to the render's timeline through each section's pieces (the voice is cut around the inserts), plus the seven
# film lines as their own cues. Section starts are rounded to whole frames exactly like render_br.py. Years and spoken percentages
# are shown as digits. Cues break at punctuation, max ~42 chars / 2.8 s.
# usage: python make_srt.py [edl.json] [voice] [out.srt] [fps]
import json, os, sys
edl = sys.argv[1] if len(sys.argv) > 1 else 'edl.json'; VOICE = sys.argv[2] if len(sys.argv) > 2 else 'voice'
OUT = sys.argv[3] if len(sys.argv) > 3 else 'upload/backrooms_survival_en.srt'; FPS = int(sys.argv[4]) if len(sys.argv) > 4 else 30
def ts(t): t = max(0, t); return '%02d:%02d:%02d,%03d' % (t // 3600, t % 3600 // 60, t % 60, round(t % 1 * 1000) % 1000)
NUM = {'ninety': '90', 'seventy': '70', 'forty': '40', 'fifteen': '15', 'ten': '10', 'seven': '7', 'five': '5', 'two': '2'}
YEARS = {('nineteen', 'ninety'): '1990'}
cues, tg = [], 0.0
for S in json.load(open(edl))['sections']:
    t0 = round(tg * FPS) / FPS
    a = json.load(open(os.path.join(VOICE, S['voice'] + '.json')))
    words, cur = [], None
    for c, s, e in zip(a['characters'], a['character_start_times_seconds'], a['character_end_times_seconds']):
        if c.isspace():
            if cur: words.append(cur); cur = None
        elif cur: cur = (cur[0] + c, cur[1], e)
        else: cur = (c, s, e)
    if cur: words.append(cur)
    i = 0
    while i + 1 < len(words):   # years and "<number> percent" as digits, one token
        w0, w1 = words[i][0].lower(), words[i + 1][0].lower().rstrip('.,?!:;')
        if (w0, w1) in YEARS:
            words[i:i + 2] = [(YEARS[(w0, w1)] + words[i + 1][0][len(w1):], words[i][1], words[i + 1][2])]
        elif w0 in NUM and w1 == 'percent':
            words[i:i + 2] = [(NUM[w0] + '%' + words[i + 1][0][len('percent'):], words[i][1], words[i + 1][2])]
        i += 1
    def place(t):   # take time -> section time (the piece that holds t; the last word may end a few ms after the take's end)
        p0, p1, at = [p for p in S['pieces'] if p[0] <= t + 1e-6][-1]
        return at + (t - p0)
    words = [(w, place(s), place(e)) for w, s, e in words]
    line = []
    for i, w in enumerate(words):
        line.append(w); txt = ' '.join(x[0] for x in line)
        nxt = words[i + 1] if i + 1 < len(words) else None
        brk = (w[0][-1] in '.,?!:;' and len(txt) > 14 or nxt is None or len(txt + ' ' + nxt[0]) > 42 or line[-1][2] - line[0][1] > 2.8
               or nxt[1] - w[2] > 0.6)   # never across an insert
        if brk: cues.append((t0 + line[0][1], t0 + line[-1][2], txt)); line = []
    for o in S['overlays']:
        if o[0] == 'sub': cues.append((t0 + o[2], t0 + o[3], o[1]))
    tg += S['len']
cues.sort()
os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    for k, (s, e, txt) in enumerate(cues):
        e = min(e + 0.25, cues[k + 1][0] - 0.02) if k + 1 < len(cues) else e + 0.5
        f.write(f'{k + 1}\n{ts(s)} --> {ts(e)}\n{txt}\n\n')
print(OUT, len(cues), 'cues', ts(tg))
