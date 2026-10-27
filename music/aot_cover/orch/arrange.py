"""Guren no Yumiya - orchestral cover test (SEG=intro: cover 0-30 s, SEG=chorus: 46.8-68 s).

Rearranges the rock-band transcription MIDI into a true orchestra and renders each
part through Spitfire BBC Symphony Orchestra Discover (VST3, hosted by pedalboard).
Choir comes from the VPO mixed-choir SFZ samples (BBC Discover has no choir).

Usage: python arrange.py [stem ...]      # renders stems/*.wav (all if none given)
"""
import os, sys, random, struct, re, time
import numpy as np, soundfile as sf, mido
from mido import Message

HERE = os.path.dirname(os.path.abspath(__file__))
MIDI = os.environ.get("GUREN_MIDI", os.path.join(HERE, "..", "midi", "guren_from_0m21_full.mid"))
if not os.path.exists(MIDI):
    MIDI = r"E:\YTP2\AoT_Music\repo\music\aot_cover\midi\guren_from_0m21_full.mid"
STEMS = os.path.join(HERE, "stems")
SR = 48000
BPM = 180.676
SPB = 60 / BPM
BAR = 4 * SPB
BAR0 = 0.0               # bar grid: cover t=0 is a downbeat
SEGMENTS = {             # render range (pre-roll/tail), output window, verse start, tam-tam hits
    'intro': dict(R=(-0.6, 33.0), T=(0.0, 30.0), verse=14.6, tamtam=[0.0]),
    'chorus': dict(R=(44.3, 70.0), T=(46.8, 68.0), verse=999, tamtam=[46.492 + 16 * 4 * 60 / 180.676]),
}
SEG = os.environ.get('SEG', 'intro')
R0, R1 = SEGMENTS[SEG]['R']
VERSE = SEGMENTS[SEG]['verse']
random.seed(7)

# ---------------------------------------------------------------- MIDI input
def track_notes(mf, idx):
    t, on, out = 0, {}, []
    tpb = mf.ticks_per_beat
    for m in mf.tracks[idx]:
        t += m.time
        if m.type == 'note_on' and m.velocity > 0:
            on[(m.note, m.channel)] = (t, m.velocity)
        elif m.type in ('note_off', 'note_on') and (m.note, m.channel) in on:
            s, v = on.pop((m.note, m.channel))
            out.append([s / tpb * SPB, t / tpb * SPB, m.note, v])
    return sorted(out)

def window(ns, a=max(R0 - 0.5, -1), b=R1 - 1.0):
    return [n for n in ns if n[1] > a and n[0] < b]

def dedupe(ns):
    """Drop notes of the same pitch that start within 30 ms of each other (stacked layers)."""
    out, seen = [], {}
    for n in sorted(ns):
        k = n[2]
        if k in seen and abs(seen[k] - n[0]) < 0.03:
            continue
        seen[k] = n[0]; out.append(n)
    return out

def beat_pos(t):
    return ((t - BAR0) / SPB) % 4

def on_beat(t, beats, tol=0.12):
    p = beat_pos(t)
    return any(min(abs(p - b), 4 - abs(p - b)) < tol for b in beats)

def chord_at(chords, t):
    cur = [n for n in chords if n[0] <= t + 0.02 < n[1] + 0.05]
    if not cur:
        prev = [n for n in chords if n[0] <= t + 0.02]
        if not prev: return []
        s = max(n[0] for n in prev); cur = [n for n in prev if n[0] == s]
    return sorted(set(n[2] for n in cur))

def place(pc, lo):
    """Pitch class pc placed at or above lo."""
    n = lo + ((pc - lo) % 12)
    return n

# ---------------------------------------------------------------- performance helpers
def humanize(ns, ms=7, vel=4):
    return [[n[0] + random.uniform(-ms, ms) / 1000, n[1], n[2], max(1, min(127, int(n[3] + random.randint(-vel, vel))))] for n in ns]

