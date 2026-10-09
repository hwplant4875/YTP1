"""German Picture Dictionary: The Kitchen (der/die/das colors). Learn section, then picture quiz."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from longform import slide, build, LIGHT

ITEMS = [  # (section, article, word, english, icon, example, example_en)
 ("Plates & Cutlery", "der", "Teller", "the plate", "fork-and-knife-with-plate", "Der Teller ist sauber.", "The plate is clean."),
 ("Plates & Cutlery", "das", "Besteck", "the cutlery", "fork-and-knife", "Das Besteck liegt auf dem Tisch.", "The cutlery is on the table."),
 ("Plates & Cutlery", "der", "Löffel", "the spoon", "spoon", "Ich brauche einen Löffel.", "I need a spoon."),
 ("Plates & Cutlery", "das", "Messer", "the knife", "kitchen-knife", "Das Messer ist scharf.", "The knife is sharp."),
 ("Plates & Cutlery", "die", "Schüssel", "the bowl", "bowl-with-spoon", "Die Schüssel ist voll.", "The bowl is full."),
 ("Plates & Cutlery", "die", "Tasse", "the cup", "hot-beverage", "Ich trinke eine Tasse Tee.", "I drink a cup of tea."),
 ("Plates & Cutlery", "das", "Glas", "the glass", "wine-glass", "Ein Glas Wein, bitte.", "A glass of wine, please."),
 ("Plates & Cutlery", "die", "Flasche", "the bottle", "bottle-with-popping-cork", "Die Flasche ist leer.", "The bottle is empty."),
 ("Plates & Cutlery", "die", "Stäbchen", "the chopsticks (plural)", "chopsticks", "Isst du mit Stäbchen?", "Do you eat with chopsticks?"),
 ("Cooking", "die", "Pfanne", "the frying pan", "cooking", "Die Pfanne ist heiß.", "The pan is hot."),
 ("Cooking", "der", "Topf", "the pot", "pot-of-food", "Der Topf steht auf dem Herd.", "The pot is on the stove."),
 ("Cooking", "die", "Teekanne", "the teapot", "teapot", "Die Teekanne ist warm.", "The teapot is warm."),
 ("Cooking", "die", "Eieruhr", "the kitchen timer", "timer-clock", "Die Eieruhr klingelt.", "The kitchen timer is ringing."),
 ("Cooking", "die", "Dose", "the can", "canned-food", "Ich öffne die Dose.", "I open the can."),
 ("Cooking", "der", "Korb", "the basket", "basket", "Das Brot ist im Korb.", "The bread is in the basket."),
 ("Cooking", "der", "Wasserhahn", "the tap", "potable-water", "Der Wasserhahn tropft.", "The tap is dripping."),
 ("Cleaning", "der", "Schwamm", "the sponge", "sponge", "Der Schwamm ist nass.", "The sponge is wet."),
 ("Cleaning", "die", "Seife", "the soap", "soap", "Wo ist die Seife?", "Where is the soap?"),
 ("Cleaning", "die", "Küchenrolle", "the paper towel roll", "roll-of-paper", "Wir brauchen eine Küchenrolle.", "We need a paper towel roll."),
 ("Cleaning", "der", "Mülleimer", "the trash can", "wastebasket", "Der Mülleimer ist voll.", "The trash can is full."),
 ("Cleaning", "der", "Besen", "the broom", "broom", "Der Besen steht in der Ecke.", "The broom is in the corner."),
 ("Cleaning", "der", "Eimer", "the bucket", "bucket", "Der Eimer ist leer.", "The bucket is empty."),
 ("Cleaning", "die", "Kerze", "the candle", "candle", "Die Kerze brennt.", "The candle is burning."),
 ("Food", "das", "Brot", "the bread", "bread", "Das Brot ist frisch.", "The bread is fresh."),
 ("Food", "die", "Butter", "the butter", "butter", "Die Butter ist im Kühlschrank.", "The butter is in the fridge."),
 ("Food", "das", "Ei", "the egg", "egg", "Ich koche ein Ei.", "I'm boiling an egg."),
 ("Food", "der", "Käse", "the cheese", "cheese-wedge", "Der Käse ist lecker.", "The cheese is delicious."),
 ("Food", "die", "Milch", "the milk", "glass-of-milk", "Die Milch ist kalt.", "The milk is cold."),
 ("Food", "der", "Honig", "the honey", "honey-pot", "Der Honig ist süß.", "The honey is sweet."),
 ("Food", "das", "Salz", "the salt", "salt", "Gib mir bitte das Salz.", "Please pass me the salt."),
 ("Food", "der", "Reis", "the rice", "cooked-rice", "Der Reis ist fertig.", "The rice is ready."),
 ("Food", "die", "Nudeln", "the pasta (plural)", "spaghetti", "Ich koche Nudeln.", "I'm cooking pasta."),
 ("Fruit & Vegetables", "der", "Apfel", "the apple", "red-apple", "Der Apfel ist rot.", "The apple is red."),
 ("Fruit & Vegetables", "die", "Banane", "the banana", "banana", "Die Banane ist gelb.", "The banana is yellow."),
 ("Fruit & Vegetables", "die", "Zitrone", "the lemon", "lemon", "Die Zitrone ist sauer.", "The lemon is sour."),
 ("Fruit & Vegetables", "die", "Tomate", "the tomato", "tomato", "Die Tomate ist reif.", "The tomato is ripe."),
 ("Fruit & Vegetables", "die", "Kartoffel", "the potato", "potato", "Ich schäle eine Kartoffel.", "I'm peeling a potato."),
 ("Fruit & Vegetables", "die", "Zwiebel", "the onion", "onion", "Die Zwiebel bringt mich zum Weinen.", "The onion makes me cry."),
 ("Fruit & Vegetables", "der", "Knoblauch", "the garlic", "garlic", "Ich mag Knoblauch.", "I like garlic."),
 ("Fruit & Vegetables", "die", "Karotte", "the carrot", "carrot", "Die Karotte ist orange.", "The carrot is orange."),
 ("Fruit & Vegetables", "die", "Gurke", "the cucumber", "cucumber", "Die Gurke ist grün.", "The cucumber is green."),
 ("Fruit & Vegetables", "der", "Pilz", "the mushroom", "mushroom", "Der Pilz ist klein.", "The mushroom is small."),
 ("Fruit & Vegetables", "der", "Salat", "the salad / lettuce", "green-salad", "Der Salat ist frisch.", "The salad is fresh."),
]
NAR = {"speed": 1.0}
DE = {"speed": 0.92}
TL = "FAST GERMAN"
S = []
intro = ("Welcome to the Fast German picture dictionary. Today: the kitchen. Forty-three words, each with a picture "
         "and a color. Blue is der, red is die, green is das. Look at the color, and the article sticks. "
         "Say every word out loud with me. And stay for the picture quiz at the end.")
S.append((lambda: slide(LIGHT, top_left=TL, word="The Kitchen", en="German picture dictionary · der die das", icon="cooking", icon_size=460),
          [("sfx", "whoosh"), ("tts", intro, NAR), ("sil", 0.6)]))
sec = None
for i, (s, a, w, en, ic, ex, exen) in enumerate(ITEMS):
    if s != sec:
        sec = s
        S.append((lambda s=s, ic=ic: slide(LIGHT, top_left=TL, label="NEXT", word=s, icon=ic, icon_size=360),
                  [("sfx", "whoosh"), ("tts", s, NAR), ("sil", 0.5)]))
    tr = f"{s} · {i + 1}/{len(ITEMS)}"
    S.append((lambda a=a, w=w, ic=ic, tr=tr: slide(LIGHT, top_left=TL, top_right=tr, icon=ic, icon_size=440),
              [("sfx", "pop"), ("sil", 1.2)]))
    S.append((lambda a=a, w=w, en=en, ic=ic, ex=ex, exen=exen, tr=tr: slide(LIGHT, top_left=TL, top_right=tr, icon=ic, word=f"{a} {w}", article=a,
                                                                            en=en, sub=ex, sub2=exen, icon_size=440),
              [("tts", f"{a} {w}", DE), ("sil", 0.9), ("tts", en, NAR), ("sil", 0.7), ("tts", ex, DE), ("sil", 1.3),
               ("tts", f"{a} {w}", DE), ("sil", 2.2)]))
S.append((lambda: slide(LIGHT, top_left=TL, label="QUIZ", word="Picture quiz", en="say the word with der, die or das", icon="thinking-face", icon_size=360),
          [("sfx", "swoosh_up"), ("tts", "Picture quiz! Say the word, with der, die, or das, before the answer appears.", NAR), ("sil", 0.6)]))
for i, (s, a, w, en, ic, ex, exen) in enumerate(ITEMS):
    tr = f"Quiz · {i + 1}/{len(ITEMS)}"
    S.append((lambda ic=ic, tr=tr: slide(LIGHT, top_left=TL, top_right=tr, label="QUIZ", icon=ic, icon_size=460),
              [("sfx", "tick"), ("sil", 0.9), ("sfx", "tick"), ("sil", 0.9), ("sfx", "tick"), ("sil", 0.6)]))
    S.append((lambda a=a, w=w, en=en, ic=ic, tr=tr: slide(LIGHT, top_left=TL, top_right=tr, label="QUIZ", icon=ic, word=f"{a} {w}", article=a, en=en, icon_size=440),
              [("sfx", "ding"), ("tts", f"{a} {w}", DE), ("sil", 1.0)]))
outro = "How many did you get? Tell me in the comments, and subscribe to Fast German. German in seconds, not hours."
S.append((lambda: slide(LIGHT, top_left=TL, word="German in seconds, not hours", icon="pretzel"), [("tts", outro, NAR), ("sil", 15.0)]))
print(build(S, sys.argv[1], fps=10, workers=1, crf=22))
