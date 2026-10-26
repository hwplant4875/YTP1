"""solo_sampler.py - expressive solo violin / cello sample player (numpy only).

    from solo_sampler import render
    audio = render(notes, 'violin', sr=48000)          # -> float32 array, shape (n_samples, 2)

notes: list of dicts
    start_s  (float)  note start in seconds
    dur_s    (float)  written duration in seconds
    midi     (float)  pitch, fractional allowed (69.0 = A4)
    vel      (0-127)  dynamic; drives both timbre (pp/mf/ff layer crossfade) and loudness
    legato   (bool)   True = slur INTO this note from the previous note (no new bow attack)
  optional per-note keys
    art      'sustain' (default) | 'short' (spiccato/staccato samples, if the manifest has them)
    vib      vibrato amount multiplier (default 1.0; 0 = no added vibrato)
    swell    0..1 crescendo-diminuendo amount for long notes (default: auto for notes > 1.1 s)
    dyn_curve list of (time_fraction, vel) points overriding vel over the note (e.g. crescendo)
    glide_ms portamento time into this legato note (default from preset 'portamento')
    release_s release time override
instrument: 'violin' | 'cello', optionally with a source suffix: 'violin:iowa_mis_2012',
            'violin:vsco2ce', 'cello:iowa_mis_2012', 'cello:philharmonia'.

Design notes
  * Samples are pre-trimmed 48 kHz 24-bit WAVs listed in lib/solo_manifest.json with their
    *measured* pitch (pyin), attack ('speak') offset, sustain level and crossfade loop points.
  * Pitch: nearest sampled pitch (<= 2 semitones shift preferred), varispeed resampling with
    cubic Hermite interpolation; the same varispeed path renders vibrato and portamento.
  * Dynamics: equal-power crossfade between the two dynamic layers bracketing the note's
    dynamic value (which may move over time for swells), plus a loudness curve.
  * Legato: the incoming note starts *after* its sample's bow attack and is equal-power
    crossfaded (30-80 ms) with the outgoing note; both notes bend toward each other (each half
    the interval) for a short slide, so no gap and no re-attack.
  * Release: phrase-final notes splice into the sample's own recorded bow-release / string ring
    (natural_release) or fall back to a raised-cosine fade.
"""
import json
import os
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MANIFEST = os.path.join(os.path.dirname(HERE), 'lib', 'solo_manifest.json')
LIB_SR = 48000

PRESETS = {
    'violin': dict(
        strings=[55, 62, 69, 76],         # open strings G3 D4 A4 E5
        max_shift=2.0,
        vib_rate=5.7, vib_depth=16.0,     # cents (peak) of *added* vibrato at full development
        vib_delay=0.16, vib_fade=0.40,
        portamento=0.35,                  # 0..1 tendency to slide on legato intervals
        xfade_min=0.030, xfade_max=0.080,
        legato_offset_ms=70.0,            # read legato heads this far past the bow attack
        release_short=0.07, release_long=0.30,
        gain_db=0.0, body=0.7,
    ),
    'cello': dict(
        strings=[36, 43, 50, 57],         # C2 G2 D3 A3
        max_shift=2.0,
        vib_rate=5.3, vib_depth=15.0,
        vib_delay=0.18, vib_fade=0.45,
        portamento=0.45,
        xfade_min=0.035, xfade_max=0.085,
        legato_offset_ms=80.0,
        release_short=0.08, release_long=0.38,
        gain_db=0.0, body=0.8,
    ),
}

_BANKS = {}
_AUDIO = {}


# ----------------------------------------------------------------------------- utilities
def _load_audio(path):
    a = _AUDIO.get(path)
    if a is None:
        y, s = sf.read(path, always_2d=True, dtype='float32')
        if s != LIB_SR:
            raise ValueError(f'{path}: expected {LIB_SR} Hz, got {s}')
        y = y.T
        if y.shape[0] == 1:
            y = np.vstack([y, y])
        a = np.ascontiguousarray(y[:2])
        _AUDIO[path] = a
    return a


