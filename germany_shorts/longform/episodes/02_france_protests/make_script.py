"""Beat script for STRATA long-form #02, "France's 2026 lycée protests" (English). Writes script.json next to this file.

  python3 make_script.py && cd ../.. && LONGFORM_CACHE=$PWD/episodes/02_france_protests/cache \
      python3 assemble.py episodes/02_france_protests/script.json episodes/02_france_protests/out/full.mp4

Narration: ElevenLabs eleven_v4, Mattes (same voice spec as the ghost-stations episode); lines live in lines.py,
keyed by the beat numbers of script_v1.md. Edit rules (from the user):
  - chapter cards are centred curiosity questions and double as the YouTube timestamps (out/*_chapters.txt);
  - key words: large, centred, amber with a black outer stroke; infographics sit on dark/blurred backgrounds;
  - news footage <= 5 s per clip, framed small over a dark blurred copy, credited ("Video: AP"), faces blurred
    (tools/news_cut.py), <= 10 % of runtime; CC photos/videos get a slow Ken Burns and a grey 50 % credit, bottom left;
  - no burned-in subtitles (.srt written separately), quiet SFX that always fade out, music under everything;
  - each 3D shot is used for one beat group only (no re-use).
"""
import csv
import json
import os

from lines import LINES

HERE = os.path.dirname(os.path.abspath(__file__))
A = "{\\c&H5CB2FF&}"          # amber (ASS BGR)
C = "{\\c&HE6EEF2&}"          # cream

# ---------------------------------------------------------------- credits

PH = {}
for r in csv.DictReader(open(os.path.join(HERE, "sources/photos/credits.csv"), encoding="utf-8")):
    PH[os.path.basename(r["file"])] = r


def lic(s):
    return s.replace("CC-BY", "CC BY").replace("CC-BY-SA", "CC BY-SA")


def photo_credit(name):
    r = PH[name]
    if r["license"] in ("CC0", "Public domain"):
        return f"{r['author']}, {r['license']}, via Wikimedia Commons"
    return f"{r['author']}, {lic(r['license'])}, via Wikimedia Commons"


WYS = "Wyslijp16, CC BY 4.0, via Wikimedia Commons"
CUNY = "Florian Cuny, CC BY-SA 4.0, via Wikimedia Commons"
VID = "sources/video/commons_2026_high_school_student_movement_and_blockades_at_{}.webm"
P = {   # photos used (sources/photos/raw)
    "bins": "2026_high_school_student_movement_and_blockades_at_Lycée_Jacques-Decour_in_Paris_01.jpg",
    "gate": "2026_high_school_student_movement_and_blockades_at_Jules_Ferry_High_School_in_Paris_06.jpg",
    "march_wide": "Manifestation_lycéenne_du_6_octobre_2026_à_Paris_26.jpg",
    "crowd_blur": "Manifestation_lycéenne_et_étudiante_du_6_octobre_2026_à_Paris_023.jpg",
    "droit": "Manifestation_lycéenne_du_6_octobre_2026_à_Paris_63.jpg",
    "republique": "Manifestation_lycéenne_du_6_octobre_2026_à_Paris_25.jpg",
    "trop_jeune": "Manifestation_lycéenne_du_6_octobre_2026_à_Paris_10.jpg",
    "lecons": "Manifestation_lycéenne_du_6_octobre_2026_à_Paris_08.jpg",
    "briller": "Manifestation_lycéenne_du_6_octobre_2026_à_Paris_68.jpg",
    "avenir": "Journée_de_mobilisation_des_lycéens_à_Perpignan_31.jpg",
    "crs_line": "Manifestation_lycéenne_et_étudiante_du_6_octobre_2026_à_Paris_104.jpg",
    "crs_voltaire": "Manifestation_lycéenne_et_étudiante_du_6_octobre_2026_à_Paris_103.jpg",
    "smoke": "Manifestation_lycéenne_et_étudiante_du_6_octobre_2026_à_Paris_015.jpg",
    "colbert_door": "2026_high_school_student_movement_and_blockades_at_Lycée_Colbert_in_Paris_18.jpg",
    "colbert_street": "2026_high_school_student_movement_and_blockades_at_Lycée_Colbert_in_Paris_24.jpg",
    "soutien93": "2026_high_school_student_movement_and_blockades_at_Lycée_Louis-le-Grand_in_Paris_63.jpg",
    "rennes": "Mouvement_lycéen_Rennes_2_-_Vive_la_Commune.jpg",
    "bayonne": "Ikasleen_protesta_Baiona_2026_2.jpg",
    "belfort": "2026-10-06_12-00-58_MouvementDesLycéens-Belfort.jpg",
    "belfort_sign": "2026-10-06_10-12-42_MouvementDesLycéens-Belfort.jpg",
    "prof_greve": "2026-10-06_Manifestation_à_Nancy_pancarte_Prof_en_grève.jpg",
    "extinguish": "Deux_lycéens_tentent_d_éteindre_une_poubelle.jpg",
    "parcoursup": "Manifestation_lycéenne_du_6_octobre_2026_à_Paris_01.jpg",
    "egalite": "Manifestation_lycéenne_et_étudiante_du_6_octobre_2026_à_Paris_079.jpg",
    "budget": "Manifestation_lycéenne_et_étudiante_du_6_octobre_2026_à_Paris_092.jpg",
    "llg_flag": "2026_high_school_student_movement_and_blockades_at_Lycée_Louis-le-Grand_in_Paris_07.jpg",
    "perpignan_police": "Journée_de_mobilisation_des_lycéens_à_Perpignan_14.jpg",
}


