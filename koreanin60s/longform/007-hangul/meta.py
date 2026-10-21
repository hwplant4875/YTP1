"""Captions + upload metadata from timeline.json. Usage: python3 meta.py <outdir> -> captions.srt, meta.json (title A), metadata.md"""
import json, re, sys
out = sys.argv[1]; T = json.load(open(f"{out}/timeline.json")); ev = T["ev"]
def ts(s):
    ms = int(round(s * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
cues = []
for a, b, txt in T["cues"]:  # split long sentences at commas/periods so a cue stays short on screen
    parts = [p.strip() for p in re.split(r"(?<=[,.])\s+", txt) if p.strip()]
    tot = sum(len(p) for p in parts); t = a
    for p in parts:
        d = (b - a) * len(p) / tot; cues.append((t, t + d - 0.02, p)); t += d
open(f"{out}/captions.srt", "w").write("\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{x}\n" for i, (a, b, x) in enumerate(cues, 1)))
mm = lambda s: f"{int(s) // 60}:{int(s) % 60:02d}"
ch = [f"{'0:00' if i == 0 else mm(e['t'] + 0.3)} {e['q']}" for i, e in enumerate(x for x in ev if x.get("q"))]
L = mm(T["END"]).split(":")[0]
TITLES = [f"Learn the Korean Alphabet in {L} Minutes", f"Read Korean in {L} Minutes (Even If You Know Nothing)", "Hangul Is the Easiest Alphabet in the World"]
desc = f"""Learn to read Korean from zero. Hangul was made in 1443 so that anyone could learn it in a morning, and by the end of this video you'll read real words like 커피, 김치 and 서울 on your own.

{chr(10).join(ch)}

✍️ Write your name in Hangul in the comments!
Subscribe for Korean you can actually use 💌

Photo: Statue of King Sejong, Republic of Korea (Korea.net), CC BY-SA 2.0. Hunminjeongeum Haerye (1446), public domain.

#learnkorean #hangul #koreanalphabet"""
tags = ["learn korean", "korean alphabet", "hangul", "how to read korean", "learn hangul", "korean for beginners", "korean lesson", "read korean",
        "hangeul", "korean letters", "korean in 60s", "learn korean fast", "korean vowels", "korean consonants", "king sejong"]
json.dump({"title": TITLES[0], "description": desc, "tags": tags}, open(f"{out}/meta.json", "w"), ensure_ascii=False, indent=1)
open(f"{out}/metadata.md", "w").write("# Titles (A/B)\n" + "\n".join(f"- 7{c}: {t}" for c, t in zip("abc", TITLES)) + f"\n\n# Description\n\n{desc}\n\n# Tags\n{', '.join(tags)}\n")
print("\n".join(TITLES)); print("\n".join(ch))
