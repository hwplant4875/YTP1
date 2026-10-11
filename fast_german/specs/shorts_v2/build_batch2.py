"""Shorts 04-06 (2026-10-11): same look as 02/03 (road, kpop_beat_c, Fredoka, top-centre pretzel). Writes the json specs."""
import json, os
HERE = os.path.dirname(__file__)
Y, RED = [255, 204, 0], [229, 72, 77]
BASE = {"music": "/mnt/project-files/fast_german/cache/music/kpop_beat_c.mp3", "bg": "road"}
FOLLOW = {"lines": [[{"en": "Follow for more German."}]], "hold": 0.8,
          "els": [{"id": "l", "type": "logo", "x": 540, "y": 740}, {"id": "t", "type": "text", "text": "Follow for more German", "size": 70, "x": 540, "y": 1000}]}

kummer = {"id": "04_kummerspeck", "title": "Germans have a word for this 🥓💔", "scenes": [
 {"lines": [[{"de": "Kummerspeck.", "show": ["w"]}], [{"en": "This German word means... grief bacon.", "show": ["m"]}]],
  "els": [{"id": "p", "type": "photo", "src": "bacon_7.jpg", "w": 920, "h": 720, "x": 540, "y": 790},
          {"id": "w", "type": "word", "de": "Kummerspeck", "size": 200, "x": 540, "y": 1320},
          {"id": "m", "type": "text", "text": "= grief bacon", "size": 80, "colour": Y, "x": 540, "y": 1470}]},
 {"lines": [[{"de": "Kummer", "show": ["r1"]}, {"en": "for grief."}], [{"de": "Speck", "show": ["r2"]}, {"en": "for bacon."}]], "hold": 0.4,
  "els": [{"id": "r1", "type": "row", "icon": "broken-heart", "de": "Kummer", "en": "= grief", "x": 540, "y": 700},
          {"id": "r2", "type": "row", "photo": "bacon_7.jpg", "de": "Speck", "en": "= bacon", "x": 540, "y": 1040}]},
 {"lines": [[{"en": "It's the weight you gain from eating your feelings.", "show": ["h"]}],
            [{"en": "One breakup,", "show": ["a"]}, {"en": "two pizzas,", "show": ["b"]}, {"en": "a lot of ice cream.", "show": ["c"]}]], "hold": 0.3,
  "els": [{"id": "h", "type": "tile", "icon": "broken-heart", "s": 520, "x": 540, "y": 720},
          {"id": "a", "type": "tile", "icon": "crying-face", "s": 280, "x": 230, "y": 1310},
          {"id": "b", "type": "tile", "icon": "pizza", "s": 280, "x": 540, "y": 1310},
          {"id": "c", "type": "tile", "icon": "soft-ice-cream", "s": 280, "x": 850, "y": 1310}]},
 {"lines": [[{"en": "And the gender?"}], [{"de": "der Kummer,", "show": ["r1"]}, {"de": "der Speck.", "show": ["r2"]}],
            [{"en": "So it's"}, {"de": "der Kummerspeck.", "show": ["w"]}]], "hold": 0.5,
  "els": [{"id": "r1", "type": "row", "icon": "broken-heart", "de": "Kummer", "article": "der", "show_article": True, "x": 540, "y": 600},
          {"id": "r2", "type": "row", "photo": "bacon_7.jpg", "de": "Speck", "article": "der", "show_article": True, "hl": True, "x": 540, "y": 900},
          {"id": "w", "type": "word", "de": "Kummerspeck", "article": "der", "size": 150, "x": 540, "y": 1260}]},
 FOLLOW]}

