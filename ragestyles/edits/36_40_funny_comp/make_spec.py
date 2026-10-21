"""Five 10 s+ Gym Funny Moments shorts (user 2026-10-20): two HD clips per short, each with the beat the user
called perfect on short 33 (red ring on the cause from the first frame, play to the moment, white flash into a
cat meme, rewind with slow-mo + ease-out zoom). User's music bed under everything; source audio muted where it
is music or a narrator, so only real gym sound stays."""
import json, os

R = '/home/user/rs_work/src/reddit/'
A, B = '/home/user/rs_work/src/hd_bank/a/', '/home/user/rs_work/src/hd_bank/b/'
M = '/home/user/rs_work/memes/t/'
FAV = '/home/user/rs_work/memes/fav_cat.png'
SFX, LIB, DRV = '/mnt/project-files/sfx/meme/', '/home/user/rs_work/sfx/', '/mnt/project-files/sfx/drive/'
BGM = '/mnt/project-files/sfx/music/user_bgm_QKThr.mp3'
HERE = os.path.dirname(os.path.abspath(__file__))

CONFUSED = M + 'confused-cat__cuW62FiZhBw__cat-stare-blinking-loop-lopped.mp4'
SIDE_EYE = M + 'cat-side-eye__LoTSdDHzoc0__cat-annoyed.mp4'
SHOCKED = M + 'shocked-cat__keHPVm2ArXc__stellarnushu.mp4'
FLABBER = M + 'shocked-cat__btYkcmAPyCc__cat-flabbergasted.mp4'
CRYING = M + 'crying-cat__9a9g-pOTZHk__nsb14-meowl.mp4'
HOLD = {SIDE_EYE: 0.55, FLABBER: 0.75}


def beat(first, meme, cap, replay):
    m = {"type": "meme", "src": meme, "dur": 0.75, "cap": cap}
    if meme in HOLD:
        m["hold"] = HOLD[meme]
    return [first, m, replay]


def short(name, title, bgm_ss, *beats, bgm_vol=0.6):
    return name, {
        "font": "/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF",
        "boom": "/home/user/rs_work/memes/vine_boom.mp3",
        "memeBg": "black", "capSize": 80,
        "title": {"text": title, "y": 190, "size": 60},
        "bgm": {"src": BGM, "ss": bgm_ss, "vol": bgm_vol},
        "segments": [s for b in beats for s in b]}


def clip(src, **kw):
    return dict({"type": "clip", "src": src, "ratio": "9:16", "track": [[0, 0.5, 0.5, 1.0]]}, **kw)


# --- beats -------------------------------------------------------------------------------------------------
# short 33, unchanged: plates slide off the unclipped side
CLIPS_BOTH = beat(
    clip(R + "1ng2nwz.mp4", **{"in": 0.0, "out": 2.6,
         "circles": [{"from": 0.0, "to": 0.7, "rx": 0.16, "ry": 0.1, "track": [[0.0, 0.24, 0.3]]}]}),
    CONFUSED, "Bro forgot the clips 😭",
    clip(R + "1ng2nwz.mp4", **{"in": 1.2, "out": 3.25, "speed": [[1.2, 1.0], [1.5, 0.45], [2.4, 1.0]],
         "hits": [{"at": 1.5, "x": 0.4, "y": 0.35, "zoom": 1.2}],
         "sfx": [{"at": 1.85, "src": SFX + "lego-breaking.mp3", "ss": 0.08, "vol": 0.9}]}))

# speed reps until the bar tips, plates slide off and he rolls off the bench laughing
BENCH = A + "7642939162378767629.mp4"
BENCH_SLIDE = beat(
    clip(BENCH, vol=0, **{"in": 8.6, "out": 10.5,
         "circles": [{"from": 8.6, "to": 9.3, "rx": 0.12, "ry": 0.12, "track": [[8.6, 0.2, 0.41]]}]}),
    SIDE_EYE, "Bro was speedrunning 💀",
    clip(BENCH, vol=0, **{"in": 9.2, "out": 11.8, "speed": [[9.2, 1.0], [9.45, 0.45], [10.4, 1.0]],
         "hits": [{"at": 9.45, "x": 0.32, "y": 0.38, "zoom": 1.25},
                  {"at": 10.5, "x": 0.55, "y": 0.45, "zoom": 1.15, "dur": 0.6}],
         "sfx": [{"at": 9.95, "src": LIB + "impact_metal.mp3", "vol": 0.8}]}))

