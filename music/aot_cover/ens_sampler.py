"""ens_sampler.py - sample-based renderer for the BACKING instruments (orchestra, choir, piano, rock band).

Uses /tmp/claude-0/aotmusic/lib/orch_manifest.json (built by orch_build_manifest.py).
Dependencies: numpy, soundfile, librosa (+ scipy.signal, a librosa dependency, for IIR filters / FFT convolution).

Main API
--------
render(notes, instrument, articulation, sr=48000, **opts) -> np.ndarray float32, shape (N, 2)
    notes: list of {start_s, dur_s, midi, vel}  (vel 1..127; if every vel <= 1.0 they are treated as 0..1)
           optional per-note keys: 'group' (mono voice group: a new note cuts the previous one in the same group),
           'detune_cents', 'gain_db', 'attack_s', 'release_s'
render_layers(notes, [(instrument, articulation, gain_db[, opts]), ...], sr) -> layered sections (e.g. SSO + VSCO strings)
drums_render(hits, sr=48000, mix='rock', ...) -> (N, 2)
    hits: list of {start_s, piece, vel}; pieces: see list_drum_pieces()
guitar_render(notes, articulation='palm_mute'|'sustain'|'staccato_bgg', sr, amp='high_gain', double=True) -> (N, 2)
power_chord(root_midi, start_s, dur_s, vel, intervals=(0, 7, 12), strum_s=0.006) -> notes (with string groups)
bass_render(notes, articulation='sustain', sr, drive=0.35) -> (N, 2)
amp_sim(mono, sr, preset='high_gain', cab='v30', seed=0) -> mono float32
list_instruments() / list_drum_pieces() -> coverage info

Level convention: one voice at vel 127 ~ -16 dBFS RMS (sustain body / first 300 ms for shorts) before pan law;
chords and layers add up, so mix with headroom. Output is DRY (no reverb) - add hall reverb at mix time.
"""
import json
import math
import os
import random
import weakref
import zlib
from collections import OrderedDict

import numpy as np
import soundfile as sf
import librosa
from scipy import signal as _sig

MANIFEST_PATH = '/tmp/claude-0/aotmusic/lib/orch_manifest.json'
REF_DB = -18.0   # per-voice RMS at vel 127 (sustain body); shorts: max-50ms RMS = REF_DB + 2

_M = None


def manifest():
    global _M
    if _M is None:
        with open(MANIFEST_PATH) as f:
            _M = json.load(f)
    return _M


# ---------------------------------------------------------------------------------------------
# caches
# ---------------------------------------------------------------------------------------------
class _LRU:
    def __init__(self, max_bytes):
        self.max = max_bytes
        self.d = OrderedDict()
        self.bytes = 0

    def get(self, k):
        v = self.d.get(k)
        if v is not None:
            self.d.move_to_end(k)
        return v

    def put(self, k, v):
        nb = sum(x.nbytes for x in v if isinstance(x, np.ndarray)) if isinstance(v, tuple) else v.nbytes
        if k in self.d:
            return
        self.d[k] = v
        self.bytes += nb
        while self.bytes > self.max and len(self.d) > 1:
            _, old = self.d.popitem(last=False)
            self.bytes -= sum(x.nbytes for x in old if isinstance(x, np.ndarray)) if isinstance(old, tuple) else old.nbytes


_RAW = _LRU(1.2e9)
_SHIFT = _LRU(2.0e9)


def clear_cache():
    global _RAW, _SHIFT, _CLICKS
    _RAW = _LRU(1.2e9)
    _SHIFT = _LRU(2.0e9)
    _CLICKS = None
    for c in ('_ALOOP', '_WINDB'):
        if c in globals():
            globals()[c].clear()


_CLICKS = None


def _click_map():
    global _CLICKS
    if _CLICKS is None:
        _CLICKS = {}
        for d in manifest()['instruments'].values():
            for e in d['articulations'].values():
                for s in e['samples']:
                    if s.get('click_times_s'):
                        _CLICKS[s['file']] = s['click_times_s']
    return _CLICKS


def _declick(y, sr, times):
    """replace +-2 ms around each spike by a 3 kHz low-passed copy (1 ms crossfades)."""
    lp = _sig.sosfiltfilt(_sig.butter(4, 3000, 'lp', fs=sr, output='sos'), y, axis=0).astype(np.float32)
    h, xf = int(0.002 * sr), max(1, int(0.001 * sr))
    for t in times:
        c = int(t * sr)
        a0, a1 = max(0, c - h - xf), min(len(y), c + h + xf)
        if a1 - a0 < 2 * xf + 2:
            continue
        w = np.ones(a1 - a0, np.float32)
        w[:xf] = _fade(xf)
        w[-xf:] = 1 - _fade(xf)
        y[a0:a1] = y[a0:a1] * (1 - w[:, None]) + lp[a0:a1] * w[:, None]
    return y


def _load(path):
    v = _RAW.get(path)
    if v is None:
        y, sr = sf.read(path, dtype='float32', always_2d=True)
        if y.shape[1] == 1:
            y = np.repeat(y, 2, axis=1)
        elif y.shape[1] > 2:
            y = y[:, :2]
        y = np.ascontiguousarray(y)
        ck = _click_map().get(path)
        if ck:
            y = _declick(y, sr, ck)
        v = (y, np.array([sr]))
        _RAW.put(path, v)
    return v[0], int(v[1][0])


def _shifted(path, semis, sr_out):
    """Return (audio(n,2) at sr_out pitch-shifted by `semis` via resampling, time_scale) ; time_scale = out_s / in_s."""
    q = int(round(semis * 100))
    key = (path, q, sr_out)
    v = _SHIFT.get(key)
    if v is not None:
        return v[0], float(v[1][0])
    y, sr = _load(path)
    r = 2.0 ** (q / 1200.0)
    in_rate = sr * r
    if abs(in_rate - sr_out) < 1e-3:
        out = y.copy()
    else:
        out = librosa.resample(y.T, orig_sr=float(in_rate), target_sr=float(sr_out), res_type='soxr_hq').T
        out = np.ascontiguousarray(out, dtype=np.float32)
    ts = 1.0 / r
    _SHIFT.put(key, (out, np.array([ts])))
    return out, ts


# ---------------------------------------------------------------------------------------------
# small DSP helpers
# ---------------------------------------------------------------------------------------------
def _db(x):
    return 10.0 ** (x / 20.0)


def _onepole_lp(x, fc, sr):
    if fc >= sr * 0.45:
        return x
    a = math.exp(-2.0 * math.pi * fc / sr)
    return _sig.lfilter([1 - a], [1, -a], x, axis=0).astype(np.float32)


