# EP08 The Conjuring Universe EDL builder (11/9 KST).
# = ../ep_backrooms/build_edl.py (a voice take cut into pieces with voiceless INSERTS between them: real film lines with their own
#   audio and a bottom subtitle; owner 11/7 on Backrooms: film dialogue and real scene audio "매우 좋아, 앞으로도 더 많이")
# + the ranked-list overlays of ../ep04/build_edl_v3.py (rank card 0-2.9 s, the stat card from CARD_AT with the entry's OWN demon,
#   a film label per run of one film until the card, the cold-open captions, the rules demo card in s01).
# shots.py (written on the laptop from verified frames, see beats_v1.md) appends one sec(...) per section, s00..s11:
#   shot   (phrase, clip, in_s, -clean_s[, opts])  phrase = exact script words (TAKE time; 'name#2' = 2nd occurrence) or a number
#   insert ins(after_phrase, seconds, 'film', shots=[(t, clip, in_s, 1.0, opts)], sub='the line exactly as spoken')
#          for a film line: in_s = 0.25 s before its first word, seconds = line length + 0.35 s, opts 'lufs=-17'
#   opts   z, dx, dy (px), flip=1, g (gamma), a (clip audio dB), lufs (levelled clip audio), f=<film key> (label for a mixed clip)
# Every insert must sit BEFORE the entry's card phrase (the card takes the right half of the frame from then on).
# usage: python build_edl.py   -> edl.json   (then python qa/caption_coverage.py). Build it on the laptop: its ffprobe gives the
# decoded take lengths the renderer uses (cloud ffprobe 6.1 pads mp3s by ~0.05 s).
import json, re, os, subprocess
D = os.path.dirname(os.path.abspath(__file__)) + '/'
W = json.load(open(D + 'voice/words.json'))
ST = {e['sec']: e for e in json.load(open(D + 'stats.json'))['entries']}
STATS = json.load(open(D + 'stats.json'))['stats']   # STRENGTH, INTELLIGENCE, KILL COUNT, POSSESSION
LEAD = 0.08
SFX = '../ep03/sfx/'
G = {'whoosh': -16, 'fill': -20, 'stamp': -12, 'slam': -8}
ORDER = ['s00', 's01', 's02', 's03', 's04', 's05', 's06', 's07', 's08', 's09', 's10', 's11']
# ---- per entry: stat-card tile key, rank-card film line, the card phrase (the entry's last line before "Survival rate") ----
TILE = {'s02': 'ach', 's03': 'a14', 's04': 'c1', 's05': 'c2', 's06': 'lr', 's07': 'cr', 's08': 'dm', 's09': 'n2', 's10': 'n1'}
SHORT = {'s02': 'Annabelle Comes Home (2019)', 's03': 'Annabelle (2014)', 's04': 'The Conjuring (2013)', 's05': 'The Conjuring 2 (2016)',
         's06': 'The Conjuring: Last Rites (2025)', 's07': 'Annabelle: Creation (2017)', 's08': 'The Devil Made Me Do It (2021)',
         's09': 'The Nun II (2023)', 's10': 'The Nun (2018)'}
CARD_AT = {'s02': 'leave the glass shut', 's03': 'never offer it your soul', 's04': 'she only wants the mother', 's05': 'learn the name',
           's06': 'if it wants you', 's07': "if you're the weakest", 's08': "you can't run from a curse", 's09': "you're not from saint",
           's10': "if the vatican's best"}
TIERS = [['S', 'Slaughtered', 25], ['A', 'Almost Dead', 40], ['B', 'Better Run', 50], ['C', 'Close Call', 60], ['D', "Don't Worry", 80],
         ['E', 'Easy', 101]]
# film label (top right) by clip prefix; the cold-open clips and mixed compilations are mapped by name or by the shot's f= option
FILMS = {'ach': 'Annabelle Comes Home (2019)', 'a14': 'Annabelle (2014)', 'c1': 'The Conjuring (2013)', 'c2': 'The Conjuring 2 (2016)',
         'lr': 'The Conjuring: Last Rites (2025)', 'cr': 'Annabelle: Creation (2017)', 'dm': 'The Conjuring: The Devil Made Me Do It (2021)',
         'n2': 'The Nun II (2023)', 'n1': 'The Nun (2018)'}
CO = {'co_burn': 'n2', 'co_burn_4k': 'n2', 'co_buried': 'n1', 'co_buried_b': 'n1', 'co_neck': 'n2', 'co_stab': 'dm', 'co_mother': 'c1',
      'co_doll': 'ach', 'co_valak0': 'n1', 'spooky_nun': 'n1'}