# big guy steps onto a fast treadmill and is shot off the back
TREAD = B + "7442160036173860127.mp4"
TREAD_LAUNCH = beat(
    clip(TREAD, vol=0, **{"in": 12.0, "out": 14.3,
         "circles": [{"from": 12.0, "to": 12.7, "rx": 0.16, "ry": 0.4, "track": [[12.0, 0.6, 0.42]]}]}),
    FAV, "He really did it 😭",
    clip(TREAD, vol=0, **{"in": 13.0, "out": 15.5, "speed": [[13.0, 1.0], [13.2, 0.4], [14.1, 1.0]],
         "hits": [{"at": 13.2, "x": 0.55, "y": 0.5, "zoom": 1.25},
                  {"at": 14.1, "x": 0.5, "y": 0.6, "zoom": 1.15, "dur": 0.6}],
         "sfx": [{"at": 13.35, "src": LIB + "whoosh_fast.mp3", "vol": 0.7},
                 {"at": 13.85, "src": LIB + "thud_heavy.mp3", "vol": 0.9}]}))

# hops sideways off a running treadmill, rolls across the floor, pops up like nothing happened
DISMOUNT = B + "7488460918595144990.mp4"
ROLLK = {"crop": [0, 528, 1080, 1392], "ratio": "3:4", "vol": 0}   # drops the burned-in caption that clashed with the title
TREAD_ROLL = beat(
    clip(DISMOUNT, **ROLLK, **{"in": 4.8, "out": 7.1,
         "circles": [{"from": 4.8, "to": 5.45, "rx": 0.14, "ry": 0.4,
                      "track": [[4.8, 0.36, 0.33], [5.1, 0.39, 0.33], [5.45, 0.46, 0.36]]}]}),
    SHOCKED, "Bro did a combat roll 💀",
    clip(DISMOUNT, **ROLLK, **{"in": 5.6, "out": 8.8, "speed": [[5.6, 1.0], [5.8, 0.45], [6.9, 1.0]],
         "hits": [{"at": 5.8, "x": 0.4, "y": 0.45, "zoom": 1.2},
                  {"at": 7.6, "x": 0.55, "y": 0.45, "zoom": 1.1, "dur": 0.6}],
         "sfx": [{"at": 6.3, "src": LIB + "thud_heavy.mp3", "vol": 0.8}]}))

# spotter clips the upright plate beside the bench; ring on the plate from the first frame (user 10/20)
SPOT = R + "1rbl5dp.mp4"
SPOTTER_PLATE = beat(
    clip(SPOT, **{"in": 15.9, "out": 18.9,
         "circles": [{"from": 15.9, "to": 16.9, "rx": 0.075, "ry": 0.15,
                      "track": [[15.9, 0.245, 0.655], [16.5, 0.24, 0.66], [16.9, 0.239, 0.664]]}]}),
    FAV, "Why was it standing??",
    clip(SPOT, **{"in": 16.9, "out": 20.2, "speed": [[16.9, 1.0], [17.3, 0.5], [17.8, 1.0]],
         "hits": [{"at": 16.95, "x": 0.32, "y": 0.62, "zoom": 1.35},
                  {"at": 17.8, "x": 0.45, "y": 0.56, "zoom": 1.25, "dur": 0.6}],
         "circles": [{"from": 17.0, "to": 17.6, "rx": 0.075, "ry": 0.15,
                      "track": [[16.9, 0.239, 0.664], [17.1, 0.229, 0.664], [17.3, 0.215, 0.672],
                                [17.45, 0.195, 0.68], [17.6, 0.17, 0.7]]}],
         "sfx": [{"at": 17.45, "src": SFX + "bowling-pins-falling.mp3", "ss": 0.92, "vol": 0.9}]}))

# "leave me, leave me" ... "get me, get me!": the spotter steps away, then has to dive back in
LEAVE = A + "7491886080573361454.mp4"
LEAVE_ME = beat(
    clip(LEAVE, vol=0, **{"in": 1.2, "out": 6.2, "speed": [[1.2, 1.0], [2.4, 1.8], [4.6, 1.0]],
         "circles": [{"from": 1.2, "to": 2.1, "rx": 0.12, "ry": 0.22,
                      "track": [[1.2, 0.7, 0.3], [2.1, 0.83, 0.3]]}]}),
    SIDE_EYE, "Make up your mind bro 😭",
    clip(LEAVE, vol=0, **{"in": 4.8, "out": 6.95, "speed": [[4.8, 1.0], [5.1, 0.45], [6.1, 1.0]],
         "hits": [{"at": 5.1, "x": 0.5, "y": 0.4, "zoom": 1.2}],
         "sfx": [{"at": 5.15, "src": DRV + "021_노갓플리즈.mp3", "ss": 0.4, "dur": 1.9, "vol": 0.9}]}))

