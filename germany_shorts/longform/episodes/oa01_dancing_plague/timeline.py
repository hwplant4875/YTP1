"""Trim each narration line to its speech, lay lines out with ~0.45 s gaps, derive shot lengths and word timings."""
import json, os, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from script import LINES
C = os.path.join(HERE, ".cache")
GAP, LEAD, TAILK, START = 0.45, 0.03, 0.16, 0.12

def load(i):
    w = os.path.join(C, f"l{i:02d}.wav")
    if not os.path.exists(w):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(C, f"l{i:02d}.mp3"), "-ac", "1", "-ar", "48000", w], check=True)
    with wave.open(w) as f: x = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
    return x

lines, t = [], START
for i, (say, cap, shots) in enumerate(LINES):
    x = load(i); fr = 480
    db = np.array([20 * np.log10(np.sqrt(np.mean(x[k:k + fr] ** 2)) + 1e-9) for k in range(0, len(x) - fr, fr)])
    loud = np.where(db > -42)[0]; a, b = loud[0] / 100, (loud[-1] + 1) / 100
    a0, b0 = max(0, a - LEAD), min(len(x) / 48000, b + TAILK)
    al = json.load(open(os.path.join(C, f"l{i:02d}.json")))
    # word timings from character alignment
    words, cur, ws = [], "", None
    for ch, s0, s1 in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch == " ":
            if cur: words.append([cur, ws, prev_end]); cur = ""
            continue
        if not cur: ws = s0
        cur += ch; prev_end = s1
    if cur: words.append([cur, ws, prev_end])
    words = [[w, t + max(0, s - a0), t + max(0, e - a0)] for w, s, e in words]
    lines.append({"i": i, "say": say, "cap": cap or say, "start": t, "trim": [a0, b0], "dur": b0 - a0, "words": words, "shots": shots})
    t += (b0 - a0) + GAP
total = t - GAP + 1.2   # tail: hold the last shot while voice and music fade
# shot spans: a line's shots cover from its start (first line: from 0) to the next line's start
spans = []
for k, L in enumerate(lines):
    s = 0.0 if k == 0 else L["start"]; e = lines[k + 1]["start"] if k + 1 < len(lines) else total
    s0 = s
    for j, (name, share) in enumerate(L["shots"]):
        d = (e - s0) * share if j < len(L["shots"]) - 1 else e - s
        spans.append({"shot": name, "start": round(s, 3), "dur": round(d, 3)}); s += d
json.dump({"lines": lines, "spans": spans, "total": total}, open(os.path.join(HERE, "timeline.json"), "w"), indent=1)
for sp in spans: print(f'{sp["start"]:6.2f} {sp["dur"]:5.2f} {sp["shot"]}')
print("total", round(total, 2), "words/s", round(sum(len(l["say"].split()) for l in lines) / sum(l["dur"] for l in lines), 2))
