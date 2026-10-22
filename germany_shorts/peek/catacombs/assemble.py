# Assemble the catacombs video (first half or full) from Blender shot mp4s, photos, text overlays and audio.
# usage: python3 assemble.py CLIPS_DIR PHOTOS_DIR AUDIO_DIR OUT.mp4 [END_SECONDS]
#   CLIPS_DIR/<shot>.mp4 from run_renders.py, PHOTOS_DIR/<slot>.jpg, AUDIO_DIR has vo_track.wav + music_a.mp3
import os, subprocess, sys, json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CLIPS, PHOTOS, AUDIO, OUT = sys.argv[1:5]
END = float(sys.argv[5]) if len(sys.argv) > 5 else 182.6
FPS, W, H, XF = 24, 1920, 1080, 0.4
WORK = os.path.join(os.path.dirname(os.path.abspath(OUT)), 'asm_work'); os.makedirs(WORK, exist_ok=True)
FONT = '/home/user/YTP1/germany_shorts/fonts/YouTubeSans-Black.otf'

# visual timeline: (start, end, kind, source)
SEG = [
    (0.0, 8.4, 'clip', 'SH01_street'), (8.4, 13.9, 'clip', 'SH02_tunnel_sign'), (13.9, 27.5, 'clip', 'SH03_cinema'),
    (27.5, 30.2, 'clip', 'SH04_screen'), (30.2, 40.9, 'clip', 'SH05_cinema_dark'), (40.9, 47.6, 'clip', 'SH06_descent'),
    (47.6, 52.9, 'clip', 'SH07_stone'), (52.9, 61.9, 'clip', 'SH08_sea'), (61.9, 69.2, 'clip', 'SH09_shaft'),
    (69.2, 71.5, 'photo', 'p01_notre_dame'), (71.5, 73.7, 'photo', 'p02_louvre'),
    (73.7, 85.3, 'clip', 'SH10_roots'), (85.3, 100.7, 'clip', 'SH11_collapse'), (100.7, 109.2, 'clip', 'SH12_pillars'),
    (109.2, 113.7, 'photo', 'p03_innocents_sign'), (113.7, 118.0, 'photo', 'p04_triumph_death'), (118.0, 122.2, 'photo', 'p05_tomb'),
    (122.2, 125.6, 'photo', 'p06_heap'), (125.6, 132.4, 'photo', 'p07_dark_tunnel'), (132.4, 137.0, 'photo', 'p08_stjean_sign'),
    (137.0, 141.3, 'photo', 'p09_madeleine_sign'), (141.3, 145.6, 'photo', 'p10_crypt'), (145.6, 151.6, 'photo', 'p11_ossuary_wide'),
    (151.6, 155.3, 'photo', 'p12_heap2'), (155.3, 159.0, 'photo', 'p13_pillar_sign'), (159.0, 161.7, 'photo', 'p14_cross'),
    (161.7, 164.4, 'photo', 'p15_barrel'), (164.4, 167.2, 'photo', 'p16_skull_row'), (167.2, 173.2, 'photo', 'p17_empire_sign'),
    (173.2, 178.0, 'photo', 'p18_gallery'), (178.0, 182.6, 'photo', 'p19_skulls'),
]
# big key text: (start, end, lines, highlight index)
TEXT = [
    (0.0, 7.6, ['AUGUST 2004'], 0), (9.6, 13.6, ['BUILDING SITE.', 'NO ACCESS.'], 1),
    (15.2, 19.2, ['A SECRET', 'CINEMA'], 1), (27.6, 30.1, ['WHO BUILT IT?'], 0),
    (38.0, 40.8, ['"DO NOT TRY', 'TO FIND US."'], -1), (48.0, 52.6, ['BUILT ON STONE'], 0),
    (53.3, 58.5, ['45 MILLION', 'YEARS AGO'], 0), (69.4, 71.4, ['NOTRE-DAME'], -1), (71.6, 73.6, ['THE LOUVRE'], -1),
    (86.0, 91.5, ['1774', "RUE D'ENFER"], 0), (91.6, 95.4, ['"HELL STREET"'], 0), (96.0, 100.4, ['STANDING ON AIR'], 0),
    (102.0, 108.8, ['QUARRY', 'INSPECTORS'], 1), (114.5, 121.8, ['2,000,000', 'BODIES'], 0), (125.8, 131.5, ['1780'], 0),
    (146.0, 151.3, ['6,000,000', 'PEOPLE'], 0),
    (174.0, 182.0, ['14°C', '20 M DEEP', '131 STEPS'], -1),
]
YEL = (255, 196, 0)


