"""L3 long-form: German Greetings & Basic Phrases (16:9, road look). Writes l3_greetings.json for lib/short_v2.py.
Usage: python3 build_l3.py [sample]   (sample = intro + chapter 1 only)"""
import json, os, sys
HERE = os.path.dirname(__file__)
Y = [255, 204, 0]

# (German, English said first, emoji, optional tip). A tip is a string (English) or a list of segments
# mixing {"en"} and {"de"} so German words in it are pronounced in German.
def T(*parts):
    """T("Guten Tag", " in shops, ", "Hallo", " with friends.") -> segments; odd parts German, even English."""
    segs = []
    for i, p in enumerate(parts):
        if p.strip():
            segs.append({"de" if i % 2 == 0 else "en": p.strip()})
    return segs, "".join(parts)


CHAPTERS = [
 ("Saying hello", "waving-hand-default", [
  ("Hallo", "Hello.", "waving-hand-default", None),
  ("Hallo zusammen", "Hello, everyone.", "people-hugging", None),
  ("Guten Morgen", "Good morning.", "sunrise", None),
  ("Guten Tag", "Good day.", "sun", T("Guten Tag", " in shops, ", "Hallo", " with friends.")),
  ("Guten Abend", "Good evening.", "sunset", None),
  ("Moin", "Hi, in the north.", "anchor", T("", "In the north, people say ", "Moin", " all day long.")),
  ("Servus", "Hi, in the south.", "snow-capped-mountain", T("Servus", " means hi and bye.")),
  ("Grüß Gott", "Hello, in Bavaria and Austria.", "church", None),
 ]),
 ("How are you?", "smiling-face", [
  ("Wie geht's?", "How are you?", "smiling-face", T("", "Casual, for friends.")),
  ("Wie geht es Ihnen?", "How are you? Polite.", "necktie", T("Ihnen", " is the polite you. Use it with strangers.")),
  ("Gut, danke.", "Good, thanks.", "thumbs-up-default", None),
  ("Sehr gut!", "Very good!", "star-struck", None),
  ("Es geht.", "So-so.", "neutral-face", None),
  ("Nicht so gut.", "Not so good.", "pensive-face", None),
  ("Und dir?", "And you?", "index-pointing-at-the-viewer-default", T("", "With strangers, say ", "Und Ihnen?")),
  ("Na?", "Hey, what's up?", "winking-face", T("", "One word. The most German greeting.")),
 ]),
 ("Introducing yourself", "bust-in-silhouette", [
  ("Ich heiße Anna.", "My name is Anna.", "name-badge", None),
  ("Wie heißt du?", "What's your name?", "red-question-mark", None),
  ("Mein Name ist Anna.", "My name is Anna. A bit more formal.", "identification-card", None),
  ("Freut mich!", "Nice to meet you!", "handshake", None),
  ("Ich komme aus Kanada.", "I'm from Canada.", "globe-showing-americas", None),
  ("Woher kommst du?", "Where are you from?", "world-map", None),
  ("Ich wohne in Berlin.", "I live in Berlin.", "house", None),
  ("Ich lerne Deutsch.", "I'm learning German.", "books", T("", "Say this, and Germans will slow down for you.")),
 ]),
 ("Polite essentials", "folded-hands-default", [
  ("Bitte", "Please.", "folded-hands-default", T("Bitte", " also means you're welcome, and here you go.")),
  ("Danke", "Thanks.", "red-heart", None),
  ("Danke schön", "Thank you very much.", "bouquet", None),
  ("Gern geschehen", "You're welcome.", "smiling-face-with-smiling-eyes", None),
  ("Entschuldigung", "Excuse me.", "person-raising-hand-default", T("", "Use it to get attention, or to say sorry.")),
  ("Tut mir leid", "I'm sorry.", "crying-face", None),
  ("Ja", "Yes.", "check-mark-button", None),
  ("Nein", "No.", "cross-mark", None),
  ("Kein Problem", "No problem.", "ok-hand-default", None),
  ("Alles klar!", "All right! Got it!", "thumbs-up-default", T("", "Germans say ", "Alles klar", " all the time.")),
 ]),
 ("When you don't understand", "thinking-face", [
  ("Ich verstehe nicht.", "I don't understand.", "confused-face", None),
  ("Noch einmal, bitte.", "Once more, please.", "repeat-button", None),
  ("Langsamer, bitte.", "Slower, please.", "snail", None),
  ("Sprechen Sie Englisch?", "Do you speak English?", "speaking-head", None),
  ("Was bedeutet das?", "What does that mean?", "thinking-face", None),
  ("Wie sagt man das auf Deutsch?", "How do you say that in German?", "speech-balloon", None),
  ("Ich spreche nur ein bisschen Deutsch.", "I only speak a little German.", "pinching-hand-default", None),
 ]),
 ("Saying goodbye", "waving-hand-default", [
  ("Tschüss", "Bye.", "waving-hand-default", None),
  ("Auf Wiedersehen", "Goodbye.", "door", T("", "Polite, for shops and strangers.")),
  ("Bis später", "See you later.", "hourglass-not-done", None),
  ("Bis morgen", "See you tomorrow.", "calendar", None),
  ("Bis bald", "See you soon.", "alarm-clock", None),
  ("Schönen Tag noch!", "Have a nice day!", "sun-with-face", None),
  ("Gute Nacht", "Good night.", "crescent-moon", None),
  ("Ciao", "Bye. Yes, Germans say it too.", "pinched-fingers-default", None),
 ]),
]

