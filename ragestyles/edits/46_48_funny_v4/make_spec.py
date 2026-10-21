"""Gym Funny Moments v4: the approved 43/45 v3 format (play to the moment, reaction meme the instant it lands,
rewind, graded slow-mo replay with a tape stop) plus the new top-level "look" polish grade on every footage
frame, and no background music (the owner adds his own).

Owner scope change: two test shorts only (gravity + one more). Clip review against the brief:
  - b/7430827209637580063 wall ball: the index note is wrong (his ball does not drop on him). The real fail is
    at 20.35 s: his partner throw comes down onto the woman's FACE and she goes over backwards. Kept, that beat.
  - a/7438634264876371231 sandbag throw: the bag hits the wall ledge off to the side; no phone is ever visible,
    so the joke only exists in the caption. Not funny on the footage alone -> skipped.
  - a/7263534152656489761 Tren Twins: the snap itself is never seen (camera falls at once), loud music bed.
    A "whoa" clip, not a funny one -> skipped.
  - b/7503648632537632031 cable: kept. Its bed is music (F/A/C/D notes, whisper hallucinates), so muted + SFX.
  - replacements: d/7504420640007392543 (incline bench back folds, he face-plants over it toward the camera;
    unused, no audio) and the F3 clip a/7593692849833594134 (evil laugh mid-set, spotter flinches; real audio).
"""
import json, os

A, B, D = '/home/user/rs_work/src/hd_bank/a/', '/home/user/rs_work/src/hd_bank/b/', '/home/user/rs_work/src/hd_bank/d/'
M = '/home/user/rs_work/memes/t/'
FAV = '/home/user/rs_work/memes/fav_cat.png'
LIB = '/home/user/rs_work/sfx/'
BOOM = '/home/user/rs_work/memes/vine_boom.mp3'
HERE = os.path.dirname(os.path.abspath(__file__))

TAPE = LIB + 'tape_stop.mp3'          # time slowing down, not a whoosh (user)
THUD = LIB + 'thud_heavy.mp3'
METAL = LIB + 'impact_metal.mp3'
EDIT = {"b": 0.04, "c": 1.12, "s": 1.2}          # replay grade
LOOK = {"contrast": 1.12, "sat": 1.15, "black": 10, "glow": 0.15, "sharpen": 0.6, "vignette": "PI/5"}


def meme(src, cap=None, **kw):
    return dict({"type": "meme", "src": src, "dur": 0.75, "cap": cap}, **kw)


def short(name, title, *beats):
    return name, {
        "font": "/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF",
        "boom": BOOM,
        "memeBg": "black", "capSize": 84, "capY": 960,
        "title": {"text": title, "y": 190, "size": 60},
        "look": LOOK,
        "segments": [s for b in beats for s in b]}


def clip(src, **kw):
    return dict({"type": "clip", "src": src, "ratio": "9:16", "track": [[0, 0.5, 0.5, 1.0]]}, **kw)


def replay(src, **kw):
    return clip(src, grade=EDIT, **kw)


# --- gravity ---------------------------------------------------------------------------------------------------
# chest-supported row on an incline bench: the back pad folds flat under him and he face-plants over the bench
# toward the camera, legs flipping up. No audio track at all, so SFX carry it.
FOLD = D + '7504420640007392543.mp4'
FOLDK = {"vol": 0, "track": [[0, 0.5, 0.5, 1.06]]}   # its "WHEN YOU FIND A NEW FEAR" caption is not hype text and
                                                    # his face dives right through it, so it is left unblurred
BENCH_FOLD = [
    clip(FOLD, **FOLDK, **{"in": 0.9, "out": 1.97,          # face hits the pad at 1.88, 3 frames before the cut (the white flash eats the last 3)
         "hits": [{"at": 1.45, "x": 0.5, "y": 0.55, "zoom": 1.15}],
         "sfx": [{"at": 1.46, "src": METAL, "vol": 0.45}]}),
    meme(FAV),
    clip(FOLD, **FOLDK, **{"in": 1.3, "out": 1.97, "reverse": 2.5}),
    replay(FOLD, **FOLDK, **{"in": 1.3, "out": 2.28, "speed": [[1.3, 1.0], [1.4, 0.4]],   # skit starts at 2.335
           "hits": [{"at": 1.4, "x": 0.5, "y": 0.56, "zoom": 1.15}],
           "sfx": [{"at": 1.36, "src": TAPE, "vol": 0.5},
                   {"at": 1.47, "src": METAL, "vol": 0.4, "rate": 0.7},
                   {"at": 1.9, "src": THUD, "vol": 0.9, "rate": 0.75}]})]

