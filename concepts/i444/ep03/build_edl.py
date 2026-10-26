# EP03 Every Ghostface Ranked: builds edl_full.json (cold open, rules, #16..#1, outro); every cut anchored to a narration word
# render: python ../ep01/render.py edl_full.json <clips_dir> voice <music.mp3> <out.mp4>
import json, re, os
V = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voice') + '/'
LEAD = 0.08
def at(seg, word):
    a = json.load(open(V + seg + '.json')); t = ''.join(a['characters'])
    i = t.find(word) if word[0].islower() or ' ' in word else t.rfind(word); assert i >= 0, (seg, word)
    return round(a['character_start_times_seconds'][i], 2)
def words(seg):
    a = json.load(open(V + seg + '.json')); t = ''.join(a['characters']); st = a['character_start_times_seconds']
    return [(st[m.start()], m.start() == 0 or t[m.start() - 2] in '.,?!:') for m in re.finditer(r"\S+", t)]
def snap(seg, t):
    W = words(seg); ph = [w for w, p in W if p and abs(w - t) <= 0.6]
    return round(max(0, min(ph or [w for w, _ in W], key=lambda w: abs(w - t)) - LEAD), 3)
def T(seg, x):
    if isinstance(x, str): return round(max(0, at(seg, x) - LEAD), 3)
    return x if x in (0, 999) else snap(seg, x)
def sec(voice, shots, rank=None, rate=None, instr=None, extra=(), pad=0.7, clip_db=-99):
    shots = [[T(voice, s[0]), *s[1:]] for s in shots]
    S = {'voice': voice, 'pad': pad, 'clip_audio_db': clip_db, 'shots': shots, 'overlays': []}
    if rank: S['overlays'].append(['rank', rank, 0.0, 2.9])
    if rate is not None:
        to, ti = T(voice, 'Survival rate'), T(voice, 'Instruction')
        S['overlays'] += [['odds', rate, to, ti - 0.04], ['instr', instr, ti, 999]]
    S['overlays'] += [[k, v, T(voice, a), T(voice, b)] for k, v, a, b in extra]
    return S
X = []
# cold open: frame 0 = the mask; one shot per way Ghostface has gone down
X.append(sec('s00', [(0, 's1_12_tables', 117), ('shot,', 's5_09_fighting', 139), ('stabbed', 's1_11_creative', 99), ('set on fire', 's5_09_fighting', 145),
  ('crushed', 's1_12_tables', 108), ('run over', 's7_04_walls', 229.5), ('and somehow', 's1_01_like_scary', 6), ('phone still', 's6_core4', 33),
  ('because Ghostface', 's7_06_spree', 219), ('one guy', 's5_08_act3', 24), ('There have', 's1_10_surprise', 60), ('sixteen', 's3_11_family', 66),
  ('people behind', 's5_09_fighting', 51), ('that mask', 's6_family', 13), ('so today', 's2_10_blame', 5), ('ranking every', 's7_09_anna_camp', 100),
  ('from the Ghostface', 's6_opening', 159), ('walk away', 's6_opening', 30), ('to the one', 's3_11_family', 75), ('really,', 's1_01_like_scary', 60),
  ('calling your', 's1_01_like_scary', 90)],
  extra=[('word', 'Shot', 'shot,', 'stabbed'), ('word', 'Stabbed', 'stabbed', 'set on fire'), ('word', 'Set on fire', 'set on fire', 'crushed'),
         ('word', 'Crushed by a TV', 'crushed', 'run over'), ('word', 'Run over by a car', 'run over', 'and somehow'),
         ('title', ['16 GHOSTFACES'], 'sixteen', 'so today')], pad=0.5, clip_db=-20))
X.append(sec('s01', [(0, 's6_core4', 3), ('not ranking', 's5_08_act3', 26), ('coolest', 's6_core4', 24), ('whose movie', 's4_still_gf', 0),
  ("we're ranking how", 's1_10_surprise', 87), ('many people', 's5_03_sheriff', 150), ('how close', 's6_core4', 89), ('how smart', 's7_02_stu', 66),
  ('how strong', 's7_06_spree', 222), ('put down', 's3_11_family', 24), ('And for every', 's6_two_gf', 138), ('your survival', 's1_01_like_scary', 30),
  ('Unlike Michael', 's6_opening', 282), ('every one of these', 's5_09_fighting', 90), ('ended up', 's1_12_tables', 0), ('so your odds', 's2_10_blame', 99),
  ('at least', 's3_11_family', 63)],
  extra=[('title', ['HOW HARD', '!TO SURVIVE'], "we're ranking how", 'based on'), ('title', ['SURVIVAL RATE'], 'your survival', 'Unlike Michael'),
         ('title', ['ALL HUMAN'], 'is human', 'and every one of them')], pad=0.5))