def ppath(key):
    return "sources/photos/raw/" + P[key]


# ---------------------------------------------------------------- visual helpers

def img(key, frm=(1.04, 0.5, 0.5), to=(1.14, 0.5, 0.5)):
    """CC photo, slow Ken Burns, credit bottom left."""
    return {"type": "image", "file": ppath(key), "from": list(frm), "to": list(to), "credit": photo_credit(P[key])}


def cc(name, start, cred=WYS, speed=1.0):
    """CC video from Wikimedia Commons (faces already blurred by the uploader)."""
    return {"type": "video", "file": VID.format(name), "start": start, "speed": speed, "credit": cred}


def news(name, src, start=0.0, frame=0.8, speed=1.0):
    """Short news excerpt (<= 5 s, pre-cut and face-blurred into assets/news by tools/news_cut.py), framed small.
    speed < 1 stretches it over a longer line; the last frame holds if the line is longer still."""
    v = {"type": "video", "file": f"assets/news/{name}.mp4", "start": start, "frame": frame, "credit": f"Video: {src}"}
    if speed != 1.0:
        v["speed"] = speed
    return v


def g3(scene, shot, t0=0):
    return {"type": "3d", "scene": scene, "shot": shot, "t0": t0}


def g2(name, credit=None, **args):
    v = {"type": "g2d", "name": name, "module": "graphics.py", "args": args}
    if credit:
        v["credit"] = credit
    return v


def ov(name, beats=1, **args):
    return {"name": name, "module": "graphics.py", "beats": beats, "args": args}


def key(text, y=0.82, size=None):
    """Big centred key word: amber, black outer stroke (LABEL style)."""
    fs = f"{{\\fs{size}}}" if size else ""
    return {"kind": "label", "content": fs + A + text, "pos": [0.5, y]}


def quote(text, sub=None, y=0.5):
    c = "{\\fs92}" + text + (f"\\N{{\\fs50}}{C}{sub}" if sub else "")
    return {"kind": "quote", "content": c, "pos": [0.5, y]}


# ---------------------------------------------------------------- sound (ElevenLabs SFX, cached by prompt; all fade out)

def fx(prompt, ln, vol, at=0.0, fade=None):
    fade = fade if fade is not None else min(1.2, ln * 0.4)
    return {"prompt": prompt, "len": ln, "vol": vol, "at": at, "filter": f"afade=t=out:st={max(ln - fade, 0):.2f}:d={fade:.2f}"}


HIT = fx("deep low cinematic boom hit, soft, short dark tail", 2.5, 0.22)
SWELL = fx("soft low cinematic tone swell, gentle and quiet", 3, 0.08)
PULSE = fx("low tense electronic pulse, quiet, documentary", 4, 0.1)
CROWD = fx("distant street protest crowd chanting, outdoor, muffled", 8, 0.06, fade=2.5)
TICK = fx("soft digital counter ticking, quiet clicks", 2, 0.06)

# ---------------------------------------------------------------- beats

B = []


def say(n, visual="same", **kw):
    B.append({"say": LINES[n], "visual": visual, **kw})


def chapter(title, question, visual, hold=2.6, bid=None):
    """Centred curiosity question at a chapter change; doubles as a YouTube chapter mark."""
    b = {"visual": visual, "hold": hold, "chapter": title, "trans": "dip", "dim": True,
         "text": {"kind": "chapter", "content": question, "pos": [0.5, 0.5]}, "sfx": SWELL}
    if bid:
        b["id"] = bid
    B.append(b)


# shots3d.json (3D agent): the per-shot stretch ("name:secs") it tuned to the narration; placement is decided below
ARG3 = {}
p3 = os.path.join(HERE, "shots3d.json")
if os.path.exists(p3):
    for s3 in json.load(open(p3)).get("shots", []):
        ARG3[(s3["scene"], s3["shot"])] = s3.get("shot_arg") or s3["shot"]


def d3(n, scene, shot, t0=0):
    """3D visual for beat n; a bare shot name takes the 3D agent's stretch, "name:secs" overrides it."""
    return g3(scene, shot if ":" in shot else ARG3.get((scene, shot), shot), t0)


# ================================================================ 0. COLD OPEN
B.append({"visual": {**cc("Lycée_Louis-le-Grand_in_Paris_76", 2.0), "zoom": [1.0, 1.1]}, "hold": 0.0, "id": "intro", "chapter": "Cold open",
          "say": LINES[1], "sfx": [fx("distant street protest crowd and bins scraping on asphalt, outdoor", 5, 0.07)]})
