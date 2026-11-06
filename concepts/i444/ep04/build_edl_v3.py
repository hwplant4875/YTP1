# EP04 Freddy v3 EDL (owner-approved script_v3.md, 11/7 01:35 KST "좋다. 진행."), adapted from ../ep07_pinhead/build_edl_v8.py.
# Shots are (phrase, clip, in, -clean[, opts]) anchored to the exact script words in voice/words.json. The shots live in
# shots_v3.py (written on the laptop from verified frame grabs, see beats_v3.md and shot_plan_v3.md). Playback order s00..s11.
# usage: python build_edl_v3.py   -> edl.json   (then python qa/caption_coverage.py)
import json, re, os
D = os.path.dirname(os.path.abspath(__file__)) + '/'
W = json.load(open(D + 'voice/words.json'))
ST = {e['sec']: e for e in json.load(open(D + 'stats.json'))['entries']}
STATS = json.load(open(D + 'stats.json'))['stats']          # STRENGTH, INTELLIGENCE, KILL COUNT, DREAM POWER
LEAD = 0.08
def norm(s): return re.sub(r"[^a-z0-9']", '', s.lower())
def at(seg, phrase):   # 'freddy is#2' = the 2nd occurrence
    phrase, _, k = phrase.partition('#'); k = int(k or 1)
    ws = [norm(w[2]) for w in W[seg]]; ph = [norm(p) for p in phrase.split()]
    for i in range(len(ws) - len(ph) + 1):
        if ws[i:i + len(ph)] == ph:
            k -= 1
            if k == 0: return W[seg][i][0]
    raise KeyError((seg, phrase))
def T(seg, x): return x if isinstance(x, (int, float)) else round(max(0, at(seg, x) - LEAD), 3)
def AL(seg): return json.load(open(D + f'voice/{seg}.json'))
def vdur(seg): return round(AL(seg)['character_end_times_seconds'][-1], 3)
def num_onset(seg):  # first letter/digit after the last "Survival rate"
    a = AL(seg); s = ''.join(a['characters']); i = s.rfind('Survival rate') + len('Survival rate')
    while not s[i].isalnum(): i += 1
    return a['character_start_times_seconds'][i]
TILE = {'s02': 'fj', 's03': 'n2', 's04': 'n5', 's05': 'n6', 's06': 'r10', 's07': 'n7', 's08': 'n1', 's09': 'n3', 's10': 'n4'}
SHORT = {'s02': 'Freddy vs. Jason (2003)', 's03': "Freddy's Revenge (1985)", 's04': 'The Dream Child (1989)', 's05': "Freddy's Dead (1991)",
         's06': 'A Nightmare on Elm Street (2010)', 's07': 'New Nightmare (1994)', 's08': 'A Nightmare on Elm Street (1984)',
         's09': 'Dream Warriors (1987)', 's10': 'The Dream Master (1988)'}
CARD_AT = {'s02': "if you've never heard", 's03': 'stay far away', 's04': 'he only gets three', 's05': "he's deadly but",
           's06': "staying awake won't", 's07': 'he only gets four', 's08': "unless you're as", 's09': "you don't have", 's10': 'if the kids'}
TIERS = [['S', 'Slaughtered', 25], ['A', 'Almost Dead', 40], ['B', 'Better Run', 50], ['C', 'Close Call', 60], ['D', "Don't Worry", 80],
         ['E', 'Easy', 101]]
SFX_GAIN = {'whoosh': -16, 'fill': -20, 'stamp': -12}
SFX = '../ep03/sfx/'
L = 'z=1.35,dx=249'   # subject left of the stat card
def sec(voice, shots, card_at=None, extra=(), pad=0.05, clip_db=-99):   # short pads, the narration runs on (owner 11/04)
    shots = [[T(voice, s[0]), *s[1:]] for s in shots]
    S = {'voice': voice, 'pad': pad, 'clip_audio_db': clip_db, 'shots': shots, 'overlays': [], 'sfx': []}
    if voice in ST:
        e = ST[voice]; film = SHORT.get(voice, e['film']); card_at = card_at or CARD_AT[voice]
        S['overlays'].append(['rank', [e['rank'], e['villain'], film], 0.0, 2.9])
        S['pad'] = 0.15; a = T(voice, card_at); tp = round(num_onset(voice) - 0.05 - a, 3)
        S['overlays'].append(['stats', {'name': 'FREDDY KRUEGER', 'tile_png': f'tiles/{TILE[voice]}.png',
                                        'stats': dict(zip(STATS, e['v'])), 'pct': e['pct'],
                                        't_pct': tp, 'dur': round(vdur(voice) + S['pad'] - a, 3), 'film': film}, a, 999])
        S['sfx'] += [[a, SFX + 'whoosh.wav', SFX_GAIN['whoosh']], [a + 0.3, SFX + 'fill.wav', SFX_GAIN['fill']], [a + tp, SFX + 'stamp.wav', SFX_GAIN['stamp']]]
        S['card_at'] = a
    S['overlays'] += [[k, val, T(voice, x), T(voice, y)] for k, val, x, y in extra]
    return S
