# You, Elsewhere EP1: ~30 min late-night jazz suite (Hedwig variations + original themes in the same mood).
# Writes per-instrument MIDI for every track, renders them with sfizz_render, mixes each track with ffmpeg
# (v1 piano chain: warm EQ, highs eased above 6 kHz, FL "Chamber Warm" convolution send), then crossfades
# all tracks into one long file.
# usage: python compose_suite.py [track_ids...]   (no args = all tracks + final join)
import mido, random, subprocess, os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = r'C:\Users\hw549\Downloads\YTP1\_samples'
SFIZZ = r'C:\Users\hw549\Downloads\YTP1\_downloads\sfizz\x\bin\Release\sfizz_render.exe'
IR = r'C:\Users\hw549\Downloads\YTP1\YouElsewhere\ep01_malfoid\trio_sfz\ir_chamber_warm.wav'
SFZ = {
    'piano': SAMPLES + r'\SalamanderGrandPiano-SFZ+FLAC-V3+20200602\SalamanderGrandPiano-V3+20200602.sfz',
    'bass': SAMPLES + r'\dsmolken.double-bass-master\d_smolken_rubner_bass_pizz.sfz',
    'kit': SAMPLES + r'\karoryfer.swirly-drums-main\Programs\Full_kit.sfz',
    'stir': SAMPLES + r'\karoryfer.swirly-drums-main\Programs\Full_kit.sfz',
    'rhodes': SAMPLES + r'\jlearman.jRhodes3c-master\jRhodes3c-looped-flac-sfz\_jRhodes-stereo-looped.sfz',
    'celesta': SAMPLES + r'\VirtualPlayingOrchestra\Virtual-Playing-Orchestra3\Keys\celesta.sfz',
    'harp': SAMPLES + r'\VSCO-2-CE-master\Harp.sfz',
    'cello': SAMPLES + r'\VSCO-2-CE-master\CelloEnsSusVib-Quiet.sfz',
}
TPB = 480
NAMES = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7,
         'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}

def m(s):
    return 12 * (int(s[-1]) + 1) + NAMES[s[:-1]]

# ------------------------------------------------------------------ harmony
QUAL = {  # intervals above the root; first entry of each list is used for rootless voicings
    'maj7': [4, 7, 11, 14], 'maj9': [4, 7, 11, 14], 'maj7#11': [4, 11, 14, 18], '6': [4, 7, 9, 14],
    'm9': [3, 7, 10, 14], 'm7': [3, 7, 10, 14], 'm6': [3, 7, 9, 14], 'm7b5': [3, 6, 10, 0],
    '7': [4, 10, 14, 7], '7b9': [4, 10, 13, 7], '9': [4, 10, 14, 7], '13': [4, 10, 14, 21],
    '7sus': [5, 10, 14, 0], 'm': [3, 7, 10, 14], '': [4, 7, 11, 14],
}

def parse(sym):
    root = sym[:2] if len(sym) > 1 and sym[1] in '#b' else sym[:1]
    q = sym[len(root):]
    return NAMES[root], (q if q in QUAL else 'm9' if q.startswith('m') else '7')

def voicing(sym, prev=None, top_limit=None):
    """Four-note rootless voicing around C4, chosen for the smallest movement from the previous one."""
    r, q = parse(sym)
    pcs = [(r + i) % 12 for i in QUAL[q]]
    best, best_cost = None, 1e9
    for base in range(46, 62):
        v, cur = [], base
        for k in range(4):
            pc = pcs[k]
            n = cur + ((pc - cur) % 12)
            v.append(n); cur = n + 1
        v = sorted(v)
        span_ok = v[-1] <= (top_limit or 72) and v[0] >= 47
        cost = sum(abs(a - b) for a, b in zip(v, prev)) if prev else abs(sum(v) / 4 - 60)
        cost += 0 if span_ok else 100 + abs(v[-1] - 70)      # out-of-range voicings only as a last resort
        if cost < best_cost: best, best_cost = v, cost
    return best

