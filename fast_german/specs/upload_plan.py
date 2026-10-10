"""Writes upload_plan.json: titles, descriptions, tags and publish times for the first batch."""
import json, os
HERE = os.path.dirname(__file__)
TAIL = ("\n\nFast German: learn German fast.\nEvery noun has a color: der = blue, die = red, das = green.\n"
        "New short every day. Subscribe and learn German without the boring hour-long lessons.")
TAGS = ["learn german", "german", "german language", "german for beginners", "deutsch lernen", "german words", "fast german"]
SHORTS = [  # (spec id, one-line hook for the description, extra tags) in publish order
 ("11_gluehbirne", "In German, a light bulb is a 'glowing pear': die Glühbirne.", ["glühbirne", "funny german words"]),
 ("13_longest_word", "Donaudampfschifffahrtsgesellschaftskapitän, broken down word by word.", ["longest german word", "german compound words"]),
 ("01_handschuh", "Germans call gloves 'hand shoes': der Handschuh.", ["handschuh", "funny german words"]),
 ("12_schmetterling", "Butterfly in French, Spanish, Italian... and German: der Schmetterling.", ["schmetterling", "butterfly in german"]),
 ("03_gift", "Das Gift means poison. A present is das Geschenk.", ["false friends german", "gift in german"]),
 ("08_der_die_das_quiz", "Der, die or das? Five nouns, one second each.", ["der die das", "german articles quiz"]),
 ("07_kummerspeck", "Kummerspeck: the German word for weight from stress eating.", ["kummerspeck", "untranslatable words"]),
 ("09_denglish", "Handy, Beamer, Oldtimer, Public Viewing: English words with German meanings.", ["denglisch", "german english words"]),
 ("04_mir_ist_heiss", "Say 'Mir ist heiß', not 'Ich bin heiß'.", ["german mistakes", "mir ist heiß"]),
 ("10_hello", "Hallo, Moin, Servus, Grüß Gott, Na? How Germans really say hello.", ["hello in german", "moin servus"]),
 ("02_torschlusspanik", "Torschlusspanik: the fear that time is running out.", ["torschlusspanik", "untranslatable words"]),
 ("05_bakery", "Five words for a German bakery, and how to order.", ["german bakery", "german food words"]),
 ("06_order_coffee", "Order coffee in German: a real café dialogue.", ["order coffee in german", "german phrases"]),
]
plan = []
day, slots = 10, ["13:00", "22:00"]  # two shorts a day for the first test week (UTC)
for i, (sid, hook, tags) in enumerate(SHORTS):
    spec = json.load(open(os.path.join(HERE, "shorts", sid + ".json")))
    d = day + i // 2
    plan.append({"file": f"out/{sid}.mp4", "title": spec["title"] + (" #shorts" if "#shorts" not in spec["title"] else ""),
                 "description": hook + TAIL + "\n\n#learngerman #german #shorts", "tags": TAGS + tags,
                 "publishAt": f"2026-10-{d:02d}T{slots[i % 2]}:00Z"})
LONG = [
 ("out/L2_a1_in_25_minutes.mp4", "Learn German A1 in 25 Minutes (No Boring Grammar)", "out/thumb_L2.jpg", "2026-10-11T15:00:00Z",
  "All the A1 basics in 25 minutes: greetings, introducing yourself, the der/die/das color trick, numbers, the 10 most useful verbs, "
  "questions, café and restaurant phrases, directions, time and days, and the mistakes that make Germans laugh. "
  "Repeat out loud when you see REPEAT AFTER ME, and stay for the speed quiz at the end.", ["learn german a1", "german crash course", "german basics"]),
 ("out/L1_sleep_8h.mp4", "8 Hours of German Words While You Sleep 😴 Calm Voice, Slow Sentences (Beginner)", "out/thumb_L1.jpg",
  "2026-10-10T12:30:00Z",
  "Fall asleep while you learn German. 350 useful beginner words, each one said in English, then in German, then a "
  "short sentence in English, in German, and once more slowly in German. The full set plays four times, so you "
  "hear every word again and again through the night.\n\n"
  "Calm, soft voice. Gentle sleep music and quiet rain. Dark screen with the word, its picture and the sentence.\n\n"
  "0:00:00 Round 1\n2:00:00 Round 2\n4:00:00 Round 3\n6:00:00 Round 4",
  ["learn german while you sleep", "german sleep learning", "german vocabulary", "german words for beginners",
   "sleep learning", "8 hours german"]),
]
UP = ["Voxel Revolution", "Digital Lemonade", "Newer Wave", "Werq", "Pookatori and Friends", "Delightful D", "Tech Live",
      "Raving Energy"]
CREDITS = {"out/L1_sleep_8h.mp4": [], "out/L2_a1_in_25_minutes.mp4": UP}


def credit(titles):
    # Incompetech tracks are CC BY 4.0: the license requires this credit in the description.
    if not titles:
        return ""
    return "\n\nMusic:\n" + "\n".join(f'"{t}" Kevin MacLeod (incompetech.com)' for t in titles) + \
        "\nLicensed under Creative Commons: By Attribution 4.0 License\nhttp://creativecommons.org/licenses/by/4.0/"


for f, title, thumb, at, desc, tags in LONG:
    plan.append({"file": f, "title": title, "thumb": thumb, "publishAt": at, "description": desc + TAIL + credit(CREDITS[f]) + "\n\n#learngerman #german",
                 "tags": TAGS + tags})
json.dump(plan, open(os.path.join(HERE, "..", "upload_plan.json"), "w"), ensure_ascii=False, indent=1)
print(len(plan))
