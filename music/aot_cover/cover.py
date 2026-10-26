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
    y, sr = sf.read(path, dtype='float32', always_2d=True)
    if y.shape[1] == 1:
        y = np.repeat(y, 2, 1)
    r = sr / SR * 2 ** (semis / 12)
    if abs(r - 1) > 1e-6:
        idx = np.arange(int(len(y) / r)) * r
        y = np.stack([np.interp(idx, np.arange(len(y)), y[:, c]) for c in range(2)], 1).astype(np.float32)
    return y


SPL = A + '/lib/splice/'

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


# ------------------------------------------------------------------------------------------------------
# stems
# ------------------------------------------------------------------------------------------------------
def stem_lead():
    mel, src = part('melody')
    if isinstance(mel, dict):
        mel = mel.get('notes') or mel.get('melody')
    mel = [n for n in mel if keep(n)]
    lines = {'violin': [], 'cello': []}
    for i, n in enumerate(mel):
        sec = n.get('section') or sec_of(n['bar'])
        for inst, octv in LEAD_PLAN.get(sec, []):
            nxt = mel[i + 1] if i + 1 < len(mel) else None
            gap = (nxt['t'] - (n['t'] + n['d'])) if nxt else 9
            same_phrase = nxt is not None and nxt.get('phrase_id', -1) == n.get('phrase_id', -2)
            q = nt(n, midi=n['midi'] + octv, vel=min(118, 22 + n.get('vel', 80)))
            beats = n.get('beats', n['d'] / BEAT)
            if beats >= 1.5:
                q['swell'] = 0.35
            if n.get('slide_from') is not None:
                q['legato'] = True
                q['glide_ms'] = 90
            lines[inst].append((q, same_phrase and gap < 0.06))
    out = {}
    for inst, lst in lines.items():
        notes = []
        for k, (q, slur_next) in enumerate(lst):
            if k and lst[k - 1][1]:
                q['legato'] = True
            notes.append(q)
        if notes:
            out['lead_' + inst] = fit(S.render(notes, instrument=inst, sr=SR, seed=3 if inst == 'violin' else 5))
    print('lead from', src, {k: len(v) for k, v in lines.items()})
    return out


def line_inst(name):
    """orchestral line -> [(instrument, articulation, gain_db, octave)]"""
    m = {
        'riff_high': [('violins1', 'sustain_vsco', 0, 0), ('violins1', 'tremolo', -9, 0)],
        'riff_pedal': [('violins2', 'sustain_vsco', -2, 0), ('horns', 'sustain_solo', -8, 0)],
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
        'jaeger_mid': [('violins2', 'sustain_vsco', -2, 0), ('horns', 'sustain', -4, 0)],
        'jaeger_low': [('trombones', 'sustain', -4, 0), ('celli', 'sustain_vsco', -4, 0)],
        'break_high': [('violins1', 'sustain_vsco', -1, 0)],
        'break_inner': [('violas', 'sustain_vsco', -3, 0)],
        'break_low': [('trombones', 'sustain', -5, 0), ('celli', 'sustain_vsco', -3, 0)],
        'narration_pedal': [('violins1', 'sustain_vsco', -10, 0)],
        'narration_inner': [('violas', 'sustain_vsco', -8, 0)],
        'bridge_descant': [('flutes', 'sustain', -5, 0), ('violins1', 'sustain_vsco', -12, 0)],
        'bridge_inner': [('violins2', 'sustain_vsco', -3, 0), ('horns', 'sustain', -8, 0)],
        'bridge_tail_low': [('trombones', 'sustain', -2, 0), ('tuba', 'sustain', -5, 0), ('celli', 'sustain_vsco', -2, 0),
                            ('basses', 'sustain', -4, -12)],
        'outro_groove': [('violins1', 'sustain_vsco', -3, 0)],
        'G_ending_high': [('violins1', 'sustain_vsco', 0, 0), ('trumpets', 'sustain', -5, 0)],
        'G_ending_mid': [('horns', 'sustain', -1, 0), ('violas', 'sustain_vsco', -3, 0)],
        'G_ending_low': [('trombones', 'sustain', -1, 0), ('tuba', 'sustain', -3, 0), ('basses', 'sustain', -3, 0)],
    }
    return m.get(name, [('violins2', 'sustain_vsco', -4, 0)])


