"""Sample 02: heavenly + heavy slowed phonk. C minor, made at 125 BPM, slowed x0.88 (~110 BPM).
Splice samples (vocals, 808, drums, cowbell) arranged by code; melody is a 2-bar motif written here."""
import sys, numpy as np, soundfile as sf, librosa
sys.path.insert(0, '/tmp/claude-0/music')
from engine import *
from pedalboard import time_stretch

SP = '/tmp/claude-0/music/splice/'
np.random.seed(3)
BPM, BARS, SLOW = 125, 56, 0.88
s = Song(BPM, BARS)
b = s.beat


def load(name, semis=0.0, stretch=1.0):
    a, sr = sf.read(SP + name, dtype='float32', always_2d=True)
    if sr != SR:
        a = np.stack([librosa.resample(a[:, c], orig_sr=sr, target_sr=SR) for c in range(a.shape[1])], 1)
    if a.shape[1] == 1:
        a = np.repeat(a, 2, 1)
    if semis or stretch != 1.0:
        a = time_stretch(a.T.copy(), SR, stretch_factor=stretch, pitch_shift_in_semitones=semis).T
    return a.astype(np.float32)


def resample_pitch(a, semis):
    """Sampler-style pitch (length changes with pitch, like an 808 / cowbell played on keys)."""
    r = 2 ** (semis / 12)
    n = int(len(a) / r)
    idx = np.arange(n) * r
    return np.stack([np.interp(idx, np.arange(len(a)), a[:, c]) for c in range(2)], 1).astype(np.float32)


SEC = {'intro': (0, 8), 'drop1': (8, 24), 'break': (24, 32), 'drop2': (32, 48), 'outro': (48, 56)}
inside = lambda bar, *n: any(SEC[k][0] <= bar < SEC[k][1] for k in n)

# 8-bar progression: Cm Cm Eb Eb Ab Ab Fm G  (fits the soprano loop's Bb -> G/Ab line)
ROOTS = ['C', 'C', 'D#', 'D#', 'G#', 'G#', 'F', 'G']
CHORD = {'C': ['C4', 'D#4', 'G4', 'A#4'], 'D#': ['A#3', 'D#4', 'G4', 'D5'], 'G#': ['G#3', 'C4', 'D#4', 'G4'],
         'F': ['F3', 'G#3', 'C4', 'D#4'], 'G': ['G3', 'B3', 'D4', 'G4']}

# ---- vocals (Splice): soprano solo/duo are 8-bar loops at 125 in Cm
sop = load('MNT_CV_125_vocal_soprano_solo_swell_chorus_delay_Cm.wav')
duo = load('MNT_CV_125_vocal_soprano_duo_swell_Cm.wav')
choir = load('OS_AD_140_vocal_choir_dreamer_Dm.wav', semis=-2, stretch=140 / 125)
drone = load('MA_MUR_120_Vocal_Drone_Loop_MagicWand_Cm.wav', stretch=120 / 125)
L8 = int(s.t(8) * SR)
for bar in range(0, BARS, 8):
    if inside(bar, 'intro', 'break', 'outro'):
        s.add('sop', sop[:L8], s.t(bar))
    if inside(bar, 'drop1', 'drop2'):
        s.add('sop', duo[:L8] * 0.8, s.t(bar))
        s.add('choir', choir[:L8], s.t(bar))
    if inside(bar, 'break'):
        s.add('choir', choir[:L8] * 0.7, s.t(bar))
    s.add('drone', drone[:L8], s.t(bar))

# ---- pads under everything (warm pad), and the short heavenly motif (celesta + music box)
pad = []
for bar in range(BARS):
    for p in CHORD[ROOTS[bar % 8]]:
        pad.append((s.t(bar), 4 * b, midi(p), 60))
s.gm('pad', 89, pad)

MOTIF = [(0, 'G5', .5), (.5, 'C6', .5), (1, 'D#6', 1), (2, 'D6', .5), (2.5, 'C6', .5), (3, 'G5', 1),
         (4, 'G5', .5), (4.5, 'C6', .5), (5, 'D#6', 1.5), (6.5, 'C6', .5), (7, 'G5', 1)]
bell, mbox = [], []
for bar in range(0, BARS, 2):
    if inside(bar, 'break', 'outro'):
        continue
    for beat, p, d in MOTIF:
        v = 70 if inside(bar, 'intro') else 92
        bell.append((s.t(bar, beat), d * b, midi(p), v))
        mbox.append((s.t(bar, beat), d * b, midi(p) + 12, v - 25))
s.gm('bell', 8, bell)    # celesta
s.gm('mbox', 10, mbox)   # music box an octave up = sparkle

