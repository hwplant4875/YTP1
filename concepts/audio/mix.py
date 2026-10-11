# Audio beds for the three previews. usage: python3 mix.py map|marble|lies
import json, subprocess, sys, math, wave
import numpy as np
C = '/home/user/YTP1/concepts'
SFX = '/mnt/project-files/sfx/drive/'
SR = 48000

def load(path, dur=None, ss=0):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(ss), '-i', path] + (['-t', str(dur)] if dur else []) + ['-f', 'f32le', '-ac', '2', '-ar', str(SR), '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()

def place(buf, clip, t, gain=1.0):
    i = int(t * SR); n = min(len(clip), len(buf) - i)
    if n > 0: buf[i:i + n] += clip[:n] * gain

def db(x): return 10 ** (x / 20)

def write(buf, out):
    peak = np.abs(buf).max(); print('peak before limit', round(float(peak), 2)); buf = buf / max(1.0, peak / 0.95)
    with wave.open(out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(buf, -1, 1) * 32767).astype(np.int16).tobytes())

def music(path, dur, ss=0, fin=1.0, fout=2.0, gain_db=-14):
    m = load(path, dur, ss); out = np.zeros((int(dur * SR), 2), np.float32); out[:len(m)] = m[:len(out)]
    t = np.arange(len(out)) / SR
    env = np.clip(t / fin, 0, 1) * np.clip((dur - t) / fout, 0, 1)
    return out * env[:, None] * db(gain_db)

def click(rng, strength):
    # glass marble hitting a hard rail: two damped partials plus a short noise transient
    n = int(0.06 * SR); t = np.arange(n) / SR
    f1, f2 = rng.uniform(2300, 3600), rng.uniform(5200, 7400)
    s = 0.6 * np.sin(2 * np.pi * f1 * t) * np.exp(-t * 90) + 0.35 * np.sin(2 * np.pi * f2 * t) * np.exp(-t * 140)
    s += rng.normal(0, 1, n) * np.exp(-t * 900) * 0.5
    pan = rng.uniform(-0.6, 0.6)
    return np.stack([s * (1 - pan) * 0.5, s * (1 + pan) * 0.5], 1).astype(np.float32) * strength

what = sys.argv[1]
if what == 'map':
    D = 40.0
    buf = music(f'{C}/audio/five_armies.mp3', D, ss=0, fin=0.8, fout=2.5, gain_db=-9)
    whoosh = load(SFX + '008_바림소리(다가와서사라지는).mp3')
    place(buf, whoosh, 3.2, db(-14)); place(buf, whoosh, 25.0, db(-15)); place(buf, whoosh, 35.2, db(-16))
    ding = load(SFX + '015_띠링.mp3')
    route = json.load(open(f'{C}/map/data/route.json'))
    # pin times are logged by the scene; approximate from the timeline keys used there
    K = [(0, 0), (6.2, 0), (8.5, .02), (12.5, .24), (16.5, .47), (19.5, .56), (22.5, .742), (25.5, .83), (28.5, .905), (31.0, .929), (33.2, .935), (35.6, 1.0)]
    for m in route['marks']:
        f = m['frac']; tt = 6.2 if f == 0 else next(K[i-1][0] + (f - K[i-1][1]) / (K[i][1] - K[i-1][1]) * (K[i][0] - K[i-1][0]) for i in range(1, len(K)) if K[i][1] >= f - 1e-4)
        place(buf, ding, tt, db(-22))
    write(buf, f'{C}/out/map_audio.wav')
