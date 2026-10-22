# Split hedwig_trio.mid (v2) into per-instrument MIDI files for sfizz_render.
# Piano velocities are compressed downward so Salamander plays its softer, mellower layers (felt-like tone).
import mido, sys
src, out = sys.argv[1], sys.argv[2]
mf = mido.MidiFile(src)
abs_t, ev = 0, []
for m in mido.merge_tracks(mf.tracks):
    abs_t += m.time
    if m.is_meta and m.type in ('set_tempo', 'time_signature'): ev.append((abs_t, m))
mt, last = mido.MidiTrack(), 0
for t, m in ev: mt.append(m.copy(time=t - last)); last = t
print('tracks', [t.name for t in mf.tracks], 'length', round(mf.length, 1), 's', 'tempo', [m.tempo for _, m in ev if m.type == 'set_tempo'])
for i, name in enumerate(['piano', 'bass', 'drums']):
    tr = mido.MidiTrack()
    for m in mf.tracks[i]:
        if m.is_meta and m.type in ('set_tempo', 'time_signature'): m = mido.MetaMessage('text', text='', time=m.time)
        if name == 'piano' and m.type == 'note_on' and m.velocity > 0:
            m = m.copy(velocity=max(12, min(70, int(14 + 0.62 * m.velocity))))
        tr.append(m)
    f = mido.MidiFile(type=0, ticks_per_beat=mf.ticks_per_beat); f.tracks.append(mido.merge_tracks([mt, tr]))
    f.save(f'{out}/{name}.mid')
    vs = [m.velocity for m in tr if m.type == 'note_on' and m.velocity > 0]
    print(name, len(vs), 'vel', min(vs) if vs else '-', max(vs) if vs else '-')
