# EP07 Pinhead: builds edl.json for ../ep03/render_v2.py style rendering (render_hw.py) from voice/ (s00 cold open, s01 rules,
# s02..s11 = #10..#1, s12 outro). Cuts are anchored to whisper word onsets (voice/words.json); the % stamp is anchored to the
# ElevenLabs alignment (whisper drops some spoken numbers). Clip in-points were picked from the contact sheets (reveal_timestamps.md).
# Terrifier: no explicit gore frames, the gory trailer beats are skipped and the kills are cut on reactions.
import json, re, os
D = os.path.dirname(os.path.abspath(__file__)) + '/'
W = json.load(open(D + 'voice/words.json'))
ST = {e['sec']: e for e in json.load(open(D + 'stats.json'))['entries']}
LEAD = 0.08
def norm(s): return re.sub(r"[^a-z0-9']", '', s.lower())
def at(seg, phrase):
    ws = [norm(w[2]) for w in W[seg]]; ph = [norm(p) for p in phrase.split()]
    for i in range(len(ws) - len(ph) + 1):
        if ws[i:i + len(ph)] == ph: return W[seg][i][0]
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
def sec(voice, shots, card_at=None, extra=(), pad=0.5, clip_db=-99):
    shots = [[T(voice, s[0]), *s[1:]] for s in shots]
    S = {'voice': voice, 'pad': pad, 'clip_audio_db': clip_db, 'shots': shots, 'overlays': [], 'sfx': []}
    if voice in ST:
        e = ST[voice]; film = SHORT.get(voice, e['film'])
        S['overlays'].append(['rank', [e['rank'], e['villain'], film], 0.0, 2.9])
        S['pad'] = 0.9; a = T(voice, card_at); tp = round(num_onset(voice) - 0.05 - a, 3)
        S['overlays'].append(['stats', {'name': e['villain'].upper(), 'tile_png': f'tiles/{TILE[voice]}.png',
                                        'stats': dict(zip(['STRENGTH', 'INTELLIGENCE', 'KILL COUNT', 'NO MERCY'], e['v'])), 'pct': e['pct'],
                                        't_pct': tp, 'dur': round(vdur(voice) + S['pad'] - a, 3), 'film': film}, a, 999])
        S['sfx'] += [[a, SFX + 'whoosh.wav', SFX_GAIN['whoosh']], [a + 0.3, SFX + 'fill.wav', SFX_GAIN['fill']], [a + tp, SFX + 'stamp.wav', SFX_GAIN['stamp']]]
        S['card_at'] = a
    S['overlays'] += [[k, val, T(voice, x), T(voice, y)] for k, val, x, y in extra]
    return S
X = []
# EP07 v2 (owner 11/04): the cold open and every entry cut to victims being hurt (scout scans 11/04, gore allowed), each cut on its word
# with a caption; the stat card comes in ~3-5 s before "survival rate" so the kills play full frame; under the card the main figure sits
# left of x 840 (flip / dx shot options). Shot = (word, clip, in, -clean[, 'flip' | 'dx=..,z=..']).
X.append(sec('s00', [(0, 'hr1_jesuswept', 127.21, -2.0), ('tear', 'hr9_rev', 4106.4, -1.7), ('flesh', 'hr4_straighthell', 27.5, -1.4),
  ('your skin', 'hr2_finalbattle', 277.1, -2.0), ('peeled', 'hr9_rev', 3937.15, -2.5), ('alive', 'hr3_pillar', 100.0, -1.4),
  ('you get', 'hr2_channardtrans', 108.9, -1.4), ('cenobites', 'hr4_painface', 295.6, -2.7), ('trapped', 'hr5_torment', 548.65, -4.0),
  ('head forever', 'hr2_channardtrans', 257.13, -1.2), ('and he does', 'hr9_rev', 4115.2, -5.5), ('calmly', 'hr1_pack4k', 45.7, -5.9),
  ("we're ranking", 'still_posterwall', 0.0, -5.0)],
  extra=[('word', 'Hooked chains', 0, 'tear'), ('word', 'Tear', 'tear', 'flesh'), ('word', 'Through your flesh', 'flesh', 'your skin'),
         ('word', 'Your skin', 'your skin', 'peeled'), ('word', 'Peeled off', 'peeled', 'alive'), ('word', 'Alive', 'alive', 'you get'),
         ('word', 'Turned', 'you get', 'cenobites'), ('word', 'Cenobites', 'cenobites', 'trapped'), ('word', 'Trapped', 'trapped', 'head forever'),
         ('word', 'Inside your head', 'head forever', 'and he does'), ('word', 'All of it', 'and he does', 'calmly'),
         ('word', 'Calmly', 'calmly', "we're ranking")], clip_db=-20))
