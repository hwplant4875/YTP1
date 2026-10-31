# Halloween special: builds edl.json for ../ep03/render_v2.py style rendering (render_hw.py) from voice/ (s00 cold open, s01 rules,
# s02..s12 = #11..#1, s13 outro). Cuts are anchored to whisper word onsets (voice/words.json); the % stamp is anchored to the
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
TILE = {'s02': 'slappy', 's03': 'sweet16', 's04': 'sam', 's05': 'other', 's06': 'ginger', 's07': 'haunt', 's08': 'michael', 's09': 'angela',
        's10': 'shamrock', 's11': 'art1', 's12': 'art2'}
SHORT = {'s02': 'Goosebumps 2 (2018)', 's10': 'Halloween III (1982)'}
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
X.append(sec('s00', [(0, 'trt_trailer', 99.3, 0.8), ('mask', 'hf_trailer', 73.9, 0.6), ('scream', 'notd_trailer', 104.6), ('knock', 'h78_trailer', 141),
  ('could be', 't1_trailer', 46.6), ('so if', 'gb2_dummy', 342.5), ('inside a', 'h3_10_off_air', 30.5), ('which one', 'h3_05_test_room', 69),
  ('actually walk', 'h78_trailer', 117.2), ("we're ranking", 't2_trailer', 78.5)],
  extra=[('title', ['11 HALLOWEEN NIGHTS'], "we're ranking", 999)], clip_db=-22))
s01_end = vdur('s01') + 0.5
X.append(sec('s01', [(0, 't2_trailer', 36.5), ('strength', 't2_trailer', 72.3), ('intelligence', 'h3_07_happy', 20), ('kill count', 'notd_trailer', 62.5),
  ('supernatural', 'gb2_dummy', 334.5), ('which is basically', 't2_trailer', 74.3), ('put it', 'tk_trailer', 116.5), ('your survival', 'h78_trailer', 36.5)]))
X[-1]['overlays'].append(['stats', {'name': 'THE KILLER', 'tile_png': 'tiles/mystery.png', 'stats': {'STRENGTH': 6, 'INTELLIGENCE': 7,
  'KILL COUNT': 5, 'SUPERNATURAL': 8}, 'pct': '??', 'dur': round(s01_end, 3), 't_pct': round(T('s01', 'survival rate') + LEAD, 3),
  'reveal': [round(T('s01', w) + LEAD, 3) for w in ('strength', 'intelligence', 'kill count', 'supernatural')]}, 0.0, 999])
X[-1]['sfx'] = [[0.0, SFX + 'whoosh.wav', SFX_GAIN['whoosh']], [T('s01', 'survival rate') + LEAD, SFX + 'stamp.wav', SFX_GAIN['stamp']]]
X.append(sec('s02', [(0, 'gb2_dummy', 296.5), ('slappy', 'gb2_dummy', 314.5), ('brings every', 'gb2_dummy', 335), ('decoration', 'gb2_dummy', 342.5),
  ('giant spiders', 'gb2_trailer', 38.6), ('flying witches', 'gb2_trailer', 36.4), ('army of', 'gb2_trailer', 94.5), ('end of', 'gb2_dummy', 362.5),
  ('but for all', 'gb2_dummy', 432.5), ('nobody actually', 'gb2_dummy', 556.5), ('three kids', 'gb2_trailer', 98.5), ('survival rate', 'gb2_dummy', 314.5)],
  'nobody actually'))
X.append(sec('s03', [(0, 'tk_trailer', 26.5), ('the sweet', 'tk_trailer', 101.3), ('stabs each', 'tk_trailer', 116.5), ('on her', 'tk_trailer', 24.5, 0.6),
  ('which is horrifying', 'tk_trailer', 118.2), ('but it also', 'tk_trailer', 116.6, 0.5), ('very specific', 'tk_trailer', 82.5, 0.8), ("if you're not", 'tk_trailer', 68.5),
  ('friend group', 'tk_trailer', 90.3), ('probably fine', 'tk_trailer', 122.5), ('survival rate', 'tk_trailer', 101.2, 0.5)], "if you're not"))
