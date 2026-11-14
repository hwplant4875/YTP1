# EP08 Conjuring: the delivered edit (edl.json, real Adam voice, commit 648d502) rebuilt as a DaVinci Resolve project, for the owner's
# monetization-appeal screen recording. Nothing is added that is not in conjuring_ranked_v1.mp4: every V1 shot is its real source clip at its
# real in-point, record time, length and speed; the overlays are the renderer's own drawings (render_cj.py functions) as stills.
#   python resolve_timeline.py prep     (Python with PIL/numpy, e.g. 3.12): plan.json, overlay PNGs, the V1 FCP7 XML (keeps shot speeds)
#   py -3.15 resolve_timeline.py build  (Resolve Studio open, External scripting = Local; fusionscript loads in 3.15, crashes 3.12 here)
#   py -3.15 resolve_timeline.py check  (length, counts, six timeline frames exported as stills next to the same render frames)
# Writes only under <EP08>\1_work\resolve. Never renders, never touches another Resolve project.
import json, os, sys, ast, subprocess, re
from fractions import Fraction as Fr
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.environ.get('EP08', r'E:\YTP2\Horror Ranked\EP08 Conjuring')
CLIPS = os.path.join(EP, '1_work', 'clips')
RES = os.path.join(EP, '1_work', 'resolve'); GFX = os.path.join(RES, 'gfx')
VOICE = os.path.join(HERE, 'voice')
MUSIC = os.path.join(EP, '1_work', 'music', 'conjuring_bed.mp3')
FINAL = os.path.join(EP, '2_renders', 'conjuring_ranked_v1.mp4')
EDL = os.path.join(HERE, 'edl.json')
PLAN = os.path.join(RES, 'plan.json'); XML = os.path.join(RES, 'ep08_v1_shots.xml'); CAL = os.path.join(RES, 'v1_in_calibration.json')
FPS = 30
PROJECT, TIMELINE = 'Horror Ranked EP08 Conjuring', 'EP08 Conjuring v1'

FILMS = {   # clip prefix -> film (bin name); cold-open clips per clip_sources_v1.txt
    'c1': 'The Conjuring (2013)', 'c2': 'The Conjuring 2 (2016)', 'a14': 'Annabelle (2014)', 'cr': 'Annabelle Creation (2017)',
    'n1': 'The Nun (2018)', 'ach': 'Annabelle Comes Home (2019)', 'dm': 'The Devil Made Me Do It (2021)', 'n2': 'The Nun II (2023)',
    'lr': 'The Conjuring Last Rites (2025)',
    'co_burn_4k': 'The Nun II (2023)', 'co_neck': 'The Nun II (2023)', 'co_neck_b': 'The Nun II (2023)', 'co_buried_b': 'The Nun (2018)',
    'co_valak0': 'The Nun (2018)', 'co_stab': 'The Devil Made Me Do It (2021)', 'co_mother': 'The Conjuring (2013)',
    'co_mother_b': 'The Conjuring (2013)', 'co_mother_c': 'The Conjuring (2013)', 'co_doll': 'Annabelle Comes Home (2019)',
    'spooky_nun': 'The Nun (2018)', 'universe': 'Conjuring Universe compilation (WB)', 'still_posterwall': 'Graphics'}
COLOURS = {'The Conjuring (2013)': 'Blue', 'The Conjuring 2 (2016)': 'Teal', 'Annabelle (2014)': 'Pink', 'Annabelle Creation (2017)': 'Violet',
           'The Nun (2018)': 'Orange', 'Annabelle Comes Home (2019)': 'Purple', 'The Devil Made Me Do It (2021)': 'Olive',
           'The Nun II (2023)': 'Yellow', 'The Conjuring Last Rites (2025)': 'Lime', 'Conjuring Universe compilation (WB)': 'Navy',
           'Graphics': 'Tan'}
