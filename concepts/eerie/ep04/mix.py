# EP04: mix narration, sound events, cut glitches, room tone and music into one track.
# python3 mix.py timeline.json voicedir sfxdir music.mp3 out.wav [music_volume]
import json, sys, subprocess
tl = json.load(open(sys.argv[1])); vdir, sdir, music, out = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
MV = float(sys.argv[6]) if len(sys.argv) > 6 else 0.35
T = tl['total']
G = 0.4   # every sound effect sits 8 dB lower than before (user, v10)
# (file, volume); soft, low-passed takes only: no harsh booms, stingers or crackles
SOUND = {'tap': ('tap.mp3', 0.5), 'tapoff': ('tapoff.mp3', 0.6), 'fog': ('fog.mp3', 0.6), 'squeak': ('squeak.mp3', 0.8), 'glasstap': ('glasstap.mp3', 0.9),
         'ripple': ('ripple.mp3', 0.7), 'grab': ('grab.mp3', 0.9), 'crack': ('crack.mp3', 0.7), 'towel': ('towel.mp3', 0.8), 'thumps': ('thumps.mp3', 0.7),
         'drip': ('drip.mp3', 0.6), 'thud': ('thud.wav', 0.6), 'slam': ('thud.wav', 0.7), 'card': ('thud.wav', 0.45), 'stamp': ('hit.wav', 0.6),
         'riser': ('riser.mp3', 0.45), 'hum': ('hum.mp3', 0.35), 'heartbeat': ('heartbeat.mp3', 0.5), 'notif': ('notif.mp3', 0.9),
         'breath': ('breath.mp3', 0.55), 'creak': ('creak.mp3', 0.6), 'whoosh': ('whoosh.mp3', 0.45), 'chime': ('chime.mp3', 0.35), 'morph': ('staticlong.mp3', 0.3),
         'drag': ('drag.mp3', 0.8), 'binlid': ('binlid.mp3', 0.6), 'keylock': ('keylock.mp3', 0.7), 'sofa': ('sofa.mp3', 0.8), 'joint': ('joint.mp3', 0.8),
         'scrape': ('scrape.mp3', 0.7), 'poweroff': ('poweroff.mp3', 0.5), 'unplug': ('unplug.mp3', 0.7), 'servo': ('servo.mp3', 0.6)}
SOFT = ',lowpass=f=6500'
ins, flt, labels = [], [], []
N = [0]
def nxt():
    N[0] += 1; return N[0] - 1
def add(path, t, vol, extra=''):
    i = nxt(); ins.extend(['-i', path]); d = int(max(0, t) * 1000)
    flt.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=stereo,volume={vol}{extra},adelay={d}|{d}[a{i}]'); labels.append(f'[a{i}]')
for s in tl['segments']: add(f"{vdir}/{s['file']}", s['start'], 1.0, f",atrim=0:{s.get('cut', 99) + 0.12},afade=t=out:st={s.get('cut', 99)}:d=0.12")
for e in tl['events']:
    if e['type'] not in SOUND: continue   # visual-only events (blackout)
    f, v = SOUND[e['type']]
    trim = ''
    add(f'{sdir}/{f}', e['t'], v * G, SOFT + trim + (',lowpass=f=3500' if e['type'] == 'morph' else ''))
# a quiet, muffled tape flicker on each cut (two soft takes)
quiet = {s['start'] for s in tl['segments'] if s['id'] in ('o2',)}   # the file opening stays silent (user)
for j, c in enumerate(c for c in tl.get('cuts', []) if c not in quiet): add(f'{sdir}/gsoft{j % 2 + 1}.wav', c - 0.03, 0.3 * G, ',atrim=0:0.4,afade=t=out:st=0.25:d=0.15')
# beds: room tone and music looped across the whole video
i = nxt(); ins.extend(['-stream_loop', '-1', '-i', f'{sdir}/roomtone.mp3'])
flt.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.25,atrim=0:{T}[a{i}]'); labels.append(f'[a{i}]')
i = nxt(); ins.extend(['-stream_loop', '-1', '-i', music])
flt.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=stereo,volume={MV},atrim=0:{T},afade=t=in:st=1.6:d=2,afade=t=out:st={T-1.2}:d=1.2[a{i}]'); labels.append(f'[a{i}]')
flt.append(''.join(labels) + f'amix=inputs={len(labels)}:normalize=0:dropout_transition=0,atrim=0:{T},alimiter=limit=0.9,loudnorm=I=-15:TP=-1.5:LRA=11[out]')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', ';'.join(flt), '-map', '[out]', '-ar', '44100', out], check=True)
print('mixed', out, T)
