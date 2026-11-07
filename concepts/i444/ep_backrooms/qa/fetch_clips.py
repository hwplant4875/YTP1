"""Backrooms phase A (copied from ../ep04/qa/fetch_clips_v3.py): download clip_sources.txt into the clips folder, re-fetch HDR as SDR,
write qa/clips_report.txt.
usage: python qa/fetch_clips.py "<clips folder>" [--report-only]"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(HERE)
CLIPS = sys.argv[1]
REPORT_ONLY = '--report-only' in sys.argv
OLD = []

rows = []
for line in open(os.path.join(EP, 'clip_sources.txt'), encoding='utf-8'):
    if line.startswith('#') or '|' not in line:
        continue
    p = [x.strip() for x in line.split('|')]
    rows.append((p[0], p[1], p[2], p[3] if len(p) > 3 else ''))


def probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                        'stream=height,width,r_frame_rate,color_transfer:format=duration', '-of', 'json', path],
                       capture_output=True, text=True)
    j = json.loads(r.stdout or '{}')
    s = (j.get('streams') or [{}])[0]
    num, den = (s.get('r_frame_rate') or '0/1').split('/')
    fps = float(num) / float(den or 1)
    return dict(h=s.get('height', 0), w=s.get('width', 0), fps=fps, dur=float(j.get('format', {}).get('duration', 0)),
                trc=s.get('color_transfer', ''))


def is_hdr(pr):
    return pr['trc'] in ('smpte2084', 'arib-std-b67')


def dl(name, vid, fmt=None):
    out = os.path.join(CLIPS, name + '.%(ext)s')
    cmd = ['yt-dlp', '--no-playlist', '--no-progress', '-S', 'res:1080', '-f', fmt or 'bv*+ba/b',
           '--merge-output-format', 'mp4', '-o', out, 'https://www.youtube.com/watch?v=' + vid]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, (r.stderr or '')[-400:]


def sdr_format(vid):
    r = subprocess.run(['yt-dlp', '-J', '--no-playlist', 'https://www.youtube.com/watch?v=' + vid], capture_output=True, text=True)
    j = json.loads(r.stdout)
    best = None
    for f in j.get('formats', []):
        if f.get('vcodec') in (None, 'none') or (f.get('dynamic_range') or 'SDR') != 'SDR':
            continue
        h = f.get('height') or 0
        if h > 1080:
            continue
        key = (h, f.get('tbr') or 0)
        if best is None or key > best[0]:
            best = (key, f['format_id'])
    return best[1] if best else None


errs = {}
def one(row):
        name, vid, ch, what = row
        path = os.path.join(CLIPS, name + '.mp4')
        if os.path.exists(path):
            return
        rc, err = dl(name, vid)
        if rc != 0 or not os.path.exists(path):
            errs[name] = 'DOWNLOAD FAILED: ' + err.strip().splitlines()[-1] if err.strip() else 'DOWNLOAD FAILED'
            print(name, errs[name], flush=True)
            return
        pr = probe(path)
        if is_hdr(pr):
            fid = sdr_format(vid)
            if fid:
                os.replace(path, path + '.hdr_tmp')
                rc, err = dl(name, vid, fid + '+ba/b')
                if rc == 0 and os.path.exists(path):
                    os.remove(path + '.hdr_tmp')
                else:
                    os.replace(path + '.hdr_tmp', path)
        print('ok', name, probe(path), flush=True)

if not REPORT_ONLY:
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(one, rows))

lines = ['# Backrooms clips report: name | height | fps | duration s | SDR/HDR | status | channel']
names = [r[0] for r in rows] + [n for n in OLD if n not in [r[0] for r in rows]]
chan = {r[0]: r[2] for r in rows}
for name in names:
    path = os.path.join(CLIPS, name + '.mp4')
    if not os.path.exists(path):
        lines.append(f'{name} | - | - | - | - | {errs.get(name, "MISSING")} | {chan.get(name, "10/27 copy")}')
        continue
    pr = probe(path)
    st = []
    if pr['h'] < 720:
        st.append(f'UNDER 720p ({pr["h"]})')
    if is_hdr(pr):
        st.append('HDR (no SDR format)')
    c = chan.get(name, '')
    if 'ClipZone' in c or 'Rotten' in c:
        st.append('channel bug possible (' + c + '), check spans')
    lines.append(f'{name} | {pr["h"]} | {pr["fps"]:.2f} | {pr["dur"]:.1f} | {"HDR" if is_hdr(pr) else "SDR"} | {"; ".join(st) or "OK"} | {c}')
open(os.path.join(HERE, 'clips_report.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('report written', len(lines) - 1)
