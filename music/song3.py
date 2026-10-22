"""Sample 03: hardtekk / hardstyle-phonk gym track. G minor, 155 BPM, drums are the main element.
Splice: hardstyle crush kick + hard techno click kick, hardstyle screech lead, demon laugh, boings,
'let's go' shout, hard-techno fill. Tekk rolling bass, risers and hats are synthesized here."""
import sys, numpy as np, soundfile as sf, librosa
sys.path.insert(0, '/tmp/claude-0/music')
from engine import *
from pedalboard import Bitcrush, PeakFilter, HighShelfFilter, Clipping

SP = '/tmp/claude-0/music/splice/'
np.random.seed(5)
BPM, BARS = 155, 80
s = Song(BPM, BARS)
b = s.beat

SEC = {'intro': (0, 8), 'drop1': (8, 32), 'break': (32, 40), 'drop2': (40, 72), 'outro': (72, 80)}
inside = lambda bar, *n: any(SEC[k][0] <= bar < SEC[k][1] for k in n)
DROPS = ('drop1', 'drop2')


def load(name, semis=0.0):
    a, sr = sf.read(SP + name, dtype='float32', always_2d=True)
    if sr != SR:
        a = np.stack([librosa.resample(a[:, c], orig_sr=sr, target_sr=SR) for c in range(a.shape[1])], 1)
    if a.shape[1] == 1:
        a = np.repeat(a, 2, 1)
    return resample_pitch(a, semis) if semis else a.astype(np.float32)


def resample_pitch(a, semis):
    r = 2 ** (semis / 12)
    idx = np.arange(int(len(a) / r)) * r
    return np.stack([np.interp(idx, np.arange(len(a)), a[:, c]) for c in range(2)], 1).astype(np.float32)


def cut(a, sec, fade=0.008):
    a = a[:int(sec * SR)].copy()
    f = min(int(fade * SR), len(a))
    a[-f:] *= np.linspace(1, 0, f)[:, None]
    return a


