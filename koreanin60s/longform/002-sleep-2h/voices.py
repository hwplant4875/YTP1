"""Sleep-video voices: Korean = Typecast 한준, English = Google Chirp3-HD Charon. Cached by text."""
import os, json, base64, hashlib, subprocess, urllib.request, time, html
CACHE = os.path.expanduser("~/.cache/k60_sleep"); os.makedirs(CACHE, exist_ok=True)
TC_VOICE = "tc_618b1849ef7827cfea34ea1e"
G_VOICE = "en-US-Chirp3-HD-Charon"
# trim both ends, then a short fade at the tail so a trimmed ending never clicks
TRIM = "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,afade=t=in:d=0.08,areverse"
def _dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
def _finish(raw, wav):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", TRIM, "-ar", "48000", "-ac", "1", wav], check=True); os.remove(raw)
def korean(text, tempo=0.9):
    wav = f"{CACHE}/ko_{hashlib.sha1(f'{TC_VOICE}|{tempo}|{text}'.encode()).hexdigest()[:16]}.wav"
    if not os.path.exists(wav):
        body = {"voice_id": TC_VOICE, "text": text, "model": "ssfm-v30", "language": "kor",
                "prompt": {"emotion_preset": "normal", "emotion_intensity": 1.0}, "output": {"audio_format": "wav", "audio_tempo": tempo}}
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
    return wav, _dur(wav)
def english(text, rate=0.9):
    wav = f"{CACHE}/en_{hashlib.sha1(f'{G_VOICE}|{rate}|ssml|{text}'.encode()).hexdigest()[:16]}.wav"
    if not os.path.exists(wav):
        # trailing break: without it Google sometimes cuts off the last sound of a sentence
        body = {"input": {"ssml": f"<speak>{html.escape(text)}<break time=\"600ms\"/></speak>"}, "voice": {"languageCode": "en-US", "name": G_VOICE},
                "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 48000, "speakingRate": rate}}
        r = urllib.request.Request("https://texttospeech.googleapis.com/v1/text:synthesize?key=" + os.environ["GOOGLE_TTS_API_KEY"],
                                   data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        raw = wav + ".raw"
        for attempt in range(6):
            try: open(raw, "wb").write(base64.b64decode(json.load(urllib.request.urlopen(r, timeout=60))["audioContent"])); break
            except Exception:
                if attempt == 5: raise
                time.sleep(2 ** attempt)
        _finish(raw, wav)
    return wav, _dur(wav)
