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
ASK = {"vol": 0, "crop": [0, 286, 1080, 1348], "ratio": "3:4"}
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

if __name__ == '__main__':
    for name, spec in SHORTS:
        json.dump(spec, open(os.path.join(HERE, name + '.json'), 'w'), indent=1, ensure_ascii=False)
    print(' '.join(n for n, _ in SHORTS))
