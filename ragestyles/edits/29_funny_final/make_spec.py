"""Final cut of test 28 (user notes 2026-10-20): stretch clip moved to the front, spotter clip last with a red ring
on the upright plate the bar knocks over (bowling-pins crash), user's favourite cat on that beat."""
import json

R, F = '/home/user/rs_work/src/reddit/', '/home/user/rs_work/src/fails/'
M = '/home/user/rs_work/memes/t/'
SFX = '/mnt/project-files/sfx/meme/'


def beat(src, src_in, cut, replay_out, focus, hit, zoom, meme, cap, crop=None, ratio="9:16", ss=0.0):
    base = [[0, focus[0], focus[1], 1.0]]
    clip = {"type": "clip", "src": src, "ratio": ratio, "track": base}
    if crop:
        clip["crop"] = crop
    return [dict(clip, **{"in": src_in, "out": cut}),
            {"type": "meme", "src": M + meme, "ss": ss, "dur": 0.75, "cap": cap},
            dict(clip, **{"in": cut - 1.0, "out": replay_out, "hits": [{"at": hit, "x": focus[2], "y": focus[3], "zoom": zoom}]})]


spotter = {"type": "clip", "src": R + "1rbl5dp.mp4", "ratio": "9:16", "track": [[0, 0.5, 0.5, 1.0]]}

spec = {
    "font": "/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF",
    "boom": "/home/user/rs_work/memes/vine_boom.mp3",
    "segments":
        # 6.2M views: a stretch goes wrong, the trainer collapses laughing (meme starts after its internal cut)
        beat(F + "7481818733451709738.mp4", 0.5, 3.7, 6.3, [0.5, 0.5, 0.68, 0.58], 4.6, 1.3,
             "cat-side-eye__LoTSdDHzoc0__cat-annoyed.mp4", "Did she just...", ss=0.7)
        # back-extension machine sends him flying over the top
        + beat(R + "1v6asnx.mp4", 32.0, 33.9, 33.95, [0.5, 0.5, 0.55, 0.45], 33.2, 1.3,
               "shocked-cat__keHPVm2ArXc__stellarnushu.mp4", "What is bro doing???", crop=[0, 76, 478, 702], ratio="3:4")
        # upside-down face in the camera
        + beat(R + "1njr0k1.mp4", 18.6, 20.5, 21.2, [0.5, 0.5, 0.5, 0.35], 19.9, 1.2,
               "confused-cat__cuW62FiZhBw__cat-stare-blinking-loop-lopped.mp4", "Hello???")
        # r/GymFails: the bar clips an upright plate beside the bench and everything goes down
        + [dict(spotter, **{"in": 15.9, "out": 18.9}),
           {"type": "meme", "src": "/home/user/rs_work/memes/fav_cat.png", "dur": 0.75, "cap": "Why was it standing??"},
           dict(spotter, **{"in": 16.9, "out": 20.2,
                            "hits": [{"at": 16.95, "x": 0.32, "y": 0.62, "zoom": 1.35},
                                     {"at": 17.75, "x": 0.45, "y": 0.56, "zoom": 1.25, "dur": 0.6}],
                            "circles": [{"from": 17.0, "to": 17.6, "rx": 0.075, "ry": 0.15,
                                         "track": [[16.9, 0.239, 0.664], [17.1, 0.229, 0.664],
                                                   [17.3, 0.215, 0.672], [17.45, 0.195, 0.68], [17.6, 0.17, 0.7]]}],
                            "sfx": [{"at": 17.45, "src": SFX + "bowling-pins-falling.mp3", "ss": 0.92, "vol": 0.9}]})],
}
json.dump(spec, open(__file__.replace('make_spec.py', 'spec.json'), 'w'), indent=1, ensure_ascii=False)
