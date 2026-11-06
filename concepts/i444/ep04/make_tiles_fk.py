# EP04 Freddy (copy of EP07 make_tiles.py): 400x400 tiles (stat card) from HD frames of the clips (clip, time, centre x, centre y, square size in 1920x1080)
import subprocess, os, io
from PIL import Image, ImageEnhance
C = 'E:/YTP2/Horror Ranked/EP04 Freddy Krueger/1_work/clips/'; D = os.path.dirname(os.path.abspath(__file__)) + '/tiles/'
T = {  # EP04: one 400x400 Freddy face per film for the stat card; fill (clip, time, centre x, centre y, square size) from verified frames
     'n1': None, 'n2': None, 'n3': None, 'n4': None, 'n5': None, 'n6': None, 'n7': None, 'fj': None, 'r10': None}
GAIN = {}
for k, (c, t, x, y, s) in T.items():
    png = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', C + c + '.mp4', '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'])
    im = Image.open(io.BytesIO(png)).convert('RGB')
    if im.size != (1920, 1080): im = im.resize((1920, 1080), Image.LANCZOS)
    h = s // 2; x = min(max(x, h), 1920 - h); y = min(max(y, h), 1080 - h)
    im = im.crop((x - h, y - h, x + h, y + h)).resize((400, 400), Image.LANCZOS)
    if k in GAIN: im = ImageEnhance.Brightness(im).enhance(GAIN[k])
    im.save(D + k + '.png'); print(k)
