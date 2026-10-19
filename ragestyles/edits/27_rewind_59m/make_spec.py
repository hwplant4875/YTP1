"""Rewind-reaction format check on four proven clips from the user's 59M-view short (480p, its ranking text stays).
Each clip: play to the moment, white flash to one meme, flash back rewound ~1 s with a zoom-in on the moment,
hard cut to the next clip."""
import json
R = '/home/user/rs_work/ref/ref59m.mp4'
M = '/home/user/rs_work/memes/t/'
SQ = [0, 213, 335, 427]       # clip 1 sits in a small window with blur around it
FULL = [0, 112, 480, 716]     # below the title bar


def beat(src_in, cut, replay_out, crop, ratio, focus, hit, zoom, meme, cap):
    base = [[0, focus[0], focus[1], 1.0]]
    return [
        {"type": "clip", "src": R, "in": src_in, "out": cut, "crop": crop, "ratio": ratio, "track": base},
        {"type": "meme", "src": M + meme, "dur": 0.75, "cap": cap},
        {"type": "clip", "src": R, "in": cut - 1.0, "out": replay_out, "crop": crop, "ratio": ratio, "track": base,
         "hits": [{"at": hit, "x": focus[2], "y": focus[3], "zoom": zoom}]},
    ]


spec = {
    "font": "/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF",
    "boom": "/home/user/rs_work/memes/vine_boom.mp3",
    "segments":
        # outdoor push-up turns into a flip
        beat(1.2, 2.75, 3.6, SQ, "3:4", [0.55, 0.5, 0.6, 0.62], 2.25, 1.3,
             "question-mark-meme__pNFqGBftNHE__nick-confused.mp4", "Wait what???")
        # he sprints in to "help" her pull-up
        + beat(5.6, 7.3, 8.3, FULL, "9:16", [0.4, 0.5, 0.35, 0.5], 6.85, 1.25,
               "suspicious-cat__hUBXfYvvOlU__sus-suspicious.mp4", "Bro came running")
        # the cable pulls her face into the floor
        + beat(8.5, 9.3, 10.4, FULL, "9:16", [0.45, 0.5, 0.42, 0.5], 8.95, 1.4,
               "shocked-cat__btYkcmAPyCc__cat-flabbergasted.mp4", "She okay???")
        # the guy behind her dives over the bench
        + beat(12.6, 14.4, 14.75, FULL, "9:16", [0.5, 0.5, 0.25, 0.47], 14.0, 1.6,
               "surprised-cat__aLoZNO7gRQo__shocked-cat-shocked.mp4", "Look behind her"),
}
json.dump(spec, open(__file__.replace('make_spec.py', 'spec.json'), 'w'), indent=1, ensure_ascii=False)
