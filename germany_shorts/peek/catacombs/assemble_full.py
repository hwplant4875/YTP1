# Assemble the full catacombs long-form: Blender shot mp4s + photos + key text + narration, music and sound design.
# usage: python3 assemble_full.py CLIPS_DIR PHOTOS_DIR AUDIO_DIR OUT.mp4 [END_SECONDS]
#   CLIPS_DIR/<shot>.mp4 (run_renders.py), PHOTOS_DIR/<name>.jpg, AUDIO_DIR: vo_full.wav, music_a.mp3, music_b.mp3, sfx/*.wav
# Text is burned into each segment before the dissolve chain, so the final pass stays light.
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CLIPS, PHOTOS, AUDIO, OUT = sys.argv[1:5]
END = float(sys.argv[5]) if len(sys.argv) > 5 else 337.2
FPS, W, H, XF = 24, 1920, 1080, 0.4
WORK = os.path.join(os.path.dirname(os.path.abspath(OUT)), 'full_work'); os.makedirs(WORK, exist_ok=True)
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'fonts', 'YouTubeSans-Black.otf')
YEL = (255, 196, 0)

# (start, end, kind, source, options) on the final timeline. options: ss = offset into the clip, x = dissolve INTO this segment
SEG = [
    (0.0, 26.0, 'clip', 'SH00_opening', {}),
    # real skulls, hard cuts right after the 3D skull wall
    (26.0, 26.4, 'flash', 'f01', {'x': 0.04}), (26.4, 26.8, 'flash', 'f02', {'x': 0.04}), (26.8, 27.2, 'flash', 'f03', {'x': 0.04}),
    (27.2, 27.6, 'flash', 'f04', {'x': 0.04}), (27.6, 28.0, 'flash', 'f05', {'x': 0.04}),
    # 1. the cinema nobody built
    (28.0, 36.4, 'clip', 'SH01_street', {'x': 0.04}), (36.4, 41.9, 'clip', 'SH02_tunnel_sign', {}), (41.9, 55.5, 'clip', 'SH03_cinema', {}),
    (55.5, 58.2, 'clip', 'SH04_screen', {}), (58.2, 68.9, 'clip', 'SH05_cinema_dark', {}),
    # 2. the city that ate itself
    (68.9, 75.6, 'clip', 'SH06_descent', {}), (75.6, 80.9, 'clip', 'SH07_stone', {}), (80.9, 89.9, 'clip', 'SH08_sea', {}),
    (89.9, 97.2, 'clip', 'SH09_shaft', {}), (97.2, 99.5, 'photo', 'p01_notre_dame', {}), (99.5, 101.7, 'photo', 'p02_louvre', {}),
    (101.7, 113.3, 'clip', 'SH10_roots', {}), (113.3, 128.7, 'clip', 'SH11_collapse', {}), (128.7, 137.2, 'clip', 'SH12_pillars', {}),
    # 3. six million bones
    (137.2, 141.7, 'photo', 'p03_innocents_sign', {}), (141.7, 146.0, 'photo', 'p04_triumph_death', {}), (146.0, 150.2, 'photo', 'p05_tomb', {}),
    (150.2, 153.6, 'photo', 'p06_heap', {}), (153.6, 160.4, 'photo', 'p07_dark_tunnel', {}), (160.4, 165.0, 'photo', 'p08_stjean_sign', {}),
    (165.0, 169.3, 'photo', 'p09_madeleine_sign', {}), (169.3, 173.6, 'photo', 'p10_crypt', {}), (173.6, 179.6, 'photo', 'p11_ossuary_wide', {}),
    (179.6, 183.3, 'photo', 'p12_heap2', {}), (183.3, 187.0, 'photo', 'p13_pillar_sign', {}), (187.0, 189.7, 'photo', 'p14_cross', {}),
    (189.7, 192.4, 'photo', 'p15_barrel', {}), (192.4, 195.2, 'photo', 'p16_skull_row', {}), (195.2, 201.2, 'photo', 'p17_empire_sign', {}),
    (201.2, 206.0, 'photo', 'p18_gallery', {}), (206.0, 210.6, 'photo', 'p19_skulls', {}),
    # 4. the man who never came back
    (210.6, 224.4, 'clip', 'SH13_candle', {}), (224.4, 232.2, 'clip', 'SH14_keys', {'x': 0.04}), (232.2, 237.6, 'photo', 'p20_dark_corridor', {}),
    # 5. the forbidden tunnels
    (237.6, 252.3, 'clip', 'SH15_map', {}), (252.3, 256.0, 'photo', 'p21_liberation_1944', {}), (256.0, 261.0, 'photo', 'p22_resistance_stairs', {}),
    (261.0, 265.6, 'photo', 'p23_bunker_corridor', {}), (265.6, 272.3, 'clip', 'SH02_tunnel_sign', {}), (272.3, 274.6, 'photo', 'p24_graffiti_face', {}),
    (274.6, 280.2, 'clip', 'SH00_opening', {'ss': 8.0}), (280.2, 282.4, 'photo', 'p25_graffiti_teeth', {}), (282.4, 285.0, 'photo', 'p26_graffiti_tunnel', {}),
    (285.0, 288.0, 'photo', 'p27_flashlight_tunnel', {}), (288.0, 291.3, 'photo', 'p28_dark_gallery', {}), (291.3, 294.9, 'photo', 'p29_portmahon_palace', {}),
    # 6. who built the cinema
    (294.9, 300.8, 'clip', 'SH03_cinema', {}), (300.8, 306.4, 'clip', 'SH03_cinema', {'ss': 6.0}), (306.4, 309.1, 'clip', 'SH05_cinema_dark', {}),
    (309.1, 314.0, 'clip', 'SH05_cinema_dark', {'ss': 6.0}), (314.0, 320.7, 'photo', 'p30_paris_night', {}), (320.7, 322.9, 'photo', 'p31_skull_row', {}),
    (322.9, 325.0, 'clip', 'SH15_map', {'ss': 12.5}), (325.0, 327.0, 'photo', 'p32_portmahon', {}), (327.0, 330.6, 'clip', 'SH00_opening', {'ss': 8.5}),
    (330.6, 337.2, 'clip', 'SH00_opening', {'ss': 20.0}),
]
# big key text: (start, end, lines, highlighted line)
TEXT = [
    (28.4, 35.6, ['AUGUST 2004'], 0), (38.0, 41.6, ['BUILDING SITE.', 'NO ACCESS.'], 1),
    (43.2, 47.2, ['A SECRET', 'CINEMA'], 1), (55.6, 58.1, ['WHO BUILT IT?'], 0),
    (66.0, 68.8, ['"DO NOT TRY', 'TO FIND US."'], -1), (76.0, 80.6, ['BUILT ON STONE'], 0),
    (81.3, 86.5, ['45 MILLION', 'YEARS AGO'], 0), (97.4, 99.4, ['NOTRE-DAME'], -1), (99.6, 101.6, ['THE LOUVRE'], -1),
    (114.0, 119.5, ['1774', "RUE D'ENFER"], 0), (119.6, 123.4, ['"HELL STREET"'], 0), (124.0, 128.4, ['STANDING ON AIR'], 0),
    (130.0, 136.8, ['QUARRY', 'INSPECTORS'], 1), (142.5, 145.8, ['2,000,000', 'BODIES'], 0), (153.8, 159.5, ['1780'], 0),
    (174.0, 179.3, ['6,000,000', 'PEOPLE'], 0), (202.0, 205.8, ['14°C', '20 M DEEP', '131 STEPS'], -1),
    (211.2, 216.4, ['1793'], 0), (232.6, 237.2, ['PHILIBERT ASPAIRT', 'LOST 1793. FOUND 1804.'], 1),
    (242.0, 244.9, ['TOURISTS', '1.5 KM'], 1), (245.4, 252.0, ['THE FULL NETWORK', 'UP TO 300 KM'], 1),
    (252.6, 255.8, ['1944'], 0), (256.4, 260.6, ['RESISTANCE', 'HEADQUARTERS'], 1), (261.4, 265.3, ['GERMAN', 'BUNKER'], 1),
    (266.0, 271.9, ['1955', 'ILLEGAL'], 1), (275.0, 279.8, ['CATAPHILES'], 0), (285.4, 290.9, ['"CATAFLICS"'], 0),
    (295.4, 300.4, ['LA MEXICAINE', 'DE PERFORATION'], 1), (320.9, 326.6, ['6,000,000 DEAD', '300 KM OF TUNNELS'], 0),
    (327.4, 330.4, ['LOOK DOWN.'], 0),
]
# sound design: (file, start s, gain, fade in, fade out, max length)
SFX = [
    ('city_night.wav', 0.0, 0.45, 0.0, 3.0, 13.0), ('whoosh_big.wav', 6.0, 0.5, 0.0, 0.5, 3.7),
    ('metal_scrape.wav', 12.2, 0.3, 0.0, 0.5, 2.6), ('whoosh_cam.wav', 13.4, 0.5, 0.0, 0.2, 1.0),
    ('cave_amb.wav', 12.5, 0.55, 2.0, 1.5, 16.0), ('impact_big.wav', 20.9, 0.6, 0.0, 1.5, 6.8),
    ('impact_sub.wav', 26.0, 0.7, 0.0, 1.0, 4.1), ('cave_amb.wav', 210.6, 0.35, 1.5, 1.5, 14.0),
    ('impact_sub.wav', 222.4, 0.45, 0.0, 1.0, 4.1), ('cave_amb.wav', 330.6, 0.4, 1.5, 3.0, 6.6),
]


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


