# Dust-mote overlay for Resolve: frames_dust/f_0001..1860.png (62 s, motes only, additive light on black)
# -> seamless 60 s loop (last 2 s crossfaded into the start), as
#    dust_overlay_60s_black.mp4        H.264 CRF 16 on pure black (Screen/Add blend)
#    dust_overlay_60s_alpha_png/dust_0000.png ...  RGBA PNG sequence (alpha = brightness, colour un-premultiplied);
#    full-frame ProRes 4444 was several GB for 60 s, so the PNG sequence replaces it
# usage: python make_dust_overlay.py <frames_dir> <out_dir>
import sys, subprocess, cv2, numpy as np
src, out = sys.argv[1], sys.argv[2]
FPS, LOOP, XF, W, H = 30, 1800, 60, 1920, 1080

def enc(args):
    return subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-s', f'{W}x{H}', '-r', str(FPS)] + args, stdin=subprocess.PIPE)

black = enc(['-pix_fmt', 'bgr24', '-i', '-', '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', '-pix_fmt', 'yuv420p', f'{out}/dust_overlay_60s_black.mp4'])
import os
os.makedirs(f'{out}/dust_overlay_60s_alpha_png', exist_ok=True)
alpha = enc(['-pix_fmt', 'bgra', '-i', '-', '-c:v', 'png', '-pix_fmt', 'rgba', '-start_number', '0', f'{out}/dust_overlay_60s_alpha_png/dust_%04d.png'])
for i in range(LOOP):
    f = cv2.imread(f'{src}/f_{i + 1:04d}.png', cv2.IMREAD_COLOR).astype(np.float32)
    if i < XF:
        tail = cv2.imread(f'{src}/f_{LOOP + i + 1:04d}.png', cv2.IMREAD_COLOR).astype(np.float32)
        k = (i + 0.5) / XF; k = k * k * (3 - 2 * k)
        f = tail * (1 - k) + f * k
    black.stdin.write(np.clip(f + 0.5, 0, 255).astype(np.uint8).tobytes())
    a = f.max(axis=2, keepdims=True)
    rgb = np.where(a > 0, f / np.maximum(a, 1e-3) * 255, 0)
    alpha.stdin.write(np.clip(np.dstack([rgb, a]) + 0.5, 0, 255).astype(np.uint8).tobytes())
for p in (black, alpha):
    p.stdin.close(); p.wait()
print('dust overlay written')