def root_note(sym, low=28, high=43):
    r, _ = parse(sym)
    n = low + ((r - low) % 12)
    return n if n <= high else n - 12

def fifth_note(sym):
    r, q = parse(sym)
    n = root_note(sym) + (6 if 'b5' in q else 7)
    return n if n <= 47 else n - 12

# ------------------------------------------------------------------ themes
# melody: (note or '-', beats); chords: one symbol per bar, 'A|B' splits the bar in half
HEDWIG = dict(
    meter=3, pickup=1,
    mel=[('B4', 1), ('E5', 1.5), ('G5', .5), ('F#5', 1), ('E5', 2), ('B5', 1), ('A5', 3), ('F#5', 3), ('E5', 1.5), ('G5', .5),
         ('F#5', 1), ('D#5', 2), ('F5', 1), ('B4', 3), ('-', 2), ('B4', 1), ('E5', 1.5), ('G5', .5), ('F#5', 1), ('E5', 2), ('B5', 1),
         ('D6', 2), ('C#6', 1), ('C6', 2), ('G#5', 1), ('C6', 1.5), ('B5', .5), ('A#5', 1), ('A#4', 2), ('G5', 1), ('E5', 3)],
    chords=['Em9', 'Em9', 'Am9', 'B7b9', 'Em9', 'B7b9', 'Em9', 'Em9', 'Em9', 'Em9', 'Gmaj7', 'Cmaj7', 'Am9', 'B7b9', 'Em9', 'Em9'])

COMMON_ROOM = dict(
    meter=3, pickup=0,
    mel=[('A4', 2), ('F4', 1), ('Bb4', 1.5), ('A4', .5), ('G4', 1), ('E4', 2), ('G4', 1), ('A4', 3),
         ('D5', 2), ('C5', 1), ('Bb4', 1.5), ('A4', .5), ('G4', 1), ('C#5', 2), ('E5', 1), ('D5', 3),
         ('F5', 2), ('E5', 1), ('D5', 1.5), ('C5', .5), ('Bb4', 1), ('Bb4', 2), ('A4', 1), ('A4', 2), ('C5', 1),
         ('F5', 1.5), ('E5', .5), ('D5', 1), ('G4', 1.5), ('A4', .5), ('C#5', 1), ('D5', 3), ('-', 3)],
    chords=['Dm9', 'Gm9', 'C7', 'Fmaj7', 'Bbmaj7', 'Em7b5', 'A7b9', 'Dm9',
            'Dm9', 'Gm9', 'C7', 'Fmaj7', 'Bbmaj7', 'Em7b5|A7b9', 'Dm9', 'Dm9'])

LAKE_WINDOW = dict(
    meter=4, pickup=0,
    mel=[('E5', 2), ('D5', 1), ('C5', 1), ('D5', 1.5), ('C5', .5), ('Bb4', 1), ('A4', 1), ('A4', 3), ('E4', 1),
         ('G4', 1.5), ('Bb4', .5), ('Eb5', 1), ('D5', 1), ('D5', 3), ('F5', 1), ('F5', 1.5), ('Db5', .5), ('C5', 1), ('Bb4', 1),
         ('C5', 2), ('Eb5', 1), ('D5', 1), ('Bb4', 2), ('A4', 1), ('G4', 1),
         ('E5', 2), ('F5', 1), ('G5', 1), ('G5', 1.5), ('F5', .5), ('E5', 1), ('C#5', 1), ('F5', 2), ('E5', 1), ('D5', 1),
         ('Eb5', 1.5), ('D5', .5), ('C5', 1), ('A4', 1), ('D5', 2), ('C5', 1), ('A4', 1), ('Db5', 2), ('C5', 1), ('Bb4', 1),
         ('A4', 1.5), ('G4', .5), ('Bb4', 1), ('E4', 1), ('F4', 4)],
    chords=['Fmaj9', 'Em7b5|A7b9', 'Dm9', 'Cm7|F7', 'Bbmaj7', 'Bbm6|Eb9', 'Am7|D7b9', 'Gm9|C7',
            'Fmaj9', 'Em7b5|A7b9', 'Dm9', 'Cm7|F7', 'Bbmaj7', 'Bbm6|Eb9', 'Gm9|C7', 'Fmaj9'])

