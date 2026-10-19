"""Rewind-reaction test with new HD picks: one cat meme per clip, rewind ~1 s with an ease-out zoom-in, hard cuts."""
import json
R, F = '/home/user/rs_work/src/reddit/', '/home/user/rs_work/src/fails/'
M = '/home/user/rs_work/memes/t/'


def beat(src, src_in, cut, replay_out, focus, hit, zoom, meme, cap, crop=None, ratio="9:16"):
    base = [[0, focus[0], focus[1], 1.0]]
    clip = {"type": "clip", "src": src, "ratio": ratio, "track": base}
    if crop:
        clip["crop"] = crop
    return [
        dict(clip, **{"in": src_in, "out": cut}),
        {"type": "meme", "src": M + meme, "dur": 0.75, "cap": cap},
        dict(clip, **{"in": cut - 1.0, "out": replay_out,
                      "hits": [{"at": hit, "x": focus[2], "y": focus[3], "zoom": zoom}]}),
    ]


spec = {
    "font": "/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF",
    "boom": "/home/user/rs_work/memes/vine_boom.mp3",
    "segments":
        # r/GymFails "the spotter is fired": bar tips off one side, plates crash, spotter just watches
        beat(R + "1rbl5dp.mp4", 15.9, 18.9, 20.2, [0.5, 0.5, 0.4, 0.55], 18.3, 1.3,
             "surprised-cat__ZuXnTDxIbjQ__shocked-shocked-cat.mp4", "Spotter???")
        # back-extension machine sends him flying over the top
        + beat(R + "1v6asnx.mp4", 32.0, 33.9, 33.95, [0.5, 0.5, 0.55, 0.45], 33.2, 1.3,
               "shocked-cat__keHPVm2ArXc__stellarnushu.mp4", "Bro flipped", crop=[0, 76, 478, 702], ratio="3:4")
        # filming herself, the phone tips over onto her face
        + beat(R + "1njr0k1.mp4", 18.6, 20.5, 21.2, [0.5, 0.5, 0.5, 0.35], 19.9, 1.2,
               "confused-cat__cuW62FiZhBw__cat-stare-blinking-loop-lopped.mp4", "Hello???")
        # 6.2M views: a stretch goes wrong, the trainer collapses laughing
        + beat(F + "7481818733451709738.mp4", 0.5, 3.7, 6.3, [0.5, 0.5, 0.68, 0.58], 4.6, 1.3,
               "cat-side-eye__LoTSdDHzoc0__cat-annoyed.mp4", "Did she just..."),
}
json.dump(spec, open(__file__.replace('make_spec.py', 'spec.json'), 'w'), indent=1, ensure_ascii=False)
