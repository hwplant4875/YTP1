"""RageStyles 'Ranking ... Moments' short builder (benchmark recipe, 2026-10-22).

Fixed black title bar, empty numbered list on the left that fills as each clip
plays (typewriter label), clip fitted below the bar over a blurred copy of
itself, hard cuts, original clip sound only, ends hard on #1.

usage: python3 build_ranking.py spec.json out.mp4
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, BAR = 1080, 1920, 30, 250
FONT = '/mnt/attach/project-files/fonts/YouTubeSans-Black.otf'
EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
NUM_COL = {1: (255, 212, 0), 2: (255, 59, 59), 3: (59, 164, 255), 4: (76, 255, 106), 5: (255, 255, 255)}
LIST_TOP, LIST_STEP = 560, 160
TYPE_SECS = 0.45


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def is_emoji(ch):
    return ord(ch) > 0x2500


def draw_text(img, xy, text, size, fill, stroke=8):
    """Draw text with black outline; emoji drawn from Noto Color Emoji."""
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, size)
    x, y = xy
    for ch in text:
        if is_emoji(ch):
            ef = ImageFont.truetype(EMOJI, 109)
            em = Image.new('RGBA', (140, 140), (0, 0, 0, 0))
            ImageDraw.Draw(em).text((0, 0), ch, font=ef, embedded_color=True)
            em = em.crop(em.getbbox()) if em.getbbox() else em
            s = int(size * 1.0)
            em = em.resize((s, int(em.height * s / em.width)), Image.LANCZOS)
            img.alpha_composite(em, (int(x), int(y + size * 0.05)))
            x += s + 4
            continue
        d.text((x, y), ch, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))
        x += d.textlength(ch, font=f)
    return x


def title_layer(spec):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(img).rectangle([0, 0, W, BAR], fill=(0, 0, 0, 255))
    f = ImageFont.truetype(FONT, 84)
    d = ImageDraw.Draw(img)
    for li, line in enumerate(spec['title']):  # line = [[text, rgb], ...]
        width = sum(d.textlength(t, font=f) for t, _ in line)
        x = (W - width) / 2
        y = 28 + li * 102
        for t, c in line:
            d.text((x, y), t, font=f, fill=tuple(c))
            x += d.textlength(t, font=f)
    return img


def list_layer(base, slots):
    """slots: {rank: label_text_so_far}; every rank 1..N shows its number."""
    img = base.copy()
    n = len(slots)
    for r in range(1, n + 1):
        y = LIST_TOP + (r - 1) * LIST_STEP
        x = draw_text(img, (24, y), f'{r}.', 96, NUM_COL[r], stroke=9)
        if slots[r]:
            draw_text(img, (x + 14, y + 24), slots[r], 56, (255, 255, 255), stroke=7)
    return img


def segment(clip, idx, tmp):
    """Cut one clip (possibly several sub-ranges), fit under the bar over a blurred fill."""
    parts = []
    for j, (a, b) in enumerate(clip['ranges']):
        out = os.path.join(tmp, f'seg{idx}_{j}.mp4')
        vf = (f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps={FPS},split[m][g];"
              f"[g]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.12[bg];"
              f"[m]scale={W}:{H - BAR}:force_original_aspect_ratio=decrease[fg];"
              f"[bg][fg]overlay=(W-w)/2:{BAR}+({H - BAR}-h)/2,format=yuv420p[v];"
              f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,loudnorm=I=-15:TP=-1.5:LRA=11[a]")
        run(['ffmpeg', '-y', '-i', clip['file'], '-filter_complex', vf, '-map', '[v]', '-map', '[a]',
             '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', out])
        parts.append((out, b - a))
    return parts


def main(spec_path, out):
    spec = json.load(open(spec_path))
    clips = spec['clips']  # played in this order; each has rank, label, file, ranges
    n = len(clips)
    tmp = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(out)))
    # 1) base video
    seg_files, t, starts = [], 0.0, []
    for i, c in enumerate(clips):
        starts.append(t)
        for f, d in segment(c, i, tmp):
            seg_files.append(f)
            t += d
    total = t
    with open(os.path.join(tmp, 'v.txt'), 'w') as fh:
        fh.writelines(f"file '{f}'\n" for f in seg_files)
    base = os.path.join(tmp, 'base.mp4')
    run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'v.txt'), '-c', 'copy', base])
    # 2) overlay states (title + list, typewriter steps)
    tl = title_layer(spec)
    slots = {r: '' for r in range(1, n + 1)}
    states = []  # (start_time, image)
    states.append((0.0, list_layer(tl, slots)))
    for i, c in enumerate(clips):
        label = c['label']
        steps = len(label)
        for k in range(1, steps + 1):
            slots[c['rank']] = label[:k]
            states.append((starts[i] + TYPE_SECS * k / steps, list_layer(tl, slots)))
    lines = []
    for k, (st, img) in enumerate(states):
        p = os.path.join(tmp, f'ov{k:03d}.png')
        img.save(p)
        end = states[k + 1][0] if k + 1 < len(states) else total
        lines.append(f"file '{p}'\nduration {max(end - st, 1 / FPS):.4f}\n")
    lines.append(f"file '{p}'\n")
    with open(os.path.join(tmp, 'ov.txt'), 'w') as fh:
        fh.writelines(lines)
    run(['ffmpeg', '-y', '-i', base, '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'ov.txt'),
         '-filter_complex', f'[1:v]fps={FPS},format=rgba[o];[0:v][o]overlay=0:0:shortest=1,format=yuv420p[v]',
         '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium',
         '-c:a', 'copy', '-movflags', '+faststart', out])
    print(f'{out}: {total:.1f}s, starts', [round(s, 2) for s in starts])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
