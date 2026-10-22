# You, Elsewhere: long-video compositor. Loops the seamless Blender background, adds the opening fade
# (60 % -> 100 % over 5 s, smoothstep), the "You, Elsewhere" watermark (Allura, bottom-left) and the small sharp
# audio spectrum next to it (64 mirrored spikes, 40 Hz - 1.5 kHz, 35 % opacity, 50/180 ms attack/release).
# Audio = music + fireplace bed looped with crossfades, about 15 LU under the music.
# usage: python composite.py <loop.mp4> <music> <fire_bed|-> <seconds> <out.mp4> [assets_dir]
import sys, os, subprocess, json, time, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

loop, music, fire, secs, out = sys.argv[1:6]
ASSETS = sys.argv[6] if len(sys.argv) > 6 else os.path.join(os.path.dirname(__file__), 'assets')
SECS = float(secs)
W, H, FPS, SR = 1920, 1080, 30, 48000
NF = int(round(SECS * FPS))
TMP = os.path.splitext(out)[0] + '_tmp'; os.makedirs(TMP, exist_ok=True)
t_start = time.time()

def decode(path, sr=SR, ch=2):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', str(ch), '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()

def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float([l for l in r.splitlines() if l.strip().startswith('I:')][-1].split()[1])

def write_wav(path, a):
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-c:a', 'pcm_f32le', path], stdin=subprocess.PIPE)
    p.stdin.write(np.ascontiguousarray(a, np.float32).tobytes()); p.stdin.close(); p.wait()

# ------------------------------------------------------------------ audio
n = int(SECS * SR)
mus = decode(music)[:n]
if len(mus) < n: mus = np.pad(mus, ((0, n - len(mus)), (0, 0)))
env = np.minimum(1, np.minimum(np.arange(n) / (3 * SR), (n - np.arange(n)) / (4 * SR)))[:, None]
mus = mus * env
mix = mus.copy()
if fire != '-':
    fb = decode(fire); XF = 3 * SR
    ramp = np.linspace(0, 1, XF)[:, None]
    bed = fb.copy()
    while len(bed) < n:                       # equal-power crossfade between copies of the bed
        bed = np.concatenate([bed[:-XF], bed[-XF:] * np.cos(ramp * np.pi / 2) + fb[:XF] * np.sin(ramp * np.pi / 2), fb[XF:]])
    bed = bed[:n] * np.minimum(1, np.arange(n) / (3 * SR))[:, None]
    write_wav(f'{TMP}/m.wav', mus); write_wav(f'{TMP}/f.wav', bed)
    g = (lufs(f'{TMP}/m.wav') - 15) - lufs(f'{TMP}/f.wav')
    mix = mus + bed * 10 ** (g / 20)
    print(f'fire bed gain {g:.1f} dB (15 LU under the music)')
peak = np.abs(mix).max()
if peak > 0.89: mix *= 0.89 / peak
write_wav(f'{TMP}/mix.wav', mix)

# ------------------------------------------------------------------ spectrum data (same analysis as the Blender v3 build)
mono = mus.mean(axis=1)
NB, WIN = 64, 8192
centers = np.geomspace(40, 1500, NB)
freqs = np.fft.rfftfreq(WIN, 1 / SR); hann = np.hanning(WIN)
lo_e = centers / 2 ** (1 / 2 / (NB / 7.4)); hi_e = centers * 2 ** (1 / 2 / (NB / 7.4))
sel = [(freqs >= lo_e[b]) & (freqs < hi_e[b]) for b in range(NB)]
mags = np.zeros((NF, NB), np.float32)
for i in range(NF):
    c0 = int(i / FPS * SR) - WIN // 2
    seg = mono[max(c0, 0):c0 + WIN]
    if len(seg) < WIN: seg = np.pad(seg, (WIN - len(seg), 0))
    sp = np.abs(np.fft.rfft(seg * hann)); it = np.interp(centers, freqs, sp)
    mags[i] = [max(sp[s].max(), it[b]) if s.any() else it[b] for b, s in enumerate(sel)]
db = 20 * np.log10(mags + 1e-6)
db = db - 0.75 * db.mean(axis=0, keepdims=True)
lo, hi = np.percentile(db, 30), np.percentile(db, 99.3)
v = np.clip((db - lo) / (hi - lo), 0, 1) ** 1.5
att, rel = 1 - np.exp(-1 / (0.05 * FPS)), 1 - np.exp(-1 / (0.18 * FPS))
sm = np.zeros_like(v); cur = np.zeros(NB)
for i in range(NF):
    k = np.where(v[i] > cur, att, rel); cur = cur + (v[i] - cur) * k; sm[i] = cur
