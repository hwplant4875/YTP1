# Build timeline.json (segment start times, word timings, sound events) from the narration files.
# python3 timeline.py voicedir out.json [last_segment_id]
import json, os, sys, subprocess
vdir, out = sys.argv[1], sys.argv[2]
last = sys.argv[3] if len(sys.argv) > 3 else None
segs = json.load(open(os.path.join(os.path.dirname(__file__), 'segments.json')))
GAP = 0.55
# extra silence after a segment (seconds), and sound events placed in that silence
EXTRA = {'s01': 0.4, 's02': 0.3, 's03': 0.2, 's04': 0.8, 's08': 0.3, 's09': 1.2, 's14': 1.0, 's17': 1.6, 's18': 1.4,
         's24': 1.0, 's26': 0.6, 's27': 2.2, 's28': 2.4, 's29': 0.6, 's35': 1.4, 's37': 3.2, 's38': 0.8, 's41': 0.8, 's43': 1.0, 's44': 0.8}
KNOCK_AFTER = {'s02': 3, 's26': 1, 's37': 3}   # knocks (count) heard in the pause after these lines
LEAD = 0.5
t = LEAD; tl = []; events = []
for s in segs:
    mp3 = os.path.join(vdir, s['id'] + '.mp3')
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp3]))
    al = json.load(open(os.path.join(vdir, s['id'] + '.json')))
    words = []; cur = None
    for ch, cs, ce in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
        if ch.isspace():
            if cur: words.append(cur); cur = None
            continue
        if cur is None: cur = {'w': '', 's': t + cs, 'e': t + ce}
        cur['w'] += ch; cur['e'] = t + ce
    if cur: words.append(cur)
    speech_end = words[-1]['e'] if words else t + dur
    tl.append({'id': s['id'], 'text': s['text'], 'start': t, 'end': speech_end, 'file': s['id'] + '.mp3', 'words': words})
    nxt = max(t + dur, speech_end) + GAP + EXTRA.get(s['id'], 0)
    if s['id'] in KNOCK_AFTER:
        k = KNOCK_AFTER[s['id']]; kt = speech_end + 0.7
        for j in range(k): events.append({'type': 'knock', 't': kt + j * 0.75})
        nxt = max(nxt, kt + k * 0.75 + 0.9)
    t = nxt
    if s['id'] == last: break
json.dump({'total': t + 0.6, 'segments': tl, 'events': events}, open(out, 'w'), indent=1)
print('total', round(t, 2), 'segments', len(tl))
