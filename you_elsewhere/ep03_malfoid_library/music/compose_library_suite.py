# You, Elsewhere EP3 (Malfoid in the library): ~30 min jazz piano trio suite, 120 BPM.
# Owner's rules (10/23-10/25): jazz piano trio only; Hedwig's melody exactly as written, in one register, for the
# whole first minute (variations only after 1:00); chords always contain the melody note (no semitone clashes);
# warm Salamander tone; upright bass full and present everywhere (never long gaps); no ride swing, soft brushes
# or no drums; steady energy, no loud entries; bright, no slow ballads.
# Pipeline: per-instrument MIDI -> sfizz_render -> ffmpeg mix per track (EP1 v1 piano chain, fuller bass EQ,
# Chamber Warm IR) -> loudness-matched 4 s crossfades -> suite WAV 48k/24-bit + mp3 + 90 s excerpt + tracklist.
# usage: python compose_library_suite.py [track ids...]   (no args = all tracks + join)
import os, sys, json, random, subprocess, importlib.util

SUITE_EP1 = r'C:\Users\hw549\Downloads\YTP1\YouElsewhere\ep01_malfoid\suite\compose_suite.py'
spec = importlib.util.spec_from_file_location('compose_suite', SUITE_EP1)
cs = importlib.util.module_from_spec(spec); spec.loader.exec_module(cs)

OUT = r'C:\Users\hw549\Downloads\YTP1\YouElsewhere\ep03_malfoid_library\music'
WORK = r'E:\YTP2\YouElsewhere\ep03_malfoid_library\suite_tracks'      # stems on E: (C: is nearly full)
BPM = 120
cs.QUAL.update({'m69': [3, 9, 14, 7], '69': [4, 9, 14, 7], '7b5': [4, 6, 10, 0], 'maj7#5': [4, 8, 11, 14]})

# ------------------------------------------------------------------ themes
HEDWIG = dict(cs.HEDWIG, chords=['Em9', 'Em9', 'Am9', 'B7', 'Em9', 'B7b5', 'Em9', 'Em9',
                                 'Em9', 'Em9', 'Bm9', 'Cmaj7#5', 'Am9|F#7', 'C9', 'Em9', 'Em9'])

LAMPLIGHT = dict(meter=4, pickup=0,   # original, F major
    mel=[('A4', 1), ('C5', 1), ('E5', 2), ('D5', 1.5), ('C5', .5), ('A4', 2), ('Bb4', 1), ('D5', 1), ('F5', 1.5), ('E5', .5),
         ('E5', 3), ('-', 1), ('C5', 1), ('E5', 1), ('G5', 2), ('F#5', 1.5), ('E5', .5), ('D5', 1), ('C5', 1),
         ('Bb4', 2), ('D5', 1), ('F5', 1), ('E5', 2), ('D5', 1), ('C5', 1),
         ('A5', 2), ('G5', 1), ('F5', 1), ('Eb5', 2), ('C5', 1), ('A4', 1), ('D5', 1.5), ('F5', .5), ('A5', 2),
         ('Db5', 2), ('G5', 1), ('F5', 1), ('E5', 1), ('C5', 1), ('F#5', 1), ('A5', 1),
         ('G5', 1.5), ('F5', .5), ('E5', 1), ('Bb4', 1), ('A4', 1), ('C5', 1), ('F5', 2), ('F5', 2), ('E5', 1), ('C5', 1)],
    chords=['Fmaj7', 'Dm7', 'Gm7', 'C7', 'Am7', 'D7', 'Gm7', 'C7', 'Fmaj7', 'F7', 'Bbmaj7', 'Bbm6|Eb9',
            'Am7|D7', 'Gm7|C7', 'Fmaj7', 'Gm7|C7'])

MARGINS = dict(meter=3, pickup=0,     # original, Bb major waltz
    mel=[('D5', 2), ('F5', 1), ('Bb5', 2), ('A5', 1), ('G5', 1.5), ('F5', .5), ('Eb5', 1), ('C5', 2), ('A4', 1),
         ('F5', 2), ('A5', 1), ('B5', 1.5), ('A5', .5), ('G5', 1), ('Eb5', 2), ('G5', 1), ('F5', 3),
         ('D5', 1), ('F5', 1), ('A5', 1), ('Ab5', 2), ('F5', 1), ('G5', 2), ('Bb5', 1), ('C6', 1.5), ('Bb5', .5), ('Gb5', 1),
         ('F5', 2), ('D5', 1), ('F5', 1), ('D5', 1), ('B4', 1), ('C5', 1), ('Eb5', .5), ('A4', 1.5), ('Bb4', 3)],
    chords=['Bbmaj7', 'Gm7', 'Cm7', 'F7', 'Dm7', 'G7', 'Cm7', 'F7', 'Bbmaj7', 'Bb7', 'Ebmaj7', 'Ab9',
            'Dm7', 'G7', 'Cm7|F7', 'Bbmaj7'])

