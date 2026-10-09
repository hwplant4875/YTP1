from bird import bird
poses=[("default","Hi! 안녕!"),("happy","정답! Correct!"),("surprised","대박?!"),("wrong","땡! Wrong"),("thinking","뭐지? Hmm…")]
bgs=["#FFE3EC","#DDF7EF","#FFF1C9","#E3F0FF","#ECE8FF"]
cards="".join(f'<div class="card" style="background:{bgs[i]}"><div class="b">{bird(p,str(i))}</div><div class="lab">{l}</div></div>' for i,(p,l) in enumerate(poses))
sw="".join(f'<div class="sw"><i style="background:{c}"></i><span>{n}<br><b>{c}</b></span></div>' for n,c in [("Fluff White","#FBF8F6"),("Ink","#1C1718"),("Rosy Flank","#E8B9A6"),("Blush Pink","#FF9DB0"),("Pop Pink","#FF4F81"),("Mint","#3DD6B5"),("Butter","#FFD23F"),("Cream BG","#FFF4E6")])
html=f'''<html><head><meta charset="utf-8"><style>
body{{margin:0;width:2400px;height:1300px;background:#FFF4E6;font-family:Pretendard,Fredoka,sans-serif;color:#1C1718;position:relative;overflow:hidden}}
.bg{{position:absolute;inset:0;background:radial-gradient(circle at 85% 10%,#FFE1EA 0,transparent 35%),radial-gradient(circle at 5% 95%,#D9F7EF 0,transparent 35%)}}
h1{{position:absolute;left:90px;top:60px;margin:0;font-size:76px;font-weight:900;letter-spacing:-2px}}
h1 span{{color:#FF4F81}}
.sub{{position:absolute;left:94px;top:160px;font-size:32px;font-weight:700;color:#7a6a66}}
.row{{position:absolute;left:70px;top:250px;display:flex;gap:28px}}
.card{{width:430px;height:640px;background:#fff;border-radius:44px;box-shadow:0 20px 50px rgba(122,92,85,.15);display:flex;flex-direction:column;align-items:center;justify-content:flex-start}}
.b svg{{width:410px;height:437px;margin-top:40px}}
.lab{{font-family:Jua,Pretendard;font-size:44px;margin-top:30px}}
.pal{{position:absolute;left:90px;top:950px;display:flex;gap:26px}}
.sw{{display:flex;align-items:center;gap:14px;font-size:22px;font-weight:700;color:#5a4c49}} .sw i{{width:64px;height:64px;border-radius:20px;box-shadow:inset 0 0 0 2px rgba(0,0,0,.08)}}
.sw b{{font-weight:600;color:#9a8a86;font-size:18px}}
.notes{{position:absolute;left:90px;top:1050px;font-size:28px;line-height:1.6;font-weight:600;color:#4a3d3a;width:2200px}}
.notes b{{color:#FF4F81}}
</style></head><body><div class="bg"></div>
<h1>Korean in 60s <span>·</span> Mascot “Baepsae 뱁새”</h1>
<div class="sub">흰머리오목눈이 (white-headed long-tailed tit) · 동글동글 솜뭉치 + 긴 검은 꼬리 · 표정 5종</div>
<div class="row">{cards}</div>
<div class="pal">{sw}</div>
<div class="notes">• 실제 흰머리오목눈이 특징 유지: <b>순백 솜털 몸통</b>, 깨알 같은 검은 눈과 부리, <b>검정+로지브라운 날개</b>, 흰 테두리 긴 꼬리, 옆구리의 연분홍 깃털<br>
• 벡터(SVG)로 그려서 확대해도 깨지지 않고, 표정·날개·꼬리를 따로 움직일 수 있어 모션그래픽에 바로 씀 (깜빡임, 통통 튀기, 날개 파닥)<br>
• 쇼츠에서 역할: 정답엔 <b>happy</b>, 반전엔 <b>surprised</b>, 오답엔 <b>wrong</b>, 질문 던질 땐 <b>thinking</b></div>
</body></html>'''
open("sheet.html","w").write(html)
# single big render
open("hero.html","w").write(f'<html><body style="margin:0;background:#FFF4E6;width:1200px;height:1280px;display:flex;align-items:center;justify-content:center">{bird("default","h").replace(chr(39)+"600"+chr(39),"1").replace("width=\"600\" height=\"640\"","width=\"1200\" height=\"1280\"")}</body></html>')
