"""Thumbnails 4a (3D stills) / 4b (provocative) / 4c (real photo), 1280x720. Usage: python3 thumbs.py <img dir from build> <outdir>"""
import os, subprocess, sys
IMG, OUT = map(os.path.abspath, sys.argv[1:3]); os.makedirs(OUT, exist_ok=True)
CSS = """*{margin:0;padding:0;box-sizing:border-box}body{width:1280px;height:720px;overflow:hidden;background:#0d0a1f;font-family:"YouTube Sans",sans-serif;color:#fff;position:relative}
.ph{position:absolute;background-size:cover;background-position:center}.a{position:absolute}
.s{paint-order:stroke fill;-webkit-text-stroke:16px #000;font-weight:900}.y{color:#ffd84a}
.chip{display:inline-block;padding:8px 26px 12px;border-radius:16px;font-weight:900}"""
T = {
"4a": f"""<div class=ph style="inset:0;background-image:url({IMG}/y_uH5bGSSw_l0_maxresdefault.jpg);background-size:125%;background-position:85% 15%"></div>
<div class=a style="inset:0;background:linear-gradient(90deg,rgba(13,10,31,.92) 0%,rgba(13,10,31,.55) 45%,transparent 70%)"></div>
<div class="a s" style="left:50px;top:70px;font-size:150px;line-height:.95">1 YEAR<br><span class=y>LATER</span></div>
<div class=a style="left:54px;top:420px"><span class=chip style="background:#ff3fa4;font-size:54px">2 OSCARS 🏆 500M VIEWS</span></div>""",
"4b": f"""<div class=ph style="left:0;top:0;width:1280px;height:720px;background-image:url({IMG}/y_yebNIHKAC4A_maxres1.jpg);background-size:140%;background-position:40% 100%"></div>
<div class=a style="inset:0;background:linear-gradient(0deg,rgba(0,0,0,.85),transparent 60%)"></div>
<div class="a s" style="left:0;width:1280px;text-align:center;top:480px;font-size:90px;line-height:1;white-space:nowrap">A CARTOON BEAT <span class=y>K-POP?</span></div>
<div class=a style="left:60px;top:60px;width:230px;height:230px;border-radius:50%;background:#ffd84a;color:#000;display:flex;flex-direction:column;align-items:center;justify-content:center;transform:rotate(-8deg);box-shadow:0 10px 30px rgba(0,0,0,.6)">
 <div style="font-size:110px;font-weight:900;line-height:1">#1</div><div style="font-size:30px;font-weight:900">HOT 100</div></div>
<svg class=a style="left:300px;top:150px" width="260" height="140" viewBox="0 0 260 140"><path d="M10 20 C 110 10, 180 50, 220 110" stroke="#ff2a2a" stroke-width="16" fill="none" stroke-linecap="round"/><path d="M175 105 L230 125 L225 65" stroke="#ff2a2a" stroke-width="16" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>""",
"4c": f"""<div class=ph style="inset:0;background-image:url({IMG}/y_uH5bGSSw_l0_maxres2.jpg);background-size:125%;background-position:95% 45%"></div>
<div class=a style="inset:0;background:linear-gradient(0deg,rgba(0,0,0,.9) 0%,rgba(0,0,0,.2) 45%,transparent 65%)"></div>
<div class="a s" style="left:0;width:1280px;text-align:center;top:540px;font-size:76px;line-height:1;white-space:nowrap">NETFLIX → <span class=y>OSCARS</span> IN 1 YEAR</div>""",
}
for k, body in T.items():
    open(f"{OUT}/{k}.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>{body}</body></html>")
js = """const { chromium } = require('playwright');(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1280,height:720}});for(const k of process.argv.slice(2)){await p.goto('file://'+k+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:k+'.jpg',type:'jpeg',quality:92});}await b.close();})();"""
open(f"{OUT}/shot.js", "w").write(js)
subprocess.run(["node", f"{OUT}/shot.js"] + [f"{OUT}/{k}" for k in T], check=True, env=os.environ | {"NODE_PATH": "/opt/node22/lib/node_modules"})
print("ok")