CHAPTERS = ['Cold open: These demons will burn you alive', 'Rules: How the survival rate works', '#9 Annabelle Comes Home (95%)',
            '#8 Annabelle (80%)', '#7 The Conjuring (65%)', '#6 The Conjuring 2 (55%)', '#5 The Conjuring Last Rites (45%)',
            '#4 Annabelle Creation (40%)', '#3 The Devil Made Me Do It (30%)', '#2 The Nun II (12%)', '#1 The Nun (5%)',
            'Outro: Which demon would you least want at home?']
INV = {'c1': 'The Conjuring (2013)'}   # shot op 'f' (film tag of a compilation shot)

def film_of(name):
    if name in FILMS: return FILMS[name]
    return FILMS[name.split('_')[0]]
def src(name):
    for ext in ('_hd.mp4', '.mp4', '.webm', '.mkv'):
        p = os.path.join(CLIPS, name + ext)
        if os.path.exists(p): return p
    raise FileNotFoundError(name)
def probe(p):
    o = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate,time_base',
                                            '-of', 'json', p]))
    v = next((s for s in o['streams'] if s['codec_type'] == 'video'), None)
    r = {'dur': float(o['format']['duration']), 'audio': any(s['codec_type'] == 'audio' for s in o['streams'])}
    if v: r.update(w=v['width'], h=v['height'], fps=str(Fr(v['r_frame_rate'])), tb=v['time_base'])
    return r

