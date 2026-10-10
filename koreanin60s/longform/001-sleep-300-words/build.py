#!/usr/bin/env python3
"""Sleep long-form: 300 words. English once, Korean twice, slow. 1920x1080 stills + ffmpeg concat at 30fps.
usage: python3 build.py <outdir> [--stills-only N]"""
import os, sys, json, base64, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../engine"))
from engine import tts, SR
import numpy as np, wave
OUT = sys.argv[1]; os.makedirs(f"{OUT}/st", exist_ok=True)
STK = os.path.join(HERE, "../../assets/baepsae")
img = lambda n: "data:image/png;base64," + base64.b64encode(open(f"{STK}/{n}.png", "rb").read()).decode()
cats, words = [], []
for ln in open(f"{HERE}/words.txt", encoding="utf-8"):
    ln = ln.strip()
    if not ln: continue
    if ln.startswith("#"): cats.append(ln[1:].strip()); continue
    en, ko, rom = ln.split("|"); words.append({"en": en, "ko": ko, "rom": rom, "cat": cats[-1], "ci": len(cats)})
INTRO = "Welcome to Korean in sixty seconds. Get comfortable, close your eyes, and let three hundred Korean words drift into your mind. I'll say each word in English, then twice in Korean. Let's begin."
OUTRO = "That's all three hundred words. You did great today. Sleep well."
# ---------- visuals
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;width:1920px;height:1080px;overflow:hidden;position:relative;font-family:'YouTube Sans',Pretendard;color:#FFF6EA;
background:radial-gradient(ellipse at 78% 18%,#3B3F72 0,transparent 50%),radial-gradient(ellipse at 10% 95%,#2E4A5E 0,transparent 50%),linear-gradient(180deg,#1B1F3B,#262A4F)}}
.st{{position:absolute;border-radius:50%;background:#FFF6D8}}
#moon{{position:absolute;right:150px;top:90px;width:130px;height:130px;border-radius:50%;box-shadow:-28px 18px 0 0 #F7E7B4;transform:rotate(-20deg)}}
#card{{position:absolute;left:360px;top:220px;width:1200px;height:600px;border-radius:60px;background:rgba(255,255,255,.07);border:3px solid rgba(255,255,255,.12);display:flex;flex-direction:column;align-items:center;justify-content:center}}
#ko{{font-family:'YouTube Sans',Pretendard;font-weight:900;font-size:230px;line-height:1.05;color:#FFE9B8;text-shadow:0 0 40px rgba(255,220,150,.25);white-space:nowrap}}
#rom{{font-family:'YouTube Sans',Pretendard;font-weight:500;font-size:60px;color:#B9B4D8;margin-top:6px}}
#en{{font-size:64px;font-weight:700;margin-top:26px;padding:10px 40px;border-radius:50px;background:rgba(255,255,255,.1)}}
#cat{{position:absolute;left:80px;top:70px;font-size:40px;font-weight:800;padding:12px 30px;border-radius:40px;background:rgba(255,255,255,.1);color:#E8E2FF}}
#num{{position:absolute;left:84px;bottom:76px;font-family:'YouTube Sans',Pretendard;font-size:40px;color:#8F8BB5}}
#bar{{position:absolute;left:84px;bottom:52px;width:500px;height:6px;border-radius:3px;background:rgba(255,255,255,.12)}}#bar i{{display:block;height:100%;border-radius:3px;background:#FFE9B8}}
#brand{{position:absolute;right:300px;bottom:66px;font-family:'YouTube Sans',Pretendard;font-weight:900;font-size:42px;color:#8F8BB5}}
#bird{{position:absolute;right:50px;bottom:24px;width:230px;opacity:.95}}
#big{{position:absolute;left:0;right:0;top:0;bottom:0;display:none;flex-direction:column;align-items:center;justify-content:center}}
#big h1{{font-family:'YouTube Sans',Pretendard;font-weight:900;font-size:120px;margin:0;color:#FFE9B8}}#big p{{font-size:48px;font-weight:700;color:#B9B4D8;margin:16px 0 0}}
#big img{{width:380px;margin-bottom:10px}}
</style></head><body><div id="stars"></div><div id="moon"></div>
<div id="card"><div id="ko"></div><div id="rom"></div><div id="en"></div></div><div id="cat"></div>
<div id="num"></div><div id="bar"><i></i></div><div id="brand">Korean in 60s</div><img id="bird" src="{img("sleeping")}">
<div id="big"><img src="{img("sleeping")}"><h1></h1><p></p></div>
<script>
let s='';let r=7;const R=()=>(r=(r*9301+49297)%233280)/233280;for(let i=0;i<90;i++){{const z=R()*3+1;s+=`<div class="st" style="left:${{R()*1920}}px;top:${{R()*1080}}px;width:${{z}}px;height:${{z}}px;opacity:${{.3+R()*.6}}"></div>`}}document.getElementById('stars').innerHTML=s;
const $=i=>document.getElementById(i);
window.word=(w,i,n)=>{{$('big').style.display='none';['card','cat','num','bar','bird'].forEach(k=>$(k).style.display='');
 $('ko').textContent=w.ko;$('rom').textContent=w.rom;$('en').textContent=w.en;$('cat').textContent=w.cat;$('num').textContent=`${{i}} / ${{n}}`;
 $('bar').firstChild.style.width=(i/n*100)+'%';const k=$('ko');k.style.fontSize='230px';while(k.scrollWidth>1100)k.style.fontSize=(parseFloat(k.style.fontSize)-10)+'px'}};
window.title=(h,p)=>{{['card','cat','num','bar','bird'].forEach(k=>$(k).style.display='none');$('big').style.display='flex';$('big').querySelector('h1').innerHTML=h;$('big').querySelector('p').innerHTML=p}};
</script></body></html>'''
open(f"{OUT}/frame.html", "w").write(html)
# ---------- schedule: (still, [(wav, offset)], duration)
seq = []
def say(text, lang="en"): return tts(text, lang)
w, d = say(INTRO); seq.append(("title", ("Korean words<br>while you sleep", "300 words · English once, Korean twice"), [(w, 1.0)], d + 2.2))
prev = None
for i, x in enumerate(words, 1):
    if x["ci"] != prev:
        prev = x["ci"]; w, d = say(f"{x['cat'].replace('&', 'and')}.")
        seq.append(("title", (x["cat"], f"part {x['ci']} of {len(cats)}"), [(w, 0.8)], d + 2.4))
    we, de = say(x["en"].replace("(", ", ").replace(")", "")); wk, dk = say(x["ko"] + ("." if not x["ko"].endswith("?") else ""), "ko")
    a = 0.4; b = a + de + 0.8; c = b + dk + 1.4
    seq.append(("word", (x, i), [(we, a), (wk, b), (wk, c)], c + dk + 2.0))
w, d = say(OUTRO); seq.append(("title", ("잘 자요 🌙", "jal jayo · sleep well"), [(w, 0.8)], d + 6.0))
total = sum(s[3] for s in seq); print("segments", len(seq), "duration %.1f min" % (total / 60))
# ---------- stills
lim = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--stills-only" else None
jobs = []
for k, (kind, arg, _, _) in enumerate(seq[:lim] if lim else seq):
    if kind == "title": jobs.append([f"{OUT}/st/{k:04d}.png", "title", list(arg)])
    else: jobs.append([f"{OUT}/st/{k:04d}.png", "word", [arg[0], arg[1], len(words)]])
json.dump(jobs, open(f"{OUT}/jobs.json", "w"), ensure_ascii=False)
subprocess.run(["node", f"{HERE}/stills.js", OUT], check=True, env={**os.environ, "NODE_PATH": "/opt/node22/lib/node_modules"})
if lim: sys.exit()
# ---------- audio: voice track
N = int((total + 1) * SR); vo = np.zeros((N, 2), np.float32); t = 0.0
def rd(p):
    with wave.open(p) as f: return np.frombuffer(f.readframes(f.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
cache = {}
for kind, arg, clips, dur in seq:
    for p, off in clips:
        if p is None: continue
        x = cache.setdefault(p, rd(p)); i = int((t + off) * SR); vo[i:i + len(x)] += x[:N - i]
    t += dur
# calm ElevenLabs piano/pad bed, looped with long crossfades
from sound import music
bed = (music(N, "sleep_music", 4.0) * .22).astype(np.float32)
fade = int(8 * SR); bed[:fade] *= np.linspace(0, 1, fade)
mix = vo * .9 + bed[:, None]
mix = mix / max(1.0, np.abs(mix).max() / .95)
with wave.open(f"{OUT}/mix.wav", "wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{OUT}/mix.wav", "-af", "loudnorm=I=-20:TP=-2:LRA=11", "-ar", str(SR), f"{OUT}/mixn.wav"], check=True)
# ---------- video: concat stills with durations
with open(f"{OUT}/concat.txt", "w") as f:
    for k, s in enumerate(seq): f.write(f"file 'st/{k:04d}.png'\nduration {s[3]:.3f}\n")
    f.write(f"file 'st/{len(seq)-1:04d}.png'\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/concat.txt", "-i", f"{OUT}/mixn.wav",
    "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart", "-shortest", f"{OUT}/out.mp4"], check=True)
print("done", f"{OUT}/out.mp4")
