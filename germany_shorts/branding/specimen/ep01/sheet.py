import sys,glob
from PIL import Image
fs=sys.argv[2:]; out=sys.argv[1]; n=len(fs); cols=3; rows=(n+cols-1)//cols
s=Image.new('RGB',(cols*640,rows*360),'#222')
for i,f in enumerate(fs): s.paste(Image.open(f).resize((640,360)),((i%cols)*640,(i//cols)*360))
s.save(out,quality=85)