def legato(ns, overlap=0.035, max_gap=0.14):
    """Long patches have no true legato in Discover: tie phrases by overlapping notes."""
    ns = sorted(ns)
    for i in range(len(ns) - 1):
        gap = ns[i + 1][0] - ns[i][1]
        if gap < max_gap:
            ns[i][1] = ns[i + 1][0] + overlap
    return ns

def cc_curve(ns, lo, hi, swell=0.0, base_shift=0, step=0.02, smooth=0.12):
    """CC1 dynamics following note velocities, with a per-bar swell, smoothed."""
    ts = np.arange(R0, R1, step)
    target = np.full(len(ts), np.nan)
    for s, e, _, v in ns:
        m = (ts >= s - 0.05) & (ts < e)
        val = lo + (hi - lo) * (v - 40) / 87 + base_shift
        target[m] = np.where(np.isnan(target[m]), val, np.maximum(target[m], val))
    # hold last value through rests
    last = lo
    for i in range(len(target)):
        if np.isnan(target[i]): target[i] = last
        else: last = target[i]
    if swell:
        ph = ((ts - BAR0) / (2 * BAR)) % 1.0
        target += swell * (np.sin(np.pi * ph) - 0.5)
    a = step / smooth; y = np.empty_like(target); acc = target[0]
    for i, x in enumerate(target):
        acc += a * (x - acc); y[i] = acc
    return [(t, int(np.clip(v, 0, 127))) for t, v in zip(ts, y)]

def to_msgs(ns, ccs=(), expr=None):
    msgs = []
    if expr is not None:
        msgs.append(Message('control_change', control=11, value=expr, time=0.0))
    for cc, curve in ccs:
        prev = None
        for t, v in curve:
            if v != prev:
                msgs.append(Message('control_change', control=cc, value=v, time=max(0.0, t - R0))); prev = v
    for s, e, n, v in ns:
        if not (0 <= n <= 127): continue
        msgs.append(Message('note_on', note=n, velocity=v, time=max(0.0, s - R0)))
        msgs.append(Message('note_off', note=n, velocity=0, time=max(0.001, e - R0)))
    msgs.sort(key=lambda m: (m.time, 0 if m.type == 'control_change' else (1 if m.type == 'note_off' else 2)))
    return msgs

# ---------------------------------------------------------------- arrangement
def sec_dyn(ns, verse_scale=0.82):
    """Pull dynamics down in the verse so the riff/chorus can open up."""
    return [[a, b, n, int(v * (verse_scale if a >= VERSE else 1.0))] for a, b, n, v in ns]

