"""Tiny music engine: GM soundfont parts via fluidsynth + numpy drums/808 + pedalboard FX."""
import numpy as np, pretty_midi, subprocess, soundfile as sf, os, tempfile
from pedalboard import Pedalboard, Reverb, Compressor, Distortion, LowpassFilter, HighpassFilter, Chorus, Gain, Limiter, Delay

SR = 44100
SF2 = '/usr/share/sounds/sf2/FluidR3_GM.sf2'
NOTE = {n: i for i, n in enumerate('C C# D D# E F F# G G# A A# B'.split())}
NOTE.update({'Db': 1, 'Eb': 3, 'Gb': 6, 'Ab': 8, 'Bb': 10})


def midi(name):  # 'C4' -> 60
    p, o = name[:-1], int(name[-1])
    return 12 * (o + 1) + NOTE[p]


class Song:
    def __init__(self, bpm, bars):
        self.bpm, self.bars = bpm, bars
        self.beat = 60 / bpm
        self.n = int(bars * 4 * self.beat * SR) + SR * 4
        self.parts = {}

    def t(self, bar, beat=0):
        return (bar * 4 + beat) * self.beat

    def gm(self, name, program, notes, vel=90):
        """notes: list of (start_sec, dur_sec, pitch, vel?) rendered with fluidsynth."""
        pm = pretty_midi.PrettyMIDI(initial_tempo=self.bpm)
        ins = pretty_midi.Instrument(program=program)
        for nt in notes:
            s, d, p = nt[:3]
            v = nt[3] if len(nt) > 3 else vel
            ins.notes.append(pretty_midi.Note(velocity=int(v), pitch=int(p), start=s, end=s + d))
        pm.instruments.append(ins)
        with tempfile.TemporaryDirectory() as td:
            mp, wp = os.path.join(td, 'a.mid'), os.path.join(td, 'a.wav')
            pm.write(mp)
            subprocess.run(['fluidsynth', '-ni', '-g', '0.8', '-r', str(SR), '-F', wp, SF2, mp],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            a, _ = sf.read(wp, dtype='float32')
        return self.add(name, a)

    def add(self, name, a, at=0.0):
        if a.ndim == 1:
            a = np.stack([a, a], 1)
        buf = self.parts.setdefault(name, np.zeros((self.n, 2), np.float32))
        i = int(at * SR)
        m = min(len(a), self.n - i)
        if m > 0:
            buf[i:i + m] += a[:m]
        return buf

    def fx(self, name, board):
        self.parts[name] = board(self.parts[name].T.copy(), SR).T

    def gain(self, name, db):
        self.parts[name] *= 10 ** (db / 20)

    def mix(self):
        return sum(self.parts.values())


# ---------- synthesized one-shots ----------

def env(n, a=0.002, d=0.3, curve=4.0):
    t = np.arange(n) / SR
    e = np.minimum(t / a, 1.0) * np.exp(-curve * t / max(d, 1e-3))
    return e


def bass808(freq, dur, glide_from=None, glide_t=0.08, drive=2.5, decay=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = np.full(n, freq, float)
    if glide_from:
        g = np.minimum(t / glide_t, 1)
        f = glide_from * (freq / glide_from) ** g
    # punchy pitch drop at the head
    f = f * (1 + 1.5 * np.exp(-t * 60))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph)
    e = np.minimum(t / 0.003, 1) * (np.exp(-t / (decay or dur * 0.9)))
    e *= np.clip((dur - t) / 0.03, 0, 1)
    x = np.tanh(drive * x * e) / np.tanh(drive)
    return x.astype(np.float32)


def kick(dur=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 45 + 120 * np.exp(-t * 35)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    click = np.random.randn(n) * np.exp(-t * 400) * 0.3
    return np.tanh(2 * (x + click)).astype(np.float32)


def clap(dur=0.4):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = np.random.randn(n)
    e = np.zeros(n)
    for off in (0, 0.010, 0.021, 0.033):
        tt = np.clip(t - off, 0, None)
        e += (t >= off) * np.exp(-tt * 45) * 0.6
    e += np.exp(-t * 9) * 0.35
    x = noise * e
    x = HighpassFilter(900)(np.stack([x, x]).astype(np.float32), SR)[0]
    return (x / np.abs(x).max()).astype(np.float32)


def hat(dur=0.06, open_=False):
    n = int((0.35 if open_ else dur) * SR); t = np.arange(n) / SR
    x = np.random.randn(n) * np.exp(-t * (9 if open_ else 70))
    x = HighpassFilter(7000)(np.stack([x, x]).astype(np.float32), SR)[0]
    return (x / np.abs(x).max()).astype(np.float32)


def cowbell(freq=1.0, dur=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    sq = lambda f: np.sign(np.sin(2 * np.pi * f * freq * t))
    x = (sq(587) + sq(845)) * np.exp(-t * 11)
    b = Pedalboard([HighpassFilter(500), LowpassFilter(3500)])
    x = b(np.stack([x, x]).astype(np.float32), SR)[0]
    return (x / np.abs(x).max()).astype(np.float32)


def slowed(a, factor):
    """Classic 'slowed' = resample: tempo and pitch drop together."""
    import librosa
    return np.stack([librosa.resample(a[:, c], orig_sr=SR, target_sr=int(SR / factor)) for c in range(2)], 1)
