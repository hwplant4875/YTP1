# Halloween special thumbnails (upload_kit_v1.md): EP03 C layout = 1280x720, three panels 427/426/427 with thin black gutters,
# f(182) % at the bottom of each panel in its tier colour, the face bigger as the survival rate falls; C = Art alone with a huge 3%.
# Sources are HD frames of the official clips in E:\YTP2\Instruction444\clips\halloween (never committed).
# usage: python thumbs.py [clips_dir] [out_dir]
import os, sys, io, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
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
    im = Image.open(io.BytesIO(png)).convert('RGB')
    return im if im.size == (1920, 1080) else im.resize((1920, 1080), Image.LANCZOS)   # 1440p sources -> 1920x1080 coordinates
def grade(im, bright=1.0, contrast=1.18, sat=0.95):
    im = ImageEnhance.Brightness(im).enhance(bright); im = ImageEnhance.Contrast(im).enhance(contrast)
    return ImageEnhance.Color(im).enhance(sat)
def panel(sp, pw):
    """crop a pw x H window around the face (cx, cy in 1920x1080), face height = face_px in the output"""
    im = grade(frame(sp['clip'], sp['t']), sp.get('bright', 1.0))
    s = sp['face_px'] / sp['face_h']                      # output px per source px
    if sp.get('blurfill'):                                # letterboxed source zoomed out: fill the panel with a blurred, enlarged copy behind it
        t0, t1 = sp['blurfill']; bg = im.crop((0, t0, 1920, t1)).resize((int(1920 * H / (t1 - t0)), H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(30))
        bg = ImageEnhance.Brightness(bg).enhance(0.6)
        bx = int(min(max(sp['cx'] * H / (t1 - t0) - pw / 2, 0), bg.width - pw)); bg = bg.crop((bx, 0, bx + pw, H))
    else: s = max(s, H / 1080, pw / 1920)                # never smaller than the panel (no black bars)
    big = im.resize((int(1920 * s), int(1080 * s)), Image.LANCZOS)
    cx, cy = sp['cx'] * s, sp['cy'] * s
    x0 = int(min(max(cx - pw / 2, 0), big.width - pw)); y0 = int(min(max(cy - sp.get('eye_y', 250), 0), big.height - H))
    p = big.crop((x0, y0, x0 + pw, y0 + H)).convert('RGBA')
    if sp.get('blurfill'):
        top = int(sp['blurfill'][0] * s) - y0; bot = int(sp['blurfill'][1] * s) - y0
        canvas = bg.convert('RGBA'); canvas.alpha_composite(p.crop((0, max(top, 0), pw, min(bot, H))), (0, max(top, 0))); p = canvas
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
# owner 10/31 13:48 (standing rule): left GREEN %, middle YELLOW %, right RED %; the three variants must look very different;
# zoomed in, the face fills most of the panel with the eyes in the upper third, % below the face. Coordinates = 1920x1080 frame.
def P(clip, t, cx, cy, face_h, pct, col, bright=1.15, face_px=430, eye_y=300, blurfill=None): return dict(clip=clip, t=t, cx=cx, cy=cy, face_h=face_h, pct=pct, col=col, bright=bright, face_px=face_px, eye_y=eye_y, blurfill=blurfill)
os.makedirs(OUT, exist_ok=True)
three([P('tk_trailer', 101.6, 840, 330, 330, '99%', GREEN, 1.6, face_px=340, eye_y=240), P('h78_best_hd', 402.5, 1140, 360, 230, '30%', YEL, 1.8, face_px=340, eye_y=260),
       P('t2_costume_hd', 85.0, 950, 270, 280, '3%', RED, 1.25, face_px=380, eye_y=230)], 'halloween_thumb_a.jpg')
three([P('ss_eone_trailer', 3.5, 1350, 500, 700, '50%', GREEN, 1.15, face_px=470, eye_y=250, blurfill=(140, 940)), P('trt_wbuk_sam_hd', 100, 740, 340, 560, '40%', YEL, 1.6, face_px=380, eye_y=210),
       P('t2_sienna_hd', 186.5, 640, 600, 470, '3%', RED, 1.25)], 'halloween_thumb_b.jpg')
three([P('h3_skull_hd', 120, 1080, 460, 430, '60%', GREEN, 1.5), P('hf_maze_hd', 28.0, 690, 400, 300, '45%', YEL, 2.6, face_px=400, eye_y=250),
       P('t1_meet_hd', 223.0, 600, 470, 560, '6%', RED, 1.1)], 'halloween_thumb_c.jpg')