for ov in X[-1]['overlays']:  # captions flash and cut out: one word 0.9 s max, a phrase 1.5 s max (EP02 rule); the frame-0 caption holds to its cut
    if ov[0] == 'word' and ov[2] > 0: ov[3] = min(ov[3], ov[2] + (0.9 if ' ' not in ov[1] else 1.5))
s01_end = vdur('s01') + 0.5
X.append(sec('s01', [(0, 'hr1_pack4k', 62.4, -3.4), ('you just', 'hr1_pack4k', 10.5, -13.9), ("this movie's", 'hr1_pack4k', 81.55, -12.8),
  ('strength', 'hr4_chart', 60.25, -7.4), ('intelligence', 'hr2_legendary', 89.8, -6.1), ('kill count', 'hr7_returns', 75.6, -5.6),
  ('how little', 'hr3_pillar', 230.15, -3.9), ('which really', 'hr4_pathway', 152.3, -6.2), ('and that gives', 'hr2_desire', 101.9, -8.9),
  ('your survival', 'hr1_trailer_arrow2', 76.0, -5.7)]))
X[0]['vfade'] = {'out': 0.25}; X[-1]['vfade'] = {'in': 0.25}
X[-1]['overlays'].append(['stats', {'name': 'PINHEAD', 'tile_png': 'tiles/mystery.png', 'stats': {'STRENGTH': 6, 'INTELLIGENCE': 7,
  'KILL COUNT': 5, 'NO MERCY': 8}, 'pct': '??', 'dur': round(s01_end, 3), 't_pct': round(T('s01', 'survival rate') + LEAD, 3),
  'reveal': [round(T('s01', w) + LEAD, 3) for w in ('strength', 'intelligence', 'kill count', 'mercy')]}, 0.0, 999])
X[-1]['sfx'] = [[0.0, SFX + 'whoosh.wav', SFX_GAIN['whoosh']], [T('s01', 'survival rate') + LEAD, SFX + 'stamp.wav', SFX_GAIN['stamp']]]
# #11 Hellworld 80%
X.append(sec('s02', [(0, 'hr8_welcome', 66.2, -4.1), ('a group', 'hr8_trailer', 14.6, -0.85), ('themed party', 'hr8_trailer', 15.5, -0.75),
  ('and most', 'hr8_cop', 31.5, -2.2), ('set up by', 'hr8_welcome', 8.2, -6.4), ('two of them', 'hr8_cop', 43.4, -4.1),
  ('and when the real', 'hr8_welcome', 116.5, -3.9), ("he's not", 'hr8_welcome', 109.3, -1.2, 'z=1.35,dx=249'), ('he takes', 'hr8_welcome', 120.8, -3.6, 'flip'),
  ('survival rate', 'hr8_welcome', 66.2, -4.1, 'z=1.35,dx=249')], "he's not"))
# #10 Judgment 60%
X.append(sec('s03', [(0, 'hr10_hell4k', 370.2, -1.5), ('this time', 'hr10_souls', 27.0, -27.0), ('where an auditor', 'hr10_scifinow', 9.6, -4.2),
  ('and a jury', 'hr10_judge4k', 475.48, -2.4), ('your punishment', 'hr10_judge4k', 568.44, -3.4), ('and pinhead mostly', 'hr10_judge4k', 523.4, -4.8),
  ("if you're not", 'hr10_judge4k', 498.6, -4.3), ('and by the end', 'hr10_judge4k', 17.0, -4.3), ('survival rate', 'hr10_hell4k', 370.2, -1.5, 'z=1.45,dx=249')], 'and by the end'))
# #9 Hellbound 55%
X.append(sec('s04', [(0, 'hr2_legendary', 89.8, -6.1), ('pinhead is still', 'hr2_legendary', 53.4, -5.3), ('but this is', 'hr2_legendary', 50.15, -3.1),
  ('and he remembers', 'hr2_legendary', 64.45, -3.3), ('a moment later', 'hr2_channardtrans', 105.52, -3.3), ('a brand new', 'hr2_channardtrans', 110.32, -1.5),
  ('cuts through', 'hr2_legendary', 147.75, -1.5), ('whole crew', 'hr2_channardtrans', 242.7, -1.7), ('in seconds', 'hr2_channardtrans', 115.03, -2.5, 'z=1.35,dx=249'),
  ('and kirsty', 'hr2_legendary', 219.2, -1.0, 'flip'), ('walk out', 'hr2_legendary', 34.75, -4.6, 'z=1.35,dx=249'), ('survival rate', 'hr2_desire', 101.9, -8.9, 'z=1.35,dx=249')], 'in seconds'))
