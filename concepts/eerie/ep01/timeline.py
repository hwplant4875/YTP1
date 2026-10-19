# Build timeline.json (segment start times, word timings, sound events) from the narration files.
# python3 timeline.py voicedir out.json [last_segment_id]
import json, os, sys, subprocess
import numpy as np
vdir, out = sys.argv[1], sys.argv[2]
last = sys.argv[3] if len(sys.argv) > 3 else None
segs = json.load(open(os.path.join(os.path.dirname(__file__), 'segments.json')))
GAP = 0.7     # silence between lines; with the voice's own breaths this lands near the reference's ~0.75 s median
LEAD = 2.3    # the opening knocks play before the first line
# extra silence after a line, and the sound placed in it: (seconds, [(sound, offset after speech end)])
EXTRA = {
    's01': (0.3, []),
    's03': (0.2, []),
    's04': (1.3, [('riser', -0.1)]),      # music-only breaks before each step card, like the reference's [music] beats
    's09': (0.9, [('boom', 0.05)]),
    's10': (1.3, [('riser', 0.0)]),
    's14': (0.2, []),
    's15': (2.1, [('meow1', 0.25)]),
    's18': (2.9, [('meow2', 0.2), ('riser', 1.3)]),
    's20': (0.2, []),
    's21': (2.4, [('knock3', 0.5)]),
    's26': (0.3, []),
    's30': (1.5, [('riser', 0.1)]),
    's31': (1.6, [('error', 0.1), ('tapestop', 0.0)]),
    's33': (2.8, [('knock3', 1.0)]),
}

def speech_bounds(mp3):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp3, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    e = np.array([np.sqrt((a[j:j + 160] ** 2).mean()) for j in range(0, len(a) - 160, 160)])
    on = np.where(20 * np.log10(e + 1e-6) > -40)[0]
    return on[0] * 0.01, (on[-1] + 1) * 0.01

t = LEAD; tl = []; events = [{'type': 'knock3', 't': 0.15}]
for s in segs:
    mp3 = os.path.join(vdir, s['id'] + '.mp3')
    lead, tail = speech_bounds(mp3)
    al = json.load(open(os.path.join(vdir, s['id'] + '.json')))
    words = []; cur = None
    for ch, cs, ce in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
        if ch.isspace():
            if cur: words.append(cur); cur = None
            continue
        if cur is None: cur = {'w': '', 's': t + cs, 'e': t + ce}
        cur['w'] += ch; cur['e'] = t + min(ce, tail)
    if cur: words.append(cur)
    speech_end = t + tail
    tl.append({'id': s['id'], 'text': s['text'], 'start': t, 'end': speech_end, 'file': s['id'] + '.mp3', 'cut': tail, 'words': words})
    extra, sounds = EXTRA.get(s['id'], (0, []))
    for name, off in sounds: events.append({'type': name, 't': speech_end + off})
    t = speech_end + GAP + extra
    if s['id'] == last: break
# word-cued sounds and in-line shot cuts (engine.js reads 'cuts' for its glitch transitions)
import re
norm = lambda w: re.sub(r"[^a-z0-9']", '', w.lower())
def wt(seg, word, nth=1):
    n = 0
    for w in seg['words']:
        if norm(w['w']) == word:
            n += 1
            if n == nth: return w['s']
    return seg['end']
S = {seg['id']: seg for seg in tl}
def cue(sid, word, nth=1, off=0.0):
    return wt(S[sid], word, nth) + off if sid in S else None
for sid, word, nth, snd, off in [('s07', 'scratch', 1, 'scratch', 0), ('s12', 'light', 1, 'hum', -0.1), ('s13', 'gap', 1, 'heartbeat', 0),
                                 ('s14', 'count', 1, 'heartbeat', 0), ('s17', 'something', 1, 'breath', 0.2), ('s28', 'open', 1, 'creak', 0.1),
                                 ('s09', 'height', 1, 'riser', 0.0), ('s15', 'meow', 1, 'staticlong', 0.3)]:
    c = cue(sid, word, nth, off)
    if c is not None: events.append({'type': snd, 't': c})
for sid in ('s05', 's11', 's19', 's31'):
    if sid in S: events.append({'type': 'stinger', 't': S[sid]['start'] - 0.05})
cuts = [seg['start'] for seg in tl[1:]]
for sid, word, nth, off in [('s04', 'there', 1, -0.1), ('s08', 'cats', 1, -0.05), ('s10', 'legs', 1, -0.1), ('s10', 'mind', 1, -0.6), ('s13', 'four', 1, -0.1),
                            ('s16', 'meow', 2, -0.2), ('s23', 'footsteps', 1, -0.1), ('s25', 'tail', 1, -0.3), ('s26', 'sleep', 1, -0.9), ('s27', 'thought', 1, -0.1),
                            ('s32', 'nobody', 1, -0.1), ('s33', 'this', 1, -0.1)]:
    c = cue(sid, word, nth, off)
    if c is not None: cuts.append(c)
for e in events:
    if e['type'] in ('boom', 'meow2', 'error'): cuts.append(e['t'] - (0.15 if e['type'] == 'meow2' else 0))
cuts.sort()
json.dump({'total': t + 0.4, 'segments': tl, 'events': events, 'cuts': cuts}, open(out, 'w'), indent=1)
print('total', round(t, 2), 'segments', len(tl))
