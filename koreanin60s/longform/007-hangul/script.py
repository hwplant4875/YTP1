"""Long-form #7: Learn the Korean Alphabet in 15 Minutes. Each beat = one TTS request; each segment = (spoken sentence, visual).
Visual kinds: S statement (html), L one big letter/word (big, rom, note), B block build (parts, res, rom), R row of letters (items, hi),
Q quiz (word, rom, mean): the answer shows when the NEXT segment starts. Korean is written in Hangul inside the English sentence
(Jennie v3 reads both); single vowels/consonants are spoken as syllables (아, 기역) and shown as jamo on screen."""

def S(html, **k): return dict(k="S", html=html, **k)
def L(big, rom="", note="", c="p"): return dict(k="L", big=big, rom=rom, note=note, c=c)
def B(parts, res, rom="", note=""): return dict(k="B", parts=parts, res=res, rom=rom, note=note)
def R(items, hi=None, note=""): return dict(k="R", items=items, hi=hi, note=note)
def I(img, html): return dict(k="I", img=img, html=html)  # real photo in a white card + text beside it

CHAPTERS = [
 {"q": "The secret of Hangul", "pose": "point_idea", "beats": [
  [("Korean looks like a wall of circles and lines. But you can learn to read it in fifteen minutes.",
    S("<span class='ko'>안녕하세요</span><br><span class='pill'>READ IT IN 15 MIN</span>"))],
  [("In fourteen forty-three, King Sejong created this alphabet, so that anyone could read.", I("sejong", "<b class='num'>1443</b><br>King Sejong 👑<br>made it for <em>everyone</em>")),
   ("He wrote: a wise person can learn it before the morning is over. Even a slow learner, in ten days.",
    I("haerye", "“A wise person<br>learns it in<br><em>one morning</em>.”<small>Hunminjeongeum Haerye, 1446</small>"))],
  [("It's called 한글.", L("한글", "han-geul", "the Korean alphabet"))],
  [("Here's the secret. Every syllable is a little block, like Lego.", S("🧱 1 block = <em>1 syllable</em>")),
   ("Put a consonant and a vowel together, and you get one block.", B(["ㅎ", "ㅏ"], "하", "ha")),
   ("Add one more letter at the bottom, and it becomes 한.", B(["하", "ㄴ"], "한", "han")),
   ("Two blocks, 한글. That's the whole system.", B(["한", "글"], "한글", "han-geul", "= Hangul"))]]},
 {"q": "The vowels", "pose": "glasses_study", "beats": [
  [("Let's start with the vowels. They're built from just three shapes.", R(["•", "ㅡ", "ㅣ"])),
   ("A dot for the sky, a flat line for the earth, and a standing line for people.", R(["• ☀️", "ㅡ 🌏", "ㅣ 🧍"], note="sky · earth · people"))],
  [("Stick a short stroke on the right of the standing line, and you get 아.", L("ㅏ", "a", "as in ‘father’", "p")),
   ("Move it to the left, and it becomes 어.", L("ㅓ", "eo", "as in ‘up’", "b")),
   ("Put it on top of the flat line: 오.", L("ㅗ", "o", "as in ‘go’", "y")),
   ("And underneath: 우.", L("ㅜ", "u", "as in ‘moon’", "m"))],
  [("See? The stroke moves, and the sound changes.", R(["ㅏ", "ㅓ", "ㅗ", "ㅜ"], note="a · eo · o · u"))]]},
]
OUTRO = []
