import librosa,numpy as np,sys
NOTES='C C# D D# E F F# G G# A A# B'.split()
maj=np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88]);mn=np.array([6.33,2.68,3.52,5.38,2.6,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
for f in sys.argv[1:]:
    y,sr=librosa.load(f,sr=22050,mono=True)
    print('\n#',f.split('/')[-1],round(len(y)/sr,1),'s')
    tempo,beats=librosa.beat.beat_track(y=y,sr=sr); print('tempo',tempo)
    ch=librosa.feature.chroma_cqt(y=y,sr=sr).mean(1)
    best=max(((np.corrcoef(np.roll(p,i),ch)[0,1],NOTES[i]+(' maj' if p is maj else ' min')) for p in (maj,mn) for i in range(12)))
    print('key',best)
    S=np.abs(librosa.stft(y)); fr=librosa.fft_frequencies(sr=sr)
    tot=S.sum()
    for lo,hi in [(20,60),(60,150),(150,400),(400,1500),(1500,4000),(4000,11000)]:
        print(f'  band {lo}-{hi}Hz {S[(fr>=lo)&(fr<hi)].sum()/tot*100:.1f}%')
    rms=librosa.feature.rms(y=y)[0]; t=librosa.frames_to_time(np.arange(len(rms)),sr=sr)
    seg=[round(float(20*np.log10(rms[(t>=s)&(t<s+8)].mean()+1e-9)),1) for s in range(0,int(t[-1]),8)]
    print('  rms per 8s',seg)
    # chord-ish: chroma per 2s, top 3 notes
    C=librosa.feature.chroma_cqt(y=y,sr=sr,hop_length=512); ft=librosa.frames_to_time(np.arange(C.shape[1]),sr=sr,hop_length=512)
    out=[]
    for s in np.arange(30,62,2):
        m=C[:,(ft>=s)&(ft<s+2)].mean(1); out.append('/'.join(NOTES[i] for i in np.argsort(m)[-3:][::-1]))
    print('  chroma 30-62s per 2s:',' '.join(out))
    on=librosa.onset.onset_strength(y=y,sr=sr); print('  onset density',round(float(on.mean()),2))