MIXED = {'universe'}   # compilation clips: every shot needs f=<key>
def norm(s): return re.sub(r"[^a-z0-9']", '', s.lower().replace('-', ''))
def find(seg, phrase):   # 'learn the name#2' = the 2nd occurrence -> (first word index, last word index)
    phrase, _, k = phrase.partition('#'); k = int(k or 1)
    ws = [norm(w[2]) for w in W[seg]]; ph = [norm(p) for p in phrase.split()]
    for i in range(len(ws) - len(ph) + 1):
        if ws[i:i + len(ph)] == ph:
            k -= 1
            if k == 0: return i, i + len(ph) - 1
    raise KeyError((seg, phrase))
def at(seg, phrase): return W[seg][find(seg, phrase)[0]][0]
def T(seg, x): return x if isinstance(x, (int, float)) else round(max(0, at(seg, x) - LEAD), 3)
def AL(seg): return json.load(open(D + f'voice/{seg}.json'))
def take_len(seg):
    try: return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', D + f'voice/{seg}.mp3']))
    except Exception: return AL(seg)['character_end_times_seconds'][-1] + 0.05
def num_onset(seg):   # take time of the first letter after the last "Survival rate"
    a = AL(seg); s = ''.join(a['characters']); i = s.rfind('Survival rate') + len('Survival rate')
    while not s[i].isalnum(): i += 1
    return a['character_start_times_seconds'][i]
_PCM = {}
def _pcm(seg):
    if seg not in _PCM:
        import numpy as np
        _PCM[seg] = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', D + f'voice/{seg}.mp3', '-ac', '1', '-ar', '48000',
                                                           '-f', 's16le', '-']), np.int16).astype('float32') / 32768
    return _PCM[seg]
def split_after(seg, phrase):
    """the middle of the longest run under -45 dB between 0.7 s before the phrase's last word ends and the next word + 0.1 s
    (Backrooms v3, owner 11/7 1:18: word times run up to ~0.4 s late; a take is never cut inside a sound)"""
    import numpy as np
    j = find(seg, phrase)[1]; ws = W[seg]
    if j + 1 >= len(ws): return None
    x = _pcm(seg); lo, hi = max(0.0, ws[j][1] - 0.7), ws[j + 1][0] + 0.1; step = 0.01
    ts = np.arange(lo, hi, step); quiet = [20 * np.log10(np.sqrt(np.mean(x[int(t * 48000):int((t + 0.02) * 48000)] ** 2)) + 1e-9) < -45 for t in ts]
    best, run0 = (0, None), None
    for k, q in enumerate(quiet + [False]):
        if q and run0 is None: run0 = k
        if not q and run0 is not None:
            if k - run0 > best[0]: best = (k - run0, run0)
            run0 = None
    if best[0] >= 5: return round(lo + (best[1] + best[0] / 2) * step + 0.01, 3)
    print('WARN no silence to split in', seg, 'after', repr(phrase)); return round((ws[j][1] + ws[j + 1][0]) / 2, 3)
TODO = None
def ins(after, dur, kind='film', shots=(), sub=None):
    """after: phrase (split after its last word), 0 (before the first word) or 'END'; shots: (t, clip, in[, speed][, opts]) relative
    to the insert start; sub: the film line as a bottom subtitle, exactly as spoken"""
    return {'after': after, 'dur': dur, 'kind': kind, 'shots': [list(s) for s in shots], 'sub': sub}