say(2, g2("montage", items=[
    {"file": ppath("bins"), "credit": photo_credit(P["bins"]), "from": [1.05, 0.5, 0.55], "to": [1.15, 0.5, 0.5]},
    {"file": ppath("gate"), "at": "With barriers", "credit": photo_credit(P["gate"]), "from": [1.08, 0.5, 0.5], "to": [1.18, 0.5, 0.48]},
    {"video": "assets/news/afp_chain.mp4", "at": "With human", "start": 0.5, "credit": "Video: AFP", "frame": 0.8}]))
say(3, g2("crowd", bg=ppath("march_wide"), title="6 OCTOBER · ACROSS FRANCE",
          a={"value": 250000, "label": "POLICE", "at": "police counted"},
          b={"value": 450000, "label": "ORGANISERS", "at": "four hundred"},
          source="Interior Ministry / unions, 6 Oct 2026"), sfx=TICK)
say(4)
say(5, g2("icons", n=6877, shape="person", box=[110, 330, 1810, 1030], bg=ppath("crs_line"),
          appear_at="six thousand", appear_d=1.6,
          highlight={"k": 5914, "at": "Eighty-six", "d": 1.4},
          head=[{"text": "", "count": 6877, "at": "six thousand", "x": 560, "y": 150, "size": 150, "color": "amber", "roll": 1.4},
                {"text": "IN POLICE CUSTODY", "at": "six thousand", "x": 560, "y": 262, "size": 54},
                {"text": "86%", "at": "Eighty-six", "x": 1360, "y": 150, "size": 150, "color": "amber"},
                {"text": "ARE MINORS", "at": "Eighty-six", "x": 1360, "y": 262, "size": 54}],
          source="Justice Ministry, to 8 Oct 2026"))
B.append({"visual": g2("blackfade", file=ppath("crowd_blur"), hold=1.0, fade=2.6, blur=16, dark=0.5,
                       credit=photo_credit(P["crowd_blur"])),
          "say": LINES[6], "lead": 0.9, "hold": 0.7, "sfx": fx("single low sustained cello note, dark, quiet", 4, 0.07, at=0.9)})
say(7, d3(7, "france_map", "spark"), trans="dip", hold=0.3)
say(8, img("droit", (1.15, 0.5, 0.4), (1.28, 0.5, 0.38)), trans="flash")
say(9, d3(9, "france_police", "standoff"))
say(10, d3(10, "france_calendar", "teaser"))
B.append({"visual": cc("Lycée_Louis-le-Grand_in_Paris_77", 0.5), "hold": 3.4, "dim": True, "trans": "dip",
          "text": {"kind": "title", "content": "{\\fs150}FRANCE'S " + A + "SCHOOL REVOLT\\N{\\fs64}" + C + "AUTUMN 2026",
                   "pos": [0.5, 0.5]}, "sfx": HIT})
say(12, hold=0.4)

# ================================================================ 1. So how did it start?
chapter("So how did it start?", "So how did\\Nit *start*?", cc("Lycée_Louis-le-Grand_in_Paris_86", 12.0), bid="act1")
say(13, d3(13, "france_map", "creteil_hold"), text=key("CRÉTEIL"))
say(14, d3(14, "france_lycee", "exterior"), text=key("{\\fs72}LYCÉE SAINT-EXUPÉRY\\N{\\fs110}~1,500 PUPILS", 0.8))
say(15, dim=True, overlay=ov("lycee_def", at="A lycée"))
say(16, d3(16, "france_lycee", "three_empty"), text=key("EMPTY POSTS"))
say(17, d3(17, "france_calendar", "sept17"))
say(18, d3(18, "france_lycee", "bins_slide"), text=key("BLOCKADE", size=120))
say(19, d3(19, "france_phone", "posts:15"))
say(20, hold=0.3)
say(21, d3(21, "france_phone", "viral:16"), text=key("{\\fs64}24 SEPT · RAP-NEWS INTERVIEW", 0.12))
say(22)
say(23, text=key("1.5 MILLION VIEWS", 0.12, 110))
say(24, d3(24, "france_map", "spread:21"), overlay=ov("day_counter", beats=4, label="SCHOOLS DISRUPTED", steps=[
    {"at": "twenty-fifth", "date": "25 SEPT", "day": 8, "value": 60, "approx": True},
    {"at": "Three days later", "date": "28 SEPT", "day": 11, "value": 180},
    {"at": "one thousand and twenty-seven", "date": "1 OCT", "day": 14, "value": 1027}]))
