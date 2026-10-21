"""Gym Funny Moments v6 (owner 2026-10-21 17:26 KST): back to the v3 cat-meme format he liked for its pace and
humour (flash only into and out of the cat meme, rewind, graded slow-mo replay), with the 17:05 rules kept: no
background music (claim), no added SFX, original clip sound only, and music or meme-sound beds muted. All earlier
clips scrapped; new viral sources from funny_sourcing_2026-10-21.md (src/new1, TikTok ids).
"""
import json, os

N = '/home/user/rs_work/src/new1/'
M = '/home/user/rs_work/memes/t/'
HERE = os.path.dirname(os.path.abspath(__file__))
EDIT = {"b": 0.04, "c": 1.12, "s": 1.2}          # replay grade


def meme(src, cap=None, **kw):
    return dict({"type": "meme", "src": src, "dur": 0.75, "cap": cap}, **kw)


def short(name, title, *beats):
    return name, {
        "font": "/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF",
        "memeBg": "black", "capSize": 84, "capY": 960,
        "title": {"text": title, "y": 190, "size": 60},
        "segments": [s for b in beats for s in b]}


def clip(src, **kw):
    return dict({"type": "clip", "src": src, "ratio": "9:16", "track": [[0, 0.5, 0.5, 1.0]]}, **kw)


def replay(src, **kw):
    return clip(src, grade=EDIT, **kw)


# House of Highlights 24.7M: on the assisted dip machine the pad launches her upside down (bed is music: muted)
ASSIST = N + '7685610049716210957.mp4'
ASK = {"vol": 0, "crop": [70, 286, 940, 940], "ratio": "1:1"}   # square above the burned-in caption, so zooms never slice it
ASSIST_FLIP = [
    clip(ASSIST, **ASK, **{"in": 1.4, "out": 4.6,
         "hits": [{"at": 3.9, "x": 0.35, "y": 0.4, "zoom": 1.15}]}),
    meme(M + 'shocked-cat__a8BssDCesmY__cat-meme-omg-cat.mp4', "Spider-Woman unlocked 😭"),
    clip(ASSIST, **ASK, **{"in": 3.4, "out": 4.6, "reverse": 3.0}),
    replay(ASSIST, **ASK, **{"in": 3.4, "out": 6.6, "speed": [[3.4, 1.0], [3.6, 0.4], [4.6, 1.0]],
           "hits": [{"at": 3.6, "x": 0.32, "y": 0.4, "zoom": 1.2},
                    {"at": 5.0, "x": 0.5, "y": 0.45, "zoom": 1.05, "dur": 0.6}]})]

# Overtime 5.2M CCTV: lying back with the dumbbells, he rolls clean over the bench next to everyone
# (its sound is added meme dings: muted)
BENCH = N + '7678461460221070605.mp4'
BK = {"vol": 0}
BENCH_ROLL = [
    clip(BENCH, **BK, **{"in": 4.6, "out": 8.1,
         "hits": [{"at": 6.6, "x": 0.45, "y": 0.45, "zoom": 1.15}]}),
    meme(M + 'crying-cat__nlRnupio1IY__sobbing-cat.mp4', "In front of EVERYONE 💀"),
    clip(BENCH, **BK, **{"in": 6.4, "out": 8.1, "reverse": 3.0}),
    replay(BENCH, **BK, **{"in": 6.4, "out": 9.6, "speed": [[6.4, 1.0], [6.6, 0.4], [8.2, 1.0]],
           "hits": [{"at": 6.6, "x": 0.4, "y": 0.45, "zoom": 1.2},
                    {"at": 8.4, "x": 0.4, "y": 0.6, "zoom": 1.1, "dur": 0.6}]})]

SHORTS = [short("48_backflips", "Accidental Gym Backflips 😭", ASSIST_FLIP, BENCH_ROLL)]

# --- 49: recent viral clips (funny_recent, posted 2026-10-01 / 10-09) -------------------------------------------
REC = '/mnt/project-files/sources/ragestyles/funny_recent/'
FAV = '/home/user/rs_work/memes/fav_cat.png'
# ESPN 3.6M: his trail foot clips the hurdle, it flips up into him and he slams flat (real sound kept)
HURDLE = REC + '01_2026-10-09_hurdle_uppercut_faceplant_7694656600287563038.mp4'
HURDLE_SLAM = [
    clip(HURDLE, vol=1.0, **{"in": 0.9, "out": 2.75,
         "hits": [{"at": 2.2, "x": 0.5, "y": 0.5, "zoom": 1.15}]}),
    meme(FAV, "The hurdle hit BACK 😭"),
    clip(HURDLE, **{"in": 1.8, "out": 2.75, "reverse": 3.0}),
    replay(HURDLE, vol=1.0, **{"in": 1.8, "out": 5.0, "speed": [[1.8, 1.0], [2.0, 0.4], [3.4, 1.0]],
           "hits": [{"at": 2.0, "x": 0.5, "y": 0.5, "zoom": 1.2},
                    {"at": 3.6, "x": 0.5, "y": 0.55, "zoom": 1.1, "dur": 0.6}]})]

# swabyfitt "4 exercises" reposts (bed is a song: muted). Cable skullcrushers: the machine's top frame comes down
FOUR = REC + '03_2026-10-01_four_gym_fails_cable_rack_collapse_7691767958514797856.mp4'
FK = {"vol": 0}
CABLE_FRAME = [
    clip(FOUR, **FK, **{"in": 3.0, "out": 4.9,
         "hits": [{"at": 4.35, "x": 0.5, "y": 0.45, "zoom": 1.12}]}),
    meme(M + 'crying-cat__b8jzGatOpv8__noo.mp4'),
    clip(FOUR, **FK, **{"in": 4.0, "out": 4.9, "reverse": 3.0}),
    replay(FOUR, **FK, **{"in": 4.0, "out": 4.95, "speed": [[4.0, 1.0], [4.2, 0.35]],
           "hits": [{"at": 4.2, "x": 0.5, "y": 0.4, "zoom": 1.15}]})]

# "automatic unrack": the plates slide off one side and the barbell catapults up past him
UNRACK = [
    clip(FOUR, **FK, **{"in": 7.6, "out": 9.6,
         "hits": [{"at": 8.6, "x": 0.5, "y": 0.45, "zoom": 1.1}]}),
    meme(M + 'surprised-cat__ZuXnTDxIbjQ__shocked-shocked-cat.mp4', "Bar said BYE 💀"),
    clip(FOUR, **FK, **{"in": 8.0, "out": 9.6, "reverse": 3.0}),
    replay(FOUR, **FK, **{"in": 8.0, "out": 9.95, "speed": [[8.0, 1.0], [8.3, 0.45], [9.5, 1.0]],
           "hits": [{"at": 8.3, "x": 0.5, "y": 0.45, "zoom": 1.15}]})]

SHORTS.append(short("49_fights_back", "Gym Equipment Fights Back 😭", HURDLE_SLAM, CABLE_FRAME, UNRACK))

if __name__ == '__main__':
    for name, spec in SHORTS:
        json.dump(spec, open(os.path.join(HERE, name + '.json'), 'w'), indent=1, ensure_ascii=False)
    print(' '.join(n for n, _ in SHORTS))
