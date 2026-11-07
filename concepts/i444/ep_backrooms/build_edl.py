# Backrooms special EDL builder (11/7 KST). Owner-approved script_v1.md, voice/ (Adam, tightened), shots.py (filled on the laptop
# from verified frames, see shot_plan.md) -> edl.json for render_br.py.
#
# What is new against the EP04 builder (../ep04/build_edl_v3.py):
# - INSERTS split a voice take between two words and put something voiceless in the gap:
#     choice  0.9 s pause after "So what do you do?" with TURN BACK / KEEP GOING on screen (the running shot keeps playing)
#     film    a real film line with its own audio and a bottom subtitle (Naren, Clark, Bobby, Kat, Clark, Clark, Phil)
#     hum     the near-silence before Captain Clark walks in (room tone only, music almost gone)
#     thud    a short voiceless lead-in for the heavy thud that opens s09
#   A section is one take cut into pieces at the split points (the middle of the pause after the anchor phrase); every time in
#   shots.py is take time (an exact script phrase, as before) and is moved past the inserts here.
# - The survival number: a corner overlay from s01 ("The number in the corner") to s10's end card, a drop animation on every
#   spoken percentage (the new number lands big in the centre, then flies into the corner), a place name at each stage start.
# usage: python build_edl.py   -> edl.json   (then python qa/caption_coverage.py)
import json, re, os, subprocess
D = os.path.dirname(os.path.abspath(__file__)) + '/'
W = json.load(open(D + 'voice/words.json'))
LEAD = 0.08
SFX = '../ep03/sfx/'
G = {'whoosh': -18, 'fill': -20, 'stamp': -12, 'slam': -8}
def norm(s): return re.sub(r"[^a-z0-9']", '', s.lower().replace('-', ''))
def find(seg, phrase):   # 'so what do you do#2' = the 2nd occurrence -> (first word index, last word index)
    phrase, _, k = phrase.partition('#'); k = int(k or 1)
    ws = [norm(w[2]) for w in W[seg]]; ph = [norm(p) for p in phrase.split()]
    for i in range(len(ws) - len(ph) + 1):
        if ws[i:i + len(ph)] == ph:
            k -= 1
            if k == 0: return i, i + len(ph) - 1
    raise KeyError((seg, phrase))
def at(seg, phrase): return W[seg][find(seg, phrase)[0]][0]
def T(seg, x): return x if isinstance(x, (int, float)) else round(max(0, at(seg, x) - LEAD), 3)
def take_len(seg):
    try: return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', D + f'voice/{seg}.mp3']))
    except Exception: return json.load(open(D + f'voice/{seg}.json'))['character_end_times_seconds'][-1] + 0.05
def split_after(seg, phrase):
    """middle of the pause after the phrase's last word (the take's end when it is the last word)"""
    j = find(seg, phrase)[1]; ws = W[seg]
    return round((ws[j][1] + ws[j + 1][0]) / 2, 3) if j + 1 < len(ws) else None
TODO = None
def ins(after, dur, kind, shots=(), sub=None, q=None):
    """after: phrase (split after its last word), 0 (before the first word) or 'END'; shots: (t, clip, in[, speed][, opts]) relative
    to the insert start; sub: the film line as a bottom subtitle; q: the question phrase that brings up the choice"""
    return {'after': after, 'dur': dur, 'kind': kind, 'shots': [list(s) for s in shots], 'sub': sub, 'q': q}
def sec(voice, shots, inserts=(), extra=(), pad=0.05, clip_db=-99):
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
    S = {'voice': voice, 'len': L, 'take': round(tl, 3), 'pieces': pieces, 'clip_audio_db': clip_db, 'shots': [], 'overlays': [], 'sfx': [],
         'duck': [], 'inserts': [{k: x[k] for k in ('kind', 'split', 's0', 's1', 'sub')} for x in I]}
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
    # inserts with their own picture: cut the running shot, play the insert shots, then resume
    for x in I:
        if not x['shots']: continue
        s0, s1 = x['s0'], x['s1']
        before = [s for s in main if s[0] < s0 - 1e-6]; after = [s for s in main if s[0] >= s0 - 1e-6]
        end_ins = s1 >= L - 0.15   # an insert at the take's end runs to the section end: nothing resumes after it
        for s in after:
            if s[0] < s1: s[0] = s1   # nothing main starts inside the insert
        if end_ins: after = []
        nxt = after[0] if after else None
        if nxt is not None and nxt[0] - s1 <= 0.6:
            sp = nxt[3] if len(nxt) > 3 and isinstance(nxt[3], (int, float)) and nxt[3] > 0 else 1.0
            back = nxt[0] - s1
            if nxt[2] - back * sp >= 0: nxt[2] = round(nxt[2] - back * sp, 3)
            nxt[0] = s1
        elif before and not end_ins:
            p = before[-1]; sp = p[3] if len(p) > 3 and isinstance(p[3], (int, float)) and p[3] > 0 else 1.0
            cont = [s1, p[1], round(p[2] + (s0 - p[0]) * (sp if sp > 0 else 1.0), 3), *p[3:]]
            after.insert(0, cont)
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
        elif x['kind'] == 'hum': S['duck'].append([x['s0'], x['s1'], -26])
        elif x['kind'] == 'thud': S['sfx'].append([x['s0'], SFX + 'slam.wav', G['slam']])
        elif x['kind'] == 'choice':
            q = M(T(voice, x['q'])) if x['q'] else x['s0'] - 0.6
            S['overlays'] += [['choice', 0, q, x['s1']], ['choice', 1, x['s1'], x['s1'] + 1.15]]
            S['sfx'] += [[q, SFX + 'whoosh.wav', G['whoosh']], [x['s1'], SFX + 'fill.wav', G['fill']]]
    def MT(v): return v if isinstance(v, (int, float)) and v >= 900 else M(T(voice, v))
    S['overlays'] += [[k, val, MT(a), MT(b)] for k, val, a, b in extra]
    S['_M'] = M
    return S
