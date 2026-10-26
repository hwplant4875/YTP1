"""Guren no Yumiya - epic orchestral cover for the AoT 3D timelapse (from bar 17 = 0:21.437 of the original).

Builds every part from the verified transcriptions in analysis/parts/, renders one stem per part with the
sample libraries (VSCO-2 CE, SSO, Iowa MIS, Salamander, DRSKit, Karoryfer, Splice one-shots), then mixes.
Lead vocal -> solo cello (verse 1, narration valley) / solo violin 8va (elsewhere) / both (final chorus).
No original audio or stem is used in the output.

usage: python3 -I cover.py [render|mix|all] [--only stem1,stem2]
"""
import json, os, sys, math, subprocess
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt

A = '/tmp/claude-0/aotmusic'
sys.path.insert(0, A + '/tools')
import ens_sampler as E      # noqa: E402
import solo_sampler as S     # noqa: E402

SR = 48000
P = A + '/analysis/parts/'
OUT = A + '/arr/out'
STEMS = OUT + '/stems'
os.makedirs(STEMS, exist_ok=True)

G = json.load(open(A + '/analysis/grid.json'))
BEAT, FIRST = G['beat_s'], G['first_beat_t']
BAR0 = 17                      # cover starts on the bar-17 downbeat (first guitar/orchestra stab)
T0 = FIRST + (BAR0 - 1) * 4 * BEAT
PRE = 0.30                     # tiny pre-roll so attack-compensated samples can start before the stab
LAST_BAR = 232                 # band cut-off is bar 231 beat 3.5; 232+ = tail
END_S = (FIRST + (LAST_BAR - 1) * 4 * BEAT) - T0 + PRE + 7.0
N = int(END_S * SR)


def tb(bar, beat=0.0):
    """grid time (original) of bar/beat"""
    return FIRST + ((bar - 1) * 4 + beat) * BEAT


def tc(t):
    """original time -> cover time"""
    return t - T0 + PRE


SEC = {s['name']: (s['bar_start'], s['bar_end_exclusive']) for s in G['sections']}


def sec_of(bar):
    for s in G['sections']:
        if s['bar_start'] <= bar < s['bar_end_exclusive']:
            return s['name']
    return 'tail'


def part(name):
    for cand in (name + '_verified.json', name + '_final.json', name + '.json'):
        if os.path.exists(P + cand):
            return json.load(open(P + cand)), cand
    raise FileNotFoundError(name)


def keep(n):
    return n.get('bar', 0) >= BAR0 and n['t'] + n.get('d', 0) > T0 - 0.05


def nt(n, midi=None, vel=None, dur=None, **kw):
    d = dict(start_s=tc(n['t']), dur_s=float(dur if dur is not None else n['d']),
             midi=float(n['midi'] if midi is None else midi), vel=float(n.get('vel', 90) if vel is None else vel))
    d.update(kw)
    return d


def fit(x, n=N):
    y = np.zeros((n, 2), np.float32)
    m = min(n, len(x))
    y[:m] = x[:m]
    return y


def place(buf, x, t, gain=1.0):
    i = int(round(t * SR))
    if i < 0:
        x, i = x[-i:], 0
    m = min(len(x), len(buf) - i)
    if m > 0:
        buf[i:i + m] += x[:m] * gain


def load_wav(path, semis=0.0):
    """one-shot -> SR, optionally pitched by varispeed (band-limited soxr resampling, no aliasing)"""
    import librosa
    y, sr = sf.read(path, dtype='float32', always_2d=True)
    if y.shape[1] == 1:
        y = np.repeat(y, 2, 1)
    src = sr * 2 ** (semis / 12)
    if abs(src / SR - 1) > 1e-6:
        y = librosa.resample(np.ascontiguousarray(y.T), orig_sr=src, target_sr=SR, res_type='soxr_hq').T
    return np.ascontiguousarray(y, dtype=np.float32)


def trim(x, length_s, fade_s=0.03):
    n = min(len(x), int(length_s * SR))
    y = x[:n].copy()
    k = min(n, int(fade_s * SR))
    y[n - k:] *= np.linspace(1, 0, k, dtype=np.float32)[:, None] ** 2
    return y


def variants(path, k=4, cents=30, length_s=None, polarity=1, seed=0):
    """k pitch variants of a one-shot (+-cents), so repeated hits are not the same waveform"""
    rng = np.random.default_rng(seed)
    out = []
    for i in range(k):
        c = 0 if i == 0 else rng.uniform(-cents, cents)
        y = load_wav(path, semis=c / 100) * polarity
        out.append(trim(y, length_s) if length_s else y)
    return out


def peak_s(x, win_s=0.05):
    """time of the loudest moment of a one-shot (smoothed energy)"""
    from scipy.ndimage import uniform_filter1d
    e = uniform_filter1d((x.astype(np.float64) ** 2).mean(1), max(1, int(win_s * SR)))
    return float(np.argmax(e)) / SR


SPL = A + '/lib/splice/'
_INST = None


def inst_ranges():
    global _INST
    if _INST is None:
        _INST = E.list_instruments()
    return _INST

