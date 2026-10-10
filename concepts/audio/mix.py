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
    R = json.load(open(f'{C}/marble/race.json'))
    LEAD = 0.8; D = 51.0; fps = R['fps']
    buf = music(f'{C}/audio/Run_Amok.mp3', D, ss=0, fin=0.5, fout=2.0, gain_db=-17)
    rng = np.random.default_rng(3)
    F = np.array(R['frames'])  # frames x marbles x 3
    v = np.diff(F[:, :, :2], axis=0) * fps
    a = np.linalg.norm(np.diff(v, axis=0), axis=2)  # velocity change per frame
    last = np.full(F.shape[1], -1.0)
    for k in range(a.shape[0]):
        for i in range(a.shape[1]):
            if a[k, i] > 1.6 and (k - last[i]) > 4:
                last[i] = k
                st = min(1.0, (a[k, i] - 1.2) / 8) * (0.55 + 0.9 * R['res'][i]['r'])
                place(buf, click(rng, st * 0.5), LEAD + (k + 1) / fps)
    beep = load(SFX + '039_삐.mp3', 0.25)
    for tt in [LEAD - 1.4 + 1.6 + x for x in (0, 1)]:
        if tt > 0: place(buf, beep, tt, db(-18))
    go = load(SFX + '026_띠딩2.mp3'); place(buf, go, LEAD + 1.6, db(-14))
    T = R['track']
    place(buf, load(SFX + '014_등장(드럼소리).mp3'), LEAD + T['lipT'] - 0.1, db(-16))
    win = min(r['finish'] for r in R['res'])
    place(buf, load(SFX + '012_군중환호.mp3', 4.0), LEAD + win, db(-20))
    write(buf, f'{C}/out/marble_audio.wav')
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