say(25)
say(26)
say(27, hold=0.5)
say(28, g2("icons", n=3700, shape="school", box=[160, 330, 1760, 1020], aspect=1.0, bg=ppath("colbert_door"),
           appear_at=0.1, appear_d=0.8, highlight={"k": 1027, "at": "more than a quarter", "d": 1.0},
           head=[{"text": "", "count": 1027, "at": 0.2, "x": 560, "y": 160, "size": 140, "color": "amber"},
                 {"text": "OF ~3,700 LYCÉES", "at": 0.2, "x": 560, "y": 268, "size": 52},
                 {"text": "1 IN 4", "at": "more than a quarter", "x": 1360, "y": 190, "size": 170, "color": "amber"}],
           source="Interior Ministry, 1 Oct 2026"))
say(29, news("reuters_gate", "Reuters", 0.0, 0.8))
say(30, d3(30, "france_lycee", "cut:4.5"), hold=0.4, fade_out=1.6)

# ================================================================ 2. What are they angry about?
chapter("What are they angry about?", "What are they\\N*angry* about?", cc("Lycée_Louis-le-Grand_in_Paris_75", 20.0), bid="act2")
say(31, d3(31, "france_lycee", "hall"))
say(32, d3(32, "france_lycee", "facade_age"), text=key("65 YEARS OLD, ON AVERAGE", size=96))
say(33, g2("bars", bg=ppath("colbert_street"), title="FRANCE'S LYCÉE BUILDINGS", items=[
    {"label": "BUILT BEFORE 1970", "value": 56, "at": "More than half"},
    {"label": "BUILT OR RENOVATED SINCE 2015", "value": 14, "at": "More than half", "color": "ink"}],
    max=100, unit_suffix="%", ytop=600, gap=200, x0=1000, x1=1560,
    head=[{"text": "65 YEARS OLD, ON AVERAGE", "at": 0.1, "y": 330, "size": 96, "color": "amber"}],
    source="franceinfo, 5 Oct 2026 (general & technological lycées)"))
say(34, d3(34, "france_lycee", "leak"))
say(35, d3(35, "france_lycee", "heat"), text=key("35–40°C"))
say(36, d3(36, "france_money", "repair_need"), text=key("€1.5 BN A YEAR NEEDED"))
say(37, d3(37, "france_lycee", "empty_desk"))
say(38, g2("icons", n=1033, shape="school", box=[200, 330, 1720, 1010], aspect=1.0, bg=ppath("prof_greve"),
           appear_at="surveyed", appear_d=1.0, highlight={"k": 548, "at": "Fifty-three", "d": 1.0},
           head=[{"text": "1,033 SCHOOLS SURVEYED", "at": "surveyed", "y": 160, "size": 80},
                 {"text": "53% MISSING A TEACHER", "at": "Fifty-three", "y": 262, "size": 80, "color": "amber"}],
           source="SNES-FSU survey, Sept 2026"))
say(39)
say(40, g2("split", bg=ppath("prof_greve"),
           left={"head": "TEACHERS' UNION", "big": "53%", "body": ["of schools missing", "at least one teacher"], "at": 0.1},
           right={"head": "MINISTRY", "big": "96.1%", "body": ["of secondary posts", "filled"], "at": "ninety-six"},
           source="SNES-FSU / Education Ministry, Sept 2026"))
say(41, d3(41, "france_timetable", "lost_lessons"), text=key("10% OF LESSONS LOST"))
say(42, img("lecons", (1.05, 0.5, 0.5), (1.16, 0.5, 0.45)), dim=True,
    text=quote("“Six months without a teacher,\\Nin an exam subject.”", "PUPIL, TO EURONEWS"))
say(43, d3(43, "france_lycee", "crowded", 2), text=key("37 PUPILS", size=120))
say(44, d3(44, "france_timetable", "hours"), text=key("1,200 vs 960 HOURS"))
say(45, d3(45, "france_parcoursup", "dashboard"))
say(46, g2("line", bg=ppath("parcoursup"), title="NO OFFER IN THE MAIN ROUND", points=[
    {"x_label": "2024", "value": 10, "at": 0.3}, {"x_label": "2025", "value": 11.9, "dec": 1, "at": 0.9},
    {"x_label": "2026", "value": 18, "at": "eighteen percent"}], ymax=24, source="Parcoursup data, via Le Monde, 11 Jul 2026"))
say(47, d3(47, "france_state", "assemblee"), text=key("2027 BUDGET · 1 OCT", size=96))
say(48, g2("stat", bg=ppath("budget"), items=[
    {"value": 1.2, "dec": 1, "prefix": "+€", "suffix": " BN", "label": "EDUCATION SPENDING IN THE 2027 BUDGET", "at": "one point two"}],
    source="Draft budget, 1 Oct 2026 (excluding pensions)"))
say(49, d3(49, "france_staffroom", "tags_fall"), text=key("−1,588 TEACHING POSTS"))
say(50, text=key("{\\fs64}GOVERNMENT: ~180,000 FEWER PUPILS EXPECTED", 0.86))
say(51, d3(51, "france_calendar", "oct1"))
say(52, d3(52, "france_map", "ignite"), hold=0.3)

