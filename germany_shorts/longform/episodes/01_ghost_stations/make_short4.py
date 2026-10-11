"""STRATA Short #4 'Friedrichstrasse, the one stop' (vertical 1080x1920). Writes short4.json next to this file.

Render (from the longform dir):
  LONGFORM_W=1080 LONGFORM_H=1920 LONGFORM_CACHE=episodes/01_ghost_stations/cache \
    python3 assemble.py episodes/01_ghost_stations/short4.json episodes/01_ghost_stations/out/short4.mp4

Facts from script_en.json ('Friedrichstrasse, the one stop') and research_ghost.md: of the stations under East Berlin,
West trains stopped only at Friedrichstrasse; West Berliners changed trains there without checks; a guarded
steel-and-glass wall split the station from the border crossing into East Germany (passport and customs checks,
interrogation rooms); the departure hall (1962) became the 'Palace of Tears'; March 1974: the Polish citizen
Czeslaw Kukuczka, who had threatened the Polish embassy with a fake bomb to be let out to the West, was shot from
ambush by a Stasi officer just after passport control.
Portrait framing: scenes/s4_*.js wrap the episode scenes (via s1_portrait.js); 2D graphics in short4_graphics.py.
Every SFX carries an afade-out so nothing is cut off.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
AMB = "&H005CB2FF"     # #FFB25C as ASS BGR
RED = "&H2A2AE6&"      # red ring / arrow


def v3(scene, shot, t0=0):
    return {"type": "3d", "scene": scene, "shot": shot, "t0": t0}


def g2(name, credit=None, **args):
    v = {"type": "g2d", "name": name, "module": "short4_graphics.py", "args": args}
    return {**v, "credit": credit} if credit else v


def img(file, a, b, credit):
    return {"type": "image", "file": file, "from": a, "to": b, "credit": credit}


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


def arrow(x0, y0, x1, y1, delay=0.3, extend=0.0):
    """red arrow from (x0, y0) to the tip (x1, y1), pixel coords, black edge, grows in"""
    import math
    L = math.hypot(x1 - x0, y1 - y0)
    ang = -math.degrees(math.atan2(y1 - y0, x1 - x0))
    # arrow drawn pointing right from the origin, tip at (L, 0); rotated about its tail (\org at the tail)
    sw, hw, hl = 16, 46, 80
    shape = (f"m 0 {-sw} l {L - hl:.0f} {-sw} l {L - hl:.0f} {-hw} l {L:.0f} 0 l {L - hl:.0f} {hw} "
             f"l {L - hl:.0f} {sw} l 0 {sw}")
    body = ("{\\an7\\org(" + f"{x0},{y0}" + ")\\frz" + f"{ang:.1f}" + "\\bord6\\shad0\\1c" + RED + "\\3c&H000000&\\blur0.6"
            "\\fscx40\\t(0,350,\\fscx100)\\p1}" + shape + "{\\p0}")
    return {"kind": "label", "content": body, "pos": [x0 / W, y0 / H], "delay": delay, "extend": extend}


def fx(prompt, length, vol, at=0.0, fade=None):
    """sound effect that always fades out before its end (never cut off)"""
    fade = fade or min(1.2, length * 0.4)
    return {"prompt": prompt, "len": length, "vol": vol, "at": at,
            "filter": f"atrim=0:{length:.2f},afade=t=in:d=0.03,afade=t=out:st={length - fade:.2f}:d={fade:.2f}"}


C13 = "Bundesarchiv, Bild 183-35539-0001 / Peter Heinz Junge / CC BY-SA 3.0"
C10 = "Bundesarchiv, Bild 183-A0706-0010-001 / Krueger / CC BY-SA 3.0"
MAP = "Map: Ericmetro / CC0"
HIT = "deep cinematic sub boom hit with short metallic tail"

B = []


def say(line, visual="same", **kw):
    B.append({"say": line, "visual": visual, **kw})


# hook: driver's view, a sealed ghost station slides past

def _arrow(x0, y0, x1, y1, delay=0.3, extend=0.0):
    """red arrow from (x0, y0) to the tip (x1, y1), pixel coords, black edge, grows in"""
    import math
    L = math.hypot(x1 - x0, y1 - y0)
    ang = -math.degrees(math.atan2(y1 - y0, x1 - x0))
    sw, hw, hl = 16, 46, 80
    shape = (f"m 0 {-sw} l {L - hl:.0f} {-sw} l {L - hl:.0f} {-hw} l {L:.0f} 0 l {L - hl:.0f} {hw} "
             f"l {L - hl:.0f} {sw} l 0 {sw}")
    body = ("{\\an7\\org(" + f"{x0},{y0}" + ")\\frz" + f"{ang:.1f}" + "\\bord6\\shad0\\1c" + RED + "\\3c&H000000&\\blur0.6"
            "\\fscx40\\t(0,350,\\fscx100)\\p1}" + shape + "{\\p0}")
    return {"kind": "label", "content": body, "pos": [x0 / W, y0 / H], "delay": delay, "extend": extend}


def ring(cx, cy, rx, ry, delay=0.3, extend=0.0):
    """user 2026-10-12: red arrows instead of red circles. Arrow from the lower left, tip just off the subject."""
    tx, ty = cx - rx * 0.75, cy + ry * 0.55
    return _arrow(max(60, tx - 230), ty + 230, tx, ty, delay, extend)


say("For twenty-eight years, West Berlin's trains crossed under East Berlin without stopping.", v3("s4_intro", "cab", 3.5), id="intro",
    text=key("NO STOPS", 0.30, 0.6),
    sfx=[fx("subway train driving through a tunnel, rumble and rattling wheels, cab interior", 6, 0.2, 0.0, 2.0),
         fx("empty underground subway station ambience, faint electrical hum, low air rumble", 8, 0.1, 0.0, 3.0)])
say("Except at one station.", g2("map_s4", credit=MAP),
    sfx=fx("soft bright synth ping with gentle reverb tail", 2.0, 0.14, 0.35, 1.2))
say("Friedrichstraße.", hold=0.35)
# the one stop: West Berliners changing trains without checks
say("Here, West Berliners changed trains without a single check.", img("assets/c13.jpg", [1.0, 0.64, 0.5], [1.1, 0.66, 0.48], C13),
    text=key("NO CHECKS", 0.30, 0.5),
    sfx=fx("crowd murmur in an echoing underground train station, footsteps", 4.5, 0.12, 0.0, 1.5))
# but behind the wall: a border crossing
say("But behind a wall of steel and glass, it was a border crossing into East Germany.", g2("split_s4"), trans="dip",
    sfx=fx("heavy steel door slamming shut in a large hall, echo", 2.5, 0.16, 1.0, 1.4))
say("A maze of passport checks, searches and interrogation rooms.",
    sfx=fx("rubber stamp thumped onto paper twice", 1.4, 0.16, 0.6, 0.6))
say("The hall where families said goodbye got a nickname:", img("assets/c10.jpg", [1.0, 0.27, 0.5], [1.1, 0.25, 0.47], C10))
say("the Palace of Tears.", text=key("PALACE\\NOF TEARS", 0.27, 0.0), hold=0.35)
# March 1974
say("In March 1974, a Polish man threatened his own embassy with a fake bomb, demanding to go West.",
    v3("s4_checkpoint", "bomb", 0), trans="dip", text=key("MARCH\\N1974", 0.27, 0.2),
    sfx=[fx("old mechanical alarm clock ticking, close, dry", 7, 0.13, 0.0, 2.0)])
say("East Germany pretended to agree.", v3("s4_checkpoint", "agree", 0.1),
    sfx=fx("heavy rubber stamp slammed onto a passport on a wooden desk", 1.2, 0.2, 0.55, 0.5))
say("Just past the checkpoint, a hidden Stasi officer shot him dead.", v3("s4_checkpoint", "shot", 0.2),
    text=ring(790, 860, 190, 300, 1.05),
    sfx=[fx("single muffled pistol shot in a concrete corridor with echo tail", 2.2, 0.16, 1.4, 1.5)])
say("West Berlin was only a few steps away.", v3("s4_checkpoint", "steps", 0), hold=0.4,
    text=[key("WEST", 0.20, 0.3), arrow(250, 1330, 470, 1080, 0.6)],
    sfx=fx("low ominous drone swell, soft", 3.5, 0.12, 0.0, 1.6))
# end card
say("Full story on Strata.", v3("s1_endcard", "amber", 0), id="end_card", hold=0.4, trans="dip",
    text=[{"kind": "label", "content": "FULL STORY ON", "pos": [0.5, 0.575], "delay": 0.15, "extend": 1.0},
          {"kind": "title", "content": "STRATA", "pos": [0.5, 0.655], "delay": 0.35, "extend": 1.0}],
    sfx=fx(HIT, 2.5, 0.2, 0.05, 1.4))

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
        # archive credit: small, grey, 50 % opacity, bottom left, just above the Shorts UI zone (bottom 25 %)
        "CREDIT": {"Fontsize": 24, "PrimaryColour": "&H80B4B4B4", "Alignment": 1, "MarginL": 44, "MarginR": 200, "MarginV": 492},
    },
    "fonts": {"YEAR": "YouTube Sans", "LABEL": "YouTube Sans", "TITLE": "Playfair Display", "FX": "YouTube Sans"},
    "music": [{"file": "music/m2_investigate.mp3", "from": "intro", "to": "end", "vol": 0.17, "fade_in": 0.6, "fade_out": 1.2}],
    "beats": B,
}
json.dump(spec, open(os.path.join(HERE, "short4.json"), "w"), ensure_ascii=False, indent=1)
print(len(B), "beats,", sum(len(b.get("say", "").split()) for b in B), "words")