elif what == 'marble':
    # usage: mix.py marble [boom|stone]   v3: low thumps only (user: quiet Vine Boom feel; bright clicks are grating)
    import os
    RACE = os.environ.get('RACE', 'race.json')
    R = json.load(open(f'{C}/marble/{RACE}'))
    style = sys.argv[2] if len(sys.argv) > 2 else 'boom'
    fps = R['fps']
    # timeline, same as marble/scene.js TIMING / timeline()
    LEAD, PRE, POST, RATE, END = -0.8, 1.0, 0.35, 0.3, 2.8
    tw = min(r['finish'] for r in R['res']); last_f = max(r['finish'] for r in R['res'])
    A, B = tw - PRE, tw + POST; tA = A + LEAD; span = (B - A) / RATE
    vt = lambda s: s + LEAD if s < A else (tA + (s - A) / RATE if s < B else tA + span + (s - B))
    D = vt(last_f) + END
    buf = music(f'{C}/audio/Run_Amok.mp3', D, ss=1.68, fin=0.02, fout=2.5, gain_db=-1)
    import os
    if os.environ.get('SOLO') == 'music': HITS = 0
    else: HITS = 1
    if os.environ.get('SOLO') == 'hits': buf[:] = 0
    tt = np.arange(len(buf)) / SR
    duck = 1 - 0.55 * np.clip((tt - tA + 0.3) / 0.4, 0, 1) * np.clip((tA + span + 0.3 - tt) / 0.4, 0, 1)
    buf *= duck[:, None]
    def lowpass(x, fc):
        a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); acc = 0.0
        for n in range(len(x)): acc = (1 - a) * x[n] + a * acc; y[n] = acc
        return y
    def thump(f0, dur, rng):
        n = int(dur * SR); t = np.arange(n) / SR
        fr = f0 * (1 + 1.3 * np.exp(-t / 0.035)); ph = 2 * np.pi * np.cumsum(fr) / SR
        body = np.tanh(1.8 * np.sin(ph)) * np.minimum(1, t / 0.004) * np.exp(-t / (dur / 3.2))
        click = lowpass(rng.normal(0, 1, n) * np.exp(-t / 0.004), 900) * 0.6
        return (body + click).astype(np.float32)
    def knock(f0, rng):  # dull stone tok: short low-mid body + muffled contact noise
        n = int(0.22 * SR); t = np.arange(n) / SR
        body = (np.sin(2 * np.pi * f0 * t) + 0.45 * np.sin(2 * np.pi * f0 * 2.31 * t) * np.exp(-t / 0.02)) * np.minimum(1, t / 0.0015) * np.exp(-t / 0.045)
        noise = lowpass(rng.normal(0, 1, n) * np.exp(-t / 0.006), 1400) * 0.9
        return (body + noise).astype(np.float32)
    def wood(f0, rng):  # hollow wooden block: low partials, soft attack, quick decay (no bright ring)
        n = int(0.25 * SR); t = np.arange(n) / SR
        body = (np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.06) + 0.5 * np.sin(2 * np.pi * f0 * 2.76 * t) * np.exp(-t / 0.018) + 0.2 * np.sin(2 * np.pi * f0 * 5.4 * t) * np.exp(-t / 0.008)) * np.minimum(1, t / 0.002)
        noise = lowpass(rng.normal(0, 1, n) * np.exp(-t / 0.003), 2000) * 0.5
        return (body + noise).astype(np.float32)
    rng = np.random.default_rng(11)
    HIT_DB = {'boom': -19, 'stone': -11, 'wood': -12, 'click': 4}
    bank = {}
    def voice(r, slow):
        key = (round(r, 2), slow)
        if key not in bank:
            if style == 'boom': bank[key] = [thump((62 - 26 * min(1, (r - 0.2) / 0.7)) * (0.8 if slow else 1), 0.9 if slow else 0.6, rng) for _ in range(3)]
            elif style == 'wood': bank[key] = [wood((420 - 200 * min(1, (r - 0.2) / 0.7)) * (0.8 if slow else 1) * rng.uniform(0.96, 1.04), rng) for _ in range(3)]
            elif style == 'click': bank[key] = [click(rng, 1.0)[:, 0] * 2 for _ in range(3)]  # v1/v2 glass click (user liked the first video)
            else: bank[key] = [knock((330 - 160 * min(1, (r - 0.2) / 0.7)) * (0.75 if slow else 1) * rng.uniform(0.95, 1.05), rng) for _ in range(3)]
        return bank[key][rng.integers(3)]
    F = np.array(R['frames']); v = np.diff(F[:, :, :2], axis=0) * fps
    a = np.linalg.norm(np.diff(v, axis=0), axis=2)
    lastv = np.full(F.shape[1], -9.0); lastg = -9.0
    for k in range(a.shape[0]):
        s_ = (k + 1) / fps; t_ = vt(s_)
        if t_ < 0 or t_ > D: continue
        for i in range(a.shape[1]):
            if a[k, i] < 2.2: continue
            if t_ - lastv[i] < 0.14: continue          # same marble: no machine-gun
            st = min(1.0, (a[k, i] - 1.8) / 9)
            if st < 0.12: continue                      # tiny touches stay silent
            r = R['res'][i]['r']
            if t_ - lastg < 0.035 and st < 0.5: continue  # thin out simultaneous small hits
            lastv[i] = t_; lastg = t_
            c = voice(r, A <= s_ < B) * (0.25 + 0.75 * st) * (0.7 + 0.5 * min(1, r / 0.9))
            pan = float(np.clip(F[k, i, 0] / 9, -0.6, 0.6))
            place(buf, np.stack([c * (1 - pan * 0.5), c * (1 + pan * 0.5)], 1), t_, HITS * db(HIT_DB[style]))
    T = R['track']
    # flipper: a soft punchy thwack each time the arm swats a marble (louder if it was a top-2 marble, like the toast)
    thw = thump(70, 0.5, np.random.default_rng(5)); kk = knock(190, np.random.default_rng(6)); thw[:len(kk)] += kk * 0.6
    fo2 = int(0.12 * SR); thw[-fo2:] *= np.linspace(1, 0, fo2)
    lastsw = -9
    for ts, i in T.get('sweeps', []):
        t_ = vt(ts)
        if t_ > D or t_ - lastsw < 0.25: continue
        lastsw = t_; pan = -0.3
        k = min(len(R['frames']) - 1, int(round(ts * fps)))
        live = sorted([(R['frames'][k][j][1], j) for j, r in enumerate(R['res']) if r['finish'] is None or r['finish'] > ts])
        top = i in [j for _, j in live[:2]]          # same rule as the scene's "flipped back" toast
        place(buf, np.stack([thw * (1 - pan * 0.5), thw * (1 + pan * 0.5)], 1), t_, HITS * db(-12 if top else -22))
    hit = load('/mnt/project-files/sfx/user/sub_hit_warm.wav'); fo = int(0.3 * SR); hit[-fo:] *= np.linspace(1, 0, fo)[:, None]
    place(buf, hit, vt(T['lipT']) - 0.03, db(-10))
    def faded(path, dur, fade):
        c = load(path, dur); n = int(fade * SR); c[-n:] *= (np.linspace(1, 0, n) ** 1.5)[:, None]
        fi = int(0.02 * SR); c[:fi] *= np.linspace(0, 1, fi)[:, None]; return c
    wt = vt(tw)
    place(buf, hit, wt - 0.02, db(-7))
    place(buf, faded(SFX + '012_군중환호.mp3', 7.0, 2.5), wt - 0.2, db(-11))
    place(buf, faded(f'{C}/audio/fireworks.mp3', 4.5, 1.5), wt + 0.1, db(-14))
    buf *= np.clip((D - tt) / 1.2, 0, 1)[:, None]
    write(buf, os.environ.get('OUT') or f'{C}/out/marble_v3_audio_{style}' + ('' if RACE == 'race.json' else '_' + RACE[:-5]) + '.wav'); print('duration', round(D, 2))
