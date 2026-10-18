"""Thumbnails 4a (3D stills, history timeline) / 4b (provocative, records) / 4c (real photo, Netflix to Oscars), 1280x720. Usage: python3 thumbs.py <img dir from build> <outdir>"""
import os, subprocess, sys
IMG, OUT = map(os.path.abspath, sys.argv[1:3]); os.makedirs(OUT, exist_ok=True)
STK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "baepsae"))
CSS = """*{margin:0;padding:0;box-sizing:border-box}body{width:1280px;height:720px;overflow:hidden;background:#0d0a1f;font-family:"YouTube Sans",sans-serif;color:#fff;position:relative}
.ph{position:absolute;background-size:cover;background-position:center}.a{position:absolute}
.s{paint-order:stroke fill;-webkit-text-stroke:16px #000;font-weight:900}.y{color:#ffd84a}
.chip{display:inline-block;padding:8px 26px 12px;border-radius:16px;font-weight:900}"""
T = {
# 4a: "The Entire History of KPop Demon Hunters in 8 Minutes": one big HUNTR/X still, two words, the channel's 뱁새
"4a": f"""<div class=ph style="inset:0;background-image:url({IMG}/og_mbw.jpg);background-size:112%;background-position:55% 40%"></div>
<div class=a style="inset:0;background:linear-gradient(0deg,rgba(0,0,0,.75) 0%,transparent 40%)"></div>
<div class="a s" style="left:44px;top:548px;font-size:120px;line-height:1;white-space:nowrap">FULL <span class=y>HISTORY</span></div>
<img class=a src="{STK}/popcorn_tv.png" style="right:26px;bottom:18px;width:260px;filter:drop-shadow(0 8px 14px rgba(0,0,0,.6))">""",
# 4b: "Every Record KPop Demon Hunters Broke in Its First Year": the official "Golden" art, two words, 뱁새 with a trophy
"4b": f"""<div class=ph style="inset:0;background-image:url({IMG}/y_yebNIHKAC4A_maxresdefault.jpg);background-size:128%;background-position:75% 8%"></div>
<div class=a style="inset:0;background:linear-gradient(0deg,rgba(0,0,0,.92) 0%,rgba(0,0,0,.6) 28%,transparent 46%)"></div>
<div class="a s" style="left:44px;top:548px;font-size:120px;line-height:1;white-space:nowrap">EVERY <span class=y>RECORD</span></div>
<img class=a src="{STK}/trophy.png" style="right:26px;bottom:18px;width:260px;filter:drop-shadow(0 8px 14px rgba(0,0,0,.6))">""",
# 4c: "How KPop Demon Hunters Went From Netflix to 2 Oscars in 1 Year": HUNTR/X big on the left, the real Oscar winners on the right
"4c": f"""<div class=ph style="left:0;top:0;width:840px;height:720px;background-image:url({IMG}/og_deadline.jpg);background-size:auto 100%;background-position:45% 0%"></div>
<div class=ph style="left:820px;top:0;width:460px;height:720px;background-image:url({IMG}/y_uH5bGSSw_l0_maxres2.jpg);background-size:auto 105%;background-position:52% 20%;border-left:8px solid #fff;box-shadow:-14px 0 30px rgba(0,0,0,.6)"></div>
<div class=a style="inset:0;background:linear-gradient(0deg,rgba(0,0,0,.85) 0%,transparent 32%)"></div>
<div class="a s" style="left:44px;top:560px;font-size:120px;line-height:1;white-space:nowrap">2 <span class=y>OSCARS</span></div>
<img class=a src="{STK}/excited.png" style="right:22px;bottom:16px;width:230px;filter:drop-shadow(0 8px 14px rgba(0,0,0,.6))">""",
}
for k, body in T.items():
    open(f"{OUT}/{k}.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>{body}</body></html>")
js = """const { chromium } = require('playwright');(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1280,height:720}});for(const k of process.argv.slice(2)){await p.goto('file://'+k+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:k+'.jpg',type:'jpeg',quality:92});}await b.close();})();"""
open(f"{OUT}/shot.js", "w").write(js)
subprocess.run(["node", f"{OUT}/shot.js"] + [f"{OUT}/{k}" for k in T], check=True, env=os.environ | {"NODE_PATH": "/opt/node22/lib/node_modules"})
print("ok")
