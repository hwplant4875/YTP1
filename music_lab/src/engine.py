"""Small numpy synth/drum engine for slowed-phonk style tracks.

Everything is rendered offline at SR into float32 stereo buffers.
Times are in beats; a Song converts beats to samples.
"""
import numpy as np
import scipy.signal as ss

SR = 44100
rng = np.random.default_rng(7)


def mtof(m):
    return 440.0 * 2 ** ((np.asarray(m, dtype=float) - 69) / 12)


NOTE = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
NOTE.update({"Db": 1, "Eb": 3, "Gb": 6, "Ab": 8, "Bb": 10})


def n(name):
    """'E3' -> midi."""
    p, o = name[:-1], int(name[-1])
    return 12 * (o + 1) + NOTE[p]


# ---------------------------------------------------------------- helpers
def adsr(length, a=0.005, d=0.1, s=0.7, r=0.1, sr=SR):
    """Envelope of `length` seconds (gate), plus release tail."""
    na, nd, nr = int(a * sr) + 1, int(d * sr) + 1, int(r * sr) + 1
    ng = max(int(length * sr), 1)
    env = np.concatenate([np.linspace(0, 1, na), np.linspace(1, s, nd), np.full(max(ng - na - nd, 0), s)])[:ng]
    last = env[-1] if len(env) else 0
    return np.concatenate([env, np.linspace(last, 0, nr)])


def lp(x, fc, q=0.707, kind="lowpass"):
    fc = float(np.clip(fc, 20, SR / 2 - 100))
    if kind in ("lowpass", "highpass"):
        sos = ss.butter(2, fc, btype=kind, fs=SR, output="sos")
    else:
        sos = ss.butter(2, [fc / 1.4, fc * 1.4], btype="bandpass", fs=SR, output="sos")
    return ss.sosfilt(sos, x, axis=-1)


def moving_lp(x, cutoff_curve, block=128):
    """Time-varying 2-pole lowpass (cutoff array per sample), blockwise biquad."""
    cutoff_curve = np.broadcast_to(np.asarray(cutoff_curve, dtype=float), x.shape)
    if np.ptp(cutoff_curve) < 1e-6:
        return lp(x, cutoff_curve[0])
    y = np.zeros_like(x)
    z = np.zeros(2)
    q = 0.707
    for i in range(0, len(x), block):
        fc = min(max(float(cutoff_curve[i]), 30.0), SR / 2 - 200)
        w = 2 * np.pi * fc / SR
        al, cw = np.sin(w) / (2 * q), np.cos(w)
        a0 = 1 + al
        b = np.array([(1 - cw) / 2, 1 - cw, (1 - cw) / 2]) / a0
        a = np.array([1, -2 * cw / a0, (1 - al) / a0])
        y[i:i + block], z = ss.lfilter(b, a, x[i:i + block], zi=z)
    return y


def saw_bl(freq_curve):
    """Band-limited-ish saw from a per-sample frequency curve (polyBLEP)."""
    dt = freq_curve / SR
    ph = np.cumsum(dt) % 1.0
    y = 2 * ph - 1
    # polyBLEP
    t = ph
    m1 = t < dt
    tt = t[m1] / dt[m1]
    y[m1] -= tt + tt - tt * tt - 1
    m2 = t > 1 - dt
    tt = (t[m2] - 1) / dt[m2]
    y[m2] -= tt * tt + tt + tt + 1
    return y


def sat(x, drive=2.0):
    return np.tanh(drive * x) / np.tanh(drive)


def pan(mono, p=0.0):
    l, r = np.cos((p + 1) * np.pi / 4), np.sin((p + 1) * np.pi / 4)
    return np.stack([mono * l, mono * r]) * np.sqrt(2)


# ---------------------------------------------------------------- instruments
import functools


def cached(fn):
    """Memoise renders of identical notes (args must be hashable)."""
    c = functools.lru_cache(maxsize=4096)(lambda *a, **k: fn(*a, **k))

    @functools.wraps(fn)
    def w(*a, **k):
        a = tuple(round(v, 6) if isinstance(v, float) else v for v in a)
        k = {kk: (round(v, 6) if isinstance(v, float) else v) for kk, v in k.items()}
        return c(*a, **k)
    return w


@cached
def kick(dur=0.6, f0=48, punch=170, drive=3.0):
    t = np.arange(int(dur * SR)) / SR
    f = f0 + (punch - f0) * np.exp(-t * 38)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 5.5)
    click = lp(rng.standard_normal(len(t)), 5000) * np.exp(-t * 300) * 0.4
    return sat(body + click, drive) * 0.9


