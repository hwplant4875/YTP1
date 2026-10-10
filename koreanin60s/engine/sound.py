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
def music(N):
    """Loop the music bed to N samples with a short crossfade at each seam and a fade-out at the end."""
    m = load("music", 0.6); xf = int(0.5 * SR); out = np.zeros(N); i = 0
    while i < N:
        seg = m.copy()
        if i: seg[:xf] *= np.linspace(0, 1, xf); out[i - xf:i] *= np.linspace(1, 0, xf)[: len(out[i - xf:i])]
        start = i - xf if i else 0; j = min(N, start + len(seg)); out[start:j] += seg[: j - start]; i = start + len(seg)
    k = int(1.5 * SR); out[-k:] *= np.linspace(1, 0, k); return out
