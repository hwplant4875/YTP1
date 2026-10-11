"""STRATA Short #2 'The Escape' (Dieter Wendt, 1980; vertical 1080x1920). Writes short2.json next to this file.

Render (from the longform dir):
  LONGFORM_W=1080 LONGFORM_H=1920 LONGFORM_CACHE=episodes/01_ghost_stations/cache \
    python3 assemble.py episodes/01_ghost_stations/short2.json episodes/01_ghost_stations/out/short2.mp4

Same format as Short #1 (make_short1.py): Mattes on eleven_v4, no subtitles, a few big amber key words kept out of the
bottom 25 % and the right-hand button column. Portrait framing: scenes/s2_escape.js wraps escape.js.
Facts follow the episode's "The escape" chapter (script_en.json) and research_ghost.md A3.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
AMB = "&H005CB2FF"     # #FFB25C as ASS BGR
RED = "&H2A2AE6&"      # red ring


def v3(scene, shot, t0=0):
    return {"type": "3d", "scene": scene, "shot": shot, "t0": t0}


def key(word, y=0.30, delay=0.0, extend=0.0):
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


def fx(prompt, length, vol, at=0.0, fade=0.8):
    """sound effect that always fades out before its clip ends (never cut off)"""
    return {"prompt": prompt, "len": length, "vol": vol, "at": at,
            "filter": f"afade=t=in:d=0.05,afade=t=out:st={max(length - fade, 0):.2f}:d={fade}"}


AMBIENT = fx("empty underground subway station ambience, faint electrical hum, distant water drips, low air rumble", 22, 0.14, 0, 3.0)
HIT = "deep cinematic sub boom hit with short metallic tail"

B = []


def say(line, visual="same", **kw):
    B.append({"say": line, "visual": visual, **kw})


# hook: one man beside the track, a train's headlights flood the tunnel behind him
say("In 1980, one man stopped a West Berlin train inside a ghost tunnel, and rode it to freedom.", v3("s2_escape", "teaser", 0),
    id="intro", text=key("1980", 0.30, 0.2),
    sfx=[AMBIENT, fx("distant subway train approaching in a long tunnel, low rumble growing", 6, 0.16, 0.2, 1.5)])
# who
say("His name was Dieter Wendt.", v3("s2_escape", "tech", 0), text=key("DIETER\\NWENDT", 0.27, 0.15))
say("He was twenty-eight, a signal technician on the East Berlin subway.")
# the plan: fake a fault
say("So he made a plan: fake a signal fault.", v3("s2_escape", "plan", 1.2), hold=1.0,
    text=key("FAKE\\NFAULT", 0.50, 0.9),
    sfx=fx("electrical relay click and a small spark crackle, short", 2, 0.22, 2.6, 0.6))
say("When a signal breaks, a technician is allowed into the tunnel to fix it.", v3("s2_escape", "allowed", 0))
say("The spot: a tunnel near Jannowitzbrücke station.", text=ring(845, 775, 150, 120, 0.25))
# the train
say("As a West Berlin train approached, he stood by the tracks and flagged it down.", v3("s2_escape", "flag", 0), hold=0.7,
    sfx=[fx("subway train approaching fast through a tunnel, rattling wheels, rising roar", 5, 0.16, 0.2, 1.2),
         fx("subway train emergency braking, loud metal screech in a tunnel", 3, 0.14, 4.2, 1.2)])
say("The stunned driver opened the door and shouted:", v3("s2_escape", "door", 0.6))
B.append({"visual": "same", "hold": 2.5, "text": key("GET IN!\\NLIE DOWN!", 0.24, 0.1, 0.0),
          "sfx": [fx(HIT, 2.5, 0.2, 0.0, 1.0),
                  {"file": "driver_shout.wav", "vol": 1.0, "duck": False, "at": 0.15,
                   "filter": "afade=t=out:st=2.2:d=0.45"}]})
# the West
say("Minutes later, the train pulled into West Berlin.", v3("s2_escape", "west", 0),
    text=key("WEST\\NBERLIN", 0.28, 1.6),
    sfx=fx("subway car interior, train rolling through a tunnel, rhythmic wheel clatter, slowing down", 7, 0.13, 0, 2.0))
say("He'd ridden straight through the border, inside a ghost tunnel.", hold=0.5)
# end card
say("Full story on Strata.", v3("s1_endcard", "amber", 0), id="end_card", hold=0.4, trans="dip",
    text=[{"kind": "label", "content": "FULL STORY ON", "pos": [0.5, 0.575], "delay": 0.15, "extend": 1.0},
          {"kind": "title", "content": "STRATA", "pos": [0.5, 0.655], "delay": 0.35, "extend": 1.0}],
    sfx=fx(HIT, 2.5, 0.2, 0.05, 1.0))

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
    "music": [{"file": "music/m3_escape.mp3", "from": "intro", "to": "end", "vol": 0.17, "fade_in": 0.6, "fade_out": 1.2}],
    "beats": B,
}
json.dump(spec, open(os.path.join(HERE, "short2.json"), "w"), ensure_ascii=False, indent=1)
print(len(B), "beats,", sum(len(b.get("say", "").split()) for b in B), "words")
