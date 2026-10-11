"""ElevenLabs-generated SFX + background music (assets/sfx), decoded to mono float arrays at SR."""
import os, subprocess, numpy as np
SR = 48000
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sfx")
_c = {}
def load(name, peak=0.5):
    if name not in _c:
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", f"{DIR}/{name}.mp3", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
        x = np.frombuffer(raw, np.float32).astype(np.float64)
        _c[name] = x / (np.abs(x).max() + 1e-9) * peak
    return _c[name]
def music(N, name="music", xfade=2.0):
    """Loop the music bed to N samples: trim the silent head/tail of the track, then join the loops with an
    equal-power crossfade so the seam never dips into silence; fade-out at the end."""
    m = load(name, 0.6); loud = np.flatnonzero(np.abs(m) > 10 ** (-40 / 20) * max(np.abs(m).max(), 1e-9))
    m = m[loud[0]:loud[-1] + 1] if len(loud) else m
    xf = min(int(xfade * SR), len(m) // 4); out = np.zeros(N); i = 0
    fin, fout = np.sin(np.linspace(0, np.pi / 2, xf)), np.cos(np.linspace(0, np.pi / 2, xf))
    while i < N:
        seg = m.copy()
        if i:
            seg[:xf] *= fin; o = out[i - xf:i]; o *= fout[: len(o)]
        start = i - xf if i else 0; j = min(N, start + len(seg)); out[start:j] += seg[: j - start]; i = start + len(seg)
    k = int(1.5 * SR); out[-k:] *= np.linspace(1, 0, k); return out