def _biquad(kind, f0, sr, q=0.707, gain_db=0.0):
    """RBJ cookbook biquad -> sos row"""
    A = 10 ** (gain_db / 40)
    w0 = 2 * math.pi * f0 / sr
    cw, sw = math.cos(w0), math.sin(w0)
    al = sw / (2 * q)
    if kind == 'lp':
        b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]
        a = [1 + al, -2 * cw, 1 - al]
    elif kind == 'hp':
        b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]
        a = [1 + al, -2 * cw, 1 - al]
    elif kind == 'peak':
        b = [1 + al * A, -2 * cw, 1 - al * A]
        a = [1 + al / A, -2 * cw, 1 - al / A]
    elif kind == 'lowshelf':
        sq = 2 * math.sqrt(A) * al
        b = [A * ((A + 1) - (A - 1) * cw + sq), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - sq)]
        a = [(A + 1) + (A - 1) * cw + sq, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - sq]
    elif kind == 'highshelf':
        sq = 2 * math.sqrt(A) * al
        b = [A * ((A + 1) + (A - 1) * cw + sq), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - sq)]
        a = [(A + 1) - (A - 1) * cw + sq, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - sq]
    else:
        raise ValueError(kind)
    return np.array([b[0] / a[0], b[1] / a[0], b[2] / a[0], 1.0, a[1] / a[0], a[2] / a[0]])


def _sos(x, rows):
    if not rows:
        return x
    return _sig.sosfilt(np.vstack(rows), x, axis=0).astype(np.float32)


def _fade(n, kind='cos'):
    t = np.linspace(0, 1, n, endpoint=False, dtype=np.float32) if n > 0 else np.zeros(0, np.float32)
    if kind == 'cos':
        return 0.5 - 0.5 * np.cos(np.pi * t)
    return t


def pan_stereo(x, pan=0.0, width=1.0):
    """x (n,2). width scales the side signal, pan uses constant-power law (unity at centre)."""
    if width != 1.0:
        m = 0.5 * (x[:, 0] + x[:, 1])
        s = 0.5 * (x[:, 0] - x[:, 1]) * width
        x = np.stack([m + s, m - s], axis=1)
    if pan:
        th = (max(-1.0, min(1.0, pan)) + 1) * math.pi / 4
        gl, gr = math.sqrt(2) * math.cos(th), math.sqrt(2) * math.sin(th)
        x = x * np.array([gl, gr], dtype=np.float32)
    return x.astype(np.float32)


def _mix_into(buf, x, start):
    if start < 0:
        x = x[-start:]
        start = 0
    end = min(len(buf), start + len(x))
    if end > start:
        buf[start:end] += x[:end - start]


# ---------------------------------------------------------------------------------------------
# articulation index (zones / layers / rr)
# ---------------------------------------------------------------------------------------------
_IDX = {}


def _art(inst, art):
    M = manifest()
    try:
        im = M['instruments'][inst]
    except KeyError:
        raise KeyError(f'unknown instrument {inst!r}; have {sorted(M["instruments"])}')
    try:
        a = im['articulations'][art]
    except KeyError:
        raise KeyError(f'{inst}: unknown articulation {art!r}; have {sorted(im["articulations"])}')
    return im, a


def _index(inst, art):
    k = (inst, art)
    if k in _IDX:
        return _IDX[k]
    im, a = _art(inst, art)
    layers = sorted({s['dyn'] for s in a['samples']})
    zones = {}
    for L in layers:
        ss = [s for s in a['samples'] if s['dyn'] == L]
        # group by key zone
        groups = OrderedDict()
        for s in ss:
            if s.get('lokey') is not None:
                gk = ('k', s['lokey'], s['hikey'])
            else:
                gk = ('r', s['midi_declared'])
            groups.setdefault(gk, []).append(s)
        zl = []
        for gk, vs in groups.items():
            root = float(np.median([v['midi'] for v in vs]))
            if gk[0] == 'k':
                zl.append({'lo': gk[1], 'hi': gk[2], 'root': root, 'vars': sorted(vs, key=lambda v: v['rr'])})
            else:
                zl.append({'lo': None, 'hi': None, 'root': root, 'vars': sorted(vs, key=lambda v: v['rr'])})
        zl.sort(key=lambda z: z['root'])
        # fill missing key ranges by midpoints
        for i, z in enumerate(zl):
            if z['lo'] is None:
                lo = -1e9 if i == 0 else (zl[i - 1]['root'] + z['root']) / 2
                hi = 1e9 if i == len(zl) - 1 else (z['root'] + zl[i + 1]['root']) / 2
                z['lo'], z['hi'] = lo, hi
        zones[L] = zl
    lk = 'loud_sus_db' if a['kind'] == 'sus' else 'loud_peak50_db'
    lay_loud = {}
    for L in layers:
        lay_loud[L] = float(np.median([s.get(lk, -40) for s in a['samples'] if s['dyn'] == L]))
    res = {'im': im, 'a': a, 'layers': layers, 'zones': zones, 'lay_loud': lay_loud, 'lk': lk}
    _IDX[k] = res
    return res


def _find_zone(zl, midi):
    best, bd = None, 1e9
    for z in zl:
        if z['lo'] - 0.01 <= midi <= z['hi'] + 0.01:
            d = abs(z['root'] - midi)
            if d < bd:
                best, bd = z, d
    if best is None:
        best = min(zl, key=lambda z: abs(z['root'] - midi))
    return best


# ---------------------------------------------------------------------------------------------
# loop builder
# ---------------------------------------------------------------------------------------------
_ALOOP = {}