def text_png(i, lines, hi):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    size = 120 if max(len(l) for l in lines) <= 14 else 92
    f = ImageFont.truetype(FONT, size)
    lh = int(size * 1.08); y0 = H // 2 - lh * len(lines) // 2 + 40
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    for k, l in enumerate(lines):
        ds.text((W // 2, y0 + k * lh), l, font=f, anchor='ma', fill=(0, 0, 0, 200), stroke_width=12, stroke_fill=(0, 0, 0, 200))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    for k, l in enumerate(lines):
        d.text((W // 2, y0 + k * lh), l, font=f, anchor='ma', fill=YEL if k == hi else (255, 255, 255),
               stroke_width=9, stroke_fill=(0, 0, 0))
    p = os.path.join(WORK, f'text{i:02d}.png'); im.save(p); return p


def photo_clip(name, dur, out, idx):
    src = os.path.join(PHOTOS, name + '.jpg')
    im = Image.open(src).convert('RGB')
    s = max(W / im.width, H / im.height) * 1.12; im = im.resize((int(im.width * s) + 2, int(im.height * s) + 2), Image.LANCZOS)
    n = int(round(dur * FPS))
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    zin = idx % 2 == 0
    for k in range(n):
        t = k / max(1, n - 1); e = t * t * (3 - 2 * t)
        z = 1.0 + (0.07 * e if zin else 0.07 * (1 - e))
        cw = im.width / z; ch = cw * H / W
        if ch > im.height / z: ch = im.height / z; cw = ch * W / H
        cx = im.width / 2 + (e - 0.5) * (im.width - cw) * 0.5 * (1 if idx % 3 else -1)
        cy = im.height / 2
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
        fr = im.transform((W, H), Image.EXTENT, box, Image.BICUBIC)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()


def main():
    parts = []
    for i, (a, b, kind, src) in enumerate([s for s in SEG if s[0] < END]):
        b = min(b, END); dur = b - a + (XF if b < END else 0)
        out = os.path.join(WORK, f'seg{i:02d}.mp4')
        if kind == 'clip':
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(CLIPS, src + '.mp4'), '-t', f'{dur:.3f}',
                            '-vf', f'fps={FPS},scale={W}:{H},tpad=stop_mode=clone:stop_duration=2', '-t', f'{dur:.3f}',
                            '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], check=True)
        else:
            photo_clip(src, dur, out, i)
        parts.append((out, dur))
    # chain cross dissolves
    args = ['ffmpeg', '-y', '-v', 'error']
    for p, _ in parts: args += ['-i', p]
    texts = [(a, b, text_png(i, l, h)) for i, (a, b, l, h) in enumerate(TEXT) if a < END]
    for _, _, t in texts: args += ['-loop', '1', '-framerate', str(FPS), '-i', t]
    fc = []; last = '[0:v]'; acc = parts[0][1]
    for k in range(1, len(parts)):
        off = acc - XF
        fc.append(f'{last}[{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{k}]'); last = f'[x{k}]'
        acc = off + parts[k][1]
    base = len(parts)
    for j, (a, b, _) in enumerate(texts):
        fc.append(f'[{base + j}:v]format=rgba,fade=t=in:st={a:.2f}:d=0.25:alpha=1,fade=t=out:st={b - 0.3:.2f}:d=0.3:alpha=1[t{j}]')
        fc.append(f"{last}[t{j}]overlay=enable='between(t,{a:.2f},{b:.2f})'[o{j}]"); last = f'[o{j}]'
    fc.append(f'{last}trim=0:{END:.3f},setpts=PTS-STARTPTS[v]')
    # audio: narration + quiet music (stereo kept, highs softened)
    args += ['-i', os.path.join(AUDIO, 'vo_track.wav'), '-i', os.path.join(AUDIO, 'music_a.mp3')]
    ai = base + len(texts)
    fc.append(f'[{ai}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,atrim=0:{END:.3f}[vo]')
    fc.append(f'[{ai + 1}:a]aresample=48000,atrim=0:{END:.3f},volume=0.16,treble=g=-4:f=3000,afade=t=out:st={END - 2.5:.2f}:d=2.5[mu]')
    fc.append('[vo][mu]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]')
    args += ['-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium',
             '-pix_fmt', 'yuv420p', '-r', str(FPS), '-c:a', 'aac', '-b:a', '256k', '-t', f'{END:.3f}', OUT]
    subprocess.run(args, check=True)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
