# Spectrum overlay with a transparent background for Resolve: just the spectrum region (no full frame), drawn at 3x the
# on-screen size, ProRes 4444 with alpha, 30 fps. Same analysis/look as Blender v3 and deliver.py, warm off-white, 100 % alpha.
# usage: python spectrum_alpha.py <music.wav> <assets_dir> <out_dir> [seconds|all]
import sys, os, subprocess, time, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

music, ASSETS, OUT = sys.argv[1:4]
LIMIT = None if len(sys.argv) < 5 or sys.argv[4] == 'all' else float(sys.argv[4])
W, H, FPS, SR = 1920, 1080, 30, 48000
COL = (246, 238, 224)
os.makedirs(OUT, exist_ok=True)
t0 = time.time()
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', music, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
mono = np.frombuffer(raw, np.float32)
NF = int(len(mono) / SR * FPS)

# same analysis as deliver.py (normalisation uses the whole track, so a short test looks identical to the full render)
NB, WIN = 64, 8192
centers = np.geomspace(40, 1500, NB)
freqs = np.fft.rfftfreq(WIN, 1 / SR); hann = np.hanning(WIN)
lo_e = centers / 2 ** (1 / 2 / (NB / 7.4)); hi_e = centers * 2 ** (1 / 2 / (NB / 7.4))
sel = [np.nonzero((freqs >= lo_e[b]) & (freqs < hi_e[b]))[0] for b in range(NB)]
mags = np.zeros((NF, NB), np.float32)
for i in range(NF):
    c0 = int(i / FPS * SR) - WIN // 2
    seg = mono[max(c0, 0):c0 + WIN]
    if len(seg) < WIN: seg = np.pad(seg, (WIN - len(seg), 0))
    sp = np.abs(np.fft.rfft(seg * hann)); it = np.interp(centers, freqs, sp)
    mags[i] = [max(sp[s].max(), it[b]) if len(s) else it[b] for b, s in enumerate(sel)]
db = 20 * np.log10(mags + 1e-6)
db = db - 0.75 * db.mean(axis=0, keepdims=True)
lo, hi = np.percentile(db, 30), np.percentile(db, 99.3)
v = np.clip((db - lo) / (hi - lo), 0, 1) ** 1.5
att, rel = 1 - np.exp(-1 / (0.05 * FPS)), 1 - np.exp(-1 / (0.18 * FPS))
sm = np.zeros_like(v); cur = np.zeros(NB)
for i in range(NF):
    k = np.where(v[i] > cur, att, rel); cur = cur + (v[i] - cur) * k; sm[i] = cur
sm *= np.minimum(1, np.minimum(np.arange(NB) + 1, NB - np.arange(NB)) / 3.0)[None, :]
print(f'analysed {NF} frames ({time.time() - t0:.0f} s)', flush=True)

# position: right of the watermark, as in deliver.py
font = ImageFont.truetype(os.path.join(ASSETS, 'Allura.ttf'), 100)
txt = 'You, Elsewhere'
bb = ImageDraw.Draw(Image.new('L', (10, 10))).textbbox((0, 0), txt, font=font)
font = ImageFont.truetype(os.path.join(ASSETS, 'Allura.ttf'), int(round(100 * 60 / (bb[3] - bb[1]))))
bb = ImageDraw.Draw(Image.new('L', (10, 10))).textbbox((0, 0), txt, font=font)
right, mid = 64 + (bb[2] - bb[0]), H - 64 - (bb[3] - bb[1]) / 2
X0 = int(round(right + 26)); CY = mid + 6
OX, OY, OW, OH = X0 - 4, int(CY) - 16, NB * 2 + 8, 32
print(f'spectrum region x={OX} y={OY} w={OW} h={OH}', flush=True)

n_out = NF if LIMIT is None else min(NF, int(LIMIT * FPS))
# cropped ProRes 4444 with alpha at 3x the on-screen size (the owner places and scales it in Resolve)
S = 3
CW, CH = OW * S, OH * S                                    # 408 x 96, even
out_mov = os.path.join(OUT, f'ep01_spectrum_alpha_crop_{CW}x{CH}_prores4444.mov')
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{CW}x{CH}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le', '-vendor', 'apl0', out_mov], stdin=subprocess.PIPE)
frame = np.empty((CH, CW, 4), np.uint8); frame[..., :3] = COL
xs = (4 + 2 * np.arange(NB)) * S; cy = (CY - OY) * S
for i in range(n_out):
    mask = np.zeros((CH, CW), np.uint8)
    h = (0.5 + 9.5 * sm[i]) * S
    pts = (np.concatenate([np.stack([xs, cy - h], 1), np.stack([xs, cy + h], 1)[::-1]]) * 16).astype(np.int32)
    cv2.fillPoly(mask, [pts], 255, cv2.LINE_AA, shift=4)
    frame[..., 3] = mask
    p.stdin.write(frame.tobytes())
p.stdin.close(); p.wait()
print(f'wrote {n_out} frames to {out_mov} ({time.time() - t0:.0f} s)')
