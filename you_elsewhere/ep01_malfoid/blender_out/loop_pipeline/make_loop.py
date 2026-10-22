# Turn the 22 s Blender background render (frames_loop/f_0001..0660.png) into a seamless 20 s loop:
# the last 2 s are crossfaded into the first 2 s, so frame 600 flows straight back into frame 1.
# usage: python make_loop.py <frames_dir> <out.mp4>
import sys, subprocess, cv2, numpy as np
src, out = sys.argv[1], sys.argv[2]
FPS, LOOP, XF = 30, 600, 60
W, H = 1920, 1080
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-crf', '12', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-g', '30', out], stdin=subprocess.PIPE)
for i in range(LOOP):
    f = cv2.imread(f'{src}/f_{i + 1:04d}.png').astype(np.float32)
    if i < XF:
        tail = cv2.imread(f'{src}/f_{LOOP + i + 1:04d}.png').astype(np.float32)
        k = (i + 0.5) / XF; k = k * k * (3 - 2 * k)            # 0 -> 1: tail (continuation of frame 600) -> head
        f = tail * (1 - k) + f * k
    p.stdin.write(np.clip(f + 0.5, 0, 255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
print('loop written', out)
