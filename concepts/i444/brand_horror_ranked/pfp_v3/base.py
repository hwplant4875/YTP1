# shared helpers for the Horror Ranked pfp v3 concepts (all built on the TierMaker tier colours used in the episodes)
# usage inside a concept script:  import sys; sys.path.insert(0, '<this dir>'); from base import *
import os, subprocess
from PIL import Image, ImageDraw
BASE = os.path.dirname(os.path.abspath(__file__))
TM = ['#FF7F7F', '#FFBF7F', '#FFDF7F', '#FFFF7F', '#BFFF7F', '#7FFF7F']   # Slaughtered, Almost Dead, Better Run, Close Call, Don't Worry, Easy
INK = '#18181A'; BOARD = '#1A1A17'; PAGE = '#0A0A0A'; CREAM = '#F1ECE2'; BLOOD = '#C8101C'

def svg(body, defs=''):
    """a 1000x1000 SVG; YouTube crops the pfp to the inscribed circle, so keep anything important within ~440 px of (500,500)"""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><defs>{defs}</defs>{body}</svg>'

def bands(n=6, x=0, y=0, w=1000, h=1000, cols=None):
    cols = cols or TM[:n]
    return ''.join(f'<rect x="{x}" y="{y + i * h / len(cols):.2f}" width="{w}" height="{h / len(cols) + 1:.2f}" fill="{c}"/>' for i, c in enumerate(cols))

def render(svg_text, out_stem):
    """writes out_stem.svg, out_stem_1600.png, out_stem.png (800 px) and out_stem_check.png (circle crops 176/88/48/32/24 on dark + light)"""
    open(out_stem + '.svg', 'w').write(svg_text)
    env = dict(os.environ); env['NODE_PATH'] = subprocess.check_output(['npm', 'root', '-g'], text=True).strip()
    subprocess.run(['node', BASE + '/render.js', out_stem + '.svg', out_stem + '_1600.png', '1600'], check=True, env=env)
    im = Image.open(out_stem + '_1600.png').convert('RGBA')
    im.convert('RGB').resize((800, 800), Image.LANCZOS).save(out_stem + '.png')
    check(im, out_stem + '_check.png')

def circ(im, n):
    big = im.resize((n * 4, n * 4), Image.LANCZOS); m = Image.new('L', big.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, n * 4 - 1, n * 4 - 1], fill=255)
    out = Image.new('RGBA', big.size); out.paste(big, (0, 0), m); return out.resize((n, n), Image.LANCZOS)

def check(im, path):
    SZ = [176, 88, 48, 32, 24]; W = sum(SZ) + 40 * (len(SZ) + 1); sh = Image.new('RGB', (W, 440))
    d = ImageDraw.Draw(sh)
    for half, bg in ((0, (15, 15, 15)), (1, (255, 255, 255))):
        d.rectangle([0, half * 220, W, half * 220 + 220], fill=bg); x = 40
        for n in SZ:
            c = circ(im, n); sh.paste(c, (x, half * 220 + (220 - n) // 2), c); x += n + 40
    sh.save(path)