X.append(sec('s04', [(0, 'trt_trailer', 30.5), ('sam', 'trt_trailer', 96.2, 0.55), ('only comes', 'trt_trailer', 42.8, 0.5), ('break the', 'trt_trailer', 26.5), ('like blowing', 'trt_trailer', 99.3, 0.8),
  ('follow the', 'trt_trailer', 119.2), ("he'll let", 'trt_trailer', 143.3), ('the problem', 'trt_trailer', 60.5), ('principal', 'trt_trailer', 88.3),
  ('candy', 'trt_trailer', 132.5), ('werewolves', 'trt_trailer', 71), ('drowned', 'trt_06_lake', 66.5), ('quarry', 'trt_05_bus', 30.5),
  ('survival rate', 'trt_trailer', 96.2, 0.6)], 'the problem'))
X.append(sec('s05', [(0, 'hf_trailer', 6.5), ('this killer', 'hf_trailer', 62.5), ('just a man', 'hf_trailer', 73.9, 0.6), ("but he's hiding", 'hf_trailer', 42.5),
  ('full of', 'hf_trailer', 78.5), ('every scream', 'hf_trailer', 142.5), ('he kills', 'hf_trailer', 84.5, 0.7), ('asher', 'hf_trailer', 99.3),
  ('quinn', 'hf_trailer', 100.5), ('and even after', 'hf_trailer', 120.5), ('drives home', 'hf_trailer', 104.5), ('survival rate', 'hf_trailer', 73.9, 0.5)],
  'and even after'))
X.append(sec('s06', [(0, 'gs_trailer', 18.0, 0.8), ('gets bitten', 'gs_trailer', 30.5), ('werewolf', 'gs_trailer', 48.5), ('by halloween', 'gs_trailer', 66.5),
  ('not really', 'gs_trailer', 62.5), ('she kills', 'gs_trailer', 98.5), ('school counselor', 'gs_trailer', 104.5), ('tears her', 'gs_trailer', 100.5),
  ('halloween party', 'gs_trailer', 68.5), ('and it ends', 'gs_trailer', 88.5), ('knife', 'gs_trailer', 97.3, 0.8), ('survival rate', 'gs_trailer', 66.5)],
  'and it ends'))
X.append(sec('s07', [(0, 'haunt_trailer', 12.5), ('pay to', 'haunt_trailer', 22.5), ('actors inside', 'haunt_trailer', 43.0), ("aren't acting", 'haunt_trailer', 50.5),
  ('six masked', 'haunt_trailer', 94), ('rooms are', 'haunt_trailer', 64.5), ('doors lock', 'haunt_trailer', 86.5), ('only two', 'haunt_trailer', 88.5),
  ('survival rate', 'haunt_trailer', 94)], 'only two'))
X.append(sec('s08', [(0, 'h78_trailer', 8.5), ('michael myers', 'h78_trailer', 36.5), ('comes home', 'h78_trailer', 12.5), ('and spends', 'h78_trailer', 65.2),
  ('stalking', 'h78_trailer', 74.2, 0.8), ('he kills', 'h78_trailer', 82.5), ('bob', 'h78_trailer', 88.5), ('and when', 'h78_trailer', 46.5),
  ('shoots him', 'h78_trailer', 117.2), ('falls off', 'h78_trailer', 119.5), ('and then', 'h78_trailer', 126.5), ('survival rate', 'h78_trailer', 117.2)],
  'and when'))
X.append(sec('s09', [(0, 'notd_trailer', 10.5), ('halloween party', 'notd_trailer', 36.5), ('funeral home', 'notd_trailer', 14.5), ('seance', 'notd_trailer', 40.5),
  ('a demon', 'notd_trailer', 62.5), ('jumping from', 'notd_trailer', 48.5), ('so the friend', 'notd_trailer', 44.5), ('anymore', 'notd_trailer', 64.5),
  ('by sunrise', 'notd_trailer', 102.5), ('judy', 'notd_trailer', 104.5), ('over the wall', 'notd_trailer', 106.5), ('survival rate', 'notd_trailer', 82.5)],
  'by sunrise'))