# ------------------------------------------------------------------------------------------------------------------------------- plan
def make_plan():
    E = json.load(open(EDL)); Z = E.get('zoom', {}); BAR = E.get('bar', {})
    P = {'sections': [], 'v1': [], 'ovl': [], 'voice': [], 'film_audio': [], 'sfx': [], 'media': {}}
    tg = 0.0
    for si, S in enumerate(E['sections']):
        L = S['len']; F0 = round(tg * FPS); NF = round((tg + L) * FPS) - F0
        P['sections'].append({'id': S['voice'], 'F0': F0, 'NF': NF, 'name': CHAPTERS[si]})
        shots = S['shots']
        for k, (t, name, tin, sp, *rest) in enumerate(shots):
            op = rest[0] if rest else {}
            f0 = round(t * FPS); f1 = round(shots[k + 1][0] * FPS) if k + 1 < len(shots) else NF; n = f1 - f0
            if n <= 0: continue
            if op.get('ins'): sp = 1.0
            if name not in P['media']: P['media'][name] = dict(probe(src(name)), path=src(name))
            m = P['media'][name]
            z = float(op.get('z', Z.get(name, 1.04)))
            lim = (1920 - 1920 / z) / 2; limy = (1080 - 1080 / z) / 2
            dx = max(-lim, min(lim, float(op.get('dx', 0)))); dy = max(-limy, min(limy, float(op.get('dy', 0))))
            crop_b = 0.0
            if name in BAR:   # renderer: black box from the bar's row down, only while this framing still shows it
                y0 = min(max(0.0, 540 - 1080 / z / 2 + float(op.get('dy', 0))), 1080 - 1080 / z)
                if int((BAR[name] - y0) * z) < 1080:
                    s = max(1920 / m['w'], 1080 / m['h']); oy = (m['h'] * s - 1080) / 2
                    crop_b = m['h'] - (BAR[name] + oy) / s
            g = float(op.get('g', E.get('gamma', {}).get(name, 1.06)))
            P['v1'].append({'sec': S['voice'], 'k': k, 'name': name, 'rec': F0 + f0, 'n': n, 'tin': tin, 'sp': sp, 'z': z, 'dx': dx, 'dy': dy,
                            'flip': bool(op.get('flip')), 'crop_b': round(crop_b, 2), 'gamma': g, 'ins': bool(op.get('ins')),
                            'film': INV.get(op.get('f')) or film_of(name)})
            # clip audio actually used by the render (s00 bed at clip_audio_db, the 'a' / 'lufs' film lines; retimed shots are silent unless 'a')
            if 'lufs' in op or 'a' in op or (sp == 1.0 and S.get('clip_audio_db', -99) > -90):
                if m['audio']:
                    P['film_audio'].append({'name': name, 'rec': F0 + f0, 'n': n, 'tin': tin, 'sp': sp,
                                            'db': op.get('a', S.get('clip_audio_db')) if 'lufs' not in op else None, 'lufs': op.get('lufs'),
                                            'line': bool(op.get('ins'))})
        for j, (kind, arg, a, b) in enumerate(S.get('overlays', [])):
            b = min(b, L)
            if b <= a: continue
            P['ovl'].append({'sec': S['voice'], 'si': si, 'j': j, 'kind': kind, 'arg': arg, 'rec': F0 + round(a * FPS),
                             'n': round(b * FPS) - round(a * FPS), 'a': a, 'b': b})
        vp = os.path.join(VOICE, S['voice'] + '.mp3')
        if vp not in P['media']: P['media'][vp] = dict(probe(vp), path=vp)
        for a, b, at in S['pieces']:
            P['voice'].append({'path': vp, 'a': a, 'b': b, 'rec': F0 + round(at * FPS)})
        for t, w, gdb in S.get('sfx', []):
            if t < L:
                wp = os.path.normpath(os.path.join(HERE, w))
                if wp not in P['media']: P['media'][wp] = dict(probe(wp), path=wp)
                P['sfx'].append({'path': wp, 'rec': F0 + round(t * FPS), 'db': gdb})
        tg += L
    P['total'] = round(tg * FPS)
    busy = {}   # SFX that overlap (whoosh, fill, stamp of a stat card) are mixed in the render: second track for the overlapping ones
    for x in P['sfx']:
        x['n'] = min(max(1, int(P['media'][x['path']]['dur'] * FPS)), P['total'] - x['rec'])
        for tr in (4, 5, 6):
            if all(x['rec'] + x['n'] <= a or x['rec'] >= b for a, b in busy.get(tr, [])):
                x['track'] = tr; busy.setdefault(tr, []).append((x['rec'], x['rec'] + x['n'])); break
    for p in (MUSIC, FINAL): P['media'][p] = dict(probe(p), path=p)
    # overlay tracks: first free of V2..V4 in EDL order (later EDL overlays drawn on top, as in the render)
    busy = {}
    for o in P['ovl']:
        for tr in (2, 3, 4):
            if all(o['rec'] + o['n'] <= s or o['rec'] >= e for s, e in busy.get(tr, [])):
                o['track'] = tr; busy.setdefault(tr, []).append((o['rec'], o['rec'] + o['n'])); break
        else: raise RuntimeError('more than three overlapping overlays')
    return P

