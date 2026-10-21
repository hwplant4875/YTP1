"""Clean 1:1 editor: footage in a 1080x1080 square on a black 9:16 canvas, static title above,
one plain label line per athlete. Hard cuts, original audio with tiny fades. No flashes, no zooms.
usage: python3 sq.py spec.json out.mp4"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

FONT = '/home/user/rs_work/fonts/TikTokSans-Black.ttf'
W, H, SQ, TOP = 1080, 1920, 1080, 420


def fit(d, text, size, maxw):
    while size > 30:
        f = ImageFont.truetype(FONT, size)
        if d.textlength(text, font=f) <= maxw:
            return f
        size -= 2
    return ImageFont.truetype(FONT, size)


def overlay(title, label, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = fit(d, title, 64, 980)
    d.text((W / 2, 250), title, font=f, fill='white', anchor='ms')
    if label:
        f2 = fit(d, label, 56, 980)
        d.text((W / 2, 350), label, font=f2, fill='#ffd400', anchor='ms')
    im.save(path)


def main(spec_path, out):
    spec = json.load(open(spec_path))
    tmp = tempfile.mkdtemp(prefix='sq_')
    parts = []
    for i, s in enumerate(spec['segs']):
        png = f'{tmp}/o{i}.png'
        overlay(spec['title'], s.get('label'), png)
        dur = s['out'] - s['in']
        cx = s.get('cx', 0.5)
        # square crop of side = source height (or the 4:3 inner picture), positioned by cx
        vf = (f"[0:v]crop=ih:ih:(iw-ih)*{cx}:0,scale={SQ}:{SQ}:flags=lanczos,"
              f"eq=contrast=1.05:brightness=0.015:saturation=1.05,unsharp=5:5:0.6,"
              f"pad={W}:{H}:0:{TOP}:black,setsar=1,fps=30[v];[v][1:v]overlay=0:0[o]")
        af = f"afade=t=in:d=0.06,afade=t=out:st={dur - 0.08:.3f}:d=0.08,aresample=48000"
        p = f'{tmp}/p{i:02d}.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(s['in']), '-t', f'{dur:.3f}', '-i', s['src'],
                        '-i', png, '-filter_complex', vf, '-map', '[o]', '-map', '0:a', '-af', af,
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '192k', '-ac', '2', p], check=True)
        parts.append(p)
    lst = f'{tmp}/list.txt'
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    end = spec.get('endfade', 0.6)
    total = sum(s['out'] - s['in'] for s in spec['segs'])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-vf', f'fade=t=out:st={total - end:.3f}:d={end}', '-af', f'afade=t=out:st={total - end:.3f}:d={end}',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out], check=True)
    print(out, round(total, 1))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