sm *= np.minimum(1, np.minimum(np.arange(NB) + 1, NB - np.arange(NB)) / 3.0)[None, :]

# ------------------------------------------------------------------ watermark (Allura, 60 px tall, 64 px margins, soft shadow)
font = ImageFont.truetype(os.path.join(ASSETS, 'Allura.ttf'), 100)
txt = 'You, Elsewhere'
bb = ImageDraw.Draw(Image.new('L', (10, 10))).textbbox((0, 0), txt, font=font)
font = ImageFont.truetype(os.path.join(ASSETS, 'Allura.ttf'), int(round(100 * 60 / (bb[3] - bb[1]))))
bb = ImageDraw.Draw(Image.new('L', (10, 10))).textbbox((0, 0), txt, font=font)
tx, ty = 64 - bb[0], H - 64 - bb[3]
alpha = Image.new('L', (W, H), 0); ImageDraw.Draw(alpha).text((tx, ty), txt, font=font, fill=255)
shadow = Image.new('L', (W, H), 0); ImageDraw.Draw(shadow).text((tx + 2, ty + 3), txt, font=font, fill=255)
shadow = shadow.filter(ImageFilter.GaussianBlur(3.5))
a_t = np.asarray(alpha, np.float32) / 255 * 0.8; a_s = np.asarray(shadow, np.float32) / 255 * 0.55
# composite "shadow then text" into one premultiplied RGBA layer
col = np.array([246, 238, 224], np.float32)
a_out = a_t + a_s * (1 - a_t)
rgb = (col[None, None, :] * a_t[..., None]) / np.maximum(a_out[..., None], 1e-6)
wm = np.dstack([rgb, a_out[..., None] * 255]).clip(0, 255).astype(np.uint8)
Image.fromarray(wm, 'RGBA').save(f'{TMP}/watermark.png')
right, mid = 64 + (bb[2] - bb[0]), H - 64 - (bb[3] - bb[1]) / 2

# ------------------------------------------------------------------ video
X0 = int(round(right + 26)); CY = mid + 6
OX, OY, OW, OH = X0 - 4, int(CY) - 16, NB * 2 + 8, 32
fade_expr = "A*(0.6+0.4*(if(lt(T,5),(T/5)*(T/5)*(3-2*T/5),1)))"
# fade only touches the first 5 s (RGB blend), the rest of the loop passes through untouched; overlays run in YUV
fc = (f"[0:v]trim=end_frame={NF},split=2[va][vb];"
      f"[va]trim=0:5,setpts=PTS-STARTPTS,format=gbrp[bg];color=c=black:s={W}x{H}:r={FPS}:d=5,format=gbrp[blk];"
      f"[bg][blk]blend=all_expr='{fade_expr}',format=yuv420p[fd];"
      f"[vb]trim=start=5,setpts=PTS-STARTPTS[rest];[fd][rest]concat=n=2:v=1:a=0[cv];"
      f"[cv][1:v]overlay=0:0:shortest=1[w];[w][2:v]overlay={OX}:{OY}:shortest=1,format=yuv420p[v]")
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-stream_loop', '-1', '-i', loop, '-loop', '1', '-r', str(FPS), '-i', f'{TMP}/watermark.png',
       '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-', '-i', f'{TMP}/mix.wav',
       '-filter_complex', fc, '-map', '[v]', '-map', '3:a', '-frames:v', str(NF),
       '-c:v', 'libx264', '-crf', '20', '-preset', 'fast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
SH = 16                                                   # cv2 fixed-point subpixel shift
for i in range(NF):
    mask = np.zeros((OH, OW), np.uint8)
    h = 0.5 + 9.5 * sm[i]
    xs = 4 + 2 * np.arange(NB); cy = CY - OY
    top = np.stack([xs, cy - h], 1); bot = np.stack([xs, cy + h], 1)[::-1]
    pts = (np.concatenate([top, bot]) * SH).astype(np.int32)
    cv2.fillPoly(mask, [pts], 255, cv2.LINE_AA, shift=4)
    img = np.empty((OH, OW, 4), np.uint8); img[..., :3] = (246, 238, 224); img[..., 3] = (mask.astype(np.uint16) * 89 // 255)
    p.stdin.write(img.tobytes())
p.stdin.close(); p.wait()
print(f'done {out}: {SECS:.0f} s in {time.time() - t_start:.1f} s ({(time.time() - t_start) / NF:.4f} s/frame)')
