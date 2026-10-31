# Clowns episode (EP06): builds edl.json for ../ep03/render_v2.py style rendering (render_hw.py) from voice/ (s00 cold open, s01 rules,
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
TILE = {'s02': 'zl', 's03': 'pg', 's04': 'spaulding', 's05': 'klown', 's06': 'frendo', 's07': 'pw90', 's08': 'pw17', 's09': 'pw19', 's10': 'art1', 's11': 'art2'}
SHORT = {'s05': 'Killer Klowns (1988)'}
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
# Clowns (EP06), Halloween v7 pipeline. A shot written (word, clip, in, -clean) has `clean` seconds before its next cut: fit() slows it to fit.
# Clip in-points from verified frame strips (agent scans 10/31 + own checks); no trailer graphics, no gore, official sources only.
# cold open: Pennywise (2017) at frame 0 with a caption; one beat per spoken action, each a hard cut + big centre caption on the word
X.append(sec('s00', [(0, 'it17_wbuk', 1067.2, -5.2), ('wrap', 'kk_mgm', 78.7, -6.4), ('drag', 'pg15_trailer', 117.3, -1.0),
  ('hunt', 'cc_trailer_shudder', 92.6, -1.3), ('pull', 'it17_georgie', 485.9, -4.7), ('saw', 'cc_trailer_shudder', 73.6, -1.7),
  ('and the scariest', 't2_costume_hd', 250.95, -3.6), ('never', 't1_meet_hd', 222.35, -3.1), ("we're ranking", 'it2_wb', 132.7, -8.5)],
  extra=[('word', 'Clowns', 0, 'wrap'), ('word', 'Cotton candy cocoon', 'wrap', 'drag'), ('word', 'Dragged under your bed', 'drag', 'hunt'),
         ('word', 'Hunted through a cornfield', 'hunt', 'pull'), ('word', 'Pulled down a storm drain', 'pull', 'and saw'),
         ('word', 'Sawed in half', 'saw', 'and the scariest'), ('word', 'Never says a word', 'never', "we're ranking"),
         ('title', ['10 KILLER CLOWNS'], "we're ranking", 999)], clip_db=-20))
for ov in X[-1]['overlays']:  # captions flash and cut out: one word 0.9 s max, a phrase 1.5 s max (EP02 rule); the frame-0 caption holds to its cut
    if ov[0] == 'word' and ov[2] > 0: ov[3] = min(ov[3], ov[2] + (0.9 if ' ' not in ov[1] else 1.5))
s01_end = vdur('s01') + 0.5
X.append(sec('s01', [(0, 'it17_wbuk', 733.7, -7.0), ('every clown', 'kk_giant', 247.1, -2.9), ('strength', 'cc_bench', 99.85, -1.75),
  ('intelligence', 'dr_clown_business', 88.1, -9.2), ('kill count', 't2_cafe_hd', 276.85, -1.4), ('supernatural', 'it17_wbuk', 712.0, -4.5),
  ('which really', 'it2_final', 110.9, -4.2), ('and that gives', 'kk_mgm', 329.8, -4.0), ('your survival', 't1_meet_hd', 222.35, -3.1)]))
X[0]['vfade'] = {'out': 0.25}; X[-1]['vfade'] = {'in': 0.25}  # dip through black into the rules card (owner 10/31)
X[-1]['overlays'].append(['stats', {'name': 'THE CLOWN', 'tile_png': 'tiles/mystery.png', 'stats': {'STRENGTH': 6, 'INTELLIGENCE': 7,
  'KILL COUNT': 5, 'SUPERNATURAL': 8}, 'pct': '??', 'dur': round(s01_end, 3), 't_pct': round(T('s01', 'survival rate') + LEAD, 3),
  'reveal': [round(T('s01', w) + LEAD, 3) for w in ('strength', 'intelligence', 'kill count', 'supernatural')]}, 0.0, 999])
X[-1]['sfx'] = [[0.0, SFX + 'whoosh.wav', SFX_GAIN['whoosh']], [T('s01', 'survival rate') + LEAD, SFX + 'stamp.wav', SFX_GAIN['stamp']]]
# #10 Zombieland clown 99%
X.append(sec('s02', [(0, 'zl_clown_cc', 25.15, -2.2), ("he's terrifying", 'zl_clown_cc', 39.55, -1.6), ('until you', 'zl_clown_cc', 17.9, -2.5),
  ("he can't", 'zl_clown_cc', 25.9, -1.4), ('columbus', 'zl_clown_cc', 37.95, -1.5), ('more than', 'zl_clown_cc', 43.85, -1.1),
  ('and even he', 'zl_clown_cc', 47.8, -1.4), ('mallet', 'zl_clown_cc', 51.2, -1.55), ('survival rate', 'zl_clown_cc', 52.85, -2.1)], 'columbus'))
