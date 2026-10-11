"""ORBIS Short #1 'The train that never stopped' (vertical 1080x1920). Writes short1.json next to this file.

Render (from the longform dir):
  LONGFORM_W=1080 LONGFORM_H=1920 LONGFORM_CACHE=episodes/01_ghost_stations/cache \
    python3 assemble.py episodes/01_ghost_stations/short1.json episodes/01_ghost_stations/out/short1.mp4

Narration: ElevenLabs eleven_v4, Mattes, speed 1.0. No subtitles; a few big key words only, kept out of the bottom 25 %
(Shorts UI). Portrait framing: scenes/s1_*.js wrap the episode scenes with a portrait camera tweak per shot.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
AMB = "&H005CB2FF"     # #FFB25C as ASS BGR
RED = "&H2A2AE6&"      # red ring / arrow


def v3(scene, shot, t0=0):
    return {"type": "3d", "scene": scene, "shot": shot, "t0": t0}


def key(word, y=0.36, delay=0.0, extend=0.0):
    """big centred key word (YEAR style: YouTube Sans Black, amber, black outer stroke)"""
    return {"kind": "year", "content": word, "pos": [0.5, y], "delay": delay, "extend": extend}


def ring(cx, cy, rx, ry, delay=0.3, extend=0.0):
    """red ellipse drawn around a subject (pixel coords), pops in"""
    k = 0.5523
    pts = (f"m {rx} 0 b {rx + k * rx:.0f} 0 {2 * rx} {ry - k * ry:.0f} {2 * rx} {ry} "
           f"b {2 * rx} {ry + k * ry:.0f} {rx + k * rx:.0f} {2 * ry} {rx} {2 * ry} "
           f"b {rx - k * rx:.0f} {2 * ry} 0 {ry + k * ry:.0f} 0 {ry} "
           f"b 0 {ry - k * ry:.0f} {rx - k * rx:.0f} 0 {rx} 0")
    body = ("{\\an5\\bord10\\shad0\\1a&HFF&\\3c" + RED + "\\blur0.8\\fscx135\\fscy135\\t(0,260,\\fscx100\\fscy100)\\p1}"
            + pts + "{\\p0}")
    return {"kind": "label", "content": body, "pos": [cx / W, cy / H], "delay": delay, "extend": extend}


TRAIN_PASS = {"prompt": "subway train rushing past through an empty underground station, rattling wheels, whoosh, echo", "len": 6,
              "vol": 0.22, "at": 0.3}
HIT = {"prompt": "deep cinematic sub boom hit with short metallic tail", "len": 2.5, "vol": 0.3}
AMBIENT = {"prompt": "empty underground subway station ambience, faint electrical hum, distant water drips, low air rumble",
           "len": 22, "vol": 0.16, "at": 0}

B = []


def say(line, visual="same", **kw):
    B.append({"say": line, "visual": visual, **kw})


# hook: the train rushes through, the guard on the dark platform
say("For twenty-eight years, this train never stopped.", v3("s1_intro", "passby", 0.4), id="intro",
    text=key("NEVER\\NSTOPPED", 0.34, 0.15), sfx=[TRAIN_PASS, AMBIENT])
say("And on the platform, someone was always watching.", v3("s1_intro", "guard", 2.2),
    text=ring(540, 960, 200, 420, 0.9), sfx=dict(HIT, at=0.9, vol=0.22))
# context
say("In 1961, the Berlin Wall split the city in two.", v3("s1_section", "stack", 0), text=key("1961", 0.30, 0.35))
say("But West Berlin's U6, U8 and S-Bahn trains still ran right underneath the East.")
say("So East Germany sealed sixteen stations.",
    {"type": "g2d", "name": "c19_short", "module": "short_graphics.py", "args": {"mode": "stations", "keys": [[1.0, 0.56, 0.5], [1.06, 0.56, 0.5]]}}, hold=0.5)
say("Entrances were bricked up. The stations vanished from the maps.", v3("s1_walk", "title", 0))
# the ghost platforms
say("On the dark platforms, armed guards stood watch,", v3("s1_watch", "guardroom", 0))
say("so no one could jump aboard.", v3("s1_watch", "teaser", 0.6))
say("West Berliners rolled past, staring out at stations frozen in time.", v3("s1_watch", "windows", 3.6))
say("Barbed wire lined the edges.", v3("s1_walk", "wire", 0))
say("A few people risked the tracks to escape. Most never made it.", v3("s1_escape", "rare", 1.0))
say("And for twenty-eight years, the trains just kept rolling through.", v3("s1_watch", "nostop", 0.2),
    text=key("28 YEARS", 0.30, 0.6), hold=0.3)
# end card
say("Full story on Orbis.", v3("s1_endcard", "amber", 0), id="end_card", hold=0.4, trans="dip",
    text=[{"kind": "label", "content": "FULL STORY ON", "pos": [0.5, 0.575], "delay": 0.15},
          {"kind": "title", "content": "ORBIS", "pos": [0.5, 0.655], "delay": 0.35}],
    sfx=dict(HIT, vol=0.2, at=0.05))

spec = {
    "voice": {"engine": "elevenlabs", "voice_id": "DrBEKFgWMDWUG6bjTSTk", "model": "eleven_v4", "stability": 0.5, "speed": 1.0},
    "gap": 0.1,
    "subtitles": False,
    "declick": True,
    "sfx_gain_db": -6,
    "style_fields": {
        # key words: big, amber, black outer stroke
        "YEAR": {"Fontsize": 200, "PrimaryColour": AMB, "Outline": 11, "Shadow": 0, "Spacing": 2},
        "LABEL": {"Fontsize": 84, "PrimaryColour": AMB, "Outline": 7, "Shadow": 0, "Spacing": 6},
        "TITLE": {"Fontsize": 230, "PrimaryColour": "&H00D0DCE4", "Outline": 0, "Shadow": 0, "Spacing": 14},
    },
    "fonts": {"YEAR": "YouTube Sans", "LABEL": "YouTube Sans", "TITLE": "Playfair Display", "FX": "YouTube Sans"},
    "music": [{"file": "music/m1_intro.mp3", "from": "intro", "to": "end", "vol": 0.17, "fade_in": 0.6, "fade_out": 1.2}],
    "beats": B,
}
json.dump(spec, open(os.path.join(HERE, "short1.json"), "w"), ensure_ascii=False, indent=1)
print(len(B), "beats,", sum(len(b.get("say", "").split()) for b in B), "words")
