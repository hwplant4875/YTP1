# EP04 Freddy (copy of EP07 make_tiles.py): 400x400 tiles (stat card) from HD frames of the clips (clip, time, centre x, centre y, square size in 1920x1080)
import subprocess, os, io
from PIL import Image, ImageEnhance
C = 'E:/YTP2/Horror Ranked/EP04 Freddy Krueger/1_work/clips/'; D = os.path.dirname(os.path.abspath(__file__)) + '/tiles/'
T = {  # EP04: one 400x400 Freddy face per film for the stat card; fill (clip, time, centre x, centre y, square size) from verified frames
     'n1': ('n1_tina_chase', 59.00, 910, 440, 500), 'n2': ('n2_pool', 329.50, 690, 530, 1060), 'n3': ('n3_joey', 4.20, 720, 290, 500),
     'n4': ('n4_nurse', 47.00, 1250, 560, 860), 'n5': ('n5_tricks', 51.2, 1185, 585, 600), 'n6': ('n6_forever', 70.00, 760, 420, 760),
     'n7': ('n7_julie', 36.60, 780, 430, 400), 'fj': ('fj_construction', 87.10, 1040, 580, 900), 'r10': ('r10_creepiest', 1412.90, 1100, 520, 1040)}
GAIN = {'n1': 1.25, 'n2': 1.15}   # the 1984 alley face is blue night light, the n2 pool face a little dim
for k, (c, t, x, y, s) in T.items():
    png = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', C + c + '.mp4', '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'])
    im = Image.open(io.BytesIO(png)).convert('RGB')
    if im.size != (1920, 1080): im = im.resize((1920, 1080), Image.LANCZOS)
    h = s // 2; x = min(max(x, h), 1920 - h); y = min(max(y, h), 1080 - h)
    im = im.crop((x - h, y - h, x + h, y + h)).resize((400, 400), Image.LANCZOS)
    if k in GAIN: im = ImageEnhance.Brightness(im).enhance(GAIN[k])
    im.save(D + k + '.png'); print(k)
