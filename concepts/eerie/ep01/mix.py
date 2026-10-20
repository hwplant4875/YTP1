# Mix narration, sound events, cut glitches, room tone and music into one track.
# python3 mix.py timeline.json voicedir sfxdir music.mp3 out.wav [music_volume]
import json, sys, subprocess
tl = json.load(open(sys.argv[1])); vdir, sdir, music, out = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
MV = float(sys.argv[6]) if len(sys.argv) > 6 else 0.35
T = tl['total']
SOUND = {'knock3': ('knock_triple.wav', 1.0), 'meow1': ('meow_deep_fx.wav', 0.9), 'meow2': ('meow_deep2_fx.wav', 0.9),
         'boom': ('boom.mp3', 0.55), 'error': ('error.mp3', 0.7), 'scratch': ('scratch.mp3', 0.8),
         'riser': ('riser.mp3', 0.45), 'stinger': ('stinger.mp3', 0.55), 'hum': ('hum.mp3', 0.35), 'heartbeat': ('heartbeat.mp3', 0.5),
         'breath': ('breath.mp3', 0.55), 'creak': ('creak.mp3', 0.6), 'staticlong': ('staticlong.mp3', 0.22), 'tapestop': ('tapestop.mp3', 0.5),
         'bark': ('bark.mp3', 0.8), 'hiss': ('hiss.mp3', 0.5), 'handle': ('handle.mp3', 0.7),
         'whoosh': ('whoosh.mp3', 0.45), 'chime': ('chime.mp3', 0.35)}
ins, flt, labels = [], [], []
N = [0]
def nxt():
    N[0] += 1; return N[0] - 1
def add(path, t, vol, extra=''):
    i = nxt(); ins.extend(['-i', path]); d = int(max(0, t) * 1000)
    flt.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=stereo,volume={vol}{extra},adelay={d}|{d}[a{i}]'); labels.append(f'[a{i}]')
for s in tl['segments']: add(f"{vdir}/{s['file']}", s['start'], 1.0, f",atrim=0:{s.get('cut', 99) + 0.12},afade=t=out:st={s.get('cut', 99)}:d=0.12")
for e in tl['events']:
    f, v = SOUND[e['type']]; add(f'{sdir}/{f}', e['t'], v)
# a short static/glitch crackle on every cut, rotating through three takes
for j, c in enumerate(tl.get('cuts', [])): add(f'{sdir}/glitch{j % 3 + 1}.mp3', c - 0.03, 0.28, ',atrim=0:0.35,afade=t=out:st=0.22:d=0.13')
# beds: room tone and music looped across the whole video
i = nxt(); ins.extend(['-stream_loop', '-1', '-i', f'{sdir}/roomtone.mp3'])
flt.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.25,atrim=0:{T}[a{i}]'); labels.append(f'[a{i}]')
i = nxt(); ins.extend(['-stream_loop', '-1', '-i', music])
flt.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=stereo,volume={MV},atrim=0:{T},afade=t=in:st=1.6:d=2,afade=t=out:st={T-3}:d=3[a{i}]'); labels.append(f'[a{i}]')
flt.append(''.join(labels) + f'amix=inputs={len(labels)}:normalize=0:dropout_transition=0,atrim=0:{T},alimiter=limit=0.9,loudnorm=I=-15:TP=-1.5:LRA=11[out]')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', ';'.join(flt), '-map', '[out]', '-ar', '44100', out], check=True)
print('mixed', out, T)
