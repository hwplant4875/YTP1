"""Voice clips for short 1 (vo/<key>.wav).
English narration: ElevenLabs Jennie via the shared engine (speed 1.0).
Korean words: a native Korean Typecast voice (user, 2026-10-11), cut in between the English lines."""
import json, os, shutil, subprocess, sys
sys.path.insert(0, "/home/user/YTP1/koreanin60s/engine"); sys.path.insert(0, "/home/user/YTP1/koreanin60s/longform/002-sleep-2h")
from engine import tts
from voices import korean
KO_VOICE = "tc_5eb55ce920d1b60016e91de6"  # Typecast 민지 (Minji), young female
os.makedirs("vo", exist_ok=True)
L = [x for x in json.load(open("lines.json")) if x[0] not in ("n1", "s1")]
L += [["n1a", "ko", "하나."], ["n1b", "ko", "둘."], ["n1c", "ko", "셋."], ["s1a", "ko", "일."], ["s1b", "ko", "이."], ["s1c", "ko", "삼."]]
for k, lang, text in L:
    if lang == "ko":
        src, d = korean(text, 1.0, voice=KO_VOICE, takes=3)
        # match the English clips' format (48 kHz stereo)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ar", "48000", "-ac", "2", f"vo/{k}.wav"], check=True)
    else:
        src, d = tts(text, lang); shutil.copy(src, f"vo/{k}.wav")
    print(k, lang, text, round(d, 2), flush=True)
