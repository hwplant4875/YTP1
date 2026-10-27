# EP03 v2 Every Ghostface Ranked: builds edl_v2.json from voice_v3 (cold open, rules, #16..#1, outro)
# Cuts are anchored to whisper word onsets (voice_v3/words.json; the ElevenLabs alignment drifts up to 0.7 s near pauses).
# Every action word in the cold open lands on the frame where it happens (checked at 10 fps on the 360p copies).
# Each entry: rank card, then the survival-rate card (4 bars, then the % stamps as the number is spoken) to the end of the entry.
# User 10/26 14:18: the tier list (board, tier lines, final board) is gone; the survival-rate card is the main graphic.
# render: python render_v2.py edl_v2.json <clips_dir> voice_v3 <music.mp3> <out.mp4>
import json, re, os
D = os.path.dirname(os.path.abspath(__file__)) + '/'
W = json.load(open(D + 'voice_v3/words.json'))
LEAD = 0.08
def norm(s): return re.sub(r"[^a-z0-9']", '', s.lower())
def at(seg, phrase):  # onset of the first word of phrase (whisper spelling) in seg
    ws = [norm(w[2]) for w in W[seg]]; ph = [norm(p) for p in phrase.split()]
    for i in range(len(ws) - len(ph) + 1):
        if ws[i:i + len(ph)] == ph: return W[seg][i][0]
    raise KeyError((seg, phrase))
def T(seg, x): return x if isinstance(x, (int, float)) else round(max(0, at(seg, x) - LEAD), 3)
def vdur(seg): return round(json.load(open(D + f'voice_v3/{seg}.json'))['character_end_times_seconds'][-1], 3)
def num_onset(seg):  # the spoken % right after "Survival rate"
    ws = W[seg]; i = max(k for k, w in enumerate(ws) if norm(w[2]) == 'survival'); return ws[i + 2][0]
STATS = json.load(open(D + 'stats_v2.json')) if os.path.exists(D + 'stats_v2.json') else {}
KS = {r['key']: r for r in STATS.get('killers', [])} if isinstance(STATS.get('killers'), list) else STATS.get('killers', {})
PCT = {'carvey': 99, 'karl': 75, 'mrs_loomis': 68, 'charlie': 60, 'quinn': 56, 'ethan': 53, 'marco': 50, 'richie': 45,
       'jessica': 43, 'stu': 40, 'mickey': 36, 'amber': 30, 'billy': 25, 'wayne': 22, 'jill': 18, 'roman': 10}
NAME = {'carvey': 'Jason Carvey', 'karl': 'Karl Gibbs', 'mrs_loomis': 'Mrs. Loomis', 'charlie': 'Charlie Walker', 'quinn': 'Quinn Bailey',
        'ethan': 'Ethan Landry', 'marco': 'Marco Davis', 'richie': 'Richie Kirsch', 'jessica': 'Jessica Bowden', 'stu': 'Stu Macher',
        'mickey': 'Mickey Altieri', 'amber': 'Amber Freeman', 'billy': 'Billy Loomis', 'wayne': 'Wayne Bailey', 'jill': 'Jill Roberts',
        'roman': 'Roman Bridger'}
def short(k): return 'MRS. LOOMIS' if k == 'mrs_loomis' else NAME[k].split()[-1 if k == 'carvey' else 0].upper()
def film_of(k): return KS.get(k, {}).get('film', '')
def stats(k):
    s = KS.get(k, {})
    return {n: s.get(f, 5) for n, f in (('STRENGTH', 'strength'), ('INTELLIGENCE', 'intelligence'), ('KILL COUNT', 'kill_count'),
                                       ('DECEPTION', 'deception'))}
# survival tiers (user 10/26 15:19: the card shows the tier name in its TierMaker colour; the % takes that colour too)
TIERS = [['S', 'Slaughtered', 25], ['A', 'Almost Dead', 40], ['B', 'Better Run', 50], ['C', 'Close Call', 60], ['D', "Don't Worry", 80],
         ['E', 'Easy', 101]]