X.append(sec('s02', [(0, 's6_opening', 3), ('from Scream', 's6_opening', 9), ('He shows up', 's6_opening', 30), ('kills his', 's6_opening', 48),
  ('and acts like', 's6_opening', 99), ('new face', 's6_opening', 168), ('until he gets', 's6_opening', 18), ('finds out', 's6_opening', 273),
  ('real Ghostface', 's6_opening', 279), ('whole time', 's6_opening', 288), ('He was the', 's6_opening', 297), ('five minutes', 's6_opening', 283.5),
  ('somebody scarier', 's6_opening', 291), ('Survival rate', 's6_opening', 186), ('Instruction', 's6_opening', 189)],
  [16, 'Jason Carvey', 'Scream VI (2023)'], 85, "Check who's already in the apartment."))
X.append(sec('s03', [(0, 's7_09_anna_camp', 21), ('from Scream', 's7_09_anna_camp', 24), ("He's big", 's7_09_anna_camp', 33), ('scary in', 's7_04_walls', 192),
  ('escaped', 's7_09_anna_camp', 156), ('used as', 's7_09_anna_camp', 0), ('people really', 's7_09_anna_camp', 99), ('his run', 's7_04_walls', 222),
  ('Gale,', 's7_04_walls', 227), ('hit him', 's7_04_walls', 230.5), ('Survival rate', 's7_04_walls', 243), ('Instruction', 's7_04_walls', 246)],
  [15, 'Karl Gibbs', 'Scream 7 (2026)'], 75, 'Stay near the people with the car keys.'))
X.append(sec('s04', [(0, 's2_10_blame', 122.45), ("Billy's mom", 's1_11_creative', 6), ('who spent', 's2_10_blame', 106), ('friendly reporter', 's2_10_blame', 120),
  ('Her plan', 's2_10_blame', 115), ('but up close', 's2_10_blame', 60), ('least dangerous', 's2_10_blame', 70), ('once Cotton', 's2_10_blame', 117),
  ('with a gun', 's2_10_blame', 123), ('it was over', 's2_10_blame', 107), ('Survival rate', 's2_10_blame', 116), ('Instruction', 's2_10_blame', 121)],
  [14, 'Mrs. Loomis', 'Scream 2 (1997)'], 68, "Never trust a reporter who's a little too nice."))
X.append(sec('s05', [(0, 's4_still_charlie', 0), ('the horror nerd', 's4_02_return', 60), ('every rule', 's4_still_trio', 0), ('He pulled', 's4_02_return', 66),
  ('kills,', 's4_02_return', 75), ('trusted', 's4_02_return', 120), ('and Jill', 's4_still_jill', 0), ('through the heart', 's4_02_return', 125.5),
  ('Survival rate', 's4_still_charlie', 2), ('Instruction', 's4_still_gf', 0)],
  [13, 'Charlie Walker', 'Scream 4 (2011)'], 60, 'If he quizzes you on horror movies, leave.'))
X.append(sec('s06', [(0, 's6_family', 29.45), ('She faked', 's6_core4', 89), ('everyone stopped', 's6_core4', 54), ('genuinely evil', 's6_family', 46.7),
  ('one confirmed', 's6_core4', 117), ('Sam shot', 's6_family', 165), ('Survival rate', 's6_family', 13.5), ('Instruction', 's6_family', 168)],
  [12, 'Quinn Bailey', 'Scream VI (2023)'], 56, 'See the body before you believe it.'))
X.append(sec('s07', [(0, 's6_family', 86), ('the awkward', 's6_family', 18), ('just a little', 's6_family', 20), ('That closeness', 's6_family', 97),
  ('but in a straight', 's6_ladder', 150), ('lost to', 's6_ladder', 138), ('Kirby dropped', 's6_family', 141), ('very Scream', 's6_two_gf', 135),
  ('Survival rate', 's6_family', 20), ('Instruction', 's6_family', 142)],
  [11, 'Ethan Landry', 'Scream VI (2023)'], 53, 'Be suspicious of the nice roommate.'))