# #8 Revelations 50% (owner's 1080p Blu-ray, read directly, never committed)
X.append(sec('s05', [(0, 'hr9_rev', 3880.0, -1.5), ('with a different', 'hr9_rev', 3952.0, -1.9), ('two friends', 'hr9_rev', 2173.75, -1.7),
  ('on a trip', 'hr9_rev', 2183.6, -3.4), ('one gets', 'hr9_rev', 2199.4, -16.0), ('the other gets', 'hr9_rev', 3968.4, -1.4),
  ('and pinhead refuses', 'hr9_rev', 4048.0, -11.0), ('but he leaves', 'hr9_rev', 3966.84, -1.55), ('and emma', 'hr9_rev', 3982.6, -2.4, 'z=1.35,dx=249'),
  ('survival rate', 'hr9_rev', 3928.0, -3.0)], 'and emma'))
# #7 Hellraiser 1987 40%
X.append(sec('s06', [(0, 'hr1_pack4k', 122.9, -2.6), ('frank solves', 'hr1_pack4k', 10.5, -13.9), ('and the cenobites', 'hr1_pack4k', 6.5, -3.8),
  ('tear him', 'hr1_jesuswept', 124.25, -1.6), ('hook chains', 'hr1_jesuswept', 127.21, -2.0), ('so completely', 'hr1_jesuswept', 131.6, -11.0),
  ('kirsty survives', 'hr1_sights', 2.4, -7.2), ('by making', 'hr1_pack4k', 30.4, -4.0), ('and then reversing', 'hr1_dont', 0.05, -1.85),
  ('before they', 'hr1_dont', 6.95, -1.4), ('survival rate', 'hr1_pack4k', 45.7, -5.9, 'z=1.35,dx=249')], 'and then reversing'))
# #6 Hellseeker 35%
X.append(sec('s07', [(0, 'hr6_painpleasure', 186.4, -4.0), ('kirsty opens', 'hr6_pain', 204.9, -4.0), ('she offers', 'hr6_painpleasure', 180.6, -2.9),
  ('including', 'hr6_pain', 32.5, -3.0), ('it works', 'hr6_pain', 204.9, -4.0, 'z=1.35,dx=249'), ('five people', 'hr6_painpleasure', 186.4, -4.0, 'z=1.35,dx=249'),
  ('survival rate', 'hr6_painpleasure', 180.6, -2.9, 'z=1.35,dx=249')], 'it works'))
# #5 Hellraiser 2022, the Priest 30%
X.append(sec('s08', [(0, 'hr22_bridge', 2.6, -3.6), ('where pinhead', 'hr22_trailer_hulu', 97.5, -2.0), ('the box has', 'hr22_carousel', 498.0, -16.5),
  ('every single', 'hr22_carousel', 140.9, -8.6), ('a blood sacrifice', 'hr22_carousel', 264.0, -2.5), ("riley's brother", 'hr22_carousel', 256.3, -2.6),
  ('nora', 'hr22_trailer_20th', 95.9, -1.5), ('skinned alive', 'hr22_nora', 161.93, -2.3), ('and trevor', 'hr22_trailer_20th', 87.6, -1.8),
  ('final victim', 'hr22_cenofeat', 34.6, -1.2), ('riley and colin', 'hr22_bridge', 0.0, -2.5, 'z=1.35,dx=249'), ('but only', 'hr22_bridge', 33.0, -4.2, 'z=1.35,dx=249'),
  ('riley turns', 'hr22_bridge', 23.8, -6.4), ('survival rate', 'hr22_bridge', 2.6, -3.6)], 'riley and colin'))
# #4 Bloodline 25%
X.append(sec('s09', [(0, 'hr4_pathway', 152.3, -6.2), ('pinhead hunts', 'hr4_pathway', 99.5, -4.5), ('kills john', 'hr4_straighthell', 23.7, -1.7),
  ('in new york', 'hr4_straighthell', 27.5, -1.4), ('and wipes out', 'hr4_painface', 251.2, -1.45), ('crew on', 'hr4_painface', 276.35, -1.45),
  ('space station in', 'hr4_finalbattle', 92.7, -3.1), ('the year', 'hr4_painface', 295.6, -2.7), ('in the end', 'hr4_space', 48.2, -10.8),
  ('giant puzzle', 'hr4_another', 279.3, -2.0, 'z=1.35,dx=249'), ('survival rate', 'hr4_chart', 158.8, -4.9, 'flip=1,z=1.35,dx=249')], 'giant puzzle'))
