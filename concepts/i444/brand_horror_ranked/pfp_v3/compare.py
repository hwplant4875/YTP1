# comparison sheet for the six pfp v3 concepts: circle crop big, then YouTube sizes (176/88/48/32/24) on dark and light
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); from base import circ
ORDER = [('skull_emoji', '1  Skull'), ('scream_face', '2  Scream'), ('tier_board', '3  Tier board'),
         ('melting_tiers', '4  Melting tiers'), ('tier_eye', '5  Tier eye'), ('tier_slash', '6  Slashed tiers')]
F = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', 30)
f2 = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Medium.otf', 15)
SZ = [176, 88, 48, 32, 24]; RH = 400; W = 1180
sh = Image.new('RGB', (W, RH * len(ORDER) + 20), (245, 245, 245)); d = ImageDraw.Draw(sh)
for r, (k, name) in enumerate(ORDER):
    im = Image.open(f'{HERE}/{k}/{k}.png').convert('RGBA'); y0 = r * RH + 20
    big = circ(im, 330); sh.paste(big, (20, y0 + 10), big); d.text((20, y0 + 346), name, font=F, fill=(20, 20, 20))
    for half, bg, fg in ((0, (15, 15, 15), (241, 241, 241)), (1, (255, 255, 255), (15, 15, 15))):
        yy = y0 + half * 190; d.rectangle([380, yy, W - 20, yy + 186], fill=bg); x = 400
        for n in SZ:
            c = circ(im, n); sh.paste(c, (x, yy + (186 - n) // 2), c)
            if n == 32: d.text((x + 40, yy + 76), 'Horror Ranked', font=f2, fill=fg); d.text((x + 40, yy + 96), '@horrorranked', font=f2, fill=(150, 150, 150))
            x += n + (150 if n == 32 else 40)
sh.save(f'{HERE}/compare.jpg', quality=90); print(sh.size)
