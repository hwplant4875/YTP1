# EP07 v7 upload kit: chapter times from edl.json (each section = its voice take + pad, the same timing make_srt.py and the
# renderer use), description refreshed for the v7 script (Hellbound safest .. Hell on Earth deadliest). usage: python3 make_kit_v7.py
import json, subprocess
E = json.load(open('edl.json'))
ST = {e['sec']: e for e in json.load(open('stats.json'))['entries']}
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', '0', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
FILM = {'s04': 'Hellbound: Hellraiser II', 's05': 'Hellraiser: Revelations', 's06': 'Hellraiser 1987', 's07': 'Hellraiser: Hellseeker',
        's08': 'Hellraiser 2022', 's09': 'Hellraiser: Bloodline', 's02': 'Hellraiser: Hellworld', 's10': 'Hellraiser: Deader',
        's03': 'Hellraiser: Judgment', 's11': 'Hellraiser: Inferno', 's12': 'Hellraiser III: Hell on Earth'}
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
kit = f'''# EP07 Pinhead upload kit v7

Video: E:\\YTP2\\Horror Ranked\\EP07 Pinhead\\2_renders\\ep07_pinhead_v7.mp4 ({mmss(t)}) | Subtitles: upload/pinhead_ranked_en_v7.srt | Thumbnails: upload/pinhead_thumb_a/b/c.jpg

## Titles (pick one; no ":" or "-")
1. Every Pinhead Ranked by Your Chance of Surviving Him  (recommended: series format)
2. Every Hellraiser Movie Ranked by Your Chance of Surviving Pinhead
3. Could You Survive Pinhead in Every Hellraiser Movie?

## Thumbnails (left GREEN / middle YELLOW / right RED; same odds as v6, so the v6 files stay valid)
A. Revelations 70% / Hellseeker 45% / Judgment 10%
B. Hellraiser 1987 55% / the Priest, 2022 35% / Inferno 8%
C. Hellbound 85% / Bloodline 25% / Hell on Earth 5%

## Description
You just solved the puzzle box, and Pinhead is standing in your room. How likely are you to survive him? We score every Pinhead on strength, intelligence, kill count and how merciless he is, which decides whether you can bargain your way out, and rank all eleven Hellraiser films, from Hellbound, where Pinhead dies remembering he was human, to Hell on Earth, where he follows no rules at all.

Which box would you be brave enough to open? Tell me in the comments, along with the killer I should rank next.

Clips are used for commentary and criticism. All rights belong to their owners.
Music: original score made for this channel (ElevenLabs Music)

Chapters
''' + '\n'.join(f'{mmss(a)} {n}' for a, n in ch) + '''

## Tags
pinhead, hellraiser, horror, horror movies, cenobites, clive barker, the priest, hellbound, ranked
'''
open('upload/upload_kit_v7.md', 'w', encoding='utf-8').write(kit)
print(kit)
