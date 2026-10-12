"""Fast German NEWS shorts (user 2026-10-12): normal news format for foreigners/travellers, real source visuals
(article screenshots, news photos, CC0 photos) in white cards, big facts on screen, Carla narrates in English,
German words spoken in German. Writes n01..n05 json specs for lib/short_v2.py."""
import json, os
from PIL import Image
HERE = os.path.dirname(__file__)
PH = "/mnt/project-files/fast_german/cache/photos/"
Y, RED, GREEN = [255, 204, 0], [229, 72, 77], [52, 199, 89]
BASE = {"music": "/mnt/project-files/fast_german/cache/music/kpop_beat_c.mp3", "bg": "road"}
FOLLOW = {"lines": [[{"en": "Follow for more German news."}]], "hold": 0.8,
          "els": [{"id": "l", "type": "logo", "x": 540, "y": 740}, {"id": "t", "type": "text", "text": "Follow for more German", "size": 70, "x": 540, "y": 1000}]}


def P(i, src, y, w=960, maxh=860):
    """Photo / article screenshot in a white card, aspect kept up to maxh (then cover-cropped)."""
    iw, ih = Image.open(PH + src).size
    return {"id": i, "type": "photo", "src": src, "w": w, "h": min(maxh, int(w * ih / iw)), "x": 540, "y": y}


def T(i, text, y, size=78, colour=None):
    d = {"id": i, "type": "text", "text": text, "size": size, "x": 540, "y": y}
    if colour: d["colour"] = colour
    return d


def Wd(i, de, y, size=170, colour=None):
    d = {"id": i, "type": "word", "de": de, "size": size, "x": 540, "y": y}
    if colour: d["colour"] = colour
    return d


onion = {"id": "n01_zwiebelmarkt", "title": "Germany just threw a festival… for ONIONS 🧅", "scenes": [
 {"lines": [[{"en": "Germany just held a festival... for onions.", "show": ["p", "t"]}]],
  "els": [P("p", "news/onion_photo.jpg", 700), T("t", "A festival for onions?!", 1260, 84, Y)]},
 {"lines": [[{"en": "It's the"}, {"de": "Zwiebelmarkt,", "show": ["w"]}, {"en": "the onion market in Weimar.", "show": ["m"]}]], "hold": 0.2,
  "els": [P("p", "news/onion_fid.jpg", 620), Wd("w", "Zwiebelmarkt", 1210, 170), T("m", "= onion market · Weimar", 1360, 70, Y)]},
 {"lines": [[{"en": "For three days, about 250,000 people came", "show": ["n"]}, {"en": "to buy onion braids.", "show": ["b"]}]], "hold": 0.2,
  "els": [P("p", "news/onion_head.jpg", 680, maxh=820), T("n", "250,000 visitors", 1200, 96, Y), T("b", "3 days of onion braids", 1330, 70)]},
 {"lines": [[{"en": "And it's old. The first one was in 1653.", "show": ["y"]}], [{"en": "This year was number 373.", "show": ["k"]}]], "hold": 0.3,
  "els": [P("p", "news/onion_photo.jpg", 640), Wd("y", "since 1653", 1180, 160, Y), T("k", "373rd onion market", 1340, 72)]},
 {"lines": [[{"en": "Oh, and they crown an onion queen.", "show": ["q"]}], [{"en": "Would you go?"}]], "hold": 0.4,
  "els": [P("p", "news/onion_fid.jpg", 620), Wd("q", "Zwiebelkönigin", 1210, 150, Y), T("m", "= onion queen", 1360, 70)]},
 FOLLOW]}