SFX_GAIN = {'whoosh': -16, 'fill': -20, 'stamp': -12, 'slam': -6}
def sec(voice, shots, rank=None, key=None, card_at=None, extra=(), pad=0.5, clip_db=-99):
    shots = [[T(voice, s[0]), *s[1:]] for s in shots]
    S = {'voice': voice, 'pad': pad, 'clip_audio_db': clip_db, 'shots': shots, 'overlays': [], 'sfx': []}
    if rank: S['overlays'].append(['rank', rank, 0.0, 2.9])
    if key:  # survival-rate card from card_at (after the death beat) to the end of the entry (voice + pad)
        S['pad'] = 0.9; a = T(voice, card_at); tp = round(num_onset(voice) - 0.05 - a, 3)
        S['overlays'].append(['stats', {'name': NAME[key].upper(), 'tile_png': f'tiles/{key}.png', 'stats': stats(key), 'pct': PCT[key],
                                        't_pct': tp, 'dur': round(vdur(voice) + S['pad'] - a, 3), 'film': film_of(key)}, a, 999])
        # a soft whoosh as the card comes in, a soft fill under the bars, the stamp on the spoken %
        S['sfx'] += [[a, 'sfx/whoosh.wav', SFX_GAIN['whoosh']], [a + 0.3, 'sfx/fill.wav', SFX_GAIN['fill']],
                     [a + tp, 'sfx/stamp.wav', SFX_GAIN['stamp']]]
        S['card_at'] = a
    S['overlays'] += [[k, val, T(voice, x), T(voice, y)] for k, val, x, y in extra]
    return S
X = []
# cold open: frame 0 = the mask; every way Ghostface has gone down lands on its word (shot / stabbed / fire / car / head)
X.append(sec('s00', [(0, 's7_01_animatronic', 178.25), ('shot', 's7_10_sidney_kills', 139.92), ('stabbed', 's5_10_daughter', 103.75),
  ('set on', 's5_09_fighting', 144.78, 0.85), ('run over', 's7_04_walls', 232.3, 0.6), ('shot in', 's6_family', 172.95, 0.7),
  ('and somehow', 's1_01_like_scary', 6), ('phone still', 's6_core4', 34.4), ('because', 's7_06_spree', 219.0, 0.95),
  ('one guy', 's5_08_act3', 24), ('there have', 's1_10_surprise', 60), ('16 different', 's3_11_family', 65.3),
  ('people behind', 's5_09_fighting', 51), ('that mask', 's7_07_hunted', 132.0), ('and today', 's2_10_blame', 9.0),
  ('ranking every', 's7_09_anna_camp', 100)],
  extra=[('word', 'Shot', 'shot', 'stabbed'), ('word', 'Stabbed', 'stabbed', 'set on'), ('word', 'Set on fire', 'set on', 'run over'),
         ('word', 'Run over by a car', 'run over', 'shot in'), ('word', 'Shot in the head', 'shot in', 'and somehow'),
         ('title', ['16 GHOSTFACES'], '16 different', 'and today')], clip_db=-20))
# rules: the stat card demo fills one bar per spoken stat, then "??%" on "survival rate"
s01_card = 0.0  # user 10/27 08:08: the ground-rules intro lines are cut; the card is up from the first frame of s01
X.append(sec('s01', [(0, 's6_core4', 23.4), ('strength', 's2_03_omega', 115.25),
  ('intelligence', 's3_11_family', 73.6), ('kill count', 's5_03_sheriff', 153.25), ('deception', 's1_10_surprise', 27.5),
  ('which is basically', 's1_09_look_behind', 83.4), ('before you figured', 's5_09_fighting', 100), ('put it all', 's7_04_walls', 53),
  ('your survival', 's1_01_like_scary', 30), ('unlike michael', 's6_opening', 282), ('michael', 'h20_final_confrontation', 93.3), ('jason', 'p6_reborn', 123.5), ('every one of these', 's5_09_fighting', 90.2),
  ('ended up dead', 's5_10_daughter', 159.3), ('so your odds', 's2_10_blame', 99.4), ('at least', 's3_11_family', 63)],
  extra=[('title', ['ALL HUMAN'], 'human', 'and every one')]))
X[-1]['overlays'].append(['stats', {'name': 'GHOSTFACE', 'tile_png': 'tiles/mystery.png', 'stats': {'STRENGTH': 6, 'INTELLIGENCE': 7,
  'KILL COUNT': 5, 'DECEPTION': 8}, 'pct': '??', 'dur': round(T('s01', 'unlike michael') - s01_card, 3),
  't_pct': round(T('s01', 'survival rate') + LEAD - s01_card, 3),
  'reveal': [round(T('s01', w) + LEAD - s01_card, 3) for w in ('strength', 'intelligence', 'kill count', 'deception')]},
  s01_card, T('s01', 'unlike michael')])
