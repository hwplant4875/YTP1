# User 10/26 14:31: Roman's survival rate 15% -> 10%. Re-voices only the last sentence of voice_v3/s17 ("Survival rate: ten percent.")
# and splices it in at the pause before "Survival", so every cut anchored earlier in s17 stays where it is.
# Keeps the original as voice_v3/parts/s17_orig.mp3/.json; updates voice_v3/s17.json (alignment) and voice_v3/words.json (s17 tail).
import json, os, base64, subprocess, urllib.request, shutil
import numpy as np
K = os.environ['ELEVENLABS_JC_API_KEY']; V = 'voice_v3/'; P = V + 'parts/'; os.makedirs(P, exist_ok=True)
NEW = 'Survival rate: ten percent.'
if not os.path.exists(P + 's17_orig.mp3'):
    shutil.copy(V + 's17.mp3', P + 's17_orig.mp3'); shutil.copy(V + 's17.json', P + 's17_orig.json')
base = json.load(open(P + 's17_orig.json')); txt = ''.join(base['characters']); ci = txt.index('Survival')
def pcm(src): return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', src, '-f', 's16le', '-ac', '1', '-ar', '44100', '-']), np.int16)
def env(x, sr=44100):
    w = sr // 100; f = x[:len(x) // w * w].astype(np.float32).reshape(-1, w) / 32768
    return 20 * np.log10(np.sqrt(np.mean(f ** 2, 1)) + 1e-9)
x = pcm(P + 's17_orig.mp3'); e = env(x)
# the quietest 10 ms window in the pause before "Survival" (alignment says it starts ~24.96 s; search 24.2..25.1 s)
lo, hi = 2420, 2510; cut = (lo + int(np.argmin(e[lo:hi]))) * 441
quiet = np.nonzero(e[lo:hi] < -54)[0]
if len(quiet): cut = (lo + int(quiet[0])) * 441 + 441 * 3          # just after the previous word has died away
pf = P + 's17_tail10.mp3'
if not os.path.exists(pf):
    body = {'text': NEW, 'model_id': 'eleven_v4', 'previous_text': txt[:ci].strip()}
    r = urllib.request.Request('https://api.elevenlabs.io/v1/text-to-speech/s3TPKV1kjDlVtZbl4Ksh/with-timestamps', data=json.dumps(body).encode(),
                               headers={'xi-api-key': K, 'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(r, timeout=300))
    open(pf, 'wb').write(base64.b64decode(d['audio_base64'])); json.dump(d['alignment'], open(P + 's17_tail10.json', 'w'))
xt = pcm(pf); et = env(xt); sp = np.nonzero(et > -42)[0]
t0 = max(0, sp[0] * 441 - 441); t1 = min(len(xt), (sp[-1] + 1) * 441 + 3528)
xt = xt[t0:t1].astype(np.float32); xt[-1764:] *= np.linspace(1, 0, 1764)
GAP = 0.30                                                           # pause before "Survival", like the original read
head = x[:cut].astype(np.float32); head[-441:] *= np.linspace(1, 0, 441)
y = np.concatenate([head, np.zeros(int(GAP * 44100), np.float32), xt]).astype(np.int16)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', '44100', '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '192k', V + 's17.mp3'],
               input=y.tobytes(), check=True)
off = cut / 44100 + GAP; sh = off - t0 / 44100; tal = json.load(open(P + 's17_tail10.json'))
al = {'characters': base['characters'][:ci] + tal['characters'],
      'character_start_times_seconds': base['character_start_times_seconds'][:ci] + [max(off, v + sh) for v in tal['character_start_times_seconds']],
      'character_end_times_seconds': base['character_end_times_seconds'][:ci] + [min(len(y) / 44100, max(off, v + sh)) for v in tal['character_end_times_seconds']]}
json.dump(al, open(V + 's17.json', 'w'))
print('cut at', round(cut / 44100, 3), 'new sentence at', round(off, 3), 'total', round(len(y) / 44100, 3))
