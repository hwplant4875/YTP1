"""Fast German spectacle-hook shorts (user 2026-10-16): open on the most striking real footage at 0 s, then explain.
Footage fills the frame (3:4 or 9:16) with its own sound under the voice; picture framed to leave out the outlet's burned-in
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


def F(i, src, start, dur, crop, w=1080, h=1920, vol=0, grade=None):
    """Footage filling the whole 9:16 frame (user 2026-10-18: no asphalt or pretzel showing, no source sound)."""
    d = {"id": i, "type": "video", "full": True, "src": SRC + src, "start": start, "dur": dur, "crop": list(crop),
         "w": w, "h": h, "x": 540, "y": 960, "vol": vol}
    if grade: d["grade"] = grade
    return d


def T(i, text, y, size=78, colour=None):
    d = {"id": i, "type": "text", "text": text, "size": size, "x": 540, "y": y}
    if colour: d["colour"] = colour
    return d


def Wd(i, de, y, size=170, colour=None):
    d = {"id": i, "type": "word", "de": de, "size": size, "x": 540, "y": y}
    if colour: d["colour"] = colour
    return d


def caps(items, bottom=1490):
    """Captions stacked upward from the bottom of the footage, clear of the Shorts title area (y > 1540)."""
    els, y = [], bottom
    for cid, kind, text, size, col in reversed(items):
        cy = int(y - size * 0.62)
        els.append(Wd(cid, text, cy, size, col) if kind == "w" else T(cid, text, cy, size, col))
        y = cy - int(size * 0.62) - 18
    return els[::-1]


def shot(i, src, start, items, x0=150, dur=6, speed=None):
    f = F(i, src, start, dur, (x0, 230, 304, 540))
    if speed: f["speed"] = speed
    return [f] + caps(items)     # 9:16 window between the StZ logo and subtitles


R = "WNdEpxh65Lo.mp4"   # Stuttgarter Zeitung, Kürbisregatta Ludwigsburg 19/20 Sept 2026 (608x1080)
# Script (user 2026-10-18 "study viral scripts"): visual hook said as a statement, an open loop in line 2 that pays off
# in line 4, one idea per line, no filler scene, and an ending question that loops back to the opening pumpkin.
regatta = {"id": "s01_kuerbisregatta", "title": "Germans race across a lake… in GIANT PUMPKINS 🎃", "badge": False, "scenes": [
 {"lines": [[{"en": "This is a real race in Germany, and the boats are giant pumpkins.", "show": ["h", "p"]}]],
  "els": shot("p", R, 39.0, [], x0=160, dur=5) + [T("h", "They race in PUMPKINS", 380, 96, Y)]},
 {"lines": [[{"en": "But the hardest part isn't the paddling.", "show": ["p", "n"]}]],
  "els": shot("p", R, 11.0, [("n", "t", "The hardest part?", 96, Y)], x0=120, dur=4)},
 {"lines": [[{"en": "It's the", "show": ["p"]}, {"de": "Kürbisregatta,", "show": ["w"]}, {"en": "the pumpkin regatta in Ludwigsburg.", "show": ["m"]}]],
  "els": shot("p", R, 4.0, [("w", "w", "Kürbisregatta", 160, Y), ("m", "t", "= pumpkin regatta · Ludwigsburg", 62, None)], x0=0, dur=5)},
 {"lines": [[{"en": "It's getting in. These pumpkins weigh over 350 kilos,", "show": ["p", "n"]}, {"en": "and people flip over before the race even starts.", "show": ["f"]}]],
  "els": shot("p", R, 22.0, [("n", "w", "350+ kg", 190, Y), ("f", "t", "...and people flip over", 72, None)], x0=140, dur=7.4)},
 {"lines": [[{"en": "And it all started as a", "show": ["p"]}, {"de": "Schnapsidee,", "show": ["w"]}, {"en": "a crazy idea you only have after a drink.", "show": ["m"]}]],
  "els": shot("p", R, 44.4, [("w", "w", "Schnapsidee", 170, Y), ("m", "t", "= a crazy idea", 70, None)], x0=170, dur=5.6, speed=0.4)},
 {"lines": [[{"en": "Twenty-three years later, hundreds of people come to watch.", "show": ["p", "n"]}]],
  "els": shot("p", R, 33.0, [("n", "t", "23 years later", 90, None)], x0=200, dur=7)},
 {"lines": [[{"en": "So, would you climb into a", "show": ["p", "q"]}, {"de": "Kürbis?", "show": ["w", "m"]}]],
  "els": shot("p", R, 18.0, [("q", "t", "Would you climb in?", 90, Y), ("w", "w", "der Kürbis", 160, None), ("m", "t", "= pumpkin", 66, None)], dur=4)}]}

for d in (regatta,):
    json.dump({**d, **BASE}, open(os.path.join(HERE, d["id"] + ".json"), "w"), indent=1, ensure_ascii=False)
