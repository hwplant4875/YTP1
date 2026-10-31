# Halloween special (10 films): builds edl.json for ../ep03/render_v2.py style rendering (render_hw.py) from voice/ (s00 cold open, s01 rules,
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
TILE = {'s02': 'sweet16', 's03': 'sam', 's04': 'other', 's05': 'ginger', 's06': 'haunt', 's07': 'michael', 's08': 'angela', 's09': 'shamrock',
        's10': 'art1', 's11': 'art2'}
SHORT = {'s09': 'Halloween III (1982)'}
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
                                        'stats': dict(zip(['STRENGTH', 'INTELLIGENCE', 'KILL COUNT', 'SUPERNATURAL'], e['v'])), 'pct': e['pct'],
                                        't_pct': tp, 'dur': round(vdur(voice) + S['pad'] - a, 3), 'film': film}, a, 999])
        S['sfx'] += [[a, SFX + 'whoosh.wav', SFX_GAIN['whoosh']], [a + 0.3, SFX + 'fill.wav', SFX_GAIN['fill']], [a + tp, SFX + 'stamp.wav', SFX_GAIN['stamp']]]
        S['card_at'] = a
    S['overlays'] += [[k, val, T(voice, x), T(voice, y)] for k, val, x, y in extra]
    return S
X = []
# v4 (owner 10/31 06:14): highlight clips instead of trailers, villain on screen and doing something, no trailer graphics, HD only.
# A shot written (word, clip, in, -clean) has `clean` seconds before its next cut: fit() slows it down so it never runs into that cut.
# cold open: Art at frame 0 with a caption from frame 0; one action word per beat, each a hard cut + big centre caption on the word
X.append(sec('s00', [(0, 't2_cafe', 260.1, -3.0), ('stalked', 'h78_best', 413.6, -2.3), ('trapped', 'haunt_hurry', 10.0, -1.8),
  ('poisoned', 'trt_trailer', 67.5, -0.9), ('possessed', 'notd_trailer', 63.8, -1.7), ('mauled', 'gs_suit', 67.4, -2.0),
  ('hunted', 't2_cafe', 346.5, -0.85), ('killed by', 'h3_05_test_room', 94.7, -5.0), ('and nobody', 'hf_welcome', 159.4, -1.6),
  ('because everyone', 'hf_vip', 33.6, -3.5), ('just a costume', 'trt_wbuk_night', 85.6, -5.7), ("we're ranking", 't2_cafe', 270.8, -2.7)],
  extra=[('word', 'Halloween night', 0, 'stalked'), ('word', 'Stalked', 'stalked', 'trapped'), ('word', 'Trapped', 'trapped', 'poisoned'),
         ('word', 'Poisoned', 'poisoned', 'possessed'), ('word', 'Possessed', 'possessed', 'mauled'), ('word', 'Mauled by a werewolf', 'mauled', 'hunted'),
         ('word', 'Hunted by a clown', 'hunted', 'and even'), ('word', 'Killed by a TV commercial', 'killed by', 'and nobody'),
         ('title', ['10 HALLOWEEN NIGHTS'], "we're ranking", 999)], clip_db=-20))
for ov in X[-1]['overlays']:  # captions flash and cut out: one word 0.9 s max, a phrase 1.5 s max (EP02 rule); the frame-0 caption holds to its cut
    if ov[0] == 'word' and ov[2] > 0: ov[3] = min(ov[3], ov[2] + (0.9 if ' ' not in ov[1] else 1.5))
s01_end = vdur('s01') + 0.5
X.append(sec('s01', [(0, 't2_costume', 52.0, -4.0), ('strength', 't1_meet', 441.8, -1.6), ('intelligence', 'h3_07_happy', 20, -3.0),
  ('kill count', 'hf_devil', 68.3, -3.8), ('supernatural', 'notd_trailer', 63.8, -1.7), ('which is basically', 't2_cafe', 37.6, -2.4),
  ('put it', 'tk_joblo_open', 45.1, -2.5), ('your survival', 'h78_best', 413.6, -2.3)]))