@cached
def clap(dur=0.5, tone=1300):
    t = np.arange(int(dur * SR)) / SR
    noise = rng.standard_normal(len(t))
    env = np.zeros_like(t)
    for off in (0.0, 0.011, 0.023):
        k = t >= off
        env[k] += np.exp(-(t[k] - off) * 140) * (0.8 if off < 0.02 else 1.0)
    k = t >= 0.03
    env[k] += np.exp(-(t[k] - 0.03) * 16) * 0.9
    x = lp(noise, tone, kind="bandpass") * env * 3
    return sat(x, 1.5) * 0.8


@cached
def snare(dur=0.45):
    t = np.arange(int(dur * SR)) / SR
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 25)
    nz = lp(lp(rng.standard_normal(len(t)), 9000), 900, kind="highpass") * np.exp(-t * 14)
    return sat(tone * 0.6 + nz * 0.9, 1.8) * 0.75


@cached
def hat(dur=0.07, open_=False):
    if open_:
        dur = 0.35
    t = np.arange(int(dur * SR)) / SR
    nz = rng.standard_normal(len(t))
    # metallic: sum of square-ish partials
    met = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (317, 421, 553, 714, 893, 1105)) / 6
    x = lp(nz * 0.6 + met * 0.5, 7000, kind="highpass")
    env = np.exp(-t * (9 if open_ else 70))
    return x * env * 0.35


@cached
def cowbell(dur=0.5, f=540):
    t = np.arange(int(dur * SR)) / SR
    x = (np.sign(np.sin(2 * np.pi * f * t)) + np.sign(np.sin(2 * np.pi * f * 1.48 * t))) * 0.5
    x = lp(x, 1100, kind="bandpass")
    return x * (np.exp(-t * 9) * 0.8 + np.exp(-t * 40) * 0.6) * 0.6


def bass808(notes, total_len, slide=0.06, drive=2.6, decay=1.1):
    """notes: list of (start_s, dur_s, midi, glide_from_prev bool). One mono voice."""
    y = np.zeros(total_len)
    for i, (st, du, m, glide) in enumerate(notes):
        a = int(st * SR)
        L = int((du + 0.15) * SR)
        t = np.arange(L) / SR
        f_target = mtof(m)
        if glide and i > 0:
            f_prev = mtof(notes[i - 1][2])
            ns = int(slide * 2.5 * SR)
            f = np.full(L, f_target)
            f[:ns] = f_prev * (f_target / f_prev) ** (np.linspace(0, 1, ns) ** 0.6)
            att = 0.003
        else:
            f = f_target * (1 + 0.9 * np.exp(-t * 60))  # little pitch punch
            att = 0.001
        ph = 2 * np.pi * np.cumsum(f) / SR
        env = np.minimum(1, t / att) * np.exp(-t / decay * 0.6)
        rel = np.ones(L)
        g = int(du * SR)
        rel[g:] = np.linspace(1, 0, L - g)
        x = (np.sin(ph) + 0.18 * np.sin(2 * ph)) * env * rel
        x = sat(x, drive)
        b = min(len(y), a + L)
        y[a:b] += x[: b - a]
    # tame the fizz, keep growl
    return lp(y, 2200) * 0.85


