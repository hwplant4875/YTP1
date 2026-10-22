import runpy,sys,numpy as np
sys.argv=['x','/tmp/claude-0/music/_tmp.wav']
g=runpy.run_path('/tmp/claude-0/music/song2.py')
s=g['s']; SR=44100
import librosa
for k,a in s.parts.items():
    y=a.mean(1); 
    S=np.abs(librosa.stft(y[:SR*60],n_fft=4096)); fr=librosa.fft_frequencies(sr=SR,n_fft=4096)
    tot=(S**2).sum()
    bands=[(S[(fr>=lo)&(fr<hi)]**2).sum()/tot*100 for lo,hi in [(20,150),(150,400),(400,1500),(1500,20000)]]
    print(f'{k:8s} rms {20*np.log10(np.sqrt((a**2).mean())+1e-9):6.1f} dB  bands', ' '.join(f'{x:4.0f}' for x in bands))
