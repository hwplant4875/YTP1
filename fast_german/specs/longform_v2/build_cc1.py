"""German Cheat Codes #1: You Already Know 1,000 German Words (16:9, road look, Carla).
Concept (user 2026-10-18): proven learning method x A1 core; here cognate sound rules. Each English word is said in
English, the German one in German. Open loop at 0:15 (a sentence that looks like nonsense) is paid off at the end.
Writes cc1_cognates.json for lib/short_v2.py.  Usage: python3 build_cc1.py [sample]"""
import json, os, sys
HERE = os.path.dirname(__file__)
Y, GREEN, RED = [255, 204, 0], [52, 199, 89], [255, 90, 90]

# (rule shown big, rule said, tip with English/German parts, [(english, german, fluent icon), ...])
CODES = [
 ("Same word", "Some words are exactly the same.", [("en", "Same spelling, same meaning. Only the sound is German.")], [
  ("hand", "Hand", "raised-hand-default"), ("finger", "Finger", "index-pointing-up-default"), ("arm", "Arm", "flexed-biceps-default"),
  ("name", "Name", "identification-card"), ("hotel", "Hotel", "hotel"), ("taxi", "Taxi", "taxi"), ("baby", "Baby", "baby-default"),
  ("film", "Film", "film-frames"), ("bus", "Bus", "bus"), ("radio", "Radio", "radio"), ("wind", "Wind", "wind-face"),
  ("winter", "Winter", "snowman"), ("park", "Park", "national-park"), ("sport", "Sport", "soccer-ball")]),
 ("ou » au", "O U becomes A U.", [("en", "Same sound, German spelling.")], [
  ("house", "Haus", "house"), ("mouse", "Maus", "mouse-face"), ("out", "aus", "door"), ("brown", "braun", "brown-circle"),
  ("loud", "laut", "loudspeaker")]),
 ("d » t", "D becomes T.", [("en", "An English D often turns into a German T.")], [
  ("day", "Tag", "sun"), ("drink", "trinken", "cup-with-straw"), ("dream", "Traum", "thought-balloon"), ("door", "Tür", "door"),
  ("red", "rot", "red-circle"), ("bread", "Brot", "bread"), ("good", "gut", "thumbs-up-default")]),
 ("t » z / ss", "T becomes Z, or double S.", [("en", "At the start of a word, T becomes Z. In the middle, it becomes double S.")], [
  ("ten", "zehn", "keycap-10"), ("time", "Zeit", "stopwatch"), ("salt", "Salz", "salt"), ("heart", "Herz", "red-heart"),
  ("water", "Wasser", "droplet"), ("eat", "essen", "fork-and-knife"), ("better", "besser", "chart-increasing"),
  ("white", "weiß", "white-circle"), ("street", "Straße", "motorway")]),
 ("p » pf / f", "P becomes P F, or F.", [("en", "P turns into P F at the start, and into F in the middle.")], [
  ("apple", "Apfel", "red-apple"), ("pepper", "Pfeffer", "hot-pepper"), ("pound", "Pfund", "balance-scale"),
  ("ship", "Schiff", "ship"), ("sleep", "schlafen", "sleeping-face"), ("help", "helfen", "sos-button"), ("deep", "tief", "diving-mask")]),
 ("th » d", "T H becomes D.", [("en", "German has no T H sound. So it uses D, or T.")], [
  ("thank you", "danke", "folded-hands-default"), ("thing", "Ding", "package"), ("three", "drei", "keycap-3"),
  ("thick", "dick", "hamburger"), ("brother", "Bruder", "people-hugging"), ("father", "Vater", "man-beard-default"),
  ("mother", "Mutter", "woman-default")]),
 ("y » j   c » k", "Y becomes J, and C becomes K.", [("en", "In German, J sounds like an English Y.")], [
  ("yes", "ja", "check-mark-button"), ("year", "Jahr", "calendar"), ("young", "jung", "child-default"),
  ("coffee", "Kaffee", "hot-beverage"), ("cat", "Katze", "cat-face"), ("class", "Klasse", "school"), ("cold", "kalt", "cold-face")]),
 ("The endings", "And the biggest cheat code of all: the endings.",
  [("en", "These five endings alone give you more than a thousand words.")], [
  ("nation", "Nation", "globe-showing-europe-africa"), ("information", "Information", "information"), ("station", "Station", "station"),
  ("university", "Universität", "graduation-cap"), ("quality", "Qualität", "sparkles"), ("reality", "Realität", "eyes"),
  ("biology", "Biologie", "dna"), ("energy", "Energie", "high-voltage"), ("photography", "Fotografie", "camera"),
  ("music", "Musik", "musical-notes"), ("politics", "Politik", "classical-building"), ("physics", "Physik", "atom-symbol"),
  ("to telephone", "telefonieren", "telephone-receiver"), ("to organize", "organisieren", "card-index-dividers"),
  ("to repair", "reparieren", "wrench"), ("to study", "studieren", "books")]),
]
# endings chapter: show the ending pattern next to each group
ENDING_OF = {"Nation": "-tion » -tion", "Information": "-tion » -tion", "Station": "-tion » -tion",
             "Universität": "-ity » -ität", "Qualität": "-ity » -ität", "Realität": "-ity » -ität",
             "Biologie": "-y » -ie", "Energie": "-y » -ie", "Fotografie": "-y » -ie",
             "Musik": "-ic » -ik", "Politik": "-ics » -ik", "Physik": "-ics » -ik",
             "telefonieren": "-ate / -ize » -ieren", "organisieren": "-ate / -ize » -ieren", "reparieren": "verb » -ieren",
             "studieren": "verb » -ieren"}

