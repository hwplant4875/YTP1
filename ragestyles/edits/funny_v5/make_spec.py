"""Gym Funny Moments v5 (owner 2026-10-21 17:05 KST): funny gym is the direction. Original clip sound only: no
added SFX (no tape stop, thud, metal clank, Vine Boom) and no background music (the last bed drew a copyright
claim). Clips without sound stay silent (the owner adds his own). Edit = the benchmarked white-flash transitions
on every cut, rewind, slow-mo, fast-forward, brightness grade and zoom-ins. Memes stay, but no cats: well-known
reaction memes (Tenor clips, silent).

Remakes 43 (band sprint + box squat), 46 (gravity) and 47 (not ready) with the same beats as v3/v4.
"""
import json, os

A, B, D = '/home/user/rs_work/src/hd_bank/a/', '/home/user/rs_work/src/hd_bank/b/', '/home/user/rs_work/src/hd_bank/d/'
R = '/home/user/rs_work/memes/r/'
HERE = os.path.dirname(os.path.abspath(__file__))

EDIT = {"b": 0.04, "c": 1.12, "s": 1.2}          # replay grade
LOOK = {"contrast": 1.12, "sat": 1.15, "black": 10, "glow": 0.15, "sharpen": 0.6, "vignette": "PI/5"}

SHOCKED = R + 'black-guy-shocked.mp4'            # hands on head, first 1.5 s
KEVIN = R + 'kevin-hart-shocked.mp4'             # eyes widen from ~1 s
LIOTTA = R + 'guy-laughing-hysterically.mp4'     # Goodfellas laugh
JORDAN = R + 'michael-jordan-laughing.mp4'       # laughing at the tablet from ~1.4 s
MONKEY = R + 'monkey-side-eye.mp4'               # puppet side-eye


def meme(src, cap=None, **kw):
    return dict({"type": "meme", "src": src, "dur": 0.9, "cap": cap}, **kw)


def short(name, title, *beats):
    return name, {
        "font": "/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF",
        "flashAll": True,
        "memeBg": "black", "capSize": 84, "capY": 960,
        "title": {"text": title, "y": 190, "size": 60},
        "look": LOOK,
        "segments": [s for b in beats for s in b]}


def clip(src, **kw):
    return dict({"type": "clip", "src": src, "ratio": "9:16", "track": [[0, 0.5, 0.5, 1.0]]}, **kw)


def replay(src, **kw):
    return clip(src, grade=EDIT, **kw)


# --- 43 not ready ----------------------------------------------------------------------------------------------
# band sprint: the partner holding the band yanks him into a backflip (real sound)
BAND = B + '7517757207409167671.mp4'
BAND_SPRINT = [
    clip(BAND, vol=0.8, **{"in": 2.6, "out": 5.0}),
    meme(SHOCKED, "Did he fly?? 😭"),
    clip(BAND, **{"in": 3.6, "out": 5.0, "reverse": 3.0}),
    replay(BAND, vol=0.8, **{"in": 3.6, "out": 5.9, "speed": [[3.6, 1.0], [3.85, 0.4], [4.7, 1.0]],
           "hits": [{"at": 3.85, "x": 0.3, "y": 0.35, "zoom": 1.2}]})]

# box squat: he rolls back over the box (real sound)
BOX = A + '7509176901458578718.mp4'
BOXK = {"crop": [0, 300, 720, 980], "ratio": "3:4"}
BOX_SQUAT = [
    clip(BOX, vol=0.8, **BOXK, **{"in": 3.45, "out": 5.5}),
    meme(JORDAN, ss=1.4, dur=1.0),
    clip(BOX, **BOXK, **{"in": 3.8, "out": 5.5, "reverse": 3.0}),
    replay(BOX, vol=0.8, **BOXK, **{"in": 3.8, "out": 7.0, "speed": [[3.8, 1.0], [4.0, 0.4], [5.2, 1.0]],
           "hits": [{"at": 4.0, "x": 0.5, "y": 0.5, "zoom": 1.2},
                    {"at": 6.3, "x": 0.5, "y": 0.45, "zoom": 1.1, "dur": 0.6}]})]