X.append(sec('s10', [(0, 'h3_10_off_air', 12.5), ('no michael', 'h3_07_happy', 20), ('toy company', 'h3_05_test_room', 50.5), ('masks', 'h3_10_off_air', 32.5),
  ('every kid', 'h3_10_off_air', 40.5), ('commercial', 'h3_05_test_room', 74.5), ('at 9', 'h3_10_off_air', 12.5), ('every kid wearing', 'h3_05_test_room', 90.5),
  ('dies', 'h3_05_test_room', 127.4), ('the hero', 'h3_10_off_air', 20.5), ('two channels', 'h3_10_off_air', 84.5), ('the third', 'h3_10_off_air', 76.5),
  ('keeps playing', 'h3_10_off_air', 88.5, 0.6), ('survival rate', 'h3_10_off_air', 78.5)], 'the hero'))
X.append(sec('s11', [(0, 't1_trailer', 16.5), ('art the clown', 't1_trailer', 22.5), ("doesn't talk", 't1_trailer', 73.3), ("doesn't run", 't1_trailer', 46.5),
  ('reason', 't1_trailer', 16.6, 0.6), ('on one', 't1_trailer', 18.5), ('he goes', 't1_trailer', 48.5), ('almost everyone', 't1_trailer', 56.5, 0.6),
  ('the only', 't1_trailer', 66.5, 0.6), ('so badly', 't1_trailer', 54.0), ('never the', 't1_trailer', 52.5), ('survival rate', 't1_trailer', 73.3, 0.5)], 'the only'))
X.append(sec('s12', [(0, 't2_trailer', 12.5), ('comes back', 't2_trailer', 36.5), ('kills the', 't2_trailer', 44.5), ('and spends', 't2_trailer', 28.5),
  ('hunting sienna', 't2_trailer', 52.5), ('little brother', 't2_trailer', 24.5), ('and this time', 't2_trailer', 48.5), ('not human', 't2_trailer', 72.5),
  ('not even death', 't2_trailer', 56.5), ('even sienna', 't2_trailer', 54.5), ('comes back and', 't2_trailer', 22.5), ('cuts his', 't2_trailer', 74.5),
  ('and he still', 't2_trailer', 78.5), ('survival rate', 't2_trailer', 48.5)], 'not even death'))
X.append(sec('s13', [(0, 'trt_trailer', 99.3, 0.7), ('ventriloquist', 'gb2_dummy', 314.5), ('a clown', 't2_trailer', 78.5), ('tell me', 'h3_10_off_air', 76.5),
  ('and happy', 'trt_trailer', 60.5), ("don't open", 'h78_trailer', 141)], pad=2.5,
  extra=[('title', ['YOUR PICK?'], 'tell me', 'and happy'), ('title', ['HAPPY', '!HALLOWEEN'], 'and happy', 999)]))
FILM = [('gb2_', 'Goosebumps 2 (2018)'), ('tk_', 'Totally Killer (2023)'), ('trt_', "Trick 'r Treat (2007)"), ('hf_', 'Hell Fest (2018)'),
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
DARK = ['trt_06_lake', 'trt_trailer', 'h78_trailer', 'notd_trailer', 'haunt_trailer', 'hf_trailer', 't1_trailer', 'gb2_trailer']
P = {'sections': X, 'tiers': TIERS, 'gamma': {k: 1.28 for k in DARK},
     }  # no watermark removal: only the black bar over the Movieclips mark; Totally Killer uses the Blumhouse trailer (no Prime bug)
json.dump(P, open(D + 'edl.json', 'w'), indent=1)
print(len(X), 'sections')
