"""Shared helpers for the STRATA France-protest Shorts (make_short1..5.py).

Render one (from germany_shorts/longform):
  python3 episodes/02_france_protests/shorts/make_shortN.py
  LONGFORM_W=1080 LONGFORM_H=1920 LONGFORM_CACHE=$PWD/episodes/02_france_protests/cache \
      python3 assemble.py episodes/02_france_protests/shorts/shortN.json episodes/02_france_protests/shorts/out/shortN.mp4

The long-form cache is used on purpose: lines reused verbatim from lines.py pass the long-form ElevenLabs context, so
they hit the cached Mattes takes (no new characters spent); SFX prompts are the long-form ones (cached too).
Every picture is a real photo / news clip / CC footage / cached long-form 3D render (maps, objects, no people) shown in
short_card.py's news-card layout; source credits go only into the YouTube description (out/shortN_credits.txt).
"""
import csv
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(HERE)
sys.path.insert(0, EP)
from lines import LINES  # noqa: E402

LF_SAYS = [LINES[k] for k in sorted(LINES)]
RAW = sorted(os.listdir(os.path.join(EP, "sources/photos/raw")))
CRED = {}
for r in csv.DictReader(open(os.path.join(EP, "sources/photos/credits.csv"), encoding="utf-8")):
    CRED["sources/photos/raw/" + os.path.basename(r["file"])] = r
for r in csv.DictReader(open(os.path.join(EP, "sources/photos/v2/credits.csv"), encoding="utf-8")):
    CRED["sources/photos/v2/" + r["file"]] = r
ENDCARD = "../../01_ghost_stations/cache/3d_s1_endcard_amber_dee852c1dc23c600.mp4"   # the approved STRATA end card render
CC_VID = "../sources/video/commons_2026_high_school_student_movement_and_blockades_at_{}.webm"
NEWS_SRC = {"ap": "AP", "afp": "AFP", "reuters": "Reuters", "f24": "FRANCE 24", "fi": "franceinfo", "franceinfo": "franceinfo",
            "lcp": "LCP"}


def ph(i):
    """photo from sources/photos/raw by its index in the sorted listing (contact sheets)"""
    return "../sources/photos/raw/" + RAW[i]


def v2(name):
    return f"../sources/photos/v2/{name}.jpg"


def news(name):
    return f"../assets/news/{name}.mp4"


def cc(name):
    return CC_VID.format(name)


def d3(scene, shot):
    """a cached long-form 3D render (1920x1080), e.g. d3("map", "spark")"""
    m = glob.glob(os.path.join(EP, "cache", f"3d_france_{scene}_{shot}:*.mp4")) or \
        glob.glob(os.path.join(EP, "cache", f"3d_france_{scene}_{shot}_*.mp4"))
    assert len(m) == 1, (scene, shot, m)
    return "../cache/" + os.path.basename(m[0])


def P(src, at=0, cap=None, kb=None, **kw):
    """one picture inside a line: photo (by path ending .jpg), else video / 3D clip"""
    it = {"at": at}
    if src.endswith((".jpg", ".jpeg", ".png", ".JPG")):
        it["photo"] = src
        if kb:
            it["kb"] = kb
    else:
        it["video"] = src
        if "/cache/" in src:
            it["grade"] = False
    if cap is not None:
        it["cap"] = cap
    it.update(kw)
    return it


