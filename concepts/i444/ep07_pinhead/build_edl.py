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
# EP07 v2 (owner 11/04): the cold open and every entry cut to victims being hurt (scout scans 11/04, gore allowed), each cut on its word
# with a caption; the stat card comes in ~3-5 s before "survival rate" so the kills play full frame; under the card the main figure sits
# left of x 840 (flip / dx shot options). Shot = (word, clip, in, -clean[, 'flip' | 'dx=..,z=..']).
X.append(sec('s00', [(0, 'hr1_jesuswept', 127.21, -2.0), ('tear', 'hr9_rev', 4106.4, -1.7), ('straight', 'hr1_jesuswept', 120.04, -0.5),
  ('your flesh', 'hr4_straighthell', 27.5, -1.4), ('your skin', 'hr2_finalbattle', 277.1, -2.0), ('gets peeled', 'hr9_rev', 3937.15, -2.5),
  ('while', 'hr9_rev', 3910.91, -1.1), ('still alive', 'hr5_torment', 450.33, -3.7), ('you get', 'hr3_cenoloose', 145.5, -2.1),
  ('into one', 'hr3_cenoloose', 167.0, -1.5), ('cenobites', 'hr4_painface', 295.6, -2.7), ('or trapped', 'hr5_torment', 548.65, -4.0),
  ('inside', 'hr5_torment', 425.1, -3.0), ('forever', 'hr5_torment', 420.85, -1.8), ('and he does', 'hr2_legendary', 55.0, -3.0),
  ('all of it', 'hr9_rev', 4115.2, -5.5), ('calmly', 'hr1_pack4k', 45.7, -5.9), ("we're ranking", 'still_posterwall', 0.0, -5.0)],
  # v5 (owner 11/04 19:51 KST: "the intro is the most important part, words like 'straight' are missing"): every spoken word of the
  # cold open is on screen while it is said, in chunks of 1-4 words that follow the narration exactly (qa/caption_coverage.py checks it)
  extra=[('word', w, a, b) for w, a, b in [
         ('Hooked chains', 0, 'tear'), ('Tear', 'tear', 'straight'), ('Straight through', 'straight', 'your flesh'),
         ('Your flesh', 'your flesh', 'your skin'), ('Your skin', 'your skin', 'gets peeled'), ('Gets peeled off', 'gets peeled', 'while'),
         ("While you're", 'while', 'still alive'), ('Still alive', 'still alive', 'you get'), ('You get turned', 'you get', 'into one'),
         ('Into one of his', 'into one', 'cenobites'), ('Cenobites', 'cenobites', 'or trapped'), ('Or trapped', 'or trapped', 'inside'),
         ('Inside your own head', 'inside', 'forever'), ('Forever', 'forever', 'and he does'), ('And he does', 'and he does', 'all of it'),
         ('All of it', 'all of it', 'calmly'), ('Calmly', 'calmly', "we're ranking"), ("We're ranking", "we're ranking", 'every pinhead'),
         ('Every Pinhead', 'every pinhead', 'by your'), ('By your chance', 'by your', 'of surviving'), ('Of surviving him', 'of surviving', 999)]], clip_db=-20))
for ov in X[-1]['overlays']:  # captions flash and cut out: one word 0.9 s max, a phrase 1.5 s max (EP02 rule); the frame-0 caption holds to its cut
    if ov[0] == 'word' and ov[2] > 0: ov[3] = min(ov[3], ov[2] + (0.9 if ' ' not in ov[1] else 1.5))
s01_end = vdur('s01') + 0.05
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
X.append(sec('s02', [(0, 'hr8_welcome', 66.2, -4.1), ('five friends', 'hr8_trailer', 15.5, -0.75), ('go to a', 'hr8_trailer', 14.6, -0.85), ('themed party', 'hr8_welcome', 36.66, -4.0),
  ('where pinhead', 'hr8_cop', 43.4, -4.1), ('mike gets', 'hr8_welcome', 90.8, -3.5), ('and pinhead even', 'hr8_cop', 31.5, -2.1),
  ('then comes', 'hr8_welcome', 84.67, -2.8), ('the host', 'hr8_welcome', 87.5, -3.3), ('drugged all', 'hr8_trailer', 42.66, -0.42),
  ('five and', 'hr8_jake', 66.2, -5.2), ('so those', 'hr8_welcome', 116.5, -3.5), ('but allison', 'hr8_jake', 109.7, -3.4),
  ('only chelsea', 'hr8_trailer', 43.36, -0.48), ('and jake', 'hr8_cop', 33.6, -1.0), ('and when the', 'hr8_welcome', 8.2, -6.4, 'z=1.35,dx=249'),
  ('the real pinhead', 'hr8_welcome', 54.0, -3.0, 'z=1.35,dx=249'), ('while his', 'hr8_welcome', 102.8, -1.4, 'z=1.35,dx=249'), ('tear him', 'hr8_welcome', 104.2, -1.0, 'z=1.35,dx=249'),
  ('survival rate', 'hr8_welcome', 66.2, -4.1, 'z=1.35,dx=249')], 'and when the'))
