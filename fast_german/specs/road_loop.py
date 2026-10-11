"""Seamless looping Autobahn background (user 2026-10-11): top-down asphalt drifting slowly, one long white dashed
centre line only. Vertical (1080x1920, road runs up the screen) and horizontal (1920x1080) versions.
The texture is exactly one loop long and wraps, so the last frame flows into the first."""
import subprocess, sys
import numpy as np
from PIL import Image, ImageFilter
OUT = "/mnt/project-files/fast_german/preview/road_loop/"
FPS, SECS = 30, 16                     # 16 s loop, slow drift
PERIOD = 480                           # dash 6 m + gap 12 m at 26.7 px/m


def strip(width, length, seed=5):
    """Asphalt strip `length` px along the road, wrapping seamlessly at both ends (road axis = rows)."""
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (length, width))
    # blur with wrap-around along the road so the seam disappears
    k = np.array([0.25, 0.5, 0.25])
    for ax in (0, 1):
        n = sum(w * np.roll(n, s, axis=ax) for w, s in zip(k, (-1, 0, 1)))
    coarse = rng.normal(0, 1, (length // 40, width // 40 + 1))
    coarse = np.array(Image.fromarray(((coarse + 4) * 30).astype("uint8")).resize((width, length), Image.BICUBIC), float) / 30 - 4
    coarse = (coarse + np.roll(coarse, length // 2, 0)) / 2 * 0  # keep flat: no visible coarse seam
    base = 46 + n * 7
    # two faint tyre tracks per lane (slightly darker, smoother)
    x = np.arange(width)[None, :]
    c = width / 2
    for off in (-0.36, -0.14, 0.14, 0.36):
        base -= 5 * np.exp(-((x - c - off * width) / (width * 0.035)) ** 2)
    rgb = np.stack([base, base + 1, base + 4], -1)
    # centre dashes
    y = np.arange(length)[:, None]
    dash = ((y % PERIOD) < PERIOD // 3) & (np.abs(x - c) < 9)
    wear = rng.random((length, width)) < 0.08
    paint = dash & ~wear
    rgb[paint] = (236, 236, 228)
    rgb[dash & wear] = rgb[dash & wear] * 0.4 + 236 * 0.6
    return np.clip(rgb, 0, 255).astype("uint8")


def render(name, w, h, vertical):
    road_w = w if vertical else h
    length = h if vertical else w
    length = (length // PERIOD + 1) * PERIOD           # loop length: whole number of dash periods
    tex = strip(road_w, length)
    if not vertical:
        tex = np.ascontiguousarray(np.transpose(tex, (1, 0, 2)))   # road runs left-right
    yy, xx = np.mgrid[0:h, 0:w]
    vig = 1 - 0.22 * (((xx / w - 0.5) * 2) ** 2 + ((yy / h - 0.5) * 2) ** 2) / 2
    n = FPS * SECS
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", OUT + name], stdin=subprocess.PIPE)
    for i in range(n):
        shift = int(round(i * length / n))              # exactly one texture length per loop
        if vertical:
            fr = np.roll(tex, shift, axis=0)[:h]        # road flows down the screen (driving forward)
        else:
            fr = np.roll(tex, -shift, axis=1)[:, :w]    # road flows to the left
        ff.stdin.write((fr * vig[..., None]).astype("uint8").tobytes())
    ff.stdin.close(); ff.wait()
    Image.fromarray((tex[:h, :w] * vig[..., None]).astype("uint8")).save(OUT + name.replace(".mp4", ".png"))


if __name__ == "__main__":
    import os; os.makedirs(OUT, exist_ok=True)
    render("road_loop_vertical_1080x1920.mp4", 1080, 1920, True)
    render("road_loop_horizontal_1920x1080.mp4", 1920, 1080, False)
