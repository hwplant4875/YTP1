# quick face tiles for the comparison mockups: square crops around hand-placed face centres (1280x720 face stills)
import sys
from PIL import Image, ImageDraw, ImageEnhance, ImageOps
EP = '/home/user/YTP1/concepts/i444/ep03/faces/'; OUT = sys.argv[1]
C = {'carvey': (.45, .43, .50), 'marco': (.51, .51, .40), 'mrs_loomis': (.525, .42, .42), 'charlie': (.60, .42, .53),
     'quinn': (.49, .42, .58), 'ethan': (.64, .47, .44), 'richie': (.66, .41, .40), 'jessica': (.37, .47, .42),
     'stu': (.265, .43, .42), 'mickey': (.295, .49, .42), 'amber': (.56, .45, .48), 'billy': (.63, .44, .42),
     'wayne': (.40, .42, .42), 'jill': (.31, .43, .42), 'roman': (.54, .43, .42)}
for k, (fx, fy, fs) in C.items():
    im = Image.open(EP + k + '.jpg').convert('RGB'); W, H = im.size; x, y, s = int(fx * W), int(fy * H), int(fs * H)
    t = im.crop((x - s // 2, y - s // 2, x + s // 2, y + s // 2)).resize((400, 400), Image.LANCZOS)
    t = ImageEnhance.Brightness(ImageEnhance.Contrast(t).enhance(1.1)).enhance(1.12)
    t.save(f'{OUT}/{k}.png')
# Karl is never unmasked in our clips: Ghostface mask on black with a red ?
m = Image.open(OUT + '/../mask_icon.png'); h = 330; m = m.resize((m.size[0] * h // m.size[1], h), Image.LANCZOS)
t = Image.new('RGBA', (400, 400), (14, 14, 18, 255)); t.alpha_composite(m, ((400 - m.size[0]) // 2, 40))
d = ImageDraw.Draw(t); from PIL import ImageFont
f = ImageFont.truetype('/home/user/YTP1/concepts/i444/ep01/YouTubeSans-Black.otf', 170)
d.text((300, 300), '?', font=f, fill=(225, 30, 30), anchor='mm', stroke_width=8, stroke_fill=(0, 0, 0))
t.convert('RGB').save(OUT + '/karl.png')