GREEN_SCARF = dict(
    meter=3, pickup=0,
    mel=[('D5', 1), ('Bb4', 1), ('A4', 1), ('G4', 2), ('D4', 1), ('Eb4', 1), ('G4', 1), ('Bb4', 1), ('A4', 2), ('F4', 1),
         ('D5', 1), ('C5', 1), ('D5', 1), ('G5', 2), ('F5', 1), ('Eb5', 1.5), ('D5', .5), ('C5', 1), ('F#4', 3),
         ('D5', 1), ('Bb4', 1), ('A4', 1), ('G4', 1), ('A4', 1), ('Bb4', 1), ('C5', 1), ('D5', 1), ('Eb5', 1), ('F5', 2), ('Eb5', 1),
         ('D5', 1.5), ('C5', .5), ('Bb4', 1), ('G4', 2), ('Bb4', 1), ('A4', 1.5), ('C5', .5), ('F#4', 1), ('G4', 3)],
    chords=['Gm9', 'Gm9', 'Cm9', 'F7', 'Bbmaj7', 'Ebmaj7', 'Am7b5', 'D7b9',
            'Gm9', 'Gm9', 'Cm9', 'F7', 'Bbmaj7', 'Ebmaj7', 'Am7b5|D7b9', 'Gm9'])

FIRESIDE = dict(
    meter=4, pickup=0,
    mel=[('E5', 2), ('B4', 1), ('C5', 1), ('A4', 3), ('G4', 1), ('F4', 1.5), ('E4', .5), ('F4', 1), ('A4', 1), ('B4', 2), ('G#4', 2),
         ('E5', 2), ('B4', 1), ('C5', 1), ('B4', 3), ('A4', 1), ('D5', 1.5), ('C5', .5), ('A4', 1), ('F4', 1), ('G#4', 4),
         ('G5', 2), ('E5', 1), ('D5', 1), ('E5', 2), ('D5', 1), ('B4', 1), ('C5', 2), ('A4', 1), ('C5', 1), ('B4', 1.5), ('A4', .5), ('G4', 1), ('C#5', 1),
         ('E5', 2), ('D5', 1), ('A4', 1), ('B4', 2), ('F5', 1), ('D5', 1), ('E5', 3), ('B4', 1), ('D5', 2), ('G#4', 2), ('A4', 4)],
    chords=['Am9', 'Fmaj7', 'Dm9', 'E7sus|E7', 'Am9', 'Fmaj7#11', 'Bm7b5', 'E7b9',
            'Cmaj7', 'G6', 'Fmaj7', 'Em7|A7', 'Dm9', 'G7', 'Cmaj7', 'Bm7b5|E7b9', 'Am9'])

RAIN = dict(
    meter=4, pickup=0,
    mel=[('G4', .5), ('Eb5', 1), ('D5', .5), ('C5', 1), ('D5', 1), ('Bb4', 3), ('-', 1), ('Ab4', .5), ('F5', 1), ('Eb5', .5), ('C5', 1), ('Eb5', 1), ('D5', 3), ('-', 1),
         ('G5', .5), ('F5', 1), ('D5', .5), ('Bb4', 1), ('F5', 1), ('Eb5', 3), ('-', 1), ('F5', 1), ('Ab4', 1), ('C5', 1), ('Eb5', 1), ('D5', 2), ('B4', 2),
         ('G4', .5), ('Eb5', 1), ('D5', .5), ('C5', 1), ('D5', 1), ('Bb4', 1.5), ('C5', .5), ('D5', 1), ('Eb5', 1), ('F5', 2), ('Ab5', 1), ('G5', 1), ('F5', 3), ('-', 1),
         ('G5', 1.5), ('F5', .5), ('Eb5', 1), ('D5', 1), ('C5', 3), ('Eb5', 1), ('D5', 1.5), ('F5', .5), ('B4', 2), ('C5', 4)],
    chords=['Cm9', 'Cm9', 'Fm9', 'Bb13', 'Ebmaj9', 'Abmaj7', 'Dm7b5', 'G7b9',
            'Cm9', 'Cm9', 'Fm9', 'Bb13', 'Ebmaj9', 'Abmaj7', 'Dm7b5|G7b9', 'Cm9'])