# ================================================================ 3. Where is it burning?
chapter("Where is it burning?", "Where is it\\N*burning*?", img("rennes", (1.04, 0.5, 0.5), (1.12, 0.5, 0.5)), bid="act3")
say(53, d3(53, "france_map", "tour"))
say(54, text=key("SAINT-DENIS · SARCELLES · LA COURNEUVE", size=64))
say(55, text=key("MARSEILLE · LILLE · LYON", size=72))
say(56, text=key("NANTES · RENNES · BORDEAUX · TOULOUSE · STRASBOURG", size=56))
say(57, g2("stat", bg=ppath("crs_voltaire"), items=[
    {"value": 1949, "label": "ARRESTS IN ONE DAY · 1 OCT", "at": "one thousand nine hundred"}],
    source="Interior Ministry, 1 Oct 2026"))
say(58, d3(58, "france_map", "blockaded"), text=key("222 FULLY BLOCKADED"))
say(59, d3(59, "france_aftermath", "nantes"), text=key("NANTES", 0.12))
say(60, d3(60, "france_aftermath", "marseille"), text=key("MARSEILLE", 0.12))
say(61, d3(61, "france_map", "border"), text=key("BELGIUM → ITALY"))
say(62, d3(62, "france_map", "padlocks"), text=key("~400 LYCÉES CLOSED"))
say(63, hold=0.3)
say(64, d3(64, "france_calendar", "oct6"), text=key("6 OCTOBER", size=120), hold=0.4)

# ================================================================ 4. What happened on October 6th?
chapter("What happened on October 6th?", "What happened\\Non *October 6th*?", img("march_wide", (1.03, 0.5, 0.5), (1.1, 0.5, 0.5)), bid="act4")
say(65, img("republique", (1.04, 0.5, 0.45), (1.16, 0.5, 0.4)), sfx=CROWD)
say(66, img("crs_voltaire", (1.04, 0.5, 0.5), (1.14, 0.55, 0.5)), text=key("~2,000 OFFICERS"))
say(67, g2("bars", bg=ppath("march_wide"), title="PARIS · 6 OCTOBER", items=[
    {"label": "POLICE", "value": 56000, "at": "fifty-six", "color": "ink"},
    {"label": "ORGANISERS", "value": 100000, "at": "a hundred thousand"}], ytop=480, gap=240,
    source="Police / organisers, 6 Oct 2026"))
say(68, d3(68, "france_map", "oct6"))
say(69, news("ap_cortege", "AP", 0.0))
say(70, cc("Lycée_Louis-le-Grand_in_Paris_78", 0.5), text=key("LOUIS-LE-GRAND · HENRI-IV", size=76))
say(71, img("briller", (1.04, 0.4, 0.5), (1.12, 0.6, 0.5)))
say(72, img("trop_jeune", (1.08, 0.5, 0.5), (1.18, 0.5, 0.48)), dim=True,
    text=quote("“Too young to be listened to,\\Nbut not too young to be clubbed.”", "Trop jeune pour être écouté mais pas trop jeune pour être matraqué"))
say(73, img("avenir", (1.04, 0.5, 0.5), (1.14, 0.5, 0.48)), text=key("“WE JUST WANT A FUTURE”"))
say(74, g2("bars", bg=ppath("crowd_blur"), title="ACROSS FRANCE · 6 OCTOBER", items=[
    {"label": "POLICE", "value": 250000, "at": "quarter of a million", "color": "ink"},
    {"label": "ORGANISERS", "value": 450000, "at": "Four hundred and fifty"}], ytop=480, gap=240,
    source="Interior Ministry / unions, 6 Oct 2026"))
say(75, news("reuters_teargas", "Reuters", 0.0, speed=0.8), text=key("488+ ARRESTS · 43 OFFICERS HURT", size=72))
say(76, news("afp_lecornu", "AFP", 0.0, speed=0.8))
say(77, img("llg_flag", (1.04, 0.5, 0.5), (1.12, 0.5, 0.5)), dim=True, text=quote("“A complete cacophony”", "HEADTEACHERS' UNION"))
say(78, fade_out=2.6)
say(79, {"type": "black"}, hold=0.8, text={"kind": "label", "content": A + "Why were teenagers getting hurt?", "pos": [0.5, 0.5]})

# ================================================================ 5. Why are teenagers getting hurt?
chapter("Why are teenagers getting hurt?", "Why are teenagers\\Ngetting *hurt*?", img("crs_line", (1.03, 0.5, 0.5), (1.1, 0.5, 0.5)), bid="act5")
say(80, d3(80, "france_weapons", "lineup"))
say(81, text=key("INTERMEDIATE WEAPONS"))
say(82, d3(82, "france_weapons", "lbd"), text=key("LBD"))
say(83, d3(83, "france_weapons", "gas"))
say(84, d3(84, "france_weapons", "grenade"))
say(85, img("crs_voltaire", (1.15, 0.6, 0.5), (1.25, 0.6, 0.5)), text=key("{\\fs64}NUÑEZ: NO INSTRUCTION TO HOLD BACK", 0.86))
say(86, d3(86, "france_map", "cases"))
say(87, d3(87, "france_weapons", "close_range"), text=key("SAINT-OUEN-L'AUMÔNE · AGE 14", size=72))
say(88, g2("split", bg=ppath("perpignan_police"),
           left={"head": "PROSECUTOR", "big": "28 SEPT", "big_size": 120, "body": ["says the boy struck", "a policewoman first"], "at": 0.1},
           right={"head": "6 OCTOBER", "big": "CHARGED", "big_size": 120, "body": ["the officer who fired"], "at": "On October sixth"}))
