"""usage: tseg.py WAV start end [prompt]  -> word timings (absolute) from a stem segment"""
import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
p,a,b=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]); pr=sys.argv[4] if len(sys.argv)>4 else None
m=WhisperModel('small.en',device='cpu',compute_type='int8',cpu_threads=4)
raw=subprocess.run(['ffmpeg','-loglevel','error','-ss',str(a),'-t',str(b-a),'-i',p,'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True,check=True).stdout
au=np.frombuffer(raw,np.int16).astype(np.float32)/32768.0
segs,_=m.transcribe(au,word_timestamps=True,vad_filter=False,beam_size=5,initial_prompt=pr)
for s in segs:
    print(' '.join(f"{w.word.strip()}[{w.start+a:.2f}-{w.end+a:.2f}]" for w in s.words))
# energy envelope 50ms
x=au.reshape(-1,800)[:len(au)//800] if len(au)%800==0 else au[:len(au)//800*800].reshape(-1,800)
e=20*np.log10(np.sqrt((x**2).mean(1))+1e-6)
print('env(dB, 50ms from',a,'):',' '.join(f"{v:.0f}" for v in e))
