# grid of candidate HD frames (480x270 each, labelled) for tile/thumbnail crops
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont
C = 'E:/YTP2/Instruction444/clips/halloween/'; L = [a.split('@') for a in sys.argv[2:]]
im = Image.new('RGB', (4 * 480, (len(L) + 3) // 4 * 270)); d = ImageDraw.Draw(im); fnt = ImageFont.truetype('arial.ttf', 22)
for i, (c, t) in enumerate(L):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', t, '-i', C + c + '.mp4', '-frames:v', '1', '-vf', 'scale=480:270', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    x, y = i % 4 * 480, i // 4 * 270; im.paste(Image.frombytes('RGB', (480, 270), raw), (x, y))
    for g in range(1, 8): d.line([(x + g * 60, y), (x + g * 60, y + 270)], fill=(80, 80, 80)); 
    for g in range(1, 5): d.line([(x, y + g * 54), (x + 480, y + g * 54)], fill=(80, 80, 80))
    d.text((x + 4, y + 2), f'{c}@{t}', font=fnt, fill='yellow', stroke_width=2, stroke_fill='black')
im.save(sys.argv[1], quality=85)
