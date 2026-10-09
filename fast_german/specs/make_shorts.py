"""Writes specs/shorts/*.json for the first batch (02-13). 01 is hand-written."""
import json, os
OUT = os.path.join(os.path.dirname(__file__), "shorts")
FOLLOW = {"say": "Follow for more German.", "top": "Follow for more German", "icons": ["pretzel"], "sfx": "swoosh_up"}
S = {}

S["02_torschlusspanik"] = ("This German word means: panic before the gate closes 😱", [
 {"say": "This German word means... panic before the gate closes.", "top": "Gate-closing panic?!", "icons": ["door", "alarm-clock"], "punch": True, "sfx": "start"},
 {"say": "Tor, gate. Schluss, closing. Panik, panic.", "icons": ["door", "locked", "face-screaming-in-fear"], "ops": ["+", "+"], "words": [{"de": "Tor", "article": "das"}, {"de": "Schluss", "article": "der"}, {"de": "Panik", "article": "die"}], "sfx": "snap"},
 {"say": "Torschlusspanik! The fear that time is running out for the big things in life.", "icons": ["hourglass-not-done"], "word": {"de": "Torschlusspanik", "article": "die"}, "en": "fear of running out of time", "sfx": "ding"},
 {"say": "Like turning thirty, and suddenly you want a ring, a house, and fluent German.", "top": "Turning 30 be like", "icons": ["ring", "house", "pretzel"], "sfx": "pop"},
 {"say": "It's red, because of die Panik. In German, the last word decides the gender.", "icons": ["face-screaming-in-fear"], "word": {"de": "Torschlusspanik", "article": "die"}, "en": "red = die", "sfx": "pop"},
 FOLLOW])

S["03_gift"] = ("Never give a German a GIFT 💀 #german", [
 {"say": "Never give a German a Gift.", "top": "Never give a German a 'Gift'", "icons": ["wrapped-gift"], "punch": True, "sfx": "start"},
 {"say": "Because in German, das Gift means... poison.", "icons": ["skull-and-crossbones"], "word": {"de": "Gift", "article": "das"}, "en": "the poison", "mark": "wrong", "sfx": "buzz"},
 {"say": "A present is das Geschenk.", "icons": ["wrapped-gift"], "word": {"de": "Geschenk", "article": "das"}, "en": "the present", "mark": "right", "sfx": "ding"},
 {"say": "Gift, poison. Geschenk, present. Don't mix them up.", "icons": ["skull-and-crossbones", "wrapped-gift"], "ops": ["vs"], "words": [{"de": "Gift", "article": "das"}, {"de": "Geschenk", "article": "das"}], "sfx": "pop"},
 {"say": "And giftig means poisonous. So please, don't call your present giftig.", "top": "giftig = poisonous", "icons": ["face-vomiting"], "sfx": "buzz"},
 FOLLOW])

S["04_mir_ist_heiss"] = ("Don't say 'Ich bin heiß' in Germany 🥵", [
 {"say": "Hot day in Germany? Don't say: Ich bin heiß.", "top": "Hot day in Germany?", "icons": ["hot-face"], "punch": True, "sfx": "start"},
 {"say": "Ich bin heiß means: I'm hot. Like, sexy hot.", "icons": ["smiling-face-with-sunglasses"], "word": {"de": "Ich bin heiß"}, "en": "I'm hot (sexy)", "mark": "wrong", "sfx": "buzz"},
 {"say": "Say: Mir ist heiß. Literally, to me it is hot.", "icons": ["hot-face"], "word": {"de": "Mir ist heiß"}, "en": "I feel hot", "mark": "right", "sfx": "ding"},
 {"say": "Same for cold. Mir ist kalt.", "icons": ["cold-face"], "word": {"de": "Mir ist kalt"}, "en": "I feel cold", "mark": "right", "sfx": "ding"},
 {"say": "Ich bin kalt means you're a cold person. Not great.", "icons": ["cold-face"], "word": {"de": "Ich bin kalt"}, "en": "I'm a cold person", "mark": "wrong", "sfx": "buzz"},
 FOLLOW])