# ------------------------------------------------------------------------------------------------------------------------------- gfx
def slug(s): return re.sub(r'[^a-z0-9]+', '-', str(s).lower()).strip('-')[:40]
def draw_gfx(P):
    """the render's own overlay drawings: render_cj.py's fit_word / overlay_png / tile run as written, stat cards in their final frame"""
    from PIL import Image
    E = json.load(open(EDL))
    for d in ('ep01', 'ep03', 'ep_backrooms'): sys.path.insert(0, os.path.join(HERE, '..', d))
    import anim
    if E.get('tiers'): anim.set_tiers(E['tiers'])
    src_rcj = open(os.path.join(HERE, 'render_cj.py'), encoding='utf-8').read()
    ns = {'os': os, 'json': json, 'EDIR': HERE, 'CLIPS': CLIPS, 'E': E}
    exec('from gfx import rank_card, film_label, f as gf, shadow_text, WHITE as GWHITE\nimport gfx_br as gx', ns)
    mod = ast.parse(src_rcj)
    keep = [n for n in mod.body if isinstance(n, ast.FunctionDef) and n.name in ('rel', 'tile', 'fit_word', 'overlay_png')]
    exec(compile(ast.Module(body=keep, type_ignores=[]), 'render_cj.py', 'exec'), ns)
    os.makedirs(GFX, exist_ok=True)
    tmp = os.path.join(RES, '_stat_frames')
    for o in P['ovl']:
        nm = f"{o['sec']}_{o['j']:02d}_{o['kind']}_" + slug(o['arg'][1] if o['kind'] == 'rank' else o['arg'].get('name') if o['kind'] == 'stats'
                                                             else os.path.splitext(os.path.basename(o['arg']))[0] if o['kind'] == 'png' else o['arg'])
        if nm[-1].isdigit(): nm += '_card'   # a trailing number would make Resolve read the PNG as an image-sequence frame
        out = os.path.join(GFX, nm + '.png')
        if o['kind'] == 'stats':
            a = dict(o['arg']); a['tile_png'] = ns['tile'](a['tile_png']); a['dur'] = min(a['dur'], o['b'] - o['a'])
            d = os.path.join(tmp, nm)
            if os.path.isdir(d):
                for p in os.listdir(d): os.remove(os.path.join(d, p))
            n, x, y = anim.stat_card(d, fps=FPS, **a)
            last = Image.open(os.path.join(d, f'{n - 1:04d}.png')).convert('RGBA')
            im = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); im.alpha_composite(last, (x, y)); im.save(out)
        else:
            p = ns['overlay_png'](o['kind'], o['arg'], out)
            if p != out: Image.open(p).convert('RGBA').save(out)
        o['png'] = out
    # a black frame for nothing: V1 has no BLACK shots in this EDL (checked in prep)
    print('gfx', len(P['ovl']), 'PNGs in', GFX)

# ------------------------------------------------------------------------------------------------------------------------------- xml
# V1 goes in as FCP7 XML: Resolve keeps its Time Remap speed as a clip speed on the normal pool clip (an FCPXML timeMap came in as one compound
# clip per retimed shot). Resolve reads a clipitem <in> (sequence frames, 30) as source time in*speed/30 s; on the 23.976 downloads stored
# with a 1/16000 time base it lands 0.1 % late (measured: 3287 for frame 3284), so their <in> is divided by 1.001.
def xrate(fps):
    f = Fr(fps); nt = f.denominator == 1001; tb = round(float(f) * 1.001) if nt else round(float(f))
    return f'<rate><timebase>{tb}</timebase><ntsc>{"TRUE" if nt else "FALSE"}</ntsc></rate>'
