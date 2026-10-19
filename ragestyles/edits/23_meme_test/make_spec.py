"""Meme-reaction format test v2: full 9:16 with blurred fill, person-focused crops, memes pop with Vine Boom."""
import glob, json
R = '/home/user/rs_work/src/reddit/'
M = lambda k: glob.glob(f'/home/user/rs_work/memes/t/*__{k}__*.mp4')[0]
SFX = '/mnt/project-files/sfx/drive/'
spec = {
    "font": "/home/user/rs_work/gfonts/Kanit-BlackItalic.ttf",
    "boom": "/home/user/rs_work/memes/vine_boom.mp3", "pop": SFX + "001_뽁.wav", "whoosh": SFX + "002_휙(만화적).mp3",
    "memeAlpha": 0.5, "memeW": 620,
    "clips": [
        # plates slide off one side, bar flips, he lands on his butt (vertical source -> full 9:16)
        {"src": R + "1ng2nwz.mp4", "in": 0.0, "out": 3.25, "ratio": "9:16",
         "track": [[0, 0.55, 0.5, 1.0]],
         "memes": [{"at": 1.75, "src": M("btYkcmAPyCc")}, {"at": 2.6, "src": M("LY5ag-cIdn8"), "dur": 0.65}],
         "replay": {"in": 1.5, "out": 2.9, "speed": 0.4}, "score": [["IMPACT", 7], ["FUNNY", 8]]},
        # push-ups on dumbbells, face-plant (square source -> 1:1 window + blurred fill)
        {"src": R + "1mi1aq3.mp4", "in": 1.7, "out": 5.15, "ratio": "1:1",
         "memes": [{"at": 3.6, "src": M("b8jzGatOpv8")}, {"at": 4.5, "src": M("aGdYBX9_DTg"), "dur": 0.65}],
         "replay": {"in": 3.2, "out": 4.4, "speed": 0.4}, "score": [["IMPACT", 9], ["FUNNY", 9]]},
        # lying on the treadmill with a band, gets yanked up and flung toward the camera, then plays it off
        # (she is only visible in the wall mirror until she flies in, so the crop follows her reflection)
        {"src": R + "1pnl9yk.mp4", "in": 2.2, "out": 7.4, "ratio": "9:16",
         "track": [[2.2, 0.6, 0.66, 2.2], [3.3, 0.58, 0.66, 2.2], [3.6, 0.44, 0.62, 2.2], [4.2, 0.34, 0.6, 2.2],
                   [4.45, 0.4, 0.55, 1.4], [4.7, 0.5, 0.5, 1.0]],
         "memes": [{"at": 3.55, "src": M("aLoZNO7gRQo")}, {"at": 6.2, "src": M("pNFqGBftNHE"), "dur": 0.9}],
         "replay": {"in": 3.3, "out": 4.8, "speed": 0.45}, "score": [["IMPACT", 6], ["FUNNY", 10]]},
    ],
}
json.dump(spec, open('spec.json', 'w'), indent=1, ensure_ascii=False)