# Quizzes after these chapters: (situation said in English, emoji, answer)
QUIZ = {3: [("You meet your boss in the morning.", "office-building", "Guten Morgen!"),
            ("You meet a friend in Munich.", "beer-mug", "Servus!"),
            ("Someone tells you their name.", "handshake", "Freut mich!")],
        6: [("You leave a bakery.", "baguette-bread", "Schönen Tag noch!"),
            ("You didn't catch that.", "ear-default", "Noch einmal, bitte."),
            ("Someone says Danke.", "red-heart", "Gern geschehen."),
            ("You bump into someone.", "collision", "Entschuldigung!"),
            ("You're going to bed.", "bed", "Gute Nacht.")]}


def phrase_scene(de, en, icon, tip):
    """English → German → German slowly → "your turn" ring. The tip comes after the ring has filled, shown and read
    (user 2026-10-11: the ring is the viewer's moment to speak, nothing may interrupt it)."""
    pause = {"pause": 2.2, "show": ["tm"], "quiet": True}
    lines = [[{"en": en, "show": ["i", "e"]}],
             [{"de": de.rstrip(".!?") + (de[-1] if de[-1] in "!?" else "."), "show": ["w"]}],
             [{"de": de.rstrip(".!?") + (de[-1] if de[-1] in "!?" else "."), "speed": 0.8}],
             [pause]]
    els = [{"id": "i", "type": "tile", "icon": icon, "s": 400, "x": 500, "y": 540},
           {"id": "w", "type": "word", "de": de, "size": 170, "max_w": 900, "x": 1370, "y": 430},
           {"id": "e", "type": "text", "text": en.rstrip("."), "size": 72, "colour": Y, "x": 1370, "y": 630},
           {"id": "tm", "type": "timer", "s": 130, "dur": pause["pause"], "x": 1370, "y": 830}]
    if tip:
        segs, text = tip
        segs = [dict(x) for x in segs]
        segs[0]["show"] = ["tip"]
        lines.append(segs)
        els.append({"id": "tip", "type": "text", "text": text, "size": 62, "x": 960, "y": 975})
    return {"lines": lines, "els": els, "hold": 0.3}


