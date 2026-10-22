# Animatic fallback: turn 3 stills per shot (frames 0, 0.5, 1.0 from shots.py --frames) into a moving clip
# with slow push-in and dissolves, so the edit can be reviewed before the full GPU render exists.
# usage: python3 stills_to_clip.py STILLS_DIR OUT_DIR
import os, sys, subprocess, glob
from PIL import Image

SHOTS = {'SH01_street': 8.4, 'SH02_tunnel_sign': 5.5, 'SH03_cinema': 13.6, 'SH04_screen': 2.7, 'SH05_cinema_dark': 10.7,
         'SH06_descent': 6.7, 'SH07_stone': 5.3, 'SH08_sea': 9.0, 'SH09_shaft': 7.3, 'SH10_roots': 11.6,
         'SH11_collapse': 15.4, 'SH12_pillars': 8.5}
W, H, FPS = 1920, 1080, 24
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
for sh, dur in SHOTS.items():
    fs = sorted(glob.glob(os.path.join(src, sh, '*.png')))
    if not fs: print('missing', sh); continue
    ims = [Image.open(f).convert('RGB').resize((W, H), Image.LANCZOS) for f in fs]
    n = int(round((dur + 0.5) * FPS)); seg = (n - 1) / max(1, len(ims) - 1)
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', os.path.join(out, sh + '.mp4')],
                         stdin=subprocess.PIPE)
    for k in range(n):
        i = min(int(k / seg), len(ims) - 2) if len(ims) > 1 else 0
        t = (k - i * seg) / seg if len(ims) > 1 else 0
        # hold each still, dissolve over the middle 40% of the gap
        m = min(1, max(0, (t - 0.3) / 0.4)); m = m * m * (3 - 2 * m)
        fr = Image.blend(ims[i], ims[min(i + 1, len(ims) - 1)], m) if len(ims) > 1 else ims[0]
        z = 1 + 0.06 * k / max(1, n - 1); cw, ch = W / z, H / z
        fr = fr.transform((W, H), Image.EXTENT, ((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2), Image.BICUBIC)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait(); print(sh, 'ok', flush=True)
