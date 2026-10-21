# EP07 (Greatest Weakness). Build timeline.json (segment start times, word timings, sound events) from the narration files.
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
    'a2': (0.2, []),
    # what happens if you break the rule: the line under LIVES ALONE turns red, then black
    'a6': (1.4, [('heartbeat', 0.1), ('blackout', 1.0)]),
    'b2': (0.4, []),
    'b5': (0.3, []),
    'b7': (1.4, [('heartbeat', 0.0), ('blackout', 1.0)]),
    'c3': (0.3, []),
    'c5': (1.4, [('heartbeat', 0.0), ('blackout', 1.0)]),
    'd2': (0.3, []),
    'd3': (0.5, []),
    'd7': (1.3, [('heartbeat', 0.0), ('blackout', 0.9)]),
    'd13': (0.4, []),
    'd14': (0.7, []),
    'f3': (1.0, [('heartbeat', 0.1)]),
    'f5': (0.0, [('stamp', 0.2)]),       # the sign-off stamp
}
RISE = ('o2', 'b6', 'c4', 'd8', 'd12')   # a riser that ends exactly on the next shot

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
for sid, word, nth, snd, off in [('h1', 'weakness', 1, 'heartbeat', 0.0), ('o1', 'four', 1, 'stamp', 0.0), ('o2', 'exactly', 1, 'stamp', 0.0), ('o2', 'emergency', 1, 'heartbeat', 0.0),
                                 ('a1', 'three', 1, 'pen', 0.0), ('a5', 'wrote', 1, 'pen', -0.1), ('a6', 'underlined', 1, 'underline', -0.05),
                                 ('b1', 'leans', 1, 'chair', -0.1), ('b1', 'weakness', 1, 'heartbeat', 0.0), ('b2', 'conditioner', 1, 'acoff', -0.3), ('b2', 'clock', 1, 'tick', 0.0),
                                 ('b5', 'forever', 1, 'heartbeat', 0.0), ('b5', 'file', 1, 'stamp', 0.0), ('b7', 'nine', 1, 'heartbeat', 0.0),
                                 ('c1', 'pens', 1, 'pens', -0.15), ('c3', 'nine', 1, 'tick', -0.1), ('c4', 'tilts', 1, 'heartbeat', 0.0), ('c5', 'monday', 1, 'heartbeat', 0.0),
                                 ('d1', 'stand', 1, 'standup', -0.2), ('d2', 'three', 2, 'heartbeat', 0.0), ('d2', 'foot', 1, 'heartbeat', 0.0), ('d5', 'write', 1, 'pen', 0.0),
                                 ('d6', 'visit', 1, 'heartbeat', 0.0), ('d7', 'email', 2, 'notif', 0.0), ('d7', 'inside', 1, 'heartbeat', 0.0), ('d9', 'sit', 1, 'situp', -0.2),
                                 ('d9', 'weakness', 1, 'heartbeat', 0.0), ('d11', 'smaller', 1, 'cloth', -0.1), ('d12', 'shake', 1, 'chair', 0.0), ('d12', 'smaller', 1, 'cloth', -0.1),
                                 ('d13', 'hire', 1, 'heartbeat', 0.0), ('d14', 'fold', 1, 'paper', -0.1), ('f1', 'email', 1, 'notif', 0.0), ('f3', 'chair', 1, 'heartbeat', 0.0),
                                 ('f4', 'four', 1, 'stamp', 0.0)]:
    c = cue(sid, word, nth, off)
    if c is not None: events.append({'type': snd, 't': c})
for sid in ('a0', 'b0', 'c0', 'd0'):   # rule cards land on a soft low thud
    if sid in S: events.append({'type': 'card', 't': S[sid]['start'] - 0.05})
for i, seg in enumerate(tl[:-1]):
    if seg['id'] in RISE: events.append({'type': 'riser', 't': tl[i + 1]['start'] - 2.04})
cuts = [seg['start'] for seg in tl[1:]]
# the hook teaser: three "do not"s, each done anyway; contact or red, then black before the next line
if 'h2' in S and 'o1' in S:
    b, c, e = cue('h2', 'never', 1), cue('h2', 'and', 1), S['o1']['start']
    for w1 in (b, c, e): events.append({'type': 'thud', 't': w1 - 0.6})
    cuts += [b, c]
for e in events:
    if e['type'] in ('thud', 'slam'): cuts.append(e['t'])
cuts.sort()
# the video ends on the sign-off: stamp, the picture dims to half, a held beat
total = tl[-1]['end'] + 2.6
json.dump({'total': total, 'segments': tl, 'events': events, 'cuts': cuts}, open(out, 'w'), indent=1)
print('total', round(t, 2), 'segments', len(tl))