class Short:
    def __init__(self, n, badge):
        self.n, self.badge, self.B = n, badge, []

    def line(self, say, items, lf=None, **kw):
        """lf=True: the line is a verbatim long-form line -> pass its long-form TTS context (cache hit)"""
        b = {"say": say, "visual": {"type": "g2d", "name": "card", "module": "short_card.py",
                                    "args": {"badge": self.badge, "items": items}}, **kw}
        if lf:
            j = LF_SAYS.index(say)
            b["ctx"] = {"previous_text": " ".join(LF_SAYS[max(0, j - 2):j]), "next_text": LF_SAYS[j + 1] if j + 1 < len(LF_SAYS) else ""}
        self.B.append(b)

    def lf(self, n, items, **kw):
        self.line(LINES[n], items, lf=True, **kw)

    def end(self, sfx=None):
        self.B.append({"say": "Full story on the channel.", "id": "end_card", "hold": 1.3, "trans": "dip", "ctx": {},
                       "visual": {"type": "g2d", "name": "card", "module": "short_card.py",
                                  "args": {"items": [{"at": 0, "full": ENDCARD}]}},
                       "text": [{"kind": "label", "content": "FULL STORY ON", "pos": [0.48, 0.575], "delay": 0.15, "extend": 1.0},
                                {"kind": "title", "content": "STRATA", "pos": [0.48, 0.655], "delay": 0.35, "extend": 1.0}],
                       **({"sfx": sfx} if sfx else {})})

    def write(self, music, title, blurb, sfx_first=None):
        self.B[0]["id"] = "intro"
        if sfx_first:
            self.B[0]["sfx"] = sfx_first
        spec = {
            "voice": {"engine": "elevenlabs", "voice_id": "DrBEKFgWMDWUG6bjTSTk", "model": "eleven_v4", "stability": 0.5, "speed": 1.0},
            "gap": 0.3,
            "pause": 0.48,
            "max_pause": 0.5,
            "tail": {"keep": 0.25, "fade": 0.15},
            "subtitles": False,
            "declick": True,
            "sfx_gain_db": -4,
            "loud_always": True,
            "loud_limit": 0.87,
            "loud_target": -13.0,
            "style_fields": {"LABEL": {"Fontsize": 84, "PrimaryColour": "&H005CB2FF", "Outline": 7, "Shadow": 0, "Spacing": 6},
                             "TITLE": {"Fontsize": 200, "PrimaryColour": "&H00D0DCE4", "Outline": 0, "Shadow": 0, "Spacing": 12}},
            "fonts": {"LABEL": "YouTube Sans", "TITLE": "Playfair Display", "FX": "YouTube Sans"},
            "music": [{**music, "from": "intro", "to": "end", "fade_in": 0.25, "fade_out": 2.2}],
            "beats": self.B,
        }
        json.dump(spec, open(os.path.join(HERE, f"short{self.n}.json"), "w"), ensure_ascii=False, indent=1)
        # sources for the description, and a record of every picture (no repeats inside one short)
        used, creds, vids = [], [], set()
        for b in self.B:
            for it in b["visual"]["args"]["items"]:
                src = it.get("photo") or it.get("video") or it.get("full")
                assert src not in used, f"short {self.n}: picture used twice: {src}"
                used.append(src)
                if "/photos/" in src:
                    r = CRED[src[3:]]
                    lic = r["license"].replace("CC-BY-SA", "CC BY-SA").replace("CC-BY", "CC BY")
                    creds.append(f"{r['author']} ({lic}, Wikimedia Commons)")
                elif "/video/commons" in src:
                    creds.append("Wyslijp16 (CC BY 4.0, Wikimedia Commons)")
                elif "/assets/news/" in src:
                    vids.add(NEWS_SRC[os.path.basename(src).split("_")[0]])
        uniq = list(dict.fromkeys(creds))
        open(os.path.join(HERE, "out", f"short{self.n}_used.json"), "w").write(json.dumps(used, ensure_ascii=False, indent=0))
        meta = {"title": title, "blurb": blurb, "photo_credits": uniq, "news": sorted(vids), "music": music["name"]}
        json.dump(meta, open(os.path.join(HERE, "out", f"short{self.n}_meta.json"), "w"), ensure_ascii=False, indent=1)
        sys.path.insert(0, os.path.dirname(os.path.dirname(EP)))
        import short_card
        small = []
        for b in self.B:
            for it in b["visual"]["args"]["items"]:
                if it.get("cap"):
                    txt = it["cap"].replace("{n}", f"{it['count'][1]:,}" if it.get("count") else "")
                    short_card.caption_layer(txt, "blue", it.get("size", 118))
                    if short_card.LAST_SIZE[0] < 100:
                        small.append((short_card.LAST_SIZE[0], it["cap"]))
        if small:
            print("  captions shrunk below 100 px:", small)
        says = [b["say"] for b in self.B]
        new = [b["say"] for b in self.B if "ctx" not in b or b["ctx"] == {}]
        print(f"short{self.n}: {len(self.B)} lines, {sum(len(s.split()) for s in says)} words, "
              f"new TTS chars <= {sum(map(len, new))}, {len(used)} pictures")


MUSIC = {
    "crypto": {"file": "../music/m1_crypto.mp3", "vol": 0.13, "name": "Crypto"},
    "hiding": {"file": "../music/m2_hiding.mp3", "vol": 0.12, "seek": 12, "name": "Hiding Your Reality"},
    "tide": {"file": "../music/m3_tide.mp3", "vol": 0.2, "seek": 4, "name": "Rising Tide"},
    "lightless": {"file": "../music/m4_lightless.mp3", "vol": 0.26, "seek": 5, "name": "Lightless Dawn"},
    "interloper": {"file": "../music/m5_interloper.mp3", "vol": 0.12, "seek": 25, "name": "Interloper"},
    "floating": {"file": "../music/m6_floating.mp3", "vol": 0.16, "seek": 3, "name": "Floating Cities"},
}


def fx(prompt, ln, vol, at=0.0, fade=None):
    fade = fade if fade is not None else min(1.2, ln * 0.4)
    return {"prompt": prompt, "len": ln, "vol": vol, "at": at, "filter": f"afade=t=out:st={max(ln - fade, 0):.2f}:d={fade:.2f}"}


HIT = fx("deep low cinematic boom hit, soft, short dark tail", 2.5, 0.16, at=0.05)
CROWD = fx("distant street protest crowd chanting, outdoor, muffled", 8, 0.05, fade=2.5)
BINS = fx("distant street protest crowd and bins scraping on asphalt, outdoor", 5, 0.05)
TICK = fx("soft digital counter ticking, quiet clicks", 2, 0.045)
SWELL = fx("soft low cinematic tone swell, gentle and quiet", 3, 0.06)
