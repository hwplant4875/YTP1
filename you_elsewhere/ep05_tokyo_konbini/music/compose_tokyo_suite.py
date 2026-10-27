# You, Elsewhere EP5 (Christmas in Tokyo, 2008 - konbini night shift on Christmas Eve): ~29 min carol suite.
# Reuses the EP4 pipeline and verified public-domain melodies (../../ep04_christmas2009/music/compose_christmas_suite.py)
# with EP4's sound rules (exact first chorus, full bass, brushes, no ride, no clashing comp notes). Different from EP4:
# new running order (opens with The First Noel), every carol in a new key, vibraphone instead of celesta,
# 88-104 BPM late-night tempos, and a very quiet konbini room tone under the music.
# Room tone (CC0 recordings from freesound.org, previews in E:\YTP2\YouElsewhere\ep05_tokyo_konbini\amb_src):
#   #338115 SpliceSound "Residential kitchen roomtone, refrigerator" (fridge hum)
#   #776147 soundandmelodies "AMB-Night, Calm, Walla, SnowMelt - Pikk Street, Tallinn" (street outside, behind glass)
#   #438206 craigsmith "Ding-dong Doorbell" (first two-note ding-dong only; generic, not a store jingle)
# usage: python compose_tokyo_suite.py [track ids...]   (no args = all tracks + join)
import os, sys, json, random, subprocess, importlib.util
import numpy as np

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

HERE = os.path.dirname(os.path.abspath(__file__))
ep4 = load('ep4', os.path.join(HERE, '..', '..', 'ep04_christmas2009', 'music', 'compose_christmas_suite.py'))
cs, ep3 = ep4.cs, ep4.ep3

OUT = r'C:\Users\hw549\Downloads\YTP1\YouElsewhere\ep05_tokyo_konbini\music'
ROOT = r'E:\YTP2\YouElsewhere\ep05_tokyo_konbini'
WORK = os.path.join(ROOT, 'suite_tracks')
AMB = os.path.join(ROOT, 'amb_src')
VIBES = r'C:\Users\hw549\Downloads\YTP1\_samples\VirtualPlayingOrchestra\Virtual-Playing-Orchestra3\Percussion\vibraphone-open.sfz'

def retune(th, semis):
    t = cs.transpose(th, semis)
    t['mel'] = [(None if p is None else p + semis, d) for p, d in th['mel']]
    return t

T = ep4.THEMES
THEMES = {
    'first_noel': retune(T['first_noel'], -2),            # F -> Eb
    'jingle_bells': retune(T['jingle_bells'], -1),        # Bb -> A
    'away_in_a_manger': retune(T['away_in_a_manger'], -2),  # Bb -> Ab
    'god_rest_ye': retune(T['god_rest_ye'], -2),          # Gm -> Fm
    'silent_night': retune(T['silent_night'], -1),        # F -> E
    'deck_the_halls': retune(T['deck_the_halls'], 2),     # F -> G
    'o_holy_night': retune(T['o_holy_night'], 1),         # D -> Eb
    'jolly_old_saint_nicholas': retune(T['jolly_old_saint_nicholas'], -2),  # C -> Bb
    'hark': retune(T['hark'], 2),                         # Ab -> Bb
    'o_christmas_tree': retune(T['o_christmas_tree'], -1),  # Bb -> A
    'good_king_wenceslas': retune(T['good_king_wenceslas'], 1),  # A -> Bb
    'carol_of_the_bells': retune(T['carol_of_the_bells'], 2),    # Gm -> Am
    'angels_we_have_heard': retune(T['angels_we_have_heard'], 1),  # G -> Ab
    'we_wish_you': retune(T['we_wish_you'], 2),           # C -> D
}

