# EP02 Jason Voorhees: builds edl_full.json (intro, rules, #11..#1 with Part V bonus and mid-roll, outro)
# render: python ../ep01/render.py edl_full.json <clips_dir> <voice_v2_dir> <music.mp3> <out.mp4>
import json, re
V = '/mnt/project-files/instruction444/ep02_jason_ranked/voice_v2/'
LEAD = 0.08  # cut a hair before the word so the picture lands with the voice
def at(seg, word):
    a = json.load(open(V + seg + '.json')); t = ''.join(a['characters'])
    i = t.find(word) if word[0].islower() or ' ' in word else t.rfind(word); assert i >= 0, (seg, word)
    return round(a['character_start_times_seconds'][i], 2)
def words(seg):  # (onset, phrase_start) for every spoken word
    a = json.load(open(V + seg + '.json')); t = ''.join(a['characters']); st = a['character_start_times_seconds']
    return [(st[m.start()], m.start() == 0 or t[m.start() - 2] in '.,?!:') for m in re.finditer(r"\S+", t)]
def snap(seg, t):  # numeric cut -> nearest phrase start within 0.6 s, else nearest word onset
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
# cold open: frame 0 = Jason's face; one word per way he has been "killed"
X.append(sec('s00', [(0, 'p6_scenepack', 69), ('hacked', 'p4_tricking_jason', 124.18), ('hanged', 'p3_trailer', 109.41, 0.87),
  ('drowned', 'p6_scenepack', 458.3), ('electrocuted', 'p7_electrocution', 48.66), ('blown', 'p9_opening_hd', 142.32),
  ('frozen', 'jx_uber_scenepack', 2.5), ('and, umm', 'jx_uber_scenepack', 11.3), ('thrown', 'jx_ending', 148.5), ('And he kept', 'p6_scenepack', 30),
  ('Here is the twist', 'p1_mrs_voorhees', 17), ('in the first', 'p1_mrs_voorhees', 27), ('It was his mother', 'p1_mrs_voorhees', 50),
  ('Every movie', 'p3_chris_escape', 34.6), ('gave us', 'p6_scenepack', 108), ('different', 'p8_vs_newyork', 6), ('Eleven of', 'jx_uber_scenepack', 9),
  ('Today', 'p7_vs_tina', 204), ('from the one', 'fvj_scenepack', 27), ('you could beat', 'p2_final_scene', 165),
  ('to the one you should', 'jx_uber_scenepack', 132), ('This is Instruction', 'BLACK', 0)],
  extra=[('word', 'Hacked', 'hacked', 'hanged'), ('word', 'Hanged', 'hanged', 'drowned'), ('word', 'Drowned', 'drowned', 'electrocuted'),
         ('word', 'Electrocuted', 'electrocuted', 'blown'), ('word', 'Blown to pieces', 'blown', 'frozen'), ('word', 'Frozen', 'frozen', 'and, umm'),
         ('word', 'Umm...', 'umm', 'thrown'), ('word', 'Thrown into space?', 'thrown', 'And he kept'),
         ('title', ['IT WAS HIS MOTHER'], 'It was his mother', 'Every movie'), ('title', ['11 JASONS'], 'Eleven of', 'Today'),
         ('title', ['INSTRUCTION', '!444'], 'This is Instruction', 999)], pad=0.5, clip_db=-20))
X.append(sec('s01', [(0, 'p3_gets_mask', 246), ('Not the best', 'p8_trailer', 57), ('The hardest', 'p6_scenepack', 120), (5.0, 'r09_scenepack', 81),
  (7.4, 'p7_vs_tina', 165), (8.8, 'fvj_scenepack', 180), (10.1, 'jx_uber_scenepack', 60)],
  extra=[('title', ['NOT THE BEST MOVIE'], 'Not the best', 'The hardest'), ('title', ['THE HARDEST', '!TO KILL'], 'The hardest', 'And for every'), ('odds', '??', at('s01', 'survival rate'), 999)], pad=0.5))
