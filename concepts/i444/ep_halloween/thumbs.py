# Halloween special thumbnails (upload_kit_v1.md): EP03 C layout = 1280x720, three panels 427/426/427 with thin black gutters,
# f(182) % at the bottom of each panel in its tier colour, the face bigger as the survival rate falls; C = Art alone with a huge 3%.
# Sources are HD frames of the official clips in E:\YTP2\Instruction444\clips\halloween (never committed).
# usage: python thumbs.py [clips_dir] [out_dir]
import os, sys, io, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ep01'))
from gfx import f, shadow_text
CLIPS = sys.argv[1] if len(sys.argv) > 1 else 'E:/YTP2/Instruction444/clips/halloween'
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'upload')
W, H = 1280, 720; PW = [427, 426, 427]
GREEN = (70, 215, 95, 255); YEL = (250, 200, 40, 255); RED = (235, 30, 38, 255); ORANGE = (255, 130, 20, 255)
def frame(clip, t):
    png = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', os.path.join(CLIPS, clip + '.mp4'), '-frames:v', '1',
                                   '-f', 'image2pipe', '-vcodec', 'png', '-'])
    return Image.open(io.BytesIO(png)).convert('RGB')
def grade(im, bright=1.0, contrast=1.12, sat=0.9):
    im = ImageEnhance.Brightness(im).enhance(bright); im = ImageEnhance.Contrast(im).enhance(contrast)
    return ImageEnhance.Color(im).enhance(sat)
def panel(sp, pw):
    """crop a pw x H window around the face (cx, cy in 1920x1080), face height = face_px in the output"""
    im = grade(frame(sp['clip'], sp['t']), sp.get('bright', 1.0))
    s = sp['face_px'] / sp['face_h']                      # output px per source px
    big = im.resize((int(1920 * s), int(1080 * s)), Image.LANCZOS)
    cx, cy = sp['cx'] * s, sp['cy'] * s
    x0 = int(min(max(cx - pw / 2, 0), big.width - pw)); y0 = int(min(max(cy - sp.get('eye_y', 250), 0), big.height - H))
    p = big.crop((x0, y0, x0 + pw, y0 + H)).convert('RGBA')
    v = np.linspace(0, 1, H)[:, None]; a = (np.clip((v - 0.55) / 0.45, 0, 1) ** 1.5 * 200).astype(np.uint8)   # dark bottom for the %
    p.alpha_composite(Image.merge('RGBA', [Image.new('L', (pw, H), 0)] * 3 + [Image.fromarray(np.repeat(a, pw, 1), 'L')]))
    return p
def three(specs, name):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); x = 0
    for sp, pw in zip(specs, PW): im.alpha_composite(panel(sp, pw), (x, 0)); x += pw
    d = ImageDraw.Draw(im); x = 0
    for k in (1, 2): gx = sum(PW[:k]); d.rectangle([gx - 3, 0, gx + 3, H], fill=(0, 0, 0, 255))
    for sp, pw in zip(specs, PW): shadow_text(im, (x + pw // 2, H - 178), sp['pct'], f(182), sp['col'], stroke=8); x += pw
    im.convert('RGB').save(os.path.join(OUT, name), quality=92); print(name)
SLAPPY = dict(clip='gb2_dummy', t=314, cx=965, cy=330, face_h=320, face_px=290, eye_y=180, pct='98%', col=GREEN, bright=1.25)
MICHAEL = dict(clip='h78_trailer_rt', t=1.5, cx=640, cy=420, face_h=800, face_px=560, pct='30%', col=YEL, eye_y=235)
SAM = dict(clip='trt_trailer', t=96.5, cx=1380, cy=560, face_h=420, face_px=300, pct='62%', col=YEL, bright=1.9)
SWEET16 = dict(clip='tk_trailer', t=101.6, cx=820, cy=380, face_h=420, face_px=310, pct='80%', col=GREEN, eye_y=230, bright=1.5)
ART = dict(clip='t2_trailer', t=48.2, cx=730, cy=400, face_h=480, face_px=380, pct='3%', col=RED, eye_y=250)
os.makedirs(OUT, exist_ok=True)
three([SWEET16, MICHAEL, ART], 'halloween_thumb_a.jpg')   # owner 10/31: Goosebumps 2 dropped, so no Slappy
three([dict(SAM), MICHAEL, ART], 'halloween_thumb_b.jpg')
# C: Art alone, full frame, huge red 3% and a small orange HALLOWEEN NIGHT tag
im = grade(frame('t1_trailer', 22.6)).resize((W, H), Image.LANCZOS).convert('RGBA')
im = im.crop((0, 0, W, H))
sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); v = np.linspace(0, 1, W)[None, :]
a = (np.clip((v - 0.45) / 0.4, 0, 1) * 170).astype(np.uint8); sh.putalpha(Image.fromarray(np.repeat(a, H, 0), 'L')); im.alpha_composite(sh)
shadow_text(im, (1010, 400), '3%', f(330), RED, stroke=10)
d = ImageDraw.Draw(im); tw = d.textlength('HALLOWEEN NIGHT', font=f(54)) + 44
d.rounded_rectangle([1010 - tw / 2, 560, 1010 + tw / 2, 636], 14, fill=ORANGE)
d.text((1010, 600), 'HALLOWEEN NIGHT', font=f(54), fill=(15, 12, 12), anchor='mm')
im.convert('RGB').save(os.path.join(OUT, 'halloween_thumb_c.jpg'), quality=92); print('halloween_thumb_c.jpg')