say(89, d3(89, "france_map", "cases_fly"), text=key("TOURS · AGE 16", size=80))
say(90, text=key("LENS · AGE 15", size=80))
say(91, dim=True)
say(92, d3(92, "france_weapons", "suspended"), text=key("STUN GRENADES SUSPENDED · 7 OCT", size=72))
say(93, g2("icons", n=24, shape="slot", box=[460, 380, 1460, 960], aspect=0.75, bg=ppath("crs_line"),
           appear_at="twenty-four", appear_d=1.2,
           head=[{"text": "24", "at": "twenty-four", "y": 200, "size": 170, "color": "amber"},
                 {"text": "IGPN INVESTIGATIONS", "at": "twenty-four", "y": 320, "size": 60}], source="ICI, 9 Oct 2026"))
say(94, img("perpignan_police", (1.04, 0.5, 0.5), (1.12, 0.5, 0.5)), dim=True,
    text={"kind": "label", "content": "{\\fs72}AMNESTY · UNICEF FRANCE · UN HUMAN RIGHTS OFFICE", "pos": [0.5, 0.5]})
say(95, d3(95, "france_police", "behind_line"))
say(96, g2("icons", shape="person", box=[120, 340, 1800, 1000], bg=ppath("smoke"), groups=[
    {"n": 761, "label": "761 POLICE & GENDARMES", "at": "seven hundred", "color": [205, 200, 190], "box": [100, 330, 1040, 930]},
    {"n": 215, "label": "215 PUPILS", "at": "two hundred and fifteen", "color": "amber", "box": [1120, 330, 1500, 930]},
    {"n": 89, "label": "89 STAFF", "at": "eighty-nine", "color": [150, 148, 142], "box": [1580, 330, 1820, 930]}],
    head=[{"text": "INJURED", "at": 0.1, "y": 180, "size": 110}], source="Interior Minister, 7 Oct 2026"))
say(97)
say(98, img("belfort", (1.04, 0.5, 0.5), (1.12, 0.5, 0.5)), text=key("BELFORT"))
say(99, d3(99, "france_lycee", "firework"))
say(100, {"type": "black"}, lead=0.6, hold=0.8, text=key("NO ONE HAS DIED", 0.5))
say(101, g2("icons", n=6877, shape="person", box=[110, 340, 1810, 1030], bg=ppath("crowd_blur"),
            appear_at=0.1, appear_d=0.8, highlight={"k": 2376, "at": "two thousand three hundred", "d": 1.2},
            head=[{"text": "6,877 IN CUSTODY", "at": 0.1, "x": 560, "y": 180, "size": 72},
                  {"text": "2,376 PROSECUTED", "at": "two thousand three hundred", "x": 1360, "y": 180, "size": 72, "color": "amber"}],
            source="Justice Ministry, to 8 Oct 2026 (1,923 of them minors)"))
say(102, d3(102, "france_state", "matignon"), hold=0.3)

# ================================================================ 6. What is the government doing?
chapter("What is the government doing?", "What is the government\\N*doing*?", img("egalite", (1.03, 0.5, 0.5), (1.1, 0.5, 0.5)), bid="act6")
say(103, news("lcp_assembly", "LCP", 0.0))
say(104, img("republique", (1.2, 0.4, 0.45), (1.3, 0.45, 0.45)), dim=True, text=quote("“An operation organised by\\NLa France Insoumise”", "PRIME MINISTER'S OFFICE, 1 OCT"))
say(105, g2("phone_posts", bg=ppath("colbert_street"), photo=ppath("gate"), date="21 SEPT", underline_at=0.4))
say(106, d3(106, "france_state", "dossier"))
say(107, g2("doc", bg=ppath("budget"), title="INTELLIGENCE NOTE (ILLUSTRATION)", mark_at="six times", lines=[
    "Seine-Saint-Denis, 21 – 25 Sept █ ██ █",
    "presence of [[outsiders]] at the gates █",
    "█ ██ [[outsiders]] █ █ ██ █ ██ █",
    "[[outsiders]] █ ██ █ █ ██ █ █",
    "█ [[outsiders]] █ █ ██ █ [[LFI]] █",
    "█ ██ [[outsiders]] █ █ ██ █",
    "[[outsiders]] █ █ ██ █ ██ █"],
    tally=[{"text": "×6", "at": "six times", "y": 380, "label": "OUTSIDERS"},
           {"text": "×1", "at": "The party, once", "y": 700, "label": "THE PARTY", "color": "ink"}],
    source="As reported by Le Monde"))