def _eqp(n, rising=True):
    t = np.linspace(0.0, 1.0, max(n, 1), dtype=np.float64)
    c = np.sin(0.5 * np.pi * t)
    return c if rising else c[::-1]


def _smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def _db(x):
    return 10.0 ** (np.asarray(x) / 20.0)


def varispeed(x, pos):
    """Cubic-Hermite read of x (ch, N) at fractional positions pos (M,) -> (ch, M).
    Positions outside [0, N-1] read as silence."""
    n = x.shape[1]
    i = np.floor(pos).astype(np.int64)
    f = (pos - i).astype(np.float32)
    xp = np.pad(x, ((0, 0), (2, 3)))
    i2 = np.clip(i + 2, 1, n + 3)  # index into padded
    ym1 = xp[:, np.clip(i2 - 1, 0, n + 4)]
    y0 = xp[:, i2]
    y1 = xp[:, np.clip(i2 + 1, 0, n + 4)]
    y2 = xp[:, np.clip(i2 + 2, 0, n + 4)]
    c0 = y0
    c1 = 0.5 * (y1 - ym1)
    c2 = ym1 - 2.5 * y0 + 2.0 * y1 - 0.5 * y2
    c3 = 0.5 * (y2 - ym1) + 1.5 * (y0 - y1)
    out = ((c3 * f + c2) * f + c1) * f + c0
    out[:, (pos < 0) | (pos > n - 1)] = 0.0
    return out


