"""Shared helpers for Fast German: TTS (ElevenLabs, cached), icons, sound effects, ffmpeg."""
import base64
import hashlib
import io
import json
import os
import re
import subprocess
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Generated audio and rasterized icons live in the shared project folder so later sessions reuse them.
CACHE = os.environ.get("FG_CACHE", "/mnt/project-files/fast_german/cache")
os.makedirs(CACHE, exist_ok=True)

VOICE = "rKiu7lQ4c5P3az3745s3"  # Carla Blum - Confident and Informative (sample 6-Carla, user's pick 2026-10-09)
MODEL = "eleven_multilingual_v2"
KEY = os.environ.get("ELEVENLABS_API_KEY", "")

# der / die / das colors: the channel signature, identical in every video.
GENDER = {"der": (47, 111, 237), "die": (229, 72, 77), "das": (34, 160, 80), None: (28, 28, 30)}
CREAM = (255, 246, 229)
INK = (28, 28, 30)
YELLOW = (255, 201, 60)
FONT = os.path.join(ROOT, "assets", "fonts", "Fredoka.ttf")


def _post(url, body):
    import time
    import urllib.error
    for attempt in range(12):
        req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                     headers={"xi-api-key": KEY, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            code = getattr(e, "code", None)
            if attempt == 11 or (code is not None and code not in (429, 500, 502, 503, 504)):
                raise
            time.sleep(min(60, 2 ** attempt * 2) + attempt)


def tts(text, speed=1.0, stability=0.45, style=0.3):
    """Return (mp3_path, alignment dict with chars + start/end times). Cached by text and settings."""
    settings = {"stability": stability, "similarity_boost": 0.8, "style": style, "speed": speed}
    h = hashlib.sha1(json.dumps([VOICE, MODEL, text, settings]).encode()).hexdigest()[:16]
    mp3 = os.path.join(CACHE, "tts", h + ".mp3")
    js = os.path.join(CACHE, "tts", h + ".json")
    if not os.path.exists(mp3):
        os.makedirs(os.path.dirname(mp3), exist_ok=True)
        raw = _post(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128",
                    {"text": text, "model_id": MODEL, "voice_settings": settings})
        d = json.loads(raw)
        open(mp3, "wb").write(base64.b64decode(d["audio_base64"]))
        json.dump({"text": text, "alignment": d.get("normalized_alignment") or d.get("alignment")}, open(js, "w"))
    return mp3, json.load(open(js))["alignment"]


def words_from_alignment(al):
    """Group character timings into words: [(word, start, end)]."""
    out, cur, st, en = [], "", None, None
    for ch, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch.isspace():
            if cur:
                out.append((cur, st, en))
            cur, st = "", None
            continue
        if st is None:
            st = s
        cur += ch
        en = e
    if cur:
        out.append((cur, st, en))
    return out


MIXKIT = os.path.join(ROOT, "assets", "sfx_mixkit")
# Mixkit free sound effects (mixkit.co/license): fallback when the Drive copies are missing.
MIXKIT_SFX = {"pop": "pop.mp3", "ding": "ding.mp3", "start": "attention.mp3", "buzz": "buzz.mp3", "snap": "snap.mp3",
              "whoosh": "whoosh.mp3", "tick": "bubble.mp3", "swoosh_up": "sparkle.mp3",
              "clock": "bubble.mp3"}
# The user's own SFX from Google Drive "효과음 ALL" (copied 2026-10-09). Preferred over Mixkit.
DRIVE_SFX_DIR = "/mnt/project-files/sfx/drive"
SFX = {
    "start": "026_띠딩2.mp3",                  # very first sound of every short
    "pop": "038_뿅.mp3",                       # word appears
    "whoosh": "041_바람.mp3",                  # transition to the next beat
    "ding": "049_띠룽 (슈퍼마리오 코인먹).mp3",  # correct answer / reveal
    "tick": "056_띠동띠동(물음표).mp3",          # question / guess moment
    "clock": "077_째깍째깍 (시계).mp3",          # quiz thinking time
    "swoosh_up": "032_뾰로롱 마법.WAV",         # follow ending
    "buzz": "063_삐삑 (오답 -짧은).mp3",
    "snap": "078_찰칵 (카메라).mp3",
}
SFX["hit"] = SFX["start"]


def get_sfx(name, max_len=1.2, peak_db=-3.0):
    """SFX as a cached wav: leading silence removed (so it plays on the cut), cut to max_len with a fade,
    peak-normalized so every sound starts at the same level and SFX_VOL alone sets the mix."""
    max_len = {"clock": 3.0}.get(name, max_len)
    src = os.path.join(DRIVE_SFX_DIR, SFX[name])
    if not os.path.exists(src):
        return os.path.join(MIXKIT, MIXKIT_SFX[name])
    out = os.path.join(CACHE, "sfx", f"{name}_{hashlib.sha1((SFX[name] + str(max_len)).encode()).hexdigest()[:8]}.wav")
    if not os.path.exists(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        cut = (f"silenceremove=start_periods=1:start_threshold=-45dB,atrim=0:{max_len},"
               f"afade=t=out:st={max(0, max_len - 0.3)}:d=0.3")
        r = subprocess.run(["ffmpeg", "-v", "info", "-i", src, "-af", cut + ",volumedetect", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        peak = float(re.search(r"max_volume: (-?[\d.]+) dB", r).group(1))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", f"{cut},volume={peak_db - peak}dB",
                        "-ar", "44100", "-ac", "2", out + ".tmp.wav"], check=True)
        os.replace(out + ".tmp.wav", out)
    return out


def icon(name, size):
    """Fluent emoji (flat style, MIT) rasterized to RGBA PNG of given size."""
    from PIL import Image
    png = os.path.join(CACHE, "icons", f"{name}_{size}.png")
    if not os.path.exists(png):
        import cairosvg
        os.makedirs(os.path.dirname(png), exist_ok=True)
        svg_path = os.path.join(CACHE, "icons", name + ".svg")
        if not os.path.exists(svg_path):
            url = f"https://cdn.jsdelivr.net/npm/fluentui-emoji@1.3.0/icons/flat/{name}.svg"
            open(svg_path, "wb").write(urllib.request.urlopen(url, timeout=60).read())
        cairosvg.svg2png(url=svg_path, write_to=png, output_width=size, output_height=size)
    return Image.open(png).convert("RGBA")


def duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", path]).strip())


def music(name, prompt, seconds=60):
    """Instrumental bed from ElevenLabs Music, cached by name."""
    path = os.path.join(CACHE, "music", name + ".mp3")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = _post("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128",
                     {"prompt": prompt, "music_length_ms": int(seconds * 1000), "force_instrumental": True})
        open(path, "wb").write(data)
    return path


KPOP_BED = ("Light, bright K-pop style instrumental background music for a cute language-learning video. "
            "Bouncy synth plucks, soft claps, warm bass, catchy but simple, mid tempo around 105 bpm, no vocals, "
            "no drops, steady energy, loop-friendly, sits quietly under a voice-over.")


GOOGLE_VOICE = "Chirp3-HD-Leda"  # sleep videos (user's pick 2026-10-10); free tier of Google Cloud TTS
# Warm, soft "sleep" treatment for the Google voice: fewer highs and harshness, gentle compression, tiny room.
SLEEP_VOICE_FX = ("highpass=f=70,lowshelf=g=2:f=180,equalizer=f=3500:t=q:w=1.2:g=-4,highshelf=g=-6:f=7000,"
                  "lowpass=f=9000,acompressor=threshold=-24dB:ratio=2.5:attack=20:release=250,aecho=0.8:0.5:40:0.12")


def gtts(text, lang="de-DE", rate=0.8, voice=GOOGLE_VOICE):
    """Google Cloud TTS (key in GOOGLE_TTS_API_KEY), cached wav path. Isolated words keep their trailing period
    so they end on a falling tone. Plain-text requests were sometimes cut off mid-sound at the end (~13 % of clips),
    so the text goes in as SSML with a trailing break, and the clip gets short fades."""
    h = hashlib.sha1(json.dumps(["google-ssml", voice, lang, text, rate]).encode()).hexdigest()[:16]
    out = os.path.join(CACHE, "gtts", h + ".wav")
    if not os.path.exists(out):
        import time
        import urllib.error
        os.makedirs(os.path.dirname(out), exist_ok=True)
        from xml.sax.saxutils import escape
        body = {"input": {"ssml": f'<speak>{escape(text)}<break time="600ms"/></speak>'}, "voice": {"languageCode": lang, "name": f"{lang}-{voice}"},
                "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 24000, "speakingRate": rate}}
        for attempt in range(8):
            try:
                req = urllib.request.Request(
                    "https://texttospeech.googleapis.com/v1/text:synthesize?key=" + os.environ["GOOGLE_TTS_API_KEY"],
                    data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
                d = json.load(urllib.request.urlopen(req, timeout=60))
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
                if attempt == 7 or getattr(e, "code", 429) not in (429, 500, 503):
                    raise
                time.sleep(2 ** attempt)
        import io
        import wave
        import numpy as np
        with wave.open(io.BytesIO(base64.b64decode(d["audioContent"]))) as w:  # parses chunks; data only
            sr, a = w.getframerate(), np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
        fi, fo = min(len(a), sr // 100), min(len(a), sr * 8 // 100)  # 10 ms in, 80 ms out
        a[:fi] *= np.linspace(0, 1, fi)
        a[len(a) - fo:] *= np.linspace(1, 0, fo)
        with wave.open(out + ".tmp", "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(a.astype(np.int16).tobytes())
        os.replace(out + ".tmp", out)
    return out
