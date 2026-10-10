"""Rebrand v2: day (60s shorts) / night (sleep lessons) concept. Profile 800x800 (2 options) + banner 2560x1440.
Usage: python3 brand2.py <outdir>; then shot.js each html."""
import base64, os, sys
OUT = sys.argv[1]
STK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "baepsae")
img = lambda n: "data:image/png;base64," + base64.b64encode(open(f"{STK}/{n}.png", "rb").read()).decode()
NIGHT = "radial-gradient(ellipse at 70% 30%,#454A85 0,transparent 60%),linear-gradient(180deg,#1B1F3B,#2A2E57)"
DAY = "radial-gradient(circle at 30% 30%,#FFFBF4 0,#FCE6EA 60%,#F6C9D4 100%)"
def stars(w, h, n, x0=0, seed=7):
    s, r = "", seed
    for i in range(n):
        r = (r * 9301 + 49297) % 233280; x = x0 + r / 233280 * (w - x0)
        r = (r * 9301 + 49297) % 233280; y = r / 233280 * h
        z = 2 + i % 4
        s += f'<div style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{z}px;height:{z}px;border-radius:50%;background:#FFF6D8;opacity:{.35 + (i % 5) / 8:.2f}"></div>'
    return s
HEAD = '<html><head><meta charset="utf-8"><style>body{margin:0;overflow:hidden;position:relative;font-family:"YouTube Sans",Pretendard}'
# profile A: big waving bird on pink, "60s" badge
pa = HEAD + f'''body{{width:800px;height:800px;background:{DAY}}}
.b{{position:absolute;left:60px;top:40px;width:680px;filter:drop-shadow(0 20px 24px rgba(120,90,80,.25))}}
.badge{{position:absolute;left:50%;bottom:92px;transform:translateX(-50%) rotate(-5deg);background:#E8678A;color:#fff;font-weight:900;font-size:96px;line-height:1;padding:14px 38px 18px;border-radius:60px;border:8px solid #fff;box-shadow:0 10px 0 #C95476}}
</style></head><body><img class="b" src="{img("hi_wave")}"><div class="badge">60s</div></body></html>'''
# profile B: day/night split circle, waving bird + crescent moon
pb = HEAD + f'''body{{width:800px;height:800px;background:linear-gradient(135deg,#FCE1E6 0,#F6C9D4 50%,#262A4F 50%,#1B1F3B 100%)}}
.m{{position:absolute;right:120px;bottom:120px;width:120px;height:120px;border-radius:50%;box-shadow:-26px 16px 0 0 #F7E7B4;transform:rotate(-20deg)}}
.b{{position:absolute;left:80px;top:70px;width:600px;filter:drop-shadow(0 20px 24px rgba(0,0,0,.25))}}
.t{{position:absolute;left:0;right:0;bottom:70px;text-align:center;font-weight:900;font-size:110px;color:#fff;-webkit-text-stroke:0;text-shadow:0 6px 0 #C95476,0 0 24px rgba(0,0,0,.25)}}
</style></head><body>{stars(800, 800, 30, 420)}<div class="m"></div><img class="b" src="{img("hi_wave")}"><div class="t">60s</div></body></html>'''
# banner: left half day, right half night; title in the 1546x423 safe area
side = lambda n, x, y, w, r: f'<img class="sd" src="{img(n)}" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({r}deg)">'
ban = HEAD + f'''body{{width:2560px;height:1440px;background:#FBF4EA}}
.day{{position:absolute;inset:0;background:radial-gradient(ellipse at 15% 25%,#FCE1E6 0,transparent 50%),radial-gradient(ellipse at 30% 90%,#E3F2EC 0,transparent 45%),#FBF4EA}}
.night{{position:absolute;inset:0;background:{NIGHT};clip-path:polygon(74% 0,100% 0,100% 100%,66% 100%)}}
.sd{{position:absolute;filter:drop-shadow(0 16px 18px rgba(60,40,40,.25))}}
.moon{{position:absolute;left:2180px;top:250px;width:150px;height:150px;border-radius:50%;box-shadow:-32px 20px 0 0 #F7E7B4;transform:rotate(-20deg)}}
.safe{{position:absolute;left:507px;top:508px;width:1546px;height:423px;display:flex;flex-direction:column;justify-content:center;padding-left:40px;box-sizing:border-box}}
h1{{margin:0;font-weight:900;font-size:170px;letter-spacing:-3px;line-height:1;color:#3A3134}}
h1 span{{color:#E8678A}}
p{{margin:24px 0 0;font-family:Pretendard;font-size:54px;font-weight:800;color:#5c4d4a;letter-spacing:-.5px}}
p b{{color:#fff;background:#2A2E57;padding:2px 18px 6px;border-radius:16px;font-weight:800}}
.pills{{display:flex;gap:18px;margin-top:30px}}
.pill{{font-family:Pretendard;font-size:34px;font-weight:800;padding:12px 30px;border-radius:40px;color:#fff}}
</style></head><body><div class="day"></div><div class="night"></div>{stars(2560, 1440, 60, 1750)}<div class="moon"></div>
{side("iced_coffee", 170, 430, 300, -6)}{side("o_x_quiz", 240, 860, 270, 5)}{side("sleeping", 2090, 780, 380, 0)}
<div class="safe"><h1>Korean in <span>60s</span></h1>
<p>Learn Korean in 60 seconds, <b>or in your sleep.</b></p>
<div class="pills"><div class="pill" style="background:#E8678A">Daily Shorts</div><div class="pill" style="background:#5CC4A8">K-Culture &amp; Slang</div><div class="pill" style="background:#6B6FB8">8h Sleep Lessons</div></div></div>
</body></html>'''
for name, h in [("profile_a", pa), ("profile_b", pb), ("banner", ban)]:
    open(f"{OUT}/{name}.html", "w").write(h)