# ------------------------------------------------------------------ performance
class Song:
    def __init__(self, bpm, meter, seed):
        self.bpm, self.meter = bpm, meter
        self.ev = {}               # part -> list of (beat, note, vel, dur_beats)
        self.cc = {}               # part -> list of (beat, cc, value)
        self.rng = random.Random(seed)
    def add(self, part, beat, note, vel, dur, jitter=0.02):
        b = max(0.0, beat + self.rng.gauss(0, jitter))
        self.ev.setdefault(part, []).append((b, int(note), int(max(1, min(127, vel))), max(0.05, dur)))
    def length(self):
        return max(b + d for evs in self.ev.values() for b, _, _, d in evs)

def bars_of(theme):
    out = []
    for c in theme['chords']:
        out.append(c.split('|'))
    return out

def play_melody(s, part, theme, start, vel, octave=0, double=False, embellish=0.0, sustain=0.95):
    t = start - theme['pickup']
    for n, b in theme['mel']:
        if n != '-':
            nn = m(n) + 12 * octave
            sw = 0.14 if abs((t % 1) - 0.5) < 1e-6 else 0
            v = vel + (5 if b >= 2 else 0) + s.rng.randint(-4, 4)
            if embellish and b >= 2 and s.rng.random() < embellish:
                # grace-note turn into long notes: upper neighbour then the note
                s.add(part, t + sw, nn + 2, v - 12, 0.25); s.add(part, t + sw + 0.25, nn, v, b * sustain - 0.25)
            else:
                s.add(part, t + sw, nn, v, b * sustain)
            if double: s.add(part, t + sw, nn - 12, v - 18, b * sustain * 0.9)
        t += b
    return t

def comp(s, part, theme, start, style, vel=38, prev=None):
    meter = s.meter
    for i, bar in enumerate(bars_of(theme)):
        at = start + i * meter
        half = meter / len(bar)
        for j, sym in enumerate(bar):
            t0 = at + j * half
            v = voicing(sym, prev); prev = v
            if style == 'pad':
                for k, n in enumerate(v): s.add(part, t0 + 0.03 * k, n, vel, half * 0.95)
            elif style == 'waltz':
                for beat in (1, 2):
                    if t0 + beat < at + meter and (len(bar) == 1 or beat < half + 0.01):
                        for n in v: s.add(part, t0 + beat, n, vel if beat == 1 else vel - 5, 0.7)
                if len(bar) > 1 and j == 1:
                    for n in v: s.add(part, t0, n, vel, half * 0.9)
            elif style == 'arp':          # broken chord in eighths, left hand
                r = root_note(sym, 36, 48)
                pat = [r, r + 7, v[1], v[2], v[3], v[2], v[1], r + 7][:int(half * 2)]
                for k, n in enumerate(pat): s.add(part, t0 + 0.5 * k, n, vel - (0 if k == 0 else 6), 1.4)
            elif style == 'ballad':       # half-note chords with a soft root
                s.add(part, t0, root_note(sym, 36, 48), vel + 2, half * 0.95)
                for k, n in enumerate(v): s.add(part, t0 + 0.04 + 0.02 * k, n, vel - 4, half * 0.92)
            elif style == 'bossa':
                for off, dur in ((0, 1.4), (1.5, 0.9), (3, 0.9)):
                    if off < half:
                        for n in v: s.add(part, t0 + off, n, vel - (4 if off else 0), dur)
    return prev