X[-1]['overlays'].append(['stats', {'name': 'THE KILLER', 'tile_png': 'tiles/mystery.png', 'stats': {'STRENGTH': 6, 'INTELLIGENCE': 7,
  'KILL COUNT': 5, 'SUPERNATURAL': 8}, 'pct': '??', 'dur': round(s01_end, 3), 't_pct': round(T('s01', 'survival rate') + LEAD, 3),
  'reveal': [round(T('s01', w) + LEAD, 3) for w in ('strength', 'intelligence', 'kill count', 'supernatural')]}, 0.0, 999])
X[-1]['sfx'] = [[0.0, SFX + 'whoosh.wav', SFX_GAIN['whoosh']], [T('s01', 'survival rate') + LEAD, SFX + 'stamp.wav', SFX_GAIN['stamp']]]
X.append(sec('s02', [(0, 'tk_joblo_open', 35.5, -3.6), ('the sweet', 'tk_joblo_open', 45.1, -2.5), ('stabs each', 'tk_joblo_open', 93.6, -1.6),
  ('on her', 'tk_trailer', 24.5, 0.6), ('which is horrifying', 'tk_joblo_open', 144.3, -9.4), ('but it also', 'tk_joblo_open', 111.4, -2.0),
  ('very specific', 'tk_trailer', 82.5, 0.8), ("if you're not", 'tk_trailer', 68.5), ('friend group', 'tk_trailer', 90.3),
  ('probably fine', 'tk_trailer', 122.5), ('survival rate', 'tk_joblo_open', 35.5, -3.6)], "if you're not"))
X.append(sec('s03', [(0, 'trt_wbuk_sam', 143.5, -6.4), ('sam', 'trt_wbuk_sam', 124.3, -2.6), ('burlap', 'trt_wbuk_sam', 163.0, -3.8),
  ('only comes', 'trt_wbuk_sam', 80.9, -2.5), ('like blowing', 'trt_wbuk_night', 391.0, -6.0), ('before midnight', 'trt_wbuk_sam', 113.5, -1.6),
  ('follow the', 'trt_wbuk_sam', 150.1, -7.2), ("he'll let", 'trt_wbuk_sam', 173.5, -7.5), ('the problem', 'trt_trailer', 60.5, -1.6),
  ('principal', 'trt_trailer', 88.3), ('candy', 'trt_trailer', 57.9, -1.6), ('werewolves', 'trt_wbuk_night', 85.6, -5.7),
  ('drowned', 'trt_trailer', 126.4, -0.6), ('quarry', 'trt_05_bus', 30.0, -1.6), ('survival rate', 'trt_wbuk_sam', 143.5, -6.4)], 'the problem'))
X.append(sec('s04', [(0, 'hf_vip', 33.6, -1.8), ('this killer', 'hf_maze', 25.8, -3.3), ('just a man', 'hf_guillotine', 169.1, -4.3),
  ("but he's hiding", 'hf_welcome', 159.4, -1.6), ('full of', 'hf_trailer', 78.5), ('every scream', 'hf_devil', 53.5, -4.7),
  ('he kills', 'hf_devil', 68.3, -3.8), ('asher', 'hf_guillotine', 92.7, -2.1), ('quinn', 'hf_guillotine', 132.9, -0.9),
  ('and even after', 'hf_trailer', 120.5), ('drives home', 'hf_trailer', 105.3), ('survival rate', 'hf_guillotine', 100.2, -4.5)], 'and even after'))