rage = {"id": "n02_ragebait", "title": "Germany's word of the year 2026 is… ENGLISH 😳", "scenes": [
 {"lines": [[{"en": "Germany's youth word of the year is... not German.", "show": ["p", "t"]}]],
  "els": [P("p", "news/rage_hs.jpg", 720, maxh=900), T("t", "Youth word of the year 2026", 1290, 70, Y)]},
 {"lines": [[{"en": "It's", "show": []}, {"en": "Ragebait.", "show": ["w"]}], [{"en": "Posts made just to make you angry.", "show": ["m"]}]], "hold": 0.2,
  "els": [P("p", "news/rage_zdf.jpg", 640, maxh=680), Wd("w", "Ragebait", 1150, 200, Y), T("m", "= posts made to make you angry", 1320, 64)]},
 {"lines": [[{"en": "About one million teenagers voted.", "show": ["v"]}],
            [{"en": "First, Ragebait.", "show": ["r1"]}, {"en": "Then Peak.", "show": ["r2"]}, {"en": "Then Crashout.", "show": ["r3"]}],
            [{"en": "All three: English.", "show": ["x"]}]], "hold": 0.3,
  "els": [T("v", "~1,000,000 votes", 420, 90, Y),
          {"id": "r1", "type": "row", "icon": "1st-place-medal", "de": "Ragebait", "en": "36.5 %", "hl": True, "x": 540, "y": 680},
          {"id": "r2", "type": "row", "icon": "2nd-place-medal", "de": "Peak", "en": "33.8 %", "x": 540, "y": 960},
          {"id": "r3", "type": "row", "icon": "3rd-place-medal", "de": "Crashout", "en": "29.7 %", "x": 540, "y": 1240},
          T("x", "All English!", 1440, 84, RED)]},
 {"lines": [[{"en": "The official German translation?"}, {"de": "Wut-Köder.", "show": ["w"]}], [{"en": "Rage bait. Literally.", "show": ["m"]}]], "hold": 0.4,
  "els": [P("p", "news/rage_zdf.jpg", 640, maxh=680), Wd("w", "Wut-Köder", 1150, 190, Y), T("m", "= rage bait", 1320, 72)]},
 FOLLOW]}

okt = {"id": "n03_oktoberfest", "title": "Oktoberfest 2026 broke its ALL-TIME record 🍺", "scenes": [
 {"lines": [[{"en": "Oktoberfest 2026 just broke its all-time record.", "show": ["p", "t"]}]],
  "els": [P("p", "news/okt_eu.jpg", 700, maxh=820), T("t", "New all-time record", 1260, 84, Y)]},
 {"lines": [[{"en": "7.4 million visitors.", "show": ["n"]}], [{"en": "The old record was 7.2 million.", "show": ["o"]}]], "hold": 0.2,
  "els": [P("p", "news/okt_crowd.jpg", 680), Wd("n", "7,400,000", 1200, 190, Y), T("o", "old record: 7.2 million", 1370, 70)]},
 {"lines": [[{"en": "They drank 6.7 million"}, {"de": "Maß.", "show": ["w"]}], [{"en": "That's a one-litre beer mug.", "show": ["m"]}]], "hold": 0.2,
  "els": [P("p", "news/okt_waiter.jpg", 680), Wd("w", "die Maß", 1200, 180, Y), T("m", "= 1 litre of beer", 1360, 72)]},
 {"lines": [[{"en": "And one"}, {"de": "Maß", "show": ["n"]}, {"en": "now costs up to 15.90 euros.", "show": ["e"]}]], "hold": 0.3,
  "els": [P("p", "news/okt_stz.jpg", 680, maxh=800), T("n", "1 Maß =", 1200, 80), Wd("e", "€15.90", 1340, 190, Y)]},
 {"lines": [[{"en": "Biggest surprise? Alcohol-free beer sales went up almost eleven percent.", "show": ["a"]}]], "hold": 0.4,
  "els": [P("p", "news/okt_waiter.jpg", 680), T("a", "Alcohol-free beer: +10.7 %", 1260, 80, Y)]},
 FOLLOW]}

