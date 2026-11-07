"""Word timings from the ElevenLabs character alignment of each beat take.
usage: python3 tools/words.py [beat ...]   -> prints words with take-local start/end"""
import json, sys, re
D = "/mnt/project-files/plans/peek/longform/ep_money/audio/takes/"
def words(bid):
    d = json.load(open(D + bid + ".json"))
    a = d["alignment"]; ch = a["characters"]; st = a["character_start_times_seconds"]; en = a["character_end_times_seconds"]
    out, cur, s0 = [], "", None
    for c, s, e in zip(ch, st, en):
        if c.isspace():
            if cur: out.append((cur, s0, pe)); cur = ""
            continue
        if not cur: s0 = s
        cur += c; pe = e
    if cur: out.append((cur, s0, pe))
    return out
if __name__ == "__main__":
    ids = sys.argv[1:] or [f"b{i:02d}" for i in range(1, 11)]
    for b in ids:
        w = words(b)
        print(f"== {b}  speech {w[0][1]:.2f}-{w[-1][2]:.2f}")
        print("  ".join(f"{t}@{s:.2f}" for t, s, e in w))