S["05_bakery"] = ("5 words you need at a German bakery 🥨", [
 {"say": "Five words you need at a German bakery.", "top": "German bakery: 5 words", "icons": ["pretzel"], "punch": True, "sfx": "start"},
 {"say": "Die Brezel. Pretzel.", "top": "1 / 5", "icons": ["pretzel"], "word": {"de": "Brezel", "article": "die"}, "en": "the pretzel", "sfx": "pop"},
 {"say": "Das Brot. Bread.", "top": "2 / 5", "icons": ["bread"], "word": {"de": "Brot", "article": "das"}, "en": "the bread", "sfx": "pop"},
 {"say": "Das Brötchen. Bread roll. Literally, little bread.", "top": "3 / 5", "icons": ["baguette-bread"], "word": {"de": "Brötchen", "article": "das"}, "en": "the bread roll", "sfx": "pop"},
 {"say": "Der Kuchen. Cake.", "top": "4 / 5", "icons": ["shortcake"], "word": {"de": "Kuchen", "article": "der"}, "en": "the cake", "sfx": "pop"},
 {"say": "Der Kaffee. Coffee.", "top": "5 / 5", "icons": ["hot-beverage"], "word": {"de": "Kaffee", "article": "der"}, "en": "the coffee", "sfx": "pop"},
 {"say": "Now order like a local. Eine Brezel und einen Kaffee, bitte!", "top": "Eine Brezel und einen Kaffee, bitte!", "icons": ["pretzel", "hot-beverage"], "ops": ["+"], "en": "A pretzel and a coffee, please!", "sfx": "ding"},
 FOLLOW])

S["06_order_coffee"] = ("How to order coffee in Germany (real dialogue) ☕", [
 {"say": "How to order coffee in Germany. Real dialogue.", "top": "Ordering coffee in Germany", "icons": ["hot-beverage"], "punch": True, "sfx": "start"},
 {"say": "You say: Einen Kaffee, bitte.", "top": "YOU", "icons": ["hot-beverage"], "word": {"de": "Einen Kaffee, bitte."}, "en": "A coffee, please.", "sfx": "pop"},
 {"say": "They ask: Für hier oder zum Mitnehmen?", "top": "BARISTA", "icons": ["teacup-without-handle", "takeout-box"], "ops": ["vs"], "en": "For here or to go?", "sfx": "pop"},
 {"say": "To go? Zum Mitnehmen, bitte.", "top": "YOU", "icons": ["takeout-box"], "word": {"de": "Zum Mitnehmen, bitte."}, "en": "To go, please.", "sfx": "pop"},
 {"say": "Das macht drei Euro.", "top": "BARISTA", "icons": ["euro-banknote"], "word": {"de": "Das macht 3 Euro."}, "en": "That's 3 euros.", "sfx": "pop"},
 {"say": "Danke, schönen Tag noch!", "top": "YOU", "icons": ["waving-hand-default"], "word": {"de": "Danke, schönen Tag noch!"}, "en": "Thanks, have a nice day!", "mark": "right", "sfx": "ding"},
 FOLLOW])

S["07_kummerspeck"] = ("Germans have a word for stress-eating weight 🥓", [
 {"say": "Germans have a word for the weight you gain from stress eating.", "top": "Stress eating has a German name", "icons": ["pizza", "ice-cream"], "punch": True, "sfx": "start"},
 {"say": "Kummer, grief. Speck, bacon.", "icons": ["broken-heart", "bacon"], "ops": ["+"], "words": [{"de": "Kummer", "article": "der"}, {"de": "Speck", "article": "der"}], "sfx": "snap"},
 {"say": "Kummerspeck. Grief bacon.", "icons": ["broken-heart", "bacon"], "ops": ["+"], "word": {"de": "Kummerspeck", "article": "der"}, "en": "grief bacon", "sfx": "ding"},
 {"say": "Breakup, plus two weeks of ice cream, equals Kummerspeck.", "top": "Breakup + ice cream =", "icons": ["broken-heart", "soft-ice-cream"], "ops": ["+"], "word": {"de": "Kummerspeck", "article": "der"}, "sfx": "pop"},
 {"say": "It's blue, because of der Speck. The last word decides.", "icons": ["bacon"], "word": {"de": "Kummerspeck", "article": "der"}, "en": "blue = der", "sfx": "pop"},
 FOLLOW])