FALSE = [("Gift", "a gift", "poison", "skull"), ("Rat", "a rat", "advice", "speech-balloon"),
         ("bald", "bald", "soon", "hourglass-not-done"), ("also", "also", "so", "thinking-face")]

QUIZ = [("garden", "Garten", "seedling", "d » t"), ("foot", "Fuß", "footprints", "t » ß"), ("tongue", "Zunge", "tongue", "t » z"),
        ("nut", "Nuss", "chestnut", "t » ss"), ("democracy", "Demokratie", "ballot-box-with-ballot", "-y » -ie")]

SENTENCE = "Mein Bruder trinkt Kaffee im Hotel."


def pair_scene(en, de, icon, rule):
    return {"lines": [[{"en": en[0].upper() + en[1:] + ".", "show": ["i", "e", "r"]}], [{"de": de + ".", "show": ["a", "w"]}]],
            "hold": 0.15,
            "els": [{"id": "r", "type": "text", "text": rule, "size": 72, "colour": Y, "x": 960, "y": 215},
                    {"id": "i", "type": "tile", "icon": icon, "s": 380, "x": 960, "y": 470},
                    {"id": "e", "type": "text", "text": en, "size": 150, "max_w": 760, "x": 500, "y": 830},
                    {"id": "a", "type": "text", "text": "»", "size": 150, "colour": Y, "x": 960, "y": 830},
                    {"id": "w", "type": "word", "de": de, "size": 200, "max_w": 820, "colour": Y, "x": 1420, "y": 830}]}


def code_card(n, rule, said, tip):
    return {"lines": [[{"en": f"Cheat code {n}.", "show": ["c"]}, {"en": said, "show": ["r"]}], [{tip[0][0]: tip[0][1], "show": ["t"]}]],
            "hold": 0.4, "header": f"Cheat code {n} · {rule}",
            "els": [{"id": "c", "type": "text", "text": f"CHEAT CODE {n}", "size": 100, "colour": Y, "x": 960, "y": 330},
                    {"id": "r", "type": "word", "de": rule, "size": 260, "max_w": 1600, "x": 960, "y": 540},
                    {"id": "t", "type": "text", "text": tip[0][1], "size": 66, "x": 960, "y": 800}]}