# #9 Poltergeist (2015) clown doll 95%
X.append(sec('s03', [(0, 'pg15_trailer', 107.6, -1.3), ('from poltergeist', 'pg15_trailer', 13.45, -1.1), ('it drags', 'pg15_trailer', 115.45, -1.9), ('tries to strangle', 'pg15_trailer', 117.6, -0.7),
  ('and the whole', 'pg15_trailer', 119.6, -0.8), ('is clearly', 'pg15_trailer2', 54.5, -1.2), ("but here's", 'pg15_trailer', 72.55, -1.35), ('nobody in', 'pg15_trailer', 78.3, -0.5), ('actually dies', 'pg15_trailer', 30.8, -1.2),
  ('pull the doll', 'pg_clown_20th', 37.8, -2.1), ("don't let", 'pg15_trailer', 89.4, -1.2),
  ('survival rate', 'pg15_trailer', 115.45, -1.9)], "but here's"))
# #8 Captain Spaulding 60% (720p official clips: sharp close shots only; 1080p trailer shots without graphics)
X.append(sec('s04', [(0, 'dr_send_clown', 25.6, -2.2), ('he runs', 'h1k_murder_ride', 8.45, -2.6), ('murder ride', 'h1k_murder_ride', 46.5, -3.2),
  ('and when two', 'h1k_murder_ride', 55.3, -5.0), ('he shoots', 'dr_send_clown', 89.1, -5.0), ("he's just", 'dr_clown_business', 39.7, -8.8),
  ('but if he', 'dr_clown_business', 14.7, -2.7), ('satan', 'dr_clown_business', 5.6, -8.9), ('his family', 'h1k_trailer_jb', 64.45, -0.8), ('end of it', 'h1k_murder_ride', 194.9, -5.3),
  ('survival rate', 'dr_send_clown', 41.2, -1.9)], "he's just"))
# #7 Killer Klowns 45%
X.append(sec('s05', [(0, 'kk_puppet', 77.95, -1.8), ('they land', 'kk_mgm', 14.6, -2.5), ('wrap people', 'kk_mgm', 78.7, -6.4),
  ('drink them', 'kk_mgm', 81.5, -3.5), ('dozens', 'kk_giant', 225.5, -1.6), ('but they have', 'kk_giant', 247.1, -2.9),
  ('their noses', 'kk_puppet', 76.45, -1.2), ('one shot', 'kk_puppet', 82.75, -3.0), ('so if you', 'kk_mgm', 329.8, -4.0),
  ('survival rate', 'kk_puppet', 77.95, -1.8)], 'so if you'))
# #6 Frendo 40%
X.append(sec('s06', [(0, 'cc_bench', 108.7, -3.9), ("friendo isn't", 'cc_trailer_shudder', 30.5, -1.8), ('the whole town', 'cc_trailer_shudder', 39.2, -1.5),
  ('the mayor', 'cc_trailer_shudder', 31.3, -1.4), ('all wearing', 'cc_trailer_shudder', 134.5, -0.8), ('same smiling', 'cc_bench', 108.7, -3.9), ('and they hunt', 'cc_run', 6.3, -2.5),
  ('chainsaws', 'cc_trailer_shudder', 92.6, -1.3), ('crossbows', 'cc_run', 8.9, -2.1), ("they're only", 'cc_bench', 99.85, -1.75),
  ('but when', 'cc_run', 63.8, -4.1), ('survival rate', 'cc_bench', 108.7, -3.9)], "they're only"))
# #5 Pennywise (1990) 30%
X.append(sec('s07', [(0, 'it90_clipzone', 194.3, -16.8), ('he comes back', 'it90_clipzone', 234.1, -8.5), ('takes georgie', 'it90_clipzone', 176.5, -4.0),
  ('and can turn', 'it90_clipzone', 261.8, -2.0), ("he's beaten", 'it90_clipzone', 277.5, -14.3), ('and as an adult', 'it90_clipzone', 200.0, -10.0),
  ('survival rate', 'it90_clipzone', 236.0, -6.5)], "he's beaten"))
