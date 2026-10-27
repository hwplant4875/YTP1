"""Turn the owner's reference duet MIDI (Violin + Cello, flat velocity 50) into an expressive piano performance.

Violin -> right hand, Cello -> left hand. Adds:
  - melody voicing (top note of each RH onset louder than inner notes, LH under the RH)
  - phrase dynamics from register/density per 2 bars, accents on downbeats
  - humanized timing/velocity, slight RH-before-LH lead on chords
  - sustain pedal re-caught on every bass (harmony) change

Usage: python ref_piano.py IN.mid OUT.mid
"""
import sys, random
import numpy as np, mido

random.seed(5)

def load(path):
    mf = mido.MidiFile(path)
    tempo = 500000
    for m in mf.tracks[0]:
        if m.type == 'set_tempo': tempo = m.tempo; break
    spb = tempo / 1e6
    parts = []
    for tr in mf.tracks:
        t, on, ns = 0, {}, []
        for m in tr:
            t += m.time
            if m.type == 'note_on' and m.velocity > 0: on[m.note] = t
            elif m.type in ('note_off', 'note_on') and m.note in on:
                s = on.pop(m.note); ns.append([s / mf.ticks_per_beat * spb, t / mf.ticks_per_beat * spb, m.note])
        if ns: parts.append(sorted(ns))
    return parts, spb, mf.ticks_per_beat

def phrase_curve(rh, lh, spb, length):
    """0..1 intensity per 2-bar block from RH register + overall note density, smoothed."""
    blk = 8 * spb; nb = int(length / blk) + 1
    reg = np.zeros(nb); den = np.zeros(nb)
    for s, e, n in rh:
        b = int(s / blk); reg[b] = max(reg[b], n); den[b] += 1
    for s, e, n in lh: den[int(s / blk)] += 0.5
    z = lambda x: (x - x.min()) / (np.ptp(x) + 1e-9)
    c = 0.6 * z(reg) + 0.4 * z(den)
    c = np.convolve(np.pad(c, 1, mode='edge'), [0.25, 0.5, 0.25], 'valid')
    return lambda t: float(c[min(nb - 1, int(t / blk))])

def perform(rh, lh, spb, length):
    curve = phrase_curve(rh, lh, spb, length)
    beat = lambda t: (t / spb) % 4
    out = []
    groups = {}
    for s, e, n in rh: groups.setdefault(round(s, 3), []).append([s, e, n])
    for s, ns in groups.items():
        top = max(x[2] for x in ns)
        dyn = 58 + 40 * curve(s)
        acc = 8 if abs(beat(s)) < 0.05 else 4 if abs(beat(s) - 2) < 0.05 else 0
        jit = random.uniform(-0.006, 0.006)
        for x in ns:
            v = dyn + acc + (10 if x[2] == top else -8) + random.uniform(-4, 4)
            out.append([s + jit - 0.004, max(x[1], s + 0.12), x[2], int(np.clip(v, 25, 118)), 'R'])
    groups = {}
    for s, e, n in lh: groups.setdefault(round(s, 3), []).append([s, e, n])
    for s, ns in groups.items():
        low = min(x[2] for x in ns)
        dyn = 48 + 34 * curve(s)
        acc = 10 if abs(beat(s)) < 0.05 else 4 if abs(beat(s) - 2) < 0.05 else 0
        jit = random.uniform(-0.006, 0.006)
        for x in ns:
            v = dyn + acc + (6 if x[2] == low else -6) + random.uniform(-4, 4)
            out.append([s + jit, max(x[1], s + 0.1), x[2], int(np.clip(v, 22, 110)), 'L'])
    # pedal: re-catch whenever the lowest LH pitch class changes
    pedal, last = [], None
    for s in sorted(groups):
        pc = min(x[2] for x in groups[s]) % 12
        if pc != last:
            pedal += [(max(0.0, s - 0.03), 0), (s + 0.05, 110)]
            last = pc
    pedal.append((length + 0.5, 0))
    return out, pedal

def write(notes, pedal, spb, tpb, path):
    mid = mido.MidiFile(type=1, ticks_per_beat=tpb)
    tick = lambda sec: max(0, int(round(sec / spb * tpb)))
    meta = mido.MidiTrack(); mid.tracks.append(meta)
    meta.append(mido.MetaMessage('set_tempo', tempo=int(spb * 1e6)))
    meta.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    for hand, name in (('R', 'Piano RH'), ('L', 'Piano LH')):
        tr = mido.MidiTrack(); mid.tracks.append(tr)
        tr.append(mido.MetaMessage('track_name', name=name))
        ev = [] if hand == 'R' else [(tick(t), 0, mido.Message('control_change', control=64, value=v)) for t, v in pedal]
        for s, e, n, v, h in notes:
            if h != hand: continue
            ev.append((tick(s), 2, mido.Message('note_on', note=n, velocity=v)))
            ev.append((tick(e), 1, mido.Message('note_off', note=n, velocity=0)))
        ev.sort(key=lambda x: (x[0], x[1])); last = 0
        for t, _, m in ev:
            tr.append(m.copy(time=t - last)); last = t
    mid.save(path)

if __name__ == '__main__':
    (rh, lh), spb, tpb = load(sys.argv[1])
    length = max(x[1] for x in rh + lh)
    notes, pedal = perform(rh, lh, spb, length)
    write(notes, pedal, spb, tpb, sys.argv[2])
    vs = [x[3] for x in notes]
    print(f'{sys.argv[2]}: {len(notes)} notes, {length:.1f}s, vel mean {np.mean(vs):.0f} sd {np.std(vs):.1f}, pedal changes {len(pedal)//2}')