# #10 Judgment 60%
X.append(sec('s03', [(0, 'hr10_hell4k', 370.2, -1.5), ('this time', 'hr10_judge4k', 17.0, -4.3), ('the stygian', 'hr10_scifinow', 9.6, -1.8),
  ('where an auditor', 'hr10_scifinow', 12.0, -2.2), ('and a jury', 'hr10_judge4k', 475.48, -2.4), ('when detective', 'hr10_hell4k', 315.7, -2.5),
  ('forces his', 'hr10_hell4k', 318.24, -11.8), ('and offers', 'hr10_hell4k', 342.0, -4.0), ('pinhead refuses', 'hr10_judge4k', 523.4, -4.8),
  ('chains rip', 'hr10_judge4k', 568.44, -3.4), ('and drag', 'hr10_hell4k', 349.35, -5.8), ('pinhead has sean', 'hr10_judge4k', 498.6, -4.3),
  ('and he even', 'hr10_judge4k', 560.31, -3.6), ("that's what", 'hr10_judge4k', 584.42, -5.3, 'z=1.35,dx=249'),
  ('survival rate', 'hr10_hell4k', 371.4, -1.3, 'z=1.45,dx=249')], "that's what"))
# #9 Hellbound 55%
X.append(sec('s04', [(0, 'hr2_legendary', 89.8, -6.1), ('pinhead is still', 'hr2_legendary', 53.4, -5.3), ('when tiffany', 'hr2_tiffany', 262.55, -3.0),
  ('the cenobites spare', 'hr2_tiffany', 295.75, -10.0), ('then kirsty', 'hr2_legendary', 50.15, -3.1), ('and he remembers', 'hr2_legendary', 64.45, -3.3),
  ('a moment later', 'hr2_channardtrans', 105.52, -3.3), ('now a brand', 'hr2_channardtrans', 110.32, -1.5), ('cuts through', 'hr2_tiffvs', 154.2, -1.5), ('pinhead and', 'hr2_tiffvs', 194.15, -1.2),
  ('whole crew', 'hr2_tiffvs', 162.5, -1.4), ('in seconds', 'hr2_tiffvs', 156.1, -1.8), ('and kirsty and', 'hr2_legendary', 219.2, -1.0, 'flip'), ('walk out', 'hr2_legendary', 34.75, -4.6, 'z=1.35,dx=249'),
  ('survival rate', 'hr2_legendary', 158.8, -2.6, 'z=1.35,dx=249')], 'and kirsty and'))
# #8 Revelations 50% (owner's 1080p Blu-ray, read directly, never committed)
X.append(sec('s05', [(0, 'hr9_rev', 3880.0, -1.5), ('with a different', 'hr9_rev', 4068.0, -6.0), ('on a trip', 'hr9_rev', 1520.0, -2.5),
  ('nico solves', 'hr9_rev', 1866.0, -2.0), ('and gets dragged', 'hr9_rev', 2173.75, -1.7), ('then claws', 'hr9_rev', 2199.4, -16.0),
  ('by getting his', 'hr9_rev', 2105.0, -1.4), ('before killing', 'hr9_rev', 3274.5, -2.5), ('and wearing his', 'hr9_rev', 3020.0, -2.5),
  ("when steven's", 'hr9_rev', 2330.0, -2.0), ('pinhead flat out', 'hr9_rev', 3951.7, -3.9), ('and takes him', 'hr9_rev', 4024.78, -5.0),
  ('and his cenobites', 'hr9_rev', 3921.0, -6.9), ("and take steven's", 'hr9_rev', 4112.8, -17.0), ('only emma', 'hr9_rev', 4189.48, -15.0),
  ('survival rate', 'hr9_rev', 4204.62, -4.1, 'z=1.35,dx=249')], 'only emma'))
