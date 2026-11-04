# EP07 Pinhead thumbnails (horror-ranked-thumbnail skill) (upload_kit_v1.md): EP03 C layout = 1280x720, three panels 427/426/427 with thin black gutters,
# f(182) % at the bottom of each panel in its tier colour, the face bigger as the survival rate falls; C = Art alone with a huge 3%.
# Sources are HD frames of the official clips in E:\YTP2\Horror Ranked\EP07 Pinhead\1_work\clips (never committed).
# usage: python thumbs.py [clips_dir] [out_dir]
import os, sys, io, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ep01'))
from gfx import f, shadow_text
CLIPS = sys.argv[1] if len(sys.argv) > 1 else 'E:/YTP2/Horror Ranked/EP07 Pinhead/1_work/clips'
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'upload')
W, H = 1280, 720; PW = [427, 426, 427]
GREEN = (70, 215, 95, 255); YEL = (250, 200, 40, 255); RED = (235, 30, 38, 255); ORANGE = (255, 130, 20, 255)
POSTERS = sys.argv[3] if len(sys.argv) > 3 else 'C:/Users/hw549/AppData/Local/Temp/claude/C--Users-hw549-Downloads-YTP1/13ed4b5d-5f22-4c14-8e5f-413f537955db/scratchpad/tmdb_ph'
def frame(clip, t):
    """a clip frame (1920x1080) or, for clip='poster:<file>', an official poster/still from TMDB at its own size (never committed)"""
    if clip.startswith('poster:'): return Image.open(os.path.join(POSTERS, clip[7:])).convert('RGB')
    nat = clip.startswith('native:'); clip = clip.replace('native:', '')       # native: keep the clip's own resolution (4K packs)
    png = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', os.path.join(CLIPS, clip + '.mp4'), '-frames:v', '1',
                                   '-f', 'image2pipe', '-vcodec', 'png', '-'])
    im = Image.open(io.BytesIO(png)).convert('RGB')
    return im if nat or im.size == (1920, 1080) else im.resize((1920, 1080), Image.LANCZOS)   # 1440p sources -> 1920x1080 coordinates
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
    else:                                                 # shared face scale; wherever the scaled source ends, a blurred copy extends the frame
        k = max(H / im.height, pw / im.width) * 1.6; bg = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
        bg = ImageEnhance.Brightness(bg).enhance(0.8); sp = dict(sp, pad=(bg, k))
    big = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    cx, cy = sp['cx'] * s, sp['cy'] * s
    if sp.get('pad'):                                     # face exactly centred on the panel, eyes on the shared eye line
        bg, k = sp['pad']; ox, oy = pw / 2 - cx, sp['eye_y'] - cy
        p = bg.crop((int(sp['cx'] * k - pw / 2), int(sp['cy'] * k - sp['eye_y'])) + (int(sp['cx'] * k + pw / 2), int(sp['cy'] * k - sp['eye_y']) + H)).convert('RGBA')
        m = Image.new('L', big.size, 0); ImageDraw.Draw(m).rectangle([30, 30, big.width - 30, big.height - 30], fill=255); m = m.filter(ImageFilter.GaussianBlur(18))
        if ox > 0 or oy > 0 or ox + big.width < pw or oy + big.height < H - 100: print(   # up to 100 px short at the bottom is inside the black number shadow
            '  WARN source does not fill the panel', sp['clip'], int(ox), int(oy), big.size)
        p.paste(big, (int(ox), int(oy)), m)
    else:
        x0 = int(min(max(cx - pw / 2, 0), big.width - pw)); y0 = int(min(max(cy - sp.get('eye_y', 250), 0), big.height - H))
        if (x0, y0) != (int(cx - pw / 2), int(cy - sp.get('eye_y', 250))): print('  WARN face not centred', sp['clip'], (x0, y0), (int(cx - pw / 2), int(cy - sp.get('eye_y', 250))))
        p = big.crop((x0, y0, x0 + pw, y0 + H)).convert('RGBA')
    if sp.get('blurfill'):
        top = int(sp['blurfill'][0] * s) - y0; bot = int(sp['blurfill'][1] * s) - y0
        canvas = bg.convert('RGBA'); canvas.alpha_composite(p.crop((0, max(top, 0), pw, min(bot, H))), (0, max(top, 0))); p = canvas
    v = np.linspace(0, 1, H)[:, None]; a = (np.clip((v - 0.5) / 0.32, 0, 1) ** 1.2 * 235).astype(np.uint8)   # dark bottom under the % (owner 10/31: strong shadow)
    p.alpha_composite(Image.merge('RGBA', [Image.new('L', (pw, H), 0)] * 3 + [Image.fromarray(np.repeat(a, pw, 1), 'L')]))
    return p
