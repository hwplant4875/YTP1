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
# 4b: "Every Record KPop Demon Hunters Broke in Its First Year": the records piled up next to Rumi (provocative: arrow, badges)
"4b": f"""<div class=ph style="left:560px;top:0;width:720px;height:720px;background-image:url({IMG}/og_wonend.jpg);background-position:60% 30%"></div>
<div class=a style="inset:0;background:linear-gradient(90deg,#0d0a1f 0%,#0d0a1f 44%,rgba(13,10,31,.3) 62%,transparent 80%)"></div>
<div class="a s" style="left:46px;top:30px;font-size:104px;line-height:.95">EVERY<br><span class=y>RECORD</span><br>BROKEN</div>
<div class=a style="left:46px;top:380px;display:flex;flex-direction:column;gap:16px">
 <span class=chip style="background:#ffd84a;color:#000;font-size:52px">#1 IN 30+ COUNTRIES</span>
 <span class=chip style="background:#ff3fa4;font-size:52px">500M NETFLIX VIEWS</span>
 <span class=chip style="background:#8b5cff;font-size:52px">FIRST K-POP OSCAR 🏆</span></div>""",
# 4c: "How KPop Demon Hunters Went From Netflix to 2 Oscars in 1 Year": real Oscars photo, from Netflix to the stage
"4c": f"""<div class=ph style="inset:0;background-image:url({IMG}/y_uH5bGSSw_l0_maxres2.jpg);background-size:125%;background-position:95% 45%"></div>
<div class=a style="inset:0;background:linear-gradient(0deg,rgba(0,0,0,.9) 0%,rgba(0,0,0,.2) 42%,transparent 60%)"></div>
<div class=a style="left:36px;top:290px;width:340px;height:191px;border-radius:14px;border:6px solid #fff;background:url({IMG}/og_mbw.jpg) center/cover;transform:rotate(-4deg);box-shadow:0 12px 30px rgba(0,0,0,.7)"></div>
<div class="a s" style="left:0;width:1280px;text-align:center;top:520px;font-size:100px;line-height:1;white-space:nowrap">NETFLIX → <span class=y>2 OSCARS</span></div>""",
}
for k, body in T.items():
    open(f"{OUT}/{k}.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>{body}</body></html>")
js = """const { chromium } = require('playwright');(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1280,height:720}});for(const k of process.argv.slice(2)){await p.goto('file://'+k+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:k+'.jpg',type:'jpeg',quality:92});}await b.close();})();"""
open(f"{OUT}/shot.js", "w").write(js)
subprocess.run(["node", f"{OUT}/shot.js"] + [f"{OUT}/{k}" for k in T], check=True, env=os.environ | {"NODE_PATH": "/opt/node22/lib/node_modules"})
print("ok")
