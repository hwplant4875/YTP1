"""Rewind-reaction test: blonde box jump fail (proven: #1 in the 59M ranking short), three beats."""
import json
F = '/home/user/rs_work/src/fails/7424792145137077537.mp4'   # fitnesswithkien compilation, clip at 11.5-17.4
M = '/home/user/rs_work/memes/t/'
CROP = [0, 96, 1080, 1724]
BASE = [[0, 0.55, 0.5, 1.0]]
spec = {
    "font": "/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF",
    "boom": "/home/user/rs_work/memes/vine_boom.mp3",
    "segments": [
        # jumps, catches the edge, slides off and plops onto the floor
        {"type": "clip", "src": F, "in": 11.5, "out": 14.0, "crop": CROP, "track": BASE,
         "hits": [{"at": 13.62, "x": 0.5, "y": 0.47, "zoom": 1.3}]},
        {"type": "meme", "src": M + "surprised-cat__aLoZNO7gRQo__shocked-cat-shocked.mp4", "dur": 0.8, "cap": "She good???"},
        # rewind 1 s: sits there, then tips over backwards
        {"type": "clip", "src": F, "in": 12.9, "out": 17.0, "crop": CROP, "track": BASE,
         "hits": [{"at": 16.0, "x": 0.45, "y": 0.6, "zoom": 1.25}]},
        {"type": "meme", "src": M + "question-mark-meme__pNFqGBftNHE__nick-confused.mp4", "dur": 0.8, "cap": "Why is she rolling???"},
        # rewind: the tip-over again, closer
        {"type": "clip", "src": F, "in": 15.4, "out": 16.7, "crop": CROP, "track": BASE,
         "hits": [{"at": 16.0, "x": 0.45, "y": 0.58, "zoom": 1.45}]},
        {"type": "meme", "src": M + "cat-laughing__aGdYBX9_DTg__cat-laugh-cat-laughing.mp4", "dur": 1.2, "cap": "The box won"},
    ],
}
json.dump(spec, open(__file__.replace('make_spec.py', 'spec.json'), 'w'), indent=1, ensure_ascii=False)
