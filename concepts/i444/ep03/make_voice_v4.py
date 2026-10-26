# EP03 narration v4 = voice_v3 + one tier line at the end of every ranked entry (user 10/26: "...so I'm putting X into the
# Don't Worry tier", worded differently each time). The tier line is voiced on its own (previous_text = the entry, so the
# delivery follows on) and appended after a short gap; s00/s01/s18 are copied unchanged.
# Writes voice_v4/<seg>.mp3 + .json (same alignment format as voice_v3) and voice_v4/tier_lines.json
# ({seg: {"start": tier line start, "word": first tier word}}); words.json is merged by the whisper step (see build_edl_v2.py).
import json, os, base64, subprocess, urllib.request, shutil
import numpy as np
K = os.environ['ELEVENLABS_JC_API_KEY']; V3, V4 = 'voice_v3/', 'voice_v4/'; P = V4 + 'parts/'
os.makedirs(P, exist_ok=True)
GAP = 0.32
TIER = {  # seg: (line, first word of the tier name as spoken)
 's02': ("For that reason, Jason goes straight into the Easy tier, because you'd outlast him by accident.", 'easy'),
 's03': ("He's big, but he had no plan of his own, so I'm putting Karl in the Don't Worry tier.", "don't"),
 's04': ("Great plan, but she's the least dangerous fighter here, so Mrs. Loomis joins him in Don't Worry.", "don't"),
 's05': ("He racked up bodies, but you can outfight him, so Charlie lands in the Close Call tier.", 'close'),
 's06': ("Creepy, but one kill and done, so Quinn is a Close Call.", 'close'),
 's07': ("Too awkward to be scary, but too close to be safe, so Ethan joins Close Call.", 'close'),
 's08': ("That's a coin you don't want to flip, so Marco goes into the Better Run tier.", 'better'),
 's09': ("You'd never see him coming, so I'm putting Richie in Better Run.", 'better'),
 's10': ("Anyone willing to kill their own family belongs in Better Run.", 'better'),
 's11': ("Unhinged and impossible to read, so Stu lands in the Almost Dead tier.", 'almost'),
 's12': ("That body count puts Mickey right into Almost Dead.", 'almost'),
 's13': ("If fire couldn't stop her, you won't either, so Amber goes into Almost Dead.", 'almost'),
 's14': ("Still, the original Ghostface goes straight into Slaughtered, just not at the very top.", 'slaughtered'),
 's15': ("When the cop is the killer, there's nobody left to call, so Wayne is Slaughtered.", 'slaughtered'),
 's16': ("She'd take out anyone for fame, so Jill goes into Slaughtered.", 'slaughtered'),
 's17': ("And the deadliest Ghostface of them all takes the very top of Slaughtered.", 'slaughtered'),
}
def A(p): return json.load(open(p))
def tts(name, text, prev):
    if os.path.exists(P + name + '.mp3'): return
    body = {'text': text, 'model_id': 'eleven_v4', 'previous_text': prev}
    r = urllib.request.Request('https://api.elevenlabs.io/v1/text-to-speech/s3TPKV1kjDlVtZbl4Ksh/with-timestamps',
                               data=json.dumps(body).encode(), headers={'xi-api-key': K, 'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(r, timeout=300))
    open(P + name + '.mp3', 'wb').write(base64.b64decode(d['audio_base64'])); json.dump(d['alignment'], open(P + name + '.json', 'w'))
    print('tts', name, round(d['alignment']['character_end_times_seconds'][-1], 2), flush=True)
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', '0', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
def pcm(src):
    return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', src, '-f', 's16le', '-ac', '1', '-ar', '44100', '-']), np.int16)
def speech_span(x, sr=44100):  # first / last 10 ms window louder than -42 dBFS
    w = sr // 100; f = x[:len(x) // w * w].astype(np.float32).reshape(-1, w) / 32768
    e = 20 * np.log10(np.sqrt(np.mean(f ** 2, 1)) + 1e-9); i = np.nonzero(e > -42)[0]
    return i[0] * w, (i[-1] + 1) * w
for s in os.listdir(V3):
    if s.endswith(('.mp3', '.json')) and s != 'words.json': shutil.copy(V3 + s, V4 + s)
out = {}
for s, (line, word) in TIER.items():
    base = A(V3 + s + '.json'); tts(s + '_tier', line, ''.join(base['characters']))
    xb = pcm(V3 + s + '.mp3'); xt = pcm(P + s + '_tier.mp3')
    t0, t1 = speech_span(xt); t0 = max(0, t0 - 441); t1 = min(len(xt), t1 + 3528)          # 10 ms lead-in, 80 ms tail
    xt = xt[t0:t1].astype(np.float32); n = 1764; xt[-n:] *= np.linspace(1, 0, n)          # 40 ms fade out
    gap = np.zeros(int(GAP * 44100), np.int16)
    y = np.concatenate([xb, gap, xt.astype(np.int16)])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', '44100', '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '192k',
                    V4 + s + '.mp3'], input=y.tobytes(), check=True)
    off = len(xb) / 44100 + GAP; tal = A(P + s + '_tier.json'); sh = off - t0 / 44100
    al = {}
    al['characters'] = base['characters'] + [' '] + tal['characters']
    al['character_start_times_seconds'] = base['character_start_times_seconds'] + [len(xb) / 44100] + [max(off, x + sh) for x in tal['character_start_times_seconds']]
    al['character_end_times_seconds'] = base['character_end_times_seconds'] + [off] + [min(len(y) / 44100, max(off, x + sh)) for x in tal['character_end_times_seconds']]
    json.dump(al, open(V4 + s + '.json', 'w'))
    out[s] = {'start': round(off, 3), 'word': word, 'line': line}
    print(s, 'tier line at', round(off, 2), 'total', round(len(y) / 44100, 2))
json.dump(out, open(V4 + 'tier_lines.json', 'w'), indent=1)
