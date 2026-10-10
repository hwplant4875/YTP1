#!/usr/bin/env python3
"""Korean while you sleep, 2 h unique content looped 4x into 8 h.
Each item: EN word -> KO word -> EN sentence -> KO sentence -> KO sentence (slow).
usage: python3 build.py <outdir> [--limit N]   (limit = quick preview with the first N items)"""
import os, sys, json, base64, subprocess, csv, re
import numpy as np, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "../../engine"))
from voices import korean, english
from sound import music
SR = 48000
OUT = sys.argv[1]; os.makedirs(f"{OUT}/st", exist_ok=True)
LIMIT = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--limit" else None
STK = os.path.join(HERE, "../../assets/baepsae")
img = lambda n: "data:image/png;base64," + base64.b64encode(open(f"{STK}/{n}.png", "rb").read()).decode()
rows = list(csv.DictReader(open(f"{HERE}/items.tsv", encoding="utf-8"), delimiter="\t"))[:LIMIT]
cats = list(dict.fromkeys(r["category"] for r in rows))
GAP = dict(after_ew=0.7, after_kw=1.6, after_es=1.1, after_ks=1.6, after_kss=2.8)
INTRO = ("Welcome to Korean in sixty seconds. Get comfortable and close your eyes. "
         "You'll hear a word in English, then in Korean, then a short sentence in both languages. Just listen and relax.")