def bassline(s, part, theme, start, style, vel=80):
    meter = s.meter
    bars = bars_of(theme)
    for i, bar in enumerate(bars):
        at = start + i * meter
        nxt = root_note(bars[(i + 1) % len(bars)][0])
        half = meter / len(bar)
        for j, sym in enumerate(bar):
            t0 = at + j * half; r, f = root_note(sym), fifth_note(sym)
            if style == 'two':
                if meter == 3 and len(bar) == 1: s.add(part, t0, r, vel, 1.9); s.add(part, t0 + 2, f, vel - 10, 0.9)
                else: s.add(part, t0, r, vel, half * 0.9)
            elif style == 'walk':
                steps = int(half)
                notes = [r, f, r + 12 if r + 12 <= 50 else f - 5, nxt + (1 if s.rng.random() < .5 else -1)]
                notes = notes[:steps - 1] + [nxt + (1 if s.rng.random() < .5 else -1)] if steps > 1 else [r]
                for k, n in enumerate(notes): s.add(part, t0 + k, n, vel - (0 if k == 0 else 8), 0.95)
            elif style == 'bossa':
                s.add(part, t0, r, vel, 1.4); s.add(part, t0 + 1.5, f, vel - 8, 0.45)
                if half > 2: s.add(part, t0 + 2, f, vel - 6, 1.4); s.add(part, t0 + 3.5, r, vel - 10, 0.45)
            elif style == 'pedal':
                s.add(part, t0, r, vel - 6, half * 0.95)

def brushes(s, start, nbars, style, vel=1.0):
    meter = s.meter
    for i in range(nbars):
        at = start + i * meter
        for beat in range(meter):
            # slow brush stir every beat (long swell), foot hat on 2 (waltz) or 2 and 4
            s.add('stir', at + beat, 60 if beat % 2 == 0 else 64, 88 * vel + s.rng.randint(-6, 6), 1.6, 0.01)
        if style == 'waltz':
            s.add('kit', at + 1, 44, 34 * vel, 0.3); s.add('kit', at, 51, 34 * vel, 0.5); s.add('kit', at + 2, 51, 28 * vel, 0.5)
        elif style == 'ballad':
            s.add('kit', at + 1, 44, 30 * vel, 0.3); s.add('kit', at + 3, 44, 30 * vel, 0.3)
        elif style == 'bossa':
            for k in range(8):
                s.add('kit', at + 0.5 * k, 42 if k % 2 else 44, (30 if k % 2 else 26) * vel, 0.2)

# ------------------------------------------------------------------ arrangements (one function per track)
def trio_waltz(theme, bpm, seed, vel_shift=0):
    s = Song(bpm, 3, seed); L = len(theme['chords']) * 3; t = theme['pickup']
    # head 1: piano alone, pads under the melody
    comp(s, 'piano', theme, t, 'pad', 36 + vel_shift); play_melody(s, 'piano', theme, t, 62 + vel_shift); t += L
    # head 2: full trio
    comp(s, 'piano', theme, t, 'waltz', 38 + vel_shift); bassline(s, 'bass', theme, t, 'two'); brushes(s, t, len(theme['chords']), 'waltz')
    play_melody(s, 'piano', theme, t, 66 + vel_shift, double=True); t += L
    # head 3: variation, melody an octave up and decorated, walking bass
    comp(s, 'piano', theme, t, 'waltz', 36 + vel_shift); bassline(s, 'bass', theme, t, 'walk'); brushes(s, t, len(theme['chords']), 'waltz')
    play_melody(s, 'piano', theme, t, 60 + vel_shift, octave=1, embellish=0.5); t += L
    # head 4: back to pads, quieter, drums out
    comp(s, 'piano', theme, t, 'pad', 33 + vel_shift); bassline(s, 'bass', theme, t, 'pedal', 70); play_melody(s, 'piano', theme, t, 56 + vel_shift); t += L
    final(s, theme, t)
    return s

def solo_ballad(theme, bpm, seed, octave_last=True):
    s = Song(bpm, theme['meter'], seed); L = len(theme['chords']) * theme['meter']; t = theme['pickup']
    comp(s, 'piano', theme, t, 'arp', 40); play_melody(s, 'piano', theme, t, 60); t += L
    comp(s, 'piano', theme, t, 'ballad', 36); play_melody(s, 'piano', theme, t, 58, octave=1 if octave_last else 0, embellish=0.4, double=octave_last); t += L
    comp(s, 'piano', theme, t, 'arp', 34); play_melody(s, 'piano', theme, t, 54); t += L
    final(s, theme, t)
    return s

