"""Voice audition: first two items of items.tsv in the video's order (EN word, KO word, EN sentence, KO sentence, KO slow).
Usage: python3 audition.py <outdir> name=typecast_voice_id[:emotion] ..."""
import csv, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from voices import korean, english
GAPS = [0.7, 1.6, 1.1, 1.6, 2.8]  # same as GAP in build.py
rows = list(csv.DictReader(open(f"{HERE}/items.tsv", encoding="utf-8"), delimiter="\t"))[:2]
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for i, arg in enumerate(sys.argv[2:], 1):
    name, vid = arg.split("="); vid, emo = (vid.split(":") + ["normal"])[:2]
    parts = []
    for r in rows:
        clips = [english(re.sub(r"\s*\([^)]*\)", "", r["en_word"]))[0], korean(r["ko_word"] + ".", voice=vid, emotion=emo)[0], english(r["en_sentence"])[0],
                 korean(r["ko_sentence"], voice=vid, emotion=emo)[0], korean(r["ko_sentence"], 0.7, voice=vid, emotion=emo)[0]]
        for c, g in zip(clips, GAPS): parts += [c, g]
    inputs, chain = [], ""
    for j, p in enumerate(parts[0::2]):
        inputs += ["-i", p]; chain += f"[{j}]apad=pad_dur={parts[2 * j + 1]}[a{j}];"
    n = len(parts) // 2
    chain += "".join(f"[a{j}]" for j in range(n)) + f"concat=n={n}:v=0:a=1,loudnorm=I=-18[o]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", chain, "-map", "[o]", "-ar", "48000", "-b:a", "192k", f"{out}/{i}-{name}.mp3"], check=True)
    print(i, name, flush=True)
