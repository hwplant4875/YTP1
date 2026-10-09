"""Profile picture (800x800) and banner (2560x1440) with the 뱁새 stickers. Screenshot with shot.js."""
import base64, os
STK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "baepsae")
img = lambda n: "data:image/png;base64," + base64.b64encode(open(f"{STK}/{n}.png", "rb").read()).decode()
PAPER = '<svg style="position:absolute;inset:0;opacity:.3;mix-blend-mode:multiply" width="100%" height="100%"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="3" seed="4"/><feColorMatrix values="0 0 0 0 .55  0 0 0 0 .45  0 0 0 0 .4  0 0 0 .55 0"/></filter><rect width="100%" height="100%" filter="url(#n)"/></svg>'
prof = f'''<html><head><meta charset="utf-8"><style>body{{margin:0;width:800px;height:800px;overflow:hidden;position:relative;font-family:Pretendard;
background:radial-gradient(circle at 50% 42%,#FFFBF4 0,#FCE6EA 52%,#F6C9D4 100%)}}
.b{{position:absolute;left:115px;top:95px;width:570px;filter:drop-shadow(0 18px 20px rgba(120,90,80,.25))}}
.badge{{position:absolute;left:50%;bottom:150px;margin-left:-105px;background:#F28BA8;color:#fff;font-family:'YouTube Sans',Pretendard;font-weight:700;font-size:70px;padding:4px 26px;border-radius:44px;transform:rotate(-6deg);box-shadow:0 8px 0 #D86E8D;border:6px solid #fff}}
</style></head><body>{PAPER}<img class="b" src="{img("hi_wave")}"><div class="badge">60s</div></body></html>'''
open("profile.html", "w").write(prof)
letters = [("한",120,140,160,"#F28BA8",-12),("ㄱ",420,1160,140,"#5CC4A8",10),("글",2300,180,170,"#A48AEB",14),("ㅎ",2150,1180,150,"#F2C14E",-8),("♥",640,240,90,"#F28BA8",-15),("안녕",1850,300,110,"#5CC4A8",6),("ㅋㅋ",300,1250,120,"#A48AEB",-6),("대박",2280,960,120,"#F28BA8",8),("ㄴ",1500,1250,130,"#7FA9E8",12),("★",1150,200,80,"#F2C14E",0)]
lt = "".join(f'<div class="lt" style="left:{x}px;top:{y}px;font-size:{s}px;color:{c};transform:rotate({r}deg)">{t}</div>' for t, x, y, s, c, r in letters)
side = "".join(f'<img class="sd" src="{img(n)}" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({r}deg)">' for n, x, y, w, r in
               [("iced_coffee",130,420,330,-6),("headphones",2110,430,320,6),("love_heart",260,880,260,4),("o_x_quiz",2040,860,280,-5)])
ban = f'''<html><head><meta charset="utf-8"><style>body{{margin:0;width:2560px;height:1440px;overflow:hidden;position:relative;font-family:Pretendard;
background:radial-gradient(ellipse at 15% 20%,#FCE1E6 0,transparent 45%),radial-gradient(ellipse at 85% 85%,#E3F2EC 0,transparent 45%),#FBF4EA}}
.lt{{position:absolute;font-family:Jua;opacity:.4}}
.sd{{position:absolute;opacity:.95;filter:drop-shadow(0 14px 16px rgba(120,90,80,.2))}}
.safe{{position:absolute;left:507px;top:508px;width:1546px;height:423px;display:flex;align-items:center}}
.b{{width:400px;flex:none;filter:drop-shadow(0 16px 18px rgba(120,90,80,.25))}}
.t{{margin-left:40px}}
h1{{margin:0;font-family:'YouTube Sans',Pretendard;font-weight:900;font-size:160px;letter-spacing:-3px;line-height:1;color:#3A3134}}
h1 span{{color:#E8678A}}
p{{margin:18px 0 0;font-size:46px;font-weight:700;color:#6b5b57;letter-spacing:-.5px}}
.pills{{display:flex;gap:16px;margin-top:24px}}
.pill{{font-size:30px;font-weight:800;padding:10px 26px;border-radius:40px;color:#fff}}
</style></head><body>{PAPER}{lt}{side}
<div class="safe"><img class="b" src="{img("hi_wave")}">
<div class="t"><h1>Korean in <span>60s</span></h1><p>Real Korean, explained fast. No boring lectures.</p>
<div class="pills"><div class="pill" style="background:#F28BA8">K-Pop Korean</div><div class="pill" style="background:#5CC4A8">Slang &amp; Culture</div><div class="pill" style="background:#A48AEB">Why is Korean like this?!</div></div></div></div>
</body></html>'''
open("banner.html", "w").write(ban)