def clamp_range(inst, art, midi):
    lo, hi = E.list_instruments()[inst][art]['range']
    while midi < lo:
        midi += 12
    while midi > hi:
        midi -= 12
    return midi


def stem_orchestra():
    orch, src = part('orch_lines')
    by = {}   # (inst, art) -> notes with gain
    for line in orch['lines']:
        for inst, art, gdb, octv in line_inst(line['name']):
            for n in line['notes']:
                if not keep(n):
                    continue
                q = nt(n, midi=clamp_range(inst, art, n['midi'] + octv), gain_db=gdb)
                if art in ('spiccato', 'staccato'):
                    q['dur_s'] = min(q['dur_s'], 0.22)
                by.setdefault((inst, art), []).append(q)
    # pads: sustained chord voicings (string section split by register, horns only in big sections)
    for p in orch['pads']:
        if p['bar'] < BAR0 or not p['voicing_midi']:
            continue
        sec = p['section']
        big = sec in BIG
        for m, s in zip(p['voicing_midi'], p['strength']):
            vel = float(np.clip(45 + 90 * s, 40, 100))
            if m >= 74:
                inst = 'violins1'
            elif m >= 64:
                inst = 'violins2'
            elif m >= 55:
                inst = 'violas'
            else:
                inst = 'celli'
            q = dict(start_s=tc(p['t']), dur_s=p['d'], midi=float(clamp_range(inst, 'sustain', m)), vel=vel, gain_db=-7)
            by.setdefault((inst, 'sustain'), []).append(q)
            if big and 52 <= m <= 72:
                by.setdefault(('horns', 'sustain'), []).append(dict(q, gain_db=-12))
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
    print('orchestra from', src)
    return stems


def choir_parts():
    ch, src = part('choir')
    orch, _ = part('orch_lines')
    notes = []      # sustained "aah"
    stabs = []      # short shouts -> choir + brass staccato
    for ps in ch['passages']:
        if ps['bar_end'] < BAR0 or ps['type'] == 'spoken':
            continue
        short = ps['type'] in ('shout', 'chant')
        for v in ps.get('voices', []):
            for n in v['notes']:
                if not keep(n):
                    continue
                q = nt(n, vel=min(110, n.get('vel', 85) + 5))
                (stabs if short and n['d'] < 0.6 else notes).append(q)
        if not ps.get('pitched', True):
            # unpitched gang shout: double its rhythm with chord tones (root + 5th, male range)
            chords, _ = part('chords')
            for o in ps.get('rhythm_onsets', []):
                if o['t'] < T0 - 0.05:
                    continue
                c = max((c for c in chords if c['t'] <= o['t'] + 0.01), key=lambda c: c['t'])
                if c['root_pc'] is None:
                    continue
                root = 48 + (c['root_pc'] - 48) % 12
                for m in (root, root + 7):
                    stabs.append(dict(start_s=tc(o['t']), dur_s=0.22, midi=float(m), vel=105))
    for p in orch['pads']:
        if p['bar'] >= BAR0 and p.get('choir_voicing_midi'):
            for m in p['choir_voicing_midi']:
                notes.append(dict(start_s=tc(p['t']), dur_s=p['d'], midi=float(m), vel=70))
    print('choir from', src, len(notes), 'sustained', len(stabs), 'stabs')
    return notes, stabs


