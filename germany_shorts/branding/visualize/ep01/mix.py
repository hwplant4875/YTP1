import subprocess
S=[('beep',0.15,.5),('beep',26.4,.5),('tv',5.0,.35),('scroll',14.0,.35),('fridge',20.0,.45),('alarm',33.0,.45),('door',40.0,.45),
   ('runheavy',46.0,.55),('rain',93.33,.5),('rundawn',104.5,.45),('beep',122.3,.5),('birds',130.0,.35)]
inp=['-i','music_v1.mp3']; f=[]
for i,(n,t,v) in enumerate(S,1):
    inp+=['-i',f'sfx_{n}.mp3']
    f.append(f'[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,afade=t=in:d=0.15,areverse,afade=t=in:d=0.6,areverse,volume={v},adelay={int(t*1000)}|{int(t*1000)}[s{i}]')
f.append('[0:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=1.0[m]')
f.append('[m]'+''.join(f'[s{i}]' for i in range(1,len(S)+1))+f'amix=inputs={len(S)+1}:normalize=0:duration=longest,atrim=0:144,afade=t=out:st=141.5:d=2.5,loudnorm=I=-14:TP=-1.5:LRA=11[out]')
subprocess.run(['ffmpeg','-y','-v','error',*inp,'-filter_complex',';'.join(f),'-map','[out]','-ar','48000','-c:a','pcm_s16le','mix.wav'],check=True)
print('ok')
