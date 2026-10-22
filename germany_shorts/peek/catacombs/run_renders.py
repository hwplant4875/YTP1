# Laptop render queue for the catacombs Blender shots.
# usage: python run_renders.py BLENDER_EXE OUT_DIR [SHOT ...]
# Renders every shot (or the given ones) to OUT_DIR/<shot>/####.png with EEVEE on the GPU, then encodes
# OUT_DIR/mp4/<shot>.mp4 (H.264 CRF 16, 24 fps). Finished shots are skipped, so it can be re-run after a stop.
import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ORDER = ['SH01_street', 'SH02_tunnel_sign', 'SH03_cinema', 'SH04_screen', 'SH05_cinema_dark', 'SH06_descent',
         'SH07_stone', 'SH08_sea', 'SH09_shaft', 'SH10_roots', 'SH11_collapse', 'SH12_pillars']


def main():
    blender, out = sys.argv[1], sys.argv[2]
    shots = sys.argv[3:] or ORDER
    os.makedirs(os.path.join(out, 'mp4'), exist_ok=True)
    log = open(os.path.join(out, 'render_log.txt'), 'a', encoding='utf-8')
    for sh in shots:
        mp4 = os.path.join(out, 'mp4', sh + '.mp4')
        if os.path.exists(mp4):
            continue
        t = time.time()
        r = subprocess.run([blender, '-b', '-P', os.path.join(HERE, 'shots.py'), '--', sh, out],
                           capture_output=True, text=True, errors='replace')
        frames = os.path.join(out, sh)
        n = len([f for f in os.listdir(frames) if f.endswith('.png')]) if os.path.isdir(frames) else 0
        if r.returncode != 0 or n == 0:
            log.write(f'{sh} FAILED rc={r.returncode}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}\n'); log.flush()
            continue
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', '24', '-i', os.path.join(frames, '%04d.png'),
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', mp4], check=True)
        dt = time.time() - t
        log.write(f'{sh} ok {n} frames {dt / 60:.1f} min ({dt / max(n, 1):.1f} s/frame)\n'); log.flush()
        print(sh, 'ok', n, round(dt / 60, 1), 'min', flush=True)


if __name__ == '__main__':
    main()
