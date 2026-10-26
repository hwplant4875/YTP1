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
    'lead_violin': (-17.5, 0.34, 0.0, [HighpassFilter(190), PeakFilter(3800, -2.5, 1.0), HighShelfFilter(9000, -3),
                                       Compressor(threshold_db=-20, ratio=2.2, attack_ms=12, release_ms=160)]),
    'lead_cello': (-17.5, 0.30, 0.0, [HighpassFilter(55), PeakFilter(250, -1.5, 1.0), PeakFilter(2500, 1.5, 1.0),
                                      Compressor(threshold_db=-20, ratio=2.2, attack_ms=12, release_ms=160)]),
    'strings': (-22.0, 0.45, 0.0, [HighpassFilter(60), PeakFilter(3200, -1.5, 0.9), HighShelfFilter(10000, -2)]),
    'low_strings': (-26.0, 0.35, 0.0, [HighpassFilter(30), LowpassFilter(3000)]),
    'brass': (-24.0, 0.42, 0.0, [HighpassFilter(70), PeakFilter(1800, 1.0, 1.0)]),
    'brass_stabs': (-25.0, 0.38, 0.0, [HighpassFilter(80)]),
    'winds': (-27.0, 0.45, 0.0, [HighpassFilter(250)]),
    'choir': (-24.0, 0.48, 0.0, [HighpassFilter(110), PeakFilter(3000, 1.0, 1.0)]),
    'guitars': (-23.5, 0.0, 0.14, [HighpassFilter(85), PeakFilter(350, -2.0, 1.0), LowpassFilter(9500)]),
    'lead_guitar': (-21.0, 0.18, 0.10, [HighpassFilter(150), LowpassFilter(8500)]),
    'bass': (-22.5, 0.0, 0.04, [HighpassFilter(32), Compressor(threshold_db=-18, ratio=3.5, attack_ms=8, release_ms=120)]),
    'piano': (-25.0, 0.30, 0.0, [HighpassFilter(80)]),
    'drums': (-20.5, 0.06, 0.22, [HighpassFilter(30), Compressor(threshold_db=-16, ratio=3.0, attack_ms=4, release_ms=90)]),
    'epic_perc': (-24.0, 0.30, 0.0, [HighpassFilter(30)]),
    'fx': (-25.0, 0.20, 0.0, [HighpassFilter(25)]),
}
OVERRIDES = {}   # stem -> extra dB (tuning after review)


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


def tp_limit(m, ceiling_db=-1.3):
    """look-ahead true-peak limiter: gain from 4x-oversampled peaks, held 40 ms, smoothed 6 ms (no makeup gain)"""
    from scipy.signal import resample_poly
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    c = 10 ** (ceiling_db / 20)
    for _ in range(3):
        up = resample_poly(m, 4, 1, axis=0)
        pk = np.abs(up).max(1).reshape(-1, 4).max(1)[:len(m)]
        need = np.clip(1 - c / np.maximum(pk, 1e-9), 0, None)          # required gain reduction (linear fraction)
        hold = maximum_filter1d(need, size=int(0.040 * SR))
        red = uniform_filter1d(hold, size=int(0.006 * SR))
        red = np.maximum(red, need)
        m = m * (1 - red)[:, None]
        if (np.abs(resample_poly(m, 4, 1, axis=0)).max() <= c * 1.001):
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
        y = Pedalboard(chain)(y.T.copy(), SR).T if chain else y
        lvl = active_rms_db(y)
        g = target - lvl + OVERRIDES.get(k, 0.0)
        y = y * 10 ** (g / 20)
        report[k] = dict(active_rms_in=round(lvl, 1), gain_db=round(g, 1))
        mix[:n] += y
        hall_send[:n] += y * hs
        room_send[:n] += y * rs
    hall = conv(hall_send, hall_ir(2.6, 0.026))
    room = conv(room_send, hall_ir(0.9, 0.008, seed=7, length=1.4))
    hall = Pedalboard([HighpassFilter(180), HighShelfFilter(7000, -4)])(hall.T.copy(), SR).T
    room = Pedalboard([HighpassFilter(120)])(room.T.copy(), SR).T
    mix = mix + hall * 0.9 + room * 0.8
    mix = Pedalboard([HighpassFilter(25), Compressor(threshold_db=-16, ratio=1.8, attack_ms=30, release_ms=250),
                      LowShelfFilter(80, 0.8), HighShelfFilter(11000, 0.8)])(mix.T.copy(), SR).T
    tmp = f'{OUT}/_premaster.wav'
    sf.write(tmp, mix / max(1e-9, np.abs(mix).max()) * 0.5, SR, subtype='FLOAT')
    I, _ = lufs(tmp)
    gain = -14.0 - I + 0.0
    m = mix / max(1e-9, np.abs(mix).max()) * 0.5 * 10 ** (gain / 20)
    m = tp_limit(m.astype(np.float32), -1.3)
    # trim leading/trailing silence to the music (keep the 0.3 s pre-roll), fade the reverb tail
    nz = np.where(np.abs(m).max(1) > 10 ** (-70 / 20))[0]
    end = min(len(m), nz[-1] + int(0.2 * SR)) if len(nz) else len(m)
    m = m[:end]
    f = int(1.5 * SR)
    m[-f:] *= np.linspace(1, 0, f)[:, None] ** 2
    wav = f'{OUT}/{name}.wav'
    sf.write(wav, m.astype(np.float32), SR, subtype='PCM_24')
    I2, tp2 = lufs(wav)
    mp3 = f'{OUT}/{name}.mp3'
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', wav, '-c:a', 'libmp3lame', '-b:a', '320k', mp3], check=True)
    report['_master'] = dict(lufs=I2, true_peak=tp2, dur_s=round(len(m) / SR, 2))
    json.dump(report, open(f'{OUT}/{name}_mix_report.json', 'w'), indent=1)
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'guren_cover_draft')