TURNING_PAGES = dict(meter=4, pickup=0,   # original, G major
    mel=[('B4', 1), ('D5', 1), ('F#5', 1.5), ('E5', .5), ('D5', 2), ('B4', 1), ('G4', 1), ('C5', 1), ('E5', 1), ('G5', 2),
         ('F#5', 2), ('E5', 1), ('C5', 1), ('D5', 1.5), ('F#5', .5), ('A5', 2), ('G#5', 1), ('F#5', 1), ('E5', 1), ('D5', 1),
         ('C5', 2), ('E5', 1), ('A5', 1), ('F#5', 3), ('-', 1),
         ('B5', 2), ('A5', 1), ('G5', 1), ('F5', 2), ('D5', 1), ('B4', 1), ('E5', 1.5), ('G5', .5), ('B5', 2),
         ('A5', 1), ('G5', 1), ('Eb5', 1), ('C5', 1), ('D5', 1), ('F#5', 1), ('G#5', 1), ('B5', 1),
         ('A5', 1.5), ('G5', .5), ('F#5', 1), ('C5', 1), ('B4', 1), ('D5', 1), ('G5', 2), ('-', 1), ('E5', 1), ('F#5', 1), ('A5', 1)],
    chords=['Gmaj7', 'Em7', 'Am7', 'D7', 'Bm7', 'E7', 'Am7', 'D7', 'Gmaj7', 'G7', 'Cmaj7', 'Cm6|F9',
            'Bm7|E7', 'Am7|D7', 'Gmaj7', 'Am7|D7'])

# ------------------------------------------------------------------ helpers
SCALE = {'m': [0, 2, 3, 5, 7, 9, 10], 'maj': [0, 2, 4, 5, 7, 9, 11], 'dom': [0, 2, 4, 5, 7, 9, 10]}
CT = {'m': [0, 3, 7, 10], 'maj': [0, 4, 7, 11], 'dom': [0, 4, 7, 10]}

def kind(sym):
    _, q = cs.parse(sym)
    return 'm' if q.startswith('m') and not q.startswith('maj') else 'maj' if q.startswith('maj') or q in ('69', '6', '') else 'dom'