TRACKS = {   # id: (title, theme, bpm, seed, vibraphone on first chorus, sleigh bells)
    '01_the_first_noel': ('The First Noel', 'first_noel', 92, 12, True, False),
    '02_jingle_bells': ('Jingle Bells', 'jingle_bells', 104, 22, False, True),
    '03_away_in_a_manger': ('Away in a Manger', 'away_in_a_manger', 90, 32, True, False),
    '04_god_rest_ye': ('God Rest Ye Merry, Gentlemen', 'god_rest_ye', 98, 42, False, False),
    '05_silent_night': ('Silent Night', 'silent_night', 88, 52, True, False),
    '06_deck_the_halls': ('Deck the Halls', 'deck_the_halls', 102, 62, False, False),
    '07_o_holy_night': ('O Holy Night', 'o_holy_night', 88, 72, False, False),
    '08_jolly_old_saint_nicholas': ('Jolly Old Saint Nicholas', 'jolly_old_saint_nicholas', 100, 82, False, True),
    '09_hark': ('Hark! The Herald Angels Sing', 'hark', 96, 92, False, False),
    '10_o_christmas_tree': ('O Christmas Tree', 'o_christmas_tree', 94, 102, True, False),
    '11_good_king_wenceslas': ('Good King Wenceslas', 'good_king_wenceslas', 100, 112, False, False),
    '12_carol_of_the_bells': ('Carol of the Bells', 'carol_of_the_bells', 104, 122, False, False),
    '13_angels_we_have_heard': ('Angels We Have Heard on High', 'angels_we_have_heard', 92, 132, True, False),
    '14_we_wish_you': ('We Wish You a Merry Christmas', 'we_wish_you', 96, 142, False, False),
}

def melody(s, start, vel, grace=0.0, celesta=False):
    """EP4 melody, but the first-chorus doubling is a soft vibraphone in the same register."""
    th = s.theme; t = start - th['pickup']
    for n, b in th['mel']:
        if n is not None:
            v = vel + (4 if b >= 2 else 0) + s.rng.randint(-3, 3)
            if grace and b >= 2 and s.rng.random() < grace:
                s.add('piano', t - 0.12, n - 1, v - 14, 0.12, 0.0)
            s.lead(t, n, v, b * 0.95)
            if celesta: s.add('vibes', t, n, v - 14, b * 0.9, 0.006)
        t += b

# point the EP4 engine at this episode
ep4.melody = melody
ep4.THEMES, ep4.TRACKS, ep4.WORK = THEMES, TRACKS, WORK
ep4.TARGET = 130
ep4.SLEIGH_SFZ = os.path.join(WORK, 'sleigh.sfz')
ep4.SFZ = dict(ep4.SFZ, sleigh=ep4.SLEIGH_SFZ, vibes=VIBES)
ep4.GAIN = dict(ep4.GAIN, vibes=-8)
ep4.FILT = dict(ep4.FILT, vibes='highpass=f=180,highshelf=f=6000:g=-4,acompressor=threshold=-24dB:ratio=2:attack=3:release=120')

# ------------------------------------------------------------------ konbini room tone
SR = 48000

def read(path):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()

def loop_to(x, n, xf=3.0):
    """Repeat x with equal-power crossfades until n samples."""
    k = int(xf * SR); fade = np.sin(np.linspace(0, np.pi / 2, k))[:, None]
    out = x.copy()
    while len(out) < n:
        out = np.concatenate([out[:-k], out[-k:] * fade[::-1] + x[:k] * fade, x[k:]])
    return out[:n]

def lufs_of(x):
    tmp = os.path.join(ROOT, '_tmp_lufs.wav'); write(tmp, x); return ep3.lufs(tmp)

def write(path, x):
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_f32le', path],
                         stdin=subprocess.PIPE)
    p.communicate(x.astype(np.float32).tobytes())

