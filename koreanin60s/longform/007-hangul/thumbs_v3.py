"""Thumbnails 9a/9b/9c (1280x720) in the user's reference style (2026-10-24, "Your Daily Korean Teacher"): bright white/pink background,
Korean flag, one big Hangul word with [romanization] and the English meaning, clean bold sans, small 뱁새. Usage: python3 thumbs_v3.py <outdir>"""
import os, subprocess, sys
OUT = os.path.abspath(sys.argv[1]); os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.abspath(os.path.join(HERE, "..", "..", "assets"))
STK = f"{A}/baepsae"; F = "/mnt/project-files/fonts"
CSS = f"""@font-face{{font-family:'YTS';src:url('file://{F}/YouTubeSans-Black.otf')}}@font-face{{font-family:'PB';src:url('file:///root/.fonts/Pretendard-Black.otf')}}
*{{margin:0;padding:0;box-sizing:border-box}}body{{width:1280px;height:720px;overflow:hidden;font-family:'YTS','PB','Noto Color Emoji',sans-serif;color:#111;position:relative;
background:radial-gradient(760px 520px at 50% 45%,#fff 35%,#FDE7EA 100%)}}
.a{{position:absolute}}.ko{{font-family:'PB'}}.c{{left:0;width:1280px;text-align:center}}
.flag{{display:inline-block;background:#fff;border-radius:22px;padding:10px 18px 4px;box-shadow:0 6px 18px rgba(0,0,0,.18);font-family:'Noto Color Emoji'}}
.rom{{font-family:'PB';font-style:italic;color:#555}}.st{{filter:drop-shadow(0 6px 10px rgba(0,0,0,.2))}}
.tile{{background:#FBD9DF;border-radius:20px;width:250px;height:250px;display:flex;align-items:center;justify-content:center;font-family:'PB';font-size:190px;line-height:1}}
.lbl{{text-align:center;font-size:40px;margin-top:12px}}.lbl small{{display:block;font-family:'PB';font-style:italic;font-size:28px;color:#666;margin-top:2px}}
.op{{font-size:80px;color:#111;margin-top:-80px}}"""
T = {
"9a": f"""<div class="a c" style="top:40px;font-size:84px"><span class=flag>🇰🇷</span></div>
<div class="a c" style="top:186px;font-size:62px">Korean Alphabet?</div>
<div class="a c ko" style="top:250px;font-size:290px;line-height:1">한글</div>
<div class="a c rom" style="top:560px;font-size:46px">[hangeul]</div>
<img class="a st" src="{STK}/excited.png" style="right:40px;bottom:30px;width:190px">""",
"9b": f"""<div class="a c" style="top:42px;font-size:96px;letter-spacing:1px"><span style="font-family:'Noto Color Emoji';font-size:72px">🇰🇷</span> LEARN KOREAN <span style="font-family:'Noto Color Emoji';font-size:72px">🇰🇷</span></div>
<div class=a style="left:0;width:1280px;top:205px;display:flex;justify-content:center;align-items:center;gap:26px">
 <div><div class=tile>ㅎ</div><div class=lbl>H<small>[h]</small></div></div><div class=op>+</div>
 <div><div class=tile>ㅏ</div><div class=lbl>A<small>[a]</small></div></div><div class=op>+</div>
 <div><div class=tile>ㄴ</div><div class=lbl>N<small>[n]</small></div></div><div class=op>=</div>
 <div><div class=tile style="background:#FF2D55;color:#fff">한</div><div class=lbl>HAN<small>[han]</small></div></div></div>
<img class="a st" src="{STK}/mind_blown.png" style="left:30px;bottom:20px;width:150px">""",
}
# 9c: "100 WORDS IN KOREAN" style, a wall of letter cards behind a black band
L = [("ㄱ","g"),("ㄴ","n"),("ㄷ","d"),("ㄹ","r"),("ㅁ","m"),("ㅂ","b"),("ㅅ","s"),("ㅇ","ng"),("ㅈ","j"),("ㅊ","ch"),("ㅋ","k"),("ㅌ","t"),("ㅍ","p"),("ㅎ","h"),
     ("ㅏ","a"),("ㅓ","eo"),("ㅗ","o"),("ㅜ","u"),("ㅡ","eu"),("ㅣ","i"),("ㅑ","ya"),("ㅕ","yeo"),("ㅛ","yo"),("ㅠ","yu")]
cells = "".join(f"<div style='background:#fff;border-radius:14px;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 3px 8px rgba(0,0,0,.08)'><div class=ko style='font-size:96px;line-height:1'>{k}</div><div class=rom style='font-size:26px'>[{r}]</div></div>" for k, r in L)
T["9c"] = f"""<div class=a style="inset:18px;display:grid;grid-template-columns:repeat(8,1fr);grid-template-rows:repeat(3,1fr);gap:14px">{cells}</div>
<div class=a style="left:0;width:1280px;top:262px;height:190px;background:#111;display:flex;align-items:center;justify-content:center;gap:22px;font-size:90px;white-space:nowrap">
<span style="font-family:'Noto Color Emoji';font-size:76px">🇰🇷</span>
<span style="color:#FF2D55">READ</span><span style="color:#fff">KOREAN</span><span style="color:#3D7BFF">IN 7 MIN</span></div>
<img class="a st" src="{STK}/excited.png" style="right:6px;bottom:4px;width:150px">"""
for k, body in T.items():
    open(f"{OUT}/{k}.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>{body}</body></html>")
js = """const { chromium } = require('playwright');(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--allow-file-access-from-files']});
const p=await b.newPage({viewport:{width:1280,height:720}});for(const k of process.argv.slice(2)){await p.goto('file://'+k+'.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
await p.screenshot({path:k+'.jpg',type:'jpeg',quality:92});}await b.close();})();"""
open(f"{OUT}/shot.js", "w").write(js)
subprocess.run(["node", f"{OUT}/shot.js"] + [f"{OUT}/{k}" for k in T], check=True, env=os.environ | {"NODE_PATH": "/opt/node22/lib/node_modules"})
print("ok")