@cached
def supersaw(m, dur, voices=7, detune=0.18, cutoff=1800, a=0.4, r=1.2, bright_env=0.0):
    L = int((dur + r) * SR)
    out = np.zeros(L)
    f0 = mtof(m)
    for v in range(voices):
        cents = (v - (voices - 1) / 2) / ((voices - 1) / 2) * detune * 100
        f = np.full(L, f0 * 2 ** (cents / 1200))
        out += saw_bl(f) * (1.0 if v == voices // 2 else 0.7)
    env = adsr(dur, a=a, d=0.3, s=0.85, r=r)[:L]
    out = out[: len(env)] * env
    cut = cutoff * (1 + bright_env * env)
    return moving_lp(out, cut) / voices * 1.6


@cached
def pluck(m, dur, cutoff=3200, decay=0.35, detune=0.07):
    L = int((dur + 0.6) * SR)
    t = np.arange(L) / SR
    f0 = mtof(m)
    x = saw_bl(np.full(L, f0 * 2 ** (detune / 12))) + saw_bl(np.full(L, f0 * 2 ** (-detune / 12))) + 0.5 * np.sin(2 * np.pi * f0 / 2 * t)
    env = np.exp(-t / decay)
    cut = 250 + cutoff * np.exp(-t / (decay * 0.5))
    return moving_lp(x * env, cut) * 0.5


@cached
def bell(m, dur, ratio=3.5, index=2.2, decay=1.6):
    L = int((dur + decay * 1.5) * SR)
    t = np.arange(L) / SR
    fc = mtof(m)
    I = index * np.exp(-t * 2.5) + 0.3
    mod = np.sin(2 * np.pi * fc * ratio * t) * I
    x = np.sin(2 * np.pi * fc * t + mod) * np.exp(-t / decay)
    x += 0.25 * np.sin(2 * np.pi * fc * 2 * t) * np.exp(-t / (decay * 0.4))
    return x * np.minimum(1, t / 0.002) * 0.45


VOWELS = {  # formant freqs/bw (soprano-ish)
    "a": [(800, 80), (1150, 90), (2900, 120)],
    "o": [(450, 70), (800, 80), (2830, 100)],
    "u": [(325, 50), (700, 60), (2530, 170)],
    "e": [(400, 60), (1600, 80), (2700, 120)],
}


@cached
def voice(m, dur, vowel="a", vibrato=5.2, a=0.25, r=0.6, breath=0.15):
    """Formant 'choir/vocal chop' voice."""
    L = int((dur + r) * SR)
    t = np.arange(L) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * vibrato * t) * np.minimum(1, t / 0.6)
    src = 0
    for c in (-0.08, 0, 0.09):
        src = src + saw_bl(mtof(m) * 2 ** (c / 12) * vib)
    src = src / 3 + breath * rng.standard_normal(L)
    y = np.zeros(L)
    for (f, bw), g in zip(VOWELS[vowel], (1.0, 0.6, 0.25)):
        b, aa = ss.iirpeak(f, f / bw, fs=SR)
        y += ss.lfilter(b, aa, src) * g
    env = adsr(dur, a=a, d=0.2, s=0.9, r=r)[:L]
    return y * env * 0.5


# ---------------------------------------------------------------- song container
class Song:
    def __init__(self, bpm, bars, beats_per_bar=4):
        self.bpm = bpm
        self.spb = 60.0 / bpm
        self.total = int((bars * beats_per_bar + 8) * self.spb * SR)
        self.tracks = {}

    def s(self, beat):
        return beat * self.spb

    def bus(self, name):
        if name not in self.tracks:
            self.tracks[name] = np.zeros((2, self.total))
        return self.tracks[name]

    def add(self, name, beat, mono_or_stereo, gain=1.0, p=0.0):
        x = mono_or_stereo
        if x.ndim == 1:
            x = pan(x, p)
        a = int(self.s(beat) * SR)
        if a >= self.total:
            return
        b = min(self.total, a + x.shape[1])
        self.bus(name)[:, a:b] += x[:, : b - a] * gain


# ---------------------------------------------------------------- sampled instruments via sfizz_render
SFIZZ = r"C:\Users\hw549\Downloads\YTP1\_downloads\sfizz\x\bin\Release\sfizz_render.exe"
SAMPLES = r"C:\Users\hw549\Downloads\YTP1\_samples"


def sfz_render(sfz, notes, bpm, tmpdir, tag, cc=None):
    """notes: list of (beat, dur_beats, midi, velocity). Returns stereo float array at SR."""
    import mido, os, subprocess, soundfile as sf
    os.makedirs(tmpdir, exist_ok=True)
    mid = mido.MidiFile(ticks_per_beat=480)
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm)))
    ev = []
    for (cn, val) in (cc or []):
        ev.append((0, 0, mido.Message("control_change", control=cn, value=val)))
    for b, d, m, v in notes:
        ev.append((int(b * 480), 1, mido.Message("note_on", note=int(m), velocity=int(v))))
        ev.append((int((b + d) * 480), 0, mido.Message("note_off", note=int(m), velocity=0)))
    ev.sort(key=lambda e: (e[0], e[1]))
    last = 0
    for t, _, msg in ev:
        tr.append(msg.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=480 * 8))
    mpath = os.path.join(tmpdir, tag + ".mid")
    wpath = os.path.join(tmpdir, tag + ".wav")
    mid.save(mpath)
    subprocess.run([SFIZZ, "--sfz", os.path.join(SAMPLES, sfz), "--midi", mpath, "--wav", wpath, "-s", str(SR), "--use-eot"],
                   check=True, capture_output=True)
    x, sr = sf.read(wpath, always_2d=True)
    assert sr == SR
    return x.T.astype(np.float64)