def build_parts():
    mf = mido.MidiFile(MIDI)
    T = {mf.tracks[i].name: i for i in range(len(mf.tracks))}
    get = lambda *names: window(sum((track_notes(mf, T[n]) for n in names), []))
    lead = dedupe(get('Lead melody (violin/cello)'))
    hook = dedupe(get('Orchestra lines riff_high', 'Orchestra lines riff_fill'))
    counter = dedupe(get('Orchestra lines chorus_high'))
    inner = dedupe(get('Orchestra lines chorus_inner', 'Orchestra lines riff_pedal', 'Orchestra lines riff_inner',
                       'Orchestra lines verse1_inner'))
    chords = get('Chords chords verified (pad voicing)')
    cbass = dedupe(get('Chords chord bass verified (bass_pc)'))
    bass = dedupe(get('Bass'))
    gtr = get('Guitars rhythm open/accent', 'Guitars rhythm palm-muted')
    kit = get('Drums Drum kit')
    fx = get('Drums Orchestral perc + FX')
    upper = dedupe(get('Orchestra pads choir pads (vocal stem)', 'Choir choir upper (S/A)'))
    men = dedupe(get('Choir choir men / chant'))

    P = {}
    # Lead: Violins 1 long an octave up (soaring); the riff hook on Violins 1 at pitch.
    v1 = legato(humanize([[s, e, n + 12, min(127, v + 8)] for s, e, n, v in lead] +
                         [[s, e, n, min(127, v + 10)] for s, e, n, v in hook]))
    P['vln1_lead'] = dict(inst='Strings_Violins_1', art=0, notes=v1,
                          ccs=[(1, cc_curve(v1, 72, 120, swell=10))], expr=120)
    # Celli double the melody an octave below the violins (= written pitch); softer in the verse.
    vc = legato(humanize(sec_dyn([[s, e, n, v] for s, e, n, v in lead], 0.75)))
    P['vc_lead'] = dict(inst='Strings_Celli', art=0, notes=vc,
                        ccs=[(1, cc_curve(vc, 55, 105, swell=8))], expr=105)

    # Trumpets: riff hook / chorus counter-line an octave down, plus the choir chant top line.
    tp = [[s, e, n - 12, v] for s, e, n, v in hook + counter]
    tp += [[s, e, n, int(v * 0.9)] for s, e, n, v in upper if n <= 80]
    tp = legato(humanize(dedupe(tp)), max_gap=0.2)
    P['tpt_counter'] = dict(inst='Brass_Trumpets_a3', art=0, notes=tp,
                            ccs=[(1, cc_curve(tp, 60, 108, swell=8))], expr=105)

    # Horns: pad voicing + inner lines + chant; trombones: low chord tones + the men's chant.
    hn = [[s, e + 0.03, n, 85] for s, e, n, v in chords] + [[s, e, n, v] for s, e, n, v in inner]
    hn += [[s, e, n, v] for s, e, n, v in upper if n <= 77]
    hn = humanize(sec_dyn(dedupe(hn), 0.7), ms=5)
    P['horns_chords'] = dict(inst='Brass_Horns_a4', art=0, notes=hn,
                             ccs=[(1, cc_curve(hn, 55, 102, swell=12))], expr=110)
    tb, groups = [], {}
    for s, e, n, v in chords: groups.setdefault(round(s, 3), []).append((e, n))
    for s, items in groups.items():
        e = max(i[0] for i in items)
        for n in sorted(i[1] for i in items)[:2]: tb.append([s, e + 0.03, n - 12, 85])
    tb += [[s, e, n - 12 if n > 62 else n, v] for s, e, n, v in men]
    tb = humanize(sec_dyn(dedupe(tb), 0.7), ms=5)
    P['tbn_chords'] = dict(inst='Brass_Tenor_Trombones_a3', art=0, notes=tb,
                           ccs=[(1, cc_curve(tb, 55, 100, swell=12))], expr=105)

    # Driving 8ths: guitar onsets -> Violins 2 + Violas spiccato on chord tones.
    onsets = {}
    for s, e, n, v in gtr:
        k = round(s / (SPB / 2)) * (SPB / 2)          # 8th grid
        onsets[k] = max(onsets.get(k, 0), v)
    v2, va = [], []
    for k, v in sorted(onsets.items()):
        ch = chord_at(chords, k) or [61, 64, 68]
        root = chord_at(cbass, k)
        rpc = (root[0] if root else ch[0]) % 12
        vel = int(np.clip(v * 0.95 + (12 if on_beat(k, [0, 2]) else 0), 50, 120))
        if k >= VERSE: vel = int(vel * 0.85)
        v2.append([k, k + SPB * 0.45, place(max(ch) % 12, 64), vel])
        v2.append([k, k + SPB * 0.45, place(rpc, 61), vel - 6])
        va.append([k, k + SPB * 0.45, place(rpc, 55), vel])
        va.append([k, k + SPB * 0.45, place((rpc + 7) % 12, 55), vel - 8])
    P['vln2_spicc'] = dict(inst='Strings_Violins_2', art=1, notes=humanize(dedupe(v2), ms=5), ccs=[(1, [(R0, 96)])], expr=110)
    P['vla_spicc'] = dict(inst='Strings_Violas', art=1, notes=humanize(dedupe(va), ms=5), ccs=[(1, [(R0, 96)])], expr=110)

    # Bass line: basses + celli spiccato (celli an octave up), basses long underneath on the chord roots.
    bs = [[s, min(e, s + SPB * 0.5), n if n >= 28 else n + 12, min(120, v + 5)] for s, e, n, v in bass]
    P['cb_spicc'] = dict(inst='Strings_Basses', art=1, notes=humanize(bs, ms=4), ccs=[(1, [(R0, 100)])], expr=115)
    P['vc_spicc'] = dict(inst='Strings_Celli', art=1, notes=humanize([[s, e, n + 12, v - 4] for s, e, n, v in bs], ms=4),
                         ccs=[(1, [(R0, 92)])], expr=105)
    cbl = humanize([[s, e + 0.05, n if n >= 28 else n + 12, 80] for s, e, n, v in cbass], ms=4)
    P['cb_long'] = dict(inst='Strings_Basses', art=0, notes=cbl, ccs=[(1, cc_curve(cbl, 55, 85, swell=10))], expr=100)

    # Low brass on downbeats / long chord changes.
    lb = []
    for s, e, n, v in cbass:
        if on_beat(s, [0]) or (e - s) > SPB * 2:
            lb.append([s, s + min(e - s, SPB * 1.6), n if n >= 30 else n + 12, 100])
    lb = sec_dyn(lb, 0.8)
    P['btbn_down'] = dict(inst='Brass_Bass_Trombones_a2', art=0, notes=humanize(lb, ms=5),
                          ccs=[(1, cc_curve(lb, 65, 105))], expr=110)
    P['tuba_down'] = dict(inst='Brass_Tuba', art=0, notes=humanize([[s, e, n - 12 if n - 12 >= 26 else n, v] for s, e, n, v in lb], ms=5),
                          ccs=[(1, cc_curve(lb, 60, 100))], expr=105)

    # Percussion: sparse and big. Cymbal-swell ramps in the FX track become timpani rolls.
    timp, perc = [], []
    def troot(t):
        r = chord_at(cbass, t); return place((r[0] if r else 37) % 12, 50)
    for s, e, n, v in kit:
        if n in (35, 36) and (on_beat(s, [0]) or (on_beat(s, [2]) and v >= 95)):
            timp.append([s, s + 0.3, troot(s), int(np.clip(v + (12 if on_beat(s, [0]) else 0), 70, 127))])
        elif n in (38, 40) and on_beat(s, [1, 3]) and v >= 80:
            perc.append([s, s + 0.2, 52, int(v * (0.6 if s >= VERSE else 0.75))])   # orchestral snare
        elif n in (49, 57, 52):
            perc.append([s, s + 0.5, 53, 112]); perc.append([s, s + 0.5, 48, 118])  # clash + gran cassa
    for s, e, n, v in fx:
        if n == 55 and v < 110:
            timp.append([s, s + 0.08, troot(s), int(np.clip(30 + v * 0.8, 30, 120))])  # roll stroke
        elif n == 55:
            perc.append([s, s + 0.5, 53, 115])
        elif n == 35:
            perc.append([s, s + 0.4, 48, int(np.clip(v + 30, 80, 125))])
    for t in SEGMENTS[SEG]['tamtam']:
        perc.append([t - 0.01, t + 1.0, 59, 105])
    P['timpani'] = dict(inst='Percussion_Percussion', art=0, notes=humanize(dedupe(timp), ms=3), ccs=[(1, [(R0, 110)])], expr=120)
    P['perc'] = dict(inst='Percussion_Percussion', art=1, notes=humanize(dedupe(perc), ms=3), ccs=[(1, [(R0, 110)])], expr=118)

    # Choir (VPO mixed sustain samples), short attack so the intro chant stays rhythmic.
    P['choir'] = dict(sfz=True, notes=humanize([[s, e + 0.15, n, v] for s, e, n, v in upper + men], ms=10))
    return P

