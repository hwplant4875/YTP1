"""Voice for short 1: one speaker (ElevenLabs Jennie) reads each line with the Korean words written in Hangul inside the
English sentence, e.g. 'Way one: native Korean. 하나. 둘. 셋.' (user, 2026-10-11), with the eleven_v3 model. Mixed lines are generated in one
request so the switch between languages sounds natural; character timestamps give each key's start/end for the animation.
Writes vo/<group>.wav, groups.json [[group, [[key, start, end], ...]], ...] (seconds within the clip)."""
import base64, hashlib, json, os, subprocess, sys
VOICE = "z6Kj0hecH20CdetSElRT"  # Jennie
MODEL = "eleven_v3"  # v3 reads the Hangul words as real Korean (v2 said "il ai saem"; user chose v3 take 2026-10-11)
CACHE = os.path.expanduser("~/.cache/k60_tts"); os.makedirs(CACHE, exist_ok=True)
G = [
 ("h1", "Koreans have two completely different ways to count...", ["Koreans have two completely different ways to count..."]),
 ("h2", "and they use BOTH in the same sentence.", ["and they use BOTH in the same sentence."]),
 ("g_n", 'Way one: native Korean. 하나. 둘. 셋.', ["Way one: native Korean.", "하나", "둘", "셋"]),
 ("g_s", 'Way two: Sino-Korean, borrowed from Chinese. 일. 이. 삼.', ["Way two: Sino-Korean, borrowed from Chinese.", "일", "이", "삼"]),
 ("c0", "So, what time is it? Three thirty.", ["So, what time is it? Three thirty."]),
 ("g_c1", "Hours use native Korean, 세 시.", ["Hours use native Korean,", "세 시"]),
 ("g_c3", "but minutes use the Chinese ones. 삼십 분.", ["but minutes use the Chinese ones.", "삼십 분"]),
 ("g_c5", "세 시 삼십 분! Two systems. One sentence.", ["세 시 삼십 분!", "Two systems. One sentence."]),
 ("g_a0", "Same with your age. With friends, you're 스물다섯 살.", ["Same with your age. With friends, you're", "스물다섯 살"]),
 ("g_a2", "But at the hospital? 이십오 세.", ["But at the hospital?", "이십오 세"]),
 ("r0", "Easy rule: counting things, hours and age? Native.", ["Easy rule: counting things, hours and age? Native."]),
 ("r1", "Money, minutes, dates and phone numbers? Chinese.", ["Money, minutes, dates and phone numbers? Chinese."]),
 ("e0", "Follow for more Korean in sixty seconds!", ["Follow for more Korean in sixty seconds!"]),
]
KEYS = {"g_n": ["n0", "n1a", "n1b", "n1c"], "g_s": ["s0", "s1a", "s1b", "s1c"], "g_c1": ["c1", "c2"], "g_c3": ["c3", "c4"],
        "g_c5": ["c5", "c6"], "g_a0": ["a0", "a1"], "g_a2": ["a2", "a3"]}
def say(text):
    h = hashlib.sha1(f"{VOICE}|{MODEL}|speed1|{text}".encode()).hexdigest()[:16]; js = f"{CACHE}/{h}.json"
    if not os.path.exists(js):
        body = {"text": text, "model_id": MODEL,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.4, "use_speaker_boost": True}}
        out = subprocess.run(["curl", "-s", "-X", "POST", f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_192",
            "-H", "xi-api-key: " + os.environ["ELEVENLABS_API_KEY"], "-H", "Content-Type: application/json", "-d", json.dumps(body)], capture_output=True, text=True).stdout
        r = json.loads(out)
        if "audio_base64" not in r: raise SystemExit(f"ElevenLabs failed: {out[:300]}")
        json.dump(r, open(js, "w"))
    return json.load(open(js))
os.makedirs("vo", exist_ok=True); groups = []
for g, text, parts in G:
    r = say(text); mp3 = f"vo/{g}.mp3"; open(mp3, "wb").write(base64.b64decode(r["audio_base64"]))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", "48000", "-ac", "2", f"vo/{g}.wav"], check=True)
    a = r["alignment"]; chars = "".join(a["characters"]); st, en = a["character_start_times_seconds"], a["character_end_times_seconds"]
    assert chars == text, (chars, text)
    keys, cur, spans = KEYS.get(g, [g]), 0, []
    for k, p in zip(keys, parts):
        i = text.index(p, cur); j = i + len(p) - 1; cur = j + 1
        spans.append([k, round(st[i], 3), round(en[j], 3)])
    groups.append([g, spans]); print(g, spans, flush=True)
json.dump(groups, open("groups.json", "w"), ensure_ascii=False, indent=1)
