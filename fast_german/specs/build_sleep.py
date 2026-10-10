"""Learn German Words While You Sleep (8 h): one ~2 h block of unique words, played 4 times.
Per word (user's order, 2026-10-10): German word, English meaning, German sentence, the same sentence slowly,
English sentence. Voice: Google Chirp 3 HD Leda (free tier), soft sleep treatment; ElevenLabs sleep music bed.
Usage: build_sleep.py OUT.mp4 [n_words] [loops]"""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
import common as C
from longform import slide, build, DARK
HERE = os.path.dirname(__file__)
words = json.load(open(os.path.join(HERE, "sleep_words_a.json"))) + json.load(open(os.path.join(HERE, "sleep_words_b.json")))
n = int(sys.argv[2]) if len(sys.argv) > 2 else 350  # ~2 h at ~20.5 s per word
loops = int(sys.argv[3]) if len(sys.argv) > 3 else 4
words = words[:n]
DE = {"engine": "google", "lang": "de-DE", "rate": 0.8}
SLOW = {"engine": "google", "lang": "de-DE", "rate": 0.6}
EN = {"engine": "google", "lang": "en-US", "rate": 0.8}
MUSIC = [os.path.join(C.CACHE, "music", "sleep_bed.mp3")]


def say(w):
    return f"{w['article']} {w['de']}." if w["article"] else f"{w['de']}."  # period: falling tone


def word_slide(w, i):
    return (lambda: slide(DARK, top_left="FAST GERMAN", top_right=f"{w['cat'].title()} · {i + 1}/{len(words)}",
                          icon=w.get("icon"), word=say(w)[:-1], article=w["article"], en=w["en"],
                          sub=w["ex_de"], sub2=w["ex_en"], icon_size=380),
            [("tts", say(w), DE), ("sil", 1.8), ("tts", w["en"] + ".", EN), ("sil", 1.8),
             ("tts", w["ex_de"], DE), ("sil", 1.5), ("tts", w["ex_de"], SLOW), ("sil", 1.5),
             ("tts", w["ex_en"], EN), ("sil", 3.0)])


intro = ("Welcome to Fast German. Get comfortable, close your eyes, and just listen. "
         "You'll hear useful German words, each with a short example, said once, and then slowly. "
         "You don't need to remember anything. Just relax, and let the words come to you.")
INTRO = [(lambda: slide(DARK, top_left="FAST GERMAN", word="German words", en="while you sleep", icon="crescent-moon"),
          [("sil", 1.5), ("tts", intro, EN), ("sil", 3.0)])]
CORE = [word_slide(w, i) for i, w in enumerate(words)]
OUTRO = [(lambda: slide(DARK, top_left="FAST GERMAN", word="Gute Nacht", en="good night", icon="crescent-moon"),
          [("tts", "Gute Nacht.", DE), ("sil", 1.5), ("tts", "Good night. Sleep well.", EN), ("sil", 20.0)])]
rain = "anoisesrc=color=brown:amplitude=0.02:sample_rate=48000,lowpass=f=500,highpass=f=60"
kw = dict(fps=5, bed=rain, workers=8, crf=28, lufs=-22, music=MUSIC, music_vol=0.22, voice_fx=C.SLEEP_VOICE_FX)

out = sys.argv[1]
if loops <= 1:
    print(build(INTRO + CORE + OUTRO, out, **kw))
    sys.exit()
# Build the three parts once, then join with stream copy: intro, core x loops, outro.
tmp = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(out)))
parts = {k: os.path.join(tmp, k + ".mp4") for k in ("intro", "core", "outro")}
for k, S in (("intro", INTRO), ("core", CORE), ("outro", OUTRO)):
    print(k, build(S, parts[k], **kw), flush=True)
lst = os.path.join(tmp, "list.txt")
open(lst, "w").write("".join(f"file '{p}'\n" for p in [parts["intro"]] + [parts["core"]] * loops + [parts["outro"]]))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                "-movflags", "+faststart", out], check=True)
print("total", C.duration(out))
