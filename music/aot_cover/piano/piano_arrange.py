"""Guren no Yumiya - solo piano arrangement of cover 0-30 s (original 0:21 onward).

Reads the band transcription MIDI and writes a two-hand piano MIDI (RH / LH tracks,
sustain pedal) for rendering in FL Studio.

Usage: python piano_arrange.py OUT.mid
"""
import sys, random
import mido
from arrange import MIDI, SPB, track_notes, dedupe, chord_at, place, on_beat

random.seed(11)
END = 30.4
INTRO, RIFF, VERSE = 0.0, 2.66, 14.6
TPB = 480
BPM = 60 / SPB

def notes(mf, *names):
    T = {t.name: i for i, t in enumerate(mf.tracks)}
    return sorted(sum((track_notes(mf, T[n]) for n in names), []))

def top_line(ns):
    """Highest note per onset (monophonic melody)."""
    by = {}
    for s, e, n, v in ns:
        k = round(s, 2)
        if k not in by or n > by[k][2]: by[k] = [s, e, n, v]
    out = sorted(by.values())
    for i in range(len(out) - 1):          # no overlaps in the line
        out[i][1] = min(out[i][1], out[i + 1][0] - 0.01)
    return out

def build():
    mf = mido.MidiFile(MIDI)
    lead = notes(mf, 'Lead melody (violin/cello)')
    hook = notes(mf, 'Orchestra lines riff_high', 'Orchestra lines riff_fill')
    upper = notes(mf, 'Choir choir upper (S/A)')
    chords = notes(mf, 'Chords chords verified (pad voicing)')
    cbass = dedupe(notes(mf, 'Chords chord bass verified (bass_pc)'))
    gtr = notes(mf, 'Guitars rhythm open/accent', 'Guitars rhythm palm-muted')

    # ---- right-hand melody
    chant = [n for n in top_line(upper) if n[0] < END]
    hk = [n for n in top_line(hook) if n[0] < VERSE and not any(c[0] - 0.05 <= n[0] < c[1] for c in chant)]
    ld = [[s, e, n + 12, v] for s, e, n, v in top_line(lead) if VERSE <= s < END]
    rh = []
    for s, e, n, v in sorted(chant + hk):
        while n > 86: n -= 12
        vel = 96 if s < VERSE else 84
        rh.append([s, e, n, vel + (6 if on_beat(s, [0, 2]) else 0)])
        rh.append([s, e, n - 12, vel - 14])                          # octave doubling (big sections)
    for s, e, n, v in ld:
        vel = int(70 + (v - 60) * 0.5) + (6 if on_beat(s, [0, 2]) else 0)
        rh.append([s, max(e, s + 0.12), n, vel])
        ch = chord_at(chords, s)
        if ch and on_beat(s, [0, 1, 2, 3], tol=0.1):                # harmony note below on beats
            below = [c for c in sorted(set(place(p % 12, n - 9) for p in ch)) if n - 9 <= c < n - 2]
            if below: rh.append([s, max(e, s + 0.12), below[-1], vel - 22])

    # ---- right-hand chord stabs on harmony changes (between melody and LH)
    groups = {}
    for s, e, n, v in chords:
        if s < END: groups.setdefault(round(s, 2), [s, e, set()])[2].add(n % 12)
    for s, e, pcs in groups.values():
        loud = s < VERSE
        voic = sorted(set(place(p, 55 if loud else 53) for p in pcs))[:3]
        for k, n in enumerate(voic):
            rh.append([s + 0.004 * k, min(e, s + (0.6 if loud else 1.2)), n, (74 if loud else 56) - 3 * k])

    # ---- left hand: octave 8ths on guitar accents (intro/riff), broken chords in the verse
    lh = []
    grid = sorted({round(s / (SPB / 2)) * (SPB / 2) for s, e, n, v in gtr if s < VERSE})
    for k in grid:
        r = chord_at(cbass, k + 0.03)
        if not r: continue
        root = place(r[0] % 12, 31)
        vel = 92 if on_beat(k, [0]) else 80 if on_beat(k, [2]) else 66
        lh.append([k, k + SPB * 0.45, root, vel])
        lh.append([k, k + SPB * 0.45, root + 12, vel - 8])
    t = VERSE
    i = 0
    while t < END:                                                 # rolling 8ths: bass, then chord tones up and back
        r = chord_at(cbass, t + 0.03)
        ch = chord_at(chords, t + 0.03)
        bass = place(r[0] % 12, 33) if r else 37
        tones = sorted({place(c % 12, bass + 5) for c in ch} | {bass + 12}) if ch else [bass + 7, bass + 12]
        arp = [bass] + tones[:3] + tones[1:3][::-1] + [tones[0]]
        n = arp[i % len(arp)] if i % 8 else bass
        vel = 70 if i % 8 == 0 else 56 if i % 2 == 0 else 49
        lh.append([t, t + SPB * 0.9, n, vel])
        t += SPB / 2; i += 1

    # ---- sustain pedal: re-pedal on every harmony change
    changes = sorted({s for s, e, n, v in cbass if s < END} | {0.0})
    pedal = []
    for s in changes:
        pedal += [(max(0, s - 0.03), 0), (s + 0.04, 127 if s >= VERSE else 100)]
    pedal.append((END, 0))
    return rh, lh, pedal

def hum(ns, ms=6, vel=4):
    out = []
    for s, e, n, v in ns:
        d = random.uniform(-ms, ms) / 1000
        out.append([max(0, s + d), max(s + d + 0.03, e), n, max(1, min(127, v + random.randint(-vel, vel)))])
    return out

def write(path):
    rh, lh, pedal = build()
    mid = mido.MidiFile(type=1, ticks_per_beat=TPB)
    tick = lambda sec: int(round(sec / SPB * TPB))
    meta = mido.MidiTrack(); mid.tracks.append(meta)
    meta.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM)))
    meta.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    for name, ns, cc in [('Piano RH', hum(rh), []), ('Piano LH', hum(lh), pedal)]:
        tr = mido.MidiTrack(); mid.tracks.append(tr)
        tr.append(mido.MetaMessage('track_name', name=name))
        tr.append(mido.Message('program_change', program=0, channel=0))
        ev = [(tick(t), 0, mido.Message('control_change', control=64, value=v, channel=0)) for t, v in cc]
        for s, e, n, v in dedupe(ns):
            ev.append((tick(s), 2, mido.Message('note_on', note=n, velocity=v, channel=0)))
            ev.append((tick(e), 1, mido.Message('note_off', note=n, velocity=0, channel=0)))
        ev.sort(key=lambda x: (x[0], x[1]))
        last = 0
        for t, _, m in ev:
            tr.append(m.copy(time=t - last)); last = t
    mid.save(path)
    print(path, 'RH', len(rh), 'LH', len(lh), 'pedal', len(pedal))

if __name__ == '__main__':
    write(sys.argv[1] if len(sys.argv) > 1 else 'guren_piano_0-30.mid')
