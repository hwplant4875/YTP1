"""Sleep-video voices: Korean = Typecast 한준, English = Google Chirp3-HD Charon. Cached by text."""
import os, json, base64, hashlib, subprocess, urllib.request
CACHE = os.path.expanduser("~/.cache/k60_sleep"); os.makedirs(CACHE, exist_ok=True)
TC_VOICE = "tc_618b1849ef7827cfea34ea1e"
G_VOICE = "en-US-Chirp3-HD-Charon"
TRIM = "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse"
def _dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
def _finish(raw, wav):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", TRIM, "-ar", "48000", "-ac", "1", wav], check=True); os.remove(raw)
def korean(text, tempo=0.9):
    wav = f"{CACHE}/ko_{hashlib.sha1(f'{TC_VOICE}|{tempo}|{text}'.encode()).hexdigest()[:16]}.wav"
    if not os.path.exists(wav):
        body = {"voice_id": TC_VOICE, "text": text, "model": "ssfm-v30", "language": "kor",
                "prompt": {"emotion_preset": "normal", "emotion_intensity": 1.0}, "output": {"audio_format": "wav", "audio_tempo": tempo}}
        raw = wav + ".raw"
        code = subprocess.run(["curl", "-s", "-X", "POST", "https://api.typecast.ai/v1/text-to-speech", "-H", "X-API-KEY: " + os.environ["TYPECAST_API_KEY"],
            "-H", "Content-Type: application/json", "-d", json.dumps(body, ensure_ascii=False), "-o", raw, "-w", "%{http_code}"], capture_output=True, text=True).stdout
        if code != "200": raise SystemExit(f"Typecast failed ({code}) for {text!r}: {open(raw, errors='replace').read()[:200]}")
        _finish(raw, wav)
    return wav, _dur(wav)
def english(text, rate=0.9):
    wav = f"{CACHE}/en_{hashlib.sha1(f'{G_VOICE}|{rate}|{text}'.encode()).hexdigest()[:16]}.wav"
    if not os.path.exists(wav):
        body = {"input": {"text": text}, "voice": {"languageCode": "en-US", "name": G_VOICE},
                "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 48000, "speakingRate": rate}}
        r = urllib.request.Request("https://texttospeech.googleapis.com/v1/text:synthesize?key=" + os.environ["GOOGLE_TTS_API_KEY"],
                                   data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        raw = wav + ".raw"; open(raw, "wb").write(base64.b64decode(json.load(urllib.request.urlopen(r))["audioContent"]))
        _finish(raw, wav)
    return wav, _dur(wav)
