"""Cut a source video into a frame sequence for the engine.
usage: python3 prep_clip.py src.mp4 name --ss 3.2 --to 5.6 [--crop w:h:x:y] [--fps 30] [--slow 1]
-> $RS_WORK/clips/<name>/00001.jpg..., info.json, audio.wav (source audio of the same range)"""
import argparse, json, os, subprocess, glob
ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('name')
ap.add_argument('--ss', type=float, default=0); ap.add_argument('--to', type=float); ap.add_argument('--crop')
ap.add_argument('--fps', type=int, default=30); ap.add_argument('--maxw', type=int, default=1620)
a = ap.parse_args()
root = os.environ.get('RS_WORK', '/home/user/rs_work'); d = f'{root}/clips/{a.name}'
os.makedirs(d, exist_ok=True)
for f in glob.glob(f'{d}/*.jpg'): os.remove(f)
rng = ['-ss', str(a.ss)] + (['-to', str(a.to)] if a.to else [])
vf = ([f'crop={a.crop}'] if a.crop else []) + [f'fps={a.fps}', f"scale='min({a.maxw},iw)':-2:flags=lanczos"]
subprocess.run(['ffmpeg', '-v', 'error', '-y', *rng, '-i', a.src, '-vf', ','.join(vf), '-q:v', '2', f'{d}/%05d.jpg'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', *rng, '-i', a.src, '-vn', '-ac', '2', '-ar', '48000', f'{d}/audio.wav'])
n = len(glob.glob(f'{d}/*.jpg'))
w, h = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', f'{d}/00001.jpg'], capture_output=True, text=True).stdout.strip().split(',')
json.dump({'n': n, 'fps': a.fps, 'w': int(w), 'h': int(h), 'src': os.path.basename(a.src), 'ss': a.ss, 'to': a.to}, open(f'{d}/info.json', 'w'))
print(a.name, n, 'frames', w, h)