# ---------------------------------------------------------------- renderers
def render_bbc(part):
    import bbc
    p = bbc.load(part['inst'], part['art'])
    dur = R1 - R0
    p.process([], duration=3.0, sample_rate=SR, num_channels=2, reset=True)   # let samples stream in
    msgs = to_msgs(part['notes'], part.get('ccs', ()), part.get('expr'))
    a = p.process(msgs, duration=dur, sample_rate=SR, num_channels=2, reset=False, buffer_size=512)
    return a.T

def read_smpl_loop(path):
    b = open(path, 'rb').read()
    i = b.find(b'smpl')
    if i < 0: return None
    n = struct.unpack('<I', b[i + 36:i + 40])[0]
    if n == 0: return None
    s, e = struct.unpack('<II', b[i + 52:i + 60])
    return s, e

NOTE = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
def key(s):
    s = s.strip().lower()
    if s.lstrip('-').isdigit(): return int(s)
    m = re.match(r'([a-g])(#|b)?(-?\d)', s)
    return NOTE[m.group(1)] + (1 if m.group(2) == '#' else -1 if m.group(2) == 'b' else 0) + (int(m.group(3)) + 1) * 12

def render_choir(part):
    sfz = r"C:\Users\hw549\Downloads\YTP1\_samples\VirtualPlayingOrchestra\Virtual-Playing-Orchestra3\Vocals\choir-MIXED-sustain.sfz"
    base = os.path.dirname(sfz)
    regions, cur = [], {}
    for line in open(sfz, encoding='utf-8', errors='ignore'):
        line = line.split('//')[0].strip()
        if not line: continue
        if line.startswith('<region>'):
            if 'sample' in cur: regions.append(cur)
            cur = {}; continue
        if line.startswith('<group>'):
            if 'sample' in cur: regions.append(cur)
            cur = {}; continue
        for k, v in re.findall(r'(\w+)=([^=]+?)(?=\s+\w+=|$)', line):
            cur[k] = v.strip()
    if 'sample' in cur: regions.append(cur)
    out = np.zeros((int((R1 - R0) * SR), 2))
    cache = {}
    for s, e, n, v in part['notes']:
        cand = [r for r in regions if key(r.get('lokey', r.get('key', '0'))) <= n <= key(r.get('hikey', r.get('key', '127')))]
        if not cand: continue
        for r in cand:   # male + female layers
            path = os.path.normpath(os.path.join(base, r['sample'].replace('\\', os.sep)))
            if path not in cache:
                d, sr = sf.read(path, always_2d=True); cache[path] = (d, sr, read_smpl_loop(path))
            d, sr, loop = cache[path]
            ratio = 2 ** ((n - key(r.get('pitch_keycenter', r.get('lokey')))) / 12) * sr / SR
            need = int((e - s + 1.3) * SR)
            idx = np.arange(need) * ratio
            if loop and idx[-1] >= loop[1]:
                L0, L1 = loop
                over = idx >= L1
                idx[over] = L0 + (idx[over] - L0) % (L1 - L0)
            idx = np.clip(idx, 0, len(d) - 2)
            i0 = idx.astype(int); fr = (idx - i0)[:, None]
            y = d[i0] * (1 - fr) + d[i0 + 1] * fr
            if y.shape[1] == 1: y = np.repeat(y, 2, 1)
            env = np.ones(need)
            att = int(min(0.5, max(0.04, (e - s) * 0.4)) * SR); rel = int(1.2 * SR); hold = int((e - s) * SR)
            env[:att] = np.linspace(0, 1, att)
            env[hold:] = np.exp(-np.arange(need - hold) / (0.35 * SR))
            gain = 10 ** (float(r.get('volume', 0)) / 20) * (v / 127)
            pan = float(r.get('pan', 0)) / 100
            y = y * env[:, None] * gain * np.array([1 - max(0, pan), 1 + min(0, pan)])
            o = int((s - R0) * SR)
            if o < 0: y = y[-o:]; o = 0
            m = min(len(y), len(out) - o)
            out[o:o + m] += y[:m]
    return out

if __name__ == '__main__':
    os.makedirs(STEMS, exist_ok=True)
    parts = build_parts()
    want = sys.argv[1:] or list(parts)
    for name in want:
        t = time.time(); part = parts[name]
        a = render_choir(part) if part.get('sfz') else render_bbc(part)
        sf.write(os.path.join(STEMS, f'{SEG}_{name}.wav'), a.astype(np.float32), SR, subtype='FLOAT')
        print(f'{name:14s} notes={len(part["notes"]):4d} peak={np.abs(a).max():.3f} rms={np.sqrt((a**2).mean()):.4f} {time.time()-t:.0f}s', flush=True)