def false_scenes():
    out = [{"lines": [[{"en": "But careful. A few words are traps.", "show": ["t", "i"]}]], "hold": 0.3, "header": "Watch out · False friends",
            "els": [{"id": "i", "type": "tile", "icon": "warning", "s": 280, "x": 960, "y": 420},
                    {"id": "t", "type": "word", "de": "False friends", "size": 150, "colour": RED, "x": 960, "y": 720}]}]
    for de, looks, means, icon in FALSE:
        out.append({"lines": [[{"de": de + ".", "show": ["w", "i"]}], [{"en": f"It's not {looks}. It means {means}.", "show": ["x", "m"]}]],
                    "hold": 0.2,
                    "els": [{"id": "i", "type": "tile", "icon": icon, "s": 280, "x": 960, "y": 380},
                            {"id": "w", "type": "word", "de": de, "size": 170, "x": 960, "y": 640},
                            {"id": "x", "type": "text", "text": f"not {looks}", "size": 70, "colour": RED, "x": 620, "y": 860},
                            {"id": "m", "type": "text", "text": f"= {means}", "size": 80, "colour": GREEN, "x": 1300, "y": 860}]})
    return out


def quiz_scenes():
    out = [{"lines": [[{"en": "Now you try. Use the cheat codes and guess the German word.", "show": ["i", "t"]}]], "hold": 0.4,
            "header": "Quiz · Crack the code",
            "els": [{"id": "i", "type": "tile", "icon": "video-game", "s": 300, "x": 960, "y": 430},
                    {"id": "t", "type": "word", "de": "Crack the code!", "size": 140, "colour": Y, "x": 960, "y": 720}]}]
    for en, de, icon, rule in QUIZ:
        out.append({"lines": [[{"en": en[0].upper() + en[1:] + "?", "show": ["i", "q"]}],
                              [{"pause": 3.0, "show": ["tm"], "quiet": True}],
                              [{"de": de + ".", "show": ["a", "r", "ok"]}], [{"pause": 0.6}]], "hold": 0.2,
                    "els": [{"id": "i", "type": "tile", "icon": icon, "s": 330, "x": 500, "y": 520},
                            {"id": "q", "type": "text", "text": en, "size": 110, "x": 1370, "y": 300},
                            {"id": "tm", "type": "timer", "s": 150, "dur": 3.0, "x": 1370, "y": 520},
                            {"id": "a", "type": "word", "de": de, "size": 160, "max_w": 900, "colour": Y, "x": 1370, "y": 760},
                            {"id": "r", "type": "text", "text": rule, "size": 56, "x": 1370, "y": 920},
                            {"id": "ok", "type": "ring", "w": 900, "h": 260, "width": 12, "x": 1370, "y": 760}]})
    return out


