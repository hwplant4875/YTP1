# EP03. Build timeline.json (segment start times, word timings, sound events) from the narration files.
# python3 timeline.py voicedir out.json [last_segment_id]
import json, os, sys, subprocess
import numpy as np
vdir, out = sys.argv[1], sys.argv[2]
last = sys.argv[3] if len(sys.argv) > 3 else None
segs = json.load(open(os.path.join(os.path.dirname(__file__), 'segments.json')))
GAP = 0.7     # silence between lines (user: about 0.7 s, never over 1.5 s)
GAPS = {}
LEAD = 0.35   # frame 0 is the hook image; the first line starts at once
# extra time after a line, only where a sound or an action fills it: (seconds, [(sound, offset after speech end)])
EXTRA = {
    'o2': (0.3, []),
    'a5': (0.3, []),
    # what would happen: it freezes, a grey hand covers it, it is dragged into the dark, the thing hits the glass, black
    'a7': (2.5, [('heartbeat', 0.05), ('grab', 0.75), ('whoosh', 1.15), ('slam', 1.85), ('glasstap', 1.85), ('blackout', 2.2)]),
    'c4': (0.4, []),
    'd1': (0.3, []),
    'd11': (0.9, []),
    'e3': (0.9, []),
    'e4': (2.4, [('heartbeat', 0.2)]),   # its back, held
    'e6': (0.0, [('stamp', 0.2)]),       # the sign-off stamp
}
RISE = ('o2', 'c5')   # a riser that ends exactly on the next shot

def speech_bounds(mp3):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp3, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    e = np.array([np.sqrt((a[j:j + 160] ** 2).mean()) for j in range(0, len(a) - 160, 160)])
    on = np.where(20 * np.log10(e + 1e-6) > -40)[0]
    return on[0] * 0.01, (on[-1] + 1) * 0.01

t = LEAD; tl = []; events = []
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
    t = speech_end + GAPS.get(s['id'], GAP) + extra
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
for sid, word, nth, snd, off in [('h1', 'run', 1, 'heartbeat', 0.0), ('o1', 'four', 1, 'stamp', 0.0), ('o2', 'exactly', 1, 'stamp', 0.0), ('o2', 'emergency', 1, 'heartbeat', 0.0),
                                 ('a1', 'washing', 1, 'tap', -0.6), ('a1', 'sink', 1, 'tap', -0.4), ('a2', 'up', 1, 'tapoff', 0.0), ('a5', 'three', 1, 'heartbeat', 0.0),
                                 ('a6', 'holding', 1, 'breath', -0.2), ('b2', 'open', 1, 'creak', -1.2), ('b3', 'tall', 1, 'hum', 0.0), ('b5', 'alone', 1, 'heartbeat', 0.0),
                                 ('c1', 'fog', 1, 'fog', -0.2), ('c1', 'water', 1, 'tap', -0.3), ('c2', 'line', 1, 'squeak', 0.0),
                                 ('c4', 'r', 1, 'squeak', -0.1), ('c4', 'u', 1, 'squeak', -0.05), ('c4', 'n', 1, 'squeak', -0.05), ('c5', 'empty', 1, 'heartbeat', 0.0),
                                 ('c6', 'run', 1, 'whoosh', 0.1), ('d1', 'hand', 1, 'ripple', 0.0), ('d1', 'wrist', 1, 'grab', 0.0), ('d3', 'pull', 1, 'breath', 0.0),
                                 ('d4', 'break', 1, 'crack', 0.05), ('d7', 'flat', 1, 'glasstap', 0.0), ('d8', 'palm', 1, 'glasstap', 0.0), ('d9', 'turn', 1, 'whoosh', 0.0),
                                 ('d9', 'off', 1, 'ripple', -0.1), ('d11', 'towel', 1, 'towel', -0.3), ('d11', 'hear', 1, 'thumps', 0.0), ('e1', 'down', 1, 'towel', -0.2),
                                 ('e2', 'wash', 1, 'tap', -0.3), ('e5', 'four', 1, 'stamp', 0.0)]:
    c = cue(sid, word, nth, off)
    if c is not None: events.append({'type': snd, 't': c})
for sid in ('a0', 'b0', 'c0', 'd0'):   # rule cards land on a soft low thud
    if sid in S: events.append({'type': 'card', 't': S[sid]['start'] - 0.05})
for i, seg in enumerate(tl[:-1]):
    if seg['id'] in RISE: events.append({'type': 'riser', 't': tl[i + 1]['start'] - 2.04})
cuts = [seg['start'] for seg in tl[1:]]
# the hook teaser: three "do not"s, each done anyway; contact or red, then black before the next line
if 'h2' in S and 'o1' in S:
    b, c, e = cue('h2', 'do', 2), cue('h2', 'do', 3), S['o1']['start']
    for w1 in (b, c, e): events.append({'type': 'thud', 't': w1 - 0.6})
    events.append({'type': 'glasstap', 't': b - 0.6})
    cuts += [b, c]
for e in events:
    if e['type'] in ('thud', 'slam'): cuts.append(e['t'])
cuts.sort()
# the video ends on the sign-off: stamp, the picture dims to half, a held beat
total = tl[-1]['end'] + 2.6
json.dump({'total': total, 'segments': tl, 'events': events, 'cuts': cuts}, open(out, 'w'), indent=1)
print('total', round(t, 2), 'segments', len(tl))