def _auto_loop(y, sr, start):
    """loop points inside the steady part of an un-looped sustain (avoid attack and the natural decay)."""
    key = (id(y), len(y), start)
    hit = _ALOOP.get(key)
    if hit is not None and hit[0]() is y:  # weakref check: an id can be reused after garbage collection
        return hit[1]
    n = len(y)
    pw = (y[:, 0].astype(np.float64) ** 2 + y[:, 1].astype(np.float64) ** 2) * 0.5
    w = 2048
    cs = np.concatenate([[0.0], np.cumsum(pw)])
    idx = np.arange(n)
    lo = np.clip(idx - w // 2, 0, n)
    hi = np.clip(idx + w // 2, 0, n)
    env = np.sqrt((cs[hi] - cs[lo]) / np.maximum(1, hi - lo) + 1e-12)
    body = env[int(min(n * 0.3, 0.6 * sr)):]
    lvl = np.median(body) if len(body) else env.max()
    ok = np.where(env > lvl * 0.5)[0]
    le = int(ok[-1]) if len(ok) else n
    le = min(le - int(0.05 * sr), n - int(0.05 * sr))
    ls = int(max(min(n * 0.35, 0.8 * sr), start + 0.05 * sr))
    if le - ls < int(0.5 * sr):
        ls = max(start, le - int(0.5 * sr))
    if le - ls < int(0.2 * sr):  # sample too short: hold last part
        ls, le = max(0, n - int(0.3 * sr)), n
    _ALOOP[key] = (weakref.ref(y), (ls, le))
    return ls, le


def _extend(y, start, need, loop=None, xfade=0.0, sr=48000):
    """Return y[start:start+need] extended by looping. loop=(ls, le) in frames of y (output rate) or None (auto)."""
    n = len(y)
    if n - start >= need:
        return y[start:start + need]
    if loop is not None:
        ls, le = int(loop[0]), int(min(loop[1], n))
        xf = int(min(0.01 * sr, (le - ls) * 0.1))  # tiny safety crossfade on designed loops
    else:
        ls, le = _auto_loop(y, sr, start)
        xf = int(min(xfade * sr if xfade else 0.25 * sr, (le - ls) * 0.45))
    seg_len = le - ls
    out = [y[start:le].copy()]
    total = le - start
    piece = y[ls:le]
    while total < need + xf:
        nxt = piece.copy()
        if xf > 0:
            prev = out[-1]
            k = min(xf, len(prev), len(nxt))
            fi = _fade(k)[:, None]
            # correlation-aware crossfade (equal power for uncorrelated material, linear for correlated)
            a_, b_ = prev[-k:], nxt[:k]
            c = float(np.sum(a_ * b_) / (np.sqrt(np.sum(a_ ** 2) * np.sum(b_ ** 2)) + 1e-12))
            if c > 0.5:
                g_in, g_out = fi, 1 - fi
            else:
                g_in, g_out = np.sin(fi * np.pi / 2), np.cos(fi * np.pi / 2)
            prev[-k:] = a_ * g_out + b_ * g_in
            nxt = nxt[k:]
        out.append(nxt)
        total += len(nxt)
        if seg_len <= 0:
            break
    res = np.concatenate(out, axis=0)
    return res[:need]


# ---------------------------------------------------------------------------------------------
# main renderer
# ---------------------------------------------------------------------------------------------
LEAD_CAP = {'sus': 0.10, 'short': 0.04, 'pluck': 0.01, 'perc': 0.005}   # max pre-delay compensation (s)
LEAD_FRAC = 0.6   # fraction of (perceived onset - onset) moved ahead of the grid
ATTACK_DEFAULT = {'choir': 0.30}
FILTER_POLES = {'brass': 2}


def _norm_vel(notes):
    vs = [n.get('vel', 100) for n in notes]
    scale = 127.0 if vs and max(vs) <= 1.0 else 1.0
    return scale


def render(notes, instrument, articulation, sr=48000, pan=None, width=None, gain_db=0.0, seed=0,
           detune_cents=None, timing_comp=True, attack_s=None, release_s=None, dyn_range_db=None,
           vel_filter=True, cut_shorts=False, pedal=False, tail_s=None, stereo=True, length_s=None, legato='auto'):
    """Render notes on one instrument/articulation. Returns float32 (N, 2).
    legato='auto': for sustained articulations, a note that starts where another note of this call ends
    (within -80..+300 ms) skips its sampled attack and fades in over 60 ms -> no level dip at chord changes."""
    if not notes:
        return np.zeros((int((length_s or 0.1) * sr), 2), np.float32)
    ix = _index(instrument, articulation)
    im, a = ix['im'], ix['a']
    kind = a['kind']
    fam = im.get('family', 'other')
    dr = dyn_range_db if dyn_range_db is not None else im.get('dyn_range_db', 24)
    one_shot = a.get('one_shot', False)
    rel_default = a.get('release_s', 0.3) if release_s is None else release_s
    att_default = ATTACK_DEFAULT.get(fam, 0.0) if attack_s is None else attack_s
    if detune_cents is None:
        detune_cents = 2.0 if fam in ('strings', 'brass', 'woodwinds', 'choir') else 0.0
    rng = random.Random(zlib.crc32(f'{instrument}|{articulation}|{seed}'.encode()))  # stable across processes
    vscale = _norm_vel(notes)
    layers = ix['layers']
    ref_layer_loud = max(ix['lay_loud'].values())
    rr_state = {}
    voices = []  # (start_frame, buffer(n,2), group)
    ends = np.array(sorted(float(q['start_s']) + float(q.get('dur_s', 0.5)) for q in notes))
    for n in sorted(notes, key=lambda q: q['start_s']):
        connected = False
        if kind == 'sus' and legato and not one_shot:
            t_s = float(n['start_s'])
            j0, j1 = np.searchsorted(ends, [t_s - 0.08, t_s + 0.30])
            connected = bool(j1 > j0) if legato == 'auto' else True
            connected = connected or n.get('legato', False)
        midi = float(n['midi'])
        v = max(1.0, min(127.0, float(n.get('vel', 100)) * vscale))
        x = (v - 1) / 126.0
        dur = max(0.01, float(n.get('dur_s', 0.5)))
        # ---- layer choice
        if len(layers) > 1 and a.get('vel_mode') == 'layers':
            p = x * (len(layers) - 1)
            lo_i = int(math.floor(p))
            fr = p - lo_i
            if kind == 'sus' and 0.25 < fr < 0.75 and lo_i + 1 < len(layers):
                picks = [(layers[lo_i], math.cos(fr * math.pi / 2)), (layers[lo_i + 1], math.sin(fr * math.pi / 2))]
            else:
                li = lo_i + (1 if rng.random() < fr else 0)
                picks = [(layers[min(li, len(layers) - 1)], 1.0)]
        else:
            picks = [(layers[-1] if len(layers) == 1 else layers[int(round(x * (len(layers) - 1)))], 1.0)]
        target_db = REF_DB + (0.0 if kind == 'sus' else 2.0) + (-dr * (1.0 - v / 127.0)) + float(n.get('gain_db', 0.0)) + gain_db
        for layer, lw in picks:
            zl = ix['zones'][layer]
            z = _find_zone(zl, midi)
            vars_ = z['vars']
            key = (layer, z['root'])
            cnt = rr_state.get(key)
            if cnt is None:
                cnt = rng.randrange(len(vars_))
            s = vars_[cnt % len(vars_)]
            rr_state[key] = cnt + 1
            extra_shift = 0.0
            # pseudo round-robin for repeated shorts with a single recording: borrow neighbour zone
            if len(vars_) == 1 and kind in ('short', 'perc', 'pluck') and len(zl) > 1 and (cnt % 2 == 1):
                zi = zl.index(z)
                cand = [zz for zz in (zl[zi - 1] if zi > 0 else None, zl[zi + 1] if zi + 1 < len(zl) else None)
                        if zz is not None and abs(zz['root'] - midi) <= 3.1]
                if cand:
                    s = min(cand, key=lambda zz: abs(zz['root'] - midi))['vars'][0]
            det = float(n.get('detune_cents', rng.uniform(-detune_cents, detune_cents))) / 100.0
            semis = midi - s['midi'] + det + extra_shift
            y, ts = _shifted(s['file'], semis, sr)
            # ---- level
            dev = s.get(ix['lk'], ix['lay_loud'][layer]) - ix['lay_loud'][layer]
            corr = -0.5 * dev if abs(dev) > 4 else 0.0
            g_db = target_db - ix['lay_loud'][layer] + corr
            g = _db(g_db) * lw
            # ---- start / timing compensation
            read0 = 0
            off = s.get('sfz_offset')
            att = float(n.get('attack_s', att_default))
            if connected:
                # legato transition: skip the recorded attack, short fade-in, start on the grid
                skip = max(s.get('onset_s', 0.0), s.get('steady_s', s.get('perceived_onset_s', 0.0)) - 0.03)
                if off:
                    skip = max(skip, off / s['sr'])
                read0 = int(skip * ts * sr)
                att = float(n.get('attack_s', 0.06))
                comp = 0.02
            elif off:
                read0 = int(off / s['sr'] * ts * sr)
                comp = 0.08 if att > 0 else 0.0
            else:
                onset = s.get('onset_s', 0.0)
                lead = 0.0
                if timing_comp:
                    lead = min(LEAD_FRAC * max(0.0, s.get('perceived_onset_s', onset) - onset), LEAD_CAP.get(kind, 0.0))
                read0 = int(max(0.0, onset - 0.003) * ts * sr)
                comp = lead * ts + min(0.003, onset) * ts
            rel = float(n.get('release_s', rel_default))
            if one_shot or (kind == 'short' and not cut_shorts) or (a.get('piano') and pedal):
                buf = y[read0:].copy()
                hold = None
            else:
                need = int((comp + dur + rel) * sr) + 8
                lp = None
                if 'loop_start' in s and kind == 'sus':
                    lp = (s['loop_start'] * ts * sr / s['sr'], s['loop_end'] * ts * sr / s['sr'])
                if kind == 'sus':
                    buf = _extend(y, read0, need, lp, sr=sr).copy()
                else:
                    buf = y[read0:read0 + need].copy()
                hold = int((comp + dur) * sr)
            if len(buf) < 16:
                continue
            # ---- envelope
            env = np.ones(len(buf), np.float32)
            if att > 0:
                k = min(len(buf), int(att * sr))
                env[:k] *= _fade(k)
            elif read0 > 0:
                k = min(len(buf), int(0.002 * sr))
                env[:k] *= _fade(k)
            if hold is not None and hold < len(buf):
                k = max(1, int(rel * sr))
                r_env = 1 - _fade(min(k, len(buf) - hold))
                env[hold:hold + len(r_env)] *= r_env
                env[hold + len(r_env):] = 0.0
                buf = buf[:hold + len(r_env)]
                env = env[:len(buf)]
            if tail_s is not None and one_shot:
                lim = int((comp + dur + tail_s) * sr)
                if lim < len(buf):
                    k = min(int(0.05 * sr), lim)
                    env[lim - k:lim] *= 1 - _fade(k)
                    env, buf = env[:lim], buf[:lim]
            k = min(len(buf), int(0.004 * sr))
            env[len(buf) - k:] *= 1 - _fade(k)
            # palm mute (DI guitar): fast exponential decay + low-pass before the amp
            if a.get('palm_mute'):
                t = np.arange(len(buf), dtype=np.float32) / sr
                tau = 0.075 + 0.05 * x
                pm = np.exp(-np.maximum(0, t - comp - 0.012) / tau)
                env *= pm
                cut = int((comp + min(dur, 0.25) + 0.12) * sr)
                if cut < len(buf):
                    buf, env = buf[:cut], env[:cut]
                buf = _sos(buf, [_biquad('lp', 900 + 2200 * x, sr, 0.6)])
            buf = buf * env[:, None]
            # ---- velocity brightness
            if vel_filter and (a.get('vel_mode') == 'filter' or len(layers) == 1) and x < 0.98:
                fc = 20000.0 * 2 ** (-(1 - x) * 4.0) * 2 ** ((midi - 60) / 24.0)
                fc = max(300.0, fc)
                if FILTER_POLES.get(fam, 1) == 2:
                    buf = _sos(buf, [_biquad('lp', min(fc, sr * 0.45), sr, 0.707)])
                else:
                    buf = _onepole_lp(buf, fc, sr)
            buf = (buf * g).astype(np.float32)
            st = int(round((float(n['start_s']) - comp) * sr))
            voices.append([st, buf, n.get('group')])
    if not voices:
        return np.zeros((int((length_s or 0.1) * sr), 2), np.float32)
    # ---- mono groups: new note cuts the previous one in the same group
    last = {}
    for vi, (st, buf, grp) in enumerate(voices):
        if grp is None:
            continue
        if grp in last:
            pv = voices[last[grp]]
            cut = st - pv[0] + int(0.002 * sr)
            if 0 < cut < len(pv[1]):
                k = min(int(0.008 * sr), len(pv[1]) - cut)
                pv[1] = pv[1][:cut + k].copy()
                pv[1][cut:cut + k] *= (1 - _fade(k))[:, None]
        last[grp] = vi
    t0 = min(v[0] for v in voices)
    shift = -t0 if t0 < 0 else 0
    end = max(v[0] + len(v[1]) for v in voices) + shift
    if length_s is not None:
        end = max(end, int(length_s * sr))
    out = np.zeros((end, 2), np.float32)
    for st, buf, _ in voices:
        _mix_into(out, buf, st + shift)
    if shift:
        out = out[shift:]  # notes that start before t=0 are truncated (timeline stays absolute)
    if length_s is not None:
        out = out[:int(length_s * sr)]
    p = im.get('pan', 0.0) if pan is None else pan
    w = im.get('width', 1.0) if width is None else width
    if stereo:
        out = pan_stereo(out, p, w)
    return out


def render_layers(notes, layers, sr=48000, **common):
    """layers: [(instrument, articulation, gain_db[, opts_dict]), ...]; returns summed stereo."""
    outs = []
    for i, L in enumerate(layers):
        inst, art, g = L[0], L[1], L[2]
        opts = dict(common)
        if len(L) > 3:
            opts.update(L[3])
        opts.setdefault('seed', i * 17 + 3)
        outs.append(render(notes, inst, art, sr=sr, gain_db=g + opts.pop('gain_db', 0.0), **opts))
    n = max(len(o) for o in outs)
    out = np.zeros((n, 2), np.float32)
    for o in outs:
        out[:len(o)] += o
    return out


# recommended layer stacks (gain dB) for a big section sound
PRESETS = {
    'violins1_sus': [('violins1', 'sustain', 0.0), ('violins1', 'sustain_vsco', -3.0)],
    'violins2_sus': [('violins2', 'sustain', 0.0), ('violins2', 'sustain_vsco', -4.0, {'pan': -0.3})],
    'violas_sus': [('violas', 'sustain', 0.0), ('violas', 'sustain_vsco', -3.0)],
    'celli_sus': [('celli', 'sustain', 0.0), ('celli', 'sustain_vsco', -3.0)],
    'basses_sus': [('basses', 'sustain', 0.0), ('basses', 'sustain_vsco', -5.0)],
    'violins1_short': [('violins1', 'spiccato', 0.0), ('violins1', 'staccato', -4.0)],
    'violins2_short': [('violins2', 'spiccato', -1.0, {'pan': -0.3, 'seed': 7}), ('violins2', 'staccato', -4.0)],
    'violas_short': [('violas', 'spiccato', 0.0), ('violas', 'staccato', -4.0)],
    'celli_short': [('celli', 'spiccato', 0.0), ('celli', 'staccato', -4.0)],
    'basses_short': [('basses', 'staccato', 0.0), ('basses', 'spiccato', -4.0)],
    'horns_sus': [('horns', 'sustain', 0.0), ('horns', 'sustain_solo', -6.0)],
    'horns_stab': [('horns', 'staccato', 0.0), ('horns', 'staccato_solo', -5.0)],
    'trombones_stab': [('trombones', 'staccato', 0.0), ('trombones', 'staccato_solo', -5.0)],
    'trumpets_stab': [('trumpets', 'staccato', 0.0), ('trumpets', 'staccato_solo', -5.0)],
}


def render_preset(notes, preset, sr=48000, **common):
    return render_layers(notes, PRESETS[preset], sr=sr, **common)


# ---------------------------------------------------------------------------------------------
# drums
# ---------------------------------------------------------------------------------------------
MIC_PAN = {'Kdrum_front': 0.0, 'Kdrum_back': 0.0, 'Snare_top': 0.0, 'Snare_bottom': 0.0, 'Tom1': -0.2,
           'Tom2': 0.25, 'Tom3': 0.6, 'Hihat': -0.45, 'Ride': 0.45, 'OHL': -0.9, 'OHR': 0.9, 'AmbL': -1.0, 'AmbR': 1.0}
# (polarity, advance in samples @44.1k) measured by cross-correlation on DRSKit
MIC_ALIGN = {'Kdrum_back': (-1, 99), 'Snare_bottom': (-1, 20)}
CLOSE_OF = {
    'kick': ['Kdrum_front', 'Kdrum_back'], 'kick_soft': ['Kdrum_front', 'Kdrum_back'],
    'snare': ['Snare_top', 'Snare_bottom'], 'snare_rim': ['Snare_top', 'Snare_bottom'], 'snare_rest': ['Snare_top', 'Snare_bottom'],
    'tom1': ['Tom1'], 'tom2': ['Tom2'], 'tom3': ['Tom3'],
    'hihat_closed': ['Hihat'], 'hihat_closed_shank': ['Hihat'], 'hihat_semi': ['Hihat'], 'hihat_open': ['Hihat'],
    'hihat_open_tip': ['Hihat'], 'hihat_pedal': ['Hihat'], 'ride': ['Ride'], 'ride_shank': ['Ride'], 'ride_bell': ['Ride'],
    'crash_l': [], 'crash_l_tip': [], 'crash_r': [], 'crash_r_tip': [],
}
MIC_PRESETS = {
    # gains in dB for: close (own close mics), oh, amb, bleed (other close mics), plus per-mic trims
    'rock': {'close': 0.0, 'oh': -4.0, 'amb': -6.0, 'bleed': -60.0,
             'trim': {'Kdrum_back': -3.0, 'Snare_bottom': -6.0, 'Hihat': -6.0, 'Ride': -6.0}},
    'tight': {'close': 0.0, 'oh': -8.0, 'amb': -14.0, 'bleed': -60.0,
              'trim': {'Kdrum_back': -2.0, 'Snare_bottom': -6.0, 'Hihat': -4.0, 'Ride': -4.0}},
    'natural': {'close': -4.0, 'oh': 0.0, 'amb': -2.0, 'bleed': -12.0,
                'trim': {'Kdrum_back': -4.0, 'Snare_bottom': -8.0, 'Hihat': -8.0, 'Ride': -8.0}},
    'room': {'close': -6.0, 'oh': -2.0, 'amb': 0.0, 'bleed': -60.0, 'trim': {'Snare_bottom': -8.0}},
}
CHOKE = {  # piece -> pieces it silences
    'hihat_closed': ('hihat_open', 'hihat_open_tip', 'hihat_semi'),
    'hihat_closed_shank': ('hihat_open', 'hihat_open_tip', 'hihat_semi'),
    'hihat_pedal': ('hihat_open', 'hihat_open_tip', 'hihat_semi'),
    'hihat_semi': ('hihat_open', 'hihat_open_tip'),
    'crash_l_choke': ('crash_l', 'crash_l_tip'), 'crash_r_choke': ('crash_r', 'crash_r_tip'),
    'ride_choke': ('ride', 'ride_shank', 'ride_bell'),
}
ORCH_PAN = {'orch_bass_drum': (-0.1, 0.6), 'orch_crash': (0.25, 0.7), 'sus_cymbal': (0.25, 0.7), 'sus_cymbal_mallet': (0.25, 0.7),
            'cymbal_swell_long': (0.2, 0.8), 'cymbal_swell_med': (0.2, 0.8), 'cymbal_swell_short': (0.2, 0.8),
            'cymbal_roll_sso': (0.2, 0.8), 'orch_snare': (0.15, 0.5), 'orch_snare_roll': (0.15, 0.5), 'gong': (0.3, 0.7),
            'tamtam': (0.3, 0.7), 'anvil': (0.2, 0.4), 'bass_drum_rub': (-0.1, 0.6)}
_DRUM_CACHE = _LRU(1.0e9)
# default kit balance (dB, applied on top of per-hit loudness normalisation) - a typical rock balance
DEFAULT_KIT_DB = {'kick': 0.0, 'kick_soft': 0.0, 'snare': 0.0, 'snare_rim': -4.0, 'snare_rest': -6.0,
                  'tom1': -1.0, 'tom2': -1.0, 'tom3': -1.0, 'hihat_closed': -9.0, 'hihat_closed_shank': -9.0,
                  'hihat_semi': -8.0, 'hihat_open': -8.0, 'hihat_open_tip': -8.0, 'hihat_pedal': -12.0,
                  'ride': -9.0, 'ride_shank': -9.0, 'ride_bell': -8.0, 'crash_l': -4.0, 'crash_l_tip': -4.0,
                  'crash_r': -4.0, 'crash_r_tip': -4.0, 'orch_bass_drum': 0.0, 'orch_crash': -2.0, 'sus_cymbal': -4.0,
                  'sus_cymbal_mallet': -4.0, 'cymbal_swell_long': -4.0, 'cymbal_swell_med': -4.0, 'cymbal_swell_short': -4.0,
                  'cymbal_roll_sso': -4.0, 'orch_snare': -3.0, 'orch_snare_roll': -4.0, 'gong': -2.0, 'tamtam': -2.0,
                  'anvil': -6.0, 'bass_drum_rub': -4.0}


_WINDB = {}


def _max_win_db(y, sr, win_s=0.15, hop_s=0.025):
    key = (id(y), len(y), win_s, hop_s)
    hit = _WINDB.get(key)
    if hit is not None and hit[0]() is y:
        return hit[1]
    m = y.mean(axis=1).astype(np.float64)
    w, hop = int(win_s * sr), int(hop_s * sr)
    if len(m) < w:
        m = np.pad(m, (0, w - len(m)))
    cs = np.concatenate([[0.0], np.cumsum(m ** 2)])
    st = np.arange(0, len(m) - w + 1, hop)
    v = float(10 * np.log10(np.max((cs[st + w] - cs[st]) / w) + 1e-20))
    _WINDB[key] = (weakref.ref(y), v)
    return v


def list_drum_pieces():
    P = manifest()['drums']['pieces']
    return {k: {'layers': len(v['layers']), 'hits': sum(len(L['rr']) for L in v['layers']), 'source': v['source']}
            for k, v in P.items()}


def _drum_hit_audio(piece, rr_entry, sr, mix, multi):
    key = (piece, rr_entry.get('hit', rr_entry.get('file')), sr, json.dumps(mix, sort_keys=True) if isinstance(mix, dict) else mix)
    v = _DRUM_CACHE.get(key)
    if v is not None:
        return v
    if not multi:
        y, fsr = _load(rr_entry['file'])
        if fsr != sr:
            y = np.ascontiguousarray(librosa.resample(y.T, orig_sr=fsr, target_sr=sr, res_type='soxr_hq').T, dtype=np.float32)
        on = rr_entry.get('onset_s', 0.0)
        y = y[int(max(0, on - 0.002) * sr):]
        _DRUM_CACHE.put(key, y)
        return y
    P = MIC_PRESETS[mix] if isinstance(mix, str) else mix
    own = CLOSE_OF.get(piece, [])
    acc = None
    for mic, path in rr_entry['files'].items():
        if mic in ('OHL', 'OHR'):
            g = P['oh']
        elif mic in ('AmbL', 'AmbR'):
            g = P['amb']
        elif mic in own:
            g = P['close']
        else:
            g = P['bleed']
        g += P.get('trim', {}).get(mic, 0.0)
        if g <= -59:
            continue
        x, fsr = sf.read(path, dtype='float32')
        pol, adv = MIC_ALIGN.get(mic, (1, 0))
        if adv:
            x = np.concatenate([x[adv:], np.zeros(adv, np.float32)])
        x = x * pol * _db(g)
        th = (MIC_PAN.get(mic, 0.0) + 1) * math.pi / 4
        st = np.stack([x * math.sqrt(2) * math.cos(th), x * math.sqrt(2) * math.sin(th)], axis=1)
        if acc is None:
            acc = st
        else:
            L = max(len(acc), len(st))
            if len(acc) < L:
                acc = np.pad(acc, ((0, L - len(acc)), (0, 0)))
            acc[:len(st)] += st
    if acc is None:
        acc = np.zeros((16, 2), np.float32)
    if fsr != sr:
        acc = librosa.resample(acc.T, orig_sr=fsr, target_sr=sr, res_type='soxr_hq').T
    acc = np.ascontiguousarray(acc, dtype=np.float32)
    # trim pre-roll (onset of the summed signal)
    e = np.abs(acc).max(axis=1)
    on = int(np.argmax(e > e.max() * 0.03))
    acc = acc[max(0, on - int(0.001 * sr)):]
    _DRUM_CACHE.put(key, acc)
    return acc


def drums_render(hits, sr=48000, mix='rock', seed=0, dyn_range_db=30.0, gain_db=0.0, choke=True, length_s=None,
                 kit_gain_db=None):
    """hits: [{start_s, piece, vel(1..127)}] -> stereo float32. Each piece normalised so vel 127 ~ REF_DB+4 dB peakish RMS."""
    P = manifest()['drums']['pieces']
    rng = random.Random(seed)
    vscale = _norm_vel(hits)
    voices = []
    last_rr = {}
    level_ref = {}
    for h in sorted(hits, key=lambda q: q['start_s']):
        piece = h['piece']
        if piece in ('crash_l_choke', 'crash_r_choke', 'ride_choke'):
            voices.append([int(h['start_s'] * sr), None, piece])
            continue
        if piece not in P:
            raise KeyError(f'unknown drum piece {piece!r}; have {sorted(P)}')
        pc = P[piece]
        Ls = pc['layers']
        v = max(1.0, min(127.0, float(h.get('vel', 100)) * vscale))
        top = Ls[-1]['loud_db']
        target = top - dyn_range_db * (1 - v / 127.0) ** 1.1  # layer choice by the raw (all-mic) loudness
        # nearest layer at or above target loudness
        cand = sorted(Ls, key=lambda L: (abs(L['loud_db'] - target) + (1.5 if L['loud_db'] < target else 0)))
        L = cand[0]
        rrs = L['rr']
        k = (piece, L['layer'])
        prev = last_rr.get(k)
        choices = [i for i in range(len(rrs)) if i != prev] or [0]
        i = rng.choice(choices)
        last_rr[k] = i
        e = rrs[i]
        y = _drum_hit_audio(piece, e, sr, mix, pc.get('multi_mic', False))
        m_db = _max_win_db(y, sr, 0.15)
        want = REF_DB - 6.0 - dyn_range_db * (1 - v / 127.0) ** 1.1 + rng.uniform(-0.6, 0.6)
        kg = dict(DEFAULT_KIT_DB)
        kg.update(kit_gain_db or {})
        g = _db(want - m_db + gain_db + float(h.get('gain_db', 0.0)) + kg.get(piece, 0.0))
        buf = y * g
        if not pc.get('multi_mic', False):
            p, w = ORCH_PAN.get(piece, (0.0, 0.7))
            buf = pan_stereo(buf, h.get('pan', p), w)
        elif 'pan' in h:
            buf = pan_stereo(buf, h['pan'], 1.0)
        voices.append([int(round(float(h['start_s']) * sr)), buf.astype(np.float32), piece])
    # chokes
    if choke:
        for vi, (st, buf, piece) in enumerate(voices):
            kills = CHOKE.get(piece)
            if not kills:
                continue
            for vj in range(vi):
                s2, b2, p2 = voices[vj]
                if b2 is None or p2 not in kills:
                    continue
                cut = st - s2
                if 0 < cut < len(b2):
                    kk = min(int(0.04 * sr), len(b2) - cut)
                    b2 = b2[:cut + kk].copy()
                    b2[cut:cut + kk] *= (1 - _fade(kk))[:, None]
                    voices[vj][1] = b2
    voices = [v for v in voices if v[1] is not None]
    if not voices:
        return np.zeros((int((length_s or 0.1) * sr), 2), np.float32)
    end = max(st + len(b) for st, b, _ in voices)
    if length_s:
        end = max(end, int(length_s * sr))
    out = np.zeros((end, 2), np.float32)
    for st, b, _ in voices:
        _mix_into(out, b, st)
    if length_s:
        out = out[:int(length_s * sr)]
    return out


# ---------------------------------------------------------------------------------------------
# electric guitar / bass: amp simulation + synthetic cabinet impulse responses (original, license-free)
# ---------------------------------------------------------------------------------------------
_CAB = {}


def make_cab_ir(sr=48000, variant='v30', n=2048, seed=0):
    """Minimum-phase 4x12 cabinet IR synthesised from a designed magnitude response (no third-party IR used).
    variants: 'v30' (Vintage-30-like: tight lows, 2-4 kHz presence peaks), 'gb' (Greenback-like: smoother, darker),
    'off' (off-axis: darker)."""
    key = (sr, variant, n, seed)
    if key in _CAB:
        return _CAB[key]
    N = 1 << 15
    f = np.fft.rfftfreq(N, 1 / sr)
    f[0] = 1.0
    lf = np.log2(f)

    def bump(fc, gain, oct_w):
        return gain * np.exp(-0.5 * ((lf - math.log2(fc)) / oct_w) ** 2)
    mag = np.zeros_like(f)
    # low end: resonance + rolloff
    if variant == 'gb':
        mag += bump(95, 3.0, 0.35) + bump(1300, 1.0, 0.8) + bump(2400, 2.0, 0.35) - bump(450, 1.5, 0.4)
        lp_f, lp_s = 4600, 30
    elif variant == 'off':
        mag += bump(110, 3.5, 0.3) + bump(1800, 1.5, 0.5) - bump(500, 2.0, 0.4) + bump(3000, 1.0, 0.3)
        lp_f, lp_s = 3800, 34
    else:
        mag += bump(105, 4.0, 0.3) + bump(800, 1.0, 0.7) + bump(2300, 4.0, 0.25) + bump(3700, 5.0, 0.18) - bump(2950, 2.0, 0.1) \
            - bump(420, 2.5, 0.35)
        lp_f, lp_s = 5200, 34
    hp = 75.0
    mag += np.where(f < hp, -24 * np.log2(hp / f), 0.0)
    mag += np.where(f > lp_f, -lp_s * np.log2(f / lp_f), 0.0)
    rs = np.random.RandomState(seed + 11)
    for _ in range(9):  # cone break-up ripple
        mag += bump(rs.uniform(900, 7000), rs.uniform(-2.0, 2.0), rs.uniform(0.03, 0.08))
    mag = np.maximum(mag, -90)
    mag -= np.interp(1000, f, mag)
    A = 10 ** (mag / 20)
    # minimum phase via real cepstrum
    logA = np.log(np.maximum(A, 1e-6))
    cep = np.fft.irfft(logA, N)
    w = np.zeros(N)
    w[0] = 1
    w[1:N // 2] = 2
    w[N // 2] = 1
    H = np.exp(np.fft.rfft(cep * w, N))
    h = np.fft.irfft(H, N)[:n]
    fade = int(n * 0.25)
    h[-fade:] *= np.cos(np.linspace(0, np.pi / 2, fade)) ** 2
    h = h / (np.sqrt(np.sum(h ** 2)) + 1e-12) * 0.25
    h = h.astype(np.float32)
    _CAB[key] = h
    return h


AMP_PRESETS = {
    # pre: tight HPF + mid hump (TS-style boost), two clipping stages, tone stack, power-amp softness
    'high_gain': {'hp': 110, 'mid_f': 750, 'mid_db': 7, 'drive1': 18.0, 'drive2': 6.0, 'bias': 0.12,
                  'bass': 2.0, 'mid': -4.0, 'treble': 2.5, 'presence': 2.0, 'out_db': -17.0},
    'crunch': {'hp': 90, 'mid_f': 800, 'mid_db': 4, 'drive1': 5.0, 'drive2': 2.0, 'bias': 0.08,
               'bass': 1.5, 'mid': -1.0, 'treble': 2.0, 'presence': 1.5, 'out_db': -17.0},
    'lead': {'hp': 120, 'mid_f': 900, 'mid_db': 8, 'drive1': 25.0, 'drive2': 6.0, 'bias': 0.15,
             'bass': 0.0, 'mid': 1.0, 'treble': 1.5, 'presence': 2.5, 'out_db': -17.0},
    'clean': {'hp': 70, 'mid_f': 800, 'mid_db': 0, 'drive1': 1.2, 'drive2': 1.0, 'bias': 0.0,
              'bass': 1.0, 'mid': 0.0, 'treble': 2.0, 'presence': 1.0, 'out_db': -17.0},
}


def amp_sim(x, sr=48000, preset='high_gain', cab='v30', seed=0, oversample=4):
    """mono DI (n,) -> mono amped guitar (n,). Two asymmetric tanh stages at 4x oversampling + tone stack + cab IR."""
    P = AMP_PRESETS[preset] if isinstance(preset, str) else preset
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 2:
        x = x.mean(axis=1)
    n0 = len(x)
    # normalise DI level so the drive amounts are predictable
    rms = float(np.sqrt(np.mean(x ** 2)) + 1e-9)
    x = x * (0.1 / rms)
    x = _sos(x, [_biquad('hp', P['hp'], sr, 0.7), _biquad('peak', P['mid_f'], sr, 0.8, P['mid_db']), _biquad('lp', 7000, sr, 0.7)])
    osr = sr * oversample
    u = librosa.resample(x, orig_sr=sr, target_sr=osr, res_type='soxr_hq')
    b = P['bias']
    u = np.tanh(P['drive1'] * u + b) - math.tanh(b)
    u = _sos(u, [_biquad('hp', 25, osr, 0.7), _biquad('lp', 9000, osr, 0.7)])
    u = np.tanh(P['drive2'] * u)
    u = _sos(u, [_biquad('lp', 12000, osr, 0.7)])
    y = librosa.resample(u, orig_sr=osr, target_sr=sr, res_type='soxr_hq')[:n0]
    y = _sos(y, [_biquad('hp', 20, sr, 0.7), _biquad('lowshelf', 120, sr, 0.7, P['bass']), _biquad('peak', 500, sr, 0.9, P['mid']),
                 _biquad('highshelf', 2500, sr, 0.7, P['treble']), _biquad('peak', 3500, sr, 1.2, P['presence'])])
    y = 0.9 * np.tanh(y / 0.9 * 0.8) / 0.8  # power amp softness
    ir = make_cab_ir(sr, cab, seed=seed)
    y = _sig.fftconvolve(y, ir)[:n0].astype(np.float32)
    y = _sos(y, [_biquad('hp', 80, sr, 0.7), _biquad('lp', 9500, sr, 0.7)])
    r = float(np.sqrt(np.mean(y ** 2)) + 1e-9)
    # level: amp output is compressed by nature; fix overall to out_db RMS over sounding parts
    act = np.abs(y) > r * 0.1
    r2 = float(np.sqrt(np.mean(y[act] ** 2)) + 1e-9) if act.any() else r
    return (y * (_db(P['out_db']) / r2)).astype(np.float32)


def power_chord(root, start_s, dur_s, vel=110, intervals=(0, 7, 12), strum_s=0.006, string_base=0):
    """Notes for a power chord; each tone gets its own mono 'string' group so repeated chugs cut naturally."""
    return [{'start_s': start_s + i * strum_s, 'dur_s': dur_s, 'midi': root + iv, 'vel': vel - 3 * i,
             'group': f'str{string_base + i}'} for i, iv in enumerate(intervals)]


def guitar_render(notes, articulation='palm_mute', sr=48000, amp='high_gain', double=True, seed=0, pan_lr=0.9,
                  timing_jitter_s=0.004, length_s=None, cab=('v30', 'gb')):
    """Distorted rhythm guitar: render the DI from Emilyguitar samples, amp it, and double-track L/R."""
    takes = [(-pan_lr, 0, cab[0])] + ([(pan_lr, 1, cab[1] if len(cab) > 1 else cab[0])] if double else [])
    outs = []
    for p, k, cb in takes:
        rng = random.Random(seed * 31 + k)
        nn = []
        for q in notes:
            q2 = dict(q)
            q2['start_s'] = max(0.0, q['start_s'] + (rng.uniform(-timing_jitter_s, timing_jitter_s) if k else 0.0))
            q2.setdefault('group', 'g0')
            nn.append(q2)
        di = render(nn, 'eguitar', articulation, sr=sr, seed=seed * 7 + k, stereo=False, detune_cents=3.0 if k else 0.0,
                    length_s=length_s)
        mono = di.mean(axis=1)
        amped = amp_sim(mono, sr, amp, cab=cb, seed=k)
        outs.append(pan_stereo(np.stack([amped, amped], axis=1), p, 1.0))
    n = max(len(o) for o in outs)
    out = np.zeros((n, 2), np.float32)
    for o in outs:
        out[:len(o)] += o
    if double:
        out *= _db(-1.5)
    return out


def bass_render(notes, articulation='sustain', sr=48000, drive=0.35, seed=0, length_s=None):
    """Electric bass (Growlybass DI) with parallel drive: clean lows + driven, high-passed upper band."""
    nn = [dict(q, group=q.get('group', 'b0')) for q in notes]
    di = render(nn, 'ebass', articulation, sr=sr, seed=seed, stereo=False, length_s=length_s)[:, 0]
    clean = _sos(di, [_biquad('lp', 900, sr, 0.7)])
    rms = float(np.sqrt(np.mean(di ** 2)) + 1e-9)
    d = _sos(di * (0.1 / rms), [_biquad('hp', 300, sr, 0.7)])
    d = np.tanh(d * (4 + 30 * drive))
    d = _sos(d, [_biquad('lp', 3500, sr, 0.7), _biquad('peak', 1200, sr, 1.0, 3.0)])
    d *= rms / (float(np.sqrt(np.mean(d ** 2))) + 1e-9)
    y = clean + drive * 0.8 * d
    y = _sos(y, [_biquad('hp', 35, sr, 0.7), _biquad('lowshelf', 90, sr, 0.7, 2.0)])
    y = y.astype(np.float32)
    return np.stack([y, y], axis=1)


# ---------------------------------------------------------------------------------------------
# info
# ---------------------------------------------------------------------------------------------
def list_instruments():
    M = manifest()
    out = {}
    for inst, d in M['instruments'].items():
        out[inst] = {a: {'kind': e['kind'], 'range': e['range'], 'n_dyn': e['n_dyn'], 'n_rr': e['n_rr'],
                         'n_samples': e['n_samples'], 'source': e['source']} for a, e in d['articulations'].items()}
    return out


if __name__ == '__main__':
    import pprint
    pprint.pprint(list_instruments())
    pprint.pprint(list_drum_pieces())
