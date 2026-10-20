import sys,re
from PIL import Image
out=sys.argv[1]; fs=sys.argv[2:]
key=lambda f:(re.search(r'_([a-z]\d+b?)_',f).group(1),float(re.search(r'_([\d.]+)\.png$',f).group(1)))
fs=sorted(fs,key=key); cols=4; rows=(len(fs)+cols-1)//cols
s=Image.new('RGB',(cols*480,rows*270),'#222')
for i,f in enumerate(fs): s.paste(Image.open(f).resize((480,270)),((i%cols)*480,(i//cols)*270))
s.save(out,quality=88)
