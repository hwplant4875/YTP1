"""Gym Funny Moments v2 (user feedback 2026-10-20 22:38 KST on 36-40): red rings only where the cause is easy
to miss, memes are any fitting meme (not cats only) and only where they add a laugh, caption-less memes where
words would be flat, meme captions at the centre of the screen (clear of the Shorts UI), replays get a light
"edit look" (slight zoom, brightness, contrast, saturation), and some beats skip the meme for a plain rewind."""
import json, os

R, FL = '/home/user/rs_work/src/reddit/', '/home/user/rs_work/src/fails/'
A, B = '/home/user/rs_work/src/hd_bank/a/', '/home/user/rs_work/src/hd_bank/b/'
M, G = '/home/user/rs_work/memes/t/', '/home/user/rs_work/memes/g/'
FAV = '/home/user/rs_work/memes/fav_cat.png'
SFX, LIB = '/mnt/project-files/sfx/meme/', '/home/user/rs_work/sfx/'
BOOM, BOOM_UP = '/home/user/rs_work/memes/vine_boom.mp3', '/home/user/rs_work/memes/vine_boom_up.wav'
BGM = '/mnt/project-files/sfx/music/user_bgm_QKThr.mp3'
HERE = os.path.dirname(os.path.abspath(__file__))

CONFUSED = M + 'confused-cat__cuW62FiZhBw__cat-stare-blinking-loop-lopped.mp4'
SHOCKED = M + 'shocked-cat__keHPVm2ArXc__stellarnushu.mp4'
NICK = G + 'q_nick-young.mp4'                     # "???" meme, question marks start popping at ~2 s
EDIT = {"b": 0.04, "c": 1.12, "s": 1.2}          # replay grade


def meme(src, cap=None, **kw):
    return dict({"type": "meme", "src": src, "dur": 0.75, "cap": cap}, **kw)


def short(name, title, bgm_ss, *beats, bgm_vol=0.6):
    return name, {
        "font": "/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF",
        "boom": BOOM,
        "memeBg": "black", "capSize": 84, "capY": 960,
        "title": {"text": title, "y": 190, "size": 60},
        "bgm": {"src": BGM, "ss": bgm_ss, "vol": bgm_vol},
        "segments": [s for b in beats for s in b]}


def clip(src, **kw):
    return dict({"type": "clip", "src": src, "ratio": "9:16", "track": [[0, 0.5, 0.5, 1.0]]}, **kw)


def replay(src, **kw):
    return clip(src, grade=EDIT, **kw)


# --- treadmill beats -----------------------------------------------------------------------------------------
DISMOUNT = B + "7488460918595144990.mp4"
ROLLK = {"crop": [0, 528, 1080, 1392], "ratio": "3:4", "vol": 0}   # crop drops the burned-in caption
TREAD_ROLL = [
    clip(DISMOUNT, **ROLLK, **{"in": 4.8, "out": 7.1}),
    meme(SHOCKED, "Bro did a combat roll 💀"),
    replay(DISMOUNT, **ROLLK, **{"in": 5.6, "out": 8.8, "speed": [[5.6, 1.0], [5.8, 0.45], [6.9, 1.0]],
           "hits": [{"at": 5.8, "x": 0.4, "y": 0.45, "zoom": 1.2},
                    {"at": 7.6, "x": 0.55, "y": 0.45, "zoom": 1.1, "dur": 0.6}],
           "sfx": [{"at": 6.3, "src": LIB + "thud_heavy.mp3", "vol": 0.8}]})]

# kid lying on a treadmill is shot off, his friend walks on and goes down the same way; no meme, two booms
KIDS = FL + "7531164171916856606.mp4"
TREAD_KIDS = [
    clip(KIDS, vol=0, **{"in": 0.3, "out": 5.9, "track": [[0.3, 0.5, 0.42, 1.15]],
         "hits": [{"at": 3.55, "x": 0.45, "y": 0.5, "zoom": 1.3}],
         "sfx": [{"at": 1.15, "src": BOOM, "vol": 0.6}, {"at": 3.6, "src": BOOM_UP, "vol": 0.6}]})]