def photo_frames(name, dur, idx, flash=False):
    im = Image.open(os.path.join(PHOTOS, name + '.jpg')).convert('RGB')
    s = max(W / im.width, H / im.height) * 1.12; im = im.resize((int(im.width * s) + 2, int(im.height * s) + 2), Image.LANCZOS)
    n = int(round(dur * FPS)); zin = idx % 2 == 0
    for k in range(n):
        t = k / max(1, n - 1); e = t * t * (3 - 2 * t)
        z = (1.0 + 0.05 * t) if flash else 1.0 + (0.07 * e if zin else 0.07 * (1 - e))
        cw = im.width / z; ch = cw * H / W
        if ch > im.height / z: ch = im.height / z; cw = ch * W / H
        cx = im.width / 2 + (0 if flash else (e - 0.5) * (im.width - cw) * 0.5 * (1 if idx % 3 else -1))
        cy = im.height / 2
        yield im.transform((W, H), Image.EXTENT, (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2), Image.BICUBIC).tobytes()


def build_segment(i, a, b, kind, src, opt, xnext):
    dur = b - a + xnext
    out = os.path.join(WORK, f'seg{i:02d}.mp4')
    texts = [(ta, tb, text_png(j, l, h)) for j, (ta, tb, l, h) in enumerate(TEXT) if a <= ta < b]
    raw = os.path.join(WORK, f'raw{i:02d}.mp4')
    enc = ['-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p']
    if kind == 'clip':
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f"{opt.get('ss', 0):.3f}", '-i', os.path.join(CLIPS, src + '.mp4'),
                        '-vf', f'fps={FPS},scale={W}:{H},tpad=stop_mode=clone:stop_duration=3', '-t', f'{dur:.3f}'] + enc + [raw], check=True)
    else:
        p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
                             + enc + [raw], stdin=subprocess.PIPE)
        for fr in photo_frames(src, dur, i, kind == 'flash'): p.stdin.write(fr)
        p.stdin.close(); p.wait()
    if not texts:
        os.replace(raw, out); return out
    args = ['ffmpeg', '-y', '-v', 'error', '-i', raw]
    fc = []; last = '[0:v]'
    for j, (ta, tb, png) in enumerate(texts):
        args += ['-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.3f}', '-i', png]
        s0, s1 = ta - a, min(tb, b) - a
        fc.append(f'[{j + 1}:v]format=rgba,fade=t=in:st={s0:.2f}:d=0.25:alpha=1,fade=t=out:st={s1 - 0.3:.2f}:d=0.3:alpha=1[t{j}]')
        fc.append(f"{last}[t{j}]overlay=enable='between(t,{s0:.2f},{s1:.2f})'[o{j}]"); last = f'[o{j}]'
    args += ['-filter_complex', ';'.join(fc), '-map', last, '-t', f'{dur:.3f}'] + enc + [out]
    subprocess.run(args, check=True); os.remove(raw)
    return out


