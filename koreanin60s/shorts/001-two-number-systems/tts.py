"""Voice clips for short 1 (vo/<key>.wav) via the shared engine (ElevenLabs Jennie, speed 1.0, Korean lines with language_code ko)."""
import json, os, shutil, sys
sys.path.insert(0, "/home/user/YTP1/koreanin60s/engine")
from engine import tts
os.makedirs("vo", exist_ok=True)
L = [x for x in json.load(open("lines.json")) if x[0] not in ("n1", "s1")]
L += [["n1a", "ko", "하나."], ["n1b", "ko", "둘."], ["n1c", "ko", "셋."], ["s1a", "ko", "일."], ["s1b", "ko", "이."], ["s1c", "ko", "삼."]]
for k, lang, text in L:
    wav, d = tts(text, lang); shutil.copy(wav, f"vo/{k}.wav"); print(k, lang, text, round(d, 2), flush=True)
