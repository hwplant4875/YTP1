"""Track 01 - original melodic 'slowed + reverb' phonk (E minor written, slowed x0.8).

Run: python -I track01.py <out_dir>
"""
import sys, os
import numpy as np
import pedalboard as pb
import soundfile as sf
from scipy.signal import resample_poly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *  # noqa
from mastering import master_ffmpeg

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)
VST = "C:/Program Files/Common Files/VST3/"

BPM = 125
SLOW = 0.8  # final speed/pitch factor  -> 100 BPM, ~-3.9 st
BARS = 60
song = Song(BPM, BARS)

# ---------------------------------------------------------------- harmony
#            Em                 C                 Am                B7
CHORDS = [["E3", "G3", "B3", "E4"], ["C3", "G3", "C4", "E4"], ["A2", "E3", "A3", "C4"], ["B2", "F#3", "A3", "D#4"]]
ROOTS808 = ["E2", "C2", "A1", "B1"]

MEL_A = [(0, .5, "B4"), (.5, .5, "E5"), (1, .5, "G5"), (1.5, 1, "F#5"), (2.5, .5, "E5"), (3, 1, "B4"),
         (4, .5, "C5"), (4.5, .5, "E5"), (5, .5, "G5"), (5.5, 1, "F#5"), (6.5, .5, "E5"), (7, 1, "G5"),
         (8, .5, "A4"), (8.5, .5, "C5"), (9, .5, "E5"), (9.5, 1, "D5"), (10.5, .5, "C5"), (11, 1, "B4"),
         (12, .5, "D#5"), (12.5, .5, "F#5"), (13, 1, "B5"), (14, .5, "A5"), (14.5, .5, "F#5"), (15, 1, "D#5")]
MEL_B = MEL_A[:18] + [(12, .5, "F#5"), (12.5, .5, "A5"), (13, 1.5, "B5"), (14.5, .5, "C6"), (15, 1, "B5")]
COW = [(0, "E5"), (.75, "E5"), (1.5, "G5"), (2.5, "E5"), (3, "D5"), (3.5, "B4")]  # cowbell riff per bar

SECTIONS = dict(intro=(0, 8), build=(8, 12), dropA=(12, 28), brk=(28, 36), dropB=(36, 52), outro=(52, 60))


def in_sec(bar, *names):
    return any(SECTIONS[k][0] <= bar < SECTIONS[k][1] for k in names)


# ---------------------------------------------------------------- write parts
spb = song.spb
for bar in range(BARS):
    b0 = bar * 4
    ci = bar % 4
    ch = CHORDS[ci]

    # pad + vocal 'ooh'
    if not in_sec(bar, "outro") or bar < 58:
        cut = 900 if in_sec(bar, "intro", "outro") else 2400
        for i, nn in enumerate(ch):
            song.add("pad", b0, supersaw(n(nn), 4 * spb, cutoff=cut, a=0.6, r=1.5), 0.14, p=(-0.4 + 0.27 * i))
    if in_sec(bar, "intro", "brk", "dropB", "outro"):
        top = ch[-1]
        song.add("vox", b0, voice(n(top) + 12, 4 * spb - 0.1, vowel="o" if bar % 2 else "u"), 0.12, p=0.15)
        song.add("vox", b0, voice(n(ch[1]) + 12, 4 * spb - 0.1, vowel="u"), 0.08, p=-0.25)

    # melody (bell), phrase = 4 bars
    if ci == 0 and not in_sec(bar, "build"):
        mel = MEL_B if in_sec(bar, "dropB") else MEL_A
        g = 0.34 if in_sec(bar, "dropA", "dropB") else 0.2
        for bt, du, nn in mel:
            song.add("bell", b0 + bt, bell(n(nn), du * spb), g, p=0.1)
            if in_sec(bar, "dropB"):  # doubled an octave down with a pluck
                song.add("lead", b0 + bt, pluck(n(nn) - 12, du * spb, cutoff=3000, decay=0.4), 0.24, p=-0.1)

    # arp plucks in drops
    if in_sec(bar, "dropA", "dropB", "build"):
        arp = [ch[1], ch[2], ch[3], ch[2]]
        for k in range(16):
            nn = n(arp[k % 4]) + (12 if k % 8 >= 4 else 0)
            song.add("arp", b0 + k * 0.25, pluck(nn, 0.25 * spb, cutoff=1800, decay=0.18), 0.10, p=(0.5 if k % 2 else -0.5))

    # drums
    drums = in_sec(bar, "dropA", "dropB")
    if drums:
        for kb in (0, 2.5) if bar % 2 == 0 else (0, 1.75, 2.5):
            song.add("kick", b0 + kb, kick(), 0.9)
        for cb in (1, 3):
            song.add("clap", b0 + cb, clap(), 0.55)
            song.add("clap", b0 + cb, snare(), 0.25)
    if drums or in_sec(bar, "build"):
        roll = (bar % 2 == 1)
        for k in range(8):
            song.add("hat", b0 + k * 0.5, hat(), 0.95 if k % 2 else 0.65, p=0.3)
        if roll:  # 16th -> 32nd triplet roll into the next bar
            for k in range(6):
                song.add("hat", b0 + 3 + k / 6, hat(0.04), 0.3, p=0.3)
        if bar % 4 == 3:
            song.add("hat", b0 + 2.5, hat(open_=True), 0.35, p=-0.2)
    if in_sec(bar, "build") and bar == SECTIONS["build"][1] - 1:
        for k in range(8):
            song.add("clap", b0 + k * 0.5, clap(), 0.2 + 0.05 * k)
    if in_sec(bar, "dropB"):
        for bt, nn in COW:
            song.add("cow", b0 + bt, cowbell(f=mtof(n(nn))), 0.16, p=-0.15)

