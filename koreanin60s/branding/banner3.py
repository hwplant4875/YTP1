"""Banner v3: channel name + a crowd of 뱁새 stickers, no tagline. Mobile safe area (1546x423 at 507,508) also holds stickers.
Usage: python3 banner3.py <outdir>; node shot.js <outdir>/banner3.html 2560 1440 <png>"""
import base64, os, sys
STK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "baepsae")
img = lambda n: "data:image/png;base64," + base64.b64encode(open(f"{STK}/{n}.png", "rb").read()).decode()
# (sticker, x, y, width, rotation): first block sits inside the mobile safe area, rest fills the desktop frame
S = [("hi_wave", 525, 585, 285, -6), ("iced_coffee", 1755, 580, 285, 6),
     ("flap", 1150, 300, 220, 4), 
     ("sing_mic", 40, 60, 300, -8), ("headphones", 400, 120, 270, 6), ("ramen", 760, 40, 260, -4), ("love_heart", 1090, 90, 250, 8),
     ("excited", 1400, 50, 270, -6), ("camera", 1730, 110, 260, 5), ("trophy", 2060, 40, 260, -7), ("umbrella", 2300, 230, 240, 8),
     ("o_x_quiz", 60, 430, 320, 4), ("reading", 90, 830, 300, -5), ("suitcase", 2230, 500, 300, -4), ("idea", 2210, 870, 290, 6),
     ("laugh_tears", 30, 1150, 260, 7), ("phone", 360, 1020, 270, -6), ("rice_bowl", 700, 1110, 260, 5), ("sleeping", 1000, 1000, 330, 0),
     ("dash", 1380, 1110, 270, -5), ("pay_card", 1700, 1060, 260, 6), ("shy_cover", 2000, 1150, 250, -6), ("teacher", 2300, 1140, 240, 4)]
sd = "".join(f'<img src="{img(n)}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;transform:rotate({r}deg);filter:drop-shadow(0 14px 16px rgba(120,90,80,.22))">' for n, x, y, w, r in S)
html = f'''<html><head><meta charset="utf-8"><style>body{{margin:0;width:2560px;height:1440px;overflow:hidden;position:relative;
background:radial-gradient(ellipse at 20% 20%,#FCE1E6 0,transparent 50%),radial-gradient(ellipse at 85% 85%,#E3F2EC 0,transparent 50%),#FBF4EA}}
h1{{position:absolute;left:0;right:0;top:645px;margin:0;text-align:center;font-family:'YouTube Sans',Pretendard;font-weight:900;font-size:150px;letter-spacing:-3px;line-height:1;color:#3A3134;
text-shadow:0 0 30px #FBF4EA,0 0 60px #FBF4EA}}
h1 span{{color:#E8678A}}
</style></head><body>{sd}<h1>Korean in <span>60s</span></h1></body></html>'''
open(f"{sys.argv[1]}/banner3.html", "w").write(html)