X = []
exec(open(D + 'shots_v3.py', encoding='utf-8').read())   # appends one sec(...) per section, s00..s11 (see shot_plan_v3.md)
def fit(S):  # turn (t, clip, in, -clean) into a speed that keeps the shot inside its clean span (never below 0.4x)
    Ls = vdur(S['voice']) + S['pad']; sh = S['shots']
    for k, s in enumerate(sh):
        if len(s) > 3 and s[3] < 0:
            d = (sh[k + 1][0] if k + 1 < len(sh) else Ls) - s[0]; sp = min(1.0, -s[3] * 0.96 / d)
            if sp < 0.4: print('WARN too short', S['voice'], s, round(d, 2))
            sp = max(sp, 0.4)
            s[3] = round(sp, 3) if sp < 0.999 else 1.0
        if len(s) > 4 and isinstance(s[4], str): s[4] = {'flip': 1} if s[4] == 'flip' else dict(kv.split('=') for kv in s[4].split(','))
        if len(s) > 4: s[4] = {k: float(v) for k, v in s[4].items()}
        elif len(s) > 3 and s[3] == 1.0: del s[3:]
ORDER = ['s00', 's01', 's02', 's03', 's04', 's05', 's06', 's07', 's08', 's09', 's10', 's11']
assert sorted(S['voice'] for S in X) == ORDER, [S['voice'] for S in X]
X.sort(key=lambda S: ORDER.index(S['voice']))
for S in X: fit(S)
FILM = [('n1_', 'A Nightmare on Elm Street (1984)'), ('n2_', "A Nightmare on Elm Street 2: Freddy's Revenge (1985)"),
        ('n3_', 'A Nightmare on Elm Street 3: Dream Warriors (1987)'), ('n4_', 'A Nightmare on Elm Street 4: The Dream Master (1988)'),
        ('n5_', 'A Nightmare on Elm Street 5: The Dream Child (1989)'), ('n6_', "Freddy's Dead: The Final Nightmare (1991)"),
        ('n7_', "Wes Craven's New Nightmare (1994)"), ('fj_', 'Freddy vs. Jason (2003)'), ('r10_', 'A Nightmare on Elm Street (2010)')]
def film(n): return next((v for k, v in FILM if n.startswith(k)), None)
for S in X:  # film label per run of one film, gone once the stat card takes the frame (none under the rules card)
    end = S.pop('card_at', 0 if S['voice'] == 's01' else 999)
    runs = []
    for t, n, *_ in S['shots']:
        if t >= end: break
        f = film(n)
        if runs and runs[-1][0] == f: continue
        runs.append([f, t])
    for k, (f, t) in enumerate(runs):
        if f: S['overlays'].append(['film', f, t, min(end, runs[k + 1][1] if k + 1 < len(runs) else 999)])
VDARK, DARK, ZOOM, BAR = [], [], {}, {}   # filled on the laptop after the first QA pass (luma under 8 -> VDARK, soft dark -> DARK)
exec(open(D + 'shots_v3_grade.py', encoding='utf-8').read()) if os.path.exists(D + 'shots_v3_grade.py') else None
P = {'sections': X, 'tiers': TIERS, 'gamma': {**{k: 1.25 for k in DARK}, **{k: 1.4 for k in VDARK}}, 'zoom': ZOOM, 'bar': BAR}
json.dump(P, open(D + 'edl.json', 'w'), indent=1)
print(len(X), 'sections')