def sec(voice, shots, inserts=(), extra=(), pad=None, clip_db=-99, card_at=None):
    pad = pad if pad is not None else (0.15 if voice in ST else 0.05)   # short pads, the narration runs on (owner 11/04)
    tl = take_len(voice); I = []
    for x in inserts:
        sp = 0.0 if x['after'] == 0 else tl if x['after'] == 'END' else (split_after(voice, x['after']) or tl)
        I.append({**x, 'split': sp})
    I.sort(key=lambda x: x['split'])
    for k, x in enumerate(I): x['s0'] = round(x['split'] + sum(y['dur'] for y in I[:k]), 3); x['s1'] = round(x['s0'] + x['dur'], 3)
    def M(t):   # take time -> section time; a time just before a split (an anchor's 0.08 s lead) counts as after it
        return round(t + sum(x['dur'] for x in I if x['split'] <= t + 0.15 and not (x['split'] == tl and t < tl - 0.15)), 3)
    L = round(tl + sum(x['dur'] for x in I) + pad, 3)
    b = sorted({0.0, tl, *[x['split'] for x in I]}); pieces = []
    for k in range(len(b) - 1):
        if b[k + 1] - b[k] > 0.01: pieces.append([b[k], b[k + 1], round(b[k] + sum(x['dur'] for x in I if x['split'] <= b[k] + 1e-6), 3)])
    S = {'voice': voice, 'len': L, 'take': round(tl, 3), 'pad': pad, 'pieces': pieces, 'clip_audio_db': clip_db, 'shots': [], 'overlays': [],
         'sfx': [], 'duck': [], 'inserts': [{k: x[k] for k in ('kind', 'split', 's0', 's1', 'sub')} for x in I]}
    main = []
    TF = os.environ.get('TESTFILL') == '1'   # pipeline test only: TODO in-points become 5.0 s with a long clean span
    for x in I:
        for s in x['shots']:
            if s[2] is None and TF: s[2] = 5.0
        x['shots'] = [s for s in x['shots'] if s[2] is not None]
    for s in shots:
        s = list(s)
        if TF and s[2] is None: s[2] = 5.0; s[3] = -30.0
        if s[2] is None: print('TODO shot skipped', voice, s[0], s[1]); continue
        main.append([M(T(voice, s[0])), *s[1:]])
    main.sort(key=lambda s: s[0])
    for x in I:   # an insert with its own picture cuts the running shot, plays its shots at 1.0x, then the running shot resumes
        if not x['shots']: continue
        s0, s1 = x['s0'], x['s1']
        before = [s for s in main if s[0] < s0 - 1e-6]; after = [s for s in main if s[0] >= s0 - 1e-6]
        end_ins = s1 >= L - 0.15
        for s in after:
            if s[0] < s1: s[0] = s1
        if end_ins: after = []
        nxt = after[0] if after else None
        if nxt is not None and nxt[0] - s1 <= 0.6:
            sp = nxt[3] if len(nxt) > 3 and isinstance(nxt[3], (int, float)) and nxt[3] > 0 else 1.0
            back = nxt[0] - s1
            if nxt[2] - back * sp >= 0: nxt[2] = round(nxt[2] - back * sp, 3)
            nxt[0] = s1
        elif before and not end_ins:
            p = before[-1]; sp = p[3] if len(p) > 3 and isinstance(p[3], (int, float)) and p[3] > 0 else 1.0
            after.insert(0, [s1, p[1], round(p[2] + (s0 - p[0]) * sp, 3), *p[3:]])
        own = [[round(s0 + s[0], 3), *s[1:]] for s in x['shots']]
        for s in own:
            if len(s) > 4 and isinstance(s[4], str): s[4] = dict(kv.split('=') for kv in s[4].split(','))
        for s in own: s.append({'ins': 1}) if len(s) < 5 else s[4].update({'ins': 1})
        for s in own:
            if len(s) == 4: s.insert(3, 1.0)
        main = before + own + after
    S['shots'] = main
    for x in I:
        if x['kind'] == 'film':
            S['duck'].append([x['s0'], x['s1'], -10])
            if x['sub']: S['overlays'].append(['sub', x['sub'], x['s0'] + 0.05, x['s1'] - 0.05])
    if voice in ST:   # rank card, then the stat card with this entry's demon from the card phrase to the section end
        e = ST[voice]; film = SHORT[voice]; a = M(T(voice, card_at or CARD_AT[voice]))
        S['overlays'].insert(0, ['rank', [e['rank'], e['villain'], film], 0.0, 2.9])
        tp = round(M(num_onset(voice)) - 0.05 - a, 3)
        S['overlays'].append(['stats', {'name': e['villain'], 'tile_png': f'tiles/{TILE[voice]}.png', 'stats': dict(zip(STATS, e['v'])),
                                        'pct': e['pct'], 't_pct': tp, 'dur': round(L - a, 3), 'film': film}, a, 999])
        S['sfx'] += [[a, SFX + 'whoosh.wav', G['whoosh']], [a + 0.3, SFX + 'fill.wav', G['fill']], [a + tp, SFX + 'stamp.wav', G['stamp']]]
        S['card_at'] = a
        for x in I:
            if x['s1'] > a - 0.1: print('WARN insert after the card phrase', voice, x['sub'])
    def MT(v): return v if isinstance(v, (int, float)) and v >= 900 else M(T(voice, v))
    S['overlays'] += [[k, val, MT(a), MT(b)] for k, val, a, b in extra]
    S['_M'] = M
    return S
