"""L3 long-form: German Greetings & Basic Phrases (16:9, road look). Writes l3_greetings.json for lib/short_v2.py.
Usage: python3 build_l3.py [sample]   (sample = intro + chapter 1 only)"""
import json, os, sys
HERE = os.path.dirname(__file__)
Y = [255, 204, 0]

# (German, English said first, emoji, optional tip as segments)
CHAPTERS = [
 ("Saying hello", "waving-hand-default", [
  ("Hallo", "Hello.", "waving-hand-default", None),
  ("Hallo zusammen", "Hello, everyone.", "people-hugging", None),
  ("Guten Morgen", "Good morning.", "sunrise", None),
  ("Guten Tag", "Good day.", "sun", [{"de": "Guten Tag"}, {"en": "in shops,"}, {"de": "Hallo"}, {"en": "with friends."}]),
  ("Guten Abend", "Good evening.", "sunset", None),
  ("Moin", "Hi, in the north.", "anchor", [{"en": "Up north, people say"}, {"de": "Moin"}, {"en": "all day long."}]),
  ("Servus", "Hi, in the south.", "snow-capped-mountain", [{"de": "Servus"}, {"en": "means hi and bye."}]),
  ("Grüß Gott", "Hello, in Bavaria and Austria.", "church", None),
 ]),
]


def phrase_scene(de, en, icon, tip):
    lines = [[{"en": en, "show": ["i", "e"]}],
             [{"de": de + ".", "show": ["w"]}],
             [{"de": de + ".", "speed": 0.8}],
             [{"pause": 2.2, "show": ["tm"], "quiet": True}]]
    els = [{"id": "i", "type": "tile", "icon": icon, "s": 400, "x": 500, "y": 540},
           {"id": "w", "type": "word", "de": de, "size": 170, "max_w": 900, "x": 1370, "y": 470},
           {"id": "e", "type": "text", "text": en.rstrip("."), "size": 72, "colour": Y, "x": 1370, "y": 650},
           {"id": "tm", "type": "timer", "s": 130, "dur": 2.2, "x": 1370, "y": 830}]
    if tip:
        tip = [dict(s) for s in tip]
        tip[0]["show"] = ["tip"]
        lines.append(tip)
        text = " ".join(s.get("de") or s.get("en") for s in tip)
        els.append({"id": "tip", "type": "text", "text": text, "size": 62, "x": 960, "y": 960})
    return {"lines": lines, "els": els, "hold": 0.3}


def chapter_card(n, title, icon):
    return {"lines": [[{"en": f"Part {n}. {title}.", "show": ["i", "t"]}]], "hold": 0.6,
            "els": [{"id": "i", "type": "tile", "icon": icon, "s": 300, "x": 960, "y": 430},
                    {"id": "t", "type": "word", "de": title, "size": 130, "colour": Y, "x": 960, "y": 720}]}


def build(sample=False):
    scenes = [{"lines": [[{"en": "Fifty German phrases. Ten minutes.", "show": ["t1", "t2"]}],
                         [{"en": "By the end, you can say hello, introduce yourself, survive when you don't understand, "
                                 "and say goodbye like a German."}],
                         [{"en": "When you see this circle, say it out loud.", "show": ["tm"]}],
                         [{"pause": 1.0}]],
               "els": [{"id": "t1", "type": "word", "de": "50 German phrases", "size": 150, "x": 960, "y": 420},
                       {"id": "t2", "type": "text", "text": "in 10 minutes", "size": 90, "colour": Y, "x": 960, "y": 580},
                       {"id": "tm", "type": "timer", "s": 150, "dur": 3.0, "x": 960, "y": 800}]}]
    for n, (title, icon, phrases) in enumerate(CHAPTERS[:1] if sample else CHAPTERS, 1):
        scenes.append(chapter_card(n, title, icon))
        scenes += [phrase_scene(*p) for p in phrases]
    return {"id": "l3_greetings", "title": "German Greetings & Basic Phrases for Beginners", "landscape": True, "bg": "road",
            "music": "/mnt/project-files/fast_german/cache/music/kpop_beat_c.mp3", "scenes": scenes}


if __name__ == "__main__":
    sample = "sample" in sys.argv
    json.dump(build(sample), open(os.path.join(HERE, "l3_greetings" + ("_sample" if sample else "") + ".json"), "w"), indent=1)
