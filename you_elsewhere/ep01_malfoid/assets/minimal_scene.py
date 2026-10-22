# Minimal still-image look: fine grain, a few dust motes, soft vignette, gentle firelight breathing,
# channel-name watermark, and a slow 20%->100% brightness fade-in at the start.
# usage: python3 minimal_scene.py <img> <out.mp4> <seconds> <font.ttf> <corner: bl|tl|br> [audio]
import sys, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
img_p, out, secs, font_p, corner = sys.argv[1:6]
audio = sys.argv[6] if len(sys.argv) > 6 else None
W, H, FPS, T = 1920, 1080, 30, 20.0
secs = float(secs)
src = cv2.cvtColor(cv2.imread(img_p), cv2.COLOR_BGR2RGB)
src = cv2.resize(src, (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32) / 255
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
# soft vignette + slightly lifted blacks / warm film tone
d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
vig = (1 - 0.28 * np.clip(d - 0.45, 0, 1) ** 1.6)[..., None]
base = src * vig
base = 0.025 + base * 0.97
base[..., 0] *= 1.015; base[..., 2] *= 0.985
# firelight area (left side of the image) breathes very gently
sx, sy = W / 1672, H / 941
fire = np.exp(-(((xx - 150 * sx) / (520 * sx)) ** 2 + ((yy - 520 * sy) / (420 * sy)) ** 2))[..., None]
# watermark
wm = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(wm)
f = ImageFont.truetype(font_p, 46)
txt = 'You, Elsewhere'
bw = dr.textbbox((0, 0), txt, font=f)
tw, th = bw[2] - bw[0], bw[3] - bw[1]
m = 64
pos = {'bl': (m, H - m - th - bw[1]), 'tl': (m, m - bw[1]), 'br': (W - m - tw, H - m - th - bw[1])}[corner]
sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pos[0] + 2, pos[1] + 2), txt, font=f, fill=(0, 0, 0, 120))
sh = np.array(sh).astype(np.float32) / 255
dr.text(pos, txt, font=f, fill=(246, 238, 224, 200))
wm = np.array(wm).astype(np.float32) / 255
sh = cv2.GaussianBlur(sh, (0, 0), 3)
rng = np.random.default_rng(7)
N = 40
dp = rng.random((N, 2)) * [W, H]; dv = rng.normal(0, 1, (N, 2)) * [6, 4] + [3, -5]
ds = rng.uniform(1.0, 2.6, N); da = rng.uniform(0.08, 0.22, N); dph = rng.integers(1, 3, N)
def pn(t, ks, seed):
    r = np.random.default_rng(seed); return sum(np.sin(2 * np.pi * k * t / T + r.random() * 6.28) / k for k in ks)
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
if audio: cmd += ['-i', audio, '-shortest', '-c:a', 'aac', '-b:a', '192k']
cmd += ['-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', out]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
FADE = 6.0
for i in range(int(secs * FPS)):
    t = i / FPS; tl = t % T
    g = 1 + 0.035 * pn(tl, [1, 2, 3, 5], 1) / 1.8
    fr = base * (1 + (g - 1) * fire * 1.6)
    # dust: tiny soft specks drifting, periodic over T
    dust = np.zeros((H, W), np.float32)
    for j in range(N):
        x = (dp[j, 0] + dv[j, 0] * tl + 10 * np.sin(2 * np.pi * dph[j] * tl / T)) % W
        y = (dp[j, 1] + dv[j, 1] * tl) % H
        cv2.circle(dust, (int(x), int(y)), int(ds[j] + .5), float(da[j] * (0.6 + 0.4 * np.sin(2 * np.pi * tl / T + j))), -1, cv2.LINE_AA)
    dust = cv2.GaussianBlur(dust, (0, 0), 1.2)[..., None]
    fr = fr + dust * np.array([1.0, 0.92, 0.8])
    gr = cv2.resize(rng.normal(0, 0.022, (H // 2, W // 2)).astype(np.float32), (W, H))[..., None]
    fr = fr + gr
    fr = fr * (1 - sh[..., 3:] * 0.6)
    fr = fr * (1 - wm[..., 3:]) + wm[..., :3] * wm[..., 3:]
    # 20% -> 100% brightness, smoothstep over FADE seconds
    k = min(t / FADE, 1.0); k = k * k * (3 - 2 * k)
    fr = fr * (0.2 + 0.8 * k)
    p.stdin.write((np.clip(fr, 0, 1) * 255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
