# You, Elsewhere EP3 (Malfoid in the library): two ~10 s style previews of Hedwig's opening phrase, 120 BPM, 3/4,
# melody exactly as written and in ONE register (lead + same-octave bell double, nothing an octave up).
#   hedwig_lofi_citypop_10s.mp3   Rhodes lead + celesta bell, chorus on keys, round sine/saw bass with small slides,
#                                 dusty kick/snare/hat (no ride), light sidechain pump, tape warmth, vinyl crackle, low-pass
#   hedwig_musicbox_piano_10s.mp3 Salamander lead + celesta music-box double, soft low chords, long bright reverb, no drums
# Harmony fix (10/24): every chord under a melody note now contains that note (EP1 had G under G#, F# under F,
# A under A#, which made the tune sound wrong). Melody note list verified against published letter-note sources.
# usage: python compose_10s_previews.py
import os, json, subprocess, importlib.util
import numpy as np
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('lib', os.path.join(HERE, 'compose_library_preview.py'))
lib = importlib.util.module_from_spec(spec); spec.loader.exec_module(lib)
cs, OUT = lib.cs, lib.OUT
D = os.path.join(OUT, 'stems_10s'); os.makedirs(D, exist_ok=True)

cs.QUAL['7b5'] = [4, 6, 10, 0]           # B7b5: D# F A B, holds both melody notes of bar 6
cs.QUAL['maj7#5'] = [4, 8, 11, 14]       # Cmaj7#5: E G# B D, holds the G# of bar 12
# bar:      1      2     3      4     5     6       7     8     9     10    11      12          13          14     15    16
CHORDS = ['Em9', 'Em9', 'Am9', 'B7', 'Em9', 'B7b5', 'Em9', 'Em9', 'Em9', 'Em9', 'Bm9', 'Cmaj7#5', 'Am9|F#7', 'C9', 'Em9', 'Em9']
SECONDS = 11.0                            # pickup + bars 1-6 (to the B of bar 7) + a short tail

# ------------------------------------------------------------------ instruments written here
KIT = r'C:\Users\hw549\Downloads\YTP1\YouElsewhere\ep01_malfoid\trio_sfz\samples\jazzkit'
def rr(key, name, extra=''):
    lines = [f'<group> key={key} {extra}']
    for i in range(8):
        lines.append(f'<region> sample={name}_n{i + 1}.flac lorand={i / 8:.3f} hirand={(i + 1) / 8:.3f}')
    return '\n'.join(lines)
LOFI_KIT = os.path.join(D, 'lofi_kit.sfz')
with open(LOFI_KIT, 'w') as f:
    f.write('// dusty lofi kit from the FL HQ jazz kit samples: kick, snare, rim, closed hat\n'
            f'<control> default_path={KIT}\\\n<global> amp_veltrack=100 ampeg_release=0.4\n'
            + rr(36, 'Kick_1_HQ_Jazz') + '\n' + rr(38, 'Snare_Hit_HQ_Jazz') + '\n'
            + rr(37, 'Snare_Rim_HQ_Jazz') + '\n' + rr(42, 'HH_Closed_HQ_Jazz', 'ampeg_release=0.15') + '\n')
SYNBASS = os.path.join(D, 'round_bass.sfz')
with open(SYNBASS, 'w') as f:
    f.write('// round bass: sine body + a little filtered saw for definition\n'
            '<global> amp_veltrack=60 ampeg_attack=0.004 ampeg_decay=1.4 ampeg_sustain=55 ampeg_release=0.12\n'
            '<region> sample=*sine\n<region> sample=*saw volume=-16 fil_type=lpf_2p cutoff=520 resonance=1\n')
cs.SFZ.update({'lead': cs.SFZ['rhodes'], 'keys': cs.SFZ['rhodes'], 'kick': LOFI_KIT, 'kit': LOFI_KIT, 'rbass': SYNBASS})

# ------------------------------------------------------------------ parts
def chords_low(s, part, start, style, vel, top=64):
    prev = None
    for i, bar in enumerate(cs.bars_of({'chords': CHORDS})):
        at = start + i * 3; half = 3 / len(bar)
        for j, sym in enumerate(bar):
            v = cs.voicing(sym, prev, top_limit=top); prev = v; t0 = at + j * half
            if style == 'pad':
                for k, n in enumerate(v): s.add(part, t0 + 0.02 * k, n, vel, half * 0.98, 0.006)
            else:   # city-pop push: chord on 1 and an anticipation on 2-and
                for k, n in enumerate(v): s.add(part, t0 + 0.01 * k, n, vel, 1.3, 0.006)
                if half == 3:
                    for k, n in enumerate(v): s.add(part, t0 + 1.5 + 0.01 * k, n, vel - 6, 1.3, 0.006)

