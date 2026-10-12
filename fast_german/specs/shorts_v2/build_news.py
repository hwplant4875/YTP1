"""Fast German NEWS shorts, round 2 (user 2026-10-12 feedback):
- hook in the first second: the news itself, said as a statement, with a big first-frame title
- real source pictures found by image search, a different picture for every beat (never reused in a short)
- every caption sits directly under its picture
- max ~0.5 s silence between sentences ("tight"), first graphic pops at 0 s
Writes n01..n05 json specs for lib/short_v2.py."""
import json, os
from PIL import Image
HERE = os.path.dirname(__file__)
PH = "/mnt/project-files/fast_german/cache/photos/"
E3 = "/mnt/project-files/fast_german/cache/emoji3d/"
Y, RED, GREEN, BLUE, ORANGE = [255, 204, 0], [235, 64, 52], [52, 199, 89], [64, 156, 255], [255, 140, 26]
BASE = {"music": "/mnt/project-files/fast_german/cache/music/kpop_beat_c.mp3", "bg": "road", "tight": 0.5}
FOLLOW = {"lines": [[{"en": "Follow for more German news."}]],
          "els": [{"id": "l", "type": "logo", "x": 540, "y": 740}, {"id": "t", "type": "text", "text": "Follow for more German", "size": 70, "x": 540, "y": 1000}]}
TOP = 290      # pictures start under the pretzel badge


