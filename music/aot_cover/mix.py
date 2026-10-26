"""Mix the cover stems: active-level gain staging, EQ/compression per stem, two convolution reverbs
(synthetic concert hall + drum room), master glue, loudness to -14 LUFS, true peak <= -1 dBTP.

usage: python3 -I mix.py [out_name]
"""
import json, os, sys, subprocess, math
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve
from pedalboard import (Pedalboard, HighpassFilter, LowpassFilter, HighShelfFilter, LowShelfFilter, PeakFilter,
                        Compressor, Limiter, Gain)

A = '/tmp/claude-0/aotmusic'
STEMS = A + '/arr/out/stems'
OUT = A + '/arr/out'
SR = 48000

# stem -> (target active RMS dBFS, hall send, room send, fx chain)
CFG = {
    'lead_violin': (-17.5, 0.28, 0.0, [HighpassFilter(190), Compressor(threshold_db=-16, ratio=3.0, attack_ms=1.0, release_ms=90),
                                       PeakFilter(3400, -3.5, 0.8), HighShelfFilter(9000, -3),
                                       Compressor(threshold_db=-20, ratio=2.2, attack_ms=12, release_ms=160)]),
    'lead_cello': (-17.5, 0.26, 0.0, [HighpassFilter(55), Compressor(threshold_db=-14, ratio=4.0, attack_ms=1.0, release_ms=90),
                                      PeakFilter(250, -1.5, 1.0), PeakFilter(2500, 1.5, 1.0),
                                      Compressor(threshold_db=-20, ratio=2.2, attack_ms=12, release_ms=160),
                                      Limiter(threshold_db=-9, release_ms=60)]),
    'strings': (-22.0, 0.34, 0.0, [HighpassFilter(60), PeakFilter(3200, -1.5, 0.9), HighShelfFilter(10000, -2)]),
    'low_strings': (-26.0, 0.28, 0.0, [HighpassFilter(30), LowpassFilter(3000)]),
    'brass': (-24.0, 0.34, 0.0, [HighpassFilter(70), PeakFilter(1800, 1.0, 1.0)]),
    'brass_stabs': (-25.0, 0.30, 0.0, [HighpassFilter(80)]),
    'winds': (-27.0, 0.36, 0.0, [HighpassFilter(250)]),
    'choir': (-24.0, 0.38, 0.0, [HighpassFilter(140), PeakFilter(3000, 1.0, 1.0)]),
    'guitars': (-23.5, 0.0, 0.14, [HighpassFilter(85), PeakFilter(350, -2.0, 1.0), PeakFilter(3000, -1.5, 1.0), LowpassFilter(12000)]),
    'lead_guitar': (-21.0, 0.18, 0.10, [HighpassFilter(150), LowpassFilter(10000)]),
    'bass': (-22.5, 0.0, 0.04, [HighpassFilter(32), PeakFilter(72, 4.0, 0.8), PeakFilter(160, -2.0, 1.2), PeakFilter(1200, -3.0, 0.8),
                                LowpassFilter(3000), Compressor(threshold_db=-18, ratio=3.5, attack_ms=8, release_ms=120)]),
    'piano': (-25.0, 0.30, 0.0, [HighpassFilter(80)]),
    'drums': (-20.5, 0.06, 0.22, [HighpassFilter(40), PeakFilter(48, -3.0, 1.4), PeakFilter(95, 2.0, 1.0), PeakFilter(3500, 2.0, 1.0),
                                  HighShelfFilter(6000, 2.0), Compressor(threshold_db=-16, ratio=3.0, attack_ms=4, release_ms=90)]),
    'epic_perc': (-24.0, 0.22, 0.0, [HighpassFilter(30)]),
    'fx': (-25.0, 0.20, 0.0, [HighpassFilter(25)]),
}
OVERRIDES = {'lead_violin': -0.5}   # stem -> extra dB (tuning after review)
DELAY_MS = {'lead_violin': 20.0, 'lead_cello': 22.0}     # the solo sampler speaks ~20 ms ahead of the grid
LR_DB = {'strings': (-1.5, 1.5)}                         # riffs leaned left (violins1 + violins2 both left)