quiz = [("Sonne", "die", "sun"), ("Mond", "der", "crescent-moon"), ("Mädchen", "das", "girl-default"), ("Butter", "die", "butter"), ("Auto", "das", "automobile")]
qb = [{"say": "Der, die, or das? One second each. Go!", "top": "der, die or das?", "icons": ["thinking-face"], "punch": True, "sfx": "start"}]
for i, (w, a, ic) in enumerate(quiz):
    qb.append({"say": f"{w}. || {a.capitalize()} {w}.", "top": f"{i + 1} / 5", "icons": [ic], "word": {"de": "___ " + w}, "sfx": "tick",
               "reveal": {"word": {"de": w, "article": a}, "mark": "right", "sfx": "ding"}})
qb.append({"say": "Mädchen is das, because every word ending in chen is das.", "icons": ["girl-default"], "word": {"de": "Mädchen", "article": "das"}, "en": "-chen = always das", "sfx": "pop"})
qb.append({"say": "How many did you get? Comment your score!", "top": "Your score?", "icons": ["trophy"], "sfx": "pop"})
qb.append(FOLLOW)
S["08_der_die_das_quiz"] = ("der, die or das? Only 1% get all 5 🧠", qb)

S["09_denglish"] = ("English words Germans use WRONG 😂", [
 {"say": "Germans use English words... but wrong.", "top": "English words Germans use WRONG", "icons": ["face-with-hand-over-mouth"], "punch": True, "sfx": "start"},
 {"say": "Handy. In Germany, that's your phone.", "icons": ["mobile-phone"], "word": {"de": "Handy", "article": "das"}, "en": "the mobile phone", "sfx": "pop"},
 {"say": "Beamer. Not a BMW. It's a projector.", "icons": ["film-projector"], "word": {"de": "Beamer", "article": "der"}, "en": "the projector", "sfx": "pop"},
 {"say": "Oldtimer. Not an old man. It's a classic car.", "icons": ["automobile"], "word": {"de": "Oldtimer", "article": "der"}, "en": "the classic car", "sfx": "pop"},
 {"say": "Public Viewing. Not a funeral. It's watching football outside with thousands of fans.", "icons": ["soccer-ball"], "word": {"de": "Public Viewing", "article": "das"}, "en": "watching a game outdoors", "sfx": "pop"},
 FOLLOW])

S["10_hello"] = ("How Germans ACTUALLY say hello 👋", [
 {"say": "Stop saying Guten Tag. Here's how Germans really say hello.", "top": "Stop saying 'Guten Tag'", "icons": ["waving-hand-default"], "word": {"de": "Guten Tag"}, "en": "very formal", "punch": True, "sfx": "start"},
 {"say": "Hallo. Works everywhere, with everyone.", "icons": ["waving-hand-default"], "word": {"de": "Hallo"}, "en": "hello (everywhere)", "mark": "right", "sfx": "ding"},
 {"say": "Moin! In the north. Even in the evening.", "icons": ["anchor"], "word": {"de": "Moin!"}, "en": "hi (North Germany)", "sfx": "pop"},
 {"say": "Servus! In Bavaria and Austria. It means hi and bye.", "icons": ["snow-capped-mountain"], "word": {"de": "Servus!"}, "en": "hi & bye (South)", "sfx": "pop"},
 {"say": "Grüß Gott! The polite hello in the south.", "icons": ["snow-capped-mountain"], "word": {"de": "Grüß Gott!"}, "en": "hello (South, polite)", "sfx": "pop"},
 {"say": "And with friends? Na? Just na. It means: how's it going?", "icons": ["grinning-face-with-smiling-eyes"], "word": {"de": "Na?"}, "en": "how's it going?", "sfx": "ding"},
 FOLLOW])

