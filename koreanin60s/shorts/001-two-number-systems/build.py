import json, sys
import os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../mascot"))
from bird import bird
T = json.load(open("timeline.json"))
poses = ["default","happy","surprised","wrong","thinking"]
birds = "".join(f'<div class="pose" data-p="{p}">{bird(p, "s"+p)}</div>' for p in poses)
birdsBig = "".join(f'<div class="pose" data-p="{p}">{bird(p, "b"+p)}</div>' for p in poses)
CAP = {
 "h1": "Koreans have <b class=k>TWO</b> completely different ways to count...",
 "h2": "...and they use <b class=k>BOTH</b> in the same sentence.",
 "n0": "Way one: <b class=p>native Korean</b>.",
 "s0": "Way two: <b class=m>Sino-Korean</b>, borrowed from Chinese.",
 "c0": "So, what time is it? <b class=k>3:30.</b>",
 "c1": "<b class=p>Hours</b> use native Korean,",
 "c3": "but <b class=m>minutes</b> use the Chinese ones.",
 "c6": "<b class=k>Two systems. One sentence.</b>",
 "a0": "Same with your <b class=k>age</b>. With friends, you're",
 "a2": "But at the <b class=m>hospital</b>?",
 "r0": "Easy rule: things, hours and age? <b class=p>Native.</b>",
 "r1": "Money, minutes, dates, phone numbers? <b class=m>Chinese.</b>",
 "e0": "Follow for more <b class=k>Korean in 60s!</b>",
}
KOC = {"n1a":("하나","hana","p"),"n1b":("둘","dul","p"),"n1c":("셋","set","p"),"s1a":("일","il","m"),"s1b":("이","i","m"),"s1c":("삼","sam","m"),
 "c2":("세 시","se si","p"),"c4":("삼십 분","samsip bun","m"),"c5":("세 시 삼십 분!","se si samsip bun","k"),"a1":("스물다섯 살","seumul-daseot sal","p"),"a3":("이십오 세","isib-o se","m")}
caps = [{"k":k,"t0":T[k][0]-0.05,"t1":T[k][1]+0.12,"html":v,"ko":0} for k,v in CAP.items()]
for k,(ko,ro,c) in KOC.items():
    caps.append({"k":k,"t0":T[k][0]-0.05,"t1":T[k][1]+0.18,"html":f'<span class="kor {c}">{ko}</span><span class="rom">{ro}</span>',"ko":1})
html = open("template.html").read().replace("/*TL*/", "const T="+json.dumps(T)+";const CAPS="+json.dumps(caps, ensure_ascii=False)+";").replace("<!--BIRDS-->", birds).replace("<!--BIRDSBIG-->", birdsBig)
open("short.html","w").write(html)
