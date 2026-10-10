"""Learn 500 German Words While You Sleep: part 1 word/meaning/example, part 2 quick review."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from longform import slide, build, DARK
HERE = os.path.dirname(__file__)
words = json.load(open(os.path.join(HERE, "sleep_words_a.json"))) + json.load(open(os.path.join(HERE, "sleep_words_b.json")))
if len(sys.argv) > 2:
    words = words[: int(sys.argv[2])]
DE = {"speed": 0.88, "stability": 0.75, "style": 0.05}
EN = {"speed": 0.92, "stability": 0.75, "style": 0.05}

def say(w):
    return f"{w['article']} {w['de']}" if w["article"] else w["de"]

S = []
intro = ("Welcome to Fast German. Get comfortable, close your eyes, and just listen. "
         "Tonight you'll hear five hundred useful German words, each with a short example. "
         "You don't need to remember anything. Just relax, and let the words come to you.")
S.append((lambda: slide(DARK, top_left="FAST GERMAN", word="500 German words", en="while you sleep", icon="crescent-moon"),
          [("sil", 1.5), ("tts", intro, EN), ("sil", 3.0)]))
cat = None
for i, w in enumerate(words):
    aud = []
    if w["cat"] != cat:
        cat = w["cat"]
    S.append((lambda w=w, i=i: slide(DARK, top_left="FAST GERMAN", top_right=f"{w['cat'].title()} · {i + 1}/{len(words)}",
                                     icon=w.get("icon"), word=say(w), article=w["article"], en=w["en"],
                                     sub=w["ex_de"], sub2=w["ex_en"], icon_size=380),
              [("tts", say(w), DE), ("sil", 1.5), ("tts", w["en"], EN), ("sil", 1.5), ("tts", w["ex_de"], DE),
               ("sil", 2.0), ("tts", say(w), DE), ("sil", 2.5)]))
review = "Now, a gentle review. Just the words, one more time."
S.append((lambda: slide(DARK, top_left="FAST GERMAN", word="Gentle review", en="just listen", icon="crescent-moon"),
          [("sil", 2.0), ("tts", review, EN), ("sil", 3.0)]))
for i, w in enumerate(words):
    S.append((lambda w=w, i=i: slide(DARK, top_left="FAST GERMAN", top_right=f"Review · {i + 1}/{len(words)}",
                                     icon=w.get("icon"), word=say(w), article=w["article"], en=w["en"], icon_size=380),
              [("tts", say(w), DE), ("sil", 1.3), ("tts", w["en"], EN), ("sil", 2.2)]))
outro = "Gute Nacht. Good night. Sleep well, and see you tomorrow on Fast German."
S.append((lambda: slide(DARK, top_left="FAST GERMAN", word="Gute Nacht", en="good night", icon="crescent-moon"),
          [("tts", outro, EN), ("sil", 20.0)]))
rain = "anoisesrc=color=brown:amplitude=0.035:sample_rate=48000,lowpass=f=600,highpass=f=60"
print(build(S, sys.argv[1], fps=5, bed=rain, workers=3, crf=28, lufs=-20,
            music=['/mnt/project-files/fast_german/cache/music/incompetech/Deep Relaxation.mp3'], music_vol=0.12))  # Kevin MacLeod, CC BY 4.0, credit in description