X.append(sec('s02', [(0, 'p2_still_window', 0), (3.8, 'p2_still_sack', 0), (7.0, 'p2_final_scene', 39), (9.4, 'p2_final_scene', 168),
  (11.0, 'p2_final_scene', 174), (12.2, 'p2_trailer', 93.6), (14.1, 'p2_final_scene', 99), (15.6, 'p2_trailer', 121.2), (17.1, 'p2_final_scene', 171),
  (18.2, 'p2_final_scene', 236), (20.8, 'p2_final_scene', 180)],
  [11, 'Friday the 13th Part 2', 1981], 90, 'Pretend to be his mom.'))
X.append(sec('s03', [(0, 'r09_scenepack', 81), (2.5, 'r09_scenepack', 135), (3.9, 'r09_scenepack', 84), (5.4, 'r09_final_death', 81),
  (7.6, 'r09_scenepack', 279), (10.2, 'r09_final_death', 186), (12.0, 'r09_final_death', 189), (13.8, 'r09_final_death', 236),
  (15.4, 'r09_final_death', 258), (18.0, 'r09_scenepack', 468)],
  [10, 'Friday the 13th', 2009], 82, "Don't hide in the tunnels."))
X.append(sec('s04', [(0, 'p3_chris_escape', 31.0), (2.2, 'p3_gets_mask', 66), (4.0, 'p3_gets_mask', 246), ('Chris hangs', 'p3_trailer', 107.17, 0.6), ('from the barn', 'p3_trailer', 109.41, 0.62),
  ('He pulls', 'p3_chris_escape', 128.5), (8.2, 'p3_chris_escape', 45), (9.4, 'p3_chris_escape', 27), (10.6, 'p3_chris_escape', 48),
  (11.8, 'p3_chris_escape', 54), (12.8, 'p3_chris_escape', 60), (15.4, 'p3_chris_escape', 36)],
  [9, 'Friday the 13th Part III', 1982], 71, 'Aim for the head. Twice.'))
X.append(sec('s05', [(0, 'p4_trailer', 84), (2.8, 'p4_trailer', 27), (4.6, 'p4_out_window', 18), (5.7, 'p4_out_window', 71),
  (7.2, 'p4_tricking_jason', 12), (8.9, 'p4_tricking_jason', 42), (10.5, 'p4_out_window', 75), (12.0, 'p4_tricking_jason', 51.9),
  (14.4, 'p4_tricking_jason', 60), (15.4, 'p4_tricking_jason', 87), (16.5, 'p4_tricking_jason', 96), (17.9, 'p4_tricking_jason', 119.25),
  (20.6, 'p4_tricking_jason', 57)],
  [8, 'The Final Chapter', 1984], 60, 'Shave your head. Trust me.'))
X.append(sec('s06', [(0, 'p5_new_beginning', 0), (1.8, 'p5_new_beginning', 120), (3.2, 'p5_new_beginning', 183),
  (4.7, 'p5_new_beginning', 282), ('Fake Jason', 'p5_new_beginning', 306), (7.9, 'p5_new_beginning', 228)],
  extra=[('title', ['BONUS'], 0.0, 'The killer'), ('title', ['FAKE JASON'], 'Fake Jason', 999)], pad=0.5))
X.append(sec('s07', [(0, 'p8_vs_newyork', 6), (1.2, 'p8_trailer', 39), (3.0, 'p8_trailer', 45), (5.1, 'p8_ending', 27),
  (6.3, 'p8_knockout', 12), (7.4, 'p8_knockout', 81), (9.2, 'p8_ending', 405), (10.6, 'p8_ending', 411), (12.1, 'p8_ending', 429),
  (13.2, 'p8_ending', 435), (14.5, 'p8_ending', 393), (15.6, 'p8_ending', 483), (16.7, 'p8_ending', 492), (19.5, 'p8_ending', 304.3)],
  [7, 'Jason Takes Manhattan', 1989], 47, 'Find the sewer.'))
