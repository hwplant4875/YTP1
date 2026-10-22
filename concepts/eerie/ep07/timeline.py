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
    'a4': (0.6, []),             # the grip meter runs past the top
    'a5': (0.5, []),
    'b3': (0.6, []),             # underlined twice
    'b4': (0.9, [('heartbeat', 0.0)]),
    'b7': (0.9, [('heartbeat', 0.0)]),
    'c3': (0.4, []),
    'c6': (0.6, []),
    'c8': (0.3, []),
    'c9': (0.3, []),
    'd2': (0.3, []),
    'd3': (0.5, []),
    'd7': (0.6, []),
    'd13': (0.4, []),
    'd14': (0.5, []),
    'd15': (1.0, []),            # they walk out one by one
    'f3': (0.8, [('heartbeat', 0.1)]),
    'f4': (0.6, []),
    'f6': (0.0, [('stamp', 0.2)]),       # the sign-off stamp
}
RISE = ('o2', 'a8', 'b9', 'c9', 'd9', 'f2')   # a riser that ends exactly on the next shot

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
                                 ('a1', 'hand', 1, 'standup', -0.6), ('a1', 'fingers', 1, 'heartbeat', 0.0), ('a3', 'challenge', 1, 'heartbeat', 0.0),
                                 ('a4', 'squeezes', 1, 'squeeze', -0.1), ('a4', 'harder', 2, 'squeeze', 0.0), ('a4', 'stop', 2, 'heartbeat', 0.0), ('a5', 'heard', 1, 'crack', -0.15),
                                 ('a6', 'signs', 1, 'pen', 0.2), ('a8', 'writes', 1, 'pen', 0.0),
                                 ('b1', 'map', 2, 'heartbeat', 0.0), ('b3', 'wrote', 1, 'pen', -0.1), ('b3', 'underlined', 1, 'underline', -0.05), ('b3', 'twice', 1, 'underline', -0.05),
                                 ('b4', 'notice', 1, 'mailpile', 0.0), ('b5', 'leans', 1, 'chair', -0.1), ('b5', 'glasses', 1, 'heartbeat', 0.0), ('b7', 'power', 1, 'poweroff', -0.1),
                                 ('c1', 'pens', 1, 'pens', -0.15), ('c2', 'ends', 1, 'keylock', 0.0), ('c3', 'clock', 1, 'tick', 0.0), ('c3', 'nine', 1, 'heartbeat', 0.0),
                                 ('c4', 'stands', 1, 'standup', -0.2), ('c5', 'until', 1, 'heartbeat', 0.0), ('c6', 'monday', 1, 'tick', 0.0), ('c9', 'stand', 1, 'standup', -0.1),
                                 ('d2', 'interviewers', 1, 'heartbeat', 0.0), ('d2', 'foot', 1, 'heartbeat', 0.0), ('d5', 'lacks', 1, 'pen', 0.0), ('d6', 'strong', 1, 'pen', 0.0),
                                 ('d7', 'visit', 1, 'heartbeat', 0.0), ('d10', 'sit', 1, 'situp', -0.2), ('d10', 'congratulations', 1, 'heartbeat', 0.0), ('d12', 'drop', 1, 'drop', -0.1),
                                 ('d14', 'appear', 1, 'boxes', -0.1), ('d15', 'walk', 1, 'steps', 0.0), ('f1', 'email', 1, 'notif', 0.0), ('f3', 'doorbell', 1, 'doorbell', 0.0),
                                 ('f3', 'hand', 1, 'heartbeat', 0.0), ('f5', 'four', 1, 'stamp', 0.0)]:
    c = cue(sid, word, nth, off)
    if c is not None: events.append({'type': snd, 't': c})
if 'c8' in S: events.append({'type': 'keylock', 't': S['c8']['end'] - 0.6})   # the lock opens
for sid in ('a0', 'b0', 'c0', 'd0'):   # rule cards land on a soft low thud
    if sid in S: events.append({'type': 'card', 't': S[sid]['start'] - 0.05})
for i, seg in enumerate(tl[:-1]):
    if seg['id'] in RISE: events.append({'type': 'riser', 't': tl[i + 1]['start'] - 2.04})
cuts = [seg['start'] for seg in tl[1:]]
# the hook teaser: three "do not"s, each done anyway; contact or red, then black before the next line
if 'h2' in S and 'o1' in S:
    b, c, e = cue('h2', 'do', 2), cue('h2', 'and', 1), S['o1']['start']
    for w1 in (b, c, e): events.append({'type': 'thud', 't': w1 - 0.6})
    cuts += [b, c]
for e in events:
    if e['type'] in ('thud', 'slam'): cuts.append(e['t'])
cuts.sort()
# the video ends on the sign-off: stamp, the picture dims to half, a held beat
total = tl[-1]['end'] + 2.6
json.dump({'total': total, 'segments': tl, 'events': events, 'cuts': cuts}, open(out, 'w'), indent=1)
print('total', round(t, 2), 'segments', len(tl))