# #7 Hellraiser 1987 40%
X.append(sec('s06', [(0, 'hr1_pack4k', 122.9, -2.6), ('frank solves', 'hr1_pack4k', 10.5, -13.9), ('and the cenobites', 'hr1_pack4k', 6.5, -3.8),
  ('tear him', 'hr1_jesuswept', 124.25, -1.6), ('hook chains', 'hr1_jesuswept', 127.21, -2.0), ('so completely', 'hr1_jesuswept', 131.6, -11.0),
  ('kirsty survives', 'hr1_sights', 2.4, -7.2), ('by making', 'hr1_pack4k', 30.4, -4.0), ('and then reversing', 'hr1_dont', 0.05, -1.85),
  ('before they', 'hr1_dont', 6.95, -1.4), ('survival rate', 'hr1_pack4k', 45.7, -5.9, 'z=1.35,dx=249')], 'and then reversing'))
# #6 Hellseeker 35%
X.append(sec('s07', [(0, 'hr6_painpleasure', 186.4, -4.0), ("kirsty's cheating", 'hr6_pain', 32.5, -3.0), ('so he gets', 'hr6_kirstypack', 121.67, -13.5),
  ('but she makes', 'hr6_kirstypack', 165.0, -11.0), ('she kills three', 'hr6_kirstypack', 268.12, -10.0), ('and then shoots', 'hr6_painpleasure', 175.3, -2.5),
  ('the fifth soul', 'hr6_painpleasure', 178.2, -2.4), ('it works', 'hr6_painpleasure', 184.0, -1.9, 'z=1.35,dx=249'), ('five people', 'hr6_kirstypack', 289.8, -16.0),
  ('survival rate', 'hr6_painpleasure', 180.6, -2.9, 'z=1.35,dx=249')], 'it works'))
# #5 Hellraiser 2022, the Priest 30%
X.append(sec('s08', [(0, 'hr22_bridge', 2.6, -3.6), ('where pinhead', 'hr22_trailer_hulu', 97.5, -2.0), ('the box has', 'hr22_carousel', 498.0, -16.5),
  ('every single', 'hr22_carousel', 140.9, -8.6), ('someone cut', 'hr22_carousel', 264.0, -2.5), ("riley's brother", 'hr22_carousel', 470.0, -3.5),
  ('and the priest', 'hr22_bridge', 23.8, -6.4), ('nora until', 'hr22_trailer_20th', 95.9, -1.5), ('flayed to death', 'hr22_nora', 161.93, -2.3),
  ('riley only', 'hr22_bridge', 0.0, -2.5), ('by stabbing', 'hr22_bridge', 33.0, -4.2), ('final sacrifice', 'hr22_carousel', 415.0, -3.0),
  ('and then turning', 'hr22_bridge', 4.0, -3.0, 'z=1.35,dx=249'), ('survival rate', 'hr22_bridge', 2.6, -3.6, 'z=1.35,dx=249')], 'and then turning'))
# #4 Bloodline 25%
X.append(sec('s09', [(0, 'hr4_pathway', 152.3, -6.2), ('the family of', 'hr4_takesoul', 47.6, -1.65), ('is cursed for', 'hr4_birth', 405.3, -4.3),
  ('and pinhead comes', 'hr4_pathway', 99.5, -4.5), ('in 1996', 'hr4_straighthell', 23.7, -1.7), ('kills john', 'hr4_straighthell', 27.5, -1.4),
  ('in the year', 'hr4_space', 48.2, -10.8), ('he wipes out', 'hr4_painface', 251.2, -1.45), ('crew on', 'hr4_finalbattle', 85.5, -1.75),
  ('space station.', 'hr4_finalbattle', 92.7, -3.1), ('in the end', 'hr4_another', 272.55, -1.15), ('it takes', 'hr4_another', 273.8, -1.25), ('giant puzzle', 'hr4_another', 279.3, -2.0, 'z=1.35,dx=249'),
  ('survival rate', 'hr4_chart', 158.8, -4.9, 'flip=1,z=1.35,dx=249')], 'giant puzzle'))
# #3 Deader 15%
X.append(sec('s10', [(0, 'hr7_returns', 89.2, -4.4), ('a reporter', 'hr7_real', 20.2, -5.9), ('that kills', 'hr7_afraid', 147.9, -1.1),
  ('all because', 'hr7_afraid', 4.55, -3.5), ('when amy', 'hr7_returns', 10.55, -5.4), ('pinhead slaughters', 'hr7_returns', 175.6, -1.55),
  ('the entire cult', 'hr7_returns', 166.2, -1.35), ('in minutes', 'hr7_returns', 142.5, -1.6), ('then tells her', 'hr7_returns', 189.0, -3.0),
  ('and that her', 'hr7_returns', 182.0, -1.5), ("amy's only", 'hr7_returns', 186.5, -2.0), ('survival rate', 'hr7_returns', 200.0, -1.8)], "amy's only"))