# ------------------------------------------------------------------------------------------------------
# section plan
# ------------------------------------------------------------------------------------------------------
LEAD_PLAN = {  # section -> list of (instrument, octave shift)
    'band_entry': [('violin', 12)], 'main_riff': [('violin', 12)],
    'verse1': [('cello', 0)], 'prechorus1': [('cello', 0)],
    'chorus1': [('violin', 12)],
    'verse2': [('violin', 12)], 'prechorus2': [('violin', 12)], 'jaeger_call_response': [('violin', 12)],
    'instrumental_break': [('violin', 12)],
    'narration': [('cello', 0)],
    'bridge': [('violin', 12)], 'build_prechorus3': [('violin', 12)],
    'final_chorus': [('violin', 12), ('cello', 0)],
    'outro_riff': [('violin', 12)], 'outro_groove': [('violin', 12)], 'outro_G_ending': [('violin', 12)],
}
BIG = {'chorus1', 'jaeger_call_response', 'final_chorus', 'outro_G_ending', 'main_riff', 'interlude_riff',
       'outro_riff', 'instrumental_break'}

# narration valley (bars 148-172) has no sung melody: composed cello recitative over the C#m-G#-A-C loop,
# (bar, beat, beats, sounding midi), checked against chords_verified
NARR_CELLO = [
    (149, 0, 2, 57), (149, 2, 2, 56), (150, 0, 2, 61), (150, 2, 1, 59), (150, 3, 1, 57), (151, 0, 3, 56), (151, 3, 1, 54),
    (152, 0, 4, 57), (153, 0, 2, 56), (153, 2, 1, 57), (153, 3, 1, 59), (154, 0, 2, 61), (154, 2, 2, 63), (155, 0, 8, 64)]
_HEAD = [(157, 0, 1, 61), (157, 1, 1, 61), (157, 2, 1, 64), (157, 3, 1, 63), (158, 0, 2, 60), (158, 2, 2, 63), (159, 0, 2, 61),
         (159, 2, 2, 64), (160, 0, 4, 64), (161, 0, 2, 68), (161, 2, 2, 64), (162, 0, 2, 63), (162, 2, 2, 60), (163, 0, 4, 61)]
NARR_CELLO += _HEAD + [(164, 0, 4, 64)] + [(b + 8, bt, n, m) for b, bt, n, m in _HEAD] + [
    (172, 0, 1.5, 64), (172, 1.5, 1.5, 63), (172, 3, 1, 62)]
# violin descant over the second half of the recitative
NARR_VIOLIN = [(b, 0, 4, m) for b, m in zip(range(165, 172), (76, 75, 73, 72, 76, 75, 73))] + [
    (172, 0, 1.5, 76), (172, 1.5, 1.5, 75), (172, 3, 1, 74)]


