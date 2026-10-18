"""Captions + upload metadata from timeline.json. Usage: python3 meta.py <outdir> -> captions.srt, meta.json (title A), metadata.md"""
import json, os, re, sys
out = sys.argv[1]; T = json.load(open(f"{out}/timeline.json")); ev = T["ev"]
def ts(s):
    ms = int(round(s * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
cues = []
for a, b, txt in T["cues"]:  # split long sentences at commas so a cue stays short on screen
    parts = [p.strip() for p in re.split(r"(?<=,)\s+", txt) if p.strip()]
    tot = sum(len(p) for p in parts); t = a
    for p in parts:
        d = (b - a) * len(p) / tot; cues.append((t, t + d - 0.02, p)); t += d
open(f"{out}/captions.srt", "w").write("\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{x}\n" for i, (a, b, x) in enumerate(cues, 1)))
srcs = []
for e in ev:
    for x in re.split(r" / | · ", e.get("src") or ""):
        if x and x not in srcs: srcs.append(x)
IMGS = ", ".join(srcs).replace("Ethan Doyle White, CC BY-SA 4.0", "National Museum of Korea photo: Ethan Doyle White (CC BY-SA 4.0)")
mm = lambda s: f"{int(s) // 60}:{int(s) % 60:02d}"
ch = [f"{'0:00' if i == 0 else mm(e['t'] + 0.3)} {e['q']}" for i, e in enumerate(x for x in ev if x.get("q"))]
outro = next(e for e in ev if e.get("ch") == 9); ch.append(f"{mm(outro['t'])} What's your favorite moment?")
TITLES = ["The Entire History of KPop Demon Hunters in 7 Minutes", "Every Record KPop Demon Hunters Broke in Its First Year", "How KPop Demon Hunters Went From Netflix to 2 Oscars in 1 Year"]
desc = f"""One year ago, almost nobody had heard of HUNTR/X. Then a cartoon girl group topped the Billboard Hot 100, packed theaters for a sing-along, became Netflix's most-watched movie ever and won two Oscars. Here's the whole year of KPop Demon Hunters, from its quiet Netflix release to the sequel and the world tour.

{chr(10).join(ch)}

Subscribe for Korea news and Korean you can actually use 💌

Sources: Netflix Tudum, Billboard, Official Charts, The Hollywood Reporter, Deadline, Variety, Korea JoongAng Daily, The Korea Times, Euronews, What's on Netflix, Collider, Travel And Tour World, Wikipedia.
Images (news commentary): {IMGS}.
This video is an independent recap and is not affiliated with Netflix or Sony Pictures Animation.

#kpopdemonhunters #huntrix #golden #netflix #korean"""
tags = ["kpop demon hunters", "kpop demon hunters recap", "huntrix", "golden huntrix", "kpop demon hunters oscars", "kpop demon hunters 2", "saja boys", "ejae",
        "kpop demon hunters world tour", "netflix most watched", "kpop demon hunters one year", "korean in 60s", "learn korean", "k-pop news"]
json.dump({"title": TITLES[0], "description": desc, "tags": tags}, open(f"{out}/meta.json", "w"), ensure_ascii=False, indent=1)
md = f"""# Long-form #4: KPop Demon Hunters, one year recap ({mm(T['END'])})

## Titles (A/B test)
- 4a: {TITLES[0]}
- 4b: {TITLES[1]}
- 4c: {TITLES[2]}

## Thumbnails
- 4a.jpg (1 YEAR LATER, HUNTR/X 3D still), 4b.jpg (A CARTOON BEAT K-POP? #1 badge + arrow), 4c.jpg (NETFLIX → OSCARS IN 1 YEAR, real Oscars photo)

## Description
{desc}

## Tags
{", ".join(tags)}

## Pinned comment idea
What was YOUR favorite KPop Demon Hunters moment this year? 🏆 Mine: "Golden" winning the Oscar 🥹
"""
open(f"{out}/metadata.md", "w").write(md); print(len(cues), "cues;", len(desc), "chars"); print("\n".join(ch))
