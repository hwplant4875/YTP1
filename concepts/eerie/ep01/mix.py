# Mix narration, knocks, cut glitches, room tone and music into one track.
# python3 mix.py timeline.json voicedir sfxdir out.wav
import json, sys, subprocess
tl = json.load(open(sys.argv[1])); vdir, sdir, out = sys.argv[2], sys.argv[3], sys.argv[4]
T = tl['total']
ins, flt, labels = [], [], []
N = [0]
def nxt():
    N[0] += 1; return N[0] - 1
def add(path, t, vol, extra=''):
    i = nxt(); ins.extend(['-i', path])
    flt.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=stereo,volume={vol}{extra},adelay={int(t*1000)}|{int(t*1000)}[a{i}]'); labels.append(f'[a{i}]')
for s in tl['segments']: add(f"{vdir}/{s['file']}", s['start'], 1.0)
for e in tl['events']:
    if e['type'] == 'knock': add(f'{sdir}/knock1.mp3', e['t'], 0.9)
for s in tl['segments'][1:]: add(f'{sdir}/static.mp3', s['start'] - 0.02, 0.10, ',atrim=0:0.25,afade=t=out:st=0.15:d=0.1')
# beds: room tone and music looped across the whole video
i = nxt(); ins.extend(['-stream_loop', '-1', '-i', f'{sdir}/roomtone.mp3'])
flt.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.35,atrim=0:{T}[a{i}]'); labels.append(f'[a{i}]')
i = nxt(); ins.extend(['-stream_loop', '-1', '-i', f'{sdir}/music.mp3'])
flt.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.16,atrim=0:{T},afade=t=in:d=1.5,afade=t=out:st={T-2.5}:d=2.5[a{i}]'); labels.append(f'[a{i}]')
flt.append(''.join(labels) + f'amix=inputs={len(labels)}:normalize=0:dropout_transition=0,atrim=0:{T},alimiter=limit=0.9[out]')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', ';'.join(flt), '-map', '[out]', '-ar', '44100', out], check=True)
print('mixed', out, T)