X.append(sec('s08', [(0, 's7_02_stu', 51), ('He worked', 's7_02_stu', 6), ('tech guy', 's7_02_stu', 48), ('faking calls', 's7_02_stu', 54),
  ('from Stu', 's7_02_stu', 66), ('with deepfakes', 's7_02_stu', 75), ('terrifying', 's7_02_stu', 63), ('final fight', 's7_10_sidney_kills', 15),
  ('Sidney shot', 's7_10_sidney_kills', 18), ('Survival rate', 's7_02_stu', 90), ('Instruction', 's7_02_stu', 105)],
  [10, 'Marco Davis', 'Scream 7 (2026)'], 50, "If a dead killer calls you, it's not him."))
X.append(sec('s09', [(0, 's5_08_act3', 73.0), ('the sweet', 's5_08_act3', 63), ('nobody suspected', 's5_08_act3', 78), ('He stabbed', 's5_03_sheriff', 135),
  ('broad daylight', 's5_03_sheriff', 141), ('fooled Sam', 's5_09_fighting', 3), ('but the moment', 's5_09_fighting', 92), ('she cut', 's5_09_fighting', 96),
  ('Survival rate', 's5_09_fighting', 0), ('Instruction', 's5_08_act3', 96), ('little too much', 's5_08_act3', 70)],
  [9, 'Richie Kirsch', 'Scream (2022)'], 45, 'If your boyfriend loves horror movies a little too much, ask questions.'))
X.append(sec('s10', [(0, 's7_09_anna_camp', 100), ("Sidney's neighbor", 's7_09_anna_camp', 3), ('actually running', 's7_09_anna_camp', 105),
  ('She was willing', 's7_09_anna_camp', 171), ('own family', 's7_09_anna_camp', 66), ('colder', 's7_09_anna_camp', 180),
  ('took Sidney', 's7_09_anna_camp', 255), ('shooting together', 's7_09_anna_camp', 266), ('Survival rate', 's7_09_anna_camp', 186),
  ('Instruction', 's7_09_anna_camp', 228)],
  [8, 'Jessica Bowden', 'Scream 7 (2026)'], 43, 'Know your neighbors better than they know you.'))
X.append(sec('s11', [(0, 's1_11_creative', 87.0), ('A lot of', 's1_10_surprise', 7), ('most unhinged', 's1_11_creative', 30), ('but he only', 's1_10_surprise', 112),
  ('Sidney ended', 's1_12_tables', 104), ('TV right', 's1_12_tables', 108.5), ('Stu might', 's1_11_creative', 89.5), ("but he's not", 's1_11_creative', 111),
  ('Survival rate', 's1_11_creative', 48), ('Instruction', 's1_12_tables', 45)],
  [7, 'Stu Macher', 'Scream (1996)'], 40, 'Keep a TV between you and him.',
  extra=[('title', ['NOT THE HARDEST', '!TO SURVIVE'], "but he's not", 'Survival rate')]))
X.append(sec('s12', [(0, 's2_10_blame', 3), ('the film', 's2_10_blame', 9), ('caught on', 's2_10_blame', 15), ('blame the', 's2_10_blame', 30),
  ('He racked', 's2_09_driving', 18), ('biggest body', 's2_09_driving', 21), ('framed Derek', 's2_10_blame', 36), ('when Gale', 's2_10_blame', 102),
  ('shot him', 's2_10_blame', 105), ('he still', 's2_10_blame', 54), ('finished him', 's2_10_blame', 78), ('Survival rate', 's2_10_blame', 33),
  ('Instruction', 's2_10_blame', 39)],
  [6, 'Mickey Altieri', 'Scream 2 (1997)'], 36, 'If he sits up, keep shooting.'))
X.append(sec('s13', [(0, 's5_09_fighting', 107.0), ('killed Dewey', 's5_09_fighting', 57), ('She got shot', 's5_09_fighting', 137), ('burning stove', 's5_09_fighting', 129),
  ('she still came', 's5_09_fighting', 145.5), ('swinging', 's5_09_fighting', 149), ('took Tara', 's5_09_fighting', 152.5), ('Survival rate', 's5_09_fighting', 70),
  ('Instruction', 's5_08_act3', 102)],
  [5, 'Amber Freeman', 'Scream (2022)'], 30, "If she's on fire and still walking, run."))
X.append(sec('s14', [(0, 's1_10_surprise', 0), ('the original', 's1_11_creative', 36), ('the one who', 's1_11_creative', 6), ("killing Sidney's", 's1_11_creative', 33),
  ('He was her', 's1_10_surprise', 19), ('he planned', 's1_11_creative', 72), ('played the', 's1_11_creative', 99.5), ("so he's", 's1_11_creative', 114),
  ("but he isn't", 's1_10_surprise', 39), ('three people', 's1_12_tables', 0), ('Survival rate', 's1_12_tables', 84), ('Instruction', 's1_12_tables', 90),
  ('check his', 's1_10_surprise', 63)],
  [4, 'Billy Loomis', 'Scream (1996)'], 25, 'If your boyfriend climbs through your window, check his pockets for a phone.'))