# progression, 2 bars per chord: Gm Gm Eb F
ROOTS = [0, 0, -4, -2]
root = lambda bar: ROOTS[(bar // 2) % 4]

# ---- KICK (main element): crush kick body + hard techno click layer, four on the floor
KB = load('MO_WS_155_kick_hardstyle_hard_techno_crush.wav')
# the crush kick is very wide (L/R corr 0.29): keep its body below 200 Hz in the middle so it punches
lo = Pedalboard([LowpassFilter(200)])(KB.T.copy(), SR).T
KB = KB - lo + lo.mean(1, keepdims=True)
KC = Pedalboard([HighpassFilter(1500)])(load('FSS_RKHSOD_kick_techno_hard.wav').T.copy(), SR).T
KICK = KB.copy()
n = min(len(KICK), len(KC)); KICK[:n] += KC[:n] * 0.35
KICK = np.tanh(KICK * 2.2) / np.tanh(2.2)
for bar in range(BARS):
    if inside(bar, 'break'):
        continue
    for beat in range(4):
        if bar % 8 == 7 and beat == 3 and inside(bar, *DROPS):
            for j in range(4):   # 16th kick stutter into the next phrase
                s.add('kick', KICK[:int(b / 4 * SR)] * (0.75 + 0.08 * j), s.t(bar, 3 + j / 4))
            continue
        s.add('kick', KICK * (0.7 if inside(bar, 'intro') else 1.0), s.t(bar, beat))


# ---- TEKK BASS: distorted saw, rolling 16ths after each kick (kick-bass-bass-bass)
def tekk(semis, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 49.0 * 2 ** (semis / 12)          # G1
    x = 2 * ((t * f) % 1) - 1 + 0.5 * (2 * ((t * f * 2.005) % 1) - 1)
    e = np.minimum(t / 0.002, 1) * np.exp(-t * 18)
    return np.tanh(3 * x * e).astype(np.float32)


for bar in range(BARS):
    if not inside(bar, *DROPS, 'outro'):
        continue
    for beat in range(4):
        for k in (1, 2, 3):
            s.add('bass', tekk(root(bar), b / 4 * 0.95), s.t(bar, beat + k / 4))

# ---- CLAP on 2 & 4, offbeat open hats, 16th closed hats
CL = load('STCR2_PHONK_Clap_One_Shot_Rose.wav')
HC, HO = load('ORBIT_RT_hat_one_shot_closed_crisp.wav'), hat(open_=True)
for bar in range(BARS):
    if not inside(bar, *DROPS):
        continue
    for beat in (1, 3):
        s.add('clap', CL, s.t(bar, beat))
    for beat in range(4):
        s.add('hats', HO * 0.5, s.t(bar, beat + 0.5))
    if inside(bar, 'drop2'):
        for i in range(16):
            s.add('hats', HC * (0.7 if i % 2 else 0.45), s.t(bar, i / 4))

# ---- SCREECH LEAD riff (hardstyle one-shot in G, sampler-pitched), 2-bar call
LEAD = load('AU_HC_lead_one_shot_misapprehension_G.wav')
RIFF = [(0, 0, .5), (.5, 0, .5), (1, 3, .75), (1.75, 0, .75), (2.5, 7, .5), (3, 5, .5), (3.5, 3, .5),
        (4, 0, .5), (4.5, 0, .5), (5, 3, .75), (5.75, 5, .75), (6.5, 3, .5), (7, -2, .5), (7.5, 0, .5)]
for bar in range(0, BARS, 2):
    on = inside(bar, 'drop2') or (inside(bar, 'drop1') and bar >= 16) or inside(bar, 'break')
    if not on:
        continue
    for beat, semi, d in RIFF:
        s.add('lead', cut(resample_pitch(LEAD, semi), d * b * 0.9), s.t(bar, beat))

# ---- FX ear-candy: demon laugh, boings, 'let's go', fills, riser + kick roll into drops
LAUGH = load('ESM_Demon_Vocal_You_Fool_Ha_Ha_Ha.wav', semis=-2)
BOING = load('FF_CRT_sfx_boing_one_low.wav')
BOING3 = load('FF_CRT_sfx_boing_two_high_triple_hop.wav')
GO = load('ELX_HV2_vocal_phrase_lets_go_03_128.wav')
FILL = load('DS_HT_158_drum_fill_mirror_G.wav')
s.add('voice', LAUGH, s.t(0, 0.5))
s.add('voice', LAUGH, s.t(32, 0))
s.add('voice', GO, s.t(7, 2))
s.add('voice', GO, s.t(39, 2))
s.add('voice', GO * 0.8, s.t(56, 0))
for bar in range(BARS):
    if inside(bar, *DROPS) and bar % 4 == 1:
        s.add('boing', BOING, s.t(bar, 3.5))
    if inside(bar, 'break') and bar % 2 == 1:
        s.add('boing', BOING3, s.t(bar, 2))
    if inside(bar, *DROPS) and bar % 8 == 3:
        s.add('fill', FILL, s.t(bar, 3))


def riser(bars):
    n = int(s.t(bars) * SR); t = np.linspace(0, 1, n)
    x = np.random.randn(n).astype(np.float32) * t ** 2
    out = np.zeros(n, np.float32)
    for i in range(16):   # stepped highpass sweep, 16 slices
        a, z = i * n // 16, (i + 1) * n // 16
        out[a:z] = HighpassFilter(200 + i * 500)(np.stack([x[a:z]] * 2), SR)[0]
    return out


s.add('riser', riser(4) * 0.5, s.t(36))
for bar in (38, 39):   # kick roll 8ths -> 16ths, pitching up
    step = 0.5 if bar == 38 else 0.25
    for j in range(int(4 / step)):
        k = cut(resample_pitch(KICK, (bar - 38) * 4 + j * step * 1.5), step * b)
        s.add('kick', k * (0.6 + 0.1 * j * step), s.t(bar, j * step))

# ---- per-part FX + gains (kick loudest)
s.fx('kick', Pedalboard([PeakFilter(60, 3, 0.8), HighShelfFilter(4000, -5), Clipping(-3)]))
s.fx('bass', Pedalboard([HighpassFilter(35), LowpassFilter(2500), Distortion(drive_db=8), Compressor(threshold_db=-12, ratio=4)]))
s.fx('clap', Pedalboard([HighpassFilter(300), Reverb(room_size=0.4, wet_level=0.18, dry_level=0.85)]))
s.fx('hats', Pedalboard([HighpassFilter(6000)]))
s.fx('lead', Pedalboard([HighpassFilter(250), Delay(delay_seconds=b * 0.75, feedback=0.25, mix=0.2),
                         Reverb(room_size=0.8, wet_level=0.3, dry_level=0.8)]))
s.fx('voice', Pedalboard([HighpassFilter(120), Reverb(room_size=0.7, wet_level=0.25, dry_level=0.9)]))
s.fx('boing', Pedalboard([HighpassFilter(100), Reverb(room_size=0.4, wet_level=0.15, dry_level=0.9)]))
s.fx('fill', Pedalboard([HighpassFilter(80)]))
for k, db in {'kick': -7, 'bass': -3, 'clap': 1, 'hats': 0, 'lead': -3, 'voice': -6, 'boing': -2,
              'fill': 2, 'riser': 2}.items():
    s.gain(k, db)

# sidechain duck: bass/lead/hats under every kick (kick stays untouched)
duck = np.ones(s.n, np.float32)
kl = int(b * SR * 0.9)
curve = 1 - 0.7 * np.exp(-np.arange(kl) / (0.05 * SR))
for bar in range(BARS):
    if inside(bar, 'break'):
        continue
    for beat in range(4):
        i = int(s.t(bar, beat) * SR)
        duck[i:i + kl] = np.minimum(duck[i:i + kl], curve[:len(duck[i:i + kl])])
for k in ('lead', 'hats', 'clap', 'riser'):
    s.parts[k] *= duck[:, None]

voice = s.parts.pop('voice')
m = s.mix()
m = m - m.mean(0)
e = int(s.t(8) * SR)   # intro: lowpassed, opens up
lp = Pedalboard([LowpassFilter(700)])(m[:e].T.copy(), SR).T
w = np.linspace(0, 1, e)[:, None] ** 3
m[:e] = lp * (1 - w) + m[:e] * w
m = m + voice   # vocals stay clear over the filtered intro
m = Pedalboard([HighpassFilter(30), Compressor(threshold_db=-10, ratio=3, attack_ms=5, release_ms=80),
                HighShelfFilter(9000, -2), Limiter(threshold_db=-1.0)])(m.T.copy().astype(np.float32), SR).T
end = int((s.t(BARS) + 1.5) * SR)
m = m[:end]
# 4x oversampled soft clip so true peaks stay under ~-1 dBTP
up = np.stack([librosa.resample(m[:, c], orig_sr=SR, target_sr=SR * 4) for c in range(2)], 1)
up = up / np.abs(up).max() * 1.6
up = np.tanh(up) * 0.85
m = np.stack([librosa.resample(up[:, c], orig_sr=SR * 4, target_sr=SR) for c in range(2)], 1).astype(np.float32)
m[-int(s.t(4) * SR):] *= np.linspace(1, 0, int(s.t(4) * SR))[:, None]
sf.write(sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/music/song3.wav', m, SR)
print('done', round(len(m) / SR, 1), 's at', BPM, 'BPM')