def round_bass(s, start, vel=92):
    bars = cs.bars_of({'chords': CHORDS})
    for i, bar in enumerate(bars):
        at = start + i * 3
        r = cs.root_note(bar[0], 36, 47)
        if i % 2: s.add('rbass', at - 0.09, r - 2, vel - 30, 0.09, 0)       # small slide up into the root
        s.add('rbass', at, r, vel, 1.7, 0.005)
        s.add('rbass', at + 2, cs.root_note(bar[-1], 36, 47) + (7 if len(bar) == 1 else 0) - (12 if cs.root_note(bar[-1], 36, 47) + 7 > 50 and len(bar) == 1 else 0),
              vel - 10, 0.8, 0.005)

def lofi_drums(s, start, nbars):
    for i in range(nbars):
        at = start + i * 3
        s.add('kick', at, 36, 96, 0.4, 0.004)
        if i % 2: s.add('kick', at + 2.5, 36, 62, 0.3, 0.004)
        s.add('kit', at + 2, 38, 70 + s.rng.randint(-4, 4), 0.4, 0.006)            # backbeat on 3
        s.add('kit', at + 1, 37, 34, 0.2, 0.006)                                     # soft rim on 2
        for k in range(6):
            x = k * 0.5 + (0.04 if k % 2 else 0)                                     # nearly straight hats
            s.add('kit', at + x, 42, (38 if k % 2 == 0 else 26) + s.rng.randint(-4, 4), 0.15, 0.004)

# ------------------------------------------------------------------ audio helpers
def render_parts(s, tag):
    paths = {}
    for p in sorted(s.ev):
        mid = os.path.join(D, f'{tag}_{p}.mid'); wav = os.path.join(D, f'{tag}_{p}.wav')
        cs.write_midi(s, p, mid)
        cs.run([cs.SFIZZ, '--sfz', cs.SFZ[p], '--midi', mid, '--wav', wav, '-s', '48000', '-q', '3', '-p', '256'])
        paths[p] = wav
    return paths

def vinyl(path, seconds, sr=48000, seed=7):
    """Sparse soft crackle + very faint band-limited hiss."""
    rng = np.random.default_rng(seed); n = int(seconds * sr)
    x = np.zeros(n)
    idx = rng.integers(0, n, int(seconds * 22)); x[idx] = rng.exponential(0.05, idx.size) * rng.choice([-1, 1], idx.size)
    k = np.exp(-np.arange(40) / 6.0); x = np.convolve(x, k, 'same')
    x += rng.normal(0, 0.0025, n)
    wavfile.write(path, sr, np.stack([x, np.roll(x, 37)], 1).astype(np.float32))

def bright_ir(path, seconds=3.2, sr=48000, seed=3):
    """Long bright hall: decorrelated decaying noise, gentle high-pass so the low end stays clean."""
    rng = np.random.default_rng(seed); n = int(seconds * sr); t = np.arange(n) / sr
    env = np.exp(-t * 6.9 / seconds) * np.minimum(1, t / 0.012)
    ir = rng.normal(0, 1, (n, 2)) * env[:, None]
    ir = ir - np.convolve(ir[:, 0], np.ones(24) / 24, 'same')[:, None] * 0.6
    ir /= np.abs(ir).max()
    wavfile.write(path, sr, ir.astype(np.float32))

def finish(mix, out, seconds, extra_in=None, extra_mix=''):
    """Tape warmth in its own pass (asoftclip + vibrato in one graph gave NaNs before), then loudness, limiter, fade."""
    pre = mix.replace('.wav', '_pre.wav')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mix, '-af', 'volume=-2dB,asoftclip=type=tanh,volume=2dB', '-c:a', 'pcm_f32le', pre])
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-16:TP=-1.5:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    js = json.loads(r[r.rindex('{'):r.rindex('}') + 1]); g = -16.5 - float(js['input_i'])
    ins = ['-i', pre] + (['-i', extra_in] if extra_in else [])
    head = f'[0:a]volume={g:.2f}dB[m];' + (f'[m][1:a]amix=inputs=2:normalize=0:duration=first{extra_mix}[n];[n]' if extra_in else '[m]')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex',
            head + f'alimiter=limit=0.82:attack=4:release=60:level=false,atrim=0:{seconds},afade=t=out:st={seconds - 1.2}:d=1.2',
            '-c:a', 'libmp3lame', '-b:a', '256k', out])
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', out, '-af', 'astats=measure_perchannel=none', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    assert 'Number of NaNs: 0.0' in r, 'NaN samples in ' + out
    print(os.path.basename(out), 'gain', round(g, 2), flush=True)