# #4 Pennywise (2017) 25%
X.append(sec('s08', [(0, 'it17_wbuk', 1075.8, -2.0), ('in derry', 'it17_wbuk', 456.8, -2.7), ('and he can', 'it17_battle', 398.4, -0.8), ('anywhere', 'it17_battle', 237.0, -1.9),
  ('in the sewer', 'it17_wbuk', 1201.4, -1.5), ('library', 'it17_wbuk', 577.6, -0.7), ('or a slideshow', 'it17_wbuk', 712.0, -4.5),
  ('he takes', 'it17_georgie', 411.2, -4.7), ('patrick', 'it17_wbuk', 1158.3, -4.0), ('and the losers', 'it17_battle', 253.4, -2.4),
  ('alone at', 'it17_battle', 249.8, -3.5), ('survival rate', 'it17_wbuk', 1350.3, -5.2)], 'and the losers'))
# #3 Pennywise (2019) 15%
X.append(sec('s09', [(0, 'it2_wb', 79.8, -4.0), ('and this time', 'it2_wb', 107.5, -2.9), ('he kills', 'it2_wb', 553.1, -8.0),
  ('lures a little', 'it2_wb', 547.8, -2.7), ('and stabs', 'it2_final', 164.0, -1.0), ('eddie through', 'it2_final', 165.1, -1.0),
  ('it takes', 'it2_final', 491.0, -2.5), ('and shouting', 'it2_final', 487.1, -3.7), ('until he shrinks', 'it2_final', 493.7, -1.9),
  ('finally dies', 'it2_final', 563.7, -2.8), ("you won't", 'it2_wb', 132.7, -8.5)], 'it takes'))
# #2 Art (Terrifier) 6%
X.append(sec('s10', [(0, 't1_meet_hd', 65.3, -2.2), ("he doesn't run", 't1_meet_hd', 101.3, -2.2), ("and he doesn't", 't1_meet_hd', 222.4, -2.2),
  ('he just keeps', 't1_meet_hd', 461.0, -2.5), ('and he goes', 't1_meet_hd', 441.8, -1.6), ('one night', 't1_meet_hd', 448.2, -1.8),
  ('the only', 't1_meet_hd', 193.3, -2.2), ('so badly', 't1_meet_hd', 196.8, -2.2), ('survival rate', 't1_meet_hd', 373.05, -3.1)], 'the only'))
# #1 Art (Terrifier 2) 3%
X.append(sec('s11', [(0, 't2_costume_hd', 83.8, -2.6), ('comes back', 't2_cafe_hd', 37.6, -2.4), ('kills the', 't2_sienna_hd', 152.4, -3.2),
  ('and spends', 't2_costume_hd', 292.5, -4.0), ('hunting sienna', 't2_sienna_hd', 209.5, -6.0), ('and fighting', 't2_cafe_hd', 276.85, -1.4),
  ('because death', 't2_cafe_hd', 270.8, -2.2), ('even sienna', 't2_sienna_hd', 308.35, -10.6), ('and he still', 't2_cafe_hd', 81.75, -1.3),
  ('survival rate', 't2_cafe_hd', 260.1, -3.0)], 'because death'))
X.append(sec('s12', [(0, 'zl_clown_cc', 25.15, -2.2), ('to one', 't2_cafe_hd', 260.1, -3.0), ('tell me', 'kk_mgm', 329.8, -4.0), ('which clown', 'kk_giant', 247.1, -2.9),
  ('and maybe', 'kk_mgm', 14.6, -2.5), ('circus', 'kk_puppet', 77.95, -1.8)], pad=2.5,
  extra=[('title', ['YOUR PICK?'], 'tell me', 'and maybe'), ('title', ['STAY AWAY', '!FROM THE CIRCUS'], 'and maybe', 999)]))
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
FILM = [('zl_', 'Zombieland (2009)'), ('pg', 'Poltergeist (2015)'), ('dr_', "The Devil's Rejects (2005)"), ('h1k_', 'House of 1000 Corpses (2003)'),
        ('kk_', 'Killer Klowns from Outer Space (1988)'), ('cc_', 'Clown in a Cornfield (2025)'), ('it90_', 'It (1990)'), ('it17_', 'It (2017)'),
        ('it2_', 'It Chapter Two (2019)'), ('t1_', 'Terrifier (2016)'), ('t2_', 'Terrifier 2 (2022)')]
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
DARK = ['cc_run', 'cc_trailer_shudder', 'cc_bench', 'pg15_trailer', 'pg_clown_20th', 'it2_wb', 'it2_final', 'it17_battle', 'h1k_murder_ride', 't1_meet_hd']
P = {'sections': X, 'tiers': TIERS, 'gamma': {k: 1.28 for k in DARK}, 'bar': {'zl_clown_cc': 835}}  # bottom bar over the Clips & Chill corner mark (reads as letterbox)
json.dump(P, open(D + 'edl.json', 'w'), indent=1)
print(len(X), 'sections')