# section automation (dB, after gain staging, 2-beat ramps): the song's shape. Keys are section names or (bar_from, bar_to).
SEC_GAIN = {
    'guitars': {'band_entry': -3, 'main_riff': 1, 'verse1': -6, 'prechorus1': -3, 'interlude_groove': -4, 'verse2': -4.5,
                'jaeger_call_response': -3, 'instrumental_break': 2, 'narration': -4, 'bridge': -7, 'build_prechorus3': -2,
                'outro_riff': 1, 'outro_groove': 3, 'outro_G_ending': 3},
    'drums': {'band_entry': 6, 'verse1': -4, 'interlude_groove': -3.5, 'verse2': -2.5, 'narration': -2, 'bridge': -4,
              'chorus1': 2.5, 'jaeger_call_response': 1, 'final_chorus': 3, 'outro_G_ending': 4},
    'lead_guitar': {'instrumental_break': 4, 'outro_groove': 5, 'outro_G_ending': 5},
    'choir': {'band_entry': 4, 'chorus1': 6, 'jaeger_call_response': 5, 'final_chorus': 6},
    'brass_stabs': {'band_entry': 3, 'jaeger_call_response': 5},
    'brass': {'chorus1': 5, 'final_chorus': 6, 'build_prechorus3': 2, 'outro_G_ending': 3},
    'strings': {'main_riff': -2, 'interlude_riff': -2, 'outro_riff': -2, 'verse1': 2, 'interlude_groove': 4, 'verse2': 2,
                (148, 157): 3, 'outro_G_ending': 3},
    'low_strings': {'outro_G_ending': 3},
    'winds': {'verse1': 2, 'interlude_groove': 4, 'verse2': 2},
    'epic_perc': {'band_entry': 6},
    'piano': {'bridge': 3, (76, 80): 5},
    'bass': {'verse1': -2, 'chorus1': 1, 'final_chorus': 1.5},
    'lead_cello': {'verse1': 6.5, 'prechorus1': 4.5, 'final_chorus': -1.0},
    'lead_violin': {'chorus1': 4.2, 'verse2': 0.8, 'prechorus2': 1.5, 'jaeger_call_response': 3.2, 'bridge': 1.8,
                    'build_prechorus3': 1.1, 'final_chorus': -1.0},
}
# whole-mix contour (measured against the original's per-section loudness): riffs and the instrumental sections
# back up, the narration valley not too deep, crescendos into each chorus
BUS_GAIN = {'band_entry': 2.5, 'main_riff': 3, 'prechorus1': 1, 'chorus1': -1, 'interlude_riff': 3, 'interlude_groove': 3.5,
            'verse2': -1.5, 'instrumental_break': 1.5, 'narration': 4, 'bridge': -1, 'outro_riff': 3, 'outro_groove': 3.5,
            (50, 51): 1, (51, 52): 2.5, (106, 107): 1, (107, 108): 2.5, (189, 193): -1, (193, 195): 1, (195, 197): 3,
            'final_chorus': 0.5, 'outro_G_ending': 2.5}
SEC_EQ = {'guitars': {'verse2': [PeakFilter(400, -3.0, 1.0)]}}   # verse 2 guitars were boxy

G = json.load(open(A + '/analysis/grid.json'))
BEAT, FIRST = G['beat_s'], G['first_beat_t']
SECS = {x['name']: (x['bar_start'], x['bar_end_exclusive']) for x in G['sections']}


def bar_t(bar):
    """cover time of a bar downbeat (cover starts on bar 17 with 0.30 s pre-roll)"""
    return (bar - 17) * 4 * BEAT + 0.30


def spans(spec):
    for k, db in spec.items():
        a, b = SECS[k] if isinstance(k, str) else k
        yield bar_t(a), bar_t(b), db


def curve_db(spec, n):
    from scipy.ndimage import uniform_filter1d
    g = np.zeros(n, np.float32)
    for a, b, db in spans(spec):
        g[max(0, int(a * SR)):max(0, int(b * SR))] += db
    return uniform_filter1d(g, size=int(2 * BEAT * SR), mode='nearest')


def apply_curve(y, spec):
    return y * (10 ** (curve_db(spec, len(y)) / 20)).astype(np.float32)[:, None]


def section_eq(y, spec):
    """blend to an EQ'd copy inside the given sections"""
    for key, chain in spec.items():
        w = np.clip(curve_db({key: 1.0}, len(y)), 0, 1)[:, None]
        yf = Pedalboard(chain)(y.T.copy(), SR).T
        y = y * (1 - w) + yf * w
    return y.astype(np.float32)


