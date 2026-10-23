# You, Elsewhere EP3 (Malfoid in the library), music step 1b: "library" sound for Hedwig at 120 BPM.
# User feedback 10/23: no ride swing, melody exactly as written (notes and rhythm, straight, no reharm of the
# melody, no octave-up variation), warmer and more present upright bass, original yet calm enough for an
# ambience channel. Variation comes only from instruments and texture:
#   head 1 celesta doubling (soft, an octave up) + piano, no drums; head 2 brushes come in; head 3 walking bass;
#   head 4 drums thin out, soft final chord (no big ending).
# Finish: gentle tape saturation, low-pass ~9.5 kHz, faint pink hiss, tiny wow. Original stereo, nothing hard-panned.
# Reuses compose_suite.py (EP1 renderer + v1 piano chain) and helpers from compose_bright_preview.py.
# usage: python compose_library_preview.py
import os, json, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('bright', os.path.join(HERE, 'compose_bright_preview.py'))
br = importlib.util.module_from_spec(spec); spec.loader.exec_module(br)
cs = br.cs
OUT = br.OUT

# EP1 changes, brightened only on the tonic (Em6/9); the melody is never touched
CHORDS = ['Em69', 'Em69', 'Am9', 'B7b9', 'Em69', 'B7b9', 'Em69', 'Em69',
          'Em69', 'Em69', 'Gmaj7', 'Cmaj7', 'Am9', 'B7b9', 'Em69', 'Em69']

def melody_exact(s, part, start, vel, octave=0, sustain=0.95):
    """Hedwig as written in the EP1 MIDI: same notes, same straight rhythm."""
    t = start - cs.HEDWIG['pickup']
    for n, b in cs.HEDWIG['mel']:
        if n != '-':
            s.add(part, t, cs.m(n) + 12 * octave, vel + (4 if b >= 2 else 0) + s.rng.randint(-3, 3), b * sustain, 0.01)
        t += b

def low_comp(s, start, style, vel):
    """Soft, simple voicings kept under the melody (top note <= E4)."""
    prev = None
    for i, bar in enumerate(cs.bars_of({'chords': CHORDS})):
        at = start + i * 3; half = 3 / len(bar)
        for j, sym in enumerate(bar):
            v = cs.voicing(sym, prev, top_limit=64); prev = v; t0 = at + j * half
            if style == 'pad':
                for k, n in enumerate(v): s.add('piano', t0 + 0.03 * k, n, vel, half * 0.97, 0.008)
            else:   # soft waltz: chord on 2 and 3
                for beat in (1, 2):
                    for k, n in enumerate(v): s.add('piano', t0 + beat + 0.01 * k, n, vel - (3 if beat == 2 else 0), 0.8, 0.008)

def bass_two(s, start, vel=86):
    for i, bar in enumerate(cs.bars_of({'chords': CHORDS})):
        at = start + i * 3
        s.add('bass', at, cs.root_note(bar[0]), vel + s.rng.randint(-3, 3), 1.95, 0.008)
        s.add('bass', at + 2, cs.fifth_note(bar[-1]), vel - 8 + s.rng.randint(-3, 3), 0.95, 0.008)

def brushes(s, start, nbars, vel=1.0):
    """Swirly brushes: slow stir across the bar, soft taps on 2 and 3, foot hat on 2. No ride."""
    for i in range(nbars):
        at = start + i * 3
        s.add('stir', at, 60, (70 + s.rng.randint(-5, 5)) * vel, 2.8, 0.008)
        s.add('stir', at + 1, 38, (22 + s.rng.randint(-3, 3)) * vel, 0.3, 0.008)
        s.add('stir', at + 2, 38, (18 + s.rng.randint(-3, 3)) * vel, 0.3, 0.008)
        s.add('stir', at + 1, 44, 34 * vel, 0.3, 0.004)