X = []
exec(open(D + 'shots.py', encoding='utf-8').read())   # appends one sec(...) per section, s00..s11 (see beats_v1.md)
assert sorted(S['voice'] for S in X) == ORDER, [S['voice'] for S in X]
X.sort(key=lambda S: ORDER.index(S['voice']))
# ---- the rules demo card (s01): the four bars fill as each stat is named, "??%" on "your survival rate" ----
for S in X:
    if S['voice'] == 's01' and not any(o[0] == 'stats' for o in S['overlays']):
        M = S['_M']; tr = round(M(T('s01', 'your survival rate')) + LEAD, 3)
        S['overlays'].append(['stats', {'name': "TONIGHT'S DEMON", 'tile_png': '../ep04/tiles/mystery.png',
                                        'stats': {'STRENGTH': 6, 'INTELLIGENCE': 7, 'KILL COUNT': 5, 'POSSESSION': 8}, 'pct': '??',
                                        'dur': S['len'], 't_pct': tr,
                                        'reveal': [round(M(T('s01', w)) + LEAD, 3) for w in ('strength', 'intelligence', 'kill count', 'and possession')]},
                              0.0, 999])
        S['sfx'] += [[0.0, SFX + 'whoosh.wav', G['whoosh']], [tr, SFX + 'stamp.wav', G['stamp']]]
        S['card_at'] = 0.0
def opts(o):
    if isinstance(o, dict): d = o
    elif o == 'flip': d = {'flip': 1}
    else: d = dict(kv.split('=') for kv in o.split(','))
    return {k: (v if k == 'f' else float(v)) for k, v in d.items()}
def fit(S):  # (t, clip, in, -clean) -> a speed that keeps the shot inside its clean span (never below 0.4x); insert shots stay 1.0x
    sh = S['shots']
    for k, s in enumerate(sh):
        d = (sh[k + 1][0] if k + 1 < len(sh) else S['len']) - s[0]
        if len(s) > 3 and isinstance(s[3], (int, float)) and s[3] < 0:
            sp = min(1.0, -s[3] * 0.96 / max(d, 0.01))
            if sp < 0.4: print('WARN too short', S['voice'], s[:3], round(d, 2))
            s[3] = round(max(sp, 0.4), 3) if sp < 0.999 else 1.0
        if len(s) > 4: s[4] = opts(s[4])
        if len(s) > 3 and s[3] is None: s[3] = 1.0
        if len(s) == 3: s.append(1.0)
    S['shots'] = [s for k, s in enumerate(sh) if (sh[k + 1][0] if k + 1 < len(sh) else S['len']) - s[0] > 0.02]
for S in X: fit(S)
def film_key(name, op):
    if op.get('f'): return op['f']
    if name in MIXED: print('WARN mixed clip without f=', name); return None
    if name in CO: return CO[name]
    k = name.split('_')[0]
    return k if k in FILMS else None
for S in X:   # a film label per run of one film, gone once the stat card takes the frame (none under the rules card)
    end = S.pop('card_at', 999); runs = []
    for t, n, tin, sp, *rest in S['shots']:
        if t >= end: break
        k = film_key(n, rest[0] if rest else {})
        if runs and runs[-1][0] == k: continue
        runs.append([k, t])
    for j, (k, t) in enumerate(runs):
        if k: S['overlays'].append(['film', FILMS[k], t, min(end, runs[j + 1][1] if j + 1 < len(runs) else 999)])
    S.pop('_M', None); L = S['len']
    for ov in S['overlays']:
        ov[2] = round(max(0.0, ov[2]), 3); ov[3] = round(min(ov[3], L), 3)
VDARK, DARK, ZOOM, BAR = [], [], {}, {}   # filled on the laptop after the first QA pass (shots_grade.py): BAR = {clip: y} over a mark
exec(open(D + 'shots_grade.py', encoding='utf-8').read()) if os.path.exists(D + 'shots_grade.py') else None
P = {'sections': X, 'tiers': TIERS, 'gamma': {**{k: 1.25 for k in DARK}, **{k: 1.4 for k in VDARK}}, 'zoom': ZOOM, 'bar': BAR}
json.dump(P, open(D + 'edl.json', 'w'), indent=1)
tot = sum(S['len'] for S in X)
print(len(X), 'sections', f'{int(tot // 60)}:{tot % 60:04.1f}', sum(len(S['shots']) for S in X), 'shots',
      sum(len(S['inserts']) for S in X), 'film lines')