def rhodes_ballad(theme, bpm, seed):
    s = Song(bpm, theme['meter'], seed); L = len(theme['chords']) * theme['meter']; n = len(theme['chords']); t = 0
    comp(s, 'rhodes', theme, t, 'ballad', 44); play_melody(s, 'rhodes', theme, t, 70); bassline(s, 'bass', theme, t, 'pedal', 72); t += L
    comp(s, 'rhodes', theme, t, 'ballad', 42); play_melody(s, 'piano', theme, t, 60, octave=1); bassline(s, 'bass', theme, t, 'two'); brushes(s, t, n, 'ballad'); t += L
    comp(s, 'rhodes', theme, t, 'ballad', 40); play_melody(s, 'rhodes', theme, t, 66, embellish=0.4); bassline(s, 'bass', theme, t, 'two'); brushes(s, t, n, 'ballad', 0.8); t += L
    final(s, theme, t, part='rhodes')
    return s

def music_box(theme, bpm, seed):
    s = Song(bpm, theme['meter'], seed); L = len(theme['chords']) * theme['meter']; n = len(theme['chords']); t = theme['pickup']
    harp_arps(s, theme, t); play_melody(s, 'celesta', theme, t, 70, octave=0); t += L
    comp(s, 'piano', theme, t, 'pad', 34); harp_arps(s, theme, t, 50); play_melody(s, 'piano', theme, t, 60); play_melody(s, 'celesta', theme, t, 46, octave=1); t += L
    comp(s, 'piano', theme, t, 'waltz', 36); bassline(s, 'bass', theme, t, 'two', 74); brushes(s, t, n, 'waltz', 0.85); play_melody(s, 'piano', theme, t, 62, double=True); t += L
    final(s, theme, t)
    return s

def harp_arps(s, theme, start, vel=58):
    meter = s.meter
    for i, bar in enumerate(bars_of(theme)):
        at = start + i * meter; half = meter / len(bar)
        for j, sym in enumerate(bar):
            v = voicing(sym); r = root_note(sym, 40, 52)
            notes = [r, v[0], v[1], v[2], v[3], v[3] + 12 - 12 * (v[3] > 66)]
            step = half / len(notes)
            for k, nn in enumerate(notes): s.add('harp', at + j * half + k * step, nn, vel - 3 * k, 2.0)

def piano_cello(theme, bpm, seed):
    s = Song(bpm, theme['meter'], seed); L = len(theme['chords']) * theme['meter']; n = len(theme['chords']); t = theme['pickup']
    comp(s, 'piano', theme, t, 'arp', 38); play_melody(s, 'piano', theme, t, 60); cello_line(s, theme, t, 48); t += L
    comp(s, 'piano', theme, t, 'arp', 34); play_melody(s, 'cello', theme, t, 70, octave=-1, sustain=1.0); play_melody(s, 'piano', theme, t, 46, octave=1); t += L
    comp(s, 'piano', theme, t, 'pad', 34); play_melody(s, 'piano', theme, t, 58, embellish=0.3); cello_line(s, theme, t, 54); t += L
    final(s, theme, t)
    return s

def cello_line(s, theme, start, vel):
    meter = s.meter
    for i, bar in enumerate(bars_of(theme)):
        half = meter / len(bar)
        for j, sym in enumerate(bar):
            s.add('cello', start + i * meter + j * half, root_note(sym, 36, 48), vel, half * 1.02, 0.0)

