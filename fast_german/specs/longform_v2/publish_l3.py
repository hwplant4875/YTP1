"""L3: .srt, YouTube chapters, description, titles sheet; `upload` uploads private + scheduled with thumbnail 1a and the .srt."""
import json, os, sys, urllib.request, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
import short_v2 as S, upload as U
HERE = os.path.dirname(__file__)
OUT = "/mnt/project-files/fast_german/upload/L3_greetings/"
spec = json.load(open(os.path.join(HERE, "l3_greetings.json")))
clips, timeline, pops, total, subs = S.plan(spec)


def ts(t, srt=False):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",") if srt else f"{m}:{int(s):02d}"


# .srt: one cue per spoken segment, German lines as they are written on screen
with open(OUT + "L3_greetings.en.srt", "w") as f:
    for i, (a, b, text, de) in enumerate(subs, 1):
        f.write(f"{i}\n{ts(a, True)} --> {ts(b, True)}\n{text}\n\n")

chap, seen = ["0:00 50 German phrases in 10 minutes"], set()
for i, tl in enumerate(timeline):
    sc = tl["scene"]
    first = sc["lines"][0][0].get("en", "")
    if sc.get("header") and sc["header"] not in seen:
        seen.add(sc["header"]); chap.append(f"{ts(tl['start'])} {sc['header'].replace(' · ', ': ')}")
    elif first.startswith("Quick quiz"):
        chap.append(f"{ts(tl['start'])} Quick quiz")
    elif first.startswith("You just learned"):
        chap.append(f"{ts(tl['start'])} Well done!")

TITLES = [("1a", "German Greetings & Basic Phrases for Beginners (50 Phrases in 10 Minutes)", "clean: 50 German phrases + waving hand"),
          ("1b", "Stop Saying Only \"Hallo\": 50 German Phrases Germans Actually Use", "provocative: red circle on Hallo, arrow to Moin / Servus / Na?"),
          ("1c", "Speak German in 10 Minutes: 50 Phrases for Real Life 👋", "real photo: Berlin Cathedral and TV tower")]
DESC = ("Learn the 50 German phrases you'll use every day, in 10 minutes. Hello, how are you, introducing yourself, "
        "please and thank you, what to say when you don't understand, and how to say goodbye.\n\n"
        "Every phrase: English first, then German, then German slowly. When the yellow circle fills, say it out loud.\n\n"
        + "\n".join(chap) +
        "\n\nNew German every day. Follow for more German.\n\n"
        "Music:\n\"Lobby Time\" Kevin MacLeod (incompetech.com)\n\"Easy Lemon\" Kevin MacLeod (incompetech.com)\n"
        "Licensed under Creative Commons: By Attribution 4.0 License\nhttp://creativecommons.org/licenses/by/4.0/\n\n"
        "#learngerman #german #germanforbeginners")
TAGS = ["learn german", "german for beginners", "german greetings", "german phrases", "basic german phrases",
        "how to say hello in german", "german conversation", "deutsch lernen", "german a1", "learn german fast",
        "german words", "common german phrases", "german lesson", "fast german"]
open(OUT + "description.txt", "w").write(DESC)
with open(OUT + "titles.md", "w") as f:
    f.write("# German Greetings & Basic Phrases: A/B titles and thumbnails\n\nUploaded with 1a. In YouTube Studio: Test & compare, add 1b and 1c.\n\n"
            "| | Title | Thumbnail |\n|---|---|---|\n" + "".join(f"| {k} | {t} | {k}.jpg ({n}) |\n" for k, t, n in TITLES)
            + "\nTags: " + ", ".join(TAGS) + "\n")
print(DESC, "\ntotal", total)

if "upload" in sys.argv:
    vid = U.upload(OUT + "L3_greetings.mp4", TITLES[0][1], DESC, TAGS, "2026-10-12T12:00:00Z", OUT + "1a.jpg")
    vid, thumb_ok = vid
    print("video", vid, "thumb", thumb_ok)
    tok, b = U.token(), uuid.uuid4().hex
    meta = json.dumps({"snippet": {"videoId": vid, "language": "en", "name": "English"}})
    body = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{meta}\r\n--{b}\r\nContent-Type: application/octet-stream\r\n\r\n").encode() \
        + open(OUT + "L3_greetings.en.srt", "rb").read() + f"\r\n--{b}--".encode()
    r = urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/captions?uploadType=multipart&part=snippet", data=body,
                               headers={"Authorization": "Bearer " + tok, "Content-Type": f"multipart/related; boundary={b}"})
    print("captions", json.load(urllib.request.urlopen(r)).get("id"))