X[-1]['sfx'] = [[s01_card, 'sfx/whoosh.wav', SFX_GAIN['whoosh']], [T('s01', 'survival rate') + LEAD, 'sfx/stamp.wav', SFX_GAIN['stamp']]]
X.append(sec('s02', [(0, 's6_opening', 3.3), ('from scream', 's6_opening', 9), ('he shows up', 's6_opening', 30), ('kills his', 's6_opening', 11.7),
  ('and acts like', 's6_opening', 99), ('new face', 's6_opening', 168), ('until he gets', 's6_opening', 18), ('finds out', 's6_opening', 273.4),
  ('real ghostface', 's6_opening', 278.75), ('whole time', 's6_opening', 288.5), ('he was the ghostface', 's6_opening', 296),
  ('5 minutes', 's6_opening', 284.2), ('somebody scarier', 's6_opening', 298.3, 0.75), ('survival rate', 's6_opening', 186, 0.75)],
  [16, 'Jason Carvey', 'Scream VI (2023)'], 'carvey', 'took the job'))
X.append(sec('s03', [(0, 's7_04_walls', 52.5), ('from scream', 's7_04_walls', 107.5), ('an escaped', 's7_04_walls', 190.0),
  ('genuinely scary', 's7_04_walls', 219.2), ('but he was really', 's7_09_anna_camp', 0), ('for the people', 's7_09_anna_camp', 194.0),
  ('and his run', 's7_04_walls', 192.5), ('floored it', 's7_04_walls', 232.85), ('and hit him', 's7_04_walls', 232.28, 0.8),
  ('once they pulled', 's7_still_karl_unmasked', 0), ('the creepy stranger', 's7_still_karl_coffee', 0), ('survival rate', 's7_04_walls', 234.1, 0.9)],
  [15, 'Karl Gibbs', 'Scream 7 (2026)'], 'karl', 19.4))
X.append(sec('s04', [(0, 's2_11_mothers_love', 85.3), ("billy's mom", 's1_11_creative', 99.75), ('who spent', 's2_11_mothers_love', 19.3),
  ('friendly reporter', 's2_11_mothers_love', 41.3), ('her plan', 's2_11_mothers_love', 66.25), ('honestly', 's2_11_mothers_love', 32.0),
  ('but up close', 's2_11_mothers_love', 75.85, 0.9), ('the least', 's2_11_mothers_love', 96.0), ('once cotton', 's2_12_intense', 110.0), ('it was over', 's2_12_intense', 107.9),
  ('survival rate', 's2_12_intense', 113.5)],
  [14, 'Mrs. Loomis', 'Scream 2 (1997)'], 'mrs_loomis', 18.0))
X.append(sec('s05', [(0, 's4_still_charlie_close', 0), ('every rule', 's4_still_trio', 0),
  ('he did most', 's4_02_return', 124.3), ('but the guy', 's4_still_charlie_close', 0),
  ('the wrong partner', 's4_still_jill', 0), ('and jill', 'scream4_reveal', 19.6), ('the second she', 's4_still_gf_knife', 0),
  (12.3, 's4_still_charlie_party', 0)],
  [13, 'Charlie Walker', 'Scream 4 (2011)'], 'charlie', 12.3))
X.append(sec('s06', [(0, 's6_family', 120.5, 0.54), ('she faked', 's6_core4', 89), ('everyone stopped', 's6_core4', 54),
  ('genuinely evil', 's6_family', 98.4, 0.55), ('but she only', 's6_family', 101.85), ('one confirmed', 's6_core4', 116.5),
  ('sam shot', 's6_family', 172.78), ('survival rate', 's6_family', 171.65, 0.3)],
  [12, 'Quinn Bailey', 'Scream VI (2023)'], 'quinn', 12.8))
X.append(sec('s07', [(0, 's6_family', 85.77, 0.7), ('the awkward', 's6_subway', 159.25, 0.65), ('too close', 's6_family', 20.05),
  ('what makes him', 's6_family', 18.3), ('but once the mask', 's6_family', 140.75), ('terra put', 's6_family', 147.5),
  ('and again', 's6_family', 158.0, 0.6), ('and that was', 's6_family', 151.7, 0.5), ('survival rate', 's6_family', 85.77, 0.78)],
  [11, 'Ethan Landry', 'Scream VI (2023)'], 'ethan', 15.9))
X.append(sec('s08', [(0, 's7_09_anna_camp', 20.0), ('he worked', 's7_02_stu', 6), ('tech guy', 's7_09_anna_camp', 32.0, 0.76), ('faking calls', 's7_02_stu', 54),
  ('from stu', 's7_02_stu', 70.4), ('with deepfakes', 's7_02_stu', 75), ('terrifying', 's7_02_stu', 63),
  ('but when it came', 's7_09_anna_camp', 232.0), ('sydney shot', 's7_09_anna_camp', 254.2), ('survival rate', 's7_09_anna_camp', 23.0)],
  [10, 'Marco Davis', 'Scream 7 (2026)'], 'marco', 15.0))
