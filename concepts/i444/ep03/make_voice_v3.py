# EP03 narration v3 = voice_v2 with the lines whose action no official clip shows rewritten to things we can show
# (laptop frame QA 10/26): s00 "crushed by a TV" -> "shot in the head", Karl run over by Gale's van, Ethan / Richie / Stu /
# Mickey / Jill deaths reworded to the footage we have. Writes voice_v3/<seg>.mp3 + .json (same alignment format as voice/)
import json, os, base64, subprocess, urllib.request, shutil
import numpy as np
K = os.environ['ELEVENLABS_JC_API_KEY']; V2, V3 = 'voice_v2/', 'voice_v3/'; P = V3 + 'parts/'
os.makedirs(P, exist_ok=True)
S00B = "There have been sixteen different people behind that mask, and today we're ranking every single one of them."
NEW = {
 's00a': ("He's been shot, stabbed, set on fire, run over by a car and shot in the head, and somehow the phone still rings, "
          "because Ghostface was never just one guy.", None, S00B),
 's03': ("Number fifteen is Karl Gibbs from Scream Seven, an escaped patient who's big and genuinely scary in a fight, but he was "
         "really just a pawn for the people running things, and his run ended the second Gale floored it and hit him with her van. "
         "Survival rate: seventy-five percent.", "Survival rate: ninety-nine percent, unless you're his film professor.", None),
 's07': ("Number eleven is Ethan Landry, the awkward roommate who was always just a little too close, and that closeness is exactly "
         "what makes him dangerous, but once the mask came off, Tara put a knife in him again and again, and that was the end of the "
         "awkward roommate. Survival rate: fifty-three percent.", "Survival rate: fifty-six percent.", None),
 's09': ("Number nine is Richie Kirsch, the sweet boyfriend nobody suspected for a single second, who stabbed the sheriff in broad "
         "daylight and fooled Sam the whole movie, but the moment she figured him out, she stabbed him over and over until he finally "
         "stopped moving. Survival rate: forty-five percent.", "Survival rate: fifty percent.", None),
 's11': ("Number seven is Stu Macher, and a lot of fans would put him way higher, because he's easily one of the most unhinged "
         "Ghostfaces ever, but he only had a couple of kills, and he was so committed to the bit that he let Billy stab him over and "
         "over just to sell their story. Survival rate: forty percent.", "Survival rate: forty-three percent.", None),
 's12': ("Number six is Mickey Altieri, the film student who planned to get caught on purpose so he could blame the movies at his "
         "trial. He racked up one of the biggest body counts of the early films and even framed Derek, but he never saw the twist "
         "coming, because his own partner shot him the second he stopped being useful. Survival rate: thirty-six percent.",
         "Survival rate: forty percent.", None),
 's16': ("Number two is Jill Roberts, Sidney's own cousin, and the smile she gave when that mask came off says everything. She killed "
         "her friends, her mom and even her own partner, then played the wounded survivor so well that the whole town believed her, "
         "and she came closer than anyone to stealing Sidney's life for good. Survival rate: eighteen percent.",
         "Survival rate: twenty-two percent.", None),
}
def tts(name, text, prev, nxt):
    if os.path.exists(P + name + '.mp3'): return
    body = {'text': text, 'model_id': 'eleven_v4'}
    if prev: body['previous_text'] = prev
    if nxt: body['next_text'] = nxt
    r = urllib.request.Request('https://api.elevenlabs.io/v1/text-to-speech/s3TPKV1kjDlVtZbl4Ksh/with-timestamps',
                               data=json.dumps(body).encode(), headers={'xi-api-key': K, 'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(r, timeout=300))
    open(P + name + '.mp3', 'wb').write(base64.b64decode(d['audio_base64'])); json.dump(d['alignment'], open(P + name + '.json', 'w'))
    print('tts', name, round(d['alignment']['character_end_times_seconds'][-1], 2), flush=True)
for k, v in NEW.items(): tts(k, *v)
def A(p): return json.load(open(p))
def cut(a, i0, i1, t0, off):
    return {k: [x - t0 + off if 'seconds' in k else x for x in a[k][i0:i1]] for k in a}
def join(*al): return {k: sum((x[k] for x in al), []) for k in al[0]}
def wav(src, out, t0=0, t1=None, fade=False):
    af = f"atrim=start={t0}" + (f":end={t1}" if t1 is not None else '') + ",asetpts=PTS-STARTPTS"
    if fade and t1 is not None: af += f",afade=t=out:st={t1 - t0 - 0.04}:d=0.04"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', af, '-ar', '44100', '-ac', '1', out], check=True)
def silence(out, d):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', str(d), out], check=True)
def concat(wavs, out):
    lst = P + 'list.txt'; open(lst, 'w').write(''.join(f"file '{os.path.abspath(w)}'\n" for w in wavs))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c:a', 'libmp3lame', '-b:a', '192k', out], check=True)
def find(a, s):
    t = ''.join(a['characters']); i = t.find(s); assert i >= 0, s; return i
def speech_end(src):  # end of the last stretch louder than -42 dBFS (10 ms windows); the alignment drifts near pauses
    x = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', src, '-f', 's16le', '-ac', '1', '-ar', '16000', '-']),
                      np.int16).astype(np.float32) / 32768
    w = 160; e = 20 * np.log10(np.sqrt(np.mean(x[:len(x) // w * w].reshape(-1, w) ** 2, 1)) + 1e-9)
    return (np.nonzero(e > -42)[0][-1] + 1) * w / 16000
for s in os.listdir(V2):
    if s.endswith(('.mp3', '.json')): shutil.copy(V2 + s, V3 + s)
# s00: new sentence 1, the v2 gap, then the v2 sentence 2 take
a = A(P + 's00a.json'); t1 = speech_end(P + 's00a.mp3') + 0.04
gap = 0.45
wav(P + 's00a.mp3', P + 'x0.wav', 0, t1, True); silence(P + 'g0.wav', gap); wav(V2 + 'parts/s00b.mp3', P + 'x1.wav')
b = A(V2 + 'parts/s00b.json')
a['character_end_times_seconds'] = [min(x, t1) for x in a['character_end_times_seconds']]
sp = {'characters': [' '], 'character_start_times_seconds': [t1], 'character_end_times_seconds': [t1 + gap]}
concat([P + 'x0.wav', P + 'g0.wav', P + 'x1.wav'], V3 + 's00.mp3')
json.dump(join(a, sp, cut(b, 0, len(b['characters']), 0, t1 + gap)), open(V3 + 's00.json', 'w'))
# re-voiced sections: trim the tail silence after "percent." (+0.08 s, 40 ms fade)
for s in [k for k in NEW if k != 's00a']:
    a = A(P + s + '.json'); t_end = speech_end(P + s + '.mp3') + 0.08
    wav(P + s + '.mp3', P + s + '.wav', 0, t_end, True); concat([P + s + '.wav'], V3 + s + '.mp3')
    a['character_start_times_seconds'] = [min(x, t_end - 0.05) for x in a['character_start_times_seconds']]
    a['character_end_times_seconds'] = [min(x, t_end) for x in a['character_end_times_seconds']]
    json.dump(a, open(V3 + s + '.json', 'w'))
for n in range(19):
    s = 's%02d' % n; d = float(subprocess.check_output(['ffprobe', '-v', '0', '-show_entries', 'format=duration', '-of', 'csv=p=0', V3 + s + '.mp3']))
    print(s, round(d, 2), ''.join(A(V3 + s + '.json')['characters'])[-50:])