# partner wall balls (@leoniesolia, ESPN): his throw drops straight onto her face and she goes over backwards
WALL = B + '7430827209637580063.mp4'
WALL_FACE = [
    clip(WALL, vol=3.0, **{"in": 18.95, "out": 20.44,                     # face contact 20.35, 3 frames before the cut
         "track": [[18.95, 0.5, 0.45, 1.0], [19.9, 0.66, 0.4, 1.2]],
         "hits": [{"at": 20.05, "x": 0.86, "y": 0.36, "zoom": 1.3}]}),
    meme(M + 'shocked-cat__GINxa2zTfIM__omg.mp4', "Caught it with her FACE 💀"),
    clip(WALL, **{"in": 19.4, "out": 20.44, "reverse": 3.0, "track": [[0, 0.8, 0.38, 1.6]]}),
    replay(WALL, vol=3.0, **{"in": 19.4, "out": 22.35, "speed": [[19.4, 1.0], [20.15, 0.35], [20.75, 1.0]],
           "track": [[0, 0.8, 0.38, 1.6]],
           "hits": [{"at": 20.15, "x": 0.86, "y": 0.36, "zoom": 1.2},
                    {"at": 20.9, "x": 0.72, "y": 0.42, "zoom": 0.8, "dur": 0.6}],
           "sfx": [{"at": 20.1, "src": TAPE, "vol": 0.5},
                   {"at": 20.35, "src": THUD, "vol": 0.9, "rate": 0.7}]})]

# --- not ready -------------------------------------------------------------------------------------------------
# straight-arm pulldown: the attachment lets go, he stumbles back and sinks onto his knees still holding the bar.
# Its sound is a music bed, so muted (user rule); framed below the burned-in "POV: your worst nightmare" box.
CABLE = B + '7503648632537632031.mp4'
CABK = {"vol": 0, "crop": [0, 630, 1080, 1290]}          # crop sits below the caption box, so zooms never show it
CABLE_KNEES = [
    clip(CABLE, **CABK, **{"in": 3.75, "out": 6.27,                         # knees reach the floor at 6.17
         "sfx": [{"at": 4.12, "src": METAL, "vol": 0.5},
                 {"at": 4.5, "src": THUD, "vol": 0.8},             # his stumble step
                 {"at": 6.08, "src": THUD, "vol": 0.9}]}),
    meme(M + 'crying-cat__ufPsZFFomo4__crying-cat-sad-cat.mp4'),
    clip(CABLE, **CABK, **{"in": 3.95, "out": 6.27, "reverse": 4.0}),
    replay(CABLE, **CABK, **{"in": 3.95, "out": 6.9, "speed": [[3.95, 1.0], [4.05, 0.4], [4.7, 1.6], [6.1, 1.0]],
           "hits": [{"at": 4.05, "x": 0.45, "y": 0.52, "zoom": 1.12},
                    {"at": 6.15, "x": 0.42, "y": 0.56, "zoom": 1.2, "dur": 0.6}],
           "sfx": [{"at": 4.0, "src": TAPE, "vol": 0.5},
                   {"at": 4.12, "src": METAL, "vol": 0.45, "rate": 0.7},
                   {"at": 4.5, "src": THUD, "vol": 0.8, "rate": 0.75},
                   {"at": 6.08, "src": THUD, "vol": 0.9}]})]

# mid-set he bursts into an evil laugh, the spotter flinches back. Real audio (the laugh is the joke); the
# laugh keeps playing under the meme. Burned-in setup caption (it gives the joke away) cropped off.
LAUGH = A + '7593692849833594134.mp4'
# 1:1 band of the picture above the caption: the caption is gone without a blur, and the spotter (whose head
# is at the very top of the source) sits clear of the title
LAUGHK = {"crop": [0, 0, 1080, 850], "ratio": "1:1", "track": [[0, 0.5, 0.5, 1.0]]}
EVIL_LAUGH = [
    clip(LAUGH, vol=1.0, **LAUGHK, **{"in": 5.4, "out": 7.35}),
    meme(M + 'suspicious-cat__T_pTpkyBlEY__judging-cat-side-eye.mp4', dur=0.9, boomVol=0.45,
         sfx=[{"at": 0.0, "src": LAUGH, "ss": 7.35, "dur": 0.9, "vol": 1.0}]),
    clip(LAUGH, **LAUGHK, **{"in": 6.5, "out": 7.35, "reverse": 3.0}),
    replay(LAUGH, vol=1.0, **LAUGHK, **{"in": 6.5, "out": 9.2, "speed": [[6.5, 1.0], [6.75, 0.45], [7.3, 1.0]],
           "hits": [{"at": 6.75, "x": 0.5, "y": 0.45, "zoom": 1.15},
                    {"at": 7.7, "x": 0.55, "y": 0.5, "zoom": 1.05, "dur": 0.6}],
           "sfx": [{"at": 6.72, "src": TAPE, "vol": 0.5}]})]

SHORTS = [
    short("46_gravity", "Gravity always wins 💀", BENCH_FOLD, WALL_FACE),
    short("47_not_ready", "Nobody was ready 😭", CABLE_KNEES, EVIL_LAUGH),
]

if __name__ == '__main__':
    for name, spec in SHORTS:
        json.dump(spec, open(os.path.join(HERE, name + '.json'), 'w'), indent=1, ensure_ascii=False)
    print(' '.join(n for n, _ in SHORTS))
