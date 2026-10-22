# You, Elsewhere EP1: deliverables for the owner's DaVinci Resolve edit.
#   audio : music_only + music_plus_fire (fire bed 15 LU under, looped with equal-power crossfades), WAV 48 kHz 24-bit,
#           plus an mp3 320k preview of the fire version
#   video : spectrum overlay on pure black for the full audio length (1920x1080, 30 fps, H.264 CRF 16, no audio),
#           same look/position as Blender v3 (64 mirrored sharp spikes, 40 Hz - 1.5 kHz), warm off-white at 100 %
#   image : "You, Elsewhere" Allura watermark, 1920x1080 transparent PNG, same position
# usage: python deliver.py <suite.wav> <fire_bed> <assets_dir> <out_dir>
import sys, os, subprocess, time, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

suite, fire, ASSETS, OUT = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
W, H, FPS, SR = 1920, 1080, 30, 48000
COL = (246, 238, 224)

def decode(path, ch=2):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()

def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float([l for l in r.splitlines() if l.strip().startswith('I:')][-1].split()[1])

def write_audio(path, a, codec=('-c:a', 'pcm_s24le')):
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', *codec, path], stdin=subprocess.PIPE)
    p.stdin.write(np.ascontiguousarray(a, np.float32).tobytes()); p.stdin.close(); p.wait()

t0 = time.time()
# ------------------------------------------------------------------ audio
mus = decode(suite); n = len(mus)
write_audio(f'{OUT}/ep01_music_only.wav', mus)
fb = decode(fire); XF = 3 * SR; ramp = np.linspace(0, 1, XF)[:, None]
bed = fb.copy()
while len(bed) < n:
    bed = np.concatenate([bed[:-XF], bed[-XF:] * np.cos(ramp * np.pi / 2) + fb[:XF] * np.sin(ramp * np.pi / 2), fb[XF:]])
bed = bed[:n] * np.minimum(1, np.minimum(np.arange(n) / (3 * SR), (n - np.arange(n)) / (4 * SR)))[:, None]
write_audio(f'{OUT}/_fire_tmp.wav', bed)
g = (lufs(f'{OUT}/ep01_music_only.wav') - 15) - lufs(f'{OUT}/_fire_tmp.wav')
mix = mus + bed * 10 ** (g / 20)
pk = np.abs(mix).max()
if pk > 0.89: mix *= 0.89 / pk
write_audio(f'{OUT}/ep01_music_plus_fire.wav', mix)
write_audio(f'{OUT}/ep01_music_plus_fire_preview.mp3', mix, ('-c:a', 'libmp3lame', '-b:a', '320k'))
os.remove(f'{OUT}/_fire_tmp.wav')
print(f'audio done: {n / SR:.1f} s, fire bed gain {g:.1f} dB ({time.time() - t0:.0f} s)', flush=True)

# ------------------------------------------------------------------ watermark PNG (same construction as composite.py)
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
a_out = a_t + a_s * (1 - a_t)
rgb = (np.array(COL, np.float32)[None, None, :] * a_t[..., None]) / np.maximum(a_out[..., None], 1e-6)
Image.fromarray(np.dstack([rgb, a_out[..., None] * 255]).clip(0, 255).astype(np.uint8), 'RGBA').save(f'{OUT}/ep01_watermark_you_elsewhere.png')
right, mid = 64 + (bb[2] - bb[0]), H - 64 - (bb[3] - bb[1]) / 2

# ------------------------------------------------------------------ spectrum analysis (Blender v3 settings), driven by the music only
mono = mus.mean(axis=1)
NF = int(n / SR * FPS)
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
print(f'spectrum analysed: {NF} frames ({time.time() - t0:.0f} s)', flush=True)

# ------------------------------------------------------------------ spectrum overlay video on black (small region drawn, padded by ffmpeg)
X0 = int(round(right + 26)); CY = mid + 6
OX, OY, OW, OH = X0 - 4, int(CY) - 16, NB * 2 + 8, 32
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'gray', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                      '-vf', f'format=gbrp,colorchannelmixer=rr={COL[0]/255:.4f}:gg={COL[1]/255:.4f}:bb={COL[2]/255:.4f},pad={W}:{H}:{OX}:{OY}:black,format=yuv420p',
                      '-c:v', 'libx264', '-crf', '16', '-preset', 'medium',
                      '-tune', 'stillimage', '-color_range', 'tv', f'{OUT}/ep01_spectrum_overlay_black.mp4'], stdin=subprocess.PIPE)
xs = 4 + 2 * np.arange(NB); cy = CY - OY
for i in range(NF):
    mask = np.zeros((OH, OW), np.uint8)
    h = 0.5 + 9.5 * sm[i]
    pts = (np.concatenate([np.stack([xs, cy - h], 1), np.stack([xs, cy + h], 1)[::-1]]) * 16).astype(np.int32)
    cv2.fillPoly(mask, [pts], 255, cv2.LINE_AA, shift=4)
    p.stdin.write(mask.tobytes())
p.stdin.close(); p.wait()
print(f'spectrum overlay written ({time.time() - t0:.0f} s)', flush=True)
