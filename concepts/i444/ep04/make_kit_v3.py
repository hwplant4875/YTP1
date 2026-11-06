# EP04 Freddy v3 upload kit (copy of ../ep07_pinhead/make_kit_v8.py): chapter times from edl.json (each section = its voice take + pad,
# the same timing make_srt.py and the renderer use). No colons anywhere, no ":" or "-" in titles (owner 11/05). usage: python make_kit_v3.py
import json, subprocess
E = json.load(open('edl.json'))
ST = {e['sec']: e for e in json.load(open('stats.json'))['entries']}
def dur(p):  # decoded length (the render is timed on it; ffprobe 'format=duration' adds ~0.04 s per mp3)
    return len(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', '48000', '-'])) / 2 / 48000
FILM = {'s02': 'Freddy vs. Jason', 's03': "Freddy's Revenge", 's04': 'The Dream Child', 's05': "Freddy's Dead", 's06': 'The 2010 remake',
        's07': 'New Nightmare', 's08': 'The 1984 original', 's09': 'Dream Warriors', 's10': 'The Dream Master'}
NAME = {'s00': 'He will drag you across the ceiling', 's01': 'How the survival rate works', 's11': 'Which Freddy scares you most?'}
t, ch = 0.0, []
for S in E['sections']:
    k = S['voice']
    ch.append((t, NAME.get(k) or f"#{ST[k]['rank']} {FILM[k]} ({ST[k]['pct']}%)"))
    t += dur(f'voice/{k}.mp3') + S.get('pad', 0.5)
order = [S['voice'] for S in E['sections']]
assert order == ['s00', 's01', 's02', 's03', 's04', 's05', 's06', 's07', 's08', 's09', 's10', 's11'], order
assert all(b[0] - a[0] >= 10 for a, b in zip(ch, ch[1:])), 'a chapter is shorter than 10 s'
def mmss(x): x = int(x); return f'{x // 60}:{x % 60:02d}'
kit = f'''# EP04 Freddy Krueger upload kit v3

Video, two versions with the same picture and voice, pick one ({mmss(t)} each):
- Mixkit music: E:\\YTP2\\Horror Ranked\\EP04 Freddy Krueger\\2_renders\\ep04_freddy_v3.mp4
- ElevenLabs bed (the channel's usual sound): E:\\YTP2\\Horror Ranked\\EP04 Freddy Krueger\\2_renders\\ep04_freddy_v3_eleven.mp4

Subtitles: upload/freddy_ranked_en_v3.srt | Thumbnails: upload/freddy_thumb_a/b/c.jpg

## Titles (pick one, never a colon or a dash)
1. Every Freddy Krueger Ranked by Your Chance of Surviving Him  (recommended, series format)
2. Every Nightmare on Elm Street Movie Ranked by Your Chance of Surviving Freddy
3. Could You Survive Freddy Krueger in Every Nightmare on Elm Street Movie?

## Description
You fall asleep tonight, and Freddy is waiting for you. How likely are you to survive him? Every Freddy is different. One is so weak he needs Jason to kill for him, one needs a teenager's body, and one is strong enough to wipe out kids with superpowers. We score each one on strength, intelligence, kill count and dream power, and rank all nine films, from Freddy vs. Jason, where he can't even find you if you've never heard his name, to The Dream Master, the Freddy who wiped out the Dream Warriors.

Which Freddy would you least want to meet tonight? Tell me in the comments, along with the killer I should rank next.

Clips are used for commentary and criticism. All rights belong to their owners.

Chapters
''' + '\n'.join(f'{mmss(a)} {n}' for a, n in ch) + '''

## Tags
freddy krueger, a nightmare on elm street, freddy, horror, horror movies, wes craven, dream warriors, ranked

## Music note
The description works for both versions. The Mixkit tracks (Piano Horror by Francisco Alvear, Echoes by Andrew Ev, Xanthos by Eugenio Mininni) are under the Mixkit Stock Music Free License, which needs no credit; the ElevenLabs bed was made for this episode.
'''
assert ':' not in kit.split('## Titles')[1].split('## Description')[0].replace('## Titles (pick one, never a colon or a dash)', '')
open('upload/upload_kit_v3.md', 'w', encoding='utf-8').write(kit)
print(kit)
