# quick face tiles for the comparison mockups: square crops around hand-placed face centres (1280x720 face stills)
import sys
from PIL import Image, ImageDraw, ImageEnhance, ImageOps
EP = '/home/user/YTP1/concepts/i444/ep03/faces/'; OUT = sys.argv[1]
C = {'carvey': (.45, .43, .50), 'marco': (.51, .51, .40), 'mrs_loomis': (.525, .42, .42), 'charlie': (.60, .42, .53),
     'quinn': (.49, .42, .58), 'ethan': (.64, .47, .44), 'richie': (.66, .41, .40), 'jessica': (.37, .47, .42),
     'stu': (.265, .43, .42), 'mickey': (.295, .49, .42), 'amber': (.56, .45, .48), 'billy': (.63, .44, .42),
     'wayne': (.40, .42, .42), 'jill': (.31, .43, .42), 'roman': (.54, .43, .42), 'karl': (.56, .42, .74)}   # karl.jpg = Scream Wiki coffee-shop still (691x763): wider crop
for k, (fx, fy, fs) in C.items():
    im = Image.open(EP + k + '.jpg').convert('RGB'); W, H = im.size; x, y, s = int(fx * W), int(fy * H), int(fs * H)
    x = min(max(x, s // 2), W - s // 2)
    t = im.crop((x - s // 2, y - s // 2, x + s // 2, y + s // 2)).resize((400, 400), Image.LANCZOS)
    t = ImageEnhance.Brightness(ImageEnhance.Contrast(t).enhance(1.1)).enhance(1.12)
    t.save(f'{OUT}/{k}.png')
