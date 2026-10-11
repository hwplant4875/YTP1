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
    peak = np.abs(buf).max(); buf = buf / max(1.0, peak / 0.95)
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
    # usage: mix.py marble [candidate 1-8]  (one-shots are cut from the chosen marble_sfx clip)
    import glob
    R = json.load(open(f'{C}/marble/race.json'))
    LEAD = -0.8; D = 43.0; fps = R['fps']
    arg = sys.argv[2] if len(sys.argv) > 2 else '0'
    scheme = None if arg.isdigit() else arg  # a marble_sounds.py scheme name, e.g. A_marimba_mountain_king
    cand = 0 if scheme else int(arg)          # 0 = the original synthesized glass click, 1-8 = ElevenLabs clips
    shots = []
    if cand:
      src = load(sorted(glob.glob(f'{C}/audio/marble_sfx/{cand:02d}_*.mp3'))[0])
      mono = np.abs(src).mean(1); hop = 240
      env = np.array([mono[i:i + hop].max() for i in range(0, len(mono), hop)])
      lastk = -99
      for k in range(1, len(env)):
          if env[k] > 0.12 * env.max() and env[k] > 2.2 * max(env[k - 1], 1e-4) and k - lastk > 20:
              lastk = k; a = max(0, k * hop - 120); c = src[a:a + int(0.16 * SR)].copy()
              if len(c) < int(0.16 * SR): continue
              fo = int(0.05 * SR); c[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
              c /= np.abs(c).max() + 1e-6; shots.append(c)
    print('one-shots', len(shots))
    buf = music(f'{C}/audio/Run_Amok.mp3', D, ss=0, fin=0.05, fout=2.5, gain_db=-17)
    if scheme:
        sys.path.insert(0, f'{C}/audio'); import marble_sounds as MS
        if not MS.SCHEMES[scheme][4]: buf[:] = 0  # melody schemes are the music
        buf += np.repeat(MS.render(scheme, D, LEAD)[:len(buf)], 1, 0)
    rng = np.random.default_rng(3)
    F = np.array(R['frames'])
    v = np.diff(F[:, :, :2], axis=0) * fps
    a = np.linalg.norm(np.diff(v, axis=0), axis=2)
    last = np.full(F.shape[1], -1.0)
    def resample(c, rate):
        n = int(len(c) / rate); x = np.arange(n) * rate
        return np.stack([np.interp(x, np.arange(len(c)), c[:, ch]) for ch in (0, 1)], 1).astype(np.float32)
    for k in range(a.shape[0] if not scheme else 0):
        tv = LEAD + (k + 1) / fps
        if tv < 0: continue
        for i in range(a.shape[1]):
            if a[k, i] > 1.6 and (k - last[i]) > 4:
                last[i] = k
                r = R['res'][i]['r']
                st = min(1.0, (a[k, i] - 1.2) / 8) * (0.55 + 0.9 * r)
                if not cand:
                    place(buf, click(rng, st * 0.5), tv); continue
                c = resample(shots[rng.integers(len(shots))], 1.25 - 0.5 * min(1, (r - 0.3) / 0.9) + rng.uniform(-0.04, 0.04))
                pan = float(np.clip(F[k, i, 0] / 9, -0.7, 0.7))
                c = c * np.array([1 - pan * 0.6, 1 + pan * 0.6], np.float32)
                place(buf, c, tv, st * db(-15))
    T = R['track']
    hit = load('/mnt/project-files/sfx/user/sub_hit_warm.wav')
    fo = int(0.3 * SR); hit[-fo:] *= np.linspace(1, 0, fo)[:, None]
    place(buf, hit, LEAD + T['lipT'] - 0.03, db(-19))
    win = min(r['finish'] for r in R['res'])
    def faded(path, dur, fade):
        c = load(path, dur); n = int(fade * SR); c[-n:] *= (np.linspace(1, 0, n) ** 1.5)[:, None]
        fi = int(0.02 * SR); c[:fi] *= np.linspace(0, 1, fi)[:, None]; return c
    place(buf, faded(SFX + '012_군중환호.mp3', 6.5, 2.5), LEAD + win - 0.3, db(-21))
    place(buf, faded(f'{C}/audio/fireworks.mp3', 4.5, 1.5), LEAD + win, db(-23))
    out = np.zeros_like(buf); tt = np.arange(len(buf)) / SR
    buf *= np.clip((D - tt) / 1.2, 0, 1)[:, None]  # everything (applause included) fades with the picture
    write(buf, f'{C}/out/marble_audio_{scheme or "c" + str(cand)}.wav')
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
