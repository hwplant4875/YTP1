"""Cat-reaction format test: 3 Reddit r/GymFails clips."""
import glob, json
R = '/home/user/rs_work/src/reddit/'
M = lambda k: glob.glob(f'/home/user/rs_work/memes/t/*__{k}__*.mp4')[0]
SFX = '/mnt/project-files/sfx/drive/'
spec = {
    "font": "/home/user/rs_work/gfonts/Kanit-BlackItalic.ttf",
    "pop": SFX + "001_뽁.wav", "whoosh": SFX + "002_휙(만화적).mp3",
    "clips": [
        {"src": R + "1ng2nwz.mp4", "in": 0.0, "hit": 1.65, "out": 3.0, "cy": 0.45,
         "replay": {"in": 1.5, "out": 2.9, "speed": 0.4},
         "watch": {"src": M("hUBXfYvvOlU"), "cy": 0.25}, "shock": {"src": M("btYkcmAPyCc"), "cy": 0.3},
         "score": [["IMPACT", 7], ["FUNNY", 8]]},
        {"src": R + "1mi1aq3.mp4", "in": 1.7, "hit": 3.45, "out": 4.7,
         "replay": {"in": 3.2, "out": 4.4, "speed": 0.4},
         "watch": {"src": M("IHkcQwK9lRA"), "cy": 0.3}, "shock": {"src": M("CNI1fSM1XSo"), "cy": 0.25},
         "score": [["IMPACT", 9], ["FUNNY", 9]]},
        {"src": R + "1pnl9yk.mp4", "in": 3.0, "hit": 4.6, "out": 7.6, "cy": 0.3,
         "replay": {"in": 4.3, "out": 5.3, "speed": 0.4},
         "watch": {"src": M("zqSA5TmyIYU"), "cy": 0.3}, "shock": {"src": M("cx-6vijuIsE"), "cy": 0.25, "ss": 2.5},
         "score": [["IMPACT", 6], ["FUNNY", 10]]},
    ],
}
json.dump(spec, open('spec.json', 'w'), indent=1, ensure_ascii=False)
