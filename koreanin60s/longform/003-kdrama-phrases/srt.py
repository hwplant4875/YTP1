"""Captions (.srt) from timeline.json. Usage: python3 srt.py <outdir> -> captions.srt"""
import json, os, sys
sys.path.insert(0, os.path.abspath(os.environ.get("SET", os.path.dirname(os.path.abspath(__file__)))))
from phrases import HOOK, OUTRO, NUM
out = sys.argv[1]; ev = json.load(open(f"{out}/timeline.json"))["ev"]
def ts(s):
    ms = int(round(s * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
cues = []
for e in ev:
    if e["k"] == "hook": cues.append((0.3, e["t1"], HOOK))
    elif e["k"] == "chapter": cues.append((e["t"] + 0.2, e["t1"], f"Chapter {NUM[e['i'] - 1]}: {e['title']}"))
    elif e["k"] == "phrase" and e.get("parts"):
        cues += [(e["t"] + 0.35, e["reveal"] - 0.05, " + ".join(f"{q[2]} ({q[1]})" for q in e["parts"]) + " = ?"),
                 (e["reveal"], e["t1"] - 0.4, f"{e['ko']} ({e['rom']}) = {e['en']}")]
    elif e["k"] == "phrase":
        cues += [(e["t"] + 0.35, e["reveal"] - 0.05, e["en"]), (e["reveal"], e["slow"] - 0.05, f"{e['ko']} ({e['rom']})"),
                 (e["slow"], e["t1"] - 0.4, f"{e['ko']} ({e['rom']})")]
    elif e["k"] == "outro": cues.append((e["t"] + 0.2, e["t1"], OUTRO))
open(f"{out}/captions.srt", "w").write("\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n" for i, (a, b, txt) in enumerate(cues, 1)))
print(len(cues))
