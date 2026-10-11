"""STRATA Short #3 'West Berlin paid the East for its own trains' (vertical 1080x1920). Writes short3.json next to this file.

Render (from the longform dir):
  LONGFORM_W=1080 LONGFORM_H=1920 LONGFORM_CACHE=episodes/01_ghost_stations/cache \
    python3 assemble.py episodes/01_ghost_stations/short3.json episodes/01_ghost_stations/out/short3.mp4

Facts from script_en.json ('The money') and research_ghost.md: monthly fee from 1963, 181,132 DM at first, 495,756 DM
by 1989 (~6 million DM a year); the West Berlin S-Bahn was run by the East German Reichsbahn (until 1984), boycotted
('Der S-Bahn-Fahrer zahlt den Stacheldraht'), ridership from ~500,000 a day to under 50,000.
Portrait framing: scenes/s3_*.js wrap the episode scenes (via s1_portrait.js); 2D money graphics in short3_graphics.py.
Every SFX carries an afade-out so nothing is cut off.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
AMB = "&H005CB2FF"     # #FFB25C as ASS BGR
RED = "&H2A2AE6&"      # red ring / arrow


def v3(scene, shot, t0=0):
    return {"type": "3d", "scene": scene, "shot": shot, "t0": t0}


def g2(name):
    return {"type": "g2d", "name": name, "module": "short3_graphics.py", "args": {}}


def key(word, y=0.34, delay=0.0, extend=0.0):
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


def fx(prompt, length, vol, at=0.0, fade=None):
    """sound effect that always fades out before its end (never cut off)"""
    fade = fade or min(1.2, length * 0.4)
    return {"prompt": prompt, "len": length, "vol": vol, "at": at,
            "filter": f"atrim=0:{length:.2f},afade=t=in:d=0.03,afade=t=out:st={length - fade:.2f}:d={fade:.2f}"}


B = []


def say(line, visual="same", **kw):
    B.append({"say": line, "visual": visual, **kw})


# hook: a West Berlin train rolls into the ghost station
say("West Berlin paid East Germany, just to run its own subway.", v3("s3_watch", "boots", 1.2), id="intro",
    text=key("PAID", 0.33, 0.35),
    sfx=[fx("subway train approaching through a tunnel, rumble and rattling wheels, echo", 5, 0.2, 0.0, 1.5),
         fx("empty underground subway station ambience, faint electrical hum, low air rumble", 12, 0.12, 0.0, 3.0)])
say("In 1961 the Wall went up, but West Berlin's trains still ran under the East,",
    v3("s3_section", "pass", 0), text=key("1961", 0.27, 0.3))
say("through sealed, guarded ghost stations.", v3("s3_watch", "eachother", 0.3))
# the money
say("From 1963, East Germany sent a bill. Every month.", g2("money_s3"), trans="dip",
    sfx=fx("old cash register ding and a few coins", 1.6, 0.2, 0.9, 0.6))
say("First, about a hundred and eighty thousand marks.")
say("By 1989, almost half a million.", sfx=fx("coins pouring onto a pile, short", 1.8, 0.14, 0.3, 0.8))
say("Close to six million marks a year,")
say("paid to the country that walled them in.", hold=0.3,
    sfx=fx("deep cinematic sub boom hit with short metallic tail", 2.5, 0.18, 0.2, 1.4))
# the S-Bahn
say("And inside West Berlin, the S-Bahn was run by East Germany.", v3("s3_reopen", "stop", 0.3), trans="dip",
    text=key("RUN BY\\NTHE EAST", 0.30, 0.9))
say("So West Berliners boycotted it.", text=key("BOYCOTT", 0.30, 0.2))
# the wire shot turns into another set-up after ~3.7 s: keep this beat short
say("Every ticket, they said, pays for the barbed wire.", v3("s3_walk", "wire", 0))
say("Ridership crashed from half a million a day to under fifty thousand.", g2("riders_s3"), hold=0.3,
    sfx=fx("low descending whoosh, soft", 2.0, 0.12, 2.2, 0.9))
# end card
say("Full story on Strata.", v3("s1_endcard", "amber", 0), id="end_card", hold=0.4, trans="dip",
    text=[{"kind": "label", "content": "FULL STORY ON", "pos": [0.5, 0.575], "delay": 0.15, "extend": 1.0},
          {"kind": "title", "content": "STRATA", "pos": [0.5, 0.655], "delay": 0.35, "extend": 1.0}],
    sfx=fx("deep cinematic sub boom hit with short metallic tail", 2.5, 0.2, 0.05, 1.4))

spec = {
    "voice": {"engine": "elevenlabs", "voice_id": "DrBEKFgWMDWUG6bjTSTk", "model": "eleven_v4", "stability": 0.5, "speed": 1.0},
    "gap": 0.1,
    "subtitles": False,
    "declick": True,
    "sfx_gain_db": -6,
    "style_fields": {
        "YEAR": {"Fontsize": 200, "PrimaryColour": AMB, "Outline": 11, "Shadow": 0, "Spacing": 2},
        "LABEL": {"Fontsize": 100, "PrimaryColour": AMB, "Outline": 7, "Shadow": 0, "Spacing": 6},
        "TITLE": {"Fontsize": 230, "PrimaryColour": "&H00D0DCE4", "Outline": 0, "Shadow": 0, "Spacing": 14},
    },
    "fonts": {"YEAR": "YouTube Sans", "LABEL": "YouTube Sans", "TITLE": "Playfair Display", "FX": "YouTube Sans"},
    "music": [{"file": "music/m2_investigate.mp3", "from": "intro", "to": "end", "vol": 0.17, "fade_in": 0.6, "fade_out": 1.2}],
    "beats": B,
}
json.dump(spec, open(os.path.join(HERE, "short3.json"), "w"), ensure_ascii=False, indent=1)
print(len(B), "beats,", sum(len(b.get("say", "").split()) for b in B), "words")
