# EP02. Build timeline.json (segment start times, word timings, sound events) from the narration files.
# python3 timeline.py voicedir out.json [last_segment_id]
import json, os, sys, subprocess
import numpy as np
vdir, out = sys.argv[1], sys.argv[2]
last = sys.argv[3] if len(sys.argv) > 3 else None
segs = json.load(open(os.path.join(os.path.dirname(__file__), 'segments.json')))
GAP = 0.7     # silence between lines (user: about 0.7 s, never over 1.5 s)
GAPS = {'d10': 0.45}   # "Then it will reach the corner" runs on into "It has never had to describe itself"
LEAD = 0.35   # the video opens on the phone with the photo already there; the first line starts at once
# extra time after a line, only where a sound or an action fills it: (seconds, [(sound, offset after speech end)])
EXTRA = {
    'o2': (0.3, []),
    'a5': (0.5, [('notif', 0.05)]),
    # you reply: typing, send, its answer, the flash from the corner, and the screen dies
    'a7': (2.45, [('typing', 0.0), ('send', 0.95), ('notif', 1.4), ('flash', 1.85), ('shutter', 2.0), ('blackout', 2.12)]),
    'c5': (0.4, []),
    'd1': (0.3, []),
    'd11': (0.6, []),
    'e3': (2.2, [('buzz', 0.5), ('notif', 1.35)]),
    'e4': (0.0, [('stamp', 0.2)]),   # the sign-off stamp
}
RISE = ('o2', 'c5')   # a riser that ends exactly on the next shot

def speech_bounds(mp3):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp3, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    e = np.array([np.sqrt((a[j:j + 160] ** 2).mean()) for j in range(0, len(a) - 160, 160)])
    on = np.where(20 * np.log10(e + 1e-6) > -40)[0]
    return on[0] * 0.01, (on[-1] + 1) * 0.01

t = LEAD; tl = []; events = [{'type': 'notif', 't': 0.0}]
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
for sid, word, nth, snd, off in [('o1', 'four', 1, 'stamp', 0.0), ('o2', 'exactly', 1, 'stamp', 0.0), ('o2', 'emergency', 1, 'heartbeat', 0.0),
                                 ('a1', 'lights', 1, 'buzz', 0.0), ('a2', 'are', 1, 'notif', -0.15),
                                 ('a6', 'taken', 1, 'shutter', 0.0), ('b3', 'holding', 1, 'creak', 0.0), ('b4', 'breath', 1, 'breath', -0.1),
                                 ('c2', 'closer', 1, 'shutter', 0.0), ('c5', 'eye', 1, 'heartbeat', 0.0), ('d1', 'awake', 1, 'thud', 0.0),
                                 ('d3', 'off', 1, 'poweroff', 0.0), ('d3', 'back', 1, 'poweron', 0.0), ('d4', 'throw', 1, 'whoosh', 0.0), ('d4', 'morning', 1, 'chime', 0.0),
                                 ('d6', 'apologize', 1, 'notif', 0.0), ('d8', 'describe', 1, 'send', 0.6), ('d10', 'corner', 1, 'heartbeat', 0.0),
                                 ('d12', 'dark', 1, 'morph', -0.1), ('e1', 'message', 1, 'notif', 0.0)]:
    c = cue(sid, word, nth, off)
    if c is not None: events.append({'type': snd, 't': c})
for sid in ('a0', 'b0', 'c0', 'd0'):   # rule cards land on a soft low thud
    if sid in S: events.append({'type': 'card', 't': S[sid]['start'] - 0.05})
for i, seg in enumerate(tl[:-1]):
    if seg['id'] in RISE: events.append({'type': 'riser', 't': tl[i + 1]['start'] - 2.04})
cuts = [seg['start'] for seg in tl[1:]]
for sid, word, nth, off in [('a6', 'taken', 1, -0.05), ('b4', 'something', 1, -0.05), ('c2', 'closer', 1, -0.05)]:
    c = cue(sid, word, nth, off)
    if c is not None: cuts.append(c)
for e in events:
    if e['type'] in ('thud', 'morph'): cuts.append(e['t'])
cuts.sort()
# the video ends on the sign-off: stamp, the picture dims to half, a held beat
total = tl[-1]['end'] + 2.6
json.dump({'total': total, 'segments': tl, 'events': events, 'cuts': cuts}, open(out, 'w'), indent=1)
print('total', round(t, 2), 'segments', len(tl))