say(108, img("egalite", (1.12, 0.5, 0.5), (1.2, 0.5, 0.5)), dim=True, text=quote("“Conspiracy thinking”", "LA FRANCE INSOUMISE"))
say(109, text=quote("“The voice of high-school students\\Nis precious, and must be heard.”", "SÉBASTIEN LECORNU, ON X"))
say(110, news("franceinfo_geffray", "franceinfo", 0.0, speed=0.85))
say(111, g2("stat", bg=ppath("prof_greve"), items=[{"value": 3024, "label": "SUPPLY TEACHERS", "at": "Three thousand teachers"}],
            source="Education Ministry, 8 Oct 2026"))
say(112, d3(112, "france_teachers", "standby"), text=key("{\\fs64}ALREADY PAID · NOT ASSIGNED TO CLASSES", 0.88))
say(113, d3(113, "france_map", "red_orange"), text=key("114 RED · ~400 ORANGE"))
say(114, img("lecons", (1.15, 0.5, 0.5), (1.24, 0.5, 0.45)), dim=True, text=quote("“A first concrete announcement”", "LES LYCÉENS"))
say(115, text=quote("“We don't want words.\\NWe want action.”", "PUPIL, 17, NANTES · FRANCE 24"))
say(116, d3(116, "france_teachers", "drop"))
say(117, d3(117, "france_teachers", "empty_field"), text=key("“NOT ASSIGNED”"))
say(118, d3(118, "france_aftermath", "ransacked"), text=key("24 LYCÉES BURNED OR RANSACKED", size=72))
say(119, g2("icons", n=300, shape="desk", box=[200, 340, 1720, 1000], aspect=0.8, bg=ppath("colbert_door"),
            appear_at=0.1, appear_d=0.8, blank={"k": 300, "at": "no classes", "d": 1.0},
            head=[{"text": "30,000", "at": "thirty thousand", "y": 170, "size": 160, "color": "amber"},
                  {"text": "PUPILS WITHOUT IN-PERSON CLASSES", "at": "thirty thousand", "y": 290, "size": 56}],
            source="Education Minister, 5 Oct 2026 · 1 desk = 100 pupils"))
say(120, news("reuters_fire", "Reuters", 0.0))
say(121, g2("bars", bg=ppath("smoke"), title="DAMAGE TO LYCÉES", items=[
    {"label": "AUVERGNE-RHÔNE-ALPES", "value": 27.5, "text": "€25–30M", "at": 0.3},
    {"label": "ÎLE-DE-FRANCE", "value": 7, "at": 0.6},
    {"label": "OCCITANIE", "value": 3, "at": 0.9}], unit_prefix="€", unit_suffix="M", max=30, x0=860, x1=1450, ytop=360, gap=170,
    label_size=50, head=[{"text": "€30 MILLION+", "at": "thirty million", "y": 900, "size": 130, "color": "amber"}],
    source="Regional presidents / government source, 9 Oct 2026"))
say(122, {"type": "black"}, text={"kind": "title", "content": "{\\fs130}" + A + "“CASSEURS-PAYEURS”\\N{\\fs70}" + C + "RIOTERS PAY",
                                  "pos": [0.5, 0.5]})
say(123, d3(123, "france_money", "fine"), text=key("UP TO €10,000 EACH"))
say(124, g2("donut", bg=ppath("march_wide"), title="ODOXA POLL FOR LE FIGARO", items=[
    {"value": 62, "label": "SAY THE MOVEMENT IS JUSTIFIED", "at": "sixty-two", "x": 560},
    {"value": 78, "label": "SAY LFI IS EXPLOITING IT", "at": "seventy-eight", "x": 1360}]))
say(125)
say(126, img("parcoursup", (1.04, 0.5, 0.5), (1.12, 0.5, 0.5)))

# ================================================================ 7. What happens next?
chapter("What happens next?", "What happens\\N*next*?", img("budget", (1.03, 0.5, 0.5), (1.1, 0.5, 0.5)), bid="act7")
say(127, d3(127, "france_map", "dimming"))
say(128, g2("stat", bg=ppath("colbert_door"), items=[
    {"value": 1027, "label": "LYCÉES AFFECTED · 1 OCT", "at": 0.2, "x": 560, "size": 170, "color": "ink"},
    {"value": 141, "label": "STILL CLOSED · 9 OCT", "at": "a hundred and forty-one", "x": 1360, "size": 170}],
    source="Interior / Education Ministry"))
say(129, g2("split", bg=ppath("colbert_street"),
            left={"head": "GOVERNMENT SOURCE", "big": "SLOWING", "big_size": 130, "body": ["“a clear deceleration”"], "at": 0.1},
            right={"head": "PUPIL UNIONS", "big": "NOT OVER", "big_size": 130, "body": ["“non”"], "at": "Pupil unions"}))