# ---- drums + 808 (Splice one-shots), heavy in drops
K = load('RKU_ENC_kick_one_shot_punchy.wav')
CL = load('STCR2_PHONK_Clap_One_Shot_Rose.wav')
HH = load('ORBIT_RT_hat_one_shot_closed_crisp.wav')
B8 = load('TRKTRN_LXLVMK_808_Bass_Hydraulic_C.wav')   # C1-ish root
CB = load('RKU_MT_synth_lead_one_shot_cowbell_drift_C.wav')
ROOT_SEMI = {'C': 0, 'D#': 3, 'G#': -4, 'F': 5, 'G': 7}
# 808 rhythm per bar (beat, length in beats) - heavy, syncopated
P808 = [(0, 1.5), (1.5, 1.0), (2.5, 0.75), (3.25, 0.75)]
for bar in range(BARS):
    if not inside(bar, 'drop1', 'drop2'):
        continue
    semi = ROOT_SEMI[ROOTS[bar % 8]]
    for i, (beat, ln) in enumerate(P808):
        x = resample_pitch(B8, semi + (12 if i == 3 and bar % 2 else 0))[:int(ln * b * SR)].copy()
        x[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))[:, None]
        s.add('808', x, s.t(bar, beat))
    for beat in (0, 2.5) if bar % 2 == 0 else (0, 1.75, 2.5):
        s.add('kick', K, s.t(bar, beat))
    for beat in (1, 3):
        s.add('clap', CL, s.t(bar, beat))
    for i in range(8):
        s.add('hats', HH * (0.9 if i % 2 == 0 else 0.6), s.t(bar, i * 0.5))
    if bar % 4 == 3:  # triplet roll into the next phrase
        for j in range(6):
            s.add('hats', HH * 0.55, s.t(bar, 3 + j / 6))
    if inside(bar, 'drop2') and bar % 2 == 0:  # drift-phonk cowbell plays the motif
        for beat, p, d in MOTIF:
            semi_cb = midi(p) - midi('C5')
            s.add('cowbell', resample_pitch(CB, semi_cb)[:int(max(d, .5) * b * SR)], s.t(bar, beat))

# build-up into drops: last bar of intro / break = snare-style clap roll + filter
for bar in (7, 31):
    for j in range(8):
        s.add('clap', CL * (0.3 + 0.08 * j), s.t(bar, 2 + j / 4))

# ---- FX per part
s.fx('sop', Pedalboard([HighpassFilter(250), Reverb(room_size=0.9, wet_level=0.35, dry_level=0.75)]))
s.fx('choir', Pedalboard([HighpassFilter(200), Reverb(room_size=0.9, wet_level=0.35, dry_level=0.7)]))
s.fx('drone', Pedalboard([HighpassFilter(150), LowpassFilter(6000)]))
s.fx('pad', Pedalboard([HighpassFilter(150), LowpassFilter(5000), Chorus(rate_hz=0.3, depth=0.4, mix=0.5), Reverb(room_size=0.9, wet_level=0.5, dry_level=0.4)]))
s.fx('bell', Pedalboard([HighpassFilter(400), Delay(delay_seconds=b * 0.75, feedback=0.3, mix=0.25), Reverb(room_size=0.85, wet_level=0.4, dry_level=0.6)]))
s.fx('mbox', Pedalboard([HighpassFilter(800), Reverb(room_size=0.95, wet_level=0.6, dry_level=0.4)]))
s.fx('808', Pedalboard([Distortion(drive_db=10), LowpassFilter(1800), Compressor(threshold_db=-10, ratio=4)]))
s.fx('kick', Pedalboard([Distortion(drive_db=4)]))
s.fx('clap', Pedalboard([Reverb(room_size=0.5, wet_level=0.2, dry_level=0.8)]))
s.fx('cowbell', Pedalboard([HighpassFilter(300), Reverb(room_size=0.6, wet_level=0.25, dry_level=0.75)]))
for k, db in {'sop': -11, 'choir': -10, 'drone': -11, 'pad': -3, 'bell': 4, 'mbox': 0, '808': -3,
              'kick': -2, 'clap': -3, 'hats': -2, 'cowbell': -2}.items():
    s.gain(k, db)

m = s.mix()
m = m - m.mean(0)
# intro: lowpass opening up over 8 bars
e = int(s.t(8) * SR)
lp = Pedalboard([LowpassFilter(1200)])(m[:e].T.copy(), SR).T
w = np.linspace(0, 1, e)[:, None] ** 2
m[:e] = lp * (1 - w) + m[:e] * w
# sidechain-style duck of the music under the kick in drops (pump = workout energy)
duck = np.ones(len(m), np.float32)
kl = int(0.18 * SR)
curve = 1 - 0.35 * np.exp(-np.arange(kl) / (0.06 * SR))
for bar in range(BARS):
    if inside(bar, 'drop1', 'drop2'):
        for beat in (0, 1, 2, 3):
            i = int(s.t(bar, beat) * SR)
            duck[i:i + kl] = np.minimum(duck[i:i + kl], curve[:len(duck[i:i + kl])])
m = m * duck[:, None]

m = Pedalboard([HighpassFilter(28), Compressor(threshold_db=-14, ratio=2.5, attack_ms=15, release_ms=120), Distortion(drive_db=2)])(m.T.copy().astype(np.float32), SR).T
m = slowed(m, SLOW)
m = Pedalboard([HighpassFilter(28), Reverb(room_size=0.7, wet_level=0.12, dry_level=0.92), Limiter(threshold_db=-0.8)])(m.T.copy().astype(np.float32), SR).T
m = m / np.abs(m).max() * 0.9
end = int((s.t(BARS) / SLOW + 2.5) * SR)
m = m[:end]
m[-3 * SR:] *= np.linspace(1, 0, 3 * SR)[:, None] ** 1.5
sf.write(sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/music/song2.wav', m, SR)
print('done', round(len(m) / SR, 1), 's, tempo', round(BPM * SLOW, 1))