X.append(sec('s15', [(0, 's6_family', 0), ('He was the cop', 's6_family', 6), ('murders', 's6_subway', 30), ('which means', 's6_family', 3),
  ('coming for', 's6_two_gf', 120), ('whole family', 's6_family', 28), ('through the', 's6_core4', 120), ('until Sam', 's6_ladder', 176.5),
  ('Survival rate', 's6_family', 1), ('Instruction', 's6_family', 8)],
  [3, 'Detective Wayne Bailey', 'Scream VI (2023)'], 22, "Don't call the detective on this case."))
X.append(sec('s16', [(0, 's4_still_jill', 0), ("Sidney's own", 's4_still_trio', 0), ('She killed', 's4_02_return', 60), ('her mom', 's4_02_return', 69),
  ('even her partner', 's4_02_return', 120), ('then stabbed', 's4_still_jill_bed', 0), ('smashed', 's4_02_return', 78), ('play the', 's4_still_jill', 3),
  ('nearly got', 's4_06_killcam', 108), ('before Sidney', 's4_still_gf', 2), ('shot her', 's4_06_killcam', 15), ('Survival rate', 's4_still_jill_bed', 3),
  ('Instruction', 's4_still_jill', 6)],
  [2, 'Jill Roberts', 'Scream 4 (2011)'], 18, "If she's the last girl standing, look twice."))
X.append(sec('s17', [(0, 's3_11_family', 66), ('from Scream', 's3_11_family', 30), ("Sidney's half", 's3_11_family', 72), ('only Ghostface', 's3_11_family', 24),
  ('completely alone', 's3_11_family', 78), ('most kills', 's3_11_family', 40), ('claims', 's3_11_family', 84), ('pushed Billy', 's1_11_creative', 16),
  ('original murders', 's1_10_surprise', 66), ('bulletproof', 's3_11_family', 50), ('did nothing', 's3_11_family', 105), ('bullet to', 's3_11_family', 113),
  ('finally stop', 's3_11_family', 118), ('Survival rate', 's3_11_family', 88), ('Instruction', 's3_11_family', 120)],
  [1, 'Roman Bridger', 'Scream 3 (2000)'], 15, 'Aim for the head, every time.'))
X.append(sec('s18', [(0, 's5_08_act3', 27), ('from the guy', 's6_opening', 186), ('to the one', 's3_11_family', 91), ('Tell me', 's7_06_spree', 162),
  ('Freddy', 's4_still_gf', 4)], pad=1.5,
  extra=[('title', ['YOUR #1?'], 'Tell me', 'and if'), ('title', ['FREDDY', '!OR PINHEAD?'], 'Freddy', 999)]))
FILM = [('s1_', 'Scream (1996)'), ('s2_', 'Scream 2 (1997)'), ('s3_', 'Scream 3 (2000)'), ('s4_', 'Scream 4 (2011)'),
        ('s5_', 'Scream (2022)'), ('s6_', 'Scream VI (2023)'), ('s7_', 'Scream 7 (2026)')]
def film(n): return next((v for k, v in FILM if n.startswith(k)), None)
for S in X:
    runs = []
    for t, n, i, *_ in S['shots']:
        f = film(n)
        if runs and runs[-1][0] == f: continue
        runs.append([f, t])
    for k, (f, t) in enumerate(runs):
        if f: S['overlays'].append(['film', f, t, runs[k + 1][1] if k + 1 < len(runs) else 999])
DARK = ['s7_04_walls', 's7_06_spree', 's7_09_anna_camp', 's7_10_sidney_kills', 's6_subway', 's6_ladder', 's6_core4', 's6_two_gf', 's4_02_return', 's4_06_killcam']
P = {'sections': X,
     'zoom': {**{k: 1.0 for k in ['s4_still_jill', 's4_still_jill_bed', 's4_still_charlie', 's4_still_gf', 's4_still_trio']},
              **{k: 1.08 for k in ['s1_01_like_scary', 's1_10_surprise', 's1_11_creative', 's1_12_tables', 's2_09_driving', 's2_10_blame', 's3_11_family']}},
     'gamma': {k: 1.28 for k in DARK}}
json.dump(P, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'edl_full.json'), 'w'), indent=1)
print(len(X), 'sections')