OUTRO = "That's all for tonight. You did great. Sleep well."
# ---------- visuals (1920x1080, night sky, same look as the 300-word video)
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;width:1920px;height:1080px;overflow:hidden;position:relative;font-family:'YouTube Sans',Pretendard;color:#FFF6EA;
background:radial-gradient(ellipse at 78% 18%,#3B3F72 0,transparent 50%),radial-gradient(ellipse at 10% 95%,#2E4A5E 0,transparent 50%),linear-gradient(180deg,#1B1F3B,#262A4F)}}
.st{{position:absolute;border-radius:50%;background:#FFF6D8}}
#moon{{position:absolute;right:70px;top:40px;width:130px;height:130px;border-radius:50%;box-shadow:-28px 18px 0 0 #F7E7B4;transform:rotate(-20deg)}}
#card{{position:absolute;left:260px;top:170px;width:1400px;height:720px;border-radius:60px;background:rgba(255,255,255,.07);border:3px solid rgba(255,255,255,.12);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
#ko{{font-family:Pretendard;font-weight:900;font-size:200px;line-height:1.05;color:#FFE9B8;text-shadow:0 0 40px rgba(255,220,150,.25);white-space:nowrap}}
#en{{font-size:58px;margin-top:18px;padding:8px 38px;border-radius:50px;background:rgba(255,255,255,.1)}}
#line{{width:900px;height:2px;background:rgba(255,255,255,.12);margin:44px 0 34px}}
#kos{{font-family:Pretendard;font-weight:800;font-size:64px;color:#FFF6EA;max-width:1300px}}
#ens{{font-size:44px;color:#B9B4D8;margin-top:14px;max-width:1300px}}
#cat{{position:absolute;left:80px;top:70px;font-size:40px;padding:12px 30px;border-radius:40px;background:rgba(255,255,255,.1);color:#E8E2FF}}
#num{{position:absolute;left:84px;bottom:76px;font-size:40px;color:#8F8BB5}}
#bar{{position:absolute;left:84px;bottom:52px;width:500px;height:6px;border-radius:3px;background:rgba(255,255,255,.12)}}#bar i{{display:block;height:100%;border-radius:3px;background:#FFE9B8}}
#brand{{position:absolute;right:300px;bottom:66px;font-size:42px;color:#8F8BB5}}
#bird{{position:absolute;right:50px;bottom:24px;width:230px}}
#big{{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
#big h1{{font-weight:400;font-size:120px;margin:0;color:#FFE9B8}}#big p{{font-size:48px;color:#B9B4D8;margin:16px 0 0}}
#big img{{width:380px;margin-bottom:10px}}
</style></head><body><div id="stars"></div><div id="moon"></div>
<div id="card"><div id="ko"></div><div id="en"></div><div id="line"></div><div id="kos"></div><div id="ens"></div></div><div id="cat"></div>
<div id="num"></div><div id="bar"><i></i></div><div id="brand">Korean in 60s</div><img id="bird" src="{img("sleeping")}">
<div id="big"><img src="{img("sleeping")}"><h1></h1><p></p></div>
<script>
let s='';let r=7;const R=()=>(r=(r*9301+49297)%233280)/233280;for(let i=0;i<90;i++){{const z=R()*3+1;s+=`<div class="st" style="left:${{R()*1920}}px;top:${{R()*1080}}px;width:${{z}}px;height:${{z}}px;opacity:${{.3+R()*.6}}"></div>`}}document.getElementById('stars').innerHTML=s;
const $=i=>document.getElementById(i);
const fit=(k,max,w)=>{{k.style.fontSize=max+'px';while(k.scrollWidth>w&&parseFloat(k.style.fontSize)>30)k.style.fontSize=(parseFloat(k.style.fontSize)-4)+'px'}};
window.word=(w,i,n)=>{{$('big').style.display='none';['card','cat','num','bar','bird'].forEach(k=>$(k).style.display='');
 $('ko').textContent=w.ko_word;const e=w.en_word.replace(/\\.$/,'');$('en').textContent=e.charAt(0).toUpperCase()+e.slice(1);$('kos').textContent=w.ko_sentence;$('ens').textContent=w.en_sentence;$('cat').textContent=w.category;
 $('num').textContent=`${{i}} / ${{n}}`;$('bar').firstChild.style.width=(i/n*100)+'%';fit($('ko'),200,1300);fit($('kos'),64,1300)}};
window.title=(h,p)=>{{['card','cat','num','bar','bird'].forEach(k=>$(k).style.display='none');$('big').style.display='flex';$('big').querySelector('h1').innerHTML=h;$('big').querySelector('p').innerHTML=p}};
</script></body></html>'''
open(f"{OUT}/frame.html", "w").write(html)
# ---------- segments: (kind, args, [(wav, offset)], duration)
def item_seg(r, i):
    ew, dew = english(re.sub(r"\s*\([^)]*\)", "", r["en_word"]))  # bracket hints are for the screen only
    kw, dkw = korean(r["ko_word"] + ".")
    es, des = english(r["en_sentence"]); ks, dks = korean(r["ko_sentence"]); kss, dkss = korean(r["ko_sentence"], 0.7)
    t = 0.5; clips = []
    for w, d, g in [(ew, dew, GAP["after_ew"]), (kw, dkw, GAP["after_kw"]), (es, des, GAP["after_es"]), (ks, dks, GAP["after_ks"]), (kss, dkss, GAP["after_kss"])]:
        clips.append((w, t)); t += d + g
    return ("word", (r, i), clips, t)
intro_w, d = english(INTRO); intro = [("title", ("Korean while you sleep", "English · 한국어 · listen and relax"), [(intro_w, 1.5)], d + 4.0)]
body = []; prev = None
for i, r in enumerate(rows, 1):
    if r["category"] != prev:
        prev = r["category"]; w, d = english(prev.replace("&", "and") + ".")
        body.append(("title", (prev, f"part {cats.index(prev) + 1} of {len(cats)}"), [(w, 1.0)], d + 3.0))
    body.append(item_seg(r, i))
outro_w, d = english(OUTRO); outro = [("title", ("잘 자요 🌙", "jal jayo · sleep well"), [(outro_w, 1.0)], d + 8.0)]
dur = lambda seq: sum(s[3] for s in seq)
print(f"items {len(rows)}  body {dur(body)/60:.1f} min  8h total {(dur(intro)+4*dur(body)+dur(outro))/3600:.2f} h", flush=True)
# ---------- stills
allseq = [("intro", intro), ("body", body), ("outro", outro)]
jobs = []
for part, seq in allseq:
    for k, (kind, arg, _, _) in enumerate(seq):
        out = f"{OUT}/st/{part}_{k:04d}.png"
        jobs.append([out, "title", list(arg)] if kind == "title" else [out, "word", [arg[0], arg[1], len(rows)]])
json.dump(jobs, open(f"{OUT}/jobs.json", "w"), ensure_ascii=False)
subprocess.run(["node", f"{HERE}/../001-sleep-300-words/stills.js", OUT], check=True, env={**os.environ, "NODE_PATH": "/opt/node22/lib/node_modules"})
# ---------- audio + video per part
def rd(p):
    with wave.open(p) as f: return np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
def render(part, seq, fade_in, fade_out):
    T = dur(seq); N = int(T * SR) + SR; vo = np.zeros(N, np.float32); t = 0.0; cache = {}
    for kind, arg, clips, d in seq:
        for p, off in clips:
            x = cache.setdefault(p, rd(p)); i = int((t + off) * SR); vo[i:i + len(x)] += x[:N - i]
        t += d
    bed = (music(N, "sleep_music", 4.0) * .2).astype(np.float32)
    f = int(fade_in * SR); bed[:f] *= np.linspace(0, 1, f) if f else 1
    mix = vo * .9 + bed
    with wave.open(f"{OUT}/{part}.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    with open(f"{OUT}/{part}.txt", "w") as fh:
        for k, s in enumerate(seq): fh.write(f"file 'st/{part}_{k:04d}.png'\nduration {s[3]:.3f}\n")
        fh.write(f"file 'st/{part}_{len(seq)-1:04d}.png'\n")
    # fixed loudness gain (not dynamic) so every loop of the body sounds identical
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/{part}.txt", "-i", f"{OUT}/{part}.wav",
        "-af", "volume=1.6" + (f",afade=t=out:st={T - fade_out:.2f}:d={fade_out}" if fade_out else ""),
        "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-tune", "stillimage", "-g", "300",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", "-shortest", f"{OUT}/{part}.mp4"], check=True)
    print("rendered", part, flush=True)
render("intro", intro, 1.5, 1.5); render("body", body, 1.0, 1.0); render("outro", outro, 1.0, 6)
with open(f"{OUT}/final8h.txt", "w") as fh: fh.write("file 'intro.mp4'\n" + "file 'body.mp4'\n" * 4 + "file 'outro.mp4'\n")
with open(f"{OUT}/final2h.txt", "w") as fh: fh.write("file 'intro.mp4'\nfile 'body.mp4'\nfile 'outro.mp4'\n")
for n in ("final2h", "final8h"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/{n}.txt", "-c", "copy", "-movflags", "+faststart", f"{OUT}/{n}.mp4"], check=True)
print("done", flush=True)