def write_xml(P):
    from xml.sax.saxutils import escape as esc
    items, files, pos = [], set(), 0
    cal = json.load(open(CAL)) if os.path.exists(CAL) else {}   # per-shot <in> offsets measured by 'calibrate'
    for i, s in enumerate(P['v1']):
        assert s['rec'] == pos, ('V1 not contiguous', s)
        m = P['media'][s['name']]; fn = os.path.basename(m['path']); fid = 'file-' + s['name']
        url = 'file://localhost/' + quote(m['path'].replace(chr(92), '/'), safe='/:')
        fe = (f'<file id="{fid}"/>' if fid in files else
              f'<file id="{fid}"><name>{esc(fn)}</name><pathurl>{esc(url)}</pathurl>{xrate(m["fps"])}<duration>{int(m["dur"] * float(Fr(m["fps"])))}</duration>'
              f'<media><video><samplecharacteristics><width>{m["w"]}</width><height>{m["h"]}</height></samplecharacteristics></video></media></file>')
        files.add(fid)
        corr = 1.001 if (Fr(m['fps']).denominator == 1001 and m.get('tb') == '1/16000') else 1.0
        fin = round(s['tin'] * FPS / s['sp'] / corr - cal.get(str(i), 0.0))
        flt = '' if s['sp'] == 1 else (
            '<filter><effect><name>Time Remap</name><effectid>timeremap</effectid><effectcategory>motion</effectcategory><effecttype>motion</effecttype>'
            '<mediatype>video</mediatype><parameter><parameterid>variablespeed</parameterid><name>variablespeed</name><value>0</value></parameter>'
            f'<parameter><parameterid>speed</parameterid><name>speed</name><value>{s["sp"] * 100:.3f}</value></parameter>'
            '<parameter><parameterid>reverse</parameterid><name>reverse</name><value>FALSE</value></parameter>'
            '<parameter><parameterid>frameblending</parameterid><name>frameblending</name><value>FALSE</value></parameter></effect></filter>')
        items.append(f'<clipitem id="v1_{i:03d}"><name>{esc(fn)}</name><enabled>TRUE</enabled><duration>{int(m["dur"] * FPS)}</duration>{xrate(FPS)}'
                     f'<start>{pos}</start><end>{pos + s["n"]}</end><in>{fin}</in><out>{fin + s["n"]}</out>{fe}{flt}</clipitem>')
        pos += s['n']
    # V2..V4: the overlay stills (AppendToTimeline ignores endFrame on a still and lays every PNG down at the 5 s default, so they go in here)
    tracks = [chr(10).join(items)]
    for tr in sorted({o['track'] for o in P['ovl']}):
        its = []
        for o in sorted((o for o in P['ovl'] if o['track'] == tr), key=lambda o: o['rec']):
            fn = os.path.basename(o['png']); url = 'file://localhost/' + quote(o['png'].replace(chr(92), '/'), safe='/:')
            its.append(f'<clipitem id="ov_{o["sec"]}_{o["j"]:02d}"><name>{esc(fn)}</name><enabled>TRUE</enabled><duration>{o["n"]}</duration>{xrate(FPS)}'
                       f'<start>{o["rec"]}</start><end>{o["rec"] + o["n"]}</end><in>0</in><out>{o["n"]}</out>'
                       f'<file id="png_{o["sec"]}_{o["j"]:02d}"><name>{esc(fn)}</name><pathurl>{esc(url)}</pathurl>{xrate(FPS)}<duration>{o["n"]}</duration>'
                       f'<media><video><samplecharacteristics><width>1920</width><height>1080</height></samplecharacteristics></video></media></file></clipitem>')
        tracks.append(chr(10).join(its))
    NL = chr(10)
    x = ('<?xml version="1.0" encoding="UTF-8"?>' + NL + '<!DOCTYPE xmeml>' + NL + '<xmeml version="5"><sequence id="seq"><name>EP08 V1 shots</name>'
         f'<duration>{pos}</duration>{xrate(FPS)}<timecode>{xrate(FPS)}<string>00:00:00:00</string><frame>0</frame><displayformat>NDF</displayformat></timecode>'
         f'<media><video><format><samplecharacteristics><width>1920</width><height>1080</height>{xrate(FPS)}</samplecharacteristics></format><track>'
         + NL + ('</track>' + NL + '<track>').join(tracks) + NL + '</track></video></media></sequence></xmeml>' + NL)
    open(XML, 'w', encoding='utf-8').write(x)
    print('xml', len(items), 'shots,', pos, 'frames ->', XML)

def prep():
    P = make_plan()
    os.makedirs(RES, exist_ok=True)
    draw_gfx(P); write_xml(P)
    json.dump(P, open(PLAN, 'w'), indent=1)
    print('plan', len(P['v1']), 'shots', len(P['ovl']), 'overlays', len(P['voice']), 'voice pieces', len(P['film_audio']), 'film-audio clips',
          len(P['sfx']), 'sfx', P['total'], 'frames')

