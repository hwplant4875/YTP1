# EP02 Jason Voorhees: builds edl_full.json (intro, rules, #11..#1 with Part V bonus and mid-roll, outro)
# render: python ../ep01/render.py edl_full.json <clips_dir> <voice_v2_dir> <music.mp3> <out.mp4>
import json, re
V = '/mnt/project-files/instruction444/ep02_jason_ranked/voice_v2/'
def at(seg, word):
    a = json.load(open(V + seg + '.json')); t = ''.join(a['characters']); i = t.rfind(word); assert i >= 0, (seg, word)
    return round(a['character_start_times_seconds'][i], 2)
def sec(voice, shots, rank=None, rate=None, instr=None, extra=(), pad=0.7, clip_db=-99):
    S = {'voice': voice, 'pad': pad, 'clip_audio_db': clip_db, 'shots': [list(s) for s in shots], 'overlays': []}
    if rank: S['overlays'].append(['rank', rank, 0.0, 2.9])
    if rate is not None:
        to, ti = at(voice, 'Survival rate'), at(voice, 'Instruction')
        S['overlays'] += [['odds', rate, to, ti - 0.08], ['instr', instr, ti, 999]]
    S['overlays'] += [list(e) for e in extra]
    return S
X = []
# cold open: frame 0 = Jason's face; one word per way he has been "killed"
X.append(sec('s00', [(0, 'p6_scenepack', 69), (0.56, 'p4_tricking_jason', 122.5), (1.28, 'p3_trailer', 109.55), (2.04, 'r09_scenepack', 465),
  (2.96, 'p7_vs_tina', 102), (3.92, 'p9_opening_hd', 141), (5.28, 'jx_trailer', 48), (6.9, 'jx_uber_scenepack', 12), (8.28, 'jx_ending', 150), (9.73, 'p6_scenepack', 30),
  (11.83, 'p1_mrs_voorhees', 17), (13.73, 'p1_mrs_voorhees', 27), (16.13, 'p1_mrs_voorhees', 50), (17.53, 'p3_chris_escape', 33),
  (18.53, 'p6_scenepack', 108), (19.53, 'p8_vs_newyork', 6), (20.53, 'jx_uber_scenepack', 9), (21.83, 'p7_vs_tina', 204),
  (23.83, 'fvj_scenepack', 27), (24.73, 'p2_final_scene', 165), (25.33, 'jx_uber_scenepack', 132), (27.43, 'BLACK', 0)],
  extra=[('word', 'Hacked', 0.56, 1.22), ('word', 'Hanged', 1.28, 1.98), ('word', 'Drowned', 2.04, 2.9), ('word', 'Electrocuted', 2.96, 3.86),
         ('word', 'Blown to pieces', 3.92, 5.2), ('word', 'Frozen', 5.28, 6.85), ('word', 'Umm...', 7.2, 8.2), ('word', 'Thrown into space?', 8.28, 9.6),
         ('title', ['IT WAS HIS MOTHER'], 16.13, 17.43), ('title', ['11 JASONS'], 20.53, 21.73), ('title', ['INSTRUCTION', '!444'], 27.53, 30.53)],
  pad=0.5, clip_db=-20))
X.append(sec('s01', [(0, 'p3_gets_mask', 246), (1.6, 'p8_trailer', 57), (3.0, 'p6_scenepack', 120), (5.0, 'r09_scenepack', 81),
  (7.4, 'p7_vs_tina', 165), (8.8, 'fvj_scenepack', 180), (10.1, 'jx_uber_scenepack', 60)],
  extra=[('title', ['NOT THE BEST MOVIE'], 1.6, 2.9), ('title', ['THE HARDEST', '!TO KILL'], 3.0, 4.9), ('odds', '??', at('s01', 'survival rate'), 999)], pad=0.5))
X.append(sec('s02', [(0, 'p2_still_window', 0), (3.8, 'p2_still_sack', 0), (7.0, 'p2_final_scene', 39), (9.4, 'p2_final_scene', 168),
  (11.0, 'p2_final_scene', 174), (12.2, 'p2_trailer', 93), (14.1, 'p2_final_scene', 99), (15.6, 'p2_trailer', 121.2), (17.1, 'p2_final_scene', 171),
  (18.2, 'p2_final_scene', 236), (20.8, 'p2_final_scene', 180)],
  [11, 'Friday the 13th Part 2', 1981], 90, 'Pretend to be his mom.'))
X.append(sec('s03', [(0, 'r09_scenepack', 81), (2.5, 'r09_scenepack', 135), (3.9, 'r09_scenepack', 84), (5.4, 'r09_final_death', 81),
  (7.6, 'r09_scenepack', 279), (10.2, 'r09_final_death', 186), (12.0, 'r09_final_death', 189), (13.8, 'r09_final_death', 236),
  (15.4, 'r09_final_death', 258), (18.0, 'r09_scenepack', 468)],
  [10, 'Friday the 13th', 2009], 82, "Don't hide in the tunnels."))