X.append(sec('s09', [(0, 's5_08_act3', 73.0, 0.85), ('the sweet', 's5_09_fighting', 90.2), ('way too harmless', 's5_09_fighting', 97.2),
  ('but his crew', 's5_03_sheriff', 141.4), ('in broad', 's5_03_sheriff', 145.7),
  ('fooled sam', 's5_09_fighting', 36.15, 0.8), ('and the moment', 's5_09_fighting', 92), ('she stabbed', 's5_10_daughter', 80.15),
  ('over and over', 's5_10_daughter', 100.0), ('until he finally', 's5_10_daughter', 107.3, 0.6)],
  [9, 'Richie Kirsch', 'Scream (2022)'], 'richie', 16.4))
X.append(sec('s10', [(0, 's7_09_anna_camp', 100), ("sydney's neighbor", 's7_09_anna_camp', 4.45), ('actually running', 's7_09_anna_camp', 8.0),
  ('she was willing', 's7_09_anna_camp', 171), ('own family', 's7_09_anna_camp', 66), ('colder', 's7_09_anna_camp', 180),
  ('and it took', 's7_09_anna_camp', 267.2), ('shooting together', 's7_10_sidney_kills', 141.25), ('to stop her', 's7_10_sidney_kills', 140.0),
  ('survival rate', 's7_09_anna_camp', 186)],
  [8, 'Jessica Bowden', 'Scream 7 (2026)'], 'jessica', 16.4))
X.append(sec('s11', [(0, 's1_10_surprise', 8.5), ('most unhinged', 's1_10_surprise', 112.4),
  ('but he was really', 's1_11_creative', 56.4), ("billy's sidekick", 's1_11_creative', 80.3), ('he was so', 's1_11_creative', 87), ('he and billy', 's1_11_creative', 101.0),
  ('each other', 's1_11_creative', 113.375, 0.75), ('survival rate', 's1_12_tables', 45)],
  [7, 'Stu Macher', 'Scream (1996)'], 'stu', 16.4))
X.append(sec('s12', [(0, 's2_10_blame', 9.0), ('the film', 's2_10_blame', 14.4), ('so he could', 's2_10_blame', 30),
  ('he racked', 's2_09_driving', 18), ('body counts', 's2_07_big_boys', 125.75), ('and even framed', 's2_10_blame', 83.75),
  ('framed derek', 's2_10_blame', 99.4), ('but he never', 's2_10_blame', 3.5), ('because his own', 's2_10_blame', 122.6, 0.8),
  ('shot him', 's2_11_mothers_love', 6.0), ('the second he', 's2_11_mothers_love', 3.85), ('survival rate', 's2_10_blame', 16.3)],
  [6, 'Mickey Altieri', 'Scream 2 (1997)'], 'mickey', 18.4))
X.append(sec('s13', [(0, 's5_09_fighting', 107.0), ('killed dewey', 's5_09_fighting', 57), ('she got shot', 's5_09_fighting', 142.2),
  ('fell', 's5_09_fighting', 144.3), ('she still came', 's5_09_fighting', 147.95), ('out on fire', 's5_09_fighting', 152.06), ('swinging', 's5_10_daughter', 171.8, 0.65),
  ('it took tara', 's5_10_daughter', 177.45, 0.85), ('survival rate', 's5_09_fighting', 115.0, 0.6)],
  [5, 'Amber Freeman', 'Scream (2022)'], 'amber', 13.2))
X.append(sec('s14', [(0, 's1_10_surprise', 0), ('the original', 's1_11_creative', 36), ('the one who', 's1_11_creative', 7.25),
  ("killing sydney's", 's1_10_surprise', 27.6), ('he was her', 's1_10_surprise', 19), ('he planned', 's1_11_creative', 72),
  ('he played', 's1_11_creative', 99.5), ("so he's", 's1_11_creative', 114), ("but he isn't", 's1_10_surprise', 39),
  ('3 people', 's1_12_tables', 0), ('survival rate', 's1_12_tables', 86)],
  [4, 'Billy Loomis', 'Scream (1996)'], 'billy', 22.0))
X.append(sec('s15', [(0, 's6_family', 0, 0.8), ('he was the cop', 's6_sam_gf', 58), ('murders', 's6_subway', 30.8), ('which means', 's6_sam_gf', 66),
  ('and he led', 's6_family', 6.9), ('whole family', 's6_family', 17.9), ('through the bloodiest', 's6_store', 79.6), ('until sam', 's6_sam_gf', 164.8),
  ('survival rate', 's6_sam_gf', 68.9)],
  [3, 'Detective Wayne Bailey', 'Scream VI (2023)'], 'wayne', 16.5))
