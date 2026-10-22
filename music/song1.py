import sys, numpy as np, soundfile as sf
sys.path.insert(0, 'music')
from engine import *

np.random.seed(7)
BPM, BARS = 125, 36
s = Song(BPM, BARS)
b = s.beat

# i - VI - III - VII in C minor, one chord per bar
CH = [['C4', 'D#4', 'G4', 'A#4'], ['G#3', 'C4', 'D#4', 'G4'], ['G3', 'A#3', 'D#4', 'D4'], ['A#3', 'D4', 'F4', 'C5']]
ROOT = [midi('C2'), midi('G#1'), midi('D#2'), midi('A#1')]
SECTIONS = {'intro': (0, 8), 'drop1': (8, 24), 'break': (24, 28), 'drop2': (28, 36)}
inside = lambda bar, *names: any(SECTIONS[n][0] <= bar < SECTIONS[n][1] for n in names)

# ---- pads (warm pad + strings) all song
pad, strings = [], []
for bar in range(BARS):
    ch = CH[bar % 4]
    for p in ch:
        pad.append((s.t(bar), 4 * b, midi(p), 70))
        if not inside(bar, 'intro'):
            strings.append((s.t(bar), 4 * b, midi(p) - 12, 55))
s.gm('pad', 89, pad)
s.gm('strings', 49, strings)

# ---- bell arpeggio (8ths) from chord tones
bell = []
pat = [3, 2, 1, 2, 3, 4, 3, 2]
for bar in range(BARS):
    if inside(bar, 'break'):
        continue
    tones = sorted(midi(p) + 12 for p in CH[bar % 4]); tones.append(tones[0] + 12)
    for i, k in enumerate(pat):
        bell.append((s.t(bar, i * 0.5), 0.5 * b, tones[k], 72 if i % 2 == 0 else 58))
s.gm('bell', 14, bell)  # tubular bells / music-box feel

# ---- lead melody (voice oohs + synth lead) in drops
MEL = [(0, 'G5', 1.5), (1.5, 'F5', .5), (2, 'D#5', 2), (4, 'D#5', 1.5), (5.5, 'D5', .5), (6, 'C5', 2),
       (8, 'A#4', 1.5), (9.5, 'C5', .5), (10, 'D#5', 2), (12, 'D5', 3), (15, 'A#4', 1)]
lead, oohs = [], []
for bar in range(0, BARS, 4):
    if not inside(bar, 'drop1', 'drop2'):
        continue
    for beat, p, d in MEL:
        lead.append((s.t(bar, beat), d * b, midi(p), 85))
        oohs.append((s.t(bar, beat), d * b, midi(p) - 12, 80))
s.gm('lead', 81, lead)   # sawtooth lead
s.gm('oohs', 53, oohs)   # voice oohs (vocal-chop stand-in)

# ---- 808 + drums
K, CL, HC, HO, CB = kick(), clap(), hat(), hat(open_=True), cowbell()
hits808 = [(0, 1.5), (1.5, 1.0), (2.5, 1.5)]
for bar in range(BARS):
    if not inside(bar, 'drop1', 'drop2'):
        continue
    r = ROOT[bar % 4]
    for i, (beat, dur) in enumerate(hits808):
        f = pretty_midi.note_number_to_hz(r + (12 if i == 1 and bar % 2 else 0))
        glide = pretty_midi.note_number_to_hz(r + 12) if i == 2 and bar % 4 == 3 else None
        s.add('808', bass808(f, dur * b, glide_from=glide) * 0.9, s.t(bar, beat))
        s.add('kick', K * 0.8, s.t(bar, beat))
    s.add('clap', CL * 0.6, s.t(bar, 2))
    for i in range(8):
        s.add('hats', HC * (0.32 if i % 2 else 0.22), s.t(bar, i * 0.5))
    if bar % 2 == 1:  # 16th/32nd roll at the end of every other bar
        for j in range(6):
            s.add('hats', HC * 0.18, s.t(bar, 3 + j / 6))
    s.add('hats', HO * 0.2, s.t(bar, 3.5))
    if inside(bar, 'drop2'):  # phonk cowbell answers on offbeats
        for beat, sh in [(0.75, 1.0), (1.5, 1.12), (2.25, 1.0), (3.0, 0.89)]:
            s.add('cowbell', cowbell(sh) * 0.25, s.t(bar, beat))

# ---- per-part FX
s.fx('pad', Pedalboard([LowpassFilter(6000), Chorus(rate_hz=0.3, depth=0.4, mix=0.5), Reverb(room_size=0.9, wet_level=0.5, dry_level=0.5)]))
s.fx('strings', Pedalboard([LowpassFilter(3000), Reverb(room_size=0.85, wet_level=0.45, dry_level=0.5)]))
s.fx('bell', Pedalboard([HighpassFilter(300), Delay(delay_seconds=b * 0.75, feedback=0.35, mix=0.3), Reverb(room_size=0.8, wet_level=0.4, dry_level=0.6)]))
s.fx('lead', Pedalboard([LowpassFilter(7000), Chorus(rate_hz=0.8, depth=0.25, mix=0.4), Reverb(room_size=0.9, wet_level=0.45, dry_level=0.55)]))
s.fx('oohs', Pedalboard([Reverb(room_size=0.95, wet_level=0.6, dry_level=0.4)]))
s.fx('808', Pedalboard([LowpassFilter(900), Compressor(threshold_db=-12, ratio=3)]))
s.fx('clap', Pedalboard([Reverb(room_size=0.6, wet_level=0.3, dry_level=0.7)]))
s.fx('cowbell', Pedalboard([Reverb(room_size=0.5, wet_level=0.25, dry_level=0.75)]))
for k, db in {'pad': -4, 'strings': -9, 'bell': -3, 'lead': -9, 'oohs': -5, '808': -2, 'kick': -5, 'clap': -9, 'hats': -6, 'cowbell': -8}.items():
    s.gain(k, db)

# intro filtered: lowpass sweep on whole mix for first 8 bars
m = s.mix()
end_intro = int(s.t(8) * SR)
intro = Pedalboard([LowpassFilter(900)])(m[:end_intro].T.copy(), SR).T
fade = np.linspace(0, 1, end_intro)[:, None] ** 2
m[:end_intro] = intro * (1 - fade) + m[:end_intro] * fade

# master: glue, warmth, then "slowed + reverb"
m = m - m.mean(0)
m = Pedalboard([HighpassFilter(28), Compressor(threshold_db=-14, ratio=2.5, attack_ms=10, release_ms=150), Distortion(drive_db=3), LowpassFilter(14000)])(m.T.copy(), SR).T
m = slowed(m, 0.82)
m = Pedalboard([HighpassFilter(28), Reverb(room_size=0.75, wet_level=0.18, dry_level=0.9), Limiter(threshold_db=-1.0)])(m.T.copy().astype(np.float32), SR).T
m = m / np.abs(m).max() * 0.89
# trim tail silence and fade out
end = int((s.t(BARS) / 0.82 + 3) * SR)
m = m[:end]; m[-2 * SR:] *= np.linspace(1, 0, 2 * SR)[:, None]
sf.write(sys.argv[1] if len(sys.argv) > 1 else 'music/song1.wav', m, SR)
print('done', len(m) / SR, 's, tempo', round(BPM * 0.82, 1))
