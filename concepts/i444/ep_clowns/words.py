# Clowns episode: whisper word onsets for voice/s00..s12 -> voice/words.json ({seg: [[start, end, word], ...]}, as EP03 voice_v3)
import json, os, subprocess
import numpy as np
from faster_whisper import WhisperModel
D = os.path.dirname(os.path.abspath(__file__)) + '/voice/'
def pcm(p): return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', '16000', '-']), np.int16).astype(np.float32) / 32768
m = WhisperModel('small.en', device='cpu', compute_type='int8'); out = {}
for k in range(13):
    s = f's{k:02d}'; segs, _ = m.transcribe(pcm(D + s + '.mp3'), word_timestamps=True, language='en')
    out[s] = [[round(w.start, 2), round(w.end, 2), w.word.strip()] for g in segs for w in g.words]
    print(s, len(out[s]), flush=True)
json.dump(out, open(D + 'words.json', 'w'))
