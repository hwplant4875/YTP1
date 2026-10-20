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
BOOM, BOOM_UP = '/home/user/rs_work/memes/vine_boom.mp3', '/home/user/rs_work/memes/vine_boom_cute.wav'   # cute = x1.9 pitch + echo tail
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
    clip(DISMOUNT, **ROLLK, **{"in": 4.8, "out": 6.55,                      # cut as his back hits the floor
         "sfx": [{"at": 5.62, "src": '/mnt/project-files/sfx/drive/002_휙(만화적).mp3', "ss": 0.25, "vol": 0.7},
                 {"at": 6.42, "src": BOOM, "vol": 0.6}]}),
    meme(SHOCKED, "Bro did a combat roll 💀", boomVol=0),
    replay(DISMOUNT, **ROLLK, **{"in": 5.6, "out": 8.8, "speed": [[5.6, 1.0], [5.8, 0.45], [6.9, 1.0]],
           "hits": [{"at": 5.8, "x": 0.4, "y": 0.45, "zoom": 1.2},
                    {"at": 7.6, "x": 0.55, "y": 0.45, "zoom": 1.1, "dur": 0.6}],
           "sfx": [{"at": 6.4, "src": BOOM, "vol": 0.6, "rate": 0.6}]})]          # stretched boom on the landing

