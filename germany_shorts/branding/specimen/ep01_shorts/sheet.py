import glob,sys
from PIL import Image
sid=sys.argv[1]; d='/tmp/claude-0/shs/'+(sys.argv[2] if len(sys.argv)>2 else 'q')
fs=sorted(glob.glob(f'{d}/{sid}_*.png'),key=lambda f:float(f.split('_')[-1][:-4]))
s=Image.new('RGB',(len(fs)*270,480))
for i,f in enumerate(fs): s.paste(Image.open(f).resize((270,480)),(i*270,0))
s.save(f'{d}/{sid}.jpg')