def main():
    segs = [s for s in SEG if s[0] < END]
    parts = []
    for i, (a, b, kind, src, opt) in enumerate(segs):
        b = min(b, END)
        xnext = segs[i + 1][4].get('x', XF) if i + 1 < len(segs) and segs[i + 1][0] < END else 0
        out = os.path.join(WORK, f'seg{i:02d}.mp4')
        if not os.path.exists(out):
            build_segment(i, a, b, kind, src, opt, xnext)
        parts.append((out, b - a + xnext, opt.get('x', XF)))
        print('seg', i, src, flush=True)
    args = ['ffmpeg', '-y', '-v', 'error']
    for p, _, _ in parts: args += ['-i', p]
    fc = []; last = '[0:v]'; acc = parts[0][1]
    for k in range(1, len(parts)):
        x = parts[k][2]; off = acc - x
        fc.append(f'{last}[{k}:v]xfade=transition=fade:duration={x}:offset={off:.3f}[x{k}]'); last = f'[x{k}]'
        acc = off + parts[k][1]
    fc.append(f'{last}trim=0:{END:.3f},setpts=PTS-STARTPTS,fade=t=out:st={END - 1.2:.2f}:d=1.2[v]')
    # audio
    base = len(parts)
    args += ['-i', os.path.join(AUDIO, 'vo_full.wav'), '-i', os.path.join(AUDIO, 'music_a.mp3'), '-i', os.path.join(AUDIO, 'music_b.mp3')]
    for f, *_ in SFX: args += ['-i', os.path.join(AUDIO, 'sfx', f)]
    fc.append(f'[{base}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,atrim=0:{END:.3f}[vo]')
    ma0, mb0 = 28.0, 214.0
    fc.append(f'[{base + 1}:a]aresample=48000,atrim=0:{mb0 + 4 - ma0:.2f},afade=t=in:d=1.5,afade=t=out:st={mb0 - ma0:.2f}:d=4,'
              f'adelay={int(ma0 * 1000)}|{int(ma0 * 1000)}[ma]')
    fc.append(f'[{base + 2}:a]aresample=48000,afade=t=in:d=4,atrim=0:{END - mb0:.2f},afade=t=out:st={END - mb0 - 3:.2f}:d=3,'
              f'adelay={int(mb0 * 1000)}|{int(mb0 * 1000)}[mb]')
    fc.append('[ma][mb]amix=inputs=2:normalize=0,volume=0.16,treble=g=-4:f=3000[mu]')
    names = []
    for j, (f, t0, g, fi, fo, ln) in enumerate(SFX):
        fc.append(f'[{base + 3 + j}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{ln},volume={g},'
                  f'afade=t=in:d={max(fi, 0.01)},afade=t=out:st={max(0, ln - fo):.2f}:d={fo},adelay={int(t0 * 1000)}|{int(t0 * 1000)}[s{j}]')
        names.append(f'[s{j}]')
    fc.append(f'[vo][mu]{"".join(names)}amix=inputs={2 + len(names)}:normalize=0,atrim=0:{END:.3f},'
              f'loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000[a]')
    args += ['-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
             '-pix_fmt', 'yuv420p', '-r', str(FPS), '-c:a', 'aac', '-b:a', '256k', '-t', f'{END:.3f}', '-movflags', '+faststart', OUT]
    subprocess.run(args, check=True)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
