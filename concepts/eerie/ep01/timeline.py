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
    's05': (1.3, [('riser', -0.1)]),      # music-only breaks before each rule card, like the reference's [music] beats
    's10': (1.6, [('boom', 0.05), ('knock3', 0.35), ('bell', 0.35)]),
    's11': (1.2, [('riser', 0.1)]),
    's16': (2.1, [('meow1', 0.25)]),
    's19': (2.9, [('meow2', 0.2), ('riser', 1.3)]),
    's22': (2.2, [('knock3', 0.3), ('bell', 0.3)]),
    's24': (0.6, [('boom', 0.0)]),
    's30': (1.5, [('riser', 0.1)]),
    's31': (0.6, []),
    's32': (0.5, [('hiss', 0.1)]),
    's39': (0.4, []),
    's41': (0.6, [('bark', 0.0)]),
    's42': (0.3, []),
    's46': (2.9, [('bell', 0.7), ('knock3', 0.9)]),
}

def speech_bounds(mp3):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp3, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    e = np.array([np.sqrt((a[j:j + 160] ** 2).mean()) for j in range(0, len(a) - 160, 160)])
    on = np.where(20 * np.log10(e + 1e-6) > -40)[0]
    return on[0] * 0.01, (on[-1] + 1) * 0.01

t = LEAD; tl = []; events = [{'type': 'knock3', 't': 0.15}, {'type': 'bell', 't': 0.15}]
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
for sid, word, nth, snd, off in [('s08', 'scratch', 1, 'scratch', 0), ('s11', 'bell', 1, 'bell', 0.1), ('s13', 'light', 1, 'hum', -0.1),
                                 ('s14', 'two', 1, 'heartbeat', 0), ('s15', 'count', 1, 'heartbeat', 0), ('s16', 'meow', 1, 'staticlong', 0.3),
                                 ('s19', 'high', 1, 'breath', 0.3), ('s23', 'bell', 1, 'bell', 0.1), ('s23', 'put', 1, 'bell', 0.7), ('s24', 'where', 1, 'bell', 0.1),
                                 ('s32', 'turn', 1, 'handle', 0.0), ('s34', 'dodge', 1, 'whoosh', -0.5), ('s34', 'every', 1, 'whoosh', 0.1),
                                 ('s40', 'bark', 1, 'bark', 0.25), ('s42', 'flatten', 1, 'hiss', 0.0), ('s43', 'sun', 1, 'chime', 0.2)]:
    c = cue(sid, word, nth, off)
    if c is not None: events.append({'type': snd, 't': c})
for sid in ('s06', 's12', 's20', 's31'):
    if sid in S: events.append({'type': 'stinger', 't': S[sid]['start'] - 0.05})
cuts = [seg['start'] for seg in tl[1:]]
for sid, word, nth, off in [('s04', 'there', 1, -0.1), ('s09', 'cats', 1, -0.05), ('s14', 'cat', 1, -0.1), ('s17', 'meow', 2, -0.2),
                            ('s22', 'let', 1, -0.3), ('s22', 'something', 1, -0.2), ('s23', 'bought', 1, -0.1)]:
    c = cue(sid, word, nth, off)
    if c is not None: cuts.append(c)
for e in events:
    if e['type'] in ('boom', 'meow2', 'error'): cuts.append(e['t'] - (0.15 if e['type'] == 'meow2' else 0))
cuts.sort()
json.dump({'total': t + 0.4, 'segments': tl, 'events': events, 'cuts': cuts}, open(out, 'w'), indent=1)
print('total', round(t, 2), 'segments', len(tl))
