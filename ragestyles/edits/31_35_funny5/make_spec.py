"""Five single-clip Gym Funny Moments shorts (user 2026-10-20 01:36 KST): POSTERlSED-style beat per clip
(red ring on the subject, play to the moment, white flash into a cat meme, rewind with slow-mo + ease-out zoom),
user's music bed under everything (louder on silent sources), original audio kept, no outro meme."""
import json, os

R, F, T = '/home/user/rs_work/src/reddit/', '/home/user/rs_work/src/fails/', '/home/user/rs_work/src/tt2/'
M = '/home/user/rs_work/memes/t/'
SFX = '/mnt/project-files/sfx/meme/'
BGM = '/mnt/project-files/sfx/music/user_bgm_QKThr.mp3'
HERE = os.path.dirname(os.path.abspath(__file__))


def short(name, title, bgm_ss, first, meme, cap, replay, hold=None, bgm_vol=0.35):
    m = {"type": "meme", "src": meme, "dur": 0.75, "cap": cap}
    if hold:
        m["hold"] = hold
    return name, {
        "font": "/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF",
        "boom": "/home/user/rs_work/memes/vine_boom.mp3",
        "memeBg": "black", "capSize": 80,
        "title": {"text": title, "y": 190, "size": 60},
        "bgm": {"src": BGM, "ss": bgm_ss, "vol": bgm_vol},
        "segments": [first, m, replay]}


def clip(src, **kw):
    return dict({"type": "clip", "src": src, "ratio": "9:16", "track": [[0, 0.5, 0.5, 1.0]]}, **kw)


SHORTS = [
    # spotter clips the upright plate beside the bench, the bar goes down
    short("31_spotter_plate", "The Spotter Had ONE Job 😭💀", 1.0,
          clip(R + "1rbl5dp.mp4", **{"in": 15.9, "out": 18.9}),
          "/home/user/rs_work/memes/fav_cat.png", "Why was it standing??",
          clip(R + "1rbl5dp.mp4", **{"in": 16.9, "out": 20.2, "speed": [[16.9, 1.0], [17.3, 0.5], [17.8, 1.0]],
               "hits": [{"at": 16.95, "x": 0.32, "y": 0.62, "zoom": 1.35},
                        {"at": 17.8, "x": 0.45, "y": 0.56, "zoom": 1.25, "dur": 0.6}],
               "circles": [{"from": 17.0, "to": 17.6, "rx": 0.075, "ry": 0.15,
                            "track": [[16.9, 0.239, 0.664], [17.1, 0.229, 0.664], [17.3, 0.215, 0.672],
                                      [17.45, 0.195, 0.68], [17.6, 0.17, 0.7]]}],
               "sfx": [{"at": 17.45, "src": SFX + "bowling-pins-falling.mp3", "ss": 0.92, "vol": 0.9}]}), bgm_vol=0.6),
    # back-extension machine: he swings all the way over the top
    short("32_back_extension", "Bro Thought It Was A Ride 😭", 14.0,
          clip(R + "1v6asnx.mp4", crop=[0, 76, 478, 702], ratio="3:4", **{"in": 32.0, "out": 33.75,
               "circles": [{"from": 32.0, "to": 32.55, "rx": 0.2, "ry": 0.12, "track": [[32.0, 0.56, 0.21]]}]}),
          M + "shocked-cat__keHPVm2ArXc__stellarnushu.mp4", "What is bro doing???",
          clip(R + "1v6asnx.mp4", crop=[0, 76, 478, 702], ratio="3:4", **{"in": 32.75, "out": 34.1,
               "speed": [[32.75, 1.0], [32.95, 0.4], [33.9, 1.0]],
               "hits": [{"at": 33.0, "x": 0.6, "y": 0.4, "zoom": 1.25}]})),
    # plates slide off the unclipped side, the bar whips up and he lands on the floor
    short("33_clip_both_sides", "Always Clip Both Sides 💀", 26.0,
          clip(R + "1ng2nwz.mp4", **{"in": 0.0, "out": 2.6,
               "circles": [{"from": 0.0, "to": 0.7, "rx": 0.16, "ry": 0.1, "track": [[0.0, 0.24, 0.3]]}]}),
          M + "confused-cat__cuW62FiZhBw__cat-stare-blinking-loop-lopped.mp4", "Bro forgot the clips 😭",
          clip(R + "1ng2nwz.mp4", **{"in": 1.2, "out": 3.25, "speed": [[1.2, 1.0], [1.5, 0.45], [2.4, 1.0]],
               "hits": [{"at": 1.5, "x": 0.4, "y": 0.35, "zoom": 1.2}],
               "sfx": [{"at": 1.85, "src": SFX + "lego-breaking.mp3", "ss": 0.08, "vol": 0.9}]}), bgm_vol=0.6),
    # the machine tips over onto him mid-set
    short("34_machine_topples", "The Machine Said NO 💀", 38.0,
          clip(R + "1un5gsf.mp4", **{"in": 17.5, "out": 20.3,
               "circles": [{"from": 17.5, "to": 18.1, "rx": 0.18, "ry": 0.12, "track": [[17.5, 0.72, 0.78]]}]}),
          M + "shocked-cat__btYkcmAPyCc__cat-flabbergasted.mp4", "Is he okay???",
          clip(R + "1un5gsf.mp4", **{"in": 19.0, "out": 21.8, "speed": [[19.0, 1.0], [19.4, 0.45], [20.2, 1.0]],
               "hits": [{"at": 19.4, "x": 0.55, "y": 0.6, "zoom": 1.25}]}), hold=0.75),
    # resistance band slips off his foot and snaps straight up
    short("35_band_snap", "Never Trust The Band 😭💀", 50.0,
          clip(T + "7282914676806126894.mp4", **{"in": 0.0, "out": 3.3,
               "circles": [{"from": 0.0, "to": 0.7, "rx": 0.16, "ry": 0.3, "track": [[0.0, 0.42, 0.72]]}]}),
          M + "crying-cat__9a9g-pOTZHk__nsb14-meowl.mp4", "Not the band 😭",
          clip(T + "7282914676806126894.mp4", **{"in": 2.2, "out": 4.8,
               "speed": [[2.2, 1.0], [2.45, 0.45], [3.1, 1.0]],
               "hits": [{"at": 2.45, "x": 0.5, "y": 0.55, "zoom": 1.2}]})),
]

for name, spec in SHORTS:
    json.dump(spec, open(os.path.join(HERE, name + '.json'), 'w'), indent=1, ensure_ascii=False)
print(' '.join(n for n, _ in SHORTS))