X.append(sec('s04', [(0, 'p3_chris_escape', 33), (2.2, 'p3_gets_mask', 66), (4.0, 'p3_gets_mask', 246), (4.6, 'p3_trailer', 108),
  (6.5, 'p3_trailer', 107.5), (8.2, 'p3_chris_escape', 45), (9.4, 'p3_chris_escape', 27), (10.6, 'p3_chris_escape', 48),
  (11.8, 'p3_chris_escape', 54), (12.8, 'p3_chris_escape', 60), (15.4, 'p3_chris_escape', 36)],
  [9, 'Friday the 13th Part III', 1982], 71, 'Aim for the head. Twice.'))
X.append(sec('s05', [(0, 'p4_trailer', 84), (2.8, 'p4_trailer', 27), (4.6, 'p4_out_window', 18), (5.7, 'p4_out_window', 71),
  (7.2, 'p4_tricking_jason', 12), (8.9, 'p4_tricking_jason', 42), (10.5, 'p4_out_window', 75), (12.0, 'p4_tricking_jason', 51),
  (14.4, 'p4_tricking_jason', 60), (15.4, 'p4_tricking_jason', 87), (16.5, 'p4_tricking_jason', 96), (17.9, 'p4_tricking_jason', 120),
  (20.6, 'p4_tricking_jason', 57)],
  [8, 'The Final Chapter', 1984], 60, 'Shave your head. Trust me.'))
X.append(sec('s06', [(0, 'p5_new_beginning', 0), (1.8, 'p5_new_beginning', 120), (3.2, 'p5_new_beginning', 183),
  (4.7, 'p5_new_beginning', 282), (6.9, 'p5_new_beginning', 306), (7.9, 'p5_new_beginning', 228)],
  extra=[('title', ['BONUS'], 0.0, 1.7), ('title', ['FAKE JASON'], 6.9, 9.6)], pad=0.5))
X.append(sec('s07', [(0, 'p8_vs_newyork', 6), (1.2, 'p8_trailer', 39), (3.0, 'p8_trailer', 45), (5.1, 'p8_ending', 27),
  (6.3, 'p8_knockout', 12), (7.4, 'p8_knockout', 81), (9.2, 'p8_ending', 405), (10.6, 'p8_ending', 411), (12.1, 'p8_ending', 429),
  (13.2, 'p8_ending', 435), (14.5, 'p8_ending', 393), (15.6, 'p8_ending', 483), (16.7, 'p8_ending', 492), (19.5, 'p8_ending', 303)],
  [7, 'Jason Takes Manhattan', 1989], 47, 'Find the sewer.'))
X.append(sec('s08', [(0, 'p7_vs_tina', 204), (1.2, 'p7_trailer', 30), (2.5, 'p7_vs_tina', 45), (4.4, 'p7_electrocution', 36),
  (5.8, 'p7_electrocution', 51), (7.4, 'p7_vs_tina', 165), (8.5, 'p7_vs_tina', 183), (10.2, 'p7_vs_tina', 258),
  (12.0, 'p7_resurrecting', 90), (13.6, 'p7_resurrecting', 96), (15.1, 'p7_resurrecting', 72), (16.0, 'p7_trailer', 54), (18.7, 'p7_vs_tina', 228)],
  [6, 'The New Blood', 1988], 38, "Don't fight alone."))
X.append(sec('s09', [(0, 'p8_ending', 15), (1.9, 'fvj_scenepack', 36)], pad=0.5,
  extra=[('title', ['SUBSCRIBE', '!TO SURVIVE'], at('s09', 'Subscribe'), 4.3)]))
X.append(sec('s10', [(0, 'p9_goes_to_hell', 87), (1.3, 'p9_opening_hd', 99), (3.1, 'p9_opening_hd', 102), (4.9, 'p9_opening_hd', 138),
  (6.2, 'p9_opening_hd', 144), (7.2, 'p9_opening_hd', 159), (8.4, 'p9_goes_to_hell', 66), (9.1, 'p9_goes_to_hell', 27),
  (10.8, 'p9_goes_to_hell', 33), (12.4, 'p9_goes_to_hell', 75), (13.3, 'p9_trailer', 57), (14.9, 'p9_goes_to_hell', 96),
  (16.0, 'p9_goes_to_hell', 126), (17.6, 'p9_goes_to_hell', 141), (20.1, 'p9_goes_to_hell', 90)],
  [5, 'Jason Goes to Hell', 1993], 26, "Don't touch the heart."))
X.append(sec('s11', [(0, 'fvj_scenepack', 0), (1.2, 'fvj_final_fight', 0), (3.0, 'fvj_scenepack', 192), (4.8, 'fvj_final_fight', 66),
  (5.9, 'fvj_scenepack', 93), (7.0, 'fvj_final_fight', 114), (8.3, 'fvj_final_fight', 126), (9.1, 'fvj_final_fight', 147),
  (10.5, 'fvj_final_fight', 162), (11.9, 'fvj_final_fight', 258), (13.6, 'fvj_final_fight', 276), (15.3, 'fvj_final_fight', 285),
  (17.8, 'fvj_scenepack', 450)],
  [4, 'Freddy vs. Jason', 2003], 15, 'Let them fight.'))