def quiz_scenes(items):
    out = [{"lines": [[{"en": "Quick quiz! What do you say?", "show": ["i", "t"]}]], "hold": 0.4,
            "els": [{"id": "i", "type": "tile", "icon": "red-question-mark", "s": 300, "x": 960, "y": 430},
                    {"id": "t", "type": "word", "de": "Quick quiz!", "size": 140, "colour": Y, "x": 960, "y": 720}]}]
    for sit, icon, ans in items:
        out.append({"lines": [[{"en": sit, "show": ["i", "q"]}],
                              [{"pause": 3.0, "show": ["tm"], "quiet": True}],
                              [{"de": ans, "show": ["a", "ok"]}],
                              [{"pause": 0.8}]], "hold": 0.2,
                    "els": [{"id": "i", "type": "tile", "icon": icon, "s": 360, "x": 500, "y": 540},
                            {"id": "q", "type": "text", "text": sit.rstrip("."), "size": 64, "colour": Y, "x": 1370, "y": 330},
                            {"id": "tm", "type": "timer", "s": 150, "dur": 3.0, "x": 1370, "y": 560},
                            {"id": "a", "type": "word", "de": ans, "size": 150, "max_w": 900, "x": 1370, "y": 800},
                            {"id": "ok", "type": "ring", "w": 1040, "h": 300, "width": 14, "x": 1370, "y": 800}]})
    return out


def chapter_card(n, title, icon):
    return {"lines": [[{"en": f"Part {n}. {title}", "show": ["i", "t"]}]], "hold": 0.6, "header": f"Part {n} · {title}",
            "els": [{"id": "i", "type": "tile", "icon": icon, "s": 300, "x": 960, "y": 430},
                    {"id": "t", "type": "word", "de": title, "size": 130, "colour": Y, "x": 960, "y": 720}]}


def build(sample=False):
    scenes = [{"lines": [[{"en": "Fifty German phrases in ten minutes.", "show": ["t1", "t2"]}],
                         [{"en": "By the end, you can say hello, introduce yourself, and get by when you don't understand."}],
                         [{"en": "When you see this circle, say it out loud.", "show": ["tm"]}],
                         [{"pause": 1.0}]],
               "els": [{"id": "t1", "type": "word", "de": "50 German phrases", "size": 150, "x": 960, "y": 420},
                       {"id": "t2", "type": "text", "text": "in 10 minutes", "size": 90, "colour": Y, "x": 960, "y": 580},
                       {"id": "tm", "type": "timer", "s": 150, "dur": 3.0, "x": 960, "y": 800}]}]
    for n, (title, icon, phrases) in enumerate(CHAPTERS[:1] if sample else CHAPTERS, 1):
        scenes.append(chapter_card(n, title, icon))
        scenes += [phrase_scene(*p) for p in phrases]
        if not sample and n in QUIZ:
            scenes += quiz_scenes(QUIZ[n])
    if not sample:
        scenes.append({"lines": [[{"en": "You just learned fifty German phrases.", "show": ["t1"]}],
                                 [{"en": "Follow for more German!", "show": ["t2"]}], [{"pause": 2.0}]],
                       "header": "", "els": [{"id": "t1", "type": "word", "de": "Super gemacht!", "size": 160, "x": 960, "y": 450},
                                             {"id": "t2", "type": "text", "text": "Follow for more German", "size": 84, "colour": Y, "x": 960, "y": 640}]})
    return {"id": "l3_greetings", "title": "German Greetings & Basic Phrases for Beginners", "landscape": True, "bg": "road",
            "music": ["/mnt/project-files/fast_german/cache/music/incompetech/lobby_time_loop.wav", "/mnt/project-files/fast_german/cache/music/incompetech/easy_lemon_loop.wav"], "scenes": scenes}


if __name__ == "__main__":
    sample = "sample" in sys.argv
    json.dump(build(sample), open(os.path.join(HERE, "l3_greetings" + ("_sample" if sample else "") + ".json"), "w"), indent=1)
