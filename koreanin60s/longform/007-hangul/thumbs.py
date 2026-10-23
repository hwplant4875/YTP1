"""Thumbnails 7a/7b/7c (1280x720), minimalist: one huge focal point, 1-2 words, channel pink, 뱁새. Usage: python3 thumbs.py <outdir>"""
import os, subprocess, sys
OUT = os.path.abspath(sys.argv[1]); os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.abspath(os.path.join(HERE, "..", "..", "assets"))
IMGS = os.environ.get("HANGUL_IMG", "/mnt/project-files/plans/toptechs/longform/07-hangul/img")
STK = f"{A}/baepsae"
CSS = f"""@font-face{{font-family:'Baloo 2';font-weight:400 800;src:url('file://{A}/fonts/Baloo2.ttf')}}@font-face{{font-family:'Jua';src:url('file://{A}/fonts/Jua.ttf')}}
*{{margin:0;padding:0;box-sizing:border-box}}body{{width:1280px;height:720px;overflow:hidden;background:#FFF1E2;font-family:'Baloo 2','Jua',sans-serif;font-weight:800;color:#1E1628;position:relative}}
.a{{position:absolute}}.ko{{font-family:'Jua';font-weight:400}}
.box{{background:#F7B8CA;color:#111;padding:6px 26px 0;border-radius:18px;box-shadow:0 8px 0 #1E1628;display:inline-block}}
.st{{filter:drop-shadow(0 10px 14px rgba(0,0,0,.45))}}.card{{background:#fff;border-radius:28px;font-size:170px;line-height:1;padding:20px 30px 6px;box-shadow:0 10px 0 #000}}.card.big{{color:#E0457F;font-size:200px;box-shadow:0 0 0 10px #FFD84A,0 10px 0 10px #000}}.op{{font-size:110px;color:#fff;-webkit-text-stroke:10px #000;paint-order:stroke fill}}"""
# v2 (user 2026-10-23: v1 cream set "너무 별로", make people click): dark high-contrast backgrounds, one giant focal point,
# a curiosity gap (can YOU read this?), 1-2 words, channel pink box, 뱁새 reacting.
S = "paint-order:stroke fill;-webkit-text-stroke:16px #000"
T = {
"8a": f"""<div class=a style="inset:0;background:radial-gradient(620px 420px at 42% 46%,#3a2a6e,transparent 75%),#120c24"></div>
<div class="a ko" style="left:60px;top:60px;font-size:380px;line-height:1;color:#fff;{S};text-shadow:0 0 60px rgba(247,184,202,.55)">커피</div>
<div class=a style="left:90px;top:470px;font-size:190px;line-height:1;color:#fff;{S}">= <span class=box style="-webkit-text-stroke:0">???</span></div>
<div class=a style="right:40px;top:40px;font-size:62px;line-height:1"><span class=box style="background:#FFD84A">7 MIN</span></div>
<img class="a st" src="{STK}/thinking.png" style="right:30px;bottom:20px;width:330px">""",
"8b": f"""<div class=a style="inset:0;background:#120c24"></div>
<div class=a style="right:0;top:0;width:640px;height:720px;background:url({IMGS}/sejong_face.jpg) 50% 18%/cover"></div>
<div class=a style="right:0;top:0;width:640px;height:720px;background:linear-gradient(90deg,#120c24 0%,rgba(18,12,36,0) 35%)"></div>
<div class=a style="left:50px;top:90px;font-size:150px;line-height:1.02;color:#fff;{S}">READ<br>KOREAN</div>
<div class=a style="left:56px;top:430px;font-size:150px;line-height:1"><span class=box>7 MIN</span></div>
<img class="a st" src="{STK}/excited.png" style="left:560px;bottom:12px;width:220px">""",
"8c": f"""<div class=a style="inset:0;background:radial-gradient(700px 420px at 50% 40%,#ff6fa0,#E0457F 70%)"></div>
<div class=a style="left:0;width:1280px;top:70px;display:flex;justify-content:center;align-items:center;gap:22px">
 <div class="ko card">ㅎ</div><div class=op>+</div><div class="ko card">ㅏ</div><div class=op>+</div><div class="ko card">ㄴ</div><div class=op>=</div><div class="ko card big">한</div></div>
<div class=a style="left:60px;top:430px;font-size:190px;line-height:1;color:#FFD84A;{S}">EASY?</div>
<img class="a st" src="{STK}/mind_blown.png" style="right:40px;bottom:20px;width:330px">""",
}
for k, body in T.items():
    open(f"{OUT}/{k}.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>{body}</body></html>")
js = """const { chromium } = require('playwright');(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--allow-file-access-from-files']});
const p=await b.newPage({viewport:{width:1280,height:720}});for(const k of process.argv.slice(2)){await p.goto('file://'+k+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:k+'.jpg',type:'jpeg',quality:92});}await b.close();})();"""
open(f"{OUT}/shot.js", "w").write(js)
subprocess.run(["node", f"{OUT}/shot.js"] + [f"{OUT}/{k}" for k in T], check=True, env=os.environ | {"NODE_PATH": "/opt/node22/lib/node_modules"})
print("ok")