def stem_choir():
    notes, stabs = choir_parts()
    lo = [q for q in notes if q['midi'] < 66]
    hi = [q for q in notes if q['midi'] >= 66]
    y = fit(E.render(lo, 'choir_male', 'aah', sr=SR, length_s=END_S)) + fit(E.render(hi, 'choir_female', 'aah', sr=SR, length_s=END_S))
    s = fit(E.render(stabs, 'choir', 'aah', sr=SR, length_s=END_S, release_s=0.12))
    br = fit(E.render([dict(q, midi=float(clamp_range('trombones', 'staccato', q['midi']))) for q in stabs],
                      'trombones', 'staccato', sr=SR, length_s=END_S))
    hn = fit(E.render([dict(q, midi=float(clamp_range('horns', 'staccato', q['midi'] + 12))) for q in stabs],
                      'horns', 'staccato', sr=SR, length_s=END_S))
    return {'choir': y + s * 0.9, 'brass_stabs': br * 0.7 + hn * 0.6}


def stem_bass():
    b, src = part('bass')
    notes = [nt(n, vel=n.get('vel', 80)) for n in b if keep(n) and not n.get('muted')]
    muted = [nt(n, dur=min(n['d'], 0.15)) for n in b if keep(n) and n.get('muted')]
    y = fit(E.bass_render(notes, 'sustain', sr=SR, drive=0.35, length_s=END_S))
    if muted:
        y += fit(E.bass_render(muted, 'staccato', sr=SR, drive=0.3, length_s=END_S)) * 0.6
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
        notes = E.power_chord(e['root_midi'], tc(e['t']), dur, vel=e.get('vel', 100))
        (pm if e['articulation'] == 'palm_mute' else op).extend(notes)
    y = fit(E.guitar_render(pm, 'palm_mute', sr=SR, amp='high_gain', length_s=END_S, seed=1))
    y += fit(E.guitar_render(op, 'sustain', sr=SR, amp='high_gain', length_s=END_S, seed=2))
    lead = [nt(n) for n in g['lead'] if keep(n)]
    di = E.render([dict(q, group='lead') for q in lead], 'eguitar', 'sustain', sr=SR, stereo=False, length_s=END_S)
    ld = E.amp_sim(di.mean(1), SR, 'lead', cab='v30')
    print('guitars from', src, len(pm) // 3, len(op) // 3, 'lead', len(lead))
    return {'guitars': y, 'lead_guitar': fit(np.stack([ld, ld], 1))}


def stem_piano():
    p, src = part('piano')
    notes = [nt(n) for n in p if keep(n)]
    print('piano from', src, len(notes))
    return {'piano': fit(E.render(notes, 'piano', 'sustain', sr=SR, length_s=END_S, pedal=True))}


DRUM_MAP = {'kick': 'kick', 'snare': 'snare', 'snare_ghost': 'snare', 'ride': 'ride', 'hh_open': 'hihat_open',
            'hh_closed': 'hihat_closed', 'tom_floor': 'tom3', 'tom_low': 'tom3', 'tom_mid': 'tom2', 'tom_hi': 'tom1',
            'gran_cassa': 'orch_bass_drum', 'orch_cymbals': 'orch_crash', 'orch_snare': 'orch_snare',
            'orch_snare_roll': 'orch_snare_roll', 'snare_roll': 'orch_snare_roll'}


def stem_drums():
    d, src = part('drums')
    hits, crash_n = [], 0
    kit = np.zeros((N, 2), np.float32)
    perc = np.zeros((N, 2), np.float32)
    k_spl = load_wav(SPL + 'DD_HR_kick_one_shot_low_hard.wav')
    s_spl = load_wav(SPL + 'DD_HR_snare_one_shot_metal_hard.wav')
    c_spl = load_wav(SPL + 'DD_HR_cymbal_one_shot_crash_large_hard.wav')
    rev = load_wav(SPL + 'SHS_MRO_fx_rev_crash.wav')
    taiko = [load_wav(SPL + f) for f in ('SC_TKO_chu_daiko_hit_resonant.wav', 'SC_TKO_chu_daiko_hit_blue.wav')]
    odaiko = load_wav(SPL + 'SC_TKO_o_daiko_hit_faults.wav')
    for h in d:
        if not keep(h):
            continue
        pc, t, v = h['piece'], tc(h['t']), h.get('vel', 90)
        if pc == 'crash':
            crash_n += 1
            hits.append(dict(start_s=t, piece='crash_l' if crash_n % 2 else 'crash_r', vel=v))
            if v >= 100:
                place(kit, c_spl, t, 0.25 * v / 127)
        elif pc in DRUM_MAP:
            vv = v * (0.45 if pc == 'snare_ghost' else 1.0)
            hits.append(dict(start_s=t, piece=DRUM_MAP[pc], vel=vv))
            if pc == 'kick':
                place(kit, k_spl, t, 0.35 * v / 127)
            if pc == 'snare':
                place(kit, s_spl, t, 0.22 * v / 127)
        elif pc == 'big_drum':
            place(perc, taiko[crash_n % 2], t, 0.55 * v / 127)
        elif pc == 'cymbal_swell':
            tgt = tc(tb(h['target_bar'], h['target_beat'])) if 'target_bar' in h else t + h['d']
            dur = max(0.4, tgt - t)
            seg = rev[-int(min(dur, len(rev) / SR) * SR):]
            place(perc, seg, tgt - len(seg) / SR, 0.5 * v / 127)
    kit += fit(E.drums_render(hits, sr=SR, mix='rock', length_s=END_S))
    # cinematic layer: o-daiko on the downbeat of every 2nd bar in the big sections, chu-daiko on beat 3
    for bar in range(BAR0, LAST_BAR):
        sec = sec_of(bar)
        if sec in ('chorus1', 'final_chorus', 'jaeger_call_response', 'outro_G_ending'):
            if bar % 2 == 0:
                place(perc, odaiko, tc(tb(bar)), 0.45)
            place(perc, taiko[bar % 2], tc(tb(bar, 2)), 0.3)
    print('drums from', src, len(hits))
    return {'drums': kit, 'epic_perc': perc}


def stem_fx():
    fx = np.zeros((N, 2), np.float32)
    boom = load_wav(SPL + 'ESM_Cinematic_Deep_Cinematic_Sub_Impact_Trailer_Movie_Hit_Boom_Drop_Doppler_Hollywood.wav')
    smack = load_wav(SPL + 'ESM_TEBSSE_FX_blockbuster_hit_one_shot_big_orchestral_bass_drum_smack_02.wav') if os.path.exists(
        SPL + 'ESM_TEBSSE_FX_blockbuster_hit_one_shot_big_orchestral_bass_drum_smack_02.wav') else None
    riser = load_wav(SPL + 'ESM_Infiltration_Thriller_Riser_Tension_Escalation_03_Horror_Trailer_Cinematic_Build_Up_Rising_Epic_Whoosh_Transition.wav') if os.path.exists(
        SPL + 'ESM_Infiltration_Thriller_Riser_Tension_Escalation_03_Horror_Trailer_Cinematic_Build_Up_Rising_Epic_Whoosh_Transition.wav') else None
    braam = load_wav(SPL + 'ESM_Movie_Trailer_Braaam_One_Shot_Brutal_Annihilation_A_02_Cinematic_Pulse_Flowing.wav', semis=4) if os.path.exists(
        SPL + 'ESM_Movie_Trailer_Braaam_One_Shot_Brutal_Annihilation_A_02_Cinematic_Pulse_Flowing.wav') else None
    for bar in (17, 52, 108, 197, 224):
        place(fx, boom, tc(tb(bar)), 0.35)
        if smack is not None:
            place(fx, smack, tc(tb(bar)), 0.4)
    if braam is not None:
        for bar in (52, 197):
            place(fx, braam, tc(tb(bar)), 0.3)
    if riser is not None:
        for bar in (52, 197, 108):
            L = len(riser) / SR
            place(fx, riser, tc(tb(bar)) - L, 0.35)
    # timpani crescendo rolls into the choruses, final hit at the band cut-off
    tim = []
    for bar, root in ((51, 49), (196, 49), (107, 40)):
        tim.append(dict(start_s=tc(tb(bar)), dur_s=4 * BEAT, midi=float(clamp_range('timpani', 'roll', root)), vel=95))
    fx += fit(E.render(tim, 'timpani', 'roll_crescendo', sr=SR, length_s=END_S)) * 0.8
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
