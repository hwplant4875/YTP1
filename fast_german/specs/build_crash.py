"""Learn German A1 in 25 Minutes: chapters of narration, repeat-after-me and quiz slides."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from longform import slide, build, LIGHT
HERE = os.path.dirname(__file__)
spec = json.load(open(os.path.join(HERE, "a1_crash_course.json")))
NAR = {"speed": 0.92}
DE = {"speed": 0.88}
CH_ICONS = ["rocket", "waving-hand-default", "bust-in-silhouette", "sparkles", "keycap-1", "running-shoe",
            "red-question-mark", "hot-beverage", "train", "alarm-clock", "folded-hands-default", "trophy"]
S = []
nch = len(spec["chapters"])
for ci, ch in enumerate(spec["chapters"]):
    tr = f"{ci + 1}/{nch} · {ch['title']}"
    if ci > 0:
        S.append((lambda ch=ch, ci=ci: slide(LIGHT, top_left="FAST GERMAN", label=f"CHAPTER {ci + 1}", word=ch["title"],
                                             icon=CH_ICONS[ci % len(CH_ICONS)], icon_size=360),
                  [("sfx", "whoosh"), ("sil", 0.4), ("tts", ch["title"], NAR), ("sil", 0.6)]))
    card = None
    for l in ch["lines"]:
        if "say" in l:
            card = l.get("card") or card
            c = card or {}
            S.append((lambda c=c, l=l, tr=tr, ci=ci: slide(LIGHT, top_left="FAST GERMAN", top_right=tr, icon=c.get("icon") or (CH_ICONS[ci] if not c else None),
                                                       word=c.get("de"), article=c.get("article"), en=c.get("en"), caption=l["say"]),
                      [("tts", l["say"], NAR), ("sil", 0.25)]))
        elif "repeat" in l:
            S.append((lambda l=l, tr=tr: slide(LIGHT, top_left="FAST GERMAN", top_right=tr, label="REPEAT AFTER ME", icon=l.get("icon"),
                                               word=l["repeat"], article=l.get("article"), en=l.get("en")),
                      [("sfx", "pop"), ("tts", l["repeat"], DE), ("sil", 3.2), ("tts", l["repeat"], DE), ("sil", 0.8)]))
        elif "quiz" in l:
            S.append((lambda l=l, tr=tr: slide(LIGHT, top_left="FAST GERMAN", top_right=tr, label="QUIZ", word=l["quiz"], icon="thinking-face"),
                      [("sfx", "swoosh_up"), ("tts", l["quiz"], NAR), ("sil", 0.3)]))
            for n in (3, 2, 1):
                S.append((lambda n=n, tr=tr: slide(LIGHT, top_left="FAST GERMAN", top_right=tr, label="QUIZ", big=str(n)),
                          [("sfx", "tick"), ("sil", 0.5)]))
            S.append((lambda l=l, tr=tr: slide(LIGHT, top_left="FAST GERMAN", top_right=tr, label="QUIZ", word=l["answer"],
                                               article=l.get("article"), en=l["quiz"]),
                      [("sfx", "ding"), ("tts", l["answer"], DE), ("sil", 1.2)]))
S.append((lambda: slide(LIGHT, top_left="FAST GERMAN", word="Follow for more German", icon="pretzel"), [("sil", 15.0)]))
print(build(S, sys.argv[1], fps=10, workers=1, crf=22))