S["11_gluehbirne"] = ("How to say LIGHT BULB in German 💡", [
 {"say": "How do you say light bulb in German?", "top": "Light bulb in German?", "icons": ["light-bulb"], "punch": True, "sfx": "start"},
 {"say": "Glühbirne.", "icons": ["light-bulb"], "word": {"de": "Glühbirne", "article": "die"}, "en": "the light bulb", "sfx": "ding", "pause": 0.3},
 {"say": "Glühen, to glow. Birne, pear.", "icons": ["sparkles", "pear"], "ops": ["+"], "words": [{"de": "glühen"}, {"de": "Birne", "article": "die"}], "sfx": "snap"},
 {"say": "A glowing pear! And honestly... they're not wrong.", "top": "A glowing pear?!", "icons": ["light-bulb", "pear"], "ops": ["="], "mark": "right", "sfx": "ding"},
 {"say": "It's red, because of die Birne.", "icons": ["pear"], "word": {"de": "Glühbirne", "article": "die"}, "en": "red = die", "sfx": "pop"},
 FOLLOW])

S["12_schmetterling"] = ("Butterfly in German is... SCHMETTERLING 🦋", [
 {"say": "Butterfly in different languages.", "top": "Butterfly in...", "icons": ["butterfly"], "punch": True, "sfx": "start"},
 {"say": "French: papillon.", "top": "French", "icons": ["butterfly"], "word": {"de": "papillon"}, "sfx": "pop"},
 {"say": "Spanish: mariposa.", "top": "Spanish", "icons": ["butterfly"], "word": {"de": "mariposa"}, "sfx": "pop"},
 {"say": "Italian: farfalla.", "top": "Italian", "icons": ["butterfly"], "word": {"de": "farfalla"}, "sfx": "pop"},
 {"say": "German: SCHMETTERLING!", "top": "German", "icons": ["butterfly"], "word": {"de": "SCHMETTERLING", "article": "der"}, "punch": True, "sfx": "start"},
 {"say": "It comes from Schmetten, an old word for cream. Butterflies love to land on cream.", "icons": ["butterfly", "glass-of-milk"], "word": {"de": "Schmetten"}, "en": "old word for cream", "sfx": "pop"},
 {"say": "So the scary word is really a little cream lover. Cute, right?", "icons": ["butterfly"], "word": {"de": "Schmetterling", "article": "der"}, "en": "the butterfly", "mark": "right", "sfx": "ding"},
 FOLLOW])

parts = [("Donau", "die", "water-wave", "the Danube"), ("Dampf", "der", "cloud", "steam"), ("Schiff", "das", "ship", "ship"),
         ("Fahrt", "die", "world-map", "trip"), ("Gesellschaft", "die", "office-building", "company"), ("Kapitän", "der", "anchor", "captain")]
lb = [{"say": "This is a real German word.", "top": "A REAL German word", "icons": ["face-screaming-in-fear"], "word": {"de": "Donaudampfschiff|fahrtsgesellschafts|kapitän", "article": "der"}, "punch": True, "sfx": "start"},
      {"say": "Let's break it down in twenty seconds.", "top": "Let's break it down", "icons": ["stopwatch"], "sfx": "whoosh"}]
for de, a, ic, en in parts:
    lb.append({"say": f"{de}, {en}.", "icons": [ic], "word": {"de": de, "article": a}, "en": en, "sfx": "snap"})
lb.append({"say": "Danube steamship company captain! And it's der, because of der Kapitän.", "icons": ["ship", "anchor"], "ops": ["+"], "word": {"de": "Donaudampfschiff|fahrtsgesellschafts|kapitän", "article": "der"}, "sfx": "ding"})
lb.append({"say": "Can you say it in one breath? Comment!", "top": "Say it in one breath!", "icons": ["face-with-hand-over-mouth"], "sfx": "pop"})
lb.append(FOLLOW)
S["13_longest_word"] = ("The longest German word, explained in 20 seconds 🤯", lb)

for k, (title, beats) in S.items():
    json.dump({"id": k, "title": title, "beats": beats}, open(os.path.join(OUT, k + ".json"), "w"), ensure_ascii=False, indent=1)
print(len(S))