# ------------------------------------------------------------------------------------------------------------------------------- resolve
def resolve():
    lib = os.environ.get('RESOLVE_SCRIPT_LIB', r'C:\All The Programs\Davinci Resolve Files\fusionscript.dll')
    os.environ['RESOLVE_SCRIPT_LIB'] = lib; os.add_dll_directory(os.path.dirname(lib))
    sys.path.append(os.path.expandvars(r'%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules'))
    import DaVinciResolveScript as dvr
    r = dvr.scriptapp('Resolve')
    if not r: sys.exit('Resolve scripting not reachable: Preferences > System > General > External scripting using = Local')
    return r

def build():
    P = json.load(open(PLAN)); r = resolve(); pm = r.GetProjectManager()
    if PROJECT in (pm.GetProjectListInCurrentFolder() or []): sys.exit(f'project "{PROJECT}" already exists: not touching it')
    pr = pm.CreateProject(PROJECT)
    if not pr: sys.exit('CreateProject failed')
    for k, v in (('timelineFrameRate', '30'), ('timelineResolutionWidth', '1920'), ('timelineResolutionHeight', '1080'),
                 ('timelinePlaybackFrameRate', '30')):
        pr.SetSetting(k, v)
    mp = pr.GetMediaPool(); root = mp.GetRootFolder(); bins = {}
    def bin_(n):
        if n not in bins: bins[n] = mp.AddSubFolder(root, n)
        return bins[n]
    items = {}
    def imp(path, b):
        if path in items: return items[path]
        mp.SetCurrentFolder(bin_(b)); got = mp.ImportMedia([path])
        if not got: raise RuntimeError('import failed: ' + path)
        items[path] = got[0]; return got[0]
    for s in P['v1']: imp(P['media'][s['name']]['path'], film_of(s['name']))
    for v in P['voice']: imp(v['path'], 'Voice')
    for a in P['film_audio']: imp(P['media'][a['name']]['path'], film_of(a['name']))
    imp(MUSIC, 'Music')
    for x in P['sfx']: imp(x['path'], 'SFX')
    for o in P['ovl']: imp(o['png'], 'Graphics')
    imp(FINAL, 'Final')
    film_bins = [bins[b] for b in bins if b not in ('Voice', 'Music', 'SFX', 'Final')]
    # V1 and the overlay tracks from the XML (the API cannot set clip speed or a still's length), linked to the pool clips already in the film bins
    mp.SetCurrentFolder(root)
    tl = mp.ImportTimelineFromFile(XML, {'timelineName': TIMELINE, 'importSourceClips': False, 'sourceClipsFolders': film_bins})
    if not tl: sys.exit('XML import failed')
    pr.SetCurrentTimeline(tl)
    for k in range(tl.GetTrackCount('audio'), 0, -1):   # the V1 import is picture only; drop any audio it linked
        its = tl.GetItemListInTrack('audio', k) or []
        if its: tl.DeleteClips(its)
    st = tl.GetStartFrame()
    v1 = sorted(tl.GetItemListInTrack('video', 1) or [], key=lambda i: i.GetStart())
    print('V1 items', len(v1), 'plan', len(P['v1']))
    for it, s in zip(v1, P['v1']):
        it.SetProperty({'Scaling': 3, 'ZoomX': s['z'] + 0.015, 'ZoomY': s['z'] + 0.015, 'Pan': -s['dx'] * s['z'], 'Tilt': s['dy'] * s['z'],
                        'FlipX': s['flip'], 'CropBottom': s['crop_b']})
        it.SetClipColor(COLOURS[s['film']])
        it.SetCDL({'NodeIndex': '1', 'Slope': '1.04 1.04 1.04', 'Offset': '-0.02 -0.02 -0.02',
                   'Power': ' '.join([f"{1 / s['gamma']:.4f}"] * 3), 'Saturation': '0.95'})
    # tracks
    nv = max(o['track'] for o in P['ovl']) + 1
    while tl.GetTrackCount('video') < nv: tl.AddTrack('video')
    na = max(x['track'] for x in P['sfx'])
    for _ in range(na - tl.GetTrackCount('audio')): tl.AddTrack('audio', 'stereo')
    for i, n in enumerate(['V1 Film shots', 'V2 Overlays', 'V3 Overlays', 'V4 Overlays'][:nv - 1], 1): tl.SetTrackName('video', i, n)
    tl.SetTrackName('video', nv, 'FINAL reference')
    for i, n in enumerate(['A1 Narration', 'A2 Film audio', 'A3 Music', 'A4 SFX', 'A5 SFX overlap'][:na], 1): tl.SetTrackName('audio', i, n)
    def app(path, s0, s1, track, rec, mtype):
        got = mp.AppendToTimeline([{'mediaPoolItem': items[path], 'startFrame': s0, 'endFrame': s1, 'trackIndex': track,
                                    'recordFrame': st + rec, 'mediaType': mtype}])
        if not got: print('append failed', os.path.basename(path), rec, track)
        return got[0] if got else None
    ref = app(FINAL, 0, P['total'] - 1, nv, 0, 1)
    tl.SetTrackEnable('video', nv, False)
    for v in P['voice']: app(v['path'], round(v['a'] * FPS), round(v['b'] * FPS), 1, v['rec'], 2)   # audio endFrame is exclusive
    for a in P['film_audio']:
        fps = float(Fr(P['media'][a['name']]['fps'])); s0 = round(a['tin'] * fps)
        app(P['media'][a['name']]['path'], s0, s0 + round(a['n'] / FPS * a['sp'] * fps), 2, a['rec'], 2)
    mfr = round(P['media'][MUSIC]['dur'] * FPS) - 1
    app(MUSIC, 0, min(P['total'], mfr + 1), 3, 0, 2)
    for x in P['sfx']:
        app(x['path'], 0, x['n'], x['track'], x['rec'], 2)
    for s in P['sections']: tl.AddMarker(s['F0'], 'Blue' if s['id'] not in ('s00', 's01', 's11') else 'Green', s['name'], s['id'], 1)
    pm.SaveProject()
    print('saved', PROJECT, '/', TIMELINE)