# --- 46 gravity ------------------------------------------------------------------------------------------------
# chest-supported row: the incline pad folds flat and he face-plants over the bench. No audio track: silent.
FOLD = D + '7504420640007392543.mp4'
FOLDK = {"vol": 0, "track": [[0, 0.5, 0.5, 1.06]]}
BENCH_FOLD = [
    clip(FOLD, **FOLDK, **{"in": 0.9, "out": 1.97,
         "hits": [{"at": 1.45, "x": 0.5, "y": 0.55, "zoom": 1.15}]}),
    meme(KEVIN, ss=1.0),
    clip(FOLD, **FOLDK, **{"in": 1.3, "out": 1.97, "reverse": 2.5}),
    replay(FOLD, **FOLDK, **{"in": 1.3, "out": 2.28, "speed": [[1.3, 1.0], [1.4, 0.4]],
           "hits": [{"at": 1.4, "x": 0.5, "y": 0.56, "zoom": 1.15}]})]

# partner wall balls: his throw drops onto her face and she goes over backwards (real sound, quiet source)
WALL = B + '7430827209637580063.mp4'
WALL_FACE = [
    clip(WALL, vol=3.0, **{"in": 18.95, "out": 20.44,
         "track": [[18.95, 0.5, 0.45, 1.0], [19.9, 0.66, 0.4, 1.2]],
         "hits": [{"at": 20.05, "x": 0.86, "y": 0.36, "zoom": 1.3}]}),
    meme(LIOTTA, "Caught it with her FACE 💀"),
    clip(WALL, **{"in": 19.4, "out": 20.44, "reverse": 3.0, "track": [[0, 0.8, 0.38, 1.6]]}),
    replay(WALL, vol=3.0, **{"in": 19.4, "out": 22.35, "speed": [[19.4, 1.0], [20.15, 0.35], [20.75, 1.0]],
           "track": [[0, 0.8, 0.38, 1.6]],
           "hits": [{"at": 20.15, "x": 0.86, "y": 0.36, "zoom": 1.2},
                    {"at": 20.9, "x": 0.72, "y": 0.42, "zoom": 0.8, "dur": 0.6}]})]

# --- 47 not ready ----------------------------------------------------------------------------------------------
# straight-arm pulldown: the attachment lets go and he sinks onto his knees. Its sound is a music bed: muted.
CABLE = B + '7503648632537632031.mp4'
CABK = {"vol": 0, "crop": [0, 630, 1080, 1290]}
CABLE_KNEES = [
    clip(CABLE, **CABK, **{"in": 3.75, "out": 6.27}),
    meme(JORDAN, ss=1.4, dur=1.0),
    clip(CABLE, **CABK, **{"in": 3.95, "out": 6.27, "reverse": 4.0}),
    replay(CABLE, **CABK, **{"in": 3.95, "out": 6.9, "speed": [[3.95, 1.0], [4.05, 0.4], [4.7, 1.6], [6.1, 1.0]],
           "hits": [{"at": 4.05, "x": 0.45, "y": 0.52, "zoom": 1.12},
                    {"at": 6.15, "x": 0.42, "y": 0.56, "zoom": 1.2, "dur": 0.6}]})]

# mid-set evil laugh, the spotter flinches (real audio; the laugh carries on under the meme, its own sound)
LAUGH = A + '7593692849833594134.mp4'
LAUGHK = {"crop": [0, 0, 1080, 850], "ratio": "1:1", "track": [[0, 0.5, 0.5, 1.0]]}
EVIL_LAUGH = [
    clip(LAUGH, vol=1.0, **LAUGHK, **{"in": 5.4, "out": 7.35}),
    meme(MONKEY, dur=1.0, sfx=[{"at": 0.0, "src": LAUGH, "ss": 7.35, "dur": 1.0, "vol": 1.0}]),
    clip(LAUGH, **LAUGHK, **{"in": 6.5, "out": 7.35, "reverse": 3.0}),
    replay(LAUGH, vol=1.0, **LAUGHK, **{"in": 6.5, "out": 9.2, "speed": [[6.5, 1.0], [6.75, 0.45], [7.3, 1.0]],
           "hits": [{"at": 6.75, "x": 0.5, "y": 0.45, "zoom": 1.15},
                    {"at": 7.7, "x": 0.55, "y": 0.5, "zoom": 1.05, "dur": 0.6}]})]

SHORTS = [
    short("43_not_ready_v4", "Bro Was NOT Ready 😭", BAND_SPRINT, BOX_SQUAT),
    short("46_gravity_v2", "Gravity always wins 💀", BENCH_FOLD, WALL_FACE),
    short("47_not_ready_v2", "Nobody was ready 😭", CABLE_KNEES, EVIL_LAUGH),
]

if __name__ == '__main__':
    for name, spec in SHORTS:
        json.dump(spec, open(os.path.join(HERE, name + '.json'), 'w'), indent=1, ensure_ascii=False)
    print(' '.join(n for n, _ in SHORTS))
