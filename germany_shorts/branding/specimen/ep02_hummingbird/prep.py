import json, os
from PIL import Image
D='/tmp/claude-0/hb2/photos'; os.makedirs(D+'/web',exist_ok=True); sz={}
for f in sorted(os.listdir(D)):
    if not f.lower().endswith(('.jpg','.jpeg','.png')): continue
    n=os.path.splitext(f)[0]; im=Image.open(os.path.join(D,f)).convert('RGB'); im.thumbnail((1400,1400)); im.save(f'{D}/web/{n}.jpg',quality=88); sz[n]=list(im.size)
json.dump(sz,open(D+'/web/sizes.json','w')); print(sz)
