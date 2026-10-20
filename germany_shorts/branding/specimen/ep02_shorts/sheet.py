import glob,sys
from PIL import Image, ImageDraw
sid=sys.argv[1]; d='/tmp/claude-0/hbs/'+(sys.argv[2] if len(sys.argv)>2 else 'q')
fs=sorted(glob.glob(f'{d}/{sid}_*.png'),key=lambda f:float(f.split('_')[-1][:-4]))
cols=6; rows=(len(fs)+cols-1)//cols
s=Image.new('RGB',(cols*300,rows*560),'white'); dr=ImageDraw.Draw(s)
for i,f in enumerate(fs):
    x,y=(i%cols)*300,(i//cols)*560; s.paste(Image.open(f).convert('RGB').resize((300,533)),(x,y)); dr.text((x+5,y+538),f.split('_')[-1][:-4],fill='black')
s.save(f'{d}/{sid}.jpg',quality=85)
