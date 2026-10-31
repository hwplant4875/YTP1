# Halloween special (copy of ../ep03/make_srt_v2.py): English .srt: ElevenLabs character alignment (voice_v3/<seg>.json) placed at each section's start,
# with the same section lengths render_v2.py uses (voice + pad). Cues break at punctuation, max ~42 chars / 2.8 s.
# usage: python make_srt_v2.py [edl_v2.json] [voice_v3] [out.srt]
import json, os, sys, subprocess
edl = sys.argv[1] if len(sys.argv) > 1 else 'edl.json'; VOICE = sys.argv[2] if len(sys.argv) > 2 else 'voice'
OUT = sys.argv[3] if len(sys.argv) > 3 else 'upload/halloween_ranked_en_v4.srt'
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', '0', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
def ts(t): t = max(0, t); return '%02d:%02d:%02d,%03d' % (t // 3600, t % 3600 // 60, t % 60, round(t % 1 * 1000) % 1000)
cues, t0 = [], 0.0
for S in json.load(open(edl))['sections']:
    vp = os.path.join(VOICE, S['voice'] + '.mp3'); a = json.load(open(os.path.join(VOICE, S['voice'] + '.json')))
    ch, st, en = a['characters'], a['character_start_times_seconds'], a['character_end_times_seconds']
    words, cur = [], None                                   # (text, start, end)
    for c, s, e in zip(ch, st, en):
        if c.isspace():
            if cur: words.append(cur); cur = None
        elif cur: cur = (cur[0] + c, cur[1], e)
        else: cur = (c, s, e)
    if cur: words.append(cur)
    line = []
    for i, w in enumerate(words):
        line.append(w); txt = ' '.join(x[0] for x in line)
        nxt = words[i + 1][0] if i + 1 < len(words) else ''
        brk = w[0][-1] in '.,?!:;' and len(txt) > 14 or len(txt + ' ' + nxt) > 42 or line[-1][2] - line[0][1] > 2.8 or not nxt
        if brk: cues.append((t0 + line[0][1], t0 + line[-1][2], txt)); line = []
    t0 += dur(vp) + S.get('pad', 0.5)
with open(OUT, 'w', encoding='utf-8') as f:
    for k, (s, e, txt) in enumerate(cues):
        e = max(e, s + 0.7)
        if k + 1 < len(cues): e = min(e + 0.25, cues[k + 1][0] - 0.02)
        f.write(f'{k + 1}\n{ts(s)} --> {ts(e)}\n{txt}\n\n')
print(OUT, len(cues), 'cues, ends', ts(t0))
