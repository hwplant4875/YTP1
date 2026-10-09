"""Shared helpers for Fast German: TTS (ElevenLabs, cached), icons, sound effects, ffmpeg."""
import base64
import hashlib
import io
import json
import os
import subprocess
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Generated audio and rasterized icons live in the shared project folder so later sessions reuse them.
CACHE = os.environ.get("FG_CACHE", "/mnt/project-files/fast_german/cache")
os.makedirs(CACHE, exist_ok=True)

VOICE = "K75lPKuh15SyVhQC1LrE"  # Carola - Sharp and Clear (chosen 2026-10-09)
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
# Mixkit free sound effects (mixkit.co/license, free for videos, no attribution). name -> file
SFX = {
    "pop": "pop.mp3",
    "ding": "ding.mp3",
    "start": "attention.mp3",
    "buzz": "buzz.mp3",
    "snap": "snap.mp3",
    "whoosh": "whoosh.mp3",
    "tick": "bubble.mp3",
    "swoosh_up": "sparkle.mp3",
}
SFX["hit"] = SFX["start"]  # the heavy sub hit was dropped (2026-10-09 feedback)


def get_sfx(name):
    return os.path.join(MIXKIT, SFX[name])


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
        open(path, "wb").write(_post("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128",
                                     {"prompt": prompt, "music_length_ms": int(seconds * 1000),
                                      "force_instrumental": True}))
    return path


KPOP_BED = ("Light, bright K-pop style instrumental background music for a cute language-learning video. "
            "Bouncy synth plucks, soft claps, warm bass, catchy but simple, mid tempo around 105 bpm, no vocals, "
            "no drops, steady energy, loop-friendly, sits quietly under a voice-over.")
