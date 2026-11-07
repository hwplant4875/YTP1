# Backrooms special upload kit (11/7 KST): titles, description with chapters taken from the EDL's section starts, sources, tags.
# usage: python make_kit.py [edl.json] [out.md] [fps]   -> upload/backrooms_kit.md (the .srt comes from make_srt.py)
import json, os, sys
edl = sys.argv[1] if len(sys.argv) > 1 else 'edl.json'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'upload/backrooms_kit.md'
FPS = int(sys.argv[3]) if len(sys.argv) > 3 else 30
E = json.load(open(edl)); starts, tg = {}, 0.0
for S in E['sections']: starts[S['voice']] = round(tg * FPS) / FPS; tg += S['len']
def mmss(t): return f'{int(t // 60)}:{int(t % 60):02d}'
CH = [('s00', 'Five went in'), ('s01', 'The 1990 tape'), ('s02', 'Stage 1, the slit (90%)'), ('s03', 'Stage 2, the map (70%)'),
      ('s04', 'Stage 3, the laundry room (40%)'), ('s05', 'Stage 4, the still lifes (15%)'), ('s06', 'Stage 5, after him (10%)'),
      ('s07', 'Stage 6, your old home (7%)'), ('s08', 'Stage 7, the dining room (5%)'), ('s09', 'Stage 8, Captain Clark (2%)'),
      ('s10', 'Async, 1 of 5'), ('s11', 'What the tapes really show')]
TITLES = ['How Long Would You Survive in the Backrooms?',
          'Five People Entered the Backrooms and Only One Came Out',
          'Could You Survive the Backrooms Movie?']
# Description layout (owner 11/8 00:36 KST, all future kits): 1) one line as a horror-movie fan, 2) [ Timeline ], 3) tags, 4) nothing else.
DESC = f"""As a horror fan, Backrooms is the first movie in years that scared me with nothing but empty yellow rooms, and that hum still follows me around.

[ Timeline ]
{chr(10).join(f'{mmss(starts[k])} {name}' for k, name in CH)}

#Backrooms #A24 #HorrorRanked #CaptainClark #KanePixels"""
TAGS = ['backrooms', 'the backrooms', 'backrooms movie', 'the backrooms movie', 'a24 backrooms', 'kane parsons', 'kane pixels',
        'backrooms explained', 'backrooms ending explained', 'captain clark', 'how long would you survive', 'could you survive',
        'horror movie', 'survival', 'liminal space', 'chiwetel ejiofor', 'renate reinsve', 'a24 horror', 'horror ranked']
os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('# The Backrooms survival special, upload kit\n\n## Titles (pick one; no colon or dash)\n' + ''.join(f'{i + 1}. {t}\n' for i, t in enumerate(TITLES)))
    f.write(f'\n## Description\n\n{DESC}\n\n## Tags\n{", ".join(TAGS)}\n\n## Length\n{mmss(tg)} ({tg:.1f} s)\n\n'
            '## Files\n- English captions: backrooms_survival_en.srt\n- Thumbnails: backrooms_thumb_a.jpg to backrooms_thumb_f.jpg\n')
print(OUT, mmss(tg))
