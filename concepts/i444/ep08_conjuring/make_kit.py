# EP08 Conjuring Universe upload kit (11/9 KST, copy of ../ep_backrooms/make_kit.py): titles, the description in the owner's layout,
# YouTube tags, length and files. Chapter times are the EDL's section starts, rounded to whole frames like render_cj.py.
# Description layout (owner 11/8 00:36 KST, every kit): 1) one line as a horror-movie fan, 2) [ Timeline ], 3) hashtags, 4) nothing else.
# No ":" or "-" in titles (owner 11/05); none in chapter names either.
# usage: python make_kit.py [edl.json] [out.md] [fps]   -> upload/conjuring_kit.md (the .srt comes from make_srt.py)
import json, os, sys
edl = sys.argv[1] if len(sys.argv) > 1 else 'edl.json'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'upload/conjuring_kit.md'
FPS = int(sys.argv[3]) if len(sys.argv) > 3 else 30
E = json.load(open(edl)); ST = {e['sec']: e for e in json.load(open('stats.json'))['entries']}
starts, tg = {}, 0.0
for S in E['sections']: starts[S['voice']] = round(tg * FPS) / FPS; tg += S['len']
def mmss(t): return f'{int(t // 60)}:{int(t % 60):02d}'
NAME = {'s02': 'Annabelle Comes Home', 's03': 'Annabelle', 's04': 'The Conjuring', 's05': 'The Conjuring 2', 's06': 'The Conjuring Last Rites',
        's07': 'Annabelle Creation', 's08': 'The Devil Made Me Do It', 's09': 'The Nun II', 's10': 'The Nun'}
CH = [('s00', 'These demons will burn you alive'), ('s01', 'How the survival rate works')] + \
     [(k, f"#{ST[k]['rank']} {NAME[k]} ({ST[k]['pct']}%)") for k in ['s02', 's03', 's04', 's05', 's06', 's07', 's08', 's09', 's10']] + \
     [('s11', 'Which demon would you least want at home?')]
assert all(starts[b[0]] - starts[a[0]] >= 10 for a, b in zip(CH, CH[1:])), 'a chapter is shorter than 10 s'
TITLES = ['Every Conjuring Demon Ranked by Your Chance of Surviving It',
          'Every Conjuring Universe Movie Ranked by Your Chance of Surviving the Demon',
          'Could You Survive Valak? Every Conjuring Demon Ranked']
for t in TITLES: assert ':' not in t and '-' not in t, t
DESC = f"""As a horror fan, I've seen every Conjuring movie more times than I should admit, and that Valak painting scene still makes me sleep with the lights on.

[ Timeline ]
{chr(10).join(f'{mmss(starts[k])} {name}' for k, name in CH)}

#TheConjuring #Valak #Annabelle #TheNun #HorrorRanked"""
TAGS = ['the conjuring', 'conjuring universe', 'valak', 'the nun', 'annabelle', 'the conjuring 2', 'the conjuring last rites',
        'annabelle comes home', 'annabelle creation', 'the nun 2', 'the devil made me do it', 'ed and lorraine warren', 'bathsheba',
        'conjuring ranked', 'could you survive', 'horror movies', 'horror ranked', 'scariest demons']
os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('# EP08 The Conjuring Universe, upload kit\n\n## Titles (pick one; no colon or dash)\n' +
            ''.join(f'{i + 1}. {t}' + ('  (recommended, the series format)' if i == 0 else '') + '\n' for i, t in enumerate(TITLES)))
    f.write(f'\n## Description\n\n{DESC}\n\n## Tags\n{", ".join(TAGS)}\n\n## Length\n{mmss(tg)} ({tg:.1f} s)\n\n'
            '## Files\n- Video: 2_renders\\conjuring_ranked_v3.mp4\n- English captions: conjuring_ranked_en.srt\n'
            '- Thumbnails: conjuring_thumb_a.jpg (95/55/5), conjuring_thumb_b.jpg (80/45/5), conjuring_thumb_c.jpg (40/30/5)\n')
print(OUT, mmss(tg))