def P(i, src, top=TOP, w=960, maxh=760):
    """Picture in a white card, aspect kept (cover-cropped past maxh). Returns (element, bottom edge y)."""
    iw, ih = Image.open(PH + "news2/" + src).size
    h = min(maxh, max(int(w * ih / iw), 620))     # wide shots get a fuller 3:2 crop, not a thin strip
    return {"id": i, "type": "photo", "src": "news2/" + src, "w": w, "h": h, "x": 540, "y": top + 10 + h // 2}, top + h + 20


def T(i, text, y, size=78, colour=None, x=540):
    d = {"id": i, "type": "text", "text": text, "size": size, "x": x, "y": y}
    if colour: d["colour"] = colour
    return d


def Wd(i, de, y, size=170, colour=None):
    d = {"id": i, "type": "word", "de": de, "size": size, "x": 540, "y": y}
    if colour: d["colour"] = colour
    return d


def under(bottom, size, gap=28):
    """Centre y for a line of text of this size placed right under a picture (or the line above)."""
    return int(bottom + gap + size * 0.62)


def shot(i, src, caps, top=TOP, w=960, maxh=760):
    """A picture plus captions stacked right under it. caps = [(id, kind, text, size, colour)]"""
    p, b = P(i, src, top, w, maxh)
    els = [p]
    for cid, kind, text, size, col in caps:
        y = under(b, size)
        els.append(Wd(cid, text, y, size, col) if kind == "w" else T(cid, text, y, size, col))
        b = y + int(size * 0.62)
    return els


# 1 ─ Weimar onion market ────────────────────────────────────────────────────────────────────────
onion = {"id": "n01_zwiebelmarkt", "title": "This German town crowns a queen… for ONIONS 🧅👑", "scenes": [
 {"lines": [[{"en": "This German town crowns a queen... for onions.", "show": ["p", "t"]}]],
  "els": shot("p", "on_queen_user.png", [("t", "t", "The ONION QUEEN", 96, Y)], maxh=740)},
 {"lines": [[{"en": "In German, she's the", "show": ["p"]}, {"de": "Zwiebelkönigin.", "show": ["w", "m"]}]],
  "els": shot("p", "onq_3.jpg", [("w", "w", "Zwiebelkönigin", 150, Y), ("m", "t", "= onion queen", 66, None)])},
 {"lines": [[{"en": "She rules over the", "show": ["p"]}, {"de": "Zwiebelmarkt,", "show": ["w"]}, {"en": "the onion market in Weimar.", "show": ["m"]}]],
  "els": shot("p", "onc_6.jpg", [("w", "w", "Zwiebelmarkt", 160, None), ("m", "t", "= onion market · Weimar", 66, Y)])},
 {"lines": [[{"en": "This weekend, about 250,000 people came", "show": ["p", "n"]}, {"en": "to buy onion braids like these.", "show": ["q", "b"], "hide": ["p", "n"]}]],
  "els": shot("p", "onc_11.jpg", [("n", "t", "250,000 visitors", 100, Y)]) + shot("q", "onb_0.jpg", [("b", "t", "Onion braids", 100, Y)])},
 {"lines": [[{"en": "And cute little onion dolls.", "show": ["p", "t"]}]],
  "els": shot("p", "on_dolls_user.png", [("t", "t", "Onion dolls", 96, None)])},
 {"lines": [[{"en": "And it's old. The first one was in 1653.", "show": ["p", "y"]}]],
  "els": shot("p", "on_stall_user.png", [("y", "w", "since 1653", 170, Y)])},
 {"lines": [[{"en": "This was number 373.", "show": ["p", "k"]}], [{"en": "Would you go?", "show": ["q"]}]],
  "els": shot("p", "onq_12.jpg", [("k", "t", "The 373rd onion market", 80, None), ("q", "t", "Would you go?", 96, Y)])},
 FOLLOW]}

# 2 ─ Jugendwort 2026: Ragebait ──────────────────────────────────────────────────────────────────
rows = [{"id": "r1", "type": "row", "icon": "1st-place-medal", "de": "Ragebait", "en": "36.5 %", "colour": RED, "w": 820, "x": 500, "y": 700},
        {"id": "r2", "type": "row", "icon": "2nd-place-medal", "de": "Peak", "en": "33.8 %", "colour": BLUE, "w": 820, "x": 500, "y": 980},
        {"id": "r3", "type": "row", "icon": "3rd-place-medal", "de": "Crashout", "en": "29.7 %", "colour": ORANGE, "w": 820, "x": 500, "y": 1260}]
rage = {"id": "n02_ragebait", "title": "Germany's word of the year 2026 is… ENGLISH 😳", "scenes": [
 {"lines": [[{"en": "Germany's youth word of the year isn't even German.", "show": ["p", "t"]}]],
  "els": shot("p", "rgb_8.jpg", [("t", "t", "Youth word of the year 2026", 76, Y)])},
 {"lines": [[{"en": "It's Ragebait.", "show": ["p", "w"]}]],
  "els": shot("p", "rg_lion_user.png", [("w", "w", "Ragebait", 210, RED)])},
 {"lines": [[{"en": "Posts made just to make you angry.", "show": ["p", "m"]}]],
  "els": shot("p", "rgb_5.jpg", [("m", "t", "= posts made to make you angry", 64, None)])},
 {"lines": [[{"en": "About one million teenagers voted.", "show": ["p", "v"]}]],
  "els": shot("p", "rgp_10.jpg", [("v", "t", "~1,000,000 votes", 100, Y)])},
 {"lines": [[{"en": "First, Ragebait.", "show": ["r1"], "join": 0.35}, {"en": "Then Peak.", "show": ["r2"], "join": 0.35}, {"en": "Then Crashout.", "show": ["r3"]}],
            [{"en": "All three: English.", "show": ["x"]}]],
  "els": [T("v", "Top 3", 430, 96, Y)] + rows + [T("x", "All English!", 1450, 90, RED)]},
 {"lines": [[{"en": "So what's the German word?", "show": ["p"]}, {"de": "Wut-Köder.", "show": ["w"]}], [{"en": "Literally, rage bait.", "show": ["m"]}]],
  "els": shot("p", "rg_wut_user.png", [("w", "w", "Wut-Köder", 190, Y), ("m", "t", "= rage + bait", 70, None)])},
 FOLLOW]}

# 3 ─ Oktoberfest record ─────────────────────────────────────────────────────────────────────────
okt = {"id": "n03_oktoberfest", "title": "Oktoberfest 2026 broke its ALL-TIME record 🍺", "scenes": [
 {"lines": [[{"en": "Oktoberfest 2026 just broke its all-time record.", "show": ["h", "p", "t", "f"]}]],
  "els": [T("h", "OKTOBERFEST 2026", 330, 104, Y)] + shot("p", "okr_7.jpg", [("t", "t", "New all-time record", 80, None)], top=400, maxh=700)
         + [{"id": "f", "type": "tile", "png": E3 + "party_popper.png", "s": 130, "x": 0, "y": 0}]},
 {"lines": [[{"en": "7.4 million visitors.", "show": ["p", "n"]}], [{"en": "The old record was 7.2 million.", "show": ["o"]}]],
  "els": shot("p", "okp_11.jpg", [("n", "w", "7,400,000", 190, Y), ("o", "t", "old record: 7.2 million", 70, None)])},
 {"lines": [[{"en": "They drank 6.7 million", "show": ["p"]}, {"de": "Maß.", "show": ["w"], "join": 0.05}], [{"en": "That's a one-litre beer mug.", "show": ["m"]}]],
  "els": shot("p", "okm_3.jpg", [("w", "w", "die Maß", 180, Y), ("m", "t", "= 1-litre beer mug", 72, None)])},
 {"lines": [[{"en": "And one", "show": ["p"]}, {"de": "Maß", "show": ["n"], "join": 0.05}, {"en": "now costs up to 15.90 euros.", "show": ["e"]}]],
  "els": shot("p", "okp_8.jpg", [("n", "t", "1 Maß =", 84, None), ("e", "w", "€15.90", 190, Y)])},
 {"lines": [[{"en": "Also, alcohol-free beer sales went up almost eleven percent.", "show": ["p", "a", "n"]}]],
  "els": shot("p", "okz_3.jpg", [("a", "t", "Alcohol-free beer", 84, None), ("n", "w", "+10.7 %", 190, GREEN)], maxh=700)},
 FOLLOW]}
_t = next(e for e in okt["scenes"][0]["els"] if e["id"] == "t")       # 🎉 right of "New all-time record"
_f = okt["scenes"][0]["els"][-1]
_f["x"], _f["y"] = 940, _t["y"]
_t["x"] = 480

# 4 ─ Deutsche Bahn alcohol ban ──────────────────────────────────────────────────────────────────
beer_x = {"id": "bx", "type": "tile", "png": E3 + "beer.png", "cross": E3 + "cross.png", "s": 300, "x": 340, "y": 1000}
wine_x = {"id": "wx", "type": "tile", "png": E3 + "wine.png", "cross": E3 + "cross.png", "s": 300, "x": 740, "y": 1000}
db = {"id": "n04_bahn_alkoholverbot", "title": "From Oct 15: NO alcohol at German train stations 🚫🍺", "scenes": [
 {"lines": [[{"en": "From October 15, you can't drink alcohol at German train stations.", "show": ["p", "t"]}]],
  "els": shot("p", "dbs_2.jpg", [("t", "t", "BANNED from Oct 15", 96, RED)])},
 {"lines": [[{"en": "No beer.", "show": ["bx"], "join": 0.35}, {"en": "No wine.", "show": ["wx"]}], [{"en": "Germans call it", "show": []}, {"de": "Alkoholverbot.", "show": ["w", "m"]}]],
  "els": [beer_x, wine_x, Wd("w", "Alkoholverbot", 1330, 150, Y), T("m", "= alcohol ban", 1460, 64)]},
 {"lines": [[{"en": "It covers 5,400 stations.", "show": ["p", "n"]}]],
  "els": shot("p", "dba_4.jpg", [("n", "t", "5,400 stations", 100, Y)])},
 {"lines": [[{"en": "But station bars and restaurants are fine.", "show": ["p", "a"]}],
            [{"en": "Closed bottles in your bag are fine.", "show": ["q", "b"], "hide": ["p", "a"]}],
            [{"en": "And on the train itself, you can still drink.", "show": ["r", "c"], "hide": ["q", "b"]}]],
  "els": shot("p", "dbr_9.jpg", [("a", "t", "OK: station bars", 90, GREEN)]) + shot("q", "dbb_8.jpg", [("b", "t", "OK: closed bottles", 90, GREEN)])
         + shot("r", "dbz_10.jpg", [("c", "t", "OK: on the train", 90, GREEN)])},
 {"lines": [[{"en": "Break the rule, and you'll be asked to leave.", "show": ["p", "x"]}],
            [{"en": "Do it again, and you can be banned.", "show": ["q", "y"], "hide": ["p", "x"]}]],
  "els": shot("p", "dbp_2.jpg", [("x", "t", "1st time: leave the station", 72, None)]) + shot("q", "dba_6.jpg", [("y", "t", "Again: banned", 100, RED)])},
 FOLLOW]}

# 5 ─ Clocks go back ─────────────────────────────────────────────────────────────────────────────
zeit = {"id": "n05_zeitumstellung", "title": "Germany gets a 25-HOUR day this month ⏰", "scenes": [
 {"lines": [[{"en": "This month, Germany gets a 25-hour day.", "show": ["p", "t"]}]],
  "els": shot("p", "zu_0.jpg", [("t", "w", "25 hours", 180, Y)])},
 {"lines": [[{"en": "On Sunday, October 25th, at 3 a.m.,", "show": ["d", "a"]}, {"en": "the clocks go back to 2 a.m.", "show": ["ar", "b"]}]],
  "els": [T("d", "Sunday, Oct 25", 420, 90, Y), Wd("a", "3:00", 760, 260), {"id": "ar", "type": "tile", "icon": "down-arrow", "s": 150, "x": 540, "y": 980},
          Wd("b", "2:00", 1200, 260, Y)]},
 {"lines": [[{"en": "In German, it's the", "show": ["p"]}, {"de": "Zeitumstellung.", "show": ["w", "m"]}]],
  "els": shot("p", "zu_1.jpg", [("w", "w", "Zeitumstellung", 150, None), ("m", "t", "= the time change", 66, Y)])},
 {"lines": [[{"en": "And winter time is", "show": ["p"]}, {"de": "Winterzeit.", "show": ["w", "m"]}]],
  "els": shot("p", "zu_4.jpg", [("w", "w", "Winterzeit", 170, Y), ("m", "t", "= winter time", 66, None)])},
 {"lines": [[{"en": "So enjoy one extra hour of sleep.", "show": ["p", "o"]}, {"de": "Gute Nacht!", "show": ["g"]}]],
  "els": shot("p", "zw_6.jpg", [("o", "t", "+1 hour of sleep", 96, Y), ("g", "w", "Gute Nacht!", 160, None)])},
 FOLLOW]}

for d in (onion, rage, okt, db, zeit):
    json.dump({**d, **BASE}, open(os.path.join(HERE, d["id"] + ".json"), "w"), indent=1, ensure_ascii=False)
