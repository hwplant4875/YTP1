# Hedwig's Theme as a romantic jazz-waltz piano trio, written as MIDI for FL Studio.
# Tracks: 1 Piano (melody + rootless comping), 2 Upright bass, 3 Brush drums (GM ch 10).
import mido, random
random.seed(4)
TPB, BPM = 480, 88
names = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
def m(s): return 12*(int(s[-1])+1)+names[s[:-1]]
mel = [('B4',1),('E5',1.5),('G5',.5),('F#5',1),('E5',2),('B5',1),('A5',3),('F#5',3),('E5',1.5),('G5',.5),('F#5',1),('D#5',2),('F5',1),('B4',3),('-',2),
       ('B4',1),('E5',1.5),('G5',.5),('F#5',1),('E5',2),('B5',1),('D6',2),('C#6',1),('C6',2),('G#5',1),('C6',1.5),('B5',.5),('A#5',1),('A#4',2),('G5',1),('E5',3)]
# one chord per bar (3/4), melody starts on beat 3 pickup
bars = ['Em9','Em9','Am9','B7b9','Em9','B7b9','Em9','Em9','Em9','Em9','Gmaj7','Cmaj7','Am9','B7b9','Em9','Em9']
VO = {'Em9':['G3','B3','D4','F#4'],'Am9':['C4','E4','G4','B4'],'B7b9':['A3','C4','D#4','G4'],
      'Gmaj7':['F#3','A3','B3','D4'],'Cmaj7':['B3','E4','F#4','G4'],'Fmaj7#11':['E3','A3','B3','C4']}
ROOT = {'Em9':'E2','Am9':'A1','B7b9':'B1','Gmaj7':'G1','Cmaj7':'C2','Fmaj7#11':'F1'}
FIFTH = {'Em9':'B2','Am9':'E2','B7b9':'F#2','Gmaj7':'D2','Cmaj7':'G2','Fmaj7#11':'C2'}
ev = {0:[], 1:[], 2:[]}  # track -> (beat, note, vel, dur_beats, channel)
def hum(): return random.gauss(0, 0.02)
def add(tr, b, n, v, d, ch=0): ev[tr].append((max(0, b + hum()), n, max(1, min(127, int(v))), d, ch))
BAR = 3
def section(start, chords, comp_style, bass_style, drums):
    for i, c in enumerate(chords):
        at = start + i*BAR
        vo = [m(x) for x in VO[c]]
        if comp_style == 'pad':
            for k, n in enumerate(vo): add(0, at + 0.04*k, n, 38, 2.8)
        elif comp_style == 'waltz':
            for beat in (1, 2):
                for n in vo: add(0, at + beat, n, 40 if beat == 1 else 34, 0.7)
        r, f = m(ROOT[c]), m(FIFTH[c])
        nxt = m(ROOT[chords[(i+1) % len(chords)]])
        if bass_style == 'two':
            add(1, at, r, 82, 1.9); add(1, at + 2, f, 70, 0.9)
        elif bass_style == 'walk':
            appr = nxt + (1 if random.random() < .5 else -1)
            add(1, at, r, 86, 0.95); add(1, at + 1, f, 72, 0.95); add(1, at + 2, appr, 74, 0.95)
        if drums:
            # brush swirl (snare, soft) every beat, ride on 1 and swung 2&, hat foot on 2
            for beat in range(3): add(2, at + beat, 40, 26 + random.randint(0, 6), 0.9, 9)
            add(2, at, 51, 40, 0.5, 9); add(2, at + 2, 51, 34, 0.5, 9)
            add(2, at + 1, 44, 34, 0.3, 9)
def melody(start, vel, octave_double=False):
    t = 0
    for n, b in mel:
        if n != '-':
            sw = 0.16 if abs((t % 1) - 0.5) < 1e-6 else 0
            v = vel + (6 if b >= 2 else 0) + random.randint(-4, 4)
            add(0, start + t + sw, m(n), v, b*0.95)
            if octave_double: add(0, start + t + sw, m(n) - 12, v - 20, b*0.9)
        t += b
    return t
# layout (v2): no intro, melody at 0:00; head 1 (sparse), head 2 (full trio), interlude 4 bars, head 3 (soft, octave), outro
# melody from the very first second (user): pickup at beat 0, solo piano head first
b = 1
L = melody(0, 62)
section(b, bars, 'pad', None, False); b += len(bars)*BAR
melody(b - 1, 68, True)
section(b, bars, 'waltz', 'walk', True); b += len(bars)*BAR
section(b, ['Gmaj7','Cmaj7','Am9','B7b9'], 'waltz', 'walk', True); b += 4*BAR
melody(b - 1, 58)
section(b, bars, 'pad', 'two', True); b += len(bars)*BAR
# outro: Em(add9) arpeggio + held chord
for k, x in enumerate(['E2','B2','D3','G3','B3','D#4','F#4','B4']): add(0, b + k*0.25, m(x), 44 - k, 8)
add(1, b, m('E1'), 70, 6)
mid = mido.MidiFile(ticks_per_beat=TPB)
names_t = ['Piano', 'Upright Bass', 'Brush Drums']
for tr in range(3):
    T = mido.MidiTrack(); mid.tracks.append(T)
    T.append(mido.MetaMessage('track_name', name=names_t[tr], time=0))
    if tr == 0:
        T.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0))
        T.append(mido.MetaMessage('time_signature', numerator=3, denominator=4, time=0))
    prog = {0: 0, 1: 32, 2: 0}[tr]
    ch = 9 if tr == 2 else tr
    T.append(mido.Message('program_change', program=prog, channel=ch, time=0))
    msgs = []
    for st, n, v, d, c in ev[tr]:
        c = 9 if tr == 2 else tr
        msgs.append((int(st*TPB), 1, n, v, c)); msgs.append((int((st+d)*TPB), 0, n, 0, c))
    msgs.sort(key=lambda x: (x[0], x[1]))
    now = 0
    for tk, on, n, v, c in msgs:
        T.append(mido.Message('note_on' if on else 'note_off', note=n, velocity=v, channel=c, time=tk - now)); now = tk
mid.save('hedwig_trio.mid')
print('bars', b/BAR, 'seconds', (b + 8) * 60 / BPM)
