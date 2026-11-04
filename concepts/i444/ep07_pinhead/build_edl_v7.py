# EP07 v7 (owner 11/05 00:59 KST: everything after the intro rebuilt from scratch for the final order and odds).
# Shots are (phrase, clip, in, -clean[, opts]) anchored to the exact script words in voice/words.json; every in-point is from
# verified frame grabs (beats_v7.md, shots_v7.md). Hellbound = the showcase: Pinhead struck and burned away at natural speed.
import json, re, os
D = os.path.dirname(os.path.abspath(__file__)) + '/'
W = json.load(open(D + 'voice/words.json'))
ST = {e['sec']: e for e in json.load(open(D + 'stats.json'))['entries']}
LEAD = 0.08
def norm(s): return re.sub(r"[^a-z0-9']", '', s.lower())
def at(seg, phrase):   # 'this one will#2' = the 2nd occurrence (v7 cold open repeats its lead-in)
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
TILE = {'s02': 'hr8', 's03': 'hr10', 's04': 'hr2', 's05': 'hr9', 's06': 'hr1', 's07': 'hr6', 's08': 'hr22', 's09': 'hr4', 's10': 'hr7', 's11': 'hr5', 's12': 'hr3'}
SHORT = {'s02': 'Hellworld (2005)', 's03': 'Judgment (2018)', 's04': 'Hellbound (1988)', 's05': 'Revelations (2011)', 's07': 'Hellseeker (2002)', 's09': 'Bloodline (1996)', 's10': 'Deader (2005)', 's11': 'Inferno (2000)', 's12': 'Hell on Earth (1992)'}
TIERS = [['S', 'Slaughtered', 25], ['A', 'Almost Dead', 40], ['B', 'Better Run', 50], ['C', 'Close Call', 60], ['D', "Don't Worry", 80],
         ['E', 'Easy', 101]]
SFX_GAIN = {'whoosh': -16, 'fill': -20, 'stamp': -12}
SFX = '../ep03/sfx/'
def sec(voice, shots, card_at=None, extra=(), pad=0.05, clip_db=-99):   # v3: short pads, the narration runs on (owner 11/04)
    shots = [[T(voice, s[0]), *s[1:]] for s in shots]
    S = {'voice': voice, 'pad': pad, 'clip_audio_db': clip_db, 'shots': shots, 'overlays': [], 'sfx': []}
    if voice in ST:
        e = ST[voice]; film = SHORT.get(voice, e['film'])
        S['overlays'].append(['rank', [e['rank'], e['villain'], film], 0.0, 2.9])
        S['pad'] = 0.15; a = T(voice, card_at); tp = round(num_onset(voice) - 0.05 - a, 3)
        S['overlays'].append(['stats', {'name': e['villain'].upper(), 'tile_png': f'tiles/{TILE[voice]}.png',
                                        'stats': dict(zip(['STRENGTH', 'INTELLIGENCE', 'KILL COUNT', 'NO MERCY'], e['v'])), 'pct': e['pct'],
                                        't_pct': tp, 'dur': round(vdur(voice) + S['pad'] - a, 3), 'film': film}, a, 999])
        S['sfx'] += [[a, SFX + 'whoosh.wav', SFX_GAIN['whoosh']], [a + 0.3, SFX + 'fill.wav', SFX_GAIN['fill']], [a + tp, SFX + 'stamp.wav', SFX_GAIN['stamp']]]
        S['card_at'] = a
    S['overlays'] += [[k, val, T(voice, x), T(voice, y)] for k, val, x, y in extra]
    return S
X = []
exec(open(D + "shots_v7.py", encoding="utf-8").read())
def fit(S):  # turn (t, clip, in, -clean) into a speed that keeps the shot inside its clean span (never below 0.4x)
    L = vdur(S['voice']) + S['pad']; sh = S['shots']
    for k, s in enumerate(sh):
        if len(s) > 3 and s[3] < 0:
            d = (sh[k + 1][0] if k + 1 < len(sh) else L) - s[0]; sp = min(1.0, -s[3] * 0.96 / d)
            if sp < 0.4: print('WARN too short', S['voice'], s, round(d, 2))
            sp = max(sp, 0.4)
            s[3] = round(sp, 3) if sp < 0.999 else 1.0
        if len(s) > 4 and isinstance(s[4], str): s[4] = {'flip': 1} if s[4] == 'flip' else dict(kv.split('=') for kv in s[4].split(','))
        if len(s) > 4: s[4] = {k: float(v) for k, v in s[4].items()}
        elif len(s) > 3 and s[3] == 1.0: del s[3:]
ORDER = ['s00', 's01', 's04', 's05', 's06', 's07', 's08', 's09', 's02', 's10', 's03', 's11', 's12', 's13']   # v6 countdown (owner 11/04): #11 Hellbound .. #1 Hell on Earth
X.sort(key=lambda S: ORDER.index(S['voice']))
for S in X: fit(S)
FILM = [('hr1_', 'Hellraiser (1987)'), ('hr2_', 'Hellbound: Hellraiser II (1988)'), ('hr3_', 'Hellraiser III: Hell on Earth (1992)'),
        ('hr4_', 'Hellraiser: Bloodline (1996)'), ('hr5_', 'Hellraiser: Inferno (2000)'), ('hr6_', 'Hellraiser: Hellseeker (2002)'),
        ('hr7_', 'Hellraiser: Deader (2005)'), ('hr8_', 'Hellraiser: Hellworld (2005)'), ('hr9_', 'Hellraiser: Revelations (2011)'),
        ('hr10_', 'Hellraiser: Judgment (2018)'), ('hr22_', 'Hellraiser (2022)')]
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
VDARK = ['hr1_dont', 'hr8_explain', 'hr22_bridge', 'hr4_pathway', 'hr4_space', 'hr4_painface', 'hr4_finalbattle', 'hr22_carousel', 'hr22_bridge', 'hr22_cenofeat', 'hr22_trailer_20th']  # v4: shots under luma 8 in v3
DARK = ['hr2_legendary', 'hr1_sights', 'hr10_judge4k', 'hr3_club', 'hr6_painpleasure', 'hr6_pain', 'hr22_nora', 'hr5_torment', 'hr8_welcome', 'hr8_jake', 'hr8_cop', 'hr10_souls', 'hr22_carousel', 'hr3_pillar', 'hr5_box', 'hr5_cruelty', 'hr7_returns', 'hr7_afraid', 'hr9_trailer_rt']
P = {'sections': X, 'tiers': TIERS, 'gamma': {**{k: 1.25 for k in DARK}, **{k: 1.4 for k in VDARK}},
     'zoom': {'hr3_dancefloor': 1.36, 'hr22_trailer_20th': 1.34, 'hr22_nora': 1.55, 'hr3_iamtheway': 1.36, 'hr3_bad_dreams': 1.36, 'hr10_judge4k': 1.2, 'hr10_hell4k': 1.2}}  # 4:3 pillarbox filled; Boxoffice corner bug cropped
json.dump(P, open(D + 'edl.json', 'w'), indent=1)
print(len(X), 'sections')