def build(sample=False):
    hook = ["Hand", "Hotel", "Baby", "Taxi", "Musik", "Kaffee"]
    scenes = [{"lines": [[{"en": "You already know a thousand German words.", "show": ["t1"]}],
                         [{"en": "You just don't know it yet.", "show": ["t2"]}]],
               "els": [{"id": "t1", "type": "word", "de": "1,000 German words", "size": 210, "colour": Y, "x": 960, "y": 440},
                       {"id": "t2", "type": "text", "text": "you already know", "size": 110, "x": 960, "y": 660}]},
              {"lines": [[{"de": w + ".", "show": [f"h{i}"], "join": 0.15} for i, w in enumerate(hook)]], "hold": 0.2,
               "els": [{"id": f"h{i}", "type": "word", "de": w, "size": 180, "colour": None if i % 2 else Y,
                        "x": [400, 960, 1520][i % 3], "y": 400 if i < 3 else 720} for i, w in enumerate(hook)]},
              {"lines": [[{"en": "Right now, this sentence looks like nonsense.", "show": ["s"]}],
                         [{"en": "By the end of this video, you'll read it. No dictionary.", "show": ["q"]}]],
               "els": [{"id": "s", "type": "word", "de": SENTENCE, "size": 140, "max_w": 1760, "x": 960, "y": 470},
                       {"id": "q", "type": "text", "text": "You'll read this by the end", "size": 70, "colour": Y, "x": 960, "y": 680}]},
              {"lines": [[{"en": "English and German are sisters. They share thousands of words, and they change in the same few ways.", "show": ["t"]}],
                         [{"en": "Learn those few changes, and the words unlock themselves. These are your cheat codes.", "show": ["c"]}]],
               "els": [{"id": "t", "type": "text", "text": "English + German = sister languages", "size": 96, "x": 960, "y": 450},
                       {"id": "c", "type": "word", "de": "8 cheat codes", "size": 220, "colour": Y, "x": 960, "y": 650}]}]
    codes = CODES[:2] if sample else CODES
    for n, (rule, said, tip, pairs) in enumerate(codes, 1):
        scenes.append(code_card(n, rule, said, tip))
        for en, de, icon in pairs:
            scenes.append(pair_scene(en, de, icon, ENDING_OF.get(de, rule)))
        if n == 1:
            scenes.append({"lines": [[{"en": "Notice something? In German, every noun starts with a capital letter.", "show": ["t"]}]],
                           "hold": 0.3, "els": [{"id": "t", "type": "word", "de": "Hand · Hotel · Baby", "size": 140, "colour": Y, "x": 960, "y": 470},
                                                {"id": "u", "type": "text", "text": "every noun = Capital letter", "size": 70, "x": 960, "y": 650}],
                           "lines_show_u": True})
    if not sample:
        scenes += false_scenes()
        scenes += quiz_scenes()
        scenes += [{"lines": [[{"en": "Now, remember this sentence?", "show": ["s"]}],
                              [{"de": SENTENCE, "show": ["s2"]}],
                              [{"en": "My brother drinks coffee in the hotel.", "show": ["e"]}],
                              [{"en": "Brother, th becomes d. Drinks, d becomes t. Coffee, c becomes k. And hotel is just hotel.", "show": ["k"]}]],
                    "header": "", "hold": 0.4,
                    "els": [{"id": "s", "type": "word", "de": SENTENCE, "size": 110, "max_w": 1700, "x": 960, "y": 380},
                            {"id": "s2", "type": "text", "text": "▲ you can read this now", "size": 56, "colour": GREEN, "x": 960, "y": 500},
                            {"id": "e", "type": "text", "text": "My brother drinks coffee in the hotel.", "size": 80, "colour": Y, "x": 960, "y": 640},
                            {"id": "k", "type": "text", "text": "Bruder (th » d) · trinkt (d » t) · Kaffee (c » k) · Hotel", "size": 54, "x": 960, "y": 790}]},
                   {"lines": [[{"en": "You just read German, with zero vocabulary lists.", "show": ["t"]}],
                              [{"en": "Next cheat code: guess the grammar rule yourself.", "show": ["n"]}], [{"pause": 1.5}]],
                    "els": [{"id": "t", "type": "word", "de": "Super gemacht!", "size": 160, "colour": Y, "x": 960, "y": 450},
                            {"id": "n", "type": "text", "text": "Next: Cheat code #2", "size": 80, "x": 960, "y": 640}]}]
    for sc in scenes:
        sc.pop("lines_show_u", None)
        ids = {e["id"] for e in sc["els"]}
        shown = {i for ln in sc["lines"] for seg in ln for i in seg.get("show", [])}
        for e in sc["els"]:                          # anything not explicitly shown appears with the first line
            if e["id"] not in shown:
                sc["lines"][0][0].setdefault("show", []).append(e["id"])
        assert shown <= ids, (shown - ids)
    return {"id": "cc1_cognates" + ("_sample" if sample else ""), "title": "You Already Know 1,000 German Words",
            "landscape": True, "bg": "road", "tight": 0.5,
            "music": ["/mnt/project-files/fast_german/cache/music/incompetech/lobby_time_loop.wav",
                      "/mnt/project-files/fast_german/cache/music/incompetech/easy_lemon_loop.wav"], "scenes": scenes}


if __name__ == "__main__":
    sample = "sample" in sys.argv
    d = build(sample)
    json.dump(d, open(os.path.join(HERE, d["id"] + ".json"), "w"), indent=1, ensure_ascii=False)
    print(d["id"], len(d["scenes"]), "scenes")
