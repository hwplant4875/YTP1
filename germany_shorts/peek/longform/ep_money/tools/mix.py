#!/usr/bin/env python3
"""PEEK long-form mix: narration + Mixkit bed + SFX -> 48 kHz stereo WAV at -14 LUFS (limiter 0.79).

usage: python3 tools/mix.py <vo.wav> <out_dir> [bed_id=554]
Writes <out_dir>/mix.wav plus stems (vo/bed/sfx) for QA. Every SFX is placed on the narration
clock through js/words.js, the same word cues the scenes use, so picture and sound stay in sync.
"""
import json, os, re, subprocess, sys
import numpy as np
from scipy.signal import lfilter, resample_poly

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__)); EP = os.path.dirname(HERE)
SH = '/mnt/project-files/plans/peek/longform/ep_money'
MK = SH + '/sfx/mixkit/'
END = 227.5
N = int(round(END * SR))


# ---------------- io + loudness helpers ----------------
def dec(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)

def write(path, x, codec='pcm_s24le'):
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'f64le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', codec, path], stdin=subprocess.PIPE)
    p.stdin.write(np.ascontiguousarray(x, np.float64).tobytes()); p.stdin.close(); p.wait()

def ff(x, af, tmp):
    """run an ffmpeg audio filter on x (float WAV in and out, so nothing clips on the way)"""
    write(tmp + '_in.wav', x, 'pcm_f32le')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp + '_in.wav', '-af', af, '-c:a', 'pcm_f32le', tmp + '_out.wav'], check=True)
    y = dec(tmp + '_out.wav')[:len(x)]
    return np.pad(y, ((0, len(x) - len(y)), (0, 0)))

def vo_chain(vo, tmp):
    """narration dynamics: gentle compression on loud syllables, then a fast look-ahead peak limiter
    so the voice reaches -14 LUFS without the master limiter working on every word (PLR ~12.3 dB)"""
    vo = vo * db(-20 - integrated(vo))
    vo = ff(vo, 'acompressor=threshold=0.2:ratio=2.5:attack=5:release=100:knee=6:detection=rms:makeup=1', tmp)
    vo = vo * db(-20 - integrated(vo))
    vo = ff(vo, f'alimiter=limit={db(-20 + 12.3):.4f}:attack=1:release=40:level=0:latency=1', tmp)
    return vo

KB1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
KB2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])
def kw(x):
    y = lfilter(*KB1, x, axis=0); return lfilter(*KB2, y, axis=0)