def chord_at(theme, beat):
    bars = cs.bars_of(theme); M = theme['meter']
    sub = bars[int(beat // M) % len(bars)]
    return sub[min(len(sub) - 1, int((beat % M) / (M / len(sub))))]

def pcs(sym, table):
    r, _ = cs.parse(sym)
    return [(r + i) % 12 for i in table[kind(sym)]]

def nearest(pcl, target, lo, hi):
    return min((n for n in range(lo, hi + 1) if n % 12 in pcl), key=lambda n: abs(n - target))

class Track(cs.Song):
    def __init__(self, theme, seed):
        super().__init__(BPM, theme['meter'], seed)
        self.theme = theme; self.mel = []           # (start, end, pitch) of everything played as a lead line
        self.L = len(theme['chords']) * theme['meter']
    def lead(self, t, n, v, d, jitter=0.01):
        self.add('piano', t, n, v, d, jitter); self.mel.append((t, t + d, n))

# ------------------------------------------------------------------ lead lines
def melody(s, start, vel, exact=False, grace=0.0):
    """exact=True: Hedwig as written (straight). Otherwise a light swing on offbeat eighths (originals only)."""
    th = s.theme; t = start - th['pickup']
    for n, b in th['mel']:
        if n != '-':
            nn = cs.m(n); off = 0 if exact or abs((t % 1) - 0.5) > 1e-6 else 0.12
            v = vel + (4 if b >= 2 else 0) + s.rng.randint(-3, 3)
            if grace and b >= 2 and s.rng.random() < grace:       # variation only: a short grace note from below
                s.add('piano', t + off - 0.12, nn - 1, v - 14, 0.12, 0.0)
            s.lead(t + off, nn, v, b * 0.95)
        t += b

def solo(s, start, vel=58):
    """Calm improvised chorus: short phrases, mostly quarters with a few eighths, chord tones on the beat."""
    th = s.theme; x = 0; n = 74
    while x < s.L - 2:
        end = min(s.L - 1, x + s.rng.choice([3, 4, 5, 6])); d = s.rng.choice([-1, 1])
        while x < end:
            sym = chord_at(th, x)
            pool = pcs(sym, CT if abs(x % 1) < 1e-6 else SCALE)
            sc = sorted(p for p in range(65, 84) if p % 12 in pool)
            up = [p for p in sc if p > n]; dn = [p for p in sc if p < n]
            n = up[0] if d > 0 and up else dn[-1] if dn else n
            if n >= 80: d = -1
            if n <= 67: d = 1
            if s.rng.random() < 0.2: d = -d
            step = 0.5 if s.rng.random() < 0.3 else 1.0
            last = x + step >= end
            s.lead(start + x + (0.1 if step == 0.5 and x % 1 else 0), n, vel + s.rng.randint(-4, 4),
                   (end - x + 0.5) * 0.9 if last else step * 0.85)
            x += step
        x = end + s.rng.choice([1, 2, 3])

# ------------------------------------------------------------------ accompaniment
def clear_of_melody(s, notes, t0, t1):
    """Drop voicing notes a semitone from any lead note sounding in [t0, t1); also keep them below the lead."""
    over = [n for a, b, n in s.mel if a < t1 and b > t0]
    keep = [v for v in notes if all((v - n) % 12 not in (1, 11) for n in over) and all(v < n for n in over)]
    return keep if len(keep) >= 2 else sorted(notes)[:2]

def comp(s, start, style, vel, prev=None):
    th = s.theme; M = th['meter']
    for i, bar in enumerate(cs.bars_of(th)):
        at = start + i * M; half = M / len(bar)
        for j, sym in enumerate(bar):
            v = cs.voicing(sym, prev, top_limit=64); prev = v; t0 = at + j * half
            if style == 'pad':
                hits = [(0, half * 0.97)]
            elif M == 3:                  # waltz: soft chords on 2 and 3
                hits = [(1, 0.8), (2, 0.8)] if half == 3 else [(0, half * 0.9)]
            else:                         # 4/4: 1 and the and of 2, or a half-note pair
                hits = [(0, 1.4), (1.5, 1.8)] if (half == 4 and s.rng.random() < 0.6) else [(k, min(2, half) * 0.9) for k in range(0, int(half), 2)]
            for off, d in hits:
                notes = clear_of_melody(s, v, t0 + off, t0 + off + d)
                for k, n in enumerate(notes):
                    s.add('piano', t0 + off + 0.012 * k, n, vel - (3 if off else 0) + s.rng.randint(-2, 2), d, 0.006)
    return prev

def bass(s, start, style, vel=86):
    th = s.theme; M = th['meter']; bars = cs.bars_of(th); prev = 40
    for i, bar in enumerate(bars):
        at = start + i * M
        nxt = cs.root_note(bars[(i + 1) % len(bars)][0])
        for beat in range(M):
            sym = chord_at(th, i * M + beat); first = beat == 0 or (len(bar) > 1 and beat == M // 2)
            if style == 'two':            # root + fifth, every bar, notes held: the bass never drops out
                if M == 3:
                    if beat == 0: n, d = cs.root_note(bar[0]), 1.95
                    elif beat == 2: n, d = cs.fifth_note(bar[-1]) if len(bar) == 1 else cs.root_note(bar[-1]), 0.95
                    else: continue
                else:
                    if beat == 0: n, d = cs.root_note(bar[0]), 1.95
                    elif beat == 2: n, d = cs.fifth_note(bar[-1]) if len(bar) == 1 else cs.root_note(bar[-1]), 1.95
                    else: continue
            else:                         # walking quarters: chord tone, passing tone, approach to the next root
                if first: n = cs.root_note(sym)
                elif beat == M - 1: n = nxt + (1 if prev > nxt else -1) if s.rng.random() < 0.6 else nearest(pcs(sym, SCALE), nxt + (2 if prev > nxt else -2), 28, 50)
                else:
                    n = nearest(pcs(sym, CT), prev + s.rng.choice([-5, -3, 3, 4, 5]), 28, 50)
                    if n == prev: n = nearest(pcs(sym, SCALE), prev + 2, 28, 50)
                d = 0.95
            s.add('bass', at + beat, n, vel - (0 if beat == 0 else 7) + s.rng.randint(-3, 3), d, 0.008)
            prev = n

def brushes(s, start, nbars, vel=1.0):
    """Swirly brushes: slow stir, soft taps on the backbeats, foot hat. No ride."""
    M = s.meter
    for i in range(nbars):
        at = start + i * M
        if M == 3:
            s.add('stir', at, 60, (68 + s.rng.randint(-5, 5)) * vel, 2.8, 0.008)
            for b, v in ((1, 22), (2, 18)): s.add('stir', at + b, 38, (v + s.rng.randint(-3, 3)) * vel, 0.3, 0.008)
            s.add('stir', at + 1, 44, 32 * vel, 0.3, 0.004)
        else:
            for b in (0, 2): s.add('stir', at + b, 60, (66 + s.rng.randint(-5, 5)) * vel, 1.9, 0.008)
            for b in (1, 3):
                s.add('stir', at + b, 38, (22 + s.rng.randint(-3, 3)) * vel, 0.3, 0.008)
                s.add('stir', at + b, 44, 30 * vel, 0.3, 0.004)

def ending(s, t):
    th = s.theme; sym = th['chords'][-1].split('|')[-1]
    s.add('bass', t, cs.root_note(sym), 78, 4.5, 0)
    for k, n in enumerate(cs.voicing(sym, top_limit=64)): s.add('piano', t + 0.04 * k, n, 38, 6.0, 0)
    s.add('piano', t, cs.root_note(sym, 36, 48), 44, 6.0, 0)

# ------------------------------------------------------------------ forms
# section codes: A melody+pads+two-feel bass (no drums) | B melody+comping+two-feel+brushes | C melody+comping+walking+brushes
#                G melody with grace notes (variation) | S improvised chorus | O melody+pads+two-feel+soft brushes
def build_track(theme, form, seed, exact):
    s = Track(theme, seed); t = theme['pickup']; n = len(theme['chords'])
    for sec in form:
        vel = 60
        if sec in 'ABCGO':
            melody(s, t, vel + (2 if sec in 'BC' else 0), exact=exact or sec != 'G', grace=0.5 if sec == 'G' else 0)
        if sec == 'S': solo(s, t, 58)
        comp(s, t, 'pad' if sec in 'AO' else 'beat', 34 if sec in 'AO' else 35)
        bass(s, t, 'walk' if sec in 'CGS' else 'two', 84 if sec != 'A' else 80)
        if sec != 'A': brushes(s, t, n, 0.7 if sec == 'O' else 0.9)
        t += s.L
    ending(s, t)
    return s

TRACKS = {   # id: (title, theme, form, seed, exact-melody)
    '01_hedwig_in_the_stacks': ('Hedwig in the Stacks', HEDWIG, 'ABCGSO', 11, True),       # 0:00-1:12 exact
    '02_common_room_waltz': ('Common Room Waltz', cs.COMMON_ROOM, 'ABCSCO', 21, False),
    '03_lamplight_index': ('Lamplight Index', LAMPLIGHT, 'ABSCO', 31, False),
    '04_green_scarf': ('Green Scarf', cs.GREEN_SCARF, 'ABCSCO', 41, False),
    '05_lake_window': ('Lake Window', cs.LAKE_WINDOW, 'ABSCO', 51, False),
    '06_hedwig_by_the_window': ('Hedwig by the Window', HEDWIG, 'BCSGCO', 61, True),
    '07_margins': ('Margins', MARGINS, 'ABCSCO', 71, False),
    '08_fireside_letters': ('Fireside Letters', cs.FIRESIDE, 'ABSCO', 81, False),
    '09_turning_pages': ('Turning Pages', TURNING_PAGES, 'ABSCO', 91, False),
    '10_rain_on_the_glass': ('Rain on the Glass', cs.RAIN, 'ABSCO', 101, False),
    '11_green_scarf_reprise': ('Green Scarf, Reprise', cs.GREEN_SCARF, 'BCSCO', 111, False),
    '12_hedwig_last_page': ('Hedwig, Last Page', HEDWIG, 'ABSGO', 121, True),
}

# ------------------------------------------------------------------ render + mix
GAIN = dict(cs.GAIN, bass=11, stir=20)
FILT = dict(cs.FILT,
    bass='pan=mono|c0=0.5*c0+0.5*c1,highpass=f=40,equalizer=f=60:t=q:w=1:g=-1.5,equalizer=f=160:t=q:w=0.9:g=3,'
         'equalizer=f=900:t=q:w=1.2:g=2,lowpass=f=3200,acompressor=threshold=-20dB:ratio=2.5:attack=15:release=180,'
         'pan=stereo|c0=c0|c1=c0')

def nan_free(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'astats=measure_perchannel=none', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    return 'Number of NaNs: 0.0' in r

def build(tid):
    title, theme, form, seed, exact = TRACKS[tid]
    s = build_track(theme, form, seed, exact)
    d = os.path.join(WORK, tid); os.makedirs(d, exist_ok=True)
    parts = sorted(s.ev)
    for p in parts:
        cs.write_midi(s, p, os.path.join(d, p + '.mid'))
        cs.run([cs.SFIZZ, '--sfz', cs.SFZ[p], '--midi', os.path.join(d, p + '.mid'), '--wav', os.path.join(d, p + '.wav'),
                '-s', '48000', '-q', '3', '-p', '256'])
    dur = s.length() * 60 / BPM + 3
    ins, fc = [], []
    for i, p in enumerate(parts):
        ins += ['-i', os.path.join(d, p + '.wav')]
        fc.append(f'[{i}:a]{FILT[p]},volume={GAIN[p]}dB[s{i}]')
    ins += ['-i', cs.IR]; k = len(parts)
    fc.append(''.join(f'[s{i}]' for i in range(k)) + f'amix=inputs={k}:normalize=0:duration=longest,atrim=0:{dur:.2f},asplit[dry][send]')
    fc.append('[send]highpass=f=200,lowpass=f=6000[sendf]')
    fc.append(f'[sendf][{k}:a]afir=dry=10:wet=10:length=1,volume=-10dB[wet]')          # a touch more room than EP1 (-11)
    fc.append(f'[dry][wet]amix=inputs=2:normalize=0:duration=first,lowpass=f=14000,afade=t=out:st={dur - 4:.2f}:d=4')
    out = os.path.join(WORK, tid + '.wav')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fc), '-ar', '48000', '-c:a', 'pcm_f32le', out])
    assert nan_free(out), 'NaN samples in ' + out
    print(tid, f'{dur:.1f}s', form, flush=True)
    return dur

def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float([l for l in r.splitlines() if l.strip().startswith('I:')][-1].split()[1])

def duration(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True)
    return float(r.stdout.strip())

def join():
    ids = list(TRACKS); files = [os.path.join(WORK, t + '.wav') for t in ids]
    ins = sum([['-i', f] for f in files], [])
    fc = [f'[{i}:a]volume={-20 - lufs(f):.2f}dB[n{i}]' for i, f in enumerate(files)]
    cur = '[n0]'
    for i in range(1, len(files)):
        fc.append(f'{cur}[n{i}]acrossfade=d=4:c1=tri:c2=tri[x{i}]'); cur = f'[x{i}]'
    pre = os.path.join(WORK, 'suite_premaster.wav')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fc), '-map', cur, '-c:a', 'pcm_f32le', pre])
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-17:TP=-1.5:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    js = json.loads(r[r.rindex('{'):r.rindex('}') + 1]); g = -17 - float(js['input_i'])
    base = os.path.join(OUT, 'you_elsewhere_ep03_library_suite')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', pre, '-af', f'volume={g:.2f}dB,alimiter=limit=0.84:attack=4:release=60:level=false',
            '-ar', '48000', '-c:a', 'pcm_s24le', base + '.wav'])
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', base + '.wav', '-c:a', 'libmp3lame', '-b:a', '256k', base + '.mp3'])
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', base + '.wav', '-t', '90', '-af', 'afade=t=out:st=86:d=4',
            '-c:a', 'libmp3lame', '-b:a', '256k', os.path.join(OUT, 'you_elsewhere_ep03_library_first90s.mp3')])
    # tracklist: each track starts 4 s before the previous one ends
    t = 0.0; lines = []
    for tid, f in zip(ids, files):
        title, theme, *_ = TRACKS[tid]
        mm, ss = divmod(int(round(t)), 60)
        tag = '' if theme in (cs.COMMON_ROOM, cs.GREEN_SCARF, cs.LAKE_WINDOW, cs.FIRESIDE, cs.RAIN, LAMPLIGHT, MARGINS, TURNING_PAGES) else " (Hedwig's Theme, John Williams)"
        lines.append(f'{mm}:{ss:02d} {title}{tag}')
        t += duration(f) - 4
    total = duration(base + '.wav')
    with open(os.path.join(OUT, 'tracklist.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + f'\n\n(total {int(total // 60)}:{int(total % 60):02d})\n')
    print('\n'.join(lines)); print('total', round(total, 1), 's, gain', round(g, 2))

if __name__ == '__main__':
    os.makedirs(WORK, exist_ok=True)
    todo = sys.argv[1:] or list(TRACKS)
    for tid in todo: build(tid)
    if not sys.argv[1:]: join()