TREAD = B + "7442160036173860127.mp4"
TREAD_LAUNCH = [
    clip(TREAD, vol=0, **{"in": 12.0, "out": 14.3}),
    meme(FAV),
    replay(TREAD, vol=0, **{"in": 13.0, "out": 15.5, "speed": [[13.0, 1.0], [13.2, 0.4], [14.1, 1.0]],
           "hits": [{"at": 13.2, "x": 0.55, "y": 0.5, "zoom": 1.25},
                    {"at": 14.1, "x": 0.5, "y": 0.6, "zoom": 1.15, "dur": 0.6}],
           "sfx": [{"at": 13.35, "src": LIB + "whoosh_fast.mp3", "vol": 0.7},
                   {"at": 13.85, "src": LIB + "thud_heavy.mp3", "vol": 0.9}]})]

# --- spotter -------------------------------------------------------------------------------------------------
SPOT = R + "1rbl5dp.mp4"
SPOTTER_PLATE = [
    clip(SPOT, **{"in": 15.9, "out": 18.9,
         "circles": [{"from": 15.9, "to": 16.9, "rx": 0.075, "ry": 0.15,
                      "track": [[15.9, 0.245, 0.655], [16.5, 0.24, 0.66], [16.9, 0.239, 0.664]]}],
         "sfx": [{"at": 17.65, "src": SFX + "bowling-pins-falling.mp3", "ss": 0.92, "vol": 0.9}]}),
    meme(NICK, ss=2.6),
    replay(SPOT, **{"in": 16.9, "out": 20.2, "speed": [[16.9, 1.0], [17.3, 0.5], [17.8, 1.0]],
           "hits": [{"at": 16.95, "x": 0.32, "y": 0.62, "zoom": 1.35},
                    {"at": 17.8, "x": 0.45, "y": 0.56, "zoom": 1.25, "dur": 0.6}]})]

# --- not ready -----------------------------------------------------------------------------------------------
BAND = B + "7517757207409167671.mp4"
BAND_SPRINT = [
    clip(BAND, vol=0, **{"in": 2.6, "out": 5.0}),
    meme(FAV, "Did he fly?? 😭"),
    replay(BAND, vol=0, **{"in": 3.6, "out": 5.9, "speed": [[3.6, 1.0], [3.85, 0.4], [4.7, 1.0]],
           "hits": [{"at": 3.85, "x": 0.3, "y": 0.35, "zoom": 1.2}],
           "sfx": [{"at": 3.9, "src": LIB + "whoosh_fast.mp3", "vol": 0.44},     # -4 dB (user)
                   {"at": 4.55, "src": LIB + "thud_heavy.mp3", "vol": 0.9}]})]

# box squat: he rolls back over the box, rewind, then the fall again in graded slow-mo with a slowed Lego crash
BOX = A + "7509176901458578718.mp4"
BOXK = {"crop": [0, 300, 720, 980], "ratio": "3:4"}
BOX_SQUAT = [
    clip(BOX, vol=0.8, **BOXK, **{"in": 3.45, "out": 5.5}),
    clip(BOX, **BOXK, **{"in": 3.8, "out": 5.5, "reverse": 3.0}),
    replay(BOX, vol=0.8, **BOXK, **{"in": 3.8, "out": 7.0, "speed": [[3.8, 1.0], [4.0, 0.4], [5.2, 1.0]],
           "hits": [{"at": 4.0, "x": 0.5, "y": 0.5, "zoom": 1.2},
                    {"at": 6.3, "x": 0.5, "y": 0.45, "zoom": 1.1, "dur": 0.6}],
           "sfx": [{"at": 4.6, "src": SFX + "lego-breaking.mp3", "ss": 0.08, "vol": 1.0, "rate": 0.6}]})]

SHORTS = [
    short("41_treadmill_v2", "Treadmills Are Undefeated 😭", 40.0, TREAD_ROLL, TREAD_KIDS, TREAD_LAUNCH),
    short("43_not_ready_v2", "Bro Was NOT Ready 😭", 12.0, BAND_SPRINT, BOX_SQUAT),
]

if __name__ == '__main__':
    for name, spec in SHORTS:
        json.dump(spec, open(os.path.join(HERE, name + '.json'), 'w'), indent=1, ensure_ascii=False)
    print(' '.join(n for n, _ in SHORTS))