def win_lufs(x, win, hop):
    """loudness (LUFS) of K-weighted x in windows of `win` s, every `hop` s (centered)"""
    y = kw(x); e = (y ** 2).sum(1); c = np.concatenate([[0], np.cumsum(e)])
    W, Hh = int(win * SR), int(hop * SR); n = max(1, len(x) // Hh)
    out = np.empty(n)
    for i in range(n):
        m = i * Hh; a, b = max(0, m - W // 2), min(len(x), m + W // 2)
        out[i] = -0.691 + 10 * np.log10((c[b] - c[a]) / max(1, b - a) + 1e-12)
    return out

def integrated(x):
    """BS.1770 integrated loudness (400 ms blocks, 75 % overlap, -70 abs / -10 rel gates)"""
    y = kw(x); e = (y ** 2).sum(1); c = np.concatenate([[0], np.cumsum(e)])
    B, Hh = int(0.4 * SR), int(0.1 * SR)
    z = np.array([(c[i + B] - c[i]) / B for i in range(0, len(x) - B, Hh)])
    l = -0.691 + 10 * np.log10(z + 1e-12); z = z[l > -70]
    rel = -0.691 + 10 * np.log10(z.mean()) - 10
    z = z[-0.691 + 10 * np.log10(z) > rel]
    return -0.691 + 10 * np.log10(z.mean())

def db(v): return 10 ** (v / 20)

def smoother(t):
    t = np.clip(t, 0, 1); return t * t * t * (t * (t * 6 - 15) + 10)


# ---------------- narration cues (same table as the scenes) ----------------
src = open(os.path.join(EP, 'js', 'words.js')).read()
WORDS = json.loads(re.search(r'WORDS = (\{.*\});', src, re.S).group(1))
def norm(s): return re.sub(r"[^a-z0-9'-]", '', s.lower())
def cue(beat, word, n=1):
    q = norm(word)
    for test in (lambda w: norm(w) == q, lambda w: norm(w).startswith(q)):
        c = 0
        for w, a, b in WORDS[beat]:
            if test(w):
                c += 1
                if c == n: return a
    raise KeyError(f'{beat} {word} {n}')


# ---------------- SFX ----------------
_cache = {}
def load_sfx(name):
    if name not in _cache:
        path = name if name.startswith('/') else (MK + name + '.wav' if name[0].isdigit() else SH + '/sfx/' + name + '.wav')
        _cache[name] = dec(path)
    return _cache[name]

def prep(name, trim=None, rate=1.0, rev=False):
    x = load_sfx(name)
    if trim:
        a, b = int(trim[0] * SR), int(trim[1] * SR); x = x[a:b].copy()
        f = min(len(x), int(0.012 * SR)); x[-f:] *= np.linspace(1, 0, f)[:, None]
    if rev: x = x[::-1].copy()
    if abs(rate - 1) > 1e-3:
        up = 1000; down = int(round(1000 * rate)); x = resample_poly(x, up, down, axis=0)
    return x

def onset(x):
    env = np.sqrt(np.convolve((x ** 2).sum(1), np.ones(240) / 240, 'same'))
    pk = env.max(); i = int(np.argmax(env > pk * db(-20)))
    return max(0, i - int(0.004 * SR)), int(np.argmax(env))

def peak100(x):
    """loudest 100 ms (K-weighted) of an SFX, LUFS-style"""
    if len(x) < int(0.1 * SR): x = np.pad(x, ((0, int(0.1 * SR) - len(x)), (0, 0)))
    return win_lufs(x, 0.1, 0.02).max()

EVENTS = []
SFX_TRIM = 8.5   # v1 sat under the bed; every SFX must clear the music and stay under the voice
FILE_TRIM = {'2568': 4.0, '3124': 4.0, '2073': 4.0, 'pop_soft': 3.0, '830': 3.0}   # short ticks and pops get masked by the bed
def ev(t, name, rel, align='onset', trim=None, rate=1.0, rev=False, pan=0.0):
    EVENTS.append(dict(t=t, name=name, rel=rel, align=align, trim=trim, rate=rate, rev=rev, pan=pan))

def sfx_bus(voref):
    bus = np.zeros((N, 2))
    for e in EVENTS:
        x = prep(e['name'], e['trim'], e['rate'], e['rev'])
        trim = FILE_TRIM.get(e['name'], FILE_TRIM.get(e['name'][:8], 0.0))
        g = db(voref + e['rel'] + SFX_TRIM + trim - peak100(x))
        o, pk = onset(x)
        anchor = {'onset': o, 'peak': pk, 'end': len(x)}[e['align']]
        i0 = int(round(e['t'] * SR)) - anchor
        th = (e['pan'] + 1) * np.pi / 4; pg = np.array([np.cos(th), np.sin(th)]) * np.sqrt(2)
        a, b = max(0, i0), min(N, i0 + len(x))
        if b > a: bus[a:b] += x[a - i0:b - i0] * g * pg
    return bus


# ---------------- the SFX schedule ----------------
def schedule():
    rng = np.random.default_rng(11)
    LAND = json.load(open(os.path.join(HERE, 'vland.json')))   # opening bundle landings on the VO clock
    THUDS = ['2091', '2093', '2090']; POPS = ['pop_soft_a', 'pop_soft_b', 'pop_soft_c', 'pop_soft_d']
    # opening: the hook slam, then every bundle that lands, faster and quieter as the camera lifts
    ev(0.0, '1975', -9.5); ev(0.0, 'sub_hit_warm', -9.5); ev(0.0, '2091', -12)
    for k, t in enumerate(LAND):
        ev(t, THUDS[k % 3], -9 - 3 * k / max(1, len(LAND) - 1), trim=(0, 0.22), rate=float(rng.uniform(0.94, 1.06)), pan=float(rng.uniform(-0.15, 0.15)))
    # owner 11/8: the stacking sound keeps going under the climb and only slowly fades (a dopamine bed)
    t, t0, t1 = LAND[-1], LAND[-1], 21.0
    while True:
        t += 0.058 + float(rng.uniform(-0.012, 0.012))
        if t > t1: break
        u = (t - t0) / (t1 - t0)
        ev(t, THUDS[int(rng.integers(0, 3))], -12 - 20 * u ** 1.6, trim=(0, 0.2), rate=float(rng.uniform(0.95, 1.08)), pan=float(rng.uniform(-0.25, 0.25)))
    ev(2.95, '1710', -17)                                   # the climb starts
    ev(8.49, '2568', -16)                                   # tallest-building pin
    ev(14.9, '340', -17, pan=0.2)                           # plane passes
    ev(15.86, '2870', -17)                                  # Karman ring
    ev(16.18, '3124', -18)
    ev(17.35, '1105', -17, pan=-0.15)                       # space station glides in
    ev(18.26, '2568', -17)
    ev(20.12, '1085', -15, align='end')                     # swell into the top
    ev(20.12, '1975', -10); ev(20.12, '586', -15)           # $2.8 TRILLION
    for i in range(6): ev(21.47 + 0.3 * i, POPS[i % 4], -14, rate=1 + 0.035 * i)   # seven stations
    ev(cue('b02', 'nobody') + 0.3, '1085', -16, align='end')                     # the pile turns into a ghost
    ev(31.45, '1922', -18)                                  # dissolve to the market board
    # market board
    ev(33.12, '2568', -16); ev(35.25, '2073', -16)
    for k in range(18):   # the city pops up back to front while the date is said
        ev(32.05 + 2.95 * (k + rng.uniform(-0.3, 0.3)) / 17, POPS[k % 4], -18 - rng.uniform(0, 2), rate=float(rng.uniform(0.95, 1.12)), pan=float(rng.uniform(-0.2, 0.2)))
    ev(40.28, '2150', -14); ev(40.36, '3124', -18)          # the whole market drops
    ev(43.05, '2568', -17)
    for k in range(3): ev(50.33 + 0.07 * k, POPS[k], -18)   # chip makers bump
    ev(52.77, '2073', -17); ev(53.28, '830', -14); ev(53.53, '2568', -17)
    ev(56.2, '2150', -15); ev(56.35, '2093', -15)           # Qualcomm and Arm fall
    ev(58.3, '1105', -16); ev(58.78, '3124', -18)           # the question mark swings in
    ev(61.45, '340', -16)                                   # data center slides in
    ev(62.98, '830', -14); ev(63.13, '2568', -17)
    for n in range(0, 40, 8): ev(61.85 + n * 0.11 + 1.25, '830', -21, rate=1.35)   # bundles arrive
    ev(66.2, '1688', -17)                                   # question mark leaves
    ev(68.1, '1922', -14); ev(68.27, '3124', -15)           # keyhole
    # Nvidia
    ev(71.6, '2568', -16); ev(72.91, '830', -15)
    ev(76.2, '2568', -15); ev(77.18, '2091', -15)
    ev(80.38, '1922', -17, trim=(0, 0.35), rate=1.3)        # Wednesday -> Thursday flip
    ev(82.75, '2299', -12)                                  # $200 -> $182
    ev(84.0, '2568', -17)
    ev(91.31, '2073', -17)
    ev(94.3, '340', -17); ev(95.48, '2093', -14); ev(95.53, '1975', -11)   # NEARLY $450 BILLION
    ev(101.5, '2640', -16, align='end'); ev(101.5, '1975', -12)            # stack passes the space station
    ev(101.9, '1105', -17); ev(102.7, '2568', -17)
    ev(105.4, '1688', -17)
    ev(107.6, '1105', -16); ev(107.62, '3124', -17)        # cutaway
    ev(108.82, '340', -17); ev(110.8, '2568', -17)
    ev(114.65, '1710', -15)                                 # shares burst out of the company
    for k in range(10): ev(115.97 + 1.38 * k / 9, '830', -20, rate=float(rng.uniform(1.15, 1.45)), pan=float(rng.uniform(-0.25, 0.25)))
    ev(116.82, '2568', -17); ev(118.58, '2073', -16)
    ev(120.17, '3124', -18); ev(123.41, '3124', -18); ev(124.89, '2091', -14)
    ev(126.53, '2150', -15)
    ev(130.32, '3124', -18); ev(131.65, '3124', -18); ev(132.8, '3144', -13)   # -$448 BILLION
    ev(133.82, '2150', -14)                                 # every share re-priced at once
    ev(135.85, '1710', -16, align='end', rev=True)          # rewind
    for k in range(4): ev(139.33 + 0.07 * k, POPS[k], -18)  # 300 million traded
    ev(141.49, '340', -17); ev(145.47, '2568', -17)
    ev(148.69, '2091', -13); ev(148.72, '2568', -16)        # 1 in 80
    for k in range(8): ev(154.83 + 0.5 * k / 7, '3124', -19 - k * 0.3, rate=float(rng.uniform(0.9, 1.1)))   # re-price wave
    ev(154.85, '2150', -16)
    ev(158.68, '2568', -17); ev(159.21, '2073', -16)
    ev(162.6, '1922', -17)                                  # to the vaults
    # cash moves
    ev(162.8, '2093', -14, rate=0.8); ev(163.0, '2093', -14, rate=0.78)
    ev(165.87, 'pop_soft_b', -14)
    ev(166.6, '340', -16); ev(167.75, '830', -14)
    ev(169.7, '1105', -16); ev(170.9, '2091', -14)
    ev(172.19, '2568', -16)
    for k in range(10): ev(174.3 + 1.3 * k / 9, '830', -21, rate=float(rng.uniform(1.2, 1.5)), pan=float(rng.uniform(-0.25, 0.25)))
    # the turn: first sound after the near-silence
    ev(cue('b08', "That's"), '1975', -9.5); ev(cue('b08', "That's"), 'sub_hit_warm', -10.5)
    ev(cue('b08', 'never') + 0.08, '1085', -15, align='end')   # the pile becomes a ghost
    ev(184.09, '1922', -18)
    ev(cue('b08', 'price') - 0.12, '340', -16); ev(cue('b08', 'price') + 0.42, '3124', -17)   # price tag drops in
    ev(cue('b08', 'whole'), '1710', -17, rate=0.85)        # dashed rim around the market
    ev(cue('b08', 'shrank'), '2150', -13); ev(cue('b08', 'shrank') + 0.05, '1922', -17, trim=(0, 0.35), rate=1.3)
    # savings
    ev(191.35, '1688', -17)
    ev(cue('b09', 'matter') - 0.62, '830', -14); ev(cue('b09', 'matter') - 0.40, '830', -14, rate=0.92)
    for k in range(10): ev(cue('b09', 'millions') + 0.8 * k / 9, POPS[k % 4], -19, rate=float(rng.uniform(0.95, 1.15)), pan=float(rng.uniform(-0.25, 0.25)))
    ev(cue('b09', 'shrink') - 0.05, '2150', -14)
    ev(cue('b09', 'sells'), '1922', -17, trim=(0, 0.35), rate=1.3)
    ev(cue('b09', 'paid'), '2091', -14)
    ev(cue('b09', 'Nvidia') + 0.06, '2326', -16)
    ev(cue('b09', 'up'), '586', -14)                        # +2.8 %
    ev(212.2, '1922', -18)
    # ending
    ev(cue('b10', 'billions') - 0.1, '2091', -12)
    ev(cue('b10', 'vanished') - 0.05, '2093', -12)
    ev(cue('b10', 'repriced') - 0.15, '1922', -14); ev(cue('b10', 'repriced') - 0.05, '2070', -12)
    ev(cue('b10', 'Did') - 0.1, '830', -13)
    ev(cue('b10', 'November') - 0.1, '2093', -13)


# ---------------- music bed ----------------
def splice_to(x, J, K, lag_search=0.03, w=0.25):
    """refine jump target K (s) so the audio after K matches the audio after J; returns K'"""
    m = x.mean(1); a = m[int((J - w) * SR):int((J + w) * SR)]
    best, bk = -2, K
    for d in np.arange(-lag_search, lag_search + 1e-9, 1 / SR * 4):
        s = int(round((K + d - w) * SR)); b = m[s:s + len(a)]
        c = float(np.dot(a, b) / np.sqrt(np.dot(a, a) * np.dot(b, b) + 1e-12))
        if c > best: best, bk = c, K + d
    return bk, best

def highshelf(f0, gain_db, q=0.7071):
    A = 10 ** (gain_db / 40); w0 = 2 * np.pi * f0 / SR; al = np.sin(w0) / (2 * q); cw = np.cos(w0)
    b = [A * ((A + 1) + (A - 1) * cw + 2 * np.sqrt(A) * al), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - 2 * np.sqrt(A) * al)]
    a = [(A + 1) - (A - 1) * cw + 2 * np.sqrt(A) * al, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - 2 * np.sqrt(A) * al]
    return np.array(b) / a[0], np.array(a) / a[0]

BEDS = {
    # track 554: 128 BPM; its own break (181.5-185 s) lands on the near-silence before beat 8 and its
    # lift (185.12 s) on "That's the answer"; two jump-backs inside the last section (8 bars, then 4)
    # carry it to the end of the video before its own fade-out starts under the closing question
    '554': dict(file=SH + '/music/mixkit_554.mp3', inpt=7.939, jumps=[(202.704, 187.704), (201.298, 193.798)], brk=(172.8, 176.6, 177.1), tail=218.5),
}

def bed_track(bid):
    B = BEDS[bid]; x = dec(B['file'])
    pieces, pos = [], B['inpt']; fade = int(0.02 * SR)
    for J, K in B['jumps']:
        K2, c = splice_to(x, J, K); print(f'  jump {J:.3f} -> {K:.3f} refined {K2:.4f} corr {c:.2f}')
        pieces.append((pos, J)); pos = K2
    pieces.append((pos, pos + END + 1))
    out = np.zeros((0, 2))
    for i, (a, b) in enumerate(pieces):
        seg = x[int(a * SR) - (fade if i else 0): int(b * SR) + fade].copy()
        if i:   # equal-gain crossfade, 20 ms either side of the splice
            r = np.linspace(0, 1, 2 * fade)[:, None]
            seg[:2 * fade] = seg[:2 * fade] * r + out[-2 * fade:] * (1 - r); out = out[:-2 * fade]
        out = np.concatenate([out, seg])
    out = out[:N]
    if len(out) < N: out = np.pad(out, ((0, N - len(out)), (0, 0)))
    b, a = highshelf(3000, -4.0); out = lfilter(b, a, out, axis=0)
    return out, B

def bed_gain(bed, B):
    """gain curve: hook loud, drains to -27 LUFS by 12 s, holds -27; the track's own break and
    final fade are left alone; short lift at the turn; last 1.1 s fades to silence"""
    hop = 0.1; L = win_lufs(bed, 3.0, hop); t = np.arange(len(L)) * hop
    b0, b1, b2 = B['brk']
    after = (t >= b2) & (t < b2 + 1.6); L[after] = L[np.searchsorted(t, b2 + 1.6)]   # window must not see the break
    T = np.where(t < 2.6, -21.0, -21.0 + (-27.0 + 21.0) * smoother((t - 2.6) / 9.4))
    lift = (t > b2) & (t < 182.5); T[lift] = -25.5 - 1.5 * smoother((t[lift] - 179.5) / 3.0)
    g = np.clip(T - L, -14, 8)
    hold = (t >= b0) & (t < b1); g[hold] = g[np.searchsorted(t, b0)]
    ramp = (t >= b1) & (t < b2); gi = g[np.searchsorted(t, b2)]
    g[ramp] = g[np.searchsorted(t, b0)] + (gi - g[np.searchsorted(t, b0)]) * smoother((t[ramp] - b1) / (b2 - b1))
    g[t >= B['tail']] = g[np.searchsorted(t, B['tail'])]
    k = int(1.5 / hop); gs = np.convolve(np.pad(g, k, mode='edge'), np.ones(2 * k + 1) / (2 * k + 1), 'valid')
    keep = (t >= b0 - 0.5) & (t < b2 + 0.4); gs[keep] = g[keep]     # break edges stay exact
    gs[t < 3.0] = g[t < 3.0]
    ts = np.arange(N) / SR; G = db(np.interp(ts, t, gs))
    G *= np.where(ts > END - 1.1, np.cos(np.clip((ts - (END - 1.1)) / 1.1, 0, 1) * np.pi / 2) ** 2, 1.0)
    return G[:, None]


def main():
    vo_path, out = sys.argv[1], sys.argv[2]; bid = sys.argv[3] if len(sys.argv) > 3 else '554'
    os.makedirs(out, exist_ok=True)
    vo = dec(vo_path)[:N]; vo = np.pad(vo, ((0, N - len(vo)), (0, 0)))
    vo = vo_chain(vo, os.path.join(out, 'tmp_vo'))
    vo *= db(-14.3 - integrated(vo))
    L100 = win_lufs(vo, 0.1, 0.05); voref = float(np.median(L100[L100 > -40]))
    print(f'VO -14.3 LUFS, typical 100 ms loudness {voref:.1f}')
    bed, B = bed_track(bid); bed = bed * bed_gain(bed, B)
    schedule(); sfx = sfx_bus(voref)
    print(f'{len(EVENTS)} sfx events')
    mix = vo + bed + sfx
    gf = db(-14.0 - integrated(mix)); mix *= gf
    write(os.path.join(out, 'mix_pre.wav'), mix, 'pcm_f32le')
    for name, s in (('vo', vo), ('bed', bed), ('sfx', sfx)): write(os.path.join(out, f'stem_{name}.wav'), s * gf, 'pcm_f32le')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(out, 'mix_pre.wav'), '-af', 'alimiter=limit=0.79:attack=5:release=60:level=0:latency=1', '-c:a', 'pcm_s24le', os.path.join(out, 'mix.wav')], check=True)
    for f in ('tmp_vo_in.wav', 'tmp_vo_out.wav'): os.remove(os.path.join(out, f))
    print('done', out)

if __name__ == '__main__':
    main()
