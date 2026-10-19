import subprocess
inp=[]; f=[]; n=0
def add(file, at, vol, ss=None, to=None, fin=0.05, fout=0.3):
    global n
    a=[]; 
    if ss is not None: a+=['-ss',str(ss)]
    if to is not None: a+=['-t',str(to-(ss or 0))]
    inp.extend(a+['-i',file]); i=n; n+=1
    dur=None
    chain=f'[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,afade=t=in:d={fin},areverse,afade=t=in:d={fout},areverse,volume={vol},adelay={int(at*1000)}|{int(at*1000)}[a{i}]'
    f.append(chain)
add('vo.mp3',0.05,1.0,fin=0.01,fout=0.3)
add('music.mp3',0,0.32,0,21.25,fin=0.01,fout=0.2)
add('music.mp3',21.0,0.38,24,34.5,fin=0.05,fout=1.2)
add('music.mp3',33.0,0.30,15,21,fin=0.8,fout=1.5)
add('sfx_bubble.mp3',3.3,0.3); add('sfx_bubble.mp3',9.0,0.3)
add('sfx_fizz.mp3',11.2,0.35)
add('sfx_rumble.mp3',15.5,0.6,fin=1.0,fout=1.5)
add('sfx_boom.mp3',21.0,0.9,fin=0.01,fout=1.0)
add('sfx_hiss.mp3',24.6,0.35)
for t in (7.0,15.0,16.0,25.0): add('sfx_pop.mp3',t,0.25,fin=0.01,fout=0.1)
f.append(''.join(f'[a{i}]' for i in range(n))+f'amix=inputs={n}:normalize=0:duration=longest,atrim=0:38.5,afade=t=out:st=37.3:d=1.2,loudnorm=I=-14:TP=-1.5:LRA=11[out]')
subprocess.run(['ffmpeg','-y','-v','error',*inp,'-filter_complex',';'.join(f),'-map','[out]','-ar','48000','mix.wav'],check=True); print('ok')