def _extend_with_loops(x, loop_start, loop_end, needed, xf_s=0.12):
    """Crossfade-loop x between loop_start..loop_end until it is at least `needed` long."""
    if needed <= x.shape[1] or loop_start is None or loop_end is None:
        return x
    xf = int(xf_s * LIB_SR)
    L = loop_end - loop_start
    if L < 2 * xf:
        xf = max(64, L // 3)
    seg = x[:, loop_start:loop_end]
    out = [x[:, :loop_end - xf]]
    tail = x[:, loop_end - xf:loop_end]
    total = loop_end - xf
    fo = _eqp(xf, False).astype(np.float32)
    fi = _eqp(xf, True).astype(np.float32)
    while total < needed + xf:
        out.append(tail * fo + seg[:, :xf] * fi)
        out.append(seg[:, xf:L - xf])
        tail = seg[:, L - xf:]
        total += xf + (L - 2 * xf)
    out.append(tail * np.linspace(1, 0, tail.shape[1], dtype=np.float32))
    return np.concatenate(out, axis=1)


# ----------------------------------------------------------------------------- sample bank
class Bank:
    def __init__(self, instrument, source=None, manifest=None):
        man = json.load(open(manifest or DEFAULT_MANIFEST))
        self.inst = instrument
        self.preset = dict(PRESETS[instrument])
        sec = man[instrument]
        self.source = source or man.get('default_source', {}).get(instrument)
        def pick(lst, src):
            return [e for e in lst if (src is None or e['source'] == src)]
        self.sustain = pick(sec.get('sustain', []), self.source)
        if not self.sustain:
            raise ValueError(f'no sustain samples for {instrument}:{self.source}')
        short_src = man.get('default_short_source', {}).get(instrument, self.source)
        self.short = pick(sec.get('short', []), short_src) or pick(sec.get('short', []), None)
        self.levels = sorted({e['dyn_level'] for e in self.sustain})
        self.short_levels = sorted({e['dyn_level'] for e in self.short}) if self.short else []
        ov = man.get('preset_overrides', {}).get(f'{instrument}:{self.source}', {})
        self.preset.update(ov)

    def choose(self, entries, midi, level, rng, avoid=None, steady=False):
        """Nearest-pitch sample within one dynamic layer with natural-string preference
        and round-robin among near-equal candidates. steady=True (long notes): skip warbling sustains
        (am_std_db > 2.2) when a steady one is within max_shift."""
        cands = [e for e in entries if e['dyn_level'] == level]
        if steady:
            ok = [e for e in cands if (e.get('am_std_db') or 0) <= 2.2 and abs(e['midi'] - midi) <= self.preset['max_shift']]
            if ok:
                cands = ok
        strings = self.preset['strings']
        def natural_string(m):
            ok = [s for s in strings if s <= m + 0.5]
            return ok[-1] if ok else strings[0]
        ns = natural_string(midi)
        scored = []
        for e in cands:
            d = abs(e['midi'] - midi)
            sc = d
            if d > self.preset['max_shift']:
                sc += 4.0 * (d - self.preset['max_shift'])
            os_ = e.get('open_string_midi')
            if os_ is not None and os_ != ns:
                sc += 0.35 * min(2, abs(strings.index(os_) - strings.index(ns)) if os_ in strings else 1)
            if avoid is not None and e['file'] == avoid:
                sc += 0.25
            am = e.get('am_std_db')
            if am is not None and am > 1.5:          # prefer steady (non-warbling) sustains
                sc += 0.3 * (am - 1.5)
            scored.append((sc, e))
        scored.sort(key=lambda t: t[0])
        best = scored[0][0]
        near = [e for sc, e in scored if sc <= best + 0.3]
        return near[int(rng.integers(len(near)))]


def _get_bank(instrument, manifest=None):
    key = (instrument, manifest)
    if key not in _BANKS:
        inst, _, src = instrument.partition(':')
        _BANKS[key] = Bank(inst, src or None, manifest)
    return _BANKS[key]


# ----------------------------------------------------------------------------- note planning
def _vel_to_level(v):
    return float(np.clip(0.04 + 0.94 * (v / 127.0), 0.0, 1.0))


def _level_to_gain_db(d):
    # d=1 -> 0 dB, d=0.55 -> ~ -8 dB, d=0.15 -> ~ -19 dB
    return -26.0 * (1.0 - d) ** 1.35


def _switch_weights(levels, d, hop_s, xf_s=0.25):
    """One dynamic layer at a time (nearest level, with hysteresis); switching between layers
    uses a short equal-power crossfade.  Avoids the comb/beating that comes from summing two
    differently-phased recordings of the same pitch for a long time."""
    d = np.atleast_1d(d)
    lv = np.asarray(levels)
    W = np.zeros((len(lv), len(d)))
    if len(lv) == 1:
        W[0] = 1.0
        return W
    cur = int(np.argmin(np.abs(lv - d[0])))
    idx = np.empty(len(d), int)
    for t, v in enumerate(d):
        j = int(np.argmin(np.abs(lv - v)))
        if j != cur:
            mid = 0.5 * (lv[j] + lv[cur])
            if abs(v - mid) > 0.04:      # hysteresis
                cur = j
        idx[t] = cur
    onehot = np.zeros_like(W)
    onehot[idx, np.arange(len(d))] = 1.0
    k = max(1, int(xf_s / hop_s))
    if k > 1:
        ker = np.ones(k) / k
        for j in range(len(lv)):
            onehot[j] = np.convolve(np.pad(onehot[j], (k // 2, k - 1 - k // 2), mode='edge'), ker, mode='valid')
    return np.sqrt(np.clip(onehot, 0, 1))


def _layer_weights(levels, d):
    """Equal-power weights over sorted layer levels for dynamic value(s) d (array)."""
    d = np.atleast_1d(d)
    W = np.zeros((len(levels), len(d)))
    if len(levels) == 1:
        W[0] = 1.0
        return W
    lv = np.asarray(levels)
    dd = np.clip(d, lv[0], lv[-1])
    k = np.clip(np.searchsorted(lv, dd, side='right') - 1, 0, len(lv) - 2)
    t = (dd - lv[k]) / (lv[k + 1] - lv[k])
    for j in range(len(lv) - 1):
        m = k == j
        W[j, m] += np.cos(0.5 * np.pi * t[m])
        W[j + 1, m] += np.sin(0.5 * np.pi * t[m])
    return W


def _group_phrases(notes):
    order = sorted(range(len(notes)), key=lambda i: notes[i]['start_s'])
    prev_of = {}
    taken = set()
    last_end = []
    for idx in order:
        n = notes[idx]
        if n.get('legato'):
            # most recent earlier note that ends near this start and is not yet linked forward
            best = None
            for j in last_end:
                pj = notes[j]
                if j in taken:
                    continue
                end = pj['start_s'] + pj['dur_s']
                if pj['start_s'] < n['start_s'] - 1e-4 and end >= n['start_s'] - 0.06:
                    if best is None or pj['start_s'] > notes[best]['start_s']:
                        best = j
            if best is not None:
                prev_of[idx] = best
                taken.add(best)
        last_end.append(idx)
    next_of = {p: i for i, p in prev_of.items()}
    return prev_of, next_of


# ----------------------------------------------------------------------------- rendering
def _merge_repeated(notes):
    """Slurred repeated pitches (legato=True, same midi, touching) are one sustained bow
    stream with bow changes: merge them so the sample/vibrato continues (no same-pitch
    crossfade interference) and mark the bow-change times."""
    notes = sorted(notes, key=lambda n: n['start_s'])
    out = []
    for n in notes:
        if out and n.get('legato') and abs(float(n['midi']) - float(out[-1]['midi'])) < 0.05:
            p = out[-1]
            p_end = p['start_s'] + p['dur_s']
            if p_end >= n['start_s'] - 0.06 and n['start_s'] > p['start_s']:
                p.setdefault('_bow', []).append(n['start_s'] - p['start_s'])
                p.setdefault('_vpts', [(0.0, p.get('vel', 90))]).append((n['start_s'] - p['start_s'], n.get('vel', 90)))
                p['dur_s'] = n['start_s'] + n['dur_s'] - p['start_s']
                for k in ('swell', 'vib', 'release_s'):
                    if k in n:
                        p[k] = n[k]
                continue
        out.append(dict(n))
    for p in out:
        if '_vpts' in p and 'dyn_curve' not in p:
            v = p['_vpts']
            dur = p['dur_s']
            pts = []
            for k, (t, vel) in enumerate(v):
                t1 = v[k + 1][0] if k + 1 < len(v) else dur
                pts += [(t / dur, vel), (max(t / dur, t1 / dur - 1e-3), vel)]
            p['dyn_curve'] = pts
            if p.get('swell') is None:
                p['swell'] = 0.0
    return out


_BODY_CACHE = {}


def _body_filter(y, inst, sr, amount=1.0):
    """Fixed bank of narrow body resonances.  Pitch vibrato rendered by resampling moves the
    recorded body formants together with the harmonics; this static filter restores the
    real-instrument behaviour where partials sweep across fixed resonances, giving the
    per-harmonic amplitude shimmer of natural vibrato (and some extra 'wood')."""
    from scipy.signal import sosfilt
    key = (inst, sr, amount)
    sos = _BODY_CACHE.get(key)
    if sos is None:
        r = np.random.default_rng(7 if inst == 'violin' else 11)
        # only where partials are dense (above the low harmonics) so per-note loudness stays
        # even while individual partials shimmer with the vibrato
        lo, hi = (2200.0, 9500.0) if inst == "violin" else (550.0, 5000.0)
        fcs = np.exp(np.sort(r.uniform(np.log(lo), np.log(hi), 26)))
        rows = []
        for fc in fcs:
            gdb = amount * r.uniform(2.0, 4.0)
            q = r.uniform(16.0, 32.0)
            A = 10 ** (gdb / 40)
            w0 = 2 * np.pi * fc / sr
            al = np.sin(w0) / (2 * q)
            b = np.array([1 + al * A, -2 * np.cos(w0), 1 - al * A])
            a = np.array([1 + al / A, -2 * np.cos(w0), 1 - al / A])
            rows.append(np.r_[b / a[0], a / a[0]])
        sos = np.array(rows)
        _BODY_CACHE[key] = sos
    z = sosfilt(sos, y, axis=0).astype(np.float32)
    # loudness-neutral
    g = np.sqrt((np.mean(y ** 2) + 1e-12) / (np.mean(z ** 2) + 1e-12))
    return z * np.float32(g)


def render(notes, instrument='violin', sr=48000, manifest=None, seed=0, humanize=1.0,
           natural_release=True, tail_s=1.0, body=None, return_info=False):
    """Render a monophonic (or loosely polyphonic) line. Returns float32 (n, 2).
    body: None = preset default (on for non-vibrato sources), True/False/float amount."""
    bank = _get_bank(instrument, manifest)
    P = bank.preset
    rng = np.random.default_rng(seed)
    if not notes:
        return np.zeros((0, 2), np.float32)
    notes = _merge_repeated([dict(n) for n in notes])
    prev_of, next_of = _group_phrases(notes)
    total_end = max(n['start_s'] + n['dur_s'] for n in notes) + tail_s + 0.6
    out = np.zeros((2, int(total_end * sr) + 1), np.float32)
    rate = LIB_SR / sr
    info = []
    last_file = None
    # pre-compute per-note transition parameters
    for i, n in enumerate(notes):
        n.setdefault('vel', 90)
        n.setdefault('legato', False)
        n['_hum_t'] = 0.0 if (i in prev_of) else float(np.clip(rng.normal(0, 0.006), -0.012, 0.012)) * humanize
        n['_detune'] = float(rng.normal(0, 2.0)) * humanize  # cents
        n['_gain_j'] = float(rng.normal(0, 0.6)) * humanize   # dB
    for i, n in enumerate(notes):
        p_i = prev_of.get(i)
        x_i = next_of.get(i)
        start = n['start_s'] + n['_hum_t']
        dur = max(0.03, n['dur_s'])
        end = n['start_s'] + dur
        target = float(n['midi'])
        art = n.get('art', 'sustain')
        use_short = art == 'short' and bank.short and p_i is None
        # transition geometry ---------------------------------------------------------
        def xfade_len(a, b):
            return float(np.clip(0.35 * min(a['dur_s'], b['dur_s']), P['xfade_min'], P['xfade_max']))
        xin = xfade_len(notes[p_i], n) if p_i is not None else 0.0
        xout = xfade_len(n, notes[x_i]) if x_i is not None else 0.0
        if x_i is not None:
            end = notes[x_i]['start_s']  # legato: this note lasts until the next one begins
        # dynamics curve ---------------------------------------------------------------
        d0 = _vel_to_level(n['vel'])
        rel = n.get('release_s')
        if rel is None:
            rel = P['release_short'] + (P['release_long'] - P['release_short']) * float(np.clip((dur - 0.15) / 1.2, 0, 1))
        seg_start = start - xin / 2 if p_i is not None else start
        will_splice = (natural_release and x_i is None and art != 'short' and dur >= 0.28)
        fade_len = rel * (2.2 if will_splice else 1.0)
        seg_end = end + (xout / 2 + 0.002 if x_i is not None else fade_len + 0.01)
        # pre-roll so the sample's "speak" point lands on the beat (non-legato only)
        n_ctrl_hop = 64
        if use_short:
            entries, levels = bank.short, bank.short_levels
        else:
            entries, levels = bank.sustain, bank.levels
        swell = n.get('swell')
        if swell is None:
            swell = 0.55 if (dur > 1.1 and x_i is None) else (0.3 if dur > 1.1 else 0.0)
        # build control-rate timeline relative to the note start
        pre = 0.0
        if p_i is None and not use_short:
            pre = 0.035
        t0 = seg_start - pre
        nseg = int(np.ceil((seg_end - t0) * sr)) + 1
        tc = np.arange(0, nseg + n_ctrl_hop, n_ctrl_hop) / sr + t0 - start  # time rel. to note start
        frac = np.clip(tc / max(dur, 1e-3), 0, 1)
        if 'dyn_curve' in n:
            pts = np.asarray(n['dyn_curve'], float)
            dcurve = np.interp(frac, pts[:, 0], [_vel_to_level(v) for v in pts[:, 1]])
        else:
            # messa di voce: start a little softer, bloom at ~65 %, relax at the end
            bloom = _smoothstep(frac / 0.65)
            relax = _smoothstep((frac - 0.65) / 0.35)
            dcurve = d0 - 0.28 * swell + 0.33 * swell * bloom - 0.12 * swell * relax
        if n.get('_bow') and 'dyn_curve' in n and n.get('swell'):
            bloom = _smoothstep(frac / 0.65)
            dcurve = dcurve - 0.2 * n['swell'] + 0.25 * n['swell'] * bloom
        dcurve = np.clip(dcurve, 0.0, 1.0)
        W = _switch_weights(levels, dcurve, n_ctrl_hop / sr)
        active = [j for j in range(len(levels)) if W[j].max() > 1e-3]
        # pitch curve (semitones relative to target) ---------------------------------
        pc = np.full(len(tc), n['_detune'] / 100.0)
        if p_i is not None:
            prev_m = float(notes[p_i]['midi'])
            iv = prev_m - target
            g = n.get('glide_ms')
            g = (0.022 + 0.09 * P['portamento'] * min(1.0, abs(iv) / 7.0)) if g is None else g / 1000.0
            if abs(iv) > 1e-3:
                # incoming note starts half-way and settles; slide centred on the crossfade
                k = _smoothstep((tc + xin / 2) / max(g + xin / 2, 1e-3))
                pc += 0.4 * iv * (1 - k)
        if x_i is not None:
            nxt = float(notes[x_i]['midi'])
            iv = nxt - target
            g = notes[x_i].get('glide_ms')
            g = (0.022 + 0.09 * P['portamento'] * min(1.0, abs(iv) / 7.0)) if g is None else g / 1000.0
            if abs(iv) > 1e-3:
                t_tr = end - start
                k = _smoothstep((tc - (t_tr - g)) / max(g + xout / 2, 1e-3))
                pc += 0.4 * iv * k
        vib_amt = float(n.get('vib', 1.0))
        vib_cents = np.zeros(len(tc))
        if vib_amt > 0 and dur > 0.22 and not use_short:
            delay = P['vib_delay'] * (0.6 if p_i is not None else 1.0)
            ramp = _smoothstep((tc - delay) / P['vib_fade'])
            rate_hz = P['vib_rate'] * (1 + 0.04 * rng.normal()) + 0.35 * (dcurve - 0.5)
            phase = 2 * np.pi * np.cumsum(rate_hz) * (n_ctrl_hop / sr) + rng.uniform(0, 2 * np.pi)
            depth = P['vib_depth'] * vib_amt * (0.75 + 0.45 * dcurve) * ramp
            # slow random depth wander, as players do
            depth *= 1 + 0.15 * np.sin(2 * np.pi * 0.7 * tc + rng.uniform(0, 6.3))
            vib_cents = depth * np.sin(phase)
            if dur < 0.45:
                vib_cents *= (dur - 0.22) / 0.23
            pc += vib_cents / 100.0
        # amplitude envelope (control rate) ------------------------------------------
        env = np.ones(len(tc))
        tt = tc + start - t0  # time since segment start
        if p_i is not None:
            env *= _eqp_curve(np.clip((tc + xin / 2) / max(xin, 1e-3), 0, 1), True)
        else:
            # fade-in at the read point (8 ms: we may start inside a bow attack)
            env *= _eqp_curve(tt / (0.003 if use_short else 0.008), True)
        for tb in n.get('_bow', []):
            # bow change inside a slurred repeated note: short dip then slight re-bite
            env *= 1 - 0.38 * np.exp(-((tc - tb + 0.012) / 0.022) ** 2)
            env *= 1 + 0.10 * np.exp(-((tc - tb - 0.045) / 0.04) ** 2)
        if p_i is not None and n.get('reartic'):
            # new syllable inside a slur: bow change at the note start (dip, then a little bite)
            env *= 1 - 0.5 * np.exp(-((tc + 0.010) / 0.018) ** 2)
            env *= 1 + 0.09 * np.exp(-((tc - 0.04) / 0.035) ** 2)
        if x_i is not None:
            t_tr = end - start
            env *= _eqp_curve(np.clip((tc - (t_tr - xout / 2)) / max(xout, 1e-3), 0, 1), False)
        # loudness from dynamics + vibrato-synchronous amplitude shimmer
        gdb = _level_to_gain_db(dcurve) + P['gain_db'] + n['_gain_j'] + 0.035 * vib_cents
        # render each active dynamic layer ---------------------------------------------
        ns_ = nseg
        tci = np.arange(ns_) / n_ctrl_hop
        pc_a = np.interp(tci, np.arange(len(pc)), pc)
        ratio = (2.0 ** (pc_a / 12.0)) * rate
        rel_flags = []
        acc = np.zeros((2, ns_), np.float32)
        chosen = []
        for j in active:
            e = bank.choose(entries, target, levels[j], rng, avoid=last_file, steady=dur >= 0.8)
            chosen.append(e)
            x = _load_audio(e['file'])
            shift = target - e['midi']
            r = ratio * (2.0 ** (shift / 12.0))
            # read start in the sample
            if p_i is not None:
                lg = e.get('legato_ms', e['attack_ms'] + P['legato_offset_ms'])
                read0 = (lg + rng.uniform(0, 30)) / 1000.0
                read0 = min(read0, max(0.0, e['release_start_s'] - 0.3))
            elif use_short:
                read0 = 0.0
            else:
                # align: speak point (e['speak_ms']) at note start; strong / short notes skip
                # part of a slow bow attack (more 'bite'), soft long notes keep the full swell
                spk = e['speak_ms'] / 1000.0
                lead = pre + 0.010
                soft = max(0.0, spk - lead)
                hard = max(soft, e['attack_ms'] / 1000.0 - 0.07)
                a = float(np.clip((n['vel'] - 55) / 55.0, 0, 1)) * (1.0 if dur < 1.0 else 0.4)
                read0 = soft + a * (hard - soft)
            pos = read0 * LIB_SR + np.concatenate([[0.0], np.cumsum(r[:-1])])
            if p_i is not None and xin > 0:
                # phase-align the incoming head with what is already sounding in the
                # crossfade window -> constructive sum, no cancellation dip
                nx = min(int(xin * sr), len(pos) - 1)
                i0w = int(round(t0 * sr))
                if nx > 16 and i0w >= 0 and i0w + nx <= out.shape[1]:
                    ref = out[:, i0w:i0w + nx].mean(axis=0)
                    if np.abs(ref).max() > 1e-6:
                        per = LIB_SR / (440.0 * 2 ** ((e['midi'] - 69) / 12))
                        fade_in = _eqp_curve(np.arange(nx) / nx, True)
                        best_d, best_c = 0.0, -np.inf
                        for dlt in np.arange(0.0, per, per / 24.0):
                            cand = varispeed(x, pos[:nx] + dlt).mean(axis=0) * fade_in
                            c = float(np.dot(cand, ref))
                            if c > best_c:
                                best_c, best_d = c, dlt
                        pos = pos + best_d
            need = int(pos[-1]) + 8
            usable_end = int((e['release_start_s'] - 0.05) * LIB_SR)
            xs = x
            if use_short:
                pass
            elif need > usable_end and e.get('loop_start') is not None:
                xs = _extend_with_loops(x[:, :e['loop_end']], e['loop_start'], e['loop_end'], need)
            elif need > x.shape[1]:
                xs = _extend_with_loops(x, int(0.45 * x.shape[1]), int(0.85 * x.shape[1]), need)
            y = varispeed(xs, pos)
            # natural release: splice into the recorded bow release of this sample
            if (natural_release and x_i is None and not use_short and dur >= 0.28
                    and e['release_start_s'] > 0.6):
                y = _splice_release(y, x, e, pos, r, start + dur - t0, sr, rel)
                rel_flags.append(True)
            w = np.interp(tci, np.arange(len(tc)), W[j])
            # per-sample normalisation: every layer is brought to a common sustain level
            acc += y * (w * _db(e.get('norm_gain_db', 0.0))).astype(np.float32)
        g = _db(np.interp(tci, np.arange(len(tc)), gdb))
        e_a = np.interp(tci, np.arange(len(tc)), env)
        # release fade (if no natural release splice, or as a safety tail)
        if x_i is None:
            t_rel0 = (start + dur - t0)
            tr = np.arange(ns_) / sr - t_rel0
            fade = np.where(tr <= 0, 1.0, np.cos(0.5 * np.pi * np.clip(tr / fade_len, 0, 1)) ** 2)
            e_a = e_a * fade
        acc *= (g * e_a).astype(np.float32)
        i0 = int(round(t0 * sr))
        a0 = max(0, -i0)
        i0c = max(0, i0)
        i1 = min(out.shape[1], i0c + ns_ - a0)
        out[:, i0c:i1] += acc[:, a0:a0 + (i1 - i0c)]
        last_file = chosen[0]['file'] if chosen else None
        info.append(dict(i=i, samples=[os.path.basename(c['file']) for c in chosen],
                         layers=[levels[j] for j in active], legato_in=p_i is not None,
                         legato_out=x_i is not None, short=bool(use_short)))
    use_body = body if body is not None else P.get('body', 0.0)
    if use_body:
        out = _body_filter(out.T, bank.inst, sr, float(use_body)).T
    # trim trailing silence
    nz = np.flatnonzero(np.abs(out).max(axis=0) > 1e-6)
    if len(nz):
        out = out[:, :nz[-1] + int(0.05 * sr)]
    res = np.ascontiguousarray(out.T.astype(np.float32))
    return (res, info) if return_info else res


def _eqp_curve(x, rising):
    c = np.sin(0.5 * np.pi * np.clip(x, 0, 1))
    return c if rising else np.cos(0.5 * np.pi * np.clip(x, 0, 1))


def _splice_release(y, x, e, pos, r, t_cut, sr, rel):
    """Crossfade (25 ms) from the played sustain into the sample's own recorded release,
    gain-matched, so the note ends with a real bow-off and string ring."""
    n = y.shape[1]
    c = int(t_cut * sr)
    if c <= 0 or c >= n - 10:
        return y
    xf = int(0.025 * sr)
    rs = int(max(0.0, e['release_start_s'] - 0.06) * LIB_SR)
    r_end = float(r[min(c, len(r) - 1)])
    m = n - c
    rpos = rs + np.arange(m) * r_end
    z = varispeed(x, rpos)
    a = y[:, max(0, c - int(0.06 * sr)):c]
    b = z[:, :int(0.06 * sr)]
    ga = np.sqrt(np.mean(a ** 2) + 1e-12)
    gb = np.sqrt(np.mean(b ** 2) + 1e-12)
    k = float(np.clip(ga / gb, 0.1, 10.0))
    z *= k
    out = y.copy()
    fo = np.ones(m, np.float32)
    fo[:xf] = np.cos(0.5 * np.pi * np.linspace(0, 1, xf))
    fo[xf:] = 0
    fi = np.sin(0.5 * np.pi * np.clip(np.arange(m) / xf, 0, 1)).astype(np.float32)
    out[:, c:] = y[:, c:] * fo + z * fi
    return out


def write(path, audio, sr=48000):
    sf.write(path, audio, sr, subtype='PCM_24')


if __name__ == '__main__':
    import sys
    print(__doc__)
    sys.exit(0)
