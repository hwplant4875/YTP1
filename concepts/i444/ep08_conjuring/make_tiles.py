# EP08 Conjuring (copy of ../ep04/make_tiles_fk.py): one 400x400 tile per entry for the stat card, cut from an HD frame of a clip:
# (clip, time, centre x, centre y, square size) in 1920x1080 frame pixels. The tiles are film frames, so they are written next to the
# clips (<clips>/../tiles/<key>.png, where render_cj.py looks for them) and never committed.
# usage: set CLIPS=<EP08 clips folder>; python make_tiles.py      (fill T from verified frames first: the demon's face, bright, centred)
import subprocess, os, io
from PIL import Image, ImageEnhance
C = os.environ.get('CLIPS', 'E:/YTP2/Horror Ranked/EP08 Conjuring/1_work/clips').rstrip('/\\') + '/'
D = os.path.join(C, '..', 'tiles') + '/'; os.makedirs(D, exist_ok=True)
TODO = None
T = {  # key: the entry's demon, as the stat card names it
     'ach': TODO,   # s02 Annabelle (Annabelle Comes Home): the doll in its glass case, face front
     'a14': TODO,   # s03 the Annabelle demon (Annabelle 2014): the horned demon or the doll's face
     'c1': TODO,    # s04 Bathsheba (The Conjuring): Bathsheba's face (the wardrobe / possessed-Carolyn shots)
     'c2': TODO,    # s05 Valak (The Conjuring 2): the nun in the hallway or the painting
     'lr': TODO,    # s06 the mirror demon (Last Rites): the demon in the mirror
     'cr': TODO,    # s07 the Annabelle demon (Creation): possessed Janice or the doll in the closet
     'dm': TODO,    # s08 the Occultist's demon (The Devil Made Me Do It): the demon (or Isla at her altar)
     'n2': TODO,    # s09 Valak (The Nun II): Valak's face
     'n1': TODO}    # s10 Valak (The Nun): Valak's face, eyes lit
GAIN = {}   # brighten a dark face: {'c1': 1.25}
for k, v in T.items():
    if v is None: print('TODO', k); continue
    c, t, x, y, s = v
    png = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', C + c + '.mp4', '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'])
    im = Image.open(io.BytesIO(png)).convert('RGB')
    if im.size != (1920, 1080): im = im.resize((1920, 1080), Image.LANCZOS)
    h = s // 2; x = min(max(x, h), 1920 - h); y = min(max(y, h), 1080 - h)
    im = im.crop((x - h, y - h, x + h, y + h)).resize((400, 400), Image.LANCZOS)
    if k in GAIN: im = ImageEnhance.Brightness(im).enhance(GAIN[k])
    im.save(D + k + '.png'); print(k, D + k + '.png')