def align_lr(y, max_ms=5.0):
    """remove an inter-channel delay (comb filtering in mono) without narrowing the image"""
    from scipy.signal import butter, sosfilt, correlate
    sos = butter(2, [1000, 3000], 'band', fs=SR, output='sos')
    act = np.where(np.abs(y).max(1) > 1e-3)[0]
    if len(act) < SR:
        return y, 0
    seg = slice(act[0], min(len(y), act[0] + 60 * SR))
    l, r = sosfilt(sos, y[seg, 0]), sosfilt(sos, y[seg, 1])
    m = int(max_ms * SR / 1000)
    c = correlate(l, r, 'full', method='fft')
    mid = len(r) - 1
    lag = int(np.argmax(c[mid - m:mid + m + 1])) - m      # >0: right channel lags behind left
    if lag > 0:
        y = np.stack([y[:, 0], np.concatenate([y[lag:, 1], np.zeros(lag, np.float32)])], 1)
    elif lag < 0:
        y = np.stack([np.concatenate([y[-lag:, 0], np.zeros(-lag, np.float32)]), y[:, 1]], 1)
    return y.astype(np.float32), lag


def lr_balance_db(y):
    a = np.sqrt((y.astype(np.float64) ** 2).mean(0) + 1e-12)
    return float(20 * np.log10(a[0] / a[1]))


def active_rms_db(y, thr_db=-55.0, win=4800):
    m = y.mean(1)
    n = len(m) // win
    if n == 0:
        return -120.0
    e = (m[:n * win].reshape(n, win) ** 2).mean(1)
    edb = 10 * np.log10(e + 1e-12)
    act = e[edb > max(thr_db, edb.max() - 30)]
    return float(10 * np.log10(act.mean() + 1e-12)) if len(act) else -120.0


