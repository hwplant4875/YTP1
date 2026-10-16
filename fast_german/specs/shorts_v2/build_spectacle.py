"""Fast German spectacle-hook shorts (user 2026-10-16): open on the most striking real footage at 0 s, then explain.
Footage plays in the white card with its own sound under the voice; picture framed to leave out the outlet's burned-in
subtitles and logo (plain crop, nothing erased). Writes s01.. json specs for lib/short_v2.py."""
import json, os
HERE = os.path.dirname(__file__)
SRC = "/home/user/fg_src/"
Y, GREEN = [255, 204, 0], [52, 199, 89]
BASE = {"music": "/mnt/project-files/fast_german/cache/music/kpop_beat_c.mp3", "bg": "road", "tight": 0.5}
FOLLOW = {"lines": [[{"en": "Follow for more German."}]],
          "els": [{"id": "l", "type": "logo", "x": 540, "y": 740}, {"id": "t", "type": "text", "text": "Follow for more German", "size": 70, "x": 540, "y": 1000}]}


def V(i, src, start, top=290, w=960, h=774, crop=(0, 230, 608, 490), dur=6, vol=0.28):
    return {"id": i, "type": "video", "src": SRC + src, "start": start, "dur": dur, "crop": list(crop), "w": w, "h": h,
            "x": 540, "y": top + 10 + h // 2, "vol": vol}, top + h + 20


def T(i, text, y, size=78, colour=None):
    d = {"id": i, "type": "text", "text": text, "size": size, "x": 540, "y": y}
    if colour: d["colour"] = colour
    return d


def Wd(i, de, y, size=170, colour=None):
    d = {"id": i, "type": "word", "de": de, "size": size, "x": 540, "y": y}
    if colour: d["colour"] = colour
    return d


def shot(i, src, start, caps, top=290, **kw):
    v, b = V(i, src, start, top, **kw)
    els = [v]
    for cid, kind, text, size, col in caps:
        y = int(b + 28 + size * 0.62)
        els.append(Wd(cid, text, y, size, col) if kind == "w" else T(cid, text, y, size, col))
        b = y + int(size * 0.62)
    return els


R = "WNdEpxh65Lo.mp4"   # Stuttgarter Zeitung, Kürbisregatta Ludwigsburg 19/20 Sept 2026 (608x1080)
regatta = {"id": "s01_kuerbisregatta", "title": "Germans race across a lake… in GIANT PUMPKINS 🎃", "scenes": [
 {"lines": [[{"en": "In Germany, people race across a lake... sitting inside giant pumpkins.", "show": ["h", "p"]}]],
  "els": [T("h", "They race in PUMPKINS", 330, 92, Y)] + shot("p", R, 39.4, [], top=400, h=700, crop=(0, 250, 608, 455))},
 {"lines": [[{"en": "It's the", "show": ["p"]}, {"de": "Kürbisregatta,", "show": ["w"]}, {"en": "the pumpkin regatta in Ludwigsburg.", "show": ["m"]}]],
  "els": shot("p", R, 12.0, [("w", "w", "Kürbisregatta", 160, Y), ("m", "t", "= pumpkin regatta · Ludwigsburg", 62, None)])},
 {"lines": [[{"en": "Sixty racers took on the palace lake.", "show": ["p", "n"]}]],
  "els": shot("p", R, 6.4, [("n", "t", "60 racers", 110, Y)])},
 {"lines": [[{"en": "This year, the pumpkins weighed over 350 kilos,", "show": ["p", "n"]}, {"en": "so some racers flipped over just getting in.", "show": ["f"]}]],
  "els": shot("p", R, 20.6, [("n", "w", "350+ kg", 190, Y), ("f", "t", "...and some flipped over", 72, None)], dur=8)},
 {"lines": [[{"en": "And it all started as a", "show": ["p"]}, {"de": "Schnapsidee,", "show": ["w"]}, {"en": "a crazy idea you only have after a drink.", "show": ["m"]}]],
  "els": shot("p", R, 26.8, [("w", "w", "Schnapsidee", 170, Y), ("m", "t", "= a crazy idea", 70, None)], dur=7)},
 {"lines": [[{"en": "Now it's the 23rd year, and hundreds of people come to watch.", "show": ["p", "n"]}]],
  "els": shot("p", R, 32.6, [("n", "t", "23rd pumpkin regatta", 84, None)], dur=7)},
 {"lines": [[{"en": "Would you get in?", "show": ["p", "q"]}, {"de": "Kürbis", "show": ["w"]}, {"en": "means pumpkin.", "show": ["m"]}]],
  "els": shot("p", R, 45.0, [("q", "t", "Would you get in?", 90, Y), ("w", "w", "der Kürbis", 160, None), ("m", "t", "= pumpkin", 66, None)])},
 FOLLOW]}

for d in (regatta,):
    json.dump({**d, **BASE}, open(os.path.join(HERE, d["id"] + ".json"), "w"), indent=1, ensure_ascii=False)
