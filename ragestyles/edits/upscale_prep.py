"""Real-ESRGAN pre-pass for an edit spec: cut each shot's (and voice line's untouched) source range, upscale its frames
on the GPU with realesrgan-ncnn-vulkan, and write a new spec that points the shots at the upscaled clips.

    python upscale_prep.py spec.json ROOT ESRGAN_EXE [model] [scale]      e.g. realesr-animevideov3 2
writes ROOT/up/<name>/NN.mp4 and spec_up.json next to spec.json (voice lines keep the original sources).
"""
import json, os, shutil, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from animedit_ff import pieces_of


def main(spec_path, root, exe, model='realesr-animevideov3', scale='2'):
    spec = json.load(open(spec_path))
    out_dir = os.path.join(root, 'up', spec['name'])
    os.makedirs(out_dir, exist_ok=True)
    for i, s in enumerate(spec['shots']):
        pieces_of(s)                                           # fills "out" from "len"
        clip = os.path.join(out_dir, f'{i:02d}.mp4')
        if not os.path.exists(clip):
            tmp = tempfile.mkdtemp()
            os.makedirs(f'{tmp}/in'); os.makedirs(f'{tmp}/out')
            dur = s['out'] - s['in'] + 0.2
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{s['in']:.3f}", '-t', f'{dur:.3f}',
                            '-i', os.path.join(root, s['src']), '-fps_mode', 'passthrough', f'{tmp}/in/%05d.png'], check=True)
            fps = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=r_frame_rate',
                                  '-of', 'csv=p=0', os.path.join(root, s['src'])], capture_output=True, text=True).stdout.strip()
            subprocess.run([exe, '-i', f'{tmp}/in', '-o', f'{tmp}/out', '-n', model, '-s', scale, '-f', 'png'], check=True)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', fps, '-i', f'{tmp}/out/%05d.png',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '12', '-pix_fmt', 'yuv420p', clip], check=True)
            shutil.rmtree(tmp)
        length = s['out'] - s['in']
        sp = s.get('speed', 1.0)
        if isinstance(sp, list):
            s['speed'] = [[k - s['in'], v] for k, v in sp]
        s.pop('len', None)
        s.update({'src': os.path.relpath(clip, root).replace('\\', '/'), 'in': 0.0, 'out': length})
        print(i, s['src'])
    dst = os.path.splitext(spec_path)[0] + '_up.json'
    json.dump(spec, open(dst, 'w'), indent=1)
    print(dst)


if __name__ == '__main__':
    main(*sys.argv[1:])
