"""Sleep-video voices: Korean = Typecast 한준, English = Google Chirp3-HD Charon. Cached by text."""
import os, json, base64, hashlib, subprocess, urllib.request, time, html
CACHE = os.path.expanduser("~/.cache/k60_sleep"); os.makedirs(CACHE, exist_ok=True)
TC_VOICE = os.environ.get("K60_KO_VOICE", "tc_618b1849ef7827cfea34ea1e")  # override for voice auditions
G_VOICE = "en-US-Chirp3-HD-Charon"
# calm, statement-like context so Smart Emotion reads each line as a quiet bedtime statement, not a question
SMART_PREV = "오늘 밤도 천천히, 편안하게 한국어를 들어 볼게요."
SMART_NEXT = "천천히 따라 해 보세요. 편안하게 쉬어요."
# trim both ends, then a short fade at the tail so a trimmed ending never clicks
TRIM = "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,afade=t=in:d=0.08,areverse"
def _dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
def _finish(raw, wav):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", TRIM, "-ar", "48000", "-ac", "1", wav], check=True); os.remove(raw)
def ending(wav):
    """Pitch change in semitones from mid-phrase to the last quarter of the voiced audio (negative = falls). Measurement only."""
    import numpy as np, parselmouth
    f = parselmouth.Sound(wav).to_pitch(time_step=0.01, pitch_floor=60, pitch_ceiling=300).selected_array["frequency"]; f = f[f > 0]; n = len(f)
    return 0.0 if n < 10 else float(12 * np.log2(np.median(f[int(n * .75):]) / np.median(f[int(n * .3):int(n * .6)])))
def korean(text, tempo=0.9, voice=None, emotion=None, takes=None):
    """emotion: a preset name (normal, tonedown, ...), "preset:intensity", or "smart" (context-aware, calm bedtime context).
    takes: Typecast output varies per request, so ask again (up to this many times) until a take ends with a falling tone,
    and keep the take that falls most. The audio itself is never pitch-edited."""
    takes = takes or int(os.environ.get("K60_KO_TAKES", "5"))
    voice = voice or TC_VOICE; emotion = emotion or os.environ.get("K60_KO_EMOTION", "normal")
    key = f'{voice}|{tempo}|{emotion}|falling-take|{text}'
    wav = f"{CACHE}/ko_{hashlib.sha1(key.encode()).hexdigest()[:16]}.wav"
    if not os.path.exists(wav):
        if emotion == "smart":
            prompt = {"emotion_type": "smart", "previous_text": SMART_PREV, "next_text": SMART_NEXT}
        else:
            name, _, k = emotion.partition(":")
            prompt = {"emotion_type": "preset", "emotion_preset": name, "emotion_intensity": float(k or 1.0)}
        body = {"voice_id": voice, "text": text, "model": "ssfm-v30", "language": "kor",
                "prompt": prompt, "output": {"audio_format": "wav", "audio_tempo": tempo}}
        best = None
        for take in range(takes):
            _typecast(body, wav, text)
            e = ending(wav)
            if best is None or e < best[0]: best = (e, take); os.replace(wav, wav + ".best")
            if e <= -1.5: break
        os.replace(wav + ".best", wav)
    return wav, _dur(wav)
def _typecast(body, wav, text):
    raw = wav + ".raw"
    for attempt in range(6):  # rate limits and dropped connections happen on long runs
        code = subprocess.run(["curl", "-s", "-X", "POST", "https://api.typecast.ai/v1/text-to-speech", "-H", "X-API-KEY: " + os.environ["TYPECAST_API_KEY"],
            "-H", "Content-Type: application/json", "-d", json.dumps(body, ensure_ascii=False), "-o", raw, "-w", "%{http_code}"], capture_output=True, text=True).stdout
        if code == "200": break
        time.sleep(2 ** attempt)
    else:
        msg = open(raw, errors="replace").read()[:200] if os.path.exists(raw) else ""
        raise SystemExit(f"Typecast failed ({code}) for {text!r}: {msg}")
    _finish(raw, wav)
def english(text, rate=0.9):
    wav = f"{CACHE}/en_{hashlib.sha1(f'{G_VOICE}|{rate}|ssml|{text}'.encode()).hexdigest()[:16]}.wav"
    if not os.path.exists(wav):
        # trailing break: without it Google sometimes cuts off the last sound of a sentence
        body = {"input": {"ssml": f"<speak>{html.escape(text)}<break time=\"600ms\"/></speak>"}, "voice": {"languageCode": "en-US", "name": G_VOICE},
                "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 48000, "speakingRate": rate}}
        r = urllib.request.Request("https://texttospeech.googleapis.com/v1/text:synthesize?key=" + os.environ["GOOGLE_TTS_API_KEY"],
                                   data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        raw = wav + ".raw"
        # Chirp 3 HD has a per-minute request quota, so 429s need waits of up to a minute
        for attempt in range(12):
            try: open(raw, "wb").write(base64.b64decode(json.load(urllib.request.urlopen(r, timeout=60))["audioContent"])); break
            except Exception:
                if attempt == 11: raise
                time.sleep(min(60, 2 ** attempt))
        _finish(raw, wav)
    return wav, _dur(wav)
