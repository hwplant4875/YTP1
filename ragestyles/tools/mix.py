"""Audio mixer for RageStyles shorts.
usage: python3 mix.py cues.json video_in.mp4 out.mp4
cues.json: {"duration": 28.5, "tracks": [{"file": "sfx:sub_hit", "t": 1.2, "db": -3, "start": 0, "len": null, "fade": 0.05, "rate": 1.0, "duck": false}]}
"file" can be "sfx:<name>" (SFX pack), "synth:sub" (generated 808 sub), or a path. Sources are peak-normalised before gain.
Tracks with "duck": true (voice) lower everything else by 6 dB while they play.
"""
import json, os, subprocess, sys
import numpy as np

SR = 48000
SFX = os.environ.get('RS_SFX', '/home/user/rs_work/sfx')


def load(path, start=0.0, length=None, rate=1.0):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(start)] + (['-t', str(length * rate)] if length else []) + ['-i', path]
    af = [f'asetrate={int(SR * rate)},aresample={SR}'] if rate != 1.0 else []
    cmd += (['-af', ','.join(af)] if af else []) + ['-f', 'f32le', '-ac', '2', '-ar', str(SR), '-']
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
    return a


def synth(kind, dur=1.2):
    t = np.arange(int(SR * dur)) / SR
    if kind == 'sub':   # 808-style: pitch drop 90 -> 38 Hz, click transient, exp decay
        f = 38 + 52 * np.exp(-t * 18)
        ph = 2 * np.pi * np.cumsum(f) / SR
        y = np.sin(ph) * np.exp(-t * 2.6) + 0.35 * np.tanh(3 * np.sin(ph)) * np.exp(-t * 6)
        y[:int(SR * .004)] += np.random.uniform(-.6, .6, int(SR * .004))
    elif kind == 'tick':
        y = np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 90)
    else:
        raise ValueError(kind)
    y = y / np.abs(y).max()
    return np.stack([y, y], 1).astype(np.float32)


def main(cues_path, video_in, out):
    cues = json.load(open(cues_path))
    base = os.path.dirname(os.path.abspath(cues_path))
    n = int(SR * cues['duration'])
    bus, duckbus = np.zeros((n, 2), np.float32), np.zeros((n, 2), np.float32)
    duck_env = np.zeros(n, np.float32)
    for c in cues['tracks']:
        f = c['file']
        if f.startswith('synth:'):
            a = synth(f[6:], c.get('len') or 1.2)
        else:
            p = f'{SFX}/{f[4:]}.mp3' if f.startswith('sfx:') else (f if os.path.isabs(f) else os.path.join(os.environ.get('RS_WORK', '/home/user/rs_work'), f))
            if not os.path.exists(p): print('missing', p); continue
            a = load(p, c.get('start', 0), c.get('len'), c.get('rate', 1.0))
        if not len(a): continue
        if c.get('norm', True): a = a / max(np.abs(a).max(), 1e-6) * 0.89
        fade = int(SR * c.get('fade', .01)); fin = int(SR * c.get('fadein', 0))
        if fade and len(a) > fade: a[-fade:] *= np.linspace(1, 0, fade)[:, None]
        if fin and len(a) > fin: a[:fin] *= np.linspace(0, 1, fin)[:, None]
        a *= 10 ** (c.get('db', 0) / 20)
        i = int(SR * c['t'])
        if i >= n: continue
        a = a[:n - i]
        tgt = duckbus if c.get('duck') else bus
        tgt[i:i + len(a)] += a
        if c.get('duck'): duck_env[i:i + len(a)] = 1
    # smooth duck envelope (attack 60 ms, release 250 ms)
    k = int(SR * .12)
    if duck_env.any():
        duck_env = np.convolve(duck_env, np.ones(k) / k, 'same')
    mix = bus * (1 - 0.5 * duck_env[:, None]) + duckbus
    # soft limiter
    mix = (np.tanh(mix * 1.1) / np.tanh(1.1)).astype(np.float32)
    raw = out + '.raw.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', raw], input=mix.tobytes(), check=True)
    # loudness: two-pass loudnorm to -14 LUFS, -1 dBTP
    st = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = json.loads(st[st.rindex('{'):st.rindex('}') + 1])
    ln = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video_in, '-i', raw, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-af', ln + f',aresample={SR}', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], check=True)
    os.remove(raw)
    print(out)


if __name__ == '__main__':
    main(*sys.argv[1:4])
