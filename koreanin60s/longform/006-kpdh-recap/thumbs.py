"""Thumbnails 4a (3D stills, history timeline) / 4b (provocative, records) / 4c (real photo, Netflix to Oscars), 1280x720. Usage: python3 thumbs.py <img dir from build> <outdir>"""
import os, subprocess, sys
IMG, OUT = map(os.path.abspath, sys.argv[1:3]); os.makedirs(OUT, exist_ok=True)
STK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "baepsae"))
CSS = """*{margin:0;padding:0;box-sizing:border-box}body{width:1280px;height:720px;overflow:hidden;background:#0d0a1f;font-family:"YouTube Sans",sans-serif;color:#fff;position:relative}
.ph{position:absolute;background-size:cover;background-position:center}.a{position:absolute}
.s{paint-order:stroke fill;-webkit-text-stroke:16px #000;font-weight:900}.y{color:#ffd84a}
.chip{display:inline-block;padding:8px 26px 12px;border-radius:16px;font-weight:900}"""
PINK = "#F7B8CA"  # channel highlight pink
HL = f'background:{PINK};color:#111;-webkit-text-stroke:0;padding:0 18px 6px;border-radius:14px;box-shadow:0 8px 0 #000'
# Benchmark (top KPDH thumbnails 2026-10-18): one huge character face filling the frame, 0-2 words, one focal point, one contrast object.
T = {
# 4a: "The Entire History of KPop Demon Hunters in 8 Minutes": Rumi's face huge, "FULL STORY", 뱁새
"4a": f"""<div class=ph style="inset:0;background-image:url({IMG}/og_wonend.jpg);background-size:150%;background-position:52% 22%"></div>
<div class=a style="inset:0;background:linear-gradient(90deg,rgba(0,0,0,.55) 0%,transparent 45%)"></div>
<div class="a s" style="left:44px;top:60px;font-size:132px;line-height:1.12">FULL<br><span style="{HL}">STORY</span></div>
<img class=a src="{STK}/popcorn_tv.png" style="left:30px;bottom:14px;width:250px;filter:drop-shadow(0 8px 14px rgba(0,0,0,.6))">""",
# 4b: "Every Record KPop Demon Hunters Broke in Its First Year": the official "Golden" art zoomed to the three faces, "EVERY RECORD", 뱁새 with a trophy
"4b": f"""<div class=ph style="inset:0;background-image:url({IMG}/y_yebNIHKAC4A_maxresdefault.jpg);background-size:140%;background-position:62% 0%"></div>
<div class=a style="inset:0;background:linear-gradient(0deg,rgba(0,0,0,.8) 0%,transparent 40%)"></div>
<div class="a s" style="left:44px;top:556px;font-size:118px;line-height:1;white-space:nowrap">EVERY <span style="{HL}">RECORD</span></div>
<img class=a src="{STK}/trophy.png" style="right:22px;bottom:14px;width:240px;filter:drop-shadow(0 8px 14px rgba(0,0,0,.6))">""",
# 4c: "How KPop Demon Hunters Went From Netflix to 2 Oscars in 1 Year": Mira's face huge + the real Oscar statuettes, "2 OSCARS", 뱁새
"4c": f"""<div class=ph style="inset:0;background-image:url({IMG}/og_deadline.jpg);background-size:190%;background-position:48% 18%"></div>
<div class=a style="right:34px;top:40px;width:420px;height:470px;border-radius:22px;border:8px solid #fff;background:url({IMG}/y_uH5bGSSw_l0_maxres2.jpg) 47% 78%/auto 210%;transform:rotate(4deg);box-shadow:0 16px 40px rgba(0,0,0,.7)"></div>
<div class=a style="inset:0;background:linear-gradient(0deg,rgba(0,0,0,.8) 0%,transparent 34%)"></div>
<div class="a s" style="left:44px;top:556px;font-size:118px;line-height:1;white-space:nowrap">2 <span style="{HL}">OSCARS</span></div>
<img class=a src="{STK}/excited.png" style="right:22px;bottom:14px;width:220px;filter:drop-shadow(0 8px 14px rgba(0,0,0,.6))">""",
}
for k, body in T.items():
    open(f"{OUT}/{k}.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>{body}</body></html>")
js = """const { chromium } = require('playwright');(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1280,height:720}});for(const k of process.argv.slice(2)){await p.goto('file://'+k+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:k+'.jpg',type:'jpeg',quality:92});}await b.close();})();"""
open(f"{OUT}/shot.js", "w").write(js)
subprocess.run(["node", f"{OUT}/shot.js"] + [f"{OUT}/{k}" for k in T], check=True, env=os.environ | {"NODE_PATH": "/opt/node22/lib/node_modules"})
print("ok")