# ---------------------------------------------------------------- sampled layers (sfizz)
TMP = os.path.join(OUT, "_stems")
rh, pno, strg = [], [], []
for bar in range(BARS):
    b0 = bar * 4
    ch = [n(x) for x in CHORDS[bar % 4]]
    if in_sec(bar, "dropA", "dropB", "build"):  # off-beat Rhodes stabs, mid register
        for st in (0.5, 1.5, 2.75, 3.5):
            for m in ch[1:]:
                rh.append((b0 + st, 0.4, m, 70 if st != 2.75 else 85))
    if in_sec(bar, "intro", "brk", "outro") and bar < 58:  # sad piano: chord + melody echo
        for m in ch:
            pno.append((b0, 3.9, m, 52))
        if bar % 4 == 0:
            for bt, du, nn in MEL_A:
                pno.append((b0 + bt, du, n(nn), 64))
    if in_sec(bar, "brk", "dropB"):
        for m in ch[1:]:
            strg.append((b0, 4.0, m + 12, 60))
rhodes = sfz_render(r"jlearman.jRhodes3c-master\jRhodes3c-looped-flac-sfz\_jRhodes-stereo-looped.sfz", rh, BPM, TMP, "rhodes")
piano = sfz_render(r"SalamanderGrandPiano-SFZ+FLAC-V3+20200602\SalamanderGrandPiano-V3+20200602.sfz", pno, BPM, TMP, "piano", cc=[(64, 0)])
strings = sfz_render(r"VirtualPlayingOrchestra\Virtual-Playing-Orchestra3\Strings\all-strings-SEC-sustain.sfz", strg, BPM, TMP, "strings")
for name, x, g in (("rhodes", rhodes, 0.5), ("piano", piano, 0.55), ("strings", strings, 0.35)):
    x = x / (np.abs(x).max() + 1e-9)
    L = min(song.total, x.shape[1])
    song.bus(name)[:, :L] += x[:, :L] * g

# 808 line
notes = []
for bar in range(BARS):
    if not in_sec(bar, "dropA", "dropB", "brk"):
        continue
    r = n(ROOTS808[bar % 4])
    b0 = bar * 4 * spb
    if in_sec(bar, "brk"):
        notes.append((b0, 3.8 * spb, r, False))
        continue
    notes += [(b0, 1.4 * spb, r, False), (b0 + 1.75 * spb, 0.6 * spb, r, False), (b0 + 2.5 * spb, 1.0 * spb, r, False)]
    if bar % 4 == 3:  # glide up an octave and back at the end of each phrase
        notes += [(b0 + 3.5 * spb, 0.5 * spb, r + 12, True)]
song.bus("808")[:] += pan(lp(bass808(notes, song.total, drive=4.5, decay=1.4), 30, kind="highpass")) * 0.3

