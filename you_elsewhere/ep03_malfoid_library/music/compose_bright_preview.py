# You, Elsewhere EP3 (Malfoid in the library), music step 1: Hedwig trio previews in a brighter,
# more swinging jazz-waltz arrangement at two tempos (160 = published Hedwig tempo, 120).
# Reuses the EP1 suite pipeline (compose_suite.py: voicings, MIDI writer, sfizz render, v1 mix chain)
# and the hedwig_trio_sfz_v1 sound (Salamander, FL acoustic bass, HQ jazz ride + pedal hat, Chamber Warm IR).
# New here: walking bass, swung ride with hat on 2, short comping stabs, piano fills between phrases,
# an improvised-style solo chorus, a G-major reharm chorus, ending on E6/9.
# usage: python compose_bright_preview.py [160|120 ...]   (no args = both)
import os, sys, subprocess, importlib.util

SUITE = r'C:\Users\hw549\Downloads\YTP1\YouElsewhere\ep01_malfoid\suite\compose_suite.py'
spec = importlib.util.spec_from_file_location('compose_suite', SUITE)
cs = importlib.util.module_from_spec(spec); spec.loader.exec_module(cs)
OUT = r'C:\Users\hw549\Downloads\YTP1\YouElsewhere\ep03_malfoid_library\music'

# brighter colours: 6/9 chords (rootless: 3rd/6th/9th/5th)
cs.QUAL['m69'] = [3, 9, 14, 7]
cs.QUAL['69'] = [4, 9, 14, 7]

# Hedwig in E minor, voiced bright (Em6/9, A13, Cmaj7#11, tritone-sub C9 into B7)
E_BRIGHT = ['Em69', 'Em69', 'A13', 'Cmaj7#11|B13', 'Em69', 'B7b9', 'Em69', 'Cmaj7|B7b9',
            'Em69', 'Em69', 'Gmaj7#11', 'Cmaj7#11', 'Am9', 'C9|B7b9', 'Em69', 'Cmaj7|B7b9']
# same melody, relative-major reharm (G major feel)
G_REHARM = ['G69', 'Em9|A13', 'Am9|D13', 'Gmaj9', 'Cmaj7#11', 'B7b9', 'G69', 'Am7|D9',
            'G69', 'Em9|A13', 'Dmaj9', 'Am9|E7', 'Am9|D13', 'Ebmaj7|D9', 'G69', 'Cmaj7|B7b9']

SCALE = {'m69': [0, 2, 3, 5, 7, 9, 10], 'm9': [0, 2, 3, 5, 7, 9, 10], 'm7': [0, 2, 3, 5, 7, 9, 10],
         'maj7#11': [0, 2, 4, 6, 7, 9, 11], 'maj7': [0, 2, 4, 5, 7, 9, 11], 'maj9': [0, 2, 4, 6, 7, 9, 11],
         '69': [0, 2, 4, 7, 9, 11], '13': [0, 2, 4, 5, 7, 9, 10], '9': [0, 2, 4, 5, 7, 9, 10],
         '7b9': [0, 1, 3, 4, 7, 8, 10], '7': [0, 2, 4, 5, 7, 9, 10]}
CT = {'m69': [0, 3, 7, 9], 'm9': [0, 3, 7, 10], 'm7': [0, 3, 7, 10], 'maj7#11': [0, 4, 7, 11],
      'maj7': [0, 4, 7, 11], 'maj9': [0, 4, 7, 11], '69': [0, 4, 7, 9], '13': [0, 4, 7, 10],
      '9': [0, 4, 7, 10], '7b9': [0, 4, 7, 10], '7': [0, 4, 7, 10]}

def sw_pos(x, ratio):
    """Straight-eighth position -> swung position (offbeat eighths pushed late)."""
    beat, frac = divmod(x, 1)
    return beat + (ratio if abs(frac - 0.5) < 1e-6 else frac)