# ------------------------------------------------------------------ previews
def citypop():
    s = cs.Song(120, 3, 1010); t = cs.HEDWIG['pickup']; nb = 8
    lib.melody_exact(s, 'lead', t, 74)                         # Rhodes lead, as written
    lib.melody_exact(s, 'celesta', t, 48, octave=0, sustain=1.0)  # bell double in the same octave
    chords_low(s, 'keys', t, 'push', 44); round_bass(s, t); lofi_drums(s, t, nb)
    p = render_parts(s, 'citypop')
    gain = {'lead': 13, 'celesta': 13, 'keys': 12, 'rbass': 2, 'kick': 15, 'kit': 15}
    filt = {'lead': 'highpass=f=120,chorus=0.6:0.9:45:0.35:0.25:2,highshelf=f=5000:g=-2',
            'celesta': 'highpass=f=300,highshelf=f=6000:g=-4',
            'keys': 'highpass=f=150,lowpass=f=5000,chorus=0.6:0.9:50|60:0.4|0.32:0.25|0.4:2|2.3',
            'rbass': 'lowpass=f=900,equalizer=f=110:t=q:w=1:g=2,pan=stereo|c0=c0|c1=c0',
            'kick': 'highpass=f=35,lowpass=f=5000,equalizer=f=70:t=q:w=1:g=3',
            'kit': 'highpass=f=80,lowpass=f=7000,acompressor=threshold=-24dB:ratio=3:attack=10:release=120'}
    order = ['lead', 'celesta', 'keys', 'rbass', 'kick', 'kit']
    ins = sum([['-i', p[k]] for k in order], []) + ['-i', cs.IR]
    fc = [f'[{i}:a]{filt[k]},volume={gain[k]}dB[{k}]' for i, k in enumerate(order)]
    fc.append('[kick]asplit[kickm][key]')
    fc.append('[keys][rbass]amix=inputs=2:normalize=0[pumpin]')
    fc.append('[pumpin][key]sidechaincompress=threshold=0.04:ratio=3:attack=5:release=200:makeup=1[pumped]')
    fc.append('[lead][celesta][pumped][kickm][kit]amix=inputs=5:normalize=0:duration=longest,asplit[dry][send]')
    fc.append('[send]highpass=f=250,lowpass=f=5000[sendf]')
    fc.append('[sendf][6:a]afir=dry=10:wet=10:length=1,volume=-12dB[wet]')
    fc.append('[dry][wet]amix=inputs=2:normalize=0:duration=first,lowpass=f=8500,highshelf=f=6000:g=-2')
    mix = os.path.join(D, 'citypop_mix.wav')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fc), '-ar', '48000', '-c:a', 'pcm_f32le', mix])
    crackle = os.path.join(D, 'vinyl.wav'); vinyl(crackle, SECONDS + 1)
    finish(mix, os.path.join(OUT, 'hedwig_lofi_citypop_10s.mp3'), SECONDS, crackle, '')

def musicbox():
    s = cs.Song(120, 3, 2020); t = cs.HEDWIG['pickup']
    lib.melody_exact(s, 'piano', t, 66, sustain=1.0)
    lib.melody_exact(s, 'celesta', t, 54, octave=0, sustain=1.0)
    chords_low(s, 'piano', t, 'pad', 32, top=62)
    p = render_parts(s, 'musicbox')
    ir = os.path.join(D, 'bright_hall_ir.wav'); bright_ir(ir)
    fc = [f'[0:a]{cs.FILT["piano"].replace("highshelf=f=6000:g=-3", "highshelf=f=6000:g=-1")},volume=16dB[p]',
          '[1:a]highpass=f=300,highshelf=f=6000:g=-3,volume=10dB[c]',
          '[p][c]amix=inputs=2:normalize=0:duration=longest,asplit[dry][send]',
          '[send]highpass=f=300[sendf]',
          '[sendf][2:a]afir=dry=10:wet=10:length=1,volume=-21dB[wet]',
          '[dry][wet]amix=inputs=2:normalize=0:duration=first,lowpass=f=13000']
    mix = os.path.join(D, 'musicbox_mix.wav')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', p['piano'], '-i', p['celesta'], '-i', ir,
            '-filter_complex', ';'.join(fc), '-ar', '48000', '-c:a', 'pcm_f32le', mix])
    finish(mix, os.path.join(OUT, 'hedwig_musicbox_piano_10s.mp3'), SECONDS)

if __name__ == '__main__':
    citypop(); musicbox()
