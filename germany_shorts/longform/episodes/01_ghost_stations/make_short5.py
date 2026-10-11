"""STRATA Short #5 'Frozen for 28 years' (vertical 1080x1920). Writes short5.json next to this file.

Render (from the longform dir):
  LONGFORM_W=1080 LONGFORM_H=1920 LONGFORM_CACHE=episodes/01_ghost_stations/cache \
    python3 assemble.py episodes/01_ghost_stations/short5.json episodes/01_ghost_stations/out/short5.mp4

Facts from script_en.json ('Life on a ghost platform', '1989: the ghosts come back') and research_ghost.md A1/A5/C1:
stations sealed from 13 Aug 1961; adverts and signs unchanged since 1961; the Wall opened on the night of 9 Nov 1989;
Jannowitzbrücke (U8) was the first to reopen, 11 Nov 1989; Rosenthaler Platz followed in Dec 1989 (22 Dec);
the remaining stations reopened 1990-92.
Archive photos (Bundesarchiv, CC BY-SA 3.0): c01 Jannowitzbrücke reopening 11 Nov 1989, c03 Rosenthaler Platz
20 Dec 1989, c05 Bernauer Straße 12 Apr 1990. They run through short5_graphics.py (hold/pan keys, red ring in photo
coordinates). Portrait framing of the 3D shots: scenes/s5_*.js. Every SFX fades out before its end.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
AMB = "&H005CB2FF"     # #FFB25C as ASS BGR
MOD = "short5_graphics.py"


def v3(scene, shot, t0=0):
    return {"type": "3d", "scene": scene, "shot": shot, "t0": t0}


def photo(file, keys, credit, ring=None, lift=1.06):
    args = {"file": file, "keys": keys, "lift": lift, **({"ring": ring} if ring else {})}
    return {"type": "g2d", "name": "photo_s5", "module": MOD, "args": args, "credit": credit}


def key(word, y=0.32, delay=0.0, extend=0.0):
    """big centred key word (YEAR style: YouTube Sans Black, amber, black outer stroke)"""
    return {"kind": "year", "content": word, "pos": [0.5, y], "delay": delay, "extend": extend}


def fx(prompt, length, vol, at=0.0, fade=None):
    """sound effect that always fades out before its end (never cut off)"""
    fade = fade or min(1.2, length * 0.4)
    return {"prompt": prompt, "len": length, "vol": vol, "at": at,
            "filter": f"atrim=0:{length:.2f},afade=t=in:d=0.03,afade=t=out:st={length - fade:.2f}:d={fade:.2f}"}


HIT = "deep cinematic sub boom hit with short metallic tail"
BA = "Bundesarchiv, Bild 183-{} / {} / CC BY-SA 3.0"

B = []


def say(line, visual="same", **kw):
    B.append({"say": line, "visual": visual, **kw})


# hook: 28 years pass over a bench on a sealed platform (time-lapse: dust, cobweb, the poster peels)
say("For twenty-eight years, these subway stations were frozen in time.", v3("s5_walk", "years", 0), id="intro",
    text=key("FROZEN", 0.32, 0.25),
    sfx=[fx("empty underground subway station ambience, faint electrical hum, distant water drips, low air rumble", 14, 0.13, 0.0, 3.0),
         fx("old clock ticking fast in an empty hall, slight echo", 3.4, 0.1, 0.0, 1.0)])
say("In 1961, the Berlin Wall split the city, and East Germany sealed them.", v3("s5_section", "stack", 0),
    text=key("1961", 0.29, 0.3))
say("West Berlin trains rolled straight through, without stopping.", v3("s5_intro", "passby", 0.4),
    sfx=fx("subway train rushing past through an empty underground station, rattling wheels, whoosh, echo", 4.5, 0.18, 0.0, 1.5))
# the time capsule
say("On the dark platforms, the posters and signs from 1961 never changed.", v3("s5_walk", "walk", 5.3))
say("Only armed guards stood watch.", v3("s5_intro", "guard", 2.2), hold=0.2)
# 1989
say("Then, on November 9th, 1989, the Wall fell.", v3("s5_reopen", "bornholmer", 0), id="fall", trans="dip",
    text=key("1989", 0.29, 1.1),
    sfx=fx("distant cheering crowd at night, celebration, outdoor", 5, 0.12, 0.3, 1.8))
say("Two days later, a train stopped at Jannowitzbrücke,", v3("s5_reopen", "stop", 1.6),
    sfx=fx("subway train braking slowly to a stop in a station, squealing brakes, hiss of air", 5, 0.14, 0.2, 1.5))
say("for the first time in twenty-eight years.", text=key("FIRST\\NSTOP", 0.29, 0.2))
say("And the platform was packed.",
    photo("assets/c01.jpg", [[0, 1.0, 0.1, 0.5], [0.75, 1.0, 0.1, 0.5], [2.0, 1.0, 0.64, 0.5], [9, 1.05, 0.64, 0.5]],
          BA.format("1989-1111-007", "Robert Roeske"), ring={"c": [208, 400], "r": [200, 62], "at": 0.15}),
    hold=0.5, sfx=fx("crowd of people cheering and clapping in an underground station, echo", 3.5, 0.11, 0.2, 1.4))
say("In December, Rosenthaler Platz reopened too.",
    photo("assets/c03.jpg", [[0, 1.0, 0.24, 0.5], [0.9, 1.0, 0.24, 0.5], [3.0, 1.06, 0.42, 0.52], [9, 1.08, 0.44, 0.52]],
          BA.format("1989-1220-301", "Peer Grimm"), ring={"c": [295, 320], "r": [190, 60], "at": "Rosenthaler"}))
say("When the lights came on, it looked like time had stopped in 1961.", v3("s5_walk", "title", 0),
    text=key("STILL\\N1961", 0.30, 1.6))
say("One by one, the ghost stations came back to life.",
    photo("assets/c05.jpg", [[0, 1.0, 0.38, 0.5], [9, 1.08, 0.5, 0.5]], BA.format("1990-0412-010", "Thomas Uhlemann"), lift=1.0),
    hold=0.3)
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
    # the frozen years on the intro bed, 1989 onwards on the resolution bed
    "music": [{"file": "music/m1_intro.mp3", "from": "intro", "to": "fall", "vol": 0.17, "fade_in": 0.6, "fade_out": 1.0},
              {"file": "music/m4_resolution.mp3", "from": "fall", "to": "end", "vol": 0.17, "fade_in": 0.8, "fade_out": 1.2}],
    "beats": B,
}
json.dump(spec, open(os.path.join(HERE, "short5.json"), "w"), ensure_ascii=False, indent=1)
print(len(B), "beats,", sum(len(b.get("say", "").split()) for b in B), "words")