X.append(sec('s12', [(0, 'p6_scenepack', 57), (2.7, 'p6_reborn', 21), (4.8, 'p6_scenepack', 0), (6.0, 'p6_scenepack', 6),
  (7.2, 'p6_scenepack', 9), (8.3, 'p6_scenepack', 27), (9.5, 'p6_scenepack', 393), (10.4, 'p6_scenepack', 402), (11.0, 'p6_scenepack', 408),
  (12.5, 'p6_bait', 57), (14.2, 'p6_bait', 63), (15.1, 'p6_scenepack', 456), (16.8, 'p6_scenepack', 471), (17.8, 'p6_scenepack', 462),
  (20.6, 'p6_scenepack', 474)],
  [3, 'Jason Lives', 1986], 7, "Chain him. Don't kill him."))
X.append(sec('s13', [(0, 'jx_trailer', 36), (1.2, 'jx_trailer', 27), (2.7, 'jx_trailer', 21), (4.6, 'jx_trailer', 15),
  (6.2, 'jx_trailer', 9), (7.7, 'jx_trailer', 51), (9.8, 'jx_trailer', 87), (11.1, 'jx_trailer', 90), (12.3, 'jx_uber_scenepack', 45),
  (13.5, 'jx_uber_scenepack', 27), (14.0, 'jx_trailer', 33), (16.9, 'jx_trailer', 45)],
  [2, 'Jason X', 2001], 3, 'Stay frozen.'))
X.append(sec('s14', [(0, 'jx_uber_scenepack', 9), (1.2, 'jx_uber_scenepack', 3), (2.7, 'jx_uber_scenepack', 21), (4.0, 'jx_trailer', 69),
  (5.0, 'jx_uber_scenepack', 15), (6.5, 'jx_uber_scenepack', 33), (7.4, 'jx_uber_scenepack', 60), (8.6, 'jx_uber_scenepack', 174),
  (9.6, 'jx_ending', 147), (10.9, 'jx_ending', 153), (11.8, 'jx_ending', 159), (12.7, 'jx_ending', 192), (14.3, 'jx_uber_scenepack', 198),
  (15.2, 'jx_uber_scenepack', 108), (16.6, 'jx_uber_scenepack', 168), (18.6, 'jx_uber_scenepack', 165), (20.7, 'jx_uber_scenepack', 72)],
  [1, 'Uber Jason, Jason X', 2001], 1, 'Leave the planet.'))
X.append(sec('s15', [(0, 'fvj_scenepack', 21), (1.8, 'fvj_final_fight', 264), (3.0, 'r09_scenepack', 471), (4.4, 'p3_gets_mask', 264),
  (6.5, 'p6_scenepack', 363), (9.2, 'BLACK', 0)], pad=1.5,
  extra=[('title', ['YOUR RANKING?'], 4.4, 9.0), ('title', ['INSTRUCTION', '!444'], 9.3, 13.0)]))
FILM = [('p1_', 'Friday the 13th (1980)'), ('p2_', 'Friday the 13th Part 2 (1981)'), ('p3_', 'Friday the 13th Part III (1982)'),
        ('p4_', 'The Final Chapter (1984)'), ('p5_', 'A New Beginning (1985)'), ('p6_', 'Jason Lives (1986)'), ('p7_', 'The New Blood (1988)'),
        ('p8_', 'Jason Takes Manhattan (1989)'), ('p9_', 'Jason Goes to Hell (1993)'), ('jx_', 'Jason X (2001)'),
        ('fvj_', 'Freddy vs. Jason (2003)'), ('r09_', 'Friday the 13th (2009)')]
def film(n): return next((v for k, v in FILM if n.startswith(k)), None)
for S in X:
    runs = []
    for t, n, i in S['shots']:
        f = film(n)
        if runs and runs[-1][0] == f: continue
        runs.append([f, t])
    for k, (f, t) in enumerate(runs):
        if f: S['overlays'].append(['film', f, t, runs[k + 1][1] if k + 1 < len(runs) else 999])
P = {'sections': X,
     'zoom': {**{k: 1.2 for k in ['p1_mrs_voorhees', 'p4_tricking_jason', 'p4_out_window', 'p7_electrocution', 'p7_resurrecting', 'p7_vs_tina',
                                  'p8_vs_newyork']}, **{k: 1.32 for k in ['p8_knockout', 'p6_reborn', 'p9_opening_hd']},
              'r09_final_death': 1.4, 'p3_chris_escape': 1.15, 'p6_bait': 1.15, 'fvj_scenepack': 1.08, 'r09_scenepack': 1.08},
     'gamma': {**{k: 1.3 for k in ['r09_scenepack', 'r09_final_death']},
               **{k: 1.22 for k in ['p9_goes_to_hell', 'p9_opening_hd', 'p7_vs_tina', 'p7_resurrecting', 'p7_electrocution', 'p8_ending',
                                    'p4_tricking_jason', 'p4_out_window', 'p6_bait', 'p8_knockout', 'jx_trailer', 'p3_chris_escape']}}}
json.dump(P, open('edl_full.json', 'w'), indent=1)
print(len(X), 'sections')
