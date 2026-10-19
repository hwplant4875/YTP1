"""German Rave: place shouted TTS lines on the beat grid of an instrumental.

python3 specs/rave/mc_mix.py BEAT.mp3 BEAT0 PERIOD CLIPDIR VOICE OUT.wav EVENTS.json
Clips: CLIPDIR/{VOICE}_{i}de.mp3 and {i}en.mp3 for pair i. Each pair: DE, EN, DE, EN on every 2nd beat.
"""
import json, subprocess, sys
import numpy as np

SR = 44100


def load(path, af=None):
    cmd = ["ffmpeg", "-loglevel", "error", "-i", path]
    if af: cmd += ["-af", af]
    raw = subprocess.run(cmd + ["-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def trim(x, th=0.02):
    e = np.abs(x).max(1)
    idx = np.where(e > th)[0]
    return x[max(0, idx[0] - 200): idx[-1] + 1] if len(idx) else x


def fade_out(x, n):
    n = min(n, len(x)); x[-n:] *= np.linspace(1, 0, n)[:, None]; return x


def main(beat, beat0, period, clipdir, voice, out, events_out, pairs=8):
    beat0, period = float(beat0), float(period)
    slot = 2 * period
    total_beats = pairs * 8
    dur = total_beats * period
    b = load(beat)[int(beat0 * SR):]
    b = b[:int((dur + 0.4) * SR)] * 0.55
    mix = np.zeros_like(b)
    vox = np.zeros_like(b)
    events = []
    chain = "highpass=f=110,acompressor=threshold=-20dB:ratio=4:attack=5:release=80:makeup=4,aecho=0.8:0.6:45|90:0.18|0.1"
    for i in range(pairs):
        for r, (kind, lead) in enumerate([("de", 0), ("en", 2), ("de", 4), ("en", 6)]):
            c = trim(load(f"{clipdir}/{voice}_{i}{kind}.mp3", chain))
            c = fade_out(c[:int((slot - 0.05) * SR)], int(0.06 * SR))
            t = (i * 8 + lead) * period - 0.02
            s = max(0, int(t * SR))
            vox[s:s + len(c)] += c[:len(vox) - s]
            events.append([round(max(0.0, t), 3), kind, i])
    # duck the beat under the voice
    env = np.convolve(np.abs(vox).max(1), np.ones(800) / 800, "same")
    duck = 1 - 0.45 * np.clip(env / (env.max() + 1e-9) * 3, 0, 1)
    mix = b * duck[:, None] + vox * 1.0
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    n = int(0.3 * SR); mix[-n:] *= np.linspace(1, 0, n)[:, None]
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-",
                    "-af", "loudnorm=I=-11:TP=-1", "-ar", str(SR), out], input=mix.astype(np.float32).tobytes())
    json.dump(events, open(events_out, "w"))


if __name__ == "__main__":
    main(*sys.argv[1:8])