# kicks the heavy bag clean off its chain, then hits a casual flex
BAG = B + "7495415155396726059.mp4"
BAG_KICK = beat(
    clip(BAG, vol=0, **{"in": 1.6, "out": 3.6,
         "circles": [{"from": 1.6, "to": 2.3, "rx": 0.16, "ry": 0.3, "track": [[1.6, 0.3, 0.45]]}]}),
    FLABBER, "He kicked it OFF 💀",
    clip(BAG, vol=0, **{"in": 2.4, "out": 8.0, "speed": [[2.4, 1.0], [2.6, 0.4], [3.5, 1.0], [4.0, 2.2], [7.2, 1.0]],
         "hits": [{"at": 2.6, "x": 0.45, "y": 0.5, "zoom": 1.2},
                  {"at": 7.2, "x": 0.55, "y": 0.35, "zoom": 1.2, "dur": 0.6}],
         "sfx": [{"at": 2.85, "src": LIB + "chain_rattle.mp3", "vol": 0.8},
                 {"at": 3.1, "src": LIB + "thud_heavy.mp3", "vol": 0.9}]}))

# partner drill tossing a loaded barbell: the catcher gets flattened
TOSS = A + "7403775149666864414.mp4"
BAR_TOSS = beat(
    clip(TOSS, vol=0.9, **{"in": 3.4, "out": 5.15,
         "circles": [{"from": 3.4, "to": 4.0, "rx": 0.12, "ry": 0.16, "track": [[3.4, 0.3, 0.52]]}]}),
    CRYING, "Catch it with your HANDS 😭",
    clip(TOSS, vol=0.9, **{"in": 4.0, "out": 5.15, "speed": [[4.0, 1.0], [4.3, 0.4]],
         "hits": [{"at": 4.3, "x": 0.33, "y": 0.5, "zoom": 1.35}],
         "sfx": [{"at": 4.8, "src": LIB + "thud_heavy.mp3", "vol": 0.9},
                 {"at": 4.82, "src": LIB + "impact_metal.mp3", "vol": 0.6}]}))

# resistance-band sprint: the partner holding the band is launched off his feet
BAND = B + "7517757207409167671.mp4"
BAND_SPRINT = beat(
    clip(BAND, vol=0, **{"in": 2.6, "out": 5.0,
         "circles": [{"from": 2.6, "to": 3.3, "rx": 0.18, "ry": 0.14, "track": [[2.6, 0.55, 0.45]]}]}),
    FAV, "He became the sled 😭",
    clip(BAND, vol=0, **{"in": 3.6, "out": 5.9, "speed": [[3.6, 1.0], [3.85, 0.4], [4.7, 1.0]],
         "hits": [{"at": 3.85, "x": 0.3, "y": 0.35, "zoom": 1.2}],
         "sfx": [{"at": 3.9, "src": LIB + "whoosh_fast.mp3", "vol": 0.7},
                 {"at": 4.55, "src": LIB + "thud_heavy.mp3", "vol": 0.9}]}))

# box squat: he sits back, rolls over the box and the plates clatter off (crop drops the burned caption)
BOX = A + "7509176901458578718.mp4"
BOXK = {"crop": [0, 300, 720, 980], "ratio": "3:4", "vol": 0.8}
BOX_SQUAT = beat(
    clip(BOX, **BOXK, **{"in": 3.45, "out": 5.5,
         "circles": [{"from": 3.45, "to": 4.1, "rx": 0.18, "ry": 0.15, "track": [[3.45, 0.55, 0.6]]}]}),
    CONFUSED, "Where did the box go 😭",
    clip(BOX, **BOXK, **{"in": 3.8, "out": 7.0, "speed": [[3.8, 1.0], [4.0, 0.45], [5.0, 1.0]],
         "hits": [{"at": 4.0, "x": 0.5, "y": 0.5, "zoom": 1.2},
                  {"at": 6.3, "x": 0.5, "y": 0.45, "zoom": 1.1, "dur": 0.6}],
         "sfx": [{"at": 4.9, "src": LIB + "impact_metal.mp3", "vol": 0.8}]}))

SHORTS = [
    short("36_plates_no_mercy", "Plates Have No Mercy 💀", 26.0, CLIPS_BOTH, BENCH_SLIDE),
    short("37_treadmill_undefeated", "Treadmills Are Undefeated 😭", 40.0, TREAD_LAUNCH, TREAD_ROLL),
    short("38_spotter_one_job", "The Spotter Had ONE Job 😭💀", 1.0, SPOTTER_PLATE, LEAVE_ME),
    short("39_gym_fought_back", "The Gym Fought Back 💀", 55.0, BAG_KICK, BAR_TOSS),
    short("40_not_ready", "Bro Was NOT Ready 😭", 12.0, BAND_SPRINT, BOX_SQUAT),
]

for name, spec in SHORTS:
    json.dump(spec, open(os.path.join(HERE, name + '.json'), 'w'), indent=1, ensure_ascii=False)
print(' '.join(n for n, _ in SHORTS))
