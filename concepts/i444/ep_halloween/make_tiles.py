# Halloween special: 400x400 villain tiles from HD frames of the official clips (clip, time, centre x, centre y, square size in 1920x1080)
import subprocess, os, io
from PIL import Image, ImageEnhance
C = 'E:/YTP2/Horror Ranked/EP05 Halloween Night/1_work/clips/'; D = os.path.dirname(os.path.abspath(__file__)) + '/tiles/'
T = {'slappy': ('gb2_dummy', 315, 960, 380, 600), 'sweet16': ('tk_machine', 59, 1000, 400, 640), 'sam': ('trt_wbuk_sam', 163.5, 720, 430, 560),
     'other': ('hf_trailer', 75, 980, 420, 560), 'haunt': ('haunt_trailer', 94, 940, 440, 640), 'ginger': ('gs_trailer', 67, 1040, 360, 560),
     'michael': ('h78_best', 402.5, 1140, 420, 380), 'angela': ('notd_trailer', 63, 1060, 560, 600), 'shamrock': ('h3_05_test_room', 70, 1020, 450, 600),
     'harold': ('ss_nc_harold', 11.8, 1000, 420, 620), 'art1': ('t1_trailer', 23, 640, 420, 640), 'art2': ('t2_trailer', 48, 760, 430, 620)}
GAIN = {'sam': 1.5, 'michael': 1.5, 'angela': 1.1, 'other': 1.25, 'haunt': 1.15}
for k, (c, t, x, y, s) in T.items():
    png = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', C + c + '.mp4', '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'])
    im = Image.open(io.BytesIO(png)).convert('RGB'); h = s // 2
    x = min(max(x, h), 1920 - h); y = min(max(y, h), 1080 - h)
    im = im.crop((x - h, y - h, x + h, y + h)).resize((400, 400), Image.LANCZOS)
    if k in GAIN: im = ImageEnhance.Brightness(im).enhance(GAIN[k])
    im.save(D + k + '.png'); print(k)
