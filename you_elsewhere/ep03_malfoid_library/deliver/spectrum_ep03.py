# EP3 spectrum overlay: same analysis, smoothing, colour and position as EP1 (spectrum_alpha.py / deliver.py), but
# FEWER bars (owner, 10/23): 24 separate bars, a little wider with small gaps, each with a sharp pointed tip.
# Writes (1) cropped transparent ProRes 4444 at 3x and (2) 1920x1080 black-background H.264 for Screen blend.
# usage: python spectrum_ep03.py <music.wav> <assets_dir> <out_dir> [qa <qa_dir> t1 t2 ...]
import sys, os, subprocess, time, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

music, ASSETS, OUT = sys.argv[1:4]
QA = len(sys.argv) > 4 and sys.argv[4] == 'qa'
W, H, FPS, SR = 1920, 1080, 30, 48000
COL = (246, 238, 224)
NB, PITCH, BW = 24, 5.0, 2.4          # bars, bar spacing and bar width in on-screen px (EP1: 64 spikes, 2 px apart)
t0 = time.time()
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', music, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
mono = np.frombuffer(raw, np.float32)
NF = int(len(mono) / SR * FPS)

# EP1 analysis with 24 bands over the same 40 Hz-1.5 kHz (each band takes the max bin, so peaks stay sharp)
WIN = 8192
centers = np.geomspace(40, 1500, NB)
freqs = np.fft.rfftfreq(WIN, 1 / SR); hann = np.hanning(WIN)
half = np.sqrt(centers[1] / centers[0])                     # contiguous bands
sel = [np.nonzero((freqs >= c / half) & (freqs < c * half))[0] for c in centers]
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
sm *= np.minimum(1, np.minimum(np.arange(NB) + 1, NB - np.arange(NB)) / 2.0)[None, :]   # soft edges (2 bars)
print(f'analysed {NF} frames ({time.time() - t0:.0f} s); frames with a bar >= 0.97: {np.mean(sm.max(1) >= 0.97) * 100:.1f} %', flush=True)

# position: right of the watermark, exactly as EP1
font = ImageFont.truetype(os.path.join(ASSETS, 'Allura.ttf'), 100)
txt = 'You, Elsewhere'
bb = ImageDraw.Draw(Image.new('L', (10, 10))).textbbox((0, 0), txt, font=font)
font = ImageFont.truetype(os.path.join(ASSETS, 'Allura.ttf'), int(round(100 * 60 / (bb[3] - bb[1]))))
bb = ImageDraw.Draw(Image.new('L', (10, 10))).textbbox((0, 0), txt, font=font)
right, mid = 64 + (bb[2] - bb[0]), H - 64 - (bb[3] - bb[1]) / 2
X0 = int(round(right + 26)); CY = mid + 6
OW = int(np.ceil((NB - 1) * PITCH + BW)) + 8; OW += OW % 2
OX, OY, OH = X0 - 4, int(CY) - 16, 32
print(f'spectrum region x={OX} y={OY} w={OW} h={OH}', flush=True)

def draw(i, S):
    """Mask of frame i at scale S: each bar is a vertical spindle, pointed at both ends, mirrored around the centre line."""
    mask = np.zeros((OH * S, OW * S), np.uint8)
    cy = (CY - OY) * S
    for b in range(NB):
        x = (4 + BW / 2 + b * PITCH) * S; w = BW / 2 * S
        h = (1.1 + 8.9 * sm[i, b]) * S                           # resting bars are thin ticks, not dots
        tip = min(h * 0.7, w * 1.5)                              # short pointed tip
        pts = np.array([(x, cy - h), (x + w, cy - h + tip), (x + w, cy + h - tip), (x, cy + h),
                        (x - w, cy + h - tip), (x - w, cy - h + tip)]) * 16
        cv2.fillPoly(mask, [pts.astype(np.int32)], 255, cv2.LINE_AA, shift=4)
    return mask

if QA:
    qd = sys.argv[5]; os.makedirs(qd, exist_ok=True)
    for ts in sys.argv[6:]:
        i = int(float(ts) * FPS); m = draw(i, 4).astype(np.float32) / 255
        img = np.full(m.shape + (3,), 40, np.float32)              # dark grey background
        img = img * (1 - m[..., None]) + np.array(COL[::-1], np.float32) * m[..., None]
        path = os.path.join(qd, f'qa_{int(float(ts)):04d}s.png'); cv2.imwrite(path, img.astype(np.uint8))
        print(path, 'max bar', round(float(sm[i].max()), 2), 'mean', round(float(sm[i].mean()), 2))
    sys.exit()

os.makedirs(OUT, exist_ok=True)
S = 3; CW, CH = OW * S, OH * S
mov = os.path.join(OUT, f'ep03_spectrum_alpha_crop_{CW}x{CH}_prores4444.mov')
mp4 = os.path.join(OUT, 'ep03_spectrum_overlay_black.mp4')
pa = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{CW}x{CH}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le', '-vendor', 'apl0', mov], stdin=subprocess.PIPE)
pb = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'gray', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                       '-vf', f'format=gbrp,colorchannelmixer=rr={COL[0]/255:.4f}:gg={COL[1]/255:.4f}:bb={COL[2]/255:.4f},pad={W}:{H}:{OX}:{OY}:black,format=yuv420p',
                       '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-tune', 'stillimage', '-color_range', 'tv', mp4], stdin=subprocess.PIPE)
frame = np.empty((CH, CW, 4), np.uint8); frame[..., :3] = COL
for i in range(NF):
    frame[..., 3] = draw(i, S); pa.stdin.write(frame.tobytes())
    pb.stdin.write(draw(i, 1).tobytes())
    if i % 9000 == 0: print(f'frame {i}/{NF} ({time.time() - t0:.0f} s)', flush=True)
pa.stdin.close(); pb.stdin.close(); pa.wait(); pb.wait()
print(f'wrote {NF} frames: {mov}, {mp4} ({time.time() - t0:.0f} s)')