# build riser + downlifter
t = np.arange(int(4 * 4 * spb * SR)) / SR
rise = lp(rng.standard_normal(len(t)), 600, kind="highpass") * (t / t[-1]) ** 2 * 0.25
song.add("fx", SECTIONS["build"][0] * 4, moving_lp(rise, 400 + 9000 * (t / t[-1]) ** 2), 1.0)
song.add("fx", SECTIONS["dropB"][0] * 4 - 8, moving_lp(rise, 400 + 9000 * (t / t[-1]) ** 2)[: int(8 * spb * SR)], 1.0)

# ---------------------------------------------------------------- mix
T = song.tracks
# sidechain envelope from kick + 808 onsets
sc = np.zeros(song.total)
for bar in range(BARS):
    if in_sec(bar, "dropA", "dropB"):
        for kb in (0, 1, 2, 3):
            a = int((bar * 4 + kb) * spb * SR)
            L = int(0.35 * SR)
            e = 1 - 0.32 * np.exp(-np.arange(L) / SR * 9)
            sc[a:a + L] = np.minimum(sc[a:a + L] if sc[a:a + L].any() else 1, e[: len(sc[a:a + L])])
sc[sc == 0] = 1
for k in ("pad", "vox", "arp", "bell", "lead", "cow", "rhodes", "strings"):
    if k in T:
        T[k] *= sc

dry = sum(T[k] for k in T)
wet_src = sum(T[k] * g for k, g in (("pad", .6), ("piano", .7), ("strings", .8), ("rhodes", .4), ("vox", .9), ("bell", .8), ("arp", .7), ("lead", .5), ("clap", .35), ("cow", .5)) if k in T)

mix = np.zeros_like(dry)
mix += dry
# vinyl + room tone
crackle = np.zeros(song.total)
idx = rng.integers(0, song.total, size=int(song.total / SR * 9))
crackle[idx] = rng.standard_normal(len(idx)) * 0.25
hiss = lp(rng.standard_normal(song.total), 5000) * 0.004
mix += pan(lp(crackle, 1500, kind="highpass") + hiss)

# ---------------------------------------------------------------- slowed (+ reverb)
def slow(x):
    # resample to more samples, play back at SR -> slower and lower
    return resample_poly(x, 5, 4, axis=-1).astype(np.float32)  # 1/0.8 = 5/4

mix_s = slow(mix)
wet_s = slow(wet_src)

verb = pb.load_plugin(VST + "ValhallaSupermassive.vst3")
verb.mix = 100.0
verb.mode = "Gemini"
verb.delay_ms = 220.0
verb.feedback = 72.0
verb.density = 60.0
verb.lowcut = 250.0
verb.highcut = 5000.0
verb.moddepth = 60.0
wet = verb(wet_s, SR)

chorus = pb.load_plugin(VST + "TAL-Chorus-LX.vst3/Contents/x86_64-win/TAL-Chorus-LX.vst3")
out = mix_s + wet * 0.45
out = chorus(out.astype(np.float32), SR) * 0.5 + out * 0.5

master = pb.Pedalboard([
    pb.HighpassFilter(28),
    pb.LowShelfFilter(cutoff_frequency_hz=60, gain_db=-1.0), pb.HighShelfFilter(cutoff_frequency_hz=6000, gain_db=3.5),
    pb.PeakFilter(cutoff_frequency_hz=2500, gain_db=2.0, q=0.8),
    pb.Compressor(threshold_db=-16, ratio=2.0, attack_ms=25, release_ms=200),
])
out = master(out.astype(np.float32), SR)

# fades + trim
L = out.shape[1]
end = int((BARS * 4 * spb / SLOW + 4) * SR)
out = out[:, :min(L, end)]
fi, fo = int(0.05 * SR), int(6 * SR)
out[:, :fi] *= np.linspace(0, 1, fi)
out[:, -fo:] *= np.linspace(1, 0, fo) ** 1.5

pre = os.path.join(OUT, "track01_premaster.wav")
sf.write(pre, (out / np.abs(out).max() * 0.5).T, SR, subtype="FLOAT")
master_ffmpeg(pre, os.path.join(OUT, "track01_slowed.wav"))
print("done", out.shape[1] / SR, "s, peak", np.abs(out).max())
