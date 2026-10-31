# Clowns episode: 400x400 villain tiles (stat card) from HD frames of the official clips (clip, time, centre x, centre y, square size in 1920x1080)
import subprocess, os, io
from PIL import Image, ImageEnhance
C = 'E:/YTP2/Horror Ranked/EP06 Clowns/1_work/clips/'; D = os.path.dirname(os.path.abspath(__file__)) + '/tiles/'
T = {'zl': ('zl_clown_cc', 26.0, 920, 470, 600), 'pg': ('pg15_trailer', 108.0, 1020, 470, 330), 'spaulding': ('dr_send_clown', 26.0, 660, 470, 880),
     'klown': ('kk_puppet', 78.5, 940, 520, 1000), 'frendo': ('cc_bench', 110.0, 960, 480, 560), 'pw90': ('it90_clipzone', 196.0, 840, 500, 720),
     'pw17': ('it17_wbuk', 1068.0, 960, 450, 640), 'pw19': ('it2_wb', 82.0, 960, 450, 520), 'art1': ('t1_meet_hd', 223.0, 600, 470, 640),
     'art2': ('t2_cafe_hd', 261.0, 1140, 560, 640)}
GAIN = {'pg': 1.5, 'frendo': 1.6, 'pw17': 1.1}
for k, (c, t, x, y, s) in T.items():
    png = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', C + c + '.mp4', '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'])
    im = Image.open(io.BytesIO(png)).convert('RGB')
    if im.size != (1920, 1080): im = im.resize((1920, 1080), Image.LANCZOS)
    h = s // 2; x = min(max(x, h), 1920 - h); y = min(max(y, h), 1080 - h)
    im = im.crop((x - h, y - h, x + h, y + h)).resize((400, 400), Image.LANCZOS)
    if k in GAIN: im = ImageEnhance.Brightness(im).enhance(GAIN[k])
    im.save(D + k + '.png'); print(k)