elif what == 'lies':
    E = json.load(open(f'{C}/counted/edl.json'))
    D = E['end'] + E['outro']
    base = load(f'{C}/counted/base.mp4')
    buf = np.zeros((int(D * SR), 2), np.float32); buf[:min(len(base), len(buf))] = base[:len(buf)]
    bed = load(f'{C}/audio/five_armies.mp3', 12, ss=0)
    t = np.arange(len(bed)) / SR
    intro = bed[:int((E['intro'] + 0.8) * SR)] * db(-16)
    ti = np.arange(len(intro)) / SR; intro *= (np.clip(ti / 0.3, 0, 1) * np.clip((E['intro'] + 0.8 - ti) / 0.8, 0, 1))[:, None]
    place(buf, intro, 0)
    out_bed = bed[:int(E['outro'] * SR)] * db(-15); to = np.arange(len(out_bed)) / SR
    out_bed *= (np.clip(to / 0.4, 0, 1) * np.clip((E['outro'] - to) / 1.2, 0, 1))[:, None]
    place(buf, out_bed, E['end'] - 0.2)
    hit = load('/mnt/project-files/sfx/user/sub_hit_warm.wav')
    for l in E['lies']: place(buf, hit, l['at'] - 0.03, db(-13))
    write(buf, f'{C}/out/lies_audio.wav')
print('ok', what)
