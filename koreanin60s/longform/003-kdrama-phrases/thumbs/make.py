"""Thumbnails 1a/1b/1c (1280x720) for long-form #1. Usage: python3 make.py <outdir>"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "..", "..", "..", "assets")
STK = "file://" + os.path.abspath(os.path.join(A, "baepsae"))
FONT = "".join(f"@font-face{{font-family:'GmarketSans';font-weight:{w};unicode-range:U+0021-10FFFF;src:url('file://{os.path.abspath(A)}/fonts/GmarketSans{n}.woff')}}" for w, n in ((500, "Medium"), (700, "Bold")))
BASE = FONT + """html,body{margin:0;width:1280px;height:720px;overflow:hidden;font-family:GmarketSans,Pretendard,"Noto Color Emoji",sans-serif;color:#3A3134}
.bg{position:absolute;inset:0;background:radial-gradient(ellipse at 85% 10%,#FCD3DD 0,transparent 45%),radial-gradient(ellipse at 5% 90%,#D8F0E6 0,transparent 45%),#FBF1E4}
.grid{position:absolute;inset:0;background-image:linear-gradient(#EADFD2 2px,transparent 2px),linear-gradient(90deg,#EADFD2 2px,transparent 2px);background-size:64px 64px;opacity:.35}
.a{position:absolute}.st{position:absolute;filter:drop-shadow(0 10px 18px rgba(80,50,40,.25))}
.a,.card{white-space:nowrap}.chip{display:inline-block;border-radius:999px;color:#fff;font-weight:700;padding:14px 30px}
.card{background:#fff;border-radius:44px;box-shadow:0 14px 0 #EAD9CB,0 24px 40px rgba(80,50,40,.15)}"""
T = {
"1a": f"""<div class=bg></div><div class=grid></div>
<div class=a style="left:60px;top:58px"><span class=chip style="background:#3A3134;font-size:40px">🎬 50 K-DRAMA PHRASES</span></div>
<div class="a card" style="left:60px;top:190px;width:760px;height:380px;display:flex;flex-direction:column;align-items:center;justify-content:center">
 <div style="font-size:52px;font-weight:700;color:#8A7A74">I miss you.</div>
 <div style="font-size:150px;font-weight:700;color:#EF6F92;letter-spacing:-4px;line-height:1.05">보고 싶어</div></div>
<img class=st src="{STK}/popcorn_tv.png" style="left:820px;top:200px;width:440px">""",
"1b": f"""<div class=bg></div><div class=grid></div>
<div class=a style="left:56px;top:40px;font-size:200px;font-weight:700;letter-spacing:-6px">50</div>
<div class=a style="left:400px;top:50px;width:500px;height:190px;background:#F2C14E;border-radius:50px;display:flex;align-items:center;justify-content:center;font-size:110px;font-weight:700;color:#3A3134;box-shadow:0 12px 0 #D9A631">사랑해 💗</div>
<div class=a style="left:470px;top:236px;width:0;height:0;border-left:34px solid transparent;border-right:34px solid transparent;border-top:50px solid #D9A631"></div>
<div class=a style="left:52px;top:270px;font-size:150px;font-weight:700;letter-spacing:-4px;color:#A48AEB">PHRASES</div>
<div class=a style="left:62px;top:480px;font-size:58px;font-weight:700;color:#5E514C">from every K-Drama 🇰🇷</div>
<img class=st src="{STK}/finger_heart.png" style="left:900px;top:330px;width:350px">""",
"1c": f"""<div class=bg></div><div class=grid></div>
<div class=a style="left:50px;top:40px;transform:rotate(-5deg);background:#F28BA8;border-radius:40px;padding:22px 40px 18px;text-align:center;box-shadow:0 10px 0 #D86A8A,0 18px 30px rgba(80,50,40,.15)"><div style="font-size:110px;font-weight:700;color:#fff;line-height:1.05">사랑해</div><div style="font-size:34px;font-weight:700;color:rgba(255,255,255,.9)">I love you</div></div>
<div class=a style="left:470px;top:30px;transform:rotate(4deg);background:#F2C14E;border-radius:40px;padding:22px 40px 18px;text-align:center;box-shadow:0 10px 0 #D9A631,0 18px 30px rgba(80,50,40,.15)"><div style="font-size:92px;font-weight:700;color:#fff;line-height:1.05">대박!</div><div style="font-size:34px;font-weight:700;color:rgba(255,255,255,.9)">Wow!</div></div>
<div class=a style="left:870px;top:60px;transform:rotate(-3deg);background:#A48AEB;border-radius:40px;padding:22px 40px 18px;text-align:center;box-shadow:0 10px 0 #8467D0,0 18px 30px rgba(80,50,40,.15)"><div style="font-size:84px;font-weight:700;color:#fff;line-height:1.05">보고 싶어</div><div style="font-size:34px;font-weight:700;color:rgba(255,255,255,.9)">I miss you</div></div>
<div class=a style="left:60px;top:330px;transform:rotate(3deg);background:#5CC4A8;border-radius:40px;padding:22px 40px 18px;text-align:center;box-shadow:0 10px 0 #3EA388,0 18px 30px rgba(80,50,40,.15)"><div style="font-size:88px;font-weight:700;color:#fff;line-height:1.05">괜찮아?</div><div style="font-size:34px;font-weight:700;color:rgba(255,255,255,.9)">Are you okay?</div></div>
<div class=a style="left:890px;top:330px;transform:rotate(-4deg);background:#7FA9E8;border-radius:40px;padding:22px 40px 18px;text-align:center;box-shadow:0 10px 0 #5C88CC,0 18px 30px rgba(80,50,40,.15)"><div style="font-size:96px;font-weight:700;color:#fff;line-height:1.05">가지 마</div><div style="font-size:34px;font-weight:700;color:rgba(255,255,255,.9)">Don't go</div></div>
<div class=a style="left:0;width:1280px;top:585px;text-align:center;font-size:76px;font-weight:700;color:#3A3134">You already know these 😳</div>
<img class=st src="{STK}/popcorn_tv.png" style="left:470px;top:225px;width:340px">""",
}
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for k, body in T.items():
    h = f"{out}/{k}.html"; open(h, "w").write(f"<!doctype html><meta charset=utf-8><style>{BASE}</style>{body}")
    subprocess.run(["node", os.path.join(HERE, "..", "..", "..", "branding", "shot.js"), h, "1280", "720", f"{out}/{k}.png"], check=True, env={**os.environ, "NODE_PATH": "/opt/node22/lib/node_modules"})
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{out}/{k}.png", "-q:v", "2", f"{out}/thumb_{k}.jpg"], check=True)