db = {"id": "n04_bahn_alkoholverbot", "title": "Going to Germany? NEW train station rule from Oct 15 🚆🍺", "scenes": [
 {"lines": [[{"en": "Travelling to Germany? There's a new rule at train stations.", "show": ["p", "t"]}]],
  "els": [P("p", "news/db_press.jpg", 640), T("t", "New rule from October 15", 1160, 80, Y)]},
 {"lines": [[{"en": "From October 15, no drinking alcohol at all 5,400 stations.", "show": ["n"]}], [{"en": "It's called"}, {"de": "Alkoholverbot.", "show": ["w"]}]], "hold": 0.2,
  "els": [P("p", "news/station_train.jpg", 660), T("n", "5,400 stations", 1100, 96, Y), Wd("w", "Alkoholverbot", 1260, 160), T("m", "= alcohol ban", 1400, 64)]},
 {"lines": [[{"en": "But station restaurants and bars are fine.", "show": ["a"]}], [{"en": "Closed bottles are fine.", "show": ["b"]}],
            [{"en": "And on the train itself, you can still drink.", "show": ["c"]}]], "hold": 0.3,
  "els": [T("h", "Still allowed:", 450, 90, GREEN),
          {"id": "a", "type": "row", "icon": "fork-and-knife-with-plate", "de": "Restaurants", "en": "in the station", "x": 540, "y": 700},
          {"id": "b", "type": "row", "icon": "bottle-with-popping-cork", "de": "Closed bottles", "en": "in your bag", "x": 540, "y": 980},
          {"id": "c", "type": "row", "icon": "high-speed-train", "de": "On the train", "en": "yes, really", "x": 540, "y": 1260}]},
 {"lines": [[{"en": "Break the rule, and you'll be asked to leave.", "show": ["x"]}], [{"en": "Do it again, and you can be banned.", "show": ["y"]}]], "hold": 0.4,
  "els": [P("p", "news/db_eu.jpg", 660, maxh=760), T("x", "1st time: leave the station", 1150, 70), T("y", "Again: banned", 1280, 90, RED)]},
 FOLLOW]}

zeit = {"id": "n05_zeitumstellung", "title": "Germany gets a 25-HOUR day this month ⏰", "scenes": [
 {"lines": [[{"en": "This month, Germany gets a 25-hour day.", "show": ["p", "t"]}]],
  "els": [P("p", "news/zeit_bz.jpg", 700, maxh=860), Wd("t", "25 hours", 1290, 170, Y)]},
 {"lines": [[{"en": "On Sunday, October 25th, at 3 a.m.,", "show": ["a"]}, {"en": "the clocks go back to 2 a.m.", "show": ["b"]}]], "hold": 0.3,
  "els": [T("d", "Sunday, Oct 25", 420, 90, Y), Wd("a", "3:00", 760, 260), {"id": "ar", "type": "tile", "icon": "down-arrow", "s": 150, "x": 540, "y": 980},
          Wd("b", "2:00", 1200, 260, Y)]},
 {"lines": [[{"en": "In German, it's the"}, {"de": "Zeitumstellung.", "show": ["w"]}], [{"en": "And winter time is"}, {"de": "Winterzeit.", "show": ["v"]}]], "hold": 0.2,
  "els": [P("p", "news/zeit_bz.jpg", 600, maxh=640), Wd("w", "Zeitumstellung", 1060, 150), T("m", "= the time change", 1190, 64), Wd("v", "Winterzeit", 1330, 150, Y)]},
 {"lines": [[{"en": "Your phone changes by itself. Your oven clock won't.", "show": ["o"]}], [{"en": "So enjoy one extra hour of sleep."}, {"de": "Gute Nacht!", "show": ["g"]}]], "hold": 0.4,
  "els": [T("o", "+1 hour of sleep", 560, 96, Y), {"id": "s", "type": "tile", "icon": "sleeping-face", "s": 420, "x": 540, "y": 900}, Wd("g", "Gute Nacht!", 1300, 170)]},
 FOLLOW]}

for d in (onion, rage, okt, db, zeit):
    json.dump({**d, **BASE}, open(os.path.join(HERE, d["id"] + ".json"), "w"), indent=1, ensure_ascii=False)
