"""Single-clip short in the POSTERlSED style (user 2026-10-20): one clip, red ring on the subject, meme cut, rewind with
slow-mo on the key move, outro meme. Source: the outdoor push-up girl from the 59M ranking short (TikTok original
7587782945499303190, found by the user)."""
import json

M = '/home/user/rs_work/memes/t/'
SFX = '/mnt/project-files/sfx/meme/'
SRC = '/home/user/rs_work/src/orig/tt_7587782945499303190.mp4'
clip = {"type": "clip", "src": SRC, "crop": [0, 174, 576, 674], "ratio": "4:5", "track": [[0, 0.55, 0.6, 1.0]]}

spec = {
    "font": "/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF",
    "boom": "/home/user/rs_work/memes/vine_boom.mp3",
    "memeBg": "black",
    "capSize": 80,
    "title": {"text": "She Really Thought She Had It 😭💀", "y": 190, "size": 60},
    "segments": [
        # push-ups sped up, kick-up, over-rotates and lands sitting
        dict(clip, **{"in": 10.9, "out": 13.25, "speed": [[10.9, 1.6], [11.6, 1.0]],
                      "circles": [{"from": 10.9, "to": 11.55, "rx": 0.2, "ry": 0.13,
                                   "track": [[10.9, 0.6, 0.76], [11.5, 0.6, 0.74]]}],
                      "sfx": [{"at": 11.65, "src": SFX + "i-got-this-clear.mp3", "ss": 0.12, "vol": 1.0}]}),
        {"type": "meme", "src": M + "shocked-cat__btYkcmAPyCc__cat-flabbergasted.mp4", "dur": 0.75, "hold": 0.75,
         "cap": "Is she okay???"},
        # rewind: the overbalance and fall in slow motion, then her laughing it off
        dict(clip, **{"in": 12.2, "out": 15.3, "speed": [[12.2, 1.0], [12.6, 0.45], [13.3, 1.0]],
                      "hits": [{"at": 12.6, "x": 0.6, "y": 0.6, "zoom": 1.2, "dur": 0.6}]}),
        {"type": "meme", "src": M + "cat-laughing__aGdYBX9_DTg__cat-laugh-cat-laughing.mp4", "dur": 1.3,
         "cap": "At least she's laughing 😭", "boomVol": 0.0,
         "sfx": [{"at": 0.0, "src": SFX + "cat-laugh-meme-1.mp3", "ss": 0.28, "vol": 0.45}]},
    ],
}
json.dump(spec, open(__file__.replace('make_spec.py', 'spec.json'), 'w'), indent=1, ensure_ascii=False)