X.append(sec('s05', [(0, 'gs_trailer', 8.3, -3.8), ('gets bitten', 'gs_curse', 129.5, -1.2), ('werewolf', 'gs_curse', 133.9, -0.9), ('right after', 'gs_trailer', 48.6, -1.9),
  ('by halloween', 'gs_curse', 239.8, -4.0), ('not really', 'gs_curse', 230.4, -0.7), ('anymore', 'gs_curse', 231.2, -0.7),
  ('she kills', 'gs_trailer', 98.5), ('school counselor', 'gs_trailer', 104.5), ('tears her', 'gs_trailer', 100.5), ('halloween party', 'gs_trailer', 68.5),
  ('and it ends', 'gs_trailer', 88.5), ('sister', 'gs_curse', 247.6, -0.8), ('knife', 'gs_trailer', 97.3, 0.8), ('survival rate', 'gs_trailer', 66.5)], 'and it ends'))
X.append(sec('s06', [(0, 'haunt_trailer', 12.5), ('pay to', 'haunt_trailer', 22.5), ('haunted house', 'haunt_trailer', 24.2, -0.9), ('actors inside', 'haunt_hurry', 17.5, -2.5),
  ("aren't acting", 'haunt_trailer', 90.0, -0.9), ('six masked', 'haunt_trailer', 19.3, -1.0), ('killers', 'haunt_trailer', 50.9, -0.8),
  ('rooms are', 'haunt_trailer', 51.9, -1.2), ('doors lock', 'haunt_hurry', 9.9, -2.0), ('only two', 'haunt_trailer', 93.4, -0.8), ('make it', 'haunt_trailer', 63.2, -3.5),
  ('survival rate', 'haunt_trailer', 95.0, -4.5)], 'only two'))
X.append(sec('s07', [(0, 'h78_ending', 540.0, -7.9), ('michael myers', 'h78_best', 413.3, -3.2), ('comes home', 'h78_best', 401.8, -1.7),
  ('and spends', 'h78_best', 75.0, -5.9), ('he kills', 'h78_every', 333.2, -1.9), ('bob', 'h78_best', 222.5, -1.9), ('linda', 'h78_best', 271.0, -5.9),
  ('and when', 'h78_best', 578.2, -1.0), ('shoots him', 'h78_best', 579.9, -0.7), ('falls off', 'h78_best', 582.7, -3.0),
  ('and then', 'h78_ending', 487.8, -4.1), ('survival rate', 'h78_best', 541.0, -6.6)], 'and when'))
X.append(sec('s08', [(0, 'notd_trailer', 14.3, -7.8), ('halloween party', 'notd_trailer', 25.8, -1.4), ('funeral home', 'notd_trailer', 40.3, -3.4),
  ('a demon', 'notd_trailer', 48.5, -0.9), ('jumping from', 'notd_trailer', 69.0, -1.0), ('body to body', 'notd_trailer', 63.8, -1.7),
  ('so the friend', 'notd_trailer', 84.0, -1.4), ('anymore', 'notd_trailer', 62.8, -0.9), ('by sunrise', 'notd_trailer', 102.8, -0.9),
  ('judy', 'notd_trailer', 105.0, -1.4), ('over the wall', 'notd_trailer', 106.5, -0.9), ('survival rate', 'notd_trailer', 82.5, -1.4)], 'by sunrise'))
X.append(sec('s09', [(0, 'h3_skull', 2.5, -5.2), ('no michael', 'h3_07_happy', 20, -3.0), ('toy company', 'h3_05_test_room', 67.5, -4.0),
  ('masks', 'h3_10_off_air', 32.5, -2.5), ('commercial', 'h3_10_off_air', 16.0, -2.0), ('at 9', 'h3_10_off_air', 12.2, -3.8),
  ('every kid wearing', 'h3_05_test_room', 94.7, -5.0), ('dies', 'h3_05_test_room', 102.0, -0.9), ('the hero', 'h3_10_off_air', 70.0, -6.0),
  ('two channels', 'h3_10_off_air', 84.5, -1.5), ('the third', 'h3_10_off_air', 76.5, -1.0), ('keeps playing', 'h3_10_off_air', 87.3, -1.9),
  ('survival rate', 'h3_10_off_air', 61.5, -3.0)], 'the hero'))
