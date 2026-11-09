"""EP08 Conjuring phase A: probe + download clip_sources_v1.txt (and the backup ids named in its notes) into the clips folder.
Keeps 720p+ SDR, not age-gated; HDR uploads are fetched as their best SDR format. Writes qa/clips_report.txt and qa/age_gated.txt.
usage: python qa/fetch_clips.py "<clips folder>" [--report-only]"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); EP = os.path.dirname(HERE)
CLIPS = sys.argv[1]; REPORT_ONLY = '--report-only' in sys.argv; os.makedirs(CLIPS, exist_ok=True)
rows = []; seen = set()
for line in open(os.path.join(EP, 'clip_sources_v1.txt'), encoding='utf-8'):
    if line.startswith('#') or '|' not in line: continue
    p = [x.strip() for x in line.split('|')]
    if len(p) < 3: continue
    name, vid, ch, what = p[0], p[1], p[2], (p[3] if len(p) > 3 else '')
    if re.fullmatch(r'[\w-]{11}', vid) and vid not in seen: rows.append((name, vid, ch, what)); seen.add(vid)
    for k, extra in enumerate(re.findall(r'\b([\w-]{11})\b', what)):   # backup ids named in the notes -> <name>_b, _c ...
        if re.search(r'[A-Z0-9_-]', extra) and re.search(r'[a-z]', extra) and extra not in seen and not extra.isalpha():
            rows.append((f'{name}_{"bcdefg"[k]}', extra, '(backup from notes)', what)); seen.add(extra)
def info(vid):
    r = subprocess.run(['yt-dlp', '-J', '--no-playlist', 'https://www.youtube.com/watch?v=' + vid], capture_output=True, text=True)
    if r.returncode:
        err = (r.stderr.strip().splitlines() or ['?'])[-1]
        return None, ('AGE-GATED' if 'age' in err.lower() or 'sign in' in err.lower() else 'ERROR: ' + err[:120])
    return json.loads(r.stdout), None
def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=height,r_frame_rate,color_transfer:format=duration',
                        '-of', 'json', path], capture_output=True, text=True)
    j = json.loads(r.stdout or '{}'); s = (j.get('streams') or [{}])[0]; n, d = (s.get('r_frame_rate') or '0/1').split('/')
    return dict(h=s.get('height', 0), fps=float(n) / float(d or 1), dur=float(j.get('format', {}).get('duration', 0)), trc=s.get('color_transfer', ''))
status = {}
def one(row):
    name, vid, ch, what = row; path = os.path.join(CLIPS, name + '.mp4')
    if os.path.exists(path): status[name] = 'have'; return
    j, err = info(vid)
    if err: status[name] = err; print(name, err, flush=True); return
    fm = [f for f in j['formats'] if f.get('vcodec') not in (None, 'none')]
    sdr = [f for f in fm if (f.get('dynamic_range') or 'SDR') == 'SDR' and (f.get('height') or 0) <= 1080]
    best = max(sdr, key=lambda f: ((f.get('height') or 0), f.get('tbr') or 0), default=None)
    if not best or (best.get('height') or 0) < 720: status[name] = f'UNDER 720p ({best.get("height") if best else 0})'; print(name, status[name], flush=True); return
    r = subprocess.run(['yt-dlp', '--no-playlist', '--no-progress', '-q', '-f', best['format_id'] + '+ba/b', '--merge-output-format', 'mp4',
                        '-o', os.path.join(CLIPS, name + '.%(ext)s'), 'https://www.youtube.com/watch?v=' + vid], capture_output=True, text=True)
    status[name] = 'ok' if os.path.exists(path) else 'DOWNLOAD FAILED: ' + (r.stderr.strip().splitlines() or ['?'])[-1][:120]
    print(name, status[name], flush=True)
if not REPORT_ONLY:
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, rows))
lines = ['# EP08 Conjuring clips report: name | id | height | fps | duration s | SDR/HDR | status | channel | beat']; gated = []
for name, vid, ch, what in rows:
    path = os.path.join(CLIPS, name + '.mp4'); st = status.get(name, '')
    if os.path.exists(path):
        pr = probe(path); hdr = pr['trc'] in ('smpte2084', 'arib-std-b67')
        lines.append(f'{name} | {vid} | {pr["h"]} | {pr["fps"]:.2f} | {pr["dur"]:.1f} | {"HDR" if hdr else "SDR"} | {"OK" if pr["h"] >= 720 and not hdr else "CHECK"} | {ch} | {what[:80]}')
    else:
        lines.append(f'{name} | {vid} | - | - | - | - | {st or "MISSING"} | {ch} | {what[:80]}')
        if st == 'AGE-GATED': gated.append(f'yt-dlp --cookies-from-browser chrome -S res:1080 -f "bv*+ba/b" --merge-output-format mp4 -o "{os.path.join(CLIPS, name)}.%(ext)s" https://www.youtube.com/watch?v={vid}')
open(os.path.join(HERE, 'clips_report.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
open(os.path.join(HERE, 'age_gated.txt'), 'w', encoding='utf-8').write('# age-gated clips: the owner can run these in a terminal with Chrome logged in\n' + '\n'.join(gated) + '\n')
print('report', len(rows), 'clips,', len(gated), 'age-gated')
