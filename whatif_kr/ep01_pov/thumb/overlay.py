# Thumbnail text in the reference layout: left dark fade, spaced label, huge serif number, italic place line.
# python3 overlay.py <render.png> <out.jpg> [label] [big] [sub] [place]
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = "/home/user/YTP1/germany_shorts/fonts/"
src, out = sys.argv[1], sys.argv[2]
label = sys.argv[3] if len(sys.argv) > 3 else "지 진  규 모"
big = sys.argv[4] if len(sys.argv) > 4 else "M 9.5"
sub = sys.argv[5] if len(sys.argv) > 5 else "단  한  걸 음 에"
place = sys.argv[6] if len(sys.argv) > 6 else "서울, 2026."
W, H = 1280, 720
im = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS)
# left fade like the reference
fade = Image.new("L", (W, H), 0); d = ImageDraw.Draw(fade)
for x in range(W):
    a = max(0.0, 1 - x / 640) ** 1.6 * 190
    d.line([(x, 0), (x, H)], fill=int(a))
dark = Image.new("RGB", (W, H), (22, 28, 36))
im = Image.composite(dark, im, fade)
d = ImageDraw.Draw(im)
def text(xy, s, font, fill=(245, 245, 242), spacing=0):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.text((xy[0] + 2, xy[1] + 3), s, font=font, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(4)); im.paste(sh, (0, 0), sh)
    ImageDraw.Draw(im).text(xy, s, font=font, fill=fill)
lab = ImageFont.truetype(F + "Pretendard-SemiBold.otf", 30)
num = ImageFont.truetype(F + "NotoSerifKR-SemiBold.ttf", 150)
pl = ImageFont.truetype(F + "NotoSerifKR-SemiBold.ttf", 46)
text((76, 178), label, lab)
text((66, 222), big, num)
text((76, 430), sub, lab)
text((74, 600), place, pl)
im.save(out, quality=94)
print("saved", out)
