# Builds out/audio.wav: narration + soft stomps + rewind + quiet BGM (stereo kept).
import re, subprocess, sys
src = open('src/timeline.ts').read()
def arr(name):
    m = re.search(name + r'[^=]*=\s*\[([^\]]*)\]', src)
    return [int(x) for x in re.findall(r'\d+', re.sub(r'//[^\n]*', '', m.group(1)))]
FPS = 30
DUR = int(re.search(r'DURATION = (\d+)', src).group(1)) / FPS
vo, steps = arr('VO_STARTS'), arr('STEP_FRAMES')
rew = int(re.search(r'REWIND_START = (\d+)', src).group(1))
ins, flt, tags = [], [], []
def add(path, t, vol, extra=''):
    i = len(ins) // 2; ins.extend(['-i', path])
    ms = int(t / FPS * 1000)
    flt.append(f'[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,{extra}volume={vol},adelay={ms}|{ms}[a{i}]')
    tags.append(f'[a{i}]')
for i, t in enumerate(vo): add(f'public/vo/l{i:02d}.mp3', t, 1.0)
for k, s in enumerate(steps):
    v = 0.30 if k < 16 else 0.16   # rapid late steps quieter
    add('public/stomp.wav', s + 6, v, 'atrim=0:1.2,afade=t=out:st=0.8:d=0.4,')
add('public/rewind.mp3', rew - 2, 0.6, 'atrim=0:1.0,afade=t=out:st=0.7:d=0.3,')
i = len(ins) // 2; ins.extend(['-i', 'public/bgm.mp3'])
flt.append(f'[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{DUR},highshelf=f=3000:g=-4,volume=0.32,afade=t=out:st={DUR-1.5}:d=1.5[bgm]')
tags.append('[bgm]')
flt.append(''.join(tags) + f'amix=inputs={len(tags)}:normalize=0,atrim=0:{DUR},loudnorm=I=-14:TP=-1.5[out]')
subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', *ins, '-filter_complex', ';'.join(flt), '-map', '[out]', '-ar', '48000', 'out/audio.wav'], check=True)
print('ok', DUR)
