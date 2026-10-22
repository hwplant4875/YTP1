# English .srt from the narration alignment + EDL section offsets
# usage: python make_srt.py edl_full.json <voice_dir_with_json> out.srt
import json, subprocess, sys
edl, V, OUT = sys.argv[1:4]
E = json.load(open(edl)); cues = []; t0 = 0.0
for S in E['sections']:
    seg = S['voice']; a = json.load(open(f'{V}/{seg}.json'))
    words = []; w = ''
    for c, s, e in zip(a['characters'], a['character_start_times_seconds'], a['character_end_times_seconds']):
        if c.isspace():
            if w: words.append((w, ws, pe)); w = ''
            continue
        if not w: ws = s
        w += c; pe = e
    if w: words.append((w, ws, pe))
    line = []
    for wd in words:
        line.append(wd); txt = ' '.join(x[0] for x in line)
        if len(txt) >= 34 or wd[0][-1] in '.?!' or (wd[0][-1] == ',' and len(txt) > 20):
            cues.append((t0 + line[0][1], t0 + line[-1][2], txt)); line = []
    if line: cues.append((t0 + line[0][1], t0 + line[-1][2], ' '.join(x[0] for x in line)))
    d = float(subprocess.check_output(['ffprobe', '-v', '0', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'{V}/{seg}.mp3']))
    t0 += d + S.get('pad', 0.5)
def ts(t): return ('%02d:%02d:%06.3f' % (t // 3600, t % 3600 // 60, t % 60)).replace('.', ',')
out = []
for k, (s, e, t) in enumerate(cues):
    e2 = min(e + 0.3, cues[k + 1][0]) if k + 1 < len(cues) else e + 0.5
    out.append(f'{k + 1}\n{ts(s)} --> {ts(e2)}\n{t}\n')
open(OUT, 'w').write('\n'.join(out)); print(len(cues), 'cues, end', round(t0, 2))