X = []
exec(open(D + 'shots.py', encoding='utf-8').read())   # appends one sec(...) per section, s00..s11 (see shot_plan.md)
ORDER = ['s00', 's01', 's02', 's03', 's04', 's05', 's06', 's07', 's08', 's09', 's10', 's11']
assert sorted(S['voice'] for S in X) == ORDER, [S['voice'] for S in X]
X.sort(key=lambda S: ORDER.index(S['voice']))
# ---- the survival number, place names, the end card ----
STAGE = {'s02': ('THE SLIT', 90, 'ninety percent'), 's03': ('THE MAP', 70, 'seventy percent'), 's04': ('THE LAUNDRY ROOM', 40, 'forty percent'),
         's05': ('THE STILL LIFES', 15, 'fifteen percent'), 's06': ('AFTER HIM', 10, 'ten percent'), 's07': ('YOUR OLD HOME', 7, 'seven percent'),
         's08': ('THE DINING ROOM', 5, 'five percent'), 's09': ('CAPTAIN CLARK', 2, 'two percent'), 's10': ('ASYNC', None, None)}
DROP = 1.5   # drop overlay length: punch-in 0.14 s, hold 1.0 s, fly into the corner 0.38 s
cur = None
for S in X:
    v = S['voice']; M = S.pop('_M'); L = S['len']
    if v == 's01':   # the corner comes in on "the number in the corner", at 100%
        a = M(T(v, 'the number in the corner')) + 0.35
        S['overlays'].append(['corner', {'p': 100, 'fin': 0.35}, a, L]); S['sfx'].append([a, SFX + 'whoosh.wav', G['whoosh']]); cur = 100
    if v in STAGE:
        name, new, phrase = STAGE[v]
        p0 = next((x['s1'] for x in S['inserts'] if x['kind'] == 'thud'), 0.0) + 0.2
        S['overlays'].append(['place', name, p0, p0 + 3.4]); S['sfx'].append([p0, SFX + 'whoosh.wav', G['whoosh']])
        end = L
        if v == 's10': end = M(T(v, 'one out of five'))
        if new is not None:
            d0 = M(at(v, phrase)) - 0.05
            S['overlays'].append(['corner', {'p': cur}, 0.0, d0])
            S['overlays'].append(['drop', {'p': new, 'hold': 1.0}, d0, d0 + DROP])
            S['overlays'].append(['corner', {'p': new}, d0 + DROP, end])
            S['sfx'] += [[d0, SFX + 'stamp.wav', G['stamp']], [d0 + 1.0, SFX + 'whoosh.wav', G['whoosh'] - 4]]
            cur = new
        else:
            S['overlays'].append(['corner', {'p': cur}, 0.0, end])
        if v == 's10':
            S['overlays'].append(['final', None, end, L + 0.5]); S['sfx'].append([end, SFX + 'slam.wav', G['slam'] - 2])
    S['overlays'].sort(key=lambda o: 0 if o[0] == 'corner' else 1)
    for ov in S['overlays']:
        ov[2] = round(max(0.0, ov[2]), 3); ov[3] = round(min(ov[3], L), 3)
    for o in S['overlays']:
        if o[0] == 'date': S['sfx'].append([o[2], SFX + 'stamp.wav', G['stamp'] - 4])
def fit(S):  # (t, clip, in, -clean) -> a speed that keeps the shot inside its clean span (never below 0.4x); insert shots stay 1.0x
    sh = S['shots']
    for k, s in enumerate(sh):
        d = (sh[k + 1][0] if k + 1 < len(sh) else S['len']) - s[0]
        if len(s) > 3 and isinstance(s[3], (int, float)) and s[3] < 0:
            sp = min(1.0, -s[3] * 0.96 / max(d, 0.01))
            if sp < 0.4: print('WARN too short', S['voice'], s[:3], round(d, 2))
            s[3] = round(max(sp, 0.4), 3) if sp < 0.999 else 1.0
        if len(s) > 4 and isinstance(s[4], str): s[4] = {'flip': 1} if s[4] == 'flip' else dict(kv.split('=') for kv in s[4].split(','))
        if len(s) > 4: s[4] = {k: float(v) for k, v in s[4].items()}
        if len(s) > 3 and s[3] is None: s[3] = 1.0
        if len(s) == 3: s.append(1.0)
    S['shots'] = [s for k, s in enumerate(sh) if (sh[k + 1][0] if k + 1 < len(sh) else S['len']) - s[0] > 0.02]
for S in X: fit(S)
VDARK, DARK, ZOOM, BAR = [], [], {}, {}   # filled on the laptop after the first QA pass (shots_grade.py)
exec(open(D + 'shots_grade.py', encoding='utf-8').read()) if os.path.exists(D + 'shots_grade.py') else None
P = {'sections': X, 'gamma': {**{k: 1.25 for k in DARK}, **{k: 1.4 for k in VDARK}}, 'zoom': ZOOM, 'bar': BAR}
json.dump(P, open(D + 'edl.json', 'w'), indent=1)
tot = sum(S['len'] for S in X)
print(len(X), 'sections', f'{int(tot // 60)}:{tot % 60:04.1f}', sum(len(S['shots']) for S in X), 'shots')
