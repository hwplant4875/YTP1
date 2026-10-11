"""Seamless music loops (user 2026-10-11): the track's tail is cross-faded into its head, so the file can repeat
forever without a click or jump. Usage: python3 music_loop.py in.mp3 out.wav [xfade_seconds]"""
import subprocess, sys
import numpy as np

SR = 48000


def load(p):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", p, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def make_loop(src, dst, xfade=4.0):
    a = load(src)
    # drop the track's own fade-out/silence at the end so the seam joins two full-volume parts
    lvl = np.abs(a).max(axis=1)
    end = len(a) - np.argmax(lvl[::-1] > 0.02) - int(1.5 * SR)
    a = a[:end]
    d = int(xfade * SR)
    w = np.sin(np.linspace(0, np.pi / 2, d))[:, None] ** 2     # equal-power-ish crossfade
    head = a[:d] * w + a[-d:] * (1 - w)                         # tail fades out over the head fading in
    loop = np.concatenate([head, a[d:-d]])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    dst], input=loop.astype(np.float32).tobytes(), check=True)
    return len(loop) / SR


if __name__ == "__main__":
    print(make_loop(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 4.0))