def hall_ir(rt60=2.6, pre=0.024, seed=1, length=3.4):
    rng = np.random.default_rng(seed)
    n = int(length * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2), np.float32)
    for c in range(2):
        x = rng.standard_normal(n)
        # frequency-dependent decay: split into 3 bands with different RT60
        from scipy.signal import butter, sosfilt
        lo = sosfilt(butter(2, 400, 'low', fs=SR, output='sos'), x)
        hi = sosfilt(butter(2, 4000, 'high', fs=SR, output='sos'), x)
        mid = x - lo - hi
        env = lambda r: np.exp(-6.91 * t / r)
        y = lo * env(rt60 * 1.15) + mid * env(rt60) + hi * env(rt60 * 0.55)
        y *= np.minimum(1, t / 0.012)          # soft onset
        # early reflections
        for k in range(10):
            d = pre + rng.uniform(0.004, 0.07)
            i = int(d * SR)
            y[i] += rng.uniform(0.3, 0.8) * (1 if rng.random() > 0.5 else -1) * 12
        ir[:, c] = y
    ir[: int(pre * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum(0, keepdims=True))
    return ir


def tp_limit(m, ceiling_db=-1.3, release_ms=120.0):
    """look-ahead true-peak limiter: gain from 4x-oversampled peaks, 5 ms look-ahead hold, exponential release
    at 1 ms control rate (no makeup gain)"""
    from scipy.signal import resample_poly
    from scipy.ndimage import maximum_filter1d
    c = 10 ** (ceiling_db / 20)
    hop = SR // 1000
    for _ in range(4):
        up = resample_poly(m, 4, 1, axis=0)
        pk = np.abs(up).max(1).reshape(-1, 4).max(1)[:len(m)]
        nb = int(np.ceil(len(m) / hop))
        pkb = np.pad(pk, (0, nb * hop - len(pk))).reshape(nb, hop).max(1)
        need = np.clip(1 - c / np.maximum(pkb, 1e-9), 0, None)
        need = maximum_filter1d(need, size=11)                      # +-5 ms around each peak
        a = np.exp(-1.0 / release_ms)
        red = np.empty_like(need)
        r = 0.0
        for k in range(nb):                                         # instant attack, smooth release
            r = need[k] if need[k] > r else r * a
            red[k] = r
        g = np.interp(np.arange(len(m)), np.arange(nb) * hop + hop / 2, 1 - red).astype(np.float32)
        m = m * g[:, None]
        if np.abs(resample_poly(m, 4, 1, axis=0)).max() <= c * 1.001:
            break
    return m.astype(np.float32)


def conv(x, ir):
    return np.stack([fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in range(2)], 1).astype(np.float32)


def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    tail = r[r.rfind('Summary:'):]
    I = float(tail.split('I:')[1].split('LUFS')[0])
    tp = float(tail.split('Peak:')[1].split('dBFS')[0])
    return I, tp


def measure_lufs(x, tag='_tmp'):
    tmp = f'{OUT}/{tag}.wav'
    sf.write(tmp, x.astype(np.float32), SR, subtype='FLOAT')
    I, tp = lufs(tmp)
    os.remove(tmp)
    return I, tp


def main(name):
    files = {f[:-4]: f for f in os.listdir(STEMS) if f.endswith('.wav')}
    mix = None
    hall_send = room_send = None
    report = {}
    for k, (target, hs, rs, chain) in CFG.items():
        if k not in files:
            continue
        y, sr = sf.read(f'{STEMS}/{files[k]}', dtype='float32', always_2d=True)
        assert sr == SR
        if mix is None:
            mix = np.zeros_like(y)
            hall_send = np.zeros_like(y)
            room_send = np.zeros_like(y)
        n = min(len(y), len(mix))
        y = y[:n]
        info = {}
        if k in DELAY_MS:
            d = int(DELAY_MS[k] * SR / 1000)
            y = np.concatenate([np.zeros((d, 2), np.float32), y[:-d]])
        if k.startswith('lead_'):
            y, info['lr_lag'] = align_lr(y)
            b = lr_balance_db(y)
            y = y * np.array([10 ** (-b / 40), 10 ** (b / 40)], np.float32)
            info['lr_bal_fixed_db'] = round(b, 2)
        if k in LR_DB:
            y = y * np.array([10 ** (LR_DB[k][0] / 20), 10 ** (LR_DB[k][1] / 20)], np.float32)
        if k in SEC_EQ:
            y = section_eq(y, SEC_EQ[k])
        y = Pedalboard(chain)(y.T.copy(), SR).T if chain else y
        lvl = active_rms_db(y)
        g = target - lvl + OVERRIDES.get(k, 0.0)
        y = y * 10 ** (g / 20)
        if k in SEC_GAIN:
            y = apply_curve(y, SEC_GAIN[k])
        report[k] = dict(active_rms_in=round(lvl, 1), gain_db=round(g, 1), **info)
        if os.environ.get('MIX_DUMP'):
            from scipy.signal import resample_poly
            os.makedirs(os.environ['MIX_DUMP'], exist_ok=True)
            np.save(f"{os.environ['MIX_DUMP']}/{k}.npy", resample_poly(y, 1, 2, axis=0).astype(np.float16))
        mix[:n] += y
        hall_send[:n] += y * hs
        room_send[:n] += y * rs
    hall = conv(hall_send, hall_ir(2.0, 0.032))
    room = conv(room_send, hall_ir(0.9, 0.008, seed=7, length=1.4))
    hall = Pedalboard([HighpassFilter(250), HighShelfFilter(7000, -4)])(hall.T.copy(), SR).T
    room = Pedalboard([HighpassFilter(120)])(room.T.copy(), SR).T
    mix = mix + hall * 0.9 + room * 0.8
    mix = apply_curve(mix, BUS_GAIN)
    # glue: bus at -18 LUFS, so the gentle compressor only rides the loudest passages instead of pumping on every beat
    I0, _ = measure_lufs(mix)
    mix = mix * 10 ** ((-18.0 - I0) / 20)
    mix = Pedalboard([HighpassFilter(25), Compressor(threshold_db=-10, ratio=1.5, attack_ms=30, release_ms=400),
                      LowShelfFilter(80, 0.8), HighShelfFilter(12000, 1.5)])(mix.T.copy(), SR).T
    I, _ = measure_lufs(mix)
    m = mix * 10 ** ((-14.0 - I) / 20)
    m = tp_limit(m.astype(np.float32), -1.3)
    # trim leading/trailing silence to the music (keep the 0.3 s pre-roll), fade the reverb tail
    nz = np.where(np.abs(m).max(1) > 10 ** (-70 / 20))[0]
    end = min(len(m), nz[-1] + int(0.2 * SR)) if len(nz) else len(m)
    m = m[:end]
    f = int(3.0 * SR)
    m[-f:] *= np.linspace(1, 0, f)[:, None] ** 2
    wav = f'{OUT}/{name}.wav'
    sf.write(wav, m.astype(np.float32), SR, subtype='PCM_24')
    I2, tp2 = lufs(wav)
    mp3 = f'{OUT}/{name}.mp3'
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', wav, '-c:a', 'libmp3lame', '-b:a', '320k', mp3], check=True)
    report['_master'] = dict(lufs=I2, true_peak=tp2, dur_s=round(len(m) / SR, 2), bus_lufs_in=round(I0, 2))
    json.dump(report, open(f'{OUT}/{name}_mix_report.json', 'w'), indent=1)
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'guren_cover_draft')
