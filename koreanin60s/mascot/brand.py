from bird import bird
def big(svg,w,h): return svg.replace('width="600" height="640"',f'width="{w}" height="{h}"')
prof=f'''<html><head><meta charset="utf-8"><style>body{{margin:0;width:800px;height:800px;overflow:hidden;background:radial-gradient(circle at 50% 38%,#FFC2D4 0,#FF8FB1 55%,#FF5F8F 100%);position:relative;font-family:Fredoka,Pretendard}}
.b{{position:absolute;left:50px;top:70px}}
.badge{{position:absolute;right:86px;top:96px;background:#FFD23F;color:#1C1718;font-weight:900;font-family:Pretendard;font-size:62px;padding:8px 22px;border-radius:40px;transform:rotate(12deg);box-shadow:0 8px 0 #E0A800}}
.ring{{position:absolute;inset:0;border-radius:50%;}}
</style></head><body><div class="b">{big(bird("default","p"),700,747)}</div><div class="badge">60s</div></body></html>'''
open("profile.html","w").write(prof)
letters=[("한",120,140,160,"#FF9DB0",-12),("ㄱ",420,1160,140,"#3DD6B5",10),("글",2300,180,170,"#7B6CFF",14),("ㅎ",2150,1180,150,"#FFD23F",-8),("♥",640,240,90,"#FF4F81",-15),("안녕",1850,300,110,"#3DD6B5",6),("ㅋㅋ",300,1250,120,"#7B6CFF",-6),("대박",2280,960,120,"#FF4F81",8),("ㄴ",1500,1250,130,"#FF9DB0",12),("★",1150,200,80,"#FFD23F",0)]
lt="".join(f'<div class="lt" style="left:{x}px;top:{y}px;font-size:{s}px;color:{c};transform:rotate({r}deg)">{t}</div>' for t,x,y,s,c,r in letters)
ban=f'''<html><head><meta charset="utf-8"><style>body{{margin:0;width:2560px;height:1440px;overflow:hidden;background:linear-gradient(120deg,#FFF4E6 0%,#FFE6EE 50%,#E4F8F1 100%);position:relative;font-family:Pretendard}}
.lt{{position:absolute;font-family:Jua;opacity:.55}}
.safe{{position:absolute;left:507px;top:508px;width:1546px;height:423px;display:flex;align-items:center}}
.b{{width:400px;height:426px;margin-left:40px;flex:none}}
.t{{margin-left:50px}}
h1{{margin:0;font-weight:900;font-size:150px;letter-spacing:-5px;line-height:1;color:#1C1718}}
h1 span{{color:#FF4F81}}
p{{margin:22px 0 0;font-size:46px;font-weight:700;color:#5a4c49;letter-spacing:-.5px}}
.pills{{display:flex;gap:16px;margin-top:26px}}
.pill{{font-size:30px;font-weight:800;padding:10px 26px;border-radius:40px;color:#fff}}
</style></head><body>{lt}
<div class="safe"><div class="b">{big(bird("happy","bn"),400,426)}</div>
<div class="t"><h1>Korean in <span>60s</span></h1><p>Real Korean, explained fast. No boring lectures.</p>
<div class="pills"><div class="pill" style="background:#FF4F81">K-Pop Korean</div><div class="pill" style="background:#3DD6B5">Slang &amp; Culture</div><div class="pill" style="background:#7B6CFF">Why is Korean like this?!</div></div></div></div>
</body></html>'''
open("banner.html","w").write(ban)