# kid lying on a treadmill is shot off, his friend walks on and goes down the same way; no meme, two booms
KIDS = FL + "7531164171916856606.mp4"
TREAD_KIDS = [
    clip(KIDS, vol=0, **{"in": 0.3, "out": 5.9, "track": [[0.3, 0.5, 0.42, 1.15]],
         "blur": [{"box": [0.2, 0.665, 0.6, 0.115]}],             # burned-in "Wait for it" 
         "hits": [{"at": 3.55, "x": 0.45, "y": 0.5, "zoom": 1.3}],
         "sfx": [{"at": 1.15, "src": BOOM, "vol": 0.6}, {"at": 3.6, "src": BOOM_UP, "vol": 0.55}]})]

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
    clip(BAND, vol=0.8, **{"in": 2.6, "out": 5.0}),                         # real sound (user)
    meme(FAV, "Did he fly?? 😭"),
    replay(BAND, vol=0.8, **{"in": 3.6, "out": 5.9, "speed": [[3.6, 1.0], [3.85, 0.4], [4.7, 1.0]],
           "hits": [{"at": 3.85, "x": 0.3, "y": 0.35, "zoom": 1.2}],
           "sfx": [{"at": 3.78, "src": LIB + "tape_stop.mp3", "vol": 0.5},       # time slowing down, not a whoosh (user)
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

# "today he didn't even touch the bar when I needed it": the spotter watches, the plates crash off one side
NOTOUCH = '/home/user/rs_work/src/hd_bank/c/7066597956744482095.mp4'
SPOTTER_NOTOUCH = [
    clip(NOTOUCH, vol=0, **{"in": 13.5, "out": 16.6,
         "sfx": [{"at": 15.85, "src": LIB + "impact_metal.mp3", "vol": 0.8}]}),
    clip(NOTOUCH, **{"in": 15.0, "out": 16.6, "reverse": 3.0}),
    replay(NOTOUCH, vol=0, **{"in": 15.0, "out": 17.2, "speed": [[15.0, 1.0], [15.15, 0.4], [16.4, 1.0]],
           "track": [[0, 0.55, 0.72, 1.3]],              # framed below the burned-in caption from the first frame
           "hits": [{"at": 15.15, "x": 0.55, "y": 0.72, "zoom": 1.08}],
           "sfx": [{"at": 15.85, "src": LIB + "impact_metal.mp3", "vol": 0.8, "rate": 0.7}]})]

# "can you spot me bro": the spotter hugs in behind the squat, then rides him piggyback
PIGGY = '/home/user/rs_work/src/hd_bank/c/7445003726793772331.mp4'
SPOTTER_PIGGY = [
    clip(PIGGY, vol=0, **{"in": 4.0, "out": 8.4, "speed": [[4.0, 1.0], [4.5, 1.6], [6.9, 1.0]]}),
    meme(M + 'cat-side-eye__LoTSdDHzoc0__cat-annoyed.mp4', hold=0.55),
    replay(PIGGY, vol=0, **{"in": 6.9, "out": 8.9, "speed": [[6.9, 1.0], [7.15, 0.45], [8.3, 1.0]],
           "hits": [{"at": 7.15, "x": 0.6, "y": 0.42, "zoom": 1.2}]})]

# bails a squat, the bar rolls straight over his phone, RIP iPhone
ROLLBAR = '/home/user/rs_work/src/hd_bank/c/7294317549473238314.mp4'
BAR_PHONE = [
    clip(ROLLBAR, vol=0, **{"in": 4.3, "out": 7.3,
         "sfx": [{"at": 5.05, "src": LIB + "thud_heavy.mp3", "vol": 0.8}]}),
    clip(ROLLBAR, **{"in": 5.2, "out": 7.3, "reverse": 4.0}),
    replay(ROLLBAR, vol=0, **{"in": 5.2, "out": 7.3, "speed": [[5.2, 1.0], [6.4, 0.45]],
           "hits": [{"at": 6.4, "x": 0.5, "y": 0.6, "zoom": 1.2}]}),
    clip(ROLLBAR, vol=0, **{"in": 10.7, "out": 12.5,
         "sfx": [{"at": 10.72, "src": '/mnt/project-files/sfx/drive/018_접시깨지는소리.mp3', "vol": 0.8}]}),
    # the broken iPhone rises up the stairs into heaven (heaven/heaven.py, user's heaven image), no cat
    meme('/home/user/rs_work/memes/heaven_iphone.mp4', dur=2.8, boomVol=0,
         sfx=[{"at": 0.0, "src": LIB + "heaven_choir.mp3", "vol": 0.32}])]

CLIPS_BOTH = [
    clip(R + "1ng2nwz.mp4", **{"in": 0.0, "out": 2.6,
         "circles": [{"from": 0.0, "to": 0.7, "rx": 0.16, "ry": 0.1, "track": [[0.0, 0.24, 0.3]]}]}),
    meme(CONFUSED, "Bro forgot the clips 😭"),
    replay(R + "1ng2nwz.mp4", **{"in": 1.2, "out": 3.25, "speed": [[1.2, 1.0], [1.5, 0.45], [2.4, 1.0]],
           "hits": [{"at": 1.5, "x": 0.4, "y": 0.35, "zoom": 1.2}],
           "sfx": [{"at": 1.85, "src": SFX + "lego-breaking.mp3", "ss": 0.08, "vol": 0.9}]})]

# kicks the dumbbells up to lie back and the momentum flips him backwards off the bench
FLIP = '/home/user/rs_work/src/hd_bank/c/7639254568102202637.mp4'
FLIPK = {"track": [[0, 0.52, 0.5, 1.2]], "vol": 0}   # keeps the burned-in caption whole
BENCH_FLIP = [
    clip(FLIP, **FLIPK, **{"in": 5.5, "out": 8.4}),
    meme(M + 'shocked-cat__btYkcmAPyCc__cat-flabbergasted.mp4', hold=0.75),
    replay(FLIP, **FLIPK, **{"in": 6.6, "out": 9.2, "speed": [[6.6, 1.0], [6.8, 0.4], [8.1, 1.0]],
           "hits": [{"at": 6.8, "x": 0.52, "y": 0.5, "zoom": 1.1}],
           "sfx": [{"at": 7.9, "src": LIB + "thud_heavy.mp3", "vol": 0.8}]})]

# push-ups on a "bar" that turns out to be soda cans; rewind, slow-mo, land on her jaw-drop
CANS = '/home/user/rs_work/src/hd_bank/c/7371135870272884011.mp4'
CAN_BAR = [
    clip(CANS, vol=1.0, **{"in": 3.0, "out": 5.6}),
    clip(CANS, **{"in": 4.4, "out": 5.6, "reverse": 3.0}),
    replay(CANS, vol=1.0, **{"in": 4.4, "out": 6.9, "speed": [[4.4, 1.0], [4.7, 0.45], [5.6, 1.0]],
           "hits": [{"at": 4.7, "x": 0.5, "y": 0.5, "zoom": 1.15},
                    {"at": 6.0, "x": 0.62, "y": 0.45, "zoom": 1.45, "dur": 0.6}],
           "sfx": [{"at": 6.05, "src": BOOM, "vol": 0.6}]})]

# box-jump compilation (@fitnesswithkien 7424792145137077537): its audio is music with bass drops, so muted
BOXJ = '/home/user/rs_work/src/hd_bank/d/7424792145137077537.mp4'
# red shirt lands the box jump, the box tips back under him and he slams flat with his legs in the air
BOX_TIP = [
    clip(BOXJ, vol=0, **{"in": 20.05, "out": 21.75,
         "sfx": [{"at": 21.6, "src": LIB + "thud_heavy.mp3", "vol": 0.8}]}),
    clip(BOXJ, **{"in": 20.9, "out": 21.75, "reverse": 3.0}),
    replay(BOXJ, vol=0, **{"in": 20.9, "out": 22.35, "speed": [[20.9, 1.0], [21.05, 0.45], [21.9, 1.0]],
           "hits": [{"at": 21.05, "x": 0.52, "y": 0.6, "zoom": 1.2}],
           "sfx": [{"at": 21.0, "src": LIB + "tape_stop.mp3", "vol": 0.5},
                   {"at": 21.6, "src": LIB + "thud_heavy.mp3", "vol": 0.8, "rate": 0.75}]})]

# all black: the box tips as he lands and he goes over backwards onto his shoulders
BOX_ROLL = [
    clip(BOXJ, vol=0, **{"in": 36.1, "out": 37.95,
         "sfx": [{"at": 37.15, "src": LIB + "impact_metal.mp3", "vol": 0.5},
                 {"at": 37.8, "src": LIB + "thud_heavy.mp3", "vol": 0.8}]}),
    meme(NICK, ss=2.6),
    replay(BOXJ, vol=0, **{"in": 36.85, "out": 38.42, "speed": [[36.85, 1.0], [37.05, 0.45], [38.05, 1.0]],
           "hits": [{"at": 37.05, "x": 0.5, "y": 0.55, "zoom": 1.2}],
           "sfx": [{"at": 37.8, "src": LIB + "thud_heavy.mp3", "vol": 0.8, "rate": 0.75}]})]

SHORTS = [
    short("41_treadmill_v3", "Treadmills Are Undefeated 😭", 40.0, TREAD_ROLL, TREAD_KIDS),   # launch clip cut (user)
    short("43_not_ready_v3", "Bro Was NOT Ready 😭", 12.0, BAND_SPRINT, BOX_SQUAT),
    short("45_humbled_v3", "Gym Bros Got HUMBLED 💀", 60.0, BENCH_FLIP, BOX_TIP, BOX_ROLL),   # can bar cut (user)
    short("44_iphone_v3", "His Phone Never Stood a Chance 💀", 26.0, BAR_PHONE),
]

if __name__ == '__main__':
    for name, spec in SHORTS:
        json.dump(spec, open(os.path.join(HERE, name + '.json'), 'w'), indent=1, ensure_ascii=False)
    print(' '.join(n for n, _ in SHORTS))