def grid_notes(spec, section, vel, phrase_bars=4):
    return [dict(t=tb(b, bt), d=n * BEAT * 0.97, bar=b, beat=bt, beats=n, midi=m, vel=vel, section=section,
                 phrase_id=10000 + (b - 148) // phrase_bars) for b, bt, n, m in spec]


def slurred(notes, max_gap=0.06):
    """solo-string note dicts with legato on every note that follows the previous one within max_gap"""
    out = []
    for k, q in enumerate(sorted(notes, key=lambda q: q['start_s'])):
        if k and q['start_s'] - (out[-1]['start_s'] + out[-1]['dur_s']) < max_gap:
            q['legato'] = True
        if q['dur_s'] >= 1.5 * BEAT:
            q.setdefault('swell', 0.35)
        out.append(q)
    return out


# ------------------------------------------------------------------------------------------------------
# stems
# ------------------------------------------------------------------------------------------------------
SEC_VEL = {'verse1': 74, 'prechorus1': 84, 'chorus1': 100, 'verse2': 86, 'prechorus2': 94, 'jaeger_call_response': 108,
           'narration': 66, 'bridge': 76, 'build_prechorus3': 100, 'final_chorus': 110}


def lead_vels(mel):
    """section dynamic arc + 1.8x the transcribed spread around each section's mean;
    each phrase's highest note +6, phrase-final short notes -8"""
    acc = {}
    for n in mel:
        acc.setdefault(n['section'], []).append(n['vel'])
    mean = {k: sum(v) / len(v) for k, v in acc.items()}
    top = {}
    for n in mel:
        pid = n.get('phrase_id')
        if pid not in top or n['midi'] > top[pid]['midi']:
            top[pid] = n
    out = []
    for i, n in enumerate(mel):
        v = SEC_VEL.get(n['section'], 90) + 1.8 * (n['vel'] - mean[n['section']])
        if top.get(n.get('phrase_id')) is n:
            v += 6
        nxt = mel[i + 1] if i + 1 < len(mel) else None
        if (nxt is None or nxt.get('phrase_id') != n.get('phrase_id')) and n.get('beats', 1) < 1:
            v -= 8
        out.append(float(np.clip(v, 50, 124)))
    return out


def stem_lead():
    mel, src = part('melody')
    if isinstance(mel, dict):
        mel = mel.get('notes') or mel.get('melody')
    mel = [n for n in mel if keep(n) and n.get('section') != 'narration']
    mel = sorted(mel + grid_notes(NARR_CELLO, 'narration', 42), key=lambda n: n['t'])
    for n in mel:
        n.setdefault('section', sec_of(n['bar']))
    vels = lead_vels(mel)
    lines = {'violin': [], 'cello': []}
    for i, n in enumerate(mel):
        sec = n['section']
        for inst, octv in LEAD_PLAN.get(sec, []):
            nxt = mel[i + 1] if i + 1 < len(mel) else None
            gap = (nxt['t'] - (n['t'] + n['d'])) if nxt else 9
            same_phrase = nxt is not None and nxt.get('phrase_id', -1) == n.get('phrase_id', -2)
            v = vels[i]
            q = nt(n, midi=n['midi'] + octv, vel=v)
            beats = n.get('beats', n['d'] / BEAT)
            if beats >= 3:
                q['dyn_curve'] = [(0, v - 4), (0.55, min(127, v + 16)), (0.85, min(127, v + 18)), (1.0, min(127, v + 8))]
            elif beats >= 1.5:
                q['swell'] = 0.6
            if n['d'] >= 0.6:
                q['vib'] = 1.3
            if n.get('slide_from') is not None:
                q['legato'] = True
                q['glide_ms'] = 90
            q['_new_syllable'] = not n.get('slur', False)
            lines[inst].append((q, same_phrase and gap < 0.06))
    out = {}
    for inst, lst in lines.items():
        notes = []
        for k, (q, slur_next) in enumerate(lst):
            if k and lst[k - 1][1]:
                q['legato'] = True
            if q.pop('_new_syllable') and q.get('legato') and 'glide_ms' not in q:
                q['reartic'] = True          # bow change on a new syllable inside a legato phrase
            notes.append(q)
        if notes:
            out['lead_' + inst] = fit(S.render(notes, instrument=inst, sr=SR, seed=3 if inst == 'violin' else 5))
    # second violin voice (separate render so its slurs do not interfere with the main line):
    # narration descant + the instrumental break, where the violin doubles the guitar solo's long on-beat notes
    extra = [nt(n, vel=64, vib=1.3) for n in grid_notes(NARR_VIOLIN, 'narration', 64, phrase_bars=8)]
    g, _ = part('guitar')
    brk = [n for n in g['lead'] if 132 <= n['bar'] < 148 and n.get('beats', 0) >= 0.5 and float(n.get('beat', 0.5)) % 1 == 0
           and 55 <= n['midi'] <= 88]
    extra += [nt(n, vel=float(np.clip(20 + n.get('vel', 80), 70, 112)), vib=1.2) for n in brk]
    out['lead_violin'] = out.get('lead_violin', np.zeros((N, 2), np.float32)) + fit(
        S.render(slurred(extra), instrument='violin', sr=SR, seed=11)) * 0.85
    print('lead from', src, {k: len(v) for k, v in lines.items()}, 'violin extra', len(extra), '(break', len(brk), ')')
    return out


def line_inst(name):
    """orchestral line -> [(instrument, articulation, gain_db, octave)]"""
    m = {
        'riff_high': [('violins1', 'sustain_vsco', 0, 0), ('violins1', 'tremolo', -9, 0)],
        'riff_pedal': [('violins2', 'sustain_vsco', -2, 0), ('horns', 'sustain', -8, 0)],
        'riff_fill': [('violins1', 'spiccato', -2, 0), ('horns', 'staccato', -6, 0)],
        'verse1_inner': [('violas', 'sustain_vsco', -6, 0)],
        'prechorus_high': [('violins1', 'sustain_vsco', -2, 0)],
        'prechorus_inner': [('violas', 'sustain_vsco', -3, 0)],
        'prechorus_low': [('celli', 'sustain_vsco', -2, 0), ('trombones', 'sustain_solo', -9, 0)],
        'chorus_high': [('violins1', 'sustain_vsco', -1, 0)],
        'chorus_inner': [('violas', 'sustain_vsco', -3, 0), ('horns', 'sustain', -6, 0)],
        'verse2_high': [('flutes', 'sustain', -8, 0), ('violins1', 'sustain_vsco', -12, 0)],
        'verse2_inner': [('violas', 'sustain_vsco', -5, 0)],
        'prechorus2_high': [('violins1', 'sustain_vsco', -2, 0)],
        'prechorus2_inner': [('violas', 'sustain_vsco', -3, 0), ('horns', 'sustain', -7, 0)],
        'jaeger_high': [('flutes', 'sustain', -6, 0), ('violins1', 'tremolo_vsco', -10, 0)],
        'jaeger_mid': [('violins2', 'sustain_vsco', -2, 0), ('horns', 'sustain', -8, 0)],
        'jaeger_low': [('trombones', 'sustain', -7, 0), ('celli', 'sustain_vsco', -4, 0)],
        'break_high': [('violins1', 'sustain_vsco', -1, 0)],
        'break_inner': [('violas', 'sustain_vsco', -3, 0)],
        'break_low': [('trombones', 'sustain', -5, 0), ('celli', 'sustain_vsco', -3, 0)],
        'narration_pedal': [('violins1', 'sustain_vsco', -4, 0)],
        'narration_inner': [('violas', 'sustain_vsco', -3, 0)],
        'bridge_descant': [('flutes', 'sustain', -5, 0), ('violins1', 'sustain_vsco', -12, 0)],
        'bridge_inner': [('violins2', 'sustain_vsco', -3, 0), ('horns', 'sustain', -8, 0)],
        'bridge_tail_low': [('trombones', 'sustain', -2, 0), ('tuba', 'sustain', -5, 0), ('celli', 'sustain_vsco', -2, 0),
                            ('basses', 'sustain', -4, -12)],
        'outro_groove': [('violins1', 'sustain_vsco', -3, 0)],
        'G_ending_high': [('violins1', 'sustain_vsco', 0, 0), ('trumpets', 'sustain', -2, 0)],
        'G_ending_mid': [('horns', 'sustain', -1, 0), ('violas', 'sustain_vsco', -3, 0)],
        'G_ending_low': [('trombones', 'sustain', -1, 0), ('tuba', 'sustain', -3, 0), ('basses', 'sustain', -3, 0)],
    }
    return m.get(name, [('violins2', 'sustain_vsco', -4, 0)])


def clamp_range(inst, art, midi):
    lo, hi = inst_ranges()[inst][art]['range']
    while midi < lo:
        midi += 12
    while midi > hi:
        midi -= 12
    return midi


ALT_ART = {'sustain_vsco': 'sustain', 'tremolo_vsco': 'tremolo', 'spiccato': 'staccato', 'pizzicato_vsco': 'pizzicato'}
BRASS = {'horns', 'trumpets', 'trombones', 'tuba'}


def in_range(inst, art, midi):
    lo, hi = inst_ranges()[inst][art]['range']
    return lo <= midi <= hi


def place_note(inst, art, midi):
    """keep the written octave: switch to a wider-range articulation before folding by octaves.
    Brass doublings are never folded (returns None -> skip the note)."""
    if in_range(inst, art, midi):
        return art, midi
    alt = ALT_ART.get(art)
    if alt and in_range(inst, alt, midi):
        return alt, midi
    if inst in BRASS:
        return None
    return art, clamp_range(inst, art, midi)


def dedup(notes, min_frac=0.5):
    """drop a note that repeats the pitch of an already kept note for more than min_frac of its length
    (two copies of the same sample at the same pitch phase against each other). Earlier entries win."""
    kept = {}
    out = []
    for q in notes:
        a0, a1 = q['start_s'], q['start_s'] + q['dur_s']
        clash = False
        for b0, b1 in kept.get(q['midi'], ()):
            if min(a1, b1) - max(a0, b0) > max(0.15, min_frac * (a1 - a0)):
                clash = True
                break
        if not clash:
            kept.setdefault(q['midi'], []).append((a0, a1))
            out.append(q)
    return out


def tutti_hits():
    """orchestral hits that are not in the transcription: low C# sforzando under the opening chant (bar 17),
    G-minor tutti chord on the band cut-off (bar 231 beat 3.5). -> [(inst, midi, start_s, dur_s, vel)]"""
    t17, fin = tc(tb(17)), tc(tb(231, 3.5))
    hits = [(i, m, t17, 0.5, 110) for i, ms in (('basses', (37,)), ('celli', (37, 49)), ('trombones', (49,)), ('tuba', (37,)))
            for m in ms]
    hits += [(i, m, fin, 1.1, 120) for i, ms in (('basses', (31, 43)), ('tuba', (31, 43)), ('trombones', (43, 55)),
                                                  ('celli', (50, 55)), ('horns', (58, 62)), ('violins2', (67, 70)),
                                                  ('violins1', (74, 79)), ('trumpets', (67, 74))) for m in ms]
    return hits


def stem_orchestra():
    orch, src = part('orch_lines')
    seq = []   # (inst, art, note) in priority order: transcribed lines first, then pads
    for line in orch['lines']:
        for inst, art, gdb, octv in line_inst(line['name']):
            for n in line['notes']:
                if not keep(n):
                    continue
                pl = place_note(inst, art, n['midi'] + octv)
                if pl is None:
                    continue
                a, m = pl
                q = nt(n, midi=m, gain_db=gdb)
                if a in ('spiccato', 'staccato'):
                    q['dur_s'] = min(q['dur_s'], 0.22)
                seq.append((inst, a, q))
    # pads: sustained chord voicings (string section split by register, horns in big sections + interlude swells)
    for p in orch['pads']:
        if p['bar'] < BAR0 or not p['voicing_midi']:
            continue
        sec = p['section']
        horns = sec in BIG or (sec == 'interlude_groove' and p['bar'] in (80, 83))
        for m, st in zip(p['voicing_midi'], p['strength']):
            vel = float(np.clip(45 + 90 * st, 40, 100))
            if m > 94:
                inst = 'piccolo'
            elif m >= 74:
                inst = 'violins1'
            elif m >= 64:
                inst = 'violins2'
            elif m >= 55:
                inst = 'violas'
            else:
                inst = 'celli'
            q = dict(start_s=tc(p['t']), dur_s=p['d'], midi=float(clamp_range(inst, 'sustain', m)), vel=vel,
                     gain_db=-10 if inst == 'piccolo' else -7)
            seq.append((inst, 'sustain', q))
            if horns and 52 <= m <= 72:
                seq.append(('horns', 'sustain', dict(q, gain_db=-12)))
    for inst, m, t, d, v in tutti_hits():
        seq.append((inst, 'staccato', dict(start_s=t, dur_s=min(d, 0.45), midi=float(m), vel=v, gain_db=0)))
        if d > 0.6:
            seq.append((inst, 'sustain', dict(start_s=t + 0.02, dur_s=d, midi=float(m), vel=v - 15, gain_db=-2)))
    by, dropped = {}, 0
    for inst in sorted({x[0] for x in seq}):
        mine = [x for x in seq if x[0] == inst]
        kept = dedup([x[2] for x in mine])
        ids = {id(q) for q in kept}
        dropped += len(mine) - len(kept)
        for _, a, q in mine:
            if id(q) in ids:
                by.setdefault((inst, a), []).append(q)
    stems = {'strings': np.zeros((N, 2), np.float32), 'brass': np.zeros((N, 2), np.float32),
             'winds': np.zeros((N, 2), np.float32)}
    fam = {'violins1': 'strings', 'violins2': 'strings', 'violas': 'strings', 'celli': 'strings', 'basses': 'strings',
           'horns': 'brass', 'trumpets': 'brass', 'trombones': 'brass', 'tuba': 'brass', 'flutes': 'winds',
           'piccolo': 'winds', 'oboes': 'winds'}
    for (inst, art), notes in sorted(by.items()):
        groups = {}
        for q in notes:
            groups.setdefault(q.pop('gain_db', 0), []).append(q)
        for gdb, qs in groups.items():
            y = E.render(qs, inst, art, sr=SR, length_s=END_S, seed=hash((inst, art, gdb)) % 97)
            stems[fam[inst]] += fit(y) * 10 ** (gdb / 20)
        print('orch', inst, art, len(notes))
    print('orchestra from', src, 'dedup dropped', dropped)
    return stems


HOOK_WORDS = ('chorus1_jaeger_word', 'final_chorus_eren_word')
BOOKEND_BARS = 213          # the opening chant (bars 17-18) returns over the last G minor bars (230-231), C# -> G;
                            # its '-ger' chord (bVII) resolves into the final G-minor tutti hit


def octave_fit(ms, lo, hi, shifts):
    """the octave shift that puts most of a line inside [lo, hi]"""
    return max(shifts, key=lambda sh: sum(lo <= m + sh <= hi for m in ms))


def choir_parts():
    ch, src = part('choir')
    orch, _ = part('orch_lines')
    notes = []      # sustained "aah"
    stabs = []      # short shouts -> choir + brass staccato
    hook = []       # "Jaeger" / "Eren" accent words -> horns + trumpets marcato
    feuer = []      # "Feuerroter Pfeil und Bogen" growl -> trombones + tuba on C#
    chords, _ = part('chords')
    for ps in ch['passages']:
        if ps['bar_end'] < BAR0 or ps['type'] == 'spoken':
            continue
        short = ps['type'] in ('shout', 'chant')
        boost = 10 if ps['type'] == 'shout' else 5
        for v in ps.get('voices', []):
            for n in v['notes']:
                if not keep(n):
                    continue
                if ps['name'] in HOOK_WORDS:
                    notes.append(nt(n, vel=min(120, n.get('vel', 85) + 15)))
                    if n['midi'] >= 76:
                        hook.append(nt(n, vel=115))
                    continue
                q = nt(n, vel=min(120, n.get('vel', 85) + boost))
                (stabs if short and n['d'] <= 0.7 else notes).append(q)
                if ps['name'] == 'seid_ihr_das_essen_chant':
                    stabs.append(dict(q, start_s=q['start_s'] + BOOKEND_BARS * 4 * BEAT, midi=q['midi'] - 6, vel=112.0))
        if not ps.get('pitched', True):
            # unpitched gang shout: double its rhythm with chord tones (root + 5th, male range)
            for o in ps.get('rhythm_onsets', []):
                if o['t'] < T0 - 0.05:
                    continue
                c = max((c for c in chords if c['t'] <= o['t'] + 0.01), key=lambda c: c['t'])
                if c['root_pc'] is None:
                    continue
                root = 48 + (c['root_pc'] - 48) % 12
                for m in (root, root + 7):
                    stabs.append(dict(start_s=tc(o['t']), dur_s=0.22, midi=float(m), vel=112))
                if ps['name'].startswith('feuerroter'):
                    feuer += [dict(start_s=tc(o['t']), dur_s=0.3, midi=49.0, vel=118),
                              dict(start_s=tc(o['t']), dur_s=0.3, midi=37.0, vel=118)]
    # chorus choir: octave doubling of the sung melody's long notes (final chorus bigger than chorus 1)
    mel, _ = part('melody')
    mel = mel if isinstance(mel, list) else (mel.get('notes') or mel.get('melody'))
    for bars, vel in (((60, 67), 65), ((197, 212), 80)):
        mm = [n for n in mel if bars[0] <= n['bar'] < bars[1] and n.get('beats', 0) >= 1]
        fs = octave_fit([n['midi'] for n in mm], 66, 84, (0, 12))
        ms = octave_fit([n['midi'] for n in mm], 43, 66, (-12, 0))
        for n in mm:
            notes.append(nt(n, midi=clamp_range('choir_female', 'aah', n['midi'] + fs), vel=vel))
            notes.append(nt(n, midi=clamp_range('choir_male', 'aah', n['midi'] + ms), vel=vel - 5))
    pads = [dict(start_s=tc(p['t']), dur_s=p['d'], midi=float(m), vel=70)
            for p in orch['pads'] if p['bar'] >= BAR0 and p.get('choir_voicing_midi') for m in p['choir_voicing_midi']]
    # G-minor tutti chord on the band cut-off
    fin = tc(tb(231, 3.5))
    pads += [dict(start_s=fin, dur_s=0.8, midi=float(m), vel=115) for m in (67, 70, 74)]
    notes = dedup(notes + pads)
    print('choir from', src, len(notes), 'sustained', len(stabs), 'stabs', len(hook), 'hook', len(feuer), 'feuer')
    return notes, stabs, hook, feuer


def stem_choir():
    notes, stabs, hook, feuer = choir_parts()
    lo = [q for q in notes if q['midi'] < 66]
    hi = [q for q in notes if q['midi'] >= 66]
    y = fit(E.render(lo, 'choir_male', 'aah', sr=SR, length_s=END_S)) + fit(E.render(hi, 'choir_female', 'aah', sr=SR, length_s=END_S))
    # shouts: start inside the sustained vowel (skip the slow recorded attack) so each stab is front-loaded
    st = [dict(q, dur_s=min(q['dur_s'] * 0.8, 0.40), legato=True, attack_s=0.012, release_s=0.10) for q in stabs]
    s = fit(E.render(st, 'choir', 'aah', sr=SR, length_s=END_S, legato=True))
    br = fit(E.render([dict(q, midi=float(clamp_range('trombones', 'staccato', q['midi']))) for q in stabs],
                      'trombones', 'staccato', sr=SR, length_s=END_S))
    hn = fit(E.render([dict(q, midi=float(clamp_range('horns', 'staccato', q['midi'] + 12))) for q in stabs],
                      'horns', 'staccato', sr=SR, length_s=END_S))
    stab_bus = br * 0.7 + hn * 0.6
    if hook:
        stab_bus += fit(E.render(hook, 'trumpets', 'staccato', sr=SR, length_s=END_S)) * 0.8
        stab_bus += fit(E.render([dict(q, midi=float(clamp_range('horns', 'staccato', q['midi']))) for q in hook],
                                 'horns', 'staccato', sr=SR, length_s=END_S)) * 0.7
        zen = trim(load_wav(SPL + '004_Stab_-_Horn_-_MS_Zenhiser_Ab.wav'), 0.6, 0.08)
        for q in hook:
            if q['midi'] == 80:
                place(stab_bus, zen, q['start_s'], 0.5)
    if feuer:
        stab_bus += fit(E.render([q for q in feuer if q['midi'] > 40], 'trombones', 'staccato', sr=SR, length_s=END_S)) * 0.9
        stab_bus += fit(E.render([q for q in feuer if q['midi'] <= 40], 'tuba', 'staccato', sr=SR, length_s=END_S)) * 0.9
    return {'choir': y + s * 0.9, 'brass_stabs': stab_bus}


def stem_bass():
    b, src = part('bass')
    sh = (194 - 49) * 4 * BEAT
    b = [n for n in b if n['bar'] != 194] + [dict(n, t=n['t'] + sh, bar=194, section=sec_of(194)) for n in b if n['bar'] == 49]
    b.sort(key=lambda n: n['t'])
    notes = [nt(n, vel=n.get('vel', 80)) for n in b if keep(n) and not n.get('muted')]
    muted = [nt(n, dur=min(n['d'], 0.15)) for n in b if keep(n) and n.get('muted')]
    y = fit(E.bass_render(notes, 'sustain', sr=SR, drive=0.2, length_s=END_S))
    if muted:
        y += fit(E.bass_render(muted, 'staccato', sr=SR, drive=0.2, length_s=END_S)) * 0.6
    # orchestral low strings double the bass in the big sections (sustained per note, 8vb where in range)
    dbl = []
    for n in b:
        if keep(n) and not n.get('muted') and sec_of(n['bar']) in BIG and n.get('beats', 1) >= 0.5:
            dbl.append(nt(n, midi=clamp_range('basses', 'sustain', n['midi']), vel=80))
    cb = fit(E.render_preset(dbl, 'basses_sus', sr=SR, length_s=END_S)) if dbl else np.zeros((N, 2), np.float32)
    print('bass from', src, len(notes), len(muted), 'dbl', len(dbl))
    return {'bass': y, 'low_strings': cb}


def stem_guitars():
    g, src = part('guitar')
    pm, op = [], []
    for e in g['rhythm']:
        if not keep(e):
            continue
        dur = max(0.08, e['d'] * (0.92 if e['articulation'] == 'palm_mute' else 1.0))
        if e['bar'] == 131 and e['beat'] >= 2:
            notes = E.power_chord(48, tc(e['t']), dur, vel=e.get('vel', 100), intervals=(0, 8, 12))
        else:
            notes = E.power_chord(e['root_midi'], tc(e['t']), dur, vel=e.get('vel', 100))
        (pm if e['articulation'] == 'palm_mute' else op).extend(notes)
    y = fit(E.guitar_render(pm, 'palm_mute', sr=SR, amp='high_gain', length_s=END_S, seed=1))
    y += fit(E.guitar_render(op, 'sustain', sr=SR, amp='high_gain', length_s=END_S, seed=2))
    lead, prev_end = [], -9
    for n in sorted((n for n in g['lead'] if keep(n)), key=lambda n: n['t']):
        q = dict(nt(n), group='lead')
        if n.get('articulation') == 'legato' and tc(n['t']) - prev_end < 0.03:
            q['vel'] = max(30, q['vel'] - 25)        # hammer-on / pull-off: no fresh pick
            q['attack_s'] = 0.008
        prev_end = tc(n['t']) + n['d']
        lead.append(q)
        for k, m in enumerate(n.get('voicing') or []):
            if m != n['midi']:
                lead.append(dict(q, midi=float(m), group='lead_v%d' % k))
    di = E.render(lead, 'eguitar', 'sustain', sr=SR, stereo=False, length_s=END_S)
    ld = E.amp_sim(di.mean(1), SR, 'lead', cab='v30')
    print('guitars from', src, len(pm) // 3, len(op) // 3, 'lead', len(lead))
    return {'guitars': y, 'lead_guitar': fit(np.stack([ld, ld], 1))}


def stem_piano():
    p, src = part('piano')
    chords, _ = part('chords')
    changes = np.array(sorted(c['t'] for c in chords))
    notes = []
    for n in p:
        if not keep(n) or n.get('section') == 'verse2' or (n['bar'] == 157 and n['midi'] == 41):
            continue
        k = np.searchsorted(changes, n['t'] + 0.05)
        nxt = changes[k] if k < len(changes) else n['t'] + 4 * BEAT
        notes.append(nt(n, dur=max(n['d'], min(nxt - n['t'], 8 * BEAT))))
    print('piano from', src, len(notes))
    return {'piano': fit(E.render(notes, 'piano', 'sustain', sr=SR, length_s=END_S, pedal=False, release_s=0.25))}


DRUM_MAP = {'kick': 'kick', 'snare': 'snare', 'snare_ghost': 'snare', 'ride': 'ride', 'hh_open': 'hihat_open',
            'hh_closed': 'hihat_closed', 'tom_floor': 'tom3', 'tom_low': 'tom3', 'tom_mid': 'tom2', 'tom_hi': 'tom1',
            'gran_cassa': 'orch_bass_drum', 'orch_cymbals': 'orch_crash', 'orch_snare': 'orch_snare',
            'orch_snare_roll': 'orch_snare_roll', 'snare_roll': 'orch_snare_roll'}


def stem_drums():
    d, src = part('drums')
    hits, crash_n = [], 0
    kit = np.zeros((N, 2), np.float32)
    perc = np.zeros((N, 2), np.float32)
    rng = np.random.default_rng(17)

    def jit(db=1.0):
        return 10 ** (rng.uniform(-db, db) / 20)
    # Splice layers under DRSKit: short (kick 0.12 s), 4 pitch variants each so no two hits are the same waveform.
    # Kick polarity/offset checked against DRSKit's kick: in phase at 0 ms (40-150 Hz sum is maximal there).
    k_var = variants(SPL + 'DD_HR_kick_one_shot_low_hard.wav', 4, 30, length_s=0.12, seed=1)
    s_var = variants(SPL + 'DD_HR_snare_one_shot_metal_hard.wav', 4, 30, seed=2)
    c_spl = load_wav(SPL + 'DD_HR_cymbal_one_shot_crash_large_hard.wav')
    rev = load_wav(SPL + 'SHS_MRO_fx_rev_crash.wav')
    taiko = []
    for k, f in enumerate(('SC_TKO_chu_daiko_hit_resonant.wav', 'SC_TKO_chu_daiko_hit_blue.wav',
                           'MNT_OTR_perc_taiko_mid_taiko_low_single_hit.wav')):
        taiko += variants(SPL + f, 2, 40, seed=10 + k)
    odaiko = variants(SPL + 'SC_TKO_o_daiko_hit_faults.wav', 2, 40, seed=20) + \
        variants(SPL + 'si_origins_percussion_bassdrum_taiko_hard_loudest_holy.wav', 2, 40, seed=21)
    tribal = load_wav(SPL + 'ESM_Deep_Cinematic_Tribal_Drum_Impact_Epic_Hit_Slam_Movie_Trailer_Boom_Bang_.wav')
    cnt = {'k': 0, 's': 0, 't': 0, 'o': 0}

    def tk(t, g):
        place(perc, taiko[cnt['t'] % len(taiko)], t, g * jit(1.5))
        cnt['t'] += 1

    def od(t, g):
        place(perc, odaiko[cnt['o'] % len(odaiko)], t, g * jit(1.5))
        cnt['o'] += 1
    for h in d:
        if not keep(h):
            continue
        pc, t, v = h['piece'], tc(h['t']), h.get('vel', 90)
        bridge = 173 <= h['bar'] < 185
        if pc == 'crash':
            if bridge and h['bar'] != 173:
                continue                      # bridge: crashes only on its first bar (and bar 185)
            if bridge:
                v *= 0.6
            crash_n += 1
            hits.append(dict(start_s=t, piece='crash_l' if crash_n % 2 else 'crash_r', vel=v))
            if v >= 100:
                place(kit, c_spl, t, 0.25 * v / 127)
        elif pc in DRUM_MAP:
            vv = v * (0.45 if pc == 'snare_ghost' else 1.0) * (0.6 if bridge and pc == 'hh_open' else 1.0)
            hits.append(dict(start_s=t, piece=DRUM_MAP[pc], vel=vv))
            if pc == 'kick':
                place(kit, k_var[cnt['k'] % 4], t, 0.12 * v / 127 * jit())
                cnt['k'] += 1
            if pc == 'snare':
                place(kit, s_var[cnt['s'] % 4], t, 0.11 * v / 127 * jit())
                cnt['s'] += 1
        elif pc == 'big_drum':
            tk(t, 0.55 * v / 127)
        elif pc == 'cymbal_swell':
            tgt = tc(tb(h['target_bar'], h['target_beat'])) if 'target_bar' in h else t + h['d']
            dur = max(0.4, tgt - t)
            seg = rev[-int(min(dur, len(rev) / SR) * SR):]
            place(perc, seg, tgt - len(seg) / SR, 0.5 * v / 127)
    # opening: the chant's downbeat, "JAE-" and "-GER" get o-daiko + chu-daiko, tribal impact on bar 17
    for bar, beat in ((17, 0), (18, 1), (18, 2.5)):
        od(tc(tb(bar, beat)), 0.5)
        tk(tc(tb(bar, beat)), 0.55)
    place(perc, tribal, tc(tb(17)), 0.35)
    # hook words: "Jaeger" (bar 59) / "Eren" (bar 204) accent
    for bar in (59, 204):
        tk(tc(tb(bar, 0.5)), 0.5)
        hits.append(dict(start_s=tc(tb(bar, 0.5)), piece='crash_r', vel=112))
    kit += fit(E.drums_render(hits, sr=SR, mix='rock', length_s=END_S))
    # cinematic layer
    for bar in range(BAR0, LAST_BAR):
        sec = sec_of(bar)
        if sec == 'jaeger_call_response':
            k = (bar - 108) % 4
            if k == 1:                             # "JAE-" downbeat: o-daiko + tribal; "-ger!" on beat 3
                od(tc(tb(bar)), 0.5)
                place(perc, tribal, tc(tb(bar)), 0.3)
                tk(tc(tb(bar, 2)), 0.45)
            elif k == 0:                           # "Wir"
                tk(tc(tb(bar)), 0.35)
            else:                                  # violin answer
                tk(tc(tb(bar, 2)), 0.3)
        elif sec in ('chorus1', 'final_chorus', 'outro_G_ending'):
            s0 = SEC[sec][0]
            if sec == 'final_chorus' or (bar - s0) % 2 == 0:
                od(tc(tb(bar)), 0.45)
            tk(tc(tb(bar, 2)), 0.3)
    print('drums from', src, len(hits), cnt)
    return {'drums': kit, 'epic_perc': perc}


def stem_fx():
    fx = np.zeros((N, 2), np.float32)
    boom = load_wav(SPL + 'ESM_Cinematic_Deep_Cinematic_Sub_Impact_Trailer_Movie_Hit_Boom_Drop_Doppler_Hollywood.wav')
    smack = load_wav(SPL + 'ESM_TEBSSE_FX_blockbuster_hit_one_shot_big_orchestral_bass_drum_smack_02.wav')
    riser = load_wav(SPL + 'ESM_Infiltration_Thriller_Riser_Tension_Escalation_03_Horror_Trailer_Cinematic_Build_Up_Rising_Epic_Whoosh_Transition.wav')
    braam = load_wav(SPL + 'ESM_Movie_Trailer_Braaam_One_Shot_Brutal_Annihilation_A_02_Cinematic_Pulse_Flowing.wav', semis=4)
    for bar, g in ((17, 0.25), (19, 0.3), (52, 0.35), (108, 0.35), (197, 0.35), (224, 0.35)):
        place(fx, boom, tc(tb(bar)), g)
        place(fx, smack, tc(tb(bar)), 0.4)
    place(fx, smack, tc(tb(124)), 0.22)        # break entry
    place(fx, boom, tc(tb(190)), 0.2)          # band re-entry in the last build
    for bar in (52, 197):
        place(fx, braam, tc(tb(bar)), 0.3)
    # riser: its loudest moment lands on the downbeat, then it is cut (60 ms fade)
    pk = peak_s(riser)
    r = trim(riser, pk + 0.06, 0.06)
    for bar in (52, 197, 108):
        place(fx, r, tc(tb(bar)) - pk, 0.35)
    # timpani crescendo rolls into the choruses: G# (dominant) before 52/197, E before the Am of 108;
    # rendered alone, then placed so the roll's peak is on the downbeat
    for bar, root in ((52, 44), (197, 44), (108, 40)):
        roll = E.render([dict(start_s=0.5, dur_s=4 * BEAT, midi=float(root), vel=95)], 'timpani', 'roll_crescendo',
                        sr=SR, length_s=6.0)
        pk = peak_s(roll)
        place(fx, trim(roll, pk + 0.25, 0.15), tc(tb(bar)) - pk, 0.8)
    # narration: soft timpani heartbeat on C# under the cello recitative
    hb = [dict(start_s=tc(tb(bar)), dur_s=0.8, midi=37.0, vel=70) for bar in range(148, 157)]
    fx += fit(E.render(hb, 'timpani', 'hit', sr=SR, length_s=END_S)) * 0.8
    fin = tc(tb(231, 3.5))
    place(fx, boom, fin, 0.5)
    fx += fit(E.drums_render([dict(start_s=fin, piece='gong', vel=120), dict(start_s=fin, piece='orch_bass_drum', vel=127)],
                             sr=SR, length_s=END_S)) * 0.7
    return {'fx': fx}


RENDERERS = {'lead': stem_lead, 'orchestra': stem_orchestra, 'choir': stem_choir, 'bass': stem_bass,
             'guitars': stem_guitars, 'piano': stem_piano, 'drums': stem_drums, 'fx': stem_fx}


def render(only=None):
    for name, fn in RENDERERS.items():
        if only and name not in only:
            continue
        res = fn()
        for k, y in res.items():
            sf.write(f'{STEMS}/{k}.wav', y.astype(np.float32), SR, subtype='FLOAT')
            pk = float(np.abs(y).max())
            rms = float(np.sqrt((y ** 2).mean()) + 1e-12)
            print(f'  stem {k}: peak {20 * math.log10(pk + 1e-12):.1f} dBFS rms {20 * math.log10(rms):.1f}')


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'render'
    only = None
    if '--only' in sys.argv:
        only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
    if mode in ('render', 'all'):
        render(only)