def check():
    P = json.load(open(PLAN)); r = resolve(); pm = r.GetProjectManager(); pr = pm.GetCurrentProject()
    assert pr.GetName() == PROJECT, pr.GetName()
    tl = next(pr.GetTimelineByIndex(i) for i in range(1, pr.GetTimelineCount() + 1) if pr.GetTimelineByIndex(i).GetName() == TIMELINE)
    pr.SetCurrentTimeline(tl); st = tl.GetStartFrame()
    rep = {'length_frames': tl.GetEndFrame() - st, 'length_s': (tl.GetEndFrame() - st) / FPS}
    for kind in ('video', 'audio'):
        for i in range(1, tl.GetTrackCount(kind) + 1):
            its = tl.GetItemListInTrack(kind, i) or []
            rep[f'{kind[0].upper()}{i} {tl.GetTrackName(kind, i)}'] = len(its)
    v1 = sorted(tl.GetItemListInTrack('video', 1), key=lambda i: i.GetStart())
    bad = [(s['sec'], s['k'], s['name'], it.GetStart() - st, s['rec'], it.GetDuration(), s['n']) for it, s in zip(v1, P['v1'])
           if it.GetStart() - st != s['rec'] or it.GetDuration() != s['n'] or it.GetName() != os.path.basename(P['media'][s['name']]['path'])]
    rep['v1_mismatch'] = bad[:20]; rep['v1_mismatch_n'] = len(bad)
    # source in-point (frame index the render's ffmpeg -ss lands on) and speed, per shot
    errs = []
    for it, s in zip(v1, P['v1']):
        fps = float(it.GetMediaPoolItem().GetClipProperty('FPS')); e0 = s['tin'] * fps; g0 = it.GetSourceStartFrame(); g1 = it.GetSourceEndFrame()
        spd = (g1 - g0) / max(1, (s['n'] - 1) * fps / FPS)
        if abs(g0 - e0) > 1.5 or (s['n'] > 20 and abs(spd - s['sp']) > 0.08): errs.append((s['sec'], s['k'], s['name'], g0, round(e0, 1), round(spd, 3), s['sp']))
    rep['v1_in_or_speed_off'] = errs
    rep['retimed_shots'] = sum(1 for s in P['v1'] if s['sp'] != 1)
    # every other item at its planned place and length
    want = {('video', tr): sorted((o['rec'], o['n'], os.path.basename(o['png'])) for o in P['ovl'] if o['track'] == tr) for tr in (2, 3, 4)}
    want[('audio', 1)] = sorted((v['rec'], round(v['b'] * FPS) - round(v['a'] * FPS), os.path.basename(v['path'])) for v in P['voice'])
    want[('audio', 2)] = sorted((a['rec'], None, os.path.basename(P['media'][a['name']]['path'])) for a in P['film_audio'])
    for tr in {x['track'] for x in P['sfx']}:
        want[('audio', tr)] = sorted((x['rec'], x['n'], os.path.basename(x['path'])) for x in P['sfx'] if x['track'] == tr)
    off = []
    for (kind, tr), w in want.items():
        got = sorted((i.GetStart() - st, i.GetDuration(), i.GetName()) for i in (tl.GetItemListInTrack(kind, tr) or []))
        if len(got) != len(w): off.append((kind, tr, 'count', len(got), len(w))); continue
        off += [(kind, tr, g, x) for g, x in zip(got, w) if g[0] != x[0] or g[2] != x[2] or (x[1] is not None and g[1] != x[1])]
    rep['other_items_off'] = off[:30]
    print(json.dumps(rep, indent=1))
    times = [float(x) for x in (sys.argv[2].split(',') if len(sys.argv) > 2 else '8.5,61.2,131.4,203.0,288.7,397.3'.split(','))]
    out = os.path.join(RES, 'check'); os.makedirs(out, exist_ok=True)
    r.OpenPage('edit')
    for tt in times:
        f = round(tt * FPS) + st
        h, m, s_, fr = f // 108000, f // 1800 % 60, f // 30 % 60, f % 30
        tl.SetCurrentTimecode(f'{h:02d}:{m:02d}:{s_:02d}:{fr:02d}')
        pr.ExportCurrentFrameAsStill(os.path.join(out, f'resolve_{tt:06.1f}.png'))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{round(tt * FPS) / FPS:.4f}', '-i', FINAL, '-frames:v', '1',
                        os.path.join(out, f'final_{tt:06.1f}.png')])
    print('frames in', out)

def calibrate():
    """read where Resolve put each V1 in-point (in its own frame numbering = source time x its FPS) and store the <in> offset per shot"""
    P = json.load(open(PLAN)); r = resolve(); pr = r.GetProjectManager().GetCurrentProject(); tl = pr.GetCurrentTimeline()
    assert pr.GetName() == PROJECT and tl.GetName() == TIMELINE
    cal = json.load(open(CAL)) if os.path.exists(CAL) else {}
    v1 = sorted(tl.GetItemListInTrack('video', 1), key=lambda i: i.GetStart())
    for i, (it, s) in enumerate(zip(v1, P['v1'])):
        rf = float(it.GetMediaPoolItem().GetClipProperty('FPS'))
        err = it.GetSourceStartFrame() - s['tin'] * rf           # source frames
        cal[str(i)] = cal.get(str(i), 0.0) + err * FPS / (s['sp'] * rf)   # in sequence frames of the retimed clip
    json.dump(cal, open(CAL, 'w'), indent=0)
    print('calibration for', len(cal), 'shots; max |offset|', round(max(abs(v) for v in cal.values()), 2), 'frames')

if __name__ == '__main__':
    {'prep': prep, 'build': build, 'check': check, 'calibrate': calibrate}[sys.argv[1]]()
