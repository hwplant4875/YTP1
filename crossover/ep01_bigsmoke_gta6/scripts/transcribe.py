import sys, json, os, subprocess
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel(os.environ.get('WM','small.en'), device='cpu', compute_type='int8', cpu_threads=4)
for p in sys.argv[1:]:
    out = os.path.splitext(p)[0] + '.words.json'
    if os.path.exists(out): print('skip', p); continue
    raw = subprocess.run(['ffmpeg','-loglevel','error','-i',p,'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True,check=True).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32)/32768.0
    segs, info = m.transcribe(audio, word_timestamps=True, vad_filter=False, beam_size=5)
    data = []
    for s in segs:
        data.append({'start': round(s.start,2), 'end': round(s.end,2), 'text': s.text.strip(), 'words': [{'w': w.word, 's': round(w.start,2), 'e': round(w.end,2)} for w in (s.words or [])]})
    json.dump(data, open(out,'w'), indent=0)
    with open(os.path.splitext(p)[0] + '.txt','w') as f:
        for d in data: f.write(f"[{d['start']:7.2f}-{d['end']:7.2f}] {d['text']}\n")
    print('done', p, len(data))