# #3 Deader 15%
X.append(sec('s10', [(0, 'hr7_returns', 89.2, -4.4), ('a reporter', 'hr7_real', 20.2, -5.9), ('that kills', 'hr7_afraid', 146.2, -1.4),
  ('all because', 'hr7_afraid', 4.55, -3.5), ('when amy', 'hr7_returns', 10.55, -5.4), ('pinhead slaughters', 'hr7_returns', 175.6, -1.55),
  ('the entire cult', 'hr7_returns', 166.2, -1.35), ('in minutes', 'hr7_returns', 142.5, -1.6), ('and he tells', 'hr7_returns', 189.1, -4.0),
  ("amy's only", 'hr7_returns', 119.1, -2.5, 'z=1.35,dx=249'), ('survival rate', 'hr7_returns', 89.2, -4.4, 'flip=1,z=1.35,dx=249')], "amy's only"))
# #2 Inferno 8%
X.append(sec('s11', [(0, 'hr5_box', 266.2, -1.7), ('detective', 'hr5_world', 50.9, -20.9), ('opens the box', 'hr5_box', 27.1, -4.0),
  ('and spends', 'hr5_cruelty', 33.5, -13.0), ('until he learns', 'hr5_child', 97.1, -2.3), ('pinhead the entire', 'hr5_box', 266.2, -1.7),
  ("and he's already", 'hr5_torment', 425.1, -12.2), ("there's no fight", 'hr5_torment', 420.85, -1.8), ('no deal', 'hr5_torment', 548.65, -4.0, 'z=1.35,dx=249'),
  ('just an eternity', 'hr5_torment', 430.0, -7.0, 'z=1.35,dx=249'), ('survival rate', 'hr5_box', 266.2, -1.7, 'z=1.35,dx=249')], 'no deal'))
# #1 Hell on Earth 5%
X.append(sec('s12', [(0, 'hr3_iamtheway', 131.0, -1.8), ('pinhead breaks', 'hr3_pillar', 128.0, -7.8), ('with no box', 'hr3_pillar', 230.15, -3.9),
  ('massacres', 'hr3_club', 124.8, -1.9), ('entire nightclub', 'hr3_dancefloor', 60.0, -1.2), ('kills the police', 'hr3_club', 108.3, -0.6),
  ('and turns his', 'hr3_iamtheway', 95.5, -4.0), ('only joey', 'hr3_iamtheway', 129.3, -1.25), ('turned into', 'hr3_iamtheway', 127.95, -2.9),
  ('can send', 'hr3_unstoppable', 106.5, -1.6), ("if he's the one", 'hr3_iamtheway', 9.6, -3.3), ('survival rate', 'hr3_pillar', 224.35, -3.1, 'z=1.35,dx=249')], "if he's the one"))
X.append(sec('s13', [(0, 'hr1_pack4k', 62.4, -3.4), ('to a demon', 'hr3_pillar', 230.15, -3.9), ('tell me', 'hr1_pack4k', 10.5, -13.9),
  ('and remember', 'hr4_pathway', 172.0, -11.0)], pad=2.5,
  extra=[('title', ['WHICH BOX', '!WOULD YOU OPEN?'], 'tell me', 'and remember'), ('title', ['SOME DOORS', '!STAY CLOSED'], 'and remember', 999)]))
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
DARK = ['hr22_nora', 'hr5_torment', 'hr8_welcome', 'hr8_jake', 'hr8_cop', 'hr10_souls', 'hr22_carousel', 'hr3_pillar', 'hr5_box', 'hr5_cruelty', 'hr7_returns', 'hr7_afraid', 'hr9_trailer_rt']
P = {'sections': X, 'tiers': TIERS, 'gamma': {k: 1.25 for k in DARK},
     'zoom': {'hr3_dancefloor': 1.36, 'hr22_trailer_20th': 1.34, 'hr22_nora': 1.55, 'hr3_iamtheway': 1.36, 'hr3_bad_dreams': 1.36, 'hr10_judge4k': 1.2, 'hr10_hell4k': 1.2}}  # 4:3 pillarbox filled; Boxoffice corner bug cropped
json.dump(P, open(D + 'edl.json', 'w'), indent=1)
print(len(X), 'sections')