def arrange(bpm=120, seed=505):
    s = cs.Song(bpm, 3, seed)
    n = len(CHORDS); L = n * 3; t = cs.HEDWIG['pickup']
    # 1 celesta + piano, pads, two-feel bass, no drums
    low_comp(s, t, 'pad', 34); bass_two(s, t, 82)
    melody_exact(s, 'piano', t, 58); melody_exact(s, 'celesta', t, 52, octave=1, sustain=1.0); t += L
    # 2 piano melody, soft waltz comping, brushes come in
    low_comp(s, t, 'waltz', 34); bass_two(s, t); brushes(s, t, n, 0.85)
    melody_exact(s, 'piano', t, 62); t += L
    # 3 walking bass under the same melody
    low_comp(s, t, 'waltz', 34); br.walking(s, CHORDS, t, 86); brushes(s, t, n)
    melody_exact(s, 'piano', t, 62); t += L
    # 4 pads again, brushes thin out over the first half, celesta returns very softly
    low_comp(s, t, 'pad', 33); bass_two(s, t, 80); brushes(s, t, 8, 0.7)
    melody_exact(s, 'piano', t, 58); melody_exact(s, 'celesta', t, 40, octave=1, sustain=1.0); t += L
    # soft close: Em6/9, no accent
    s.add('bass', t, cs.root_note('Em69'), 74, 5.0, 0)
    for k, nn in enumerate(cs.voicing('Em69')): s.add('piano', t + 0.05 * k, nn, 36, 6.0, 0)
    s.add('piano', t + 0.6, cs.m('B5'), 34, 5.0, 0); s.add('celesta', t + 0.6, cs.m('B6'), 30, 4.0, 0)
    return s

GAIN = dict(cs.GAIN, bass=11, celesta=11, stir=20)   # bass ~4 dB more than EP1
FILT = dict(cs.FILT,
    # fuller upright: body around 100-250 Hz, a little finger attack near 900 Hz, no boom below 40 Hz
    bass='pan=mono|c0=0.5*c0+0.5*c1,highpass=f=40,equalizer=f=60:t=q:w=1:g=-1.5,equalizer=f=160:t=q:w=0.9:g=3,'
         'equalizer=f=900:t=q:w=1.2:g=2,lowpass=f=3200,acompressor=threshold=-20dB:ratio=2.5:attack=15:release=180,'
         'pan=stereo|c0=c0|c1=c0',
    celesta='highpass=f=300,highshelf=f=6000:g=-5')

def render():
    s = arrange()
    name = 'hedwig_library_120_preview'
    d = os.path.join(OUT, 'stems_library_120'); os.makedirs(d, exist_ok=True)
    parts = sorted(s.ev)
    for p in parts:
        cs.write_midi(s, p, os.path.join(d, p + '.mid'))
        cs.run([cs.SFIZZ, '--sfz', cs.SFZ[p], '--midi', os.path.join(d, p + '.mid'), '--wav', os.path.join(d, p + '.wav'),
                '-s', '48000', '-q', '3', '-p', '256'])
    dur = s.length() * 60 / s.bpm + 2
    ins, fc = [], []
    for i, p in enumerate(parts):
        ins += ['-i', os.path.join(d, p + '.wav')]
        fc.append(f'[{i}:a]{FILT[p]},volume={GAIN[p]}dB[s{i}]')
    ins += ['-i', cs.IR]; k = len(parts)
    fc.append(''.join(f'[s{i}]' for i in range(k)) + f'amix=inputs={k}:normalize=0:duration=longest,atrim=0:{dur:.2f},asplit[dry][send]')
    fc.append('[send]highpass=f=220,lowpass=f=5500[sendf]')
    fc.append(f'[sendf][{k}:a]afir=dry=10:wet=10:length=1,volume=-11dB[wet]')
    # old-record finish: soft tape saturation, roll-off above ~9.5 kHz, very slight wow
    fc.append('[dry][wet]amix=inputs=2:normalize=0:duration=first,volume=-3dB,asoftclip=type=tanh,volume=3dB,'
              'lowpass=f=9500,highshelf=f=7000:g=-1.5,vibrato=f=0.45:d=0.012')
    pre = os.path.join(d, 'premaster.wav')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fc), '-ar', '48000', '-c:a', 'pcm_f32le', pre])
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-16:TP=-1.5:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    js = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
    g = -16.5 - float(js['input_i'])
    # faint pink hiss (~-50 dB RMS) under everything, band-limited like old tape
    hiss = f'anoisesrc=color=pink:amplitude=0.006:sample_rate=48000:duration={dur:.2f},highpass=f=300,lowpass=f=7000,pan=stereo|c0=c0|c1=c0'
    out = os.path.join(OUT, name + '.mp3')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', pre, '-f', 'lavfi', '-i', hiss, '-filter_complex',
            f'[0:a]volume={g:.2f}dB[m];[m][1:a]amix=inputs=2:normalize=0:duration=first,'
            f'alimiter=limit=0.82:attack=4:release=60:level=false,afade=t=out:st={dur - 5:.2f}:d=5',
            '-c:a', 'libmp3lame', '-b:a', '256k', out])
    print(name, f'{dur:.1f}s', 'gain', round(g, 2), 'parts', parts, flush=True)

if __name__ == '__main__':
    render()