say(130, d3(130, "france_calendar", "wall"))
say(131, d3(131, "france_calendar", "oct13"), text=key("13 OCT", 0.12))
say(132, d3(132, "france_phone", "anon"), text=key("17 OCT", 0.12))
say(133, d3(133, "france_calendar", "oct17"), text=key("NOT AN OFFICIAL UNION DATE", size=72))
say(134)
say(135, d3(135, "france_calendar", "oct23_27"))
say(136)
say(137, d3(137, "france_calendar", "nov5"))
say(138)
say(139, d3(139, "france_calendar", "apr2027"), text=key("APRIL 2027 · PRESIDENTIAL ELECTION", size=72))
say(140, d3(140, "france_map", "ripple"))
say(141)
say(142, img("egalite", (1.04, 0.5, 0.45), (1.16, 0.5, 0.42)), hold=1.2, id="last")
say(143, {"type": "black"}, hold=2.5, fade_out=0.1,
    text={"kind": "title", "content": "{\\fs130}" + A + "STRATA", "pos": [0.5, 0.47]})
B[-1]["visual"] = img("budget", (1.1, 0.5, 0.5), (1.16, 0.5, 0.5))
B[-1]["fade_out"] = 3.0
B[-1]["dim"] = True

# ---------------------------------------------------------------- music (Kevin MacLeod, incompetech.com, CC BY 4.0)
MUSIC = [
    ("music/m1_crypto.mp3", "intro", "act2", 0.13),          # Crypto
    ("music/m2_hiding.mp3", "act2", "act3", 0.12),           # Hiding Your Reality
    ("music/m3_tide.mp3", "act3", "act5", 0.13),             # Rising Tide
    ("music/m4_lightless.mp3", "act5", "act6", 0.14),        # Lightless Dawn
    ("music/m5_interloper.mp3", "act6", "act7", 0.12),       # Interloper
    ("music/m6_floating.mp3", "act7", "end", 0.14),          # Floating Cities
]
music = []
for i, (f, a, z, v) in enumerate(MUSIC):
    m = {"file": f, "from": a, "to": z, "vol": v, "fade_in": 3.0 if i else 2.0, "fade_out": 3.0}
    if i:
        m["offset"] = -2.5   # crossfade into the next bed: no gap, no silence
    if z == "end":
        m["fade_out"] = 5.0
    music.append(m)

spec = {
    "voice": {"engine": "elevenlabs", "voice_id": "DrBEKFgWMDWUG6bjTSTk", "model": "eleven_v4", "stability": 0.5, "speed": 1.0},
    "gap": 0.2,
    # real photos/footage stay in colour with a light warm grade (no black and white)
    "look": "eq=contrast=1.06:saturation=1.12:brightness=-0.01,colorbalance=rs=0.035:bs=-0.045:rm=0.025:bm=-0.03",
    # keep each line's natural decay and fade it out over 150 ms; never a hard stop
    "tail": {"keep": 0.25, "fade": 0.15},
    # 3D renders are reused across the small retiming (cut, or last frame held, within 1.2 s)
    "reuse_3d": 1.2,
    "subtitles": False,
    "declick": True,
    "sfx_gain_db": -4,
    "style_fields": {"CREDIT": {"PrimaryColour": "&H80B4B4B4", "Alignment": 1, "MarginL": 30, "MarginR": 0, "Fontsize": 24},
                     "LABEL": {"Fontsize": 96, "Outline": 6, "Shadow": 0},
                     "TITLE": {"Outline": 8, "Shadow": 0},
                     "QUOTE": {"Fontsize": 84, "Outline": 5, "Shadow": 0},
                     "CHAPTER": {"Outline": 7},
                     "YEAR": {"Outline": 10, "Shadow": 0}},
    "fonts": {"LABEL": "YouTube Sans", "YEAR": "YouTube Sans", "FX": "YouTube Sans", "CREDIT": "YouTube Sans",
              "TITLE": "YouTube Sans", "QUOTE": "Playfair Display"},
    "music": music,
    "beats": B,
}

def plain(o, inside_quote=False):
    """YouTube Sans has no curly quotes or en dash: straighten them everywhere except the serif QUOTE style."""
    if isinstance(o, dict):
        q = o.get("kind") == "quote"
        return {k: plain(v, q) for k, v in o.items()}
    if isinstance(o, list):
        return [plain(v, inside_quote) for v in o]
    if isinstance(o, str) and not inside_quote:
        return o.replace("“", '"').replace("”", '"').replace("–", "-")
    return o


for b in B:
    for k in ("visual", "text", "overlay"):
        if isinstance(b.get(k), (dict, list)):
            b[k] = plain(b[k])

if __name__ == "__main__":
    json.dump(spec, open(os.path.join(HERE, "script.json"), "w"), ensure_ascii=False, indent=1)
    says = [b["say"] for b in B if b.get("say")]
    assert says == [LINES[k] for k in sorted(LINES)], "narration order must match lines.py (TTS cache + context)"
    print(len(B), "beats,", sum(len(s.split()) for s in says), "words,", sum(map(len, says)), "chars,", len(ARG3), "3D shots listed")