def bossa(theme, bpm, seed):
    s = Song(bpm, theme['meter'], seed); L = len(theme['chords']) * theme['meter']; n = len(theme['chords']); t = 0
    comp(s, 'piano', theme, t, 'bossa', 38); bassline(s, 'bass', theme, t, 'bossa', 76); brushes(s, t, n, 'bossa', 0.8); play_melody(s, 'piano', theme, t, 62); t += L
    comp(s, 'rhodes', theme, t, 'bossa', 40); bassline(s, 'bass', theme, t, 'bossa', 76); brushes(s, t, n, 'bossa', 0.9); play_melody(s, 'piano', theme, t, 60, octave=1, embellish=0.3); t += L
    comp(s, 'piano', theme, t, 'bossa', 36); bassline(s, 'bass', theme, t, 'bossa', 74); brushes(s, t, n, 'bossa', 0.8); play_melody(s, 'piano', theme, t, 60); t += L
    final(s, theme, t)
    return s

def final(s, theme, t, part='piano'):
    sym = theme['chords'][-1].split('|')[-1]
    s.add('bass', t, root_note(sym), 72, 4.0)
    s.add(part, t, root_note(sym, 36, 48), 48, 6.0)
    for k, n in enumerate(voicing(sym)): s.add(part, t + 0.06 * k, n, 42, 6.0)
    s.add(part, t + 0.5, voicing(sym)[-1] + 12, 40, 6.0)

TRACKS = {
    '02_common_room_waltz': lambda: trio_waltz(COMMON_ROOM, 88, 21),
    '03_lake_window': lambda: rhodes_ballad(LAKE_WINDOW, 64, 31),
    '04_hedwig_music_box': lambda: music_box(HEDWIG, 72, 41),
    '05_green_scarf': lambda: trio_waltz(GREEN_SCARF, 96, 51, vel_shift=-2),
    '06_fireside_letters': lambda: solo_ballad(FIRESIDE, 58, 61),
    '07_hedwig_with_cellos': lambda: piano_cello(HEDWIG, 66, 71),
    '08_rain_on_the_glass': lambda: bossa(RAIN, 74, 81),
    '09_hedwig_ballad': lambda: solo_ballad(HEDWIG, 60, 91),
    '10_lake_window_reprise': lambda: solo_ballad(LAKE_WINDOW, 60, 101, octave_last=False),
    '11_common_room_solo': lambda: solo_ballad(COMMON_ROOM, 70, 111),
    '12_green_scarf_rhodes': lambda: rhodes_ballad(GREEN_SCARF, 76, 121),
}

ORDER = ['01_hedwig_trio', '02_common_room_waltz', '03_lake_window', '04_hedwig_music_box', '05_green_scarf',
         '06_fireside_letters', '07_hedwig_with_cellos', '08_rain_on_the_glass', '11_common_room_solo',
         '12_green_scarf_rhodes', '09_hedwig_ballad', '10_lake_window_reprise']

# ------------------------------------------------------------------ rendering + mixing
GAIN = {'piano': 16, 'rhodes': 14, 'bass': 9, 'kit': 15, 'stir': 22, 'celesta': 10, 'harp': 12, 'cello': 11}
FILT = {
    'piano': 'highpass=f=40,equalizer=f=220:t=q:w=0.9:g=1.5,equalizer=f=3200:t=q:w=1.2:g=-1.5,highshelf=f=6000:g=-3',
    'rhodes': 'highpass=f=45,equalizer=f=250:t=q:w=1:g=1,highshelf=f=5000:g=-3',
    'bass': 'pan=mono|c0=0.5*c0+0.5*c1,highpass=f=34,lowpass=f=2800,equalizer=f=90:t=q:w=1:g=1.5,pan=stereo|c0=c0|c1=c0',
    'kit': 'highshelf=f=6000:g=-4,lowpass=f=9500,pan=stereo|c0=0.85*c0+0.15*c1|c1=c1',
    'stir': 'highpass=f=150,highshelf=f=7000:g=-3,pan=stereo|c0=0.8*c0+0.2*c1|c1=c1',
    'celesta': 'highshelf=f=6000:g=-4',
    'harp': 'highshelf=f=6000:g=-2',
    'cello': 'lowpass=f=5000',
}

