# EP07 v8 upload kit: chapter times from edl.json (each section = its voice take + pad, the same timing make_srt.py and the
# renderer use), description and chapter names follow the owner-approved v8 script, with no colons anywhere (owner 11/05). usage: python3 make_kit_v8.py
import json, subprocess
E = json.load(open('edl.json'))
ST = {e['sec']: e for e in json.load(open('stats.json'))['entries']}
def dur(p):  # decoded length: the laptop's newer ffprobe reports this (no encoder delay/padding), and the render is timed on it;
    # ffprobe 6.1 'format=duration' adds ~0.04 s per mp3, which drifted the v8 srt 0.6 s late by the end
    return len(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', '48000', '-'])) / 2 / 48000
FILM = {'s04': 'Hellbound', 's05': 'Revelations', 's06': 'Hellraiser 1987', 's07': 'Hellseeker',
        's08': 'Hellraiser 2022', 's09': 'Bloodline', 's02': 'Hellworld', 's10': 'Deader',
        's03': 'Judgment', 's11': 'Inferno', 's12': 'Hell on Earth'}
NAME = {'s00': 'Hooked chains', 's01': 'How the survival rate works', 's13': 'Which box would you open?'}
t, ch = 0.0, []
for S in E['sections']:
    k = S['voice']
    ch.append((t, NAME.get(k) or f"#{ST[k]['rank']} {FILM[k]} ({ST[k]['pct']}%)"))
    t += dur(f'voice/{k}.mp3') + S.get('pad', 0.5)
order = [S['voice'] for S in E['sections']]
assert order == ['s00', 's01', 's04', 's05', 's06', 's07', 's08', 's09', 's02', 's10', 's03', 's11', 's12', 's13'], order
assert all(b[0] - a[0] >= 10 for a, b in zip(ch, ch[1:])), 'a chapter is shorter than 10 s'
def mmss(x): x = int(x); return f'{x // 60}:{x % 60:02d}'
kit = f'''# EP07 Pinhead upload kit v8

Video: E:\\YTP2\\Horror Ranked\\EP07 Pinhead\\2_renders\\ep07_pinhead_v8.mp4 ({mmss(t)}) | Subtitles: upload/pinhead_ranked_en_v8.srt | Thumbnails: upload/pinhead_thumb_a/b/c/d/e/f.jpg

## Titles (pick one, never a colon or a dash)
1. Every Pinhead Ranked by Your Chance of Surviving Him  (recommended, series format)
2. Every Hellraiser Movie Ranked by Your Chance of Surviving Pinhead
3. Could You Survive Pinhead in Every Hellraiser Movie?

## Thumbnails (left GREEN / middle YELLOW / right RED; same odds as v6 and v7, so these files stay valid)
A. Revelations 70% / Hellseeker 45% / Judgment 10%
B. Hellraiser 1987 55% / the Priest, 2022 35% / Inferno 8%
C. Hellbound 85% / Bloodline 25% / Hell on Earth 5%
D. Hellbound 85% / Hellseeker 45% / Hellworld 20%  (new 11/05, official HD stills)
E. Revelations 70% / the Priest, 2022 35% / Hell on Earth 5%  (new 11/05)
F. Hellraiser 1987 55% / Bloodline 25% / Judgment 10%  (new 11/05)

## Description
You just solved the puzzle box, and Pinhead is standing in your room. How likely are you to survive him? Every Pinhead is different. Some play by the rules, some take your deal and come for you anyway, and one doesn't even need the box. We score each one on strength, intelligence, kill count and how much mercy he shows, and rank all eleven Hellraiser films, from Hellbound, where Pinhead dies remembering he was human, to Hell on Earth, where he follows no rules at all.

Which box would you be brave enough to open? Tell me in the comments, along with the killer I should rank next.

Clips are used for commentary and criticism. All rights belong to their owners.
Music is an original score made for this channel with ElevenLabs Music.

Chapters
''' + '\n'.join(f'{mmss(a)} {n}' for a, n in ch) + '''

## Tags
pinhead, hellraiser, horror, horror movies, cenobites, clive barker, the priest, hellbound, ranked
'''
open('upload/upload_kit_v8.md', 'w', encoding='utf-8').write(kit)
print(kit)