# #2 Inferno 8%
X.append(sec('s11', [(0, 'hr5_box', 266.2, -1.7), ('detective', 'hr5_world', 50.9, -20.9), ('opens the box', 'hr5_box', 27.1, -4.0),
  ('and spends', 'hr5_cruelty', 33.5, -13.0), ('until he learns', 'hr5_child', 97.1, -2.3), ('pinhead the entire', 'hr5_box', 266.2, -1.7),
  ("and he's already", 'hr5_torment', 425.1, -12.2), ("there's no fight", 'hr5_torment', 420.85, -1.8), ('no deal', 'hr5_torment', 548.65, -4.0, 'z=1.35,dx=249'),
  ('just an eternity', 'hr5_torment', 430.0, -7.0, 'z=1.35,dx=249'), ('survival rate', 'hr5_box', 266.2, -1.7, 'z=1.35,dx=249')], 'no deal'))
# #1 Hell on Earth 5%
X.append(sec('s12', [(0, 'hr3_iamtheway', 131.0, -1.8), ('pinhead breaks', 'hr3_pillar', 128.0, -7.8), ('with no box', 'hr3_pillar', 230.15, -3.9),
  ('massacres', 'hr3_club', 124.8, -1.9), ('entire nightclub', 'hr3_dancefloor', 60.0, -1.2), ('and turns his', 'hr3_cenoloose', 76.14, -1.26),
  ('brand new', 'hr3_cenoloose', 18.12, -3.7), ('who go on', 'hr3_cenoloose', 99.13, -4.7), ('kill the police', 'hr3_cenoloose', 138.31, -6.0),
  ('only joey', 'hr3_iamtheway', 129.3, -1.25), ('turned into', 'hr3_iamtheway', 127.95, -2.9), ('can send', 'hr3_finalbattle', 343.0, -3.1),
  ("if he's the one", 'hr3_iamtheway', 9.6, -3.3, 'z=1.35,dx=249'), ('survival rate', 'hr3_pillar', 224.35, -3.1, 'z=1.35,dx=249')], "if he's the one"))
# outro (v3, owner 11/04: sincere small-channel subscribe ask): calm Pinhead / box shots, a plain subscribe button, ends on the box closing
X.append(sec('s13', [(0, 'hr1_pack4k', 62.4, -3.4), ('to a demon', 'hr3_pillar', 230.15, -3.9), ('tell me', 'hr1_pack4k', 10.5, -13.9),
  ('and honestly', 'hr1_pack4k', 45.7, -5.9), ('rewatching', 'hr5_box', 27.1, -4.0), ('as a small', 'hr2_legendary', 89.8, -6.1),
  ('and it decides', 'hr7_returns', 189.1, -4.0), ('thank you', 'hr4_pathway', 172.0, -11.0), ('keep that', 'hr1_dont', 0.05, -1.85)], pad=2.0,
  extra=[('title', ['WHICH BOX', '!WOULD YOU OPEN?'], 'tell me', 'and honestly'), ('png', 'tiles/subscribe.png', 'your subscribe', 'thank you'),
         ('title', ['KEEP THAT BOX', '!CLOSED'], 'keep that', 999)]))
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
VDARK = ['hr4_pathway', 'hr4_space', 'hr4_painface', 'hr4_finalbattle', 'hr22_carousel', 'hr22_bridge', 'hr22_cenofeat', 'hr22_trailer_20th']  # v4: shots under luma 8 in v3
DARK = ['hr2_legendary', 'hr1_sights', 'hr10_judge4k', 'hr3_club', 'hr6_painpleasure', 'hr6_pain', 'hr22_nora', 'hr5_torment', 'hr8_welcome', 'hr8_jake', 'hr8_cop', 'hr10_souls', 'hr22_carousel', 'hr3_pillar', 'hr5_box', 'hr5_cruelty', 'hr7_returns', 'hr7_afraid', 'hr9_trailer_rt']
P = {'sections': X, 'tiers': TIERS, 'gamma': {**{k: 1.25 for k in DARK}, **{k: 1.4 for k in VDARK}},
     'zoom': {'hr3_dancefloor': 1.36, 'hr22_trailer_20th': 1.34, 'hr22_nora': 1.55, 'hr3_iamtheway': 1.36, 'hr3_bad_dreams': 1.36, 'hr10_judge4k': 1.2, 'hr10_hell4k': 1.2}}  # 4:3 pillarbox filled; Boxoffice corner bug cropped
json.dump(P, open(D + 'edl.json', 'w'), indent=1)
print(len(X), 'sections')