def chord_at(chords, beat, meter=3):
    bar = cs.bars_of({'chords': chords})
    i = int(beat // meter) % len(bar); sub = bar[i]
    j = min(len(sub) - 1, int((beat % meter) / (meter / len(sub))))
    return sub[j]

def pcs(sym, table):
    r, q = cs.parse(sym)
    return [(r + i) % 12 for i in table.get(q, table['7'])]

def nearest(pc_list, target, lo, hi):
    c = [n for n in range(lo, hi + 1) if n % 12 in pc_list]
    return min(c, key=lambda n: abs(n - target))

# ------------------------------------------------------------------ parts
def walking(s, chords, start, vel=84):
    """Quarter-note walking bass in 3/4: chord tone on 1, a passing line, chromatic or scale approach on 3."""
    bars = cs.bars_of({'chords': chords}); prev = 40
    for i, bar in enumerate(bars):
        at = start + i * 3
        nxt = cs.root_note(bars[(i + 1) % len(bars)][0], 28, 43)
        for beat in range(3):
            sym = chord_at(chords, i * 3 + beat)
            if beat == 0:
                n = cs.root_note(sym, 28, 43) if s.rng.random() < 0.8 else nearest(pcs(sym, CT), prev, 28, 50)
            elif beat == 1:
                tgt = prev + s.rng.choice([-5, -3, 3, 4, 5, 7])
                n = nearest(pcs(sym, CT), tgt, 28, 50)
                if n == prev: n = nearest(pcs(sym, SCALE), prev + 2, 28, 50)
            else:
                if s.rng.random() < 0.6: n = nxt + (1 if prev > nxt else -1)       # chromatic approach
                else: n = nearest(pcs(sym, SCALE), nxt + (2 if prev > nxt else -2), 28, 50)
                if n == prev: n = nxt - 1
            s.add('bass', at + beat, n, vel - (0 if beat == 0 else 9) + s.rng.randint(-4, 4), 0.92, 0.012)
            prev = n

def two_feel(s, chords, start, vel=80):
    for i, bar in enumerate(cs.bars_of({'chords': chords})):
        at = start + i * 3
        s.add('bass', at, cs.root_note(bar[0]), vel, 1.9)
        s.add('bass', at + 2, cs.fifth_note(bar[-1]), vel - 10, 0.9)

def ride(s, start, nbars, ratio, vel=1.0, hat2=True):
    """Jazz-waltz ride: 1, 2, 2-and (swung), 3, with a skip on 3-and every other bar; pedal hat on 2."""
    for i in range(nbars):
        at = start + i * 3
        pat = [(0, 46), (1, 38), (1.5, 30), (2, 42)] + ([(2.5, 28)] if i % 2 else [])
        for b, v in pat:
            s.add('kit', at + sw_pos(b, ratio), 51, (v + s.rng.randint(-4, 4)) * vel, 0.5, 0.006)
        if hat2: s.add('kit', at + 1, 44, 40 * vel, 0.3, 0.004)

def stabs(s, chords, start, vel=42, density=0.7):
    """Short rootless stabs (Red Garland style): a hit on 1 or a push on 1-and/2-and, sometimes on 3."""
    prev = None
    for i, bar in enumerate(cs.bars_of({'chords': chords})):
        at = start + i * 3; half = 3 / len(bar)
        for j, sym in enumerate(bar):
            v = cs.voicing(sym, prev, top_limit=69); prev = v; t0 = at + j * half
            r = s.rng.random()
            hits = [(0, 0.55)] if r < 0.3 else [(0.5, 0.35), (2, 0.4)] if r < 0.6 else [(1.5, 0.35)] if r < 0.85 else [(0, 0.3), (1.5, 0.3)]
            for off, d in hits:
                if off >= half: continue
                if s.rng.random() > density and off: continue
                for k, n in enumerate(v):
                    s.add('piano', t0 + sw_pos(off, s.ratio) + 0.008 * k, n, vel + (4 if off % 1 else 0) + s.rng.randint(-3, 3), d, 0.008)
    return prev

def melody_with_fills(s, theme, chords, start, vel, octave=0, double=False, fills=True):
    """Head melody (EP1 MIDI) plus short fills in the gaps: held notes of 3 beats and the rests."""
    t = start - theme['pickup']; mel = theme['mel']
    for idx, (n, b) in enumerate(mel):
        if n != '-':
            nn = cs.m(n) + 12 * octave
            off = sw_pos(t, s.ratio) - t
            s.add('piano', t + off, nn, vel + (5 if b >= 2 else 0) + s.rng.randint(-4, 4), b * 0.93)
            if double: s.add('piano', t + off, nn - 12, vel - 16, b * 0.88)
        gap_end = t + b
        if fills and ((n != '-' and b >= 3) or n == '-') and gap_end - t >= 2:
            fs = t + (1.0 if n != '-' else 0.0)
            nxt = [x for x in mel[idx + 1:] if x[0] != '-']
            fe = gap_end - (0.0 if nxt else 0.5)
            if fe - fs >= 1.0 and s.rng.random() < 0.85:
                fill(s, chords, fs, fe - 0.1, start, vel - 14, (cs.m(n) + 12 * octave) if n != '-' else 79)
        t += b
    return t

def fill(s, chords, fs, fe, origin, vel, from_note):
    """Fill between phrases: chord relative to the chorus start, notes stay above the comping."""
    n = from_note; x = fs; d = s.rng.choice([-1, 1])
    while x < fe - 0.3:
        sym = chord_at(chords, x - origin)
        sc = sorted(p for p in range(67, 89) if p % 12 in pcs(sym, SCALE))
        up = [p for p in sc if p > n]; dn = [p for p in sc if p < n]
        n = up[0] if d > 0 and up else dn[-1] if dn else n
        if n >= 86: d = -1
        if n <= 69: d = 1
        if s.rng.random() < 0.25: d = -d
        last = x + 0.5 >= fe - 0.3
        s.add('piano', sw_pos(x, s.ratio), n, vel + (5 if x % 1 else 0) + s.rng.randint(-4, 4), (fe - x) * 0.9 if last else 0.4, 0.01)
        x += 0.5

def solo_chorus(s, chords, start, vel=60):
    """One chorus of right-hand solo: 2-bar phrases of eighths with breaths, sometimes a triplet pickup."""
    L = len(chords) * 3; x = 0; note = 76
    while x < L - 1:
        phr = s.rng.choice([3.5, 4.5, 5, 6]); rest = s.rng.choice([1, 1.5, 2])
        end = min(L - 0.5, x + phr)
        if s.rng.random() < 0.3 and x + 1 < end:            # triplet pickup into the phrase
            sym = chord_at(chords, x)
            tgt = nearest(pcs(sym, CT), note, 66, 84)
            for k, nn in enumerate((tgt - 2, tgt - 1, tgt)):
                s.add('piano', start + x + k / 3, nn, vel - 4 + s.rng.randint(-3, 3), 0.3, 0.006)
            x += 1
        note = _line_rel(s, chords, start, x, end, vel, note)
        x = end + rest

def _line_rel(s, chords, origin, x0, x1, vel, note):
    """Swung eighth line from x0 to x1 (beats from the chorus start): chord tones on the beat,
    scale steps between, occasional chromatic passing tone; the last note is held."""
    n = note; x = x0; d = s.rng.choice([-1, 1])
    while x < x1 - 0.4:
        sym = chord_at(chords, x)
        on_beat = abs(x % 1) < 1e-6
        if on_beat:
            n = nearest(pcs(sym, CT), n + d * 2, 64, 86)
        else:
            sc = sorted(p for p in range(64, 87) if p % 12 in pcs(sym, SCALE))
            up = [p for p in sc if p > n]; dn = [p for p in sc if p < n]
            n = up[0] if d > 0 and up else dn[-1] if dn else n
            if s.rng.random() < 0.12: n -= 1
        if n >= 83: d = -1
        if n <= 66: d = 1
        if s.rng.random() < 0.2: d = -d
        last = x + 0.5 >= x1 - 0.4
        s.add('piano', origin + sw_pos(x, s.ratio), n, vel + (6 if not on_beat else 0) + s.rng.randint(-5, 5),
              (x1 - x) * 0.9 if last else 0.42, 0.01)
        x += 0.5
    return n

def ending(s, t):
    # E6/9 (E major, bright tag): low E, rootless E6/9 voicing, a high B on top, ride bell-ish last hit
    s.add('bass', t, cs.m('E1'), 78, 4.5, 0)
    s.add('piano', t, cs.m('E2'), 54, 7.0, 0)
    for k, n in enumerate(['G#3', 'C#4', 'F#4', 'B4', 'E5']): s.add('piano', t + 0.05 * k, cs.m(n), 48, 7.0, 0)
    for k, n in enumerate(['G#5', 'B5', 'C#6', 'F#6']): s.add('piano', t + 0.75 + 0.22 * k, cs.m(n), 44 - 2 * k, 6.0, 0)
    s.add('kit', t, 51, 52, 2.0, 0)

# ------------------------------------------------------------------ arrangement
def arrange(bpm, seed=303):
    s = cs.Song(bpm, 3, seed)
    s.ratio = 0.62 if bpm >= 150 else 0.66            # lighter swing at the faster tempo
    H = cs.HEDWIG; n = len(E_BRIGHT); L = n * 3; t = H['pickup']
    # 1 head: piano + two-feel bass + ride
    stabs(s, E_BRIGHT, t, 40, 0.6); two_feel(s, E_BRIGHT, t, 80); ride(s, t, n, s.ratio, 0.85)
    melody_with_fills(s, H, E_BRIGHT, t, 66); t += L
    # 2 head: full swing, walking bass, melody in octaves
    stabs(s, E_BRIGHT, t, 42); walking(s, E_BRIGHT, t); ride(s, t, n, s.ratio)
    melody_with_fills(s, H, E_BRIGHT, t, 70, double=True); t += L
    # 3 piano solo over the changes
    stabs(s, E_BRIGHT, t, 38, 0.8); walking(s, E_BRIGHT, t); ride(s, t, n, s.ratio, 1.05)
    solo_chorus(s, E_BRIGHT, t, 62); t += L
    if bpm >= 150:   # at 160 the chorus is only 18 s: a second solo chorus keeps the preview ~90 s
        stabs(s, E_BRIGHT, t, 40, 0.8); walking(s, E_BRIGHT, t); ride(s, t, n, s.ratio, 1.05)
        solo_chorus(s, E_BRIGHT, t, 64); t += L
    # 4 head out in the G-major reharm, melody up an octave, then the E6/9 tag
    stabs(s, G_REHARM, t, 40); walking(s, G_REHARM, t); ride(s, t, n, s.ratio)
    melody_with_fills(s, H, G_REHARM, t, 64, octave=1, fills=False); t += L
    ending(s, t)
    return s

def render(bpm):
    s = arrange(bpm)
    name = f'hedwig_bright_{bpm}_preview'
    d = os.path.join(OUT, 'stems_' + str(bpm)); os.makedirs(d, exist_ok=True)
    parts = sorted(s.ev)
    for p in parts:
        cs.write_midi(s, p, os.path.join(d, p + '.mid'))
        cs.run([cs.SFIZZ, '--sfz', cs.SFZ[p], '--midi', os.path.join(d, p + '.mid'), '--wav', os.path.join(d, p + '.wav'),
                '-s', '48000', '-q', '3', '-p', '256'])
    dur = s.length() * 60 / s.bpm + 3
    gain = dict(cs.GAIN, kit=15)                     # ride a little more present than EP1 for the swing feel
    ins, fc = [], []
    for i, p in enumerate(parts):
        ins += ['-i', os.path.join(d, p + '.wav')]
        fc.append(f'[{i}:a]{cs.FILT[p]},volume={gain[p]}dB[s{i}]')
    ins += ['-i', cs.IR]; k = len(parts)
    fc.append(''.join(f'[s{i}]' for i in range(k)) + f'amix=inputs={k}:normalize=0:duration=longest,atrim=0:{dur:.2f},asplit[dry][send]')
    fc.append('[send]highpass=f=220,lowpass=f=5500[sendf]')
    fc.append(f'[sendf][{k}:a]afir=dry=10:wet=10:length=1,volume=-12dB[wet]')
    fc.append(f'[dry][wet]amix=inputs=2:normalize=0:duration=first,lowpass=f=14000,afade=t=out:st={dur - 3:.2f}:d=3')
    pre = os.path.join(d, 'premaster.wav')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fc), '-ar', '48000', '-c:a', 'pcm_f32le', pre])
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-16:TP=-1.5:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    import json
    js = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
    g = -16.5 - float(js['input_i'])                # loudness first; a soft limiter catches ride/piano transients
    out = os.path.join(OUT, name + '.mp3')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', pre, '-af', f'volume={g:.2f}dB,alimiter=limit=0.82:attack=4:release=60:level=false', '-c:a', 'libmp3lame', '-b:a', '256k', out])
    print(name, f'{dur:.1f}s', 'gain', round(g, 2), flush=True)

if __name__ == '__main__':
    for b in (sys.argv[1:] or ['160', '120']): render(int(b))