def room_tone(seconds):
    n = int(seconds * SR); rng = random.Random(2008)
    fridge = loop_to(read(os.path.join(AMB, '338115.mp3')), n)
    street = loop_to(read(os.path.join(AMB, '776147.mp3'))[int(5 * SR):], n)
    fridge *= 10 ** ((-46 - lufs_of(fridge[:SR * 60])) / 20)       # steady hum
    street *= 10 ** ((-50 - lufs_of(street[:SR * 120])) / 20)      # faint street behind the glass
    write(os.path.join(ROOT, '_street.wav'), street)
    street = read_filtered(os.path.join(ROOT, '_street.wav'), 'lowpass=f=2500,highpass=f=80')
    chime = read(os.path.join(AMB, '438206.mp3'))[int(0.15 * SR):int(2.2 * SR)]
    k = int(0.3 * SR); chime[-k:] *= np.linspace(1, 0, k)[:, None]
    chime *= 10 ** (-34 / 20) / np.abs(chime).max()                  # chime peaks at -34 dBFS before the room gain
    amb = fridge + street[:n]
    t = rng.uniform(70, 140)
    while t < seconds - 60:                                           # a customer every few minutes
        i = int(t * SR); amb[i:i + len(chime)] += chime * rng.uniform(0.7, 1.0)
        t += rng.uniform(150, 260)
    return amb

def read_filtered(path, af):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-af', af, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()

# ------------------------------------------------------------------ join
def join():
    ids = list(TRACKS); files = [os.path.join(WORK, t + '.wav') for t in ids]
    ins = sum([['-i', f] for f in files], [])
    fc = [f'[{i}:a]volume={-20 - ep3.lufs(f):.2f}dB[n{i}]' for i, f in enumerate(files)]
    cur = '[n0]'
    for i in range(1, len(files)):
        fc.append(f'{cur}[n{i}]acrossfade=d=4:c1=tri:c2=tri[x{i}]'); cur = f'[x{i}]'
    music = os.path.join(WORK, 'suite_music.wav')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fc), '-map', cur, '-c:a', 'pcm_f32le', music])
    amb_path = os.path.join(ROOT, 'konbini_room_tone.wav')
    write(amb_path, room_tone(ep3.duration(music)))
    pre = os.path.join(WORK, 'suite_premaster.wav')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', music, '-i', amb_path, '-filter_complex',
            '[1:a]afade=t=in:d=3[a];[0:a][a]amix=inputs=2:normalize=0:duration=first',
            '-c:a', 'pcm_f32le', pre])
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-17:TP=-1.5:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    js = json.loads(r[r.rindex('{'):r.rindex('}') + 1]); g = -17 - float(js['input_i'])
    base = os.path.join(OUT, 'you_elsewhere_ep05_tokyo_suite')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', pre, '-af', f'volume={g:.2f}dB,alimiter=limit=0.84:attack=4:release=60:level=false',
            '-ar', '48000', '-c:a', 'pcm_s24le', base + '.wav'])
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', base + '.wav', '-c:a', 'libmp3lame', '-b:a', '256k', base + '.mp3'])
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', base + '.wav', '-t', '90', '-af', 'afade=t=out:st=86:d=4',
            '-c:a', 'libmp3lame', '-b:a', '256k', os.path.join(OUT, 'you_elsewhere_ep05_tokyo_first90s.mp3')])
    t = 0.0; lines = []
    for tid, f in zip(ids, files):
        title, key, *_ = TRACKS[tid]
        mm, ss = divmod(int(round(t)), 60)
        lines.append(f'{mm}:{ss:02d} {title} ({ep4.CREDIT[key]})')
        t += ep3.duration(f) - 4
    total = ep3.duration(base + '.wav')
    with open(os.path.join(OUT, 'tracklist.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + f'\n\n(total {int(total // 60)}:{int(total % 60):02d})\n'
                 'All melodies public domain; arrangements and recordings original.\n'
                 'Room tone: CC0 recordings from freesound.org (#338115 SpliceSound, #776147 soundandmelodies, #438206 craigsmith).\n')
    print('\n'.join(lines)); print('total', round(total, 1), 's, gain', round(g, 2))

if __name__ == '__main__':
    os.makedirs(WORK, exist_ok=True); os.makedirs(OUT, exist_ok=True); ep4.write_sleigh()
    todo = sys.argv[1:] or list(TRACKS)
    for tid in todo: ep4.build(tid)
    if not sys.argv[1:]: join()
