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
.st{{filter:drop-shadow(0 10px 14px rgba(80,40,60,.35))}}"""
T = {
"7a": f"""<div class=a style="inset:0;background:radial-gradient(700px 500px at 30% 40%,#FFD3DF,transparent 70%),#FFF1E2"></div>
<div class="a ko" style="left:60px;top:40px;font-size:400px;line-height:1;color:#E0457F;-webkit-text-stroke:14px #1E1628;paint-order:stroke fill">한글</div>
<div class=a style="left:80px;top:500px;font-size:118px;line-height:1"><span class=box>7 MIN</span></div>
<img class="a st" src="{STK}/reading.png" style="right:40px;bottom:30px;width:330px">""",
"7b": f"""<div class=a style="inset:0;background:radial-gradient(700px 500px at 40% 45%,#FFE7A3,transparent 70%),#FFF1E2"></div>
<div class="a ko" style="left:50px;top:70px;font-size:330px;line-height:1;color:#1E1628">ㅋㅋㅋ</div>
<div class=a style="left:70px;top:470px;font-size:130px;line-height:1">= <span class=box>LOL?</span></div>
<img class="a st" src="{STK}/laugh_tears.png" style="right:40px;bottom:30px;width:340px">""",
"7c": f"""<div class=a style="left:0;top:0;width:620px;height:720px;background:url({IMGS}/sejong.jpg) center 20%/cover"></div>
<div class=a style="left:620px;top:0;width:10px;height:720px;background:#fff"></div>
<div class=a style="left:680px;top:120px;font-size:120px;line-height:1.05">READ<br><span class=box>KOREAN</span></div>
<div class="a ko" style="left:690px;top:420px;font-size:120px;color:#E0457F">한글</div>
<img class="a st" src="{STK}/glasses_study.png" style="right:30px;bottom:24px;width:250px">""",
}
for k, body in T.items():
    open(f"{OUT}/{k}.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>{body}</body></html>")
js = """const { chromium } = require('playwright');(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--allow-file-access-from-files']});
const p=await b.newPage({viewport:{width:1280,height:720}});for(const k of process.argv.slice(2)){await p.goto('file://'+k+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:k+'.jpg',type:'jpeg',quality:92});}await b.close();})();"""
open(f"{OUT}/shot.js", "w").write(js)
subprocess.run(["node", f"{OUT}/shot.js"] + [f"{OUT}/{k}" for k in T], check=True, env=os.environ | {"NODE_PATH": "/opt/node22/lib/node_modules"})
print("ok")