def write_midi(s, part, path):
    f = mido.MidiFile(type=0, ticks_per_beat=TPB); tr = mido.MidiTrack(); f.tracks.append(tr)
    tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(s.bpm), time=0))
    evs = []
    if part in ('kit', 'stir'):
        evs.append((0, 0, 'cc', 7, 100))
    for b, n, v, d in s.ev[part]:
        evs.append((int(b * TPB), 1, 'on', n, v)); evs.append((int((b + d) * TPB), 0, 'off', n, 0))
    evs.sort(key=lambda e: (e[0], e[1]))
    last = 0
    for t, _, kind, n, v in evs:
        if kind == 'cc': tr.append(mido.Message('control_change', control=n, value=v, time=t - last))
        elif kind == 'on': tr.append(mido.Message('note_on', note=n, velocity=v, time=t - last))
        else: tr.append(mido.Message('note_off', note=n, velocity=0, time=t - last))
        last = t
    f.save(path)

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def build(name):
    s = TRACKS[name]()
    d = os.path.join(HERE, 'tracks', name); os.makedirs(d, exist_ok=True)
    parts = sorted(s.ev)
    for p in parts:
        write_midi(s, p, os.path.join(d, p + '.mid'))
        run([SFIZZ, '--sfz', SFZ[p], '--midi', os.path.join(d, p + '.mid'), '--wav', os.path.join(d, p + '.wav'), '-s', '48000', '-q', '3', '-p', '256'])
    dur = s.length() * 60 / s.bpm + 5
    ins = []; fc = []
    for i, p in enumerate(parts):
        ins += ['-i', os.path.join(d, p + '.wav')]
        fc.append(f'[{i}:a]{FILT[p]},volume={GAIN[p]}dB[s{i}]')
    ins += ['-i', IR]; k = len(parts)
    fc.append(''.join(f'[s{i}]' for i in range(k)) + f'amix=inputs={k}:normalize=0:duration=longest,atrim=0:{dur:.2f},asplit[dry][send]')
    fc.append('[send]highpass=f=220,lowpass=f=5500[sendf]')
    fc.append(f'[sendf][{k}:a]afir=dry=10:wet=10:length=1,volume=-11dB[wet]')
    fc.append(f'[dry][wet]amix=inputs=2:normalize=0:duration=first,lowpass=f=14000,afade=t=out:st={dur - 4:.2f}:d=4')
    out = os.path.join(HERE, 'tracks', name + '.wav')
    run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fc), '-ar', '44100', '-c:a', 'pcm_f32le', out])
    print(name, f'{dur:.1f}s', 'parts', parts, flush=True)
    return out

def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float([l for l in r.splitlines() if l.strip().startswith('I:')][-1].split()[1])

def join(names):
    files = [os.path.join(HERE, 'tracks', n + '.wav') for n in names]
    ins = sum([['-i', f] for f in files], [])
    # match every track to the same loudness first, then crossfade them in order
    fc = [f'[{i}:a]aresample=44100,volume={-20 - lufs(f):.2f}dB[n{i}]' for i, f in enumerate(files)]
    cur = '[n0]'
    for i in range(1, len(files)):
        fc.append(f'{cur}[n{i}]acrossfade=d=4:c1=tri:c2=tri[x{i}]'); cur = f'[x{i}]'
    pre = os.path.join(HERE, 'suite_premaster.wav')
    run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fc), '-map', cur, '-c:a', 'pcm_f32le', pre])
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-17:TP=-1.5:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    js = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
    g = min(-17 - float(js['input_i']), -1.5 - float(js['input_tp']))
    out = os.path.join(HERE, 'you_elsewhere_ep01_suite_v1')
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', pre, '-af', f'volume={g:.2f}dB', '-ar', '44100', '-c:a', 'pcm_s24le', out + '.wav'])
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', out + '.wav', '-c:a', 'libmp3lame', '-b:a', '256k', out + '.mp3'])
    print('joined', len(files), 'tracks, gain', round(g, 2))

if __name__ == '__main__':
    todo = sys.argv[1:] or list(TRACKS)
    for n in todo: build(n)
    if not sys.argv[1:]:
        join(ORDER)
