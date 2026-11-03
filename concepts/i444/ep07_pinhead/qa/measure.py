# gridded crop around a face in source pixels: python qa/measure.py out.jpg src x0 y0 x1 y1 [step]   (src = TMDB file name or clip@t)
import sys, os, io, subprocess
from PIL import Image, ImageDraw, ImageFont
out, src = sys.argv[1], sys.argv[2]; x0, y0, x1, y1 = map(int, sys.argv[3:7]); st = int(sys.argv[7]) if len(sys.argv) > 7 else 50
POSTERS = 'C:/Users/hw549/AppData/Local/Temp/claude/C--Users-hw549-Downloads-YTP1/13ed4b5d-5f22-4c14-8e5f-413f537955db/scratchpad/tmdb_ph'
CLIPS = 'E:/YTP2/Horror Ranked/EP07 Pinhead/1_work/clips'
if '@' in src:
    c, t = src.split('@'); png = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', t, '-i', os.path.join(CLIPS, c + '.mp4'), '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'])
    im = Image.open(io.BytesIO(png)).convert('RGB'); im = im.resize((1920, 1080), Image.LANCZOS)   # same 1920x1080 coordinates as thumbs.py
else: im = Image.open(os.path.join(POSTERS, src)).convert('RGB')
c = im.crop((x0, y0, x1, y1)); k = 900 / max(c.size); c = c.resize((int(c.width * k), int(c.height * k))); d = ImageDraw.Draw(c); fn = ImageFont.truetype('arial.ttf', 16)
for x in range((x0 // st + 1) * st, x1, st): X = (x - x0) * k; d.line([(X, 0), (X, c.height)], fill=(255, 255, 0) if x % (st * 2) == 0 else (110, 110, 0)); d.text((X + 2, 2), str(x), font=fn, fill='yellow')
for y in range((y0 // st + 1) * st, y1, st): Y = (y - y0) * k; d.line([(0, Y), (c.width, Y)], fill=(0, 255, 255) if y % (st * 2) == 0 else (0, 110, 110)); d.text((2, Y + 2), str(y), font=fn, fill='cyan')
c.save(out, quality=85)