def three(specs, name):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); x = 0
    for sp, pw in zip(specs, PW): im.alpha_composite(panel(sp, pw), (x, 0)); x += pw
    d = ImageDraw.Draw(im); x = 0
    for k in (1, 2): gx = sum(PW[:k]); d.rectangle([gx - 3, 0, gx + 3, H], fill=(0, 0, 0, 255))
    for sp, pw in zip(specs, PW): shadow_text(im, (x + pw // 2, H - 205), sp['pct'], f(182), sp['col'], stroke=8); x += pw
    im.convert('RGB').save(os.path.join(OUT, name), quality=92); print(name)
# owner 10/31 13:48 (standing rule): left GREEN %, middle YELLOW %, right RED %; the three variants must look very different;
# zoomed in, the face fills most of the panel with the eyes in the upper third, % below the face. Coordinates = 1920x1080 frame.
def P(clip, t, cx, cy, face_h, pct, col, bright=1.15, face_px=430, eye_y=300, blurfill=None): return dict(clip=clip, t=t, cx=cx, cy=cy, face_h=face_h, pct=pct, col=col, bright=bright, face_px=face_px, eye_y=eye_y, blurfill=blurfill)
os.makedirs(OUT, exist_ok=True)
# owner 11/04: every face centred (nose on the panel centre) and the same size with the eyes on one line in all panels:
# (cx, cy) = nose x / eye line, face_h = eye-to-mouth distance in source px -> FACE px in the output, eyes at EYE.
# No source image twice in a thumbnail or across A/B/C (the 1987 / Hell on Earth skyline face is one photo).
FACE, EYE = 135, 215
def F(clip, t, cx, cy, em, pct, col, bright=1.15): return P(clip, t, cx, cy, em, pct, col, bright, face_px=FACE, eye_y=EYE)
# v6b (owner 11/04 21:43 KST numbers): each film once across A/B/C; green >= 50, yellow 25-45, red <= 20
three([F('poster:o_lnCm_notitle.jpg', 0, 506, 633, 289, '70%', GREEN, 1.05),                   # Revelations #10, official poster art (title faded)
       F('hr6_pain', 205.0, 925, 410, 280, '45%', YEL, 1.6),                                # Hellseeker #8 (Miramax HD clip)
       F('poster:o_qW4hr2WweKiyztgd4Ql0wlfRYBF.jpg', 0, 2403, 458, 275, '10%', RED, 1.2)], 'pinhead_thumb_a.jpg')    # Judgment #3
three([F('native:hr1_pack4k', 44.0, 1240, 425, 230, '55%', GREEN, 1.05),                   # Hellraiser 1987 #9, hospital blinds (4K)
       F('hr22_bridge', 25.0, 807, 434, 191, '35%', YEL, 1.9),                              # the Priest, 2022 #7
       F('poster:o_yyiu_notitle.jpg', 0, 430, 639, 228, '8%', RED, 1.1)], 'pinhead_thumb_b.jpg')    # Inferno #2, official poster art (title faded)
three([F('poster:o_pl5OzUABUK5AgAsMlQg2VyybRHL.jpg', 0, 1719, 485, 188, '85%', GREEN, 0.95),   # Hellbound #11
       F('poster:o_udZ3XqsurnNuGp1QfS5CLod6MS5.jpg', 0, 1000, 450, 283, '25%', YEL, 0.95),   # Bloodline #6, official poster art
       F('poster:o_xjeoa7KjnUMQzJXGunHmgMjhHmP.jpg', 0, 2556, 802, 405, '5%', RED, 1.05)], 'pinhead_thumb_c.jpg')   # Hell on Earth #1, skyline       # Hell on Earth, Boiler Room chains