X.append(sec('s08', [(0, 'p7_vs_tina', 204), (1.2, 'p7_trailer', 30), (2.5, 'p7_vs_tina', 45), (4.4, 'p7_electrocution', 36.85),
  (5.8, 'p7_electrocution', 51), (7.4, 'p7_vs_tina', 165), (8.5, 'p7_vs_tina', 183), (10.2, 'p7_vs_tina', 258),
  (12.0, 'p7_resurrecting', 90), (13.6, 'p7_resurrecting', 96), (15.1, 'p7_resurrecting', 72), (16.0, 'p7_trailer', 54), (18.7, 'p7_vs_tina', 228)],
  [6, 'The New Blood', 1988], 38, "Don't fight alone."))
X.append(sec('s09', [(0, 'p8_ending', 15), ('Subscribe', 'fvj_scenepack', 36)], pad=0.5,
  extra=[('title', ['SUBSCRIBE', '!TO SURVIVE'], 'Subscribe', 999)]))
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
X.append(sec('s13', [(0, 'jx_trailer', 36), (1.2, 'jx_trailer', 27), (2.7, 'jx_trailer', 21), (4.6, 'jx_trailer', 15.75, 0.5),
  (6.2, 'jx_trailer', 7.9), (7.7, 'jx_trailer', 51.9), (9.8, 'jx_trailer', 87), (11.1, 'jx_trailer', 90.5), (12.3, 'jx_uber_scenepack', 45),
  (13.5, 'jx_uber_scenepack', 27), (14.0, 'jx_trailer', 33.25), (16.9, 'jx_trailer', 45)],
  [2, 'Jason X', 2001], 3, 'Stay frozen.'))
X.append(sec('s14', [(0, 'jx_uber_scenepack', 9), (1.2, 'jx_uber_scenepack', 4.5), (2.7, 'jx_uber_scenepack', 21), (4.0, 'jx_trailer', 69),
  (5.0, 'jx_uber_scenepack', 15), (6.5, 'jx_uber_scenepack', 33), (7.4, 'jx_uber_scenepack', 60), (8.6, 'jx_uber_scenepack', 174),
  (9.6, 'jx_ending', 147), (10.9, 'jx_ending', 153), (11.8, 'jx_ending', 159), (12.7, 'jx_ending', 192), (14.3, 'jx_uber_scenepack', 198),
  (15.2, 'jx_uber_scenepack', 108), (16.6, 'jx_uber_scenepack', 168), (18.6, 'jx_uber_scenepack', 165.6), (20.7, 'jx_uber_scenepack', 72)],
  [1, 'Uber Jason, Jason X', 2001], 1, 'Leave the planet.'))
X.append(sec('s15', [(0, 'fvj_scenepack', 21), (1.8, 'fvj_final_fight', 264), (3.0, 'r09_scenepack', 471), ('Tell us', 'p3_gets_mask', 264),
  (6.5, 'p6_scenepack', 363), ('This was', 'BLACK', 0)], pad=1.5,
  extra=[('title', ['YOUR RANKING?'], 'Tell us', 'This was'), ('title', ['INSTRUCTION', '!444'], 'This was', 999)]))
FILM = [('p1_', 'Friday the 13th (1980)'), ('p2_', 'Friday the 13th Part 2 (1981)'), ('p3_', 'Friday the 13th Part III (1982)'),
        ('p4_', 'The Final Chapter (1984)'), ('p5_', 'A New Beginning (1985)'), ('p6_', 'Jason Lives (1986)'), ('p7_', 'The New Blood (1988)'),
        ('p8_', 'Jason Takes Manhattan (1989)'), ('p9_', 'Jason Goes to Hell (1993)'), ('jx_', 'Jason X (2001)'),
        ('fvj_', 'Freddy vs. Jason (2003)'), ('r09_', 'Friday the 13th (2009)')]
def film(n): return next((v for k, v in FILM if n.startswith(k)), None)
for S in X:
    runs = []
    for t, n, i, *_ in S['shots']:
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