X.append(sec('s10', [(0, 't1_meet', 65.3, -2.2), ('art the clown', 't1_meet', 101.3, -2.2), ("doesn't talk", 't1_meet', 222.4, -2.2),
  ("doesn't run", 't1_meet', 461.0, -2.5), ('on one', 't1_meet', 182.3, -2.2), ('he goes', 't1_meet', 441.8, -1.6),
  ('almost everyone', 't1_meet', 448.2, -1.8), ('the only', 't1_meet', 193.3, -2.2), ('so badly', 't1_meet', 196.8, -2.2),
  ('survival rate', 't1_meet', 101.3, -2.2)], 'the only'))
X.append(sec('s11', [(0, 't2_costume', 83.8, -2.6), ('comes back', 't2_cafe', 37.6, -2.4), ('kills the', 't2_sienna', 152.4, -3.2),
  ('and spends', 't2_costume', 292.5, -4.0), ('hunting sienna', 't2_sienna', 209.5, -6.0), ('and this time', 't2_sienna', 142.4, -1.6),
  ('not human', 't2_cafe', 270.8, -2.7), ('not even death', 't2_sienna', 185.9, -3.3), ('even sienna', 't2_costume', 86.6, -2.6),
  ('cuts his', 't2_sienna', 308.3, -6.0), ('and he still', 't2_costume', 338.6, -5.5), ('survival rate', 't2_cafe', 260.1, -3.0)], 'not even death'))
X.append(sec('s12', [(0, 'trt_wbuk_night', 391.0, -6.0), ('a killer', 'tk_joblo_open', 35.5, -3.6), ('a clown', 't2_cafe', 346.5, -0.85), ("you can't", 't2_cafe', 270.8, -2.7),
  ('tell me', 'h3_10_off_air', 64.5, -4.0), ('and happy', 'trt_wbuk_night', 85.6, -5.7), ("don't open", 'h78_best', 413.6, -2.3)], pad=2.5,
  extra=[('title', ['YOUR PICK?'], 'tell me', 'and happy'), ('title', ['HAPPY', '!HALLOWEEN'], 'and happy', 999)]))
def fit(S):  # turn (t, clip, in, -clean) into a speed that keeps the shot inside its clean span (never below 0.4x)
    L = vdur(S['voice']) + S['pad']; sh = S['shots']
    for k, s in enumerate(sh):
        if len(s) > 3 and s[3] < 0:
            d = (sh[k + 1][0] if k + 1 < len(sh) else L) - s[0]; sp = min(1.0, -s[3] * 0.96 / d)
            if sp < 0.4: print('WARN too short', S['voice'], s, round(d, 2))
            sp = max(sp, 0.4)
            if sp >= 0.999: del s[3:]
            else: s[3] = round(sp, 3)
for S in X: fit(S)
FILM = [('tk_', 'Totally Killer (2023)'), ('trt_', "Trick 'r Treat (2007)"), ('hf_', 'Hell Fest (2018)'),
        ('gs_', 'Ginger Snaps (2000)'), ('haunt_', 'Haunt (2019)'), ('h78_', 'Halloween (1978)'), ('notd_', 'Night of the Demons (1988)'),
        ('h3_', 'Halloween III (1982)'), ('t1_', 'Terrifier (2016)'), ('t2_', 'Terrifier 2 (2022)')]
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
DARK = ['trt_06_lake', 'trt_trailer', 'notd_trailer', 'haunt_trailer', 'hf_trailer', 't1_trailer', 'h78_best', 'h78_every', 'h78_ending', 't1_meet', 'gs_suit', 'gs_curse', 'tk_joblo_open', 'haunt_hurry']
P = {'sections': X, 'tiers': TIERS, 'gamma': {k: 1.28 for k in DARK}, 'zoom': {'h78_ending': 1.36},  # Binge Society logo sits in the letterbox bar
     }  # no watermark removal: only the black bar over the Movieclips mark; Totally Killer uses the Blumhouse trailer (no Prime bug)
json.dump(P, open(D + 'edl.json', 'w'), indent=1)
print(len(X), 'sections')