turtle = {"id": "05_schildkroete", "title": "Germans call a turtle a SHIELD TOAD 🐢", "scenes": [
 {"lines": [[{"en": "In German, a turtle is a"}, {"de": "Schildkröte.", "show": ["w"]}], [{"en": "Literally... a shield toad.", "show": ["m"]}]],
  "els": [{"id": "p", "type": "photo", "src": "turtle_4.jpg", "w": 920, "h": 720, "x": 540, "y": 790},
          {"id": "w", "type": "word", "de": "Schildkröte", "size": 200, "x": 540, "y": 1320},
          {"id": "m", "type": "text", "text": "= shield toad", "size": 80, "colour": Y, "x": 540, "y": 1470}]},
 {"lines": [[{"de": "Schild", "show": ["r1"]}, {"en": "for shield."}], [{"de": "Kröte", "show": ["r2"]}, {"en": "for toad."}]], "hold": 0.4,
  "els": [{"id": "r1", "type": "row", "icon": "shield", "de": "Schild", "en": "= shield", "x": 540, "y": 700},
          {"id": "r2", "type": "row", "icon": "frog", "de": "Kröte", "en": "= toad", "x": 540, "y": 1040}]},
 {"lines": [[{"en": "A toad,", "show": ["a"]}, {"en": "carrying a shield on its back.", "show": ["b"]}], [{"en": "Honestly? Not wrong.", "show": ["c"]}]], "hold": 0.4,
  "els": [{"id": "a", "type": "tile", "icon": "frog", "s": 420, "x": 300, "y": 800},
          {"id": "b", "type": "tile", "icon": "shield", "s": 420, "x": 780, "y": 800},
          {"id": "c", "type": "tile", "icon": "turtle", "s": 520, "x": 540, "y": 1300}]},
 {"lines": [[{"en": "And the gender?"}], [{"de": "das Schild,", "show": ["r1"]}, {"de": "die Kröte.", "show": ["r2"]}],
            [{"en": "The last word decides. So it's"}, {"de": "die Schildkröte.", "show": ["w"]}]], "hold": 0.5,
  "els": [{"id": "r1", "type": "row", "icon": "shield", "de": "Schild", "article": "das", "show_article": True, "x": 540, "y": 600},
          {"id": "r2", "type": "row", "icon": "frog", "de": "Kröte", "article": "die", "show_article": True, "hl": True, "x": 540, "y": 900},
          {"id": "w", "type": "word", "de": "Schildkröte", "article": "die", "size": 150, "x": 540, "y": 1260}]},
 FOLLOW]}

become = {"id": "06_bekommen", "title": "He did NOT become a schnitzel 😂", "scenes": [
 {"lines": [[{"en": "In a German restaurant, you'll hear:", "show": ["i"]}], [{"de": "Ich bekomme ein Schnitzel.", "show": ["w", "w2"]}]],
  "els": [{"id": "i", "type": "tile", "icon": "cut-of-meat", "s": 560, "x": 540, "y": 760},
          {"id": "w", "type": "word", "de": "Ich bekomme", "size": 150, "x": 540, "y": 1250},
          {"id": "w2", "type": "word", "de": "ein Schnitzel", "size": 150, "x": 540, "y": 1420}]},
 {"lines": [[{"en": "No, he does not become a schnitzel.", "show": ["m", "x"]}]], "hold": 0.3,
  "els": [{"id": "i", "type": "tile", "icon": "cut-of-meat", "s": 560, "x": 540, "y": 760},
          {"id": "m", "type": "text", "text": "I become a schnitzel?", "size": 80, "colour": Y, "x": 540, "y": 1300},
          {"id": "x", "type": "tile", "icon": "cross-mark", "s": 200, "x": 820, "y": 520}]},
 {"lines": [[{"de": "bekommen", "show": ["r1"]}, {"en": "means to get."}], [{"en": "To become is"}, {"de": "werden.", "show": ["r2"]}]], "hold": 0.4,
  "els": [{"id": "r1", "type": "row", "icon": "package", "de": "bekommen", "en": "= to get", "hl": True, "x": 540, "y": 700},
          {"id": "r2", "type": "row", "icon": "butterfly", "de": "werden", "en": "= to become", "x": 540, "y": 1040}]},
 {"lines": [[{"en": "So"}, {"de": "Ich bekomme ein Schnitzel", "show": ["w", "w2", "ok"]}, {"en": "means: I'll get a schnitzel.", "show": ["m"]}]], "hold": 0.6,
  "els": [{"id": "i", "type": "tile", "icon": "cut-of-meat", "s": 420, "x": 540, "y": 640},
          {"id": "w", "type": "word", "de": "Ich bekomme", "size": 115, "x": 540, "y": 1080},
          {"id": "w2", "type": "word", "de": "ein Schnitzel", "size": 115, "x": 540, "y": 1240},
          {"id": "m", "type": "text", "text": "= I'll get a schnitzel", "size": 80, "colour": Y, "x": 540, "y": 1440},
          {"id": "ok", "type": "ring", "w": 900, "h": 400, "width": 16, "x": 540, "y": 1160}]},
 FOLLOW]}

for d in (kummer, turtle, become):
    json.dump({**d, **BASE}, open(os.path.join(HERE, d["id"] + ".json"), "w"), indent=1)