X.append(sec('s16', [(0, 's4_still_jill', 0), ("sydney's own", 'scream4_reveal', 4.75), ('the smile', 'scream4_reveal', 14.0),
  ('says everything', 'scream4_reveal', 19.5), ('she killed', 's4_02_return', 122.0), ('her mom', 's4_still_gf_knife', 0),
  ('even her', 's4_still_charlie_party', 0), ('then played', 's4_still_jill_hospital', 0), ('the whole town', 's4_06_killcam', 108),
  ('came closer', 's4_still_trio', 0), ('to stealing', 'scream4_reveal', 20.9, 0.9), ('for good', 's4_still_jill', 6)],
  [2, 'Jill Roberts', 'Scream 4 (2011)'], 'jill', 19.6))
X.append(sec('s17', [(0, 's3_11_family', 65.3, 0.8), (2.08, 's3_11_family', 50.2), ("sydney's half", 's3_11_family', 72),
  ('only ghostface', 's3_11_family', 24), ('completely alone', 's3_11_family', 78), ('most kills', 's3_02_cutting', 126.3),
  ('claims', 's3_11_family', 84), ('pushed billy', 's1_11_creative', 16), ('original murders', 's1_10_surprise', 66),
  ('even wore', 's3_12_firing', 27.0), ('bulletproof', 's3_12_firing', 26.0), ('so shooting', 's3_12_firing', 111.5), ('and it took', 's3_12_firing', 119.55), ('a bullet to', 's3_12_firing', 122.05), ('dewey', 's3_12_firing', 121.4),
  ('finally stop', 's3_12_firing', 129.95, 0.6), ('survival rate', 's3_11_family', 80)],
  [1, 'Roman Bridger', 'Scream 3 (2000)'], 'roman', 24.2))
# outro: the CTA over the mask footage
X.append(sec('s18', [(0, 's6_opening', 186), ('and if you', 's6_subway', 167, 0.65)], pad=2.5,
  extra=[('title', ['YOUR #1?'], 'tell me', 'and if you'), ('title', ['FREDDY', '!OR PINHEAD?'], 'freddie', 999)]))
FILM = [('h20_', 'Halloween H20 (1998)'), ('p6_', 'Jason Lives (1986)'), ('s1_', 'Scream (1996)'), ('s2_', 'Scream 2 (1997)'), ('s3_', 'Scream 3 (2000)'), ('s4_', 'Scream 4 (2011)'), ('scream4', 'Scream 4 (2011)'),
        ('s5_', 'Scream (2022)'), ('s6_', 'Scream VI (2023)'), ('s7_', 'Scream 7 (2026)')]
def film(n): return next((v for k, v in FILM if n.startswith(k)), None)
for S in X:  # film label per run of one film, gone once the stat card takes the frame
    end = S.pop('card_at', 999)
    runs = []
    for t, n, *_ in S['shots']:
        if t >= end: break
        f = film(n)
        if runs and runs[-1][0] == f: continue
        runs.append([f, t])
    for k, (f, t) in enumerate(runs):
        if f: S['overlays'].append(['film', f, t, min(end, runs[k + 1][1] if k + 1 < len(runs) else 999)])
DARK = ['s7_04_walls', 's7_06_spree', 's7_09_anna_camp', 's7_10_sidney_kills', 's6_subway', 's6_ladder', 's6_core4', 's6_two_gf', 's4_02_return',
        's4_06_killcam', 's3_12_firing']
P = {'sections': X, 'tiers': TIERS,
     'zoom': {**{k: 1.0 for k in ['s4_still_jill', 's4_still_jill_bed', 's4_still_charlie', 's4_still_gf', 's4_still_trio', 's4_still_charlie_party', 's4_still_charlie_close', 's4_still_gf_knife', 's4_still_jill_hospital', 's7_still_karl_unmasked', 's7_still_karl_coffee']},
              **{k: 1.08 for k in ['s1_01_like_scary', 's1_10_surprise', 's1_11_creative', 's1_12_tables', 's2_09_driving', 's2_10_blame',
                                   's2_11_mothers_love', 's2_12_intense', 's3_11_family', 's3_12_firing']}},
     'gamma': {k: 1.28 for k in DARK}}
json.dump(P, open(D + 'edl_v2.json', 'w'), indent=1)
print(len(X), 'sections;', 'stats from', 'stats_v2.json' if STATS else 'PLACEHOLDER 5s')
