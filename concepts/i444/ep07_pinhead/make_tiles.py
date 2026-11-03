# EP07 Pinhead: 400x400 tiles (stat card) from HD frames of the clips (clip, time, centre x, centre y, square size in 1920x1080)
import subprocess, os, io
from PIL import Image, ImageEnhance
C = 'E:/YTP2/Horror Ranked/EP07 Pinhead/1_work/clips/'; D = os.path.dirname(os.path.abspath(__file__)) + '/tiles/'
T = {'hr1': ('hr1_pack4k', 47.0, 960, 420, 640), 'hr2': ('hr2_legendary', 91.0, 960, 480, 760), 'hr3': ('hr3_pillar', 231.0, 960, 470, 700),
     'hr4': ('hr4_pathway', 154.0, 960, 470, 700), 'hr5': ('hr5_box', 267.0, 960, 450, 760), 'hr6': ('hr6_painpleasure', 187.5, 960, 470, 700),
     'hr7': ('hr7_returns', 191.0, 960, 450, 760), 'hr8': ('hr8_jake', 111.0, 960, 450, 700), 'hr9': ('hr9_rev_g', 2.0, 960, 420, 760),
     'hr10': ('hr10_hell4k', 371.0, 960, 450, 700), 'hr22': ('hr22_bridge', 25.0, 960, 450, 640)}
GAIN = {'hr6': 1.4, 'hr7': 1.2, 'hr8': 1.3, 'hr10': 1.3, 'hr22': 1.5, 'hr2': 1.2}
for k, (c, t, x, y, s) in T.items():
    png = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', C + c + '.mp4', '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'])
    im = Image.open(io.BytesIO(png)).convert('RGB')
    if im.size != (1920, 1080): im = im.resize((1920, 1080), Image.LANCZOS)
    h = s // 2; x = min(max(x, h), 1920 - h); y = min(max(y, h), 1080 - h)
    im = im.crop((x - h, y - h, x + h, y + h)).resize((400, 400), Image.LANCZOS)
    if k in GAIN: im = ImageEnhance.Brightness(im).enhance(GAIN[k])
    im.save(D + k + '.png'); print(k)
