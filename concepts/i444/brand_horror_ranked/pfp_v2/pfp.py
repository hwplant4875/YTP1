# Horror Ranked profile picture v2 (user 10/26: carefully made, brand-logo-like, readable even when tiny).
# A crowned skull = "the #1 of horror": flat vector shapes (SVG) so it stays crisp from 800 px down to a 24 px comment avatar.
# Options: A black + red crown, A2 red + black crown, B black skull over the TierMaker tier colours (ties to the episodes' tier list).
# run: NODE_PATH=$(npm root -g) python3 pfp.py   -> <name>.svg, <name>.png (800 px for YouTube), <name>_1600.png, preview.jpg
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)) + '/'
BG, CREAM, RED = '#0B0B0D', '#F1ECE2', '#D0141E'
TM = ['#FF7F7F', '#FFBF7F', '#FFDF7F', '#FFFF7F', '#BFFF7F', '#7FFF7F']   # TierMaker row colours, as in the episodes

def skull_parts():
    """silhouette and holes (angry eye sockets, nose, cheek notches, teeth) of a flat skull, about x 236..764, y 184..790"""
    sil = '<ellipse cx="500" cy="430" rx="264" ry="246"/><rect x="338" y="540" width="324" height="250" rx="66"/>'
    holes = ('<path d="M332 446 L456 494 L447 590 L350 590 Z" stroke-linejoin="round" stroke-width="32"/>'
             '<path d="M668 446 L544 494 L553 590 L650 590 Z" stroke-linejoin="round" stroke-width="32"/>'
             '<path d="M500 622 L466 682 L534 682 Z" stroke-linejoin="round" stroke-width="22"/>'
             '<path d="M318 650 Q330 676 338 700 L338 650 Z"/><path d="M682 650 Q670 676 662 700 L662 650 Z"/>'
             + ''.join(f'<rect x="{x - 9}" y="712" width="18" height="90" rx="9"/>' for x in (410, 455, 500, 545, 590)))
    return sil, holes

def crown(fill, sep, tilt=-9):
    """three-point crown with balls and three jewels, outlined in the background colour, tilted a little for attitude"""
    p = 'M328 212 L328 150 L358 46 L428 122 L500 14 L572 122 L642 46 L672 150 L672 212 Z'
    balls = ''.join(f'<circle cx="{x}" cy="{y}" r="21"/>' for x, y in ((358, 40), (500, 8), (642, 40)))
    jew = ''.join(f'<circle cx="{x}" cy="181" r="14" fill="{sep}"/>' for x in (414, 500, 586))
    g = f'<g fill="{sep}" stroke="{sep}" stroke-width="34" stroke-linejoin="round"><path d="{p}"/>{balls}</g>'
    g += f'<g fill="{fill}" stroke="{fill}" stroke-width="4" stroke-linejoin="round"><path d="{p}"/>{balls}</g>{jew}'
    return f'<g transform="rotate({tilt} 500 200)">{g}</g>'

def svg(body, defs=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><defs>{defs}</defs>{body}</svg>'

def fit(inner, cy, s):   # centre content whose vertical middle is cy, scaled by s (everything stays inside YouTube's circle crop)
    return f'<g transform="translate(500 500) scale({s}) translate(-500 {-cy})">{inner}</g>'

def crowned_skull(bg=BG, bone=CREAM, crown_c=RED, glow='#3a0408', tilt=-9):
    sil, holes = skull_parts()
    inner = f'<g fill="{bone}">{sil}</g><g fill="{bg}" stroke="{bg}">{holes}</g>' + crown(crown_c, bg, tilt)
    defs = f'<radialGradient id="g" cx="50%" cy="56%" r="58%"><stop offset="0" stop-color="{glow}"/><stop offset="1" stop-color="{bg}"/></radialGradient>'
    return svg('<rect width="1000" height="1000" fill="url(#g)"/>' + fit(inner, 400, 1.08), defs)

def tier_skull():
    sil, holes = skull_parts()
    bands = ''.join(f'<rect x="0" y="{i * 1000 / 6:.1f}" width="1000" height="{1000 / 6 + 1:.1f}" fill="{c}"/>' for i, c in enumerate(TM))
    defs = (f'<mask id="m"><rect width="1000" height="1000" fill="black"/><g fill="white">{sil}</g>'
            f'<g fill="black" stroke="black">{holes}</g></mask>')
    inner = '<rect x="-200" y="-200" width="1400" height="1400" fill="#111113" mask="url(#m)"/>'
    return svg(bands + fit(inner, 488, 1.12), defs)

OPTS = {'A_skull_crown_black': crowned_skull(),
        'A2_skull_crown_red': crowned_skull('#B30F1A', CREAM, '#0B0B0D', '#D4202C'),
        'B_tier_skull': tier_skull()}

def circ(im, n):
    big = im.resize((n * 4, n * 4), Image.LANCZOS); m = Image.new('L', big.size, 0); ImageDraw.Draw(m).ellipse([0, 0, n * 4 - 1, n * 4 - 1], fill=255)
    out = Image.new('RGBA', big.size); out.paste(big, (0, 0), m); return out.resize((n, n), Image.LANCZOS)

def preview(names):
    """each option big, then circle-cropped at YouTube sizes (channel page 176, 88, 48, list 32, comment 24) on dark and light UI"""
    F = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', 22); f2 = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Medium.otf', 16)
    SZ = [176, 88, 48, 32, 24]; W = 1080; RH = 420
    sh = Image.new('RGB', (W, RH * len(names) + 20), (255, 255, 255)); d = ImageDraw.Draw(sh)
    for r, o in enumerate(names):
        im = Image.open(D + o + '_1600.png').convert('RGBA'); y0 = r * RH + 20
        sh.paste(im.resize((360, 360), Image.LANCZOS), (20, y0)); d.text((20, y0 + 366), o.split('_', 1)[0], font=F, fill=(20, 20, 20))
        for half, bg, fg in ((0, (15, 15, 15), (241, 241, 241)), (1, (255, 255, 255), (15, 15, 15))):
            yy = y0 + half * 190; d.rectangle([400, yy, W - 20, yy + 186], fill=bg); x = 420
            for n in SZ:
                c = circ(im, n); sh.paste(c, (x, yy + (186 - n) // 2), c)
                if n == 32: d.text((x + 40, yy + 74), 'Horror Ranked', font=f2, fill=fg); d.text((x + 40, yy + 96), '@horrorranked', font=f2, fill=(150, 150, 150))
                x += n + (150 if n == 32 else 40)
    sh.save(D + 'preview.jpg', quality=90)

if __name__ == '__main__':
    for k, s in OPTS.items():
        open(D + k + '.svg', 'w').write(s)
        subprocess.run(['node', D + 'render.js', D + k + '.svg', D + k + '_1600.png', '1600'], check=True)
        Image.open(D + k + '_1600.png').convert('RGB').resize((800, 800), Image.LANCZOS).save(D + k + '.png')
        print(k)
    preview(list(OPTS))
