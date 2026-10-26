# EP03 narration v2: new s01 (4 stats), spliced s00 (drop the "from the Ghostface..." clause) and s02 (99%), and every
# "Instruction: ..." tail trimmed off s02-s17. Writes voice_v2/<seg>.mp3 + .json (same alignment format as voice/)
import json, os, base64, subprocess, urllib.request
K = os.environ['ELEVENLABS_JC_API_KEY']; V1, V2 = 'voice/', 'voice_v2/'; P = V2 + 'parts/'
os.makedirs(P, exist_ok=True)
SEG = json.load(open('segments.json'))
NEW = {
 's00b': ("There have been sixteen different people behind that mask, and today we're ranking every single one of them.",
          "He's been shot, stabbed, set on fire, crushed by a TV and run over by a car, and somehow the phone still rings, because Ghostface was never just one guy."),
 's01': ("Quick ground rules before we start. We're not ranking who's the coolest or whose movie was best, we're ranking how hard each one "
         "would be to survive, so every Ghostface gets scored on four things: strength, intelligence, kill count, and deception, which is "
         "basically how close they got to you before you figured it out. Put it all together and you get one number, your survival rate. "
         "Unlike Michael or Jason, every one of these guys is human and every one of them ended up dead, so your odds are a lot better here, "
         "at least at the start.", "There have been sixteen different people behind that mask, and today we're ranking every single one of them."),
 's02b': ("Survival rate: ninety-nine percent, unless you're his film professor.",
          "He was the Ghostface for about five minutes before somebody scarier took the job."),
}
def tts(name, text, prev):
    if os.path.exists(P + name + '.mp3'): return
    body = json.dumps({'text': text, 'model_id': 'eleven_v4', 'previous_text': prev}).encode()
    r = urllib.request.Request('https://api.elevenlabs.io/v1/text-to-speech/s3TPKV1kjDlVtZbl4Ksh/with-timestamps', data=body,
                               headers={'xi-api-key': K, 'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(r, timeout=300))
    open(P + name + '.mp3', 'wb').write(base64.b64decode(d['audio_base64'])); json.dump(d['alignment'], open(P + name + '.json', 'w'))
    print('tts', name, round(d['alignment']['character_end_times_seconds'][-1], 2), flush=True)
for k, (t, prev) in NEW.items(): tts(k, t, prev)
def A(p): return json.load(open(p))
def cut(a, i0, i1, t0, off):  # characters [i0, i1) re-timed: subtract t0, add off
    return {k: [x - t0 + off if 'seconds' in k else x for x in a[k][i0:i1]] for k in a}
def join(*al):
    return {k: sum((x[k] for x in al), []) for k in al[0]}
def wav(src, out, t0=0, t1=None):
    af = f"atrim=start={t0}" + (f":end={t1}" if t1 is not None else '') + ",asetpts=PTS-STARTPTS"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', af, '-ar', '44100', '-ac', '1', out], check=True)
def silence(out, d):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', str(d), out], check=True)
def concat(wavs, out):
    lst = P + 'list.txt'; open(lst, 'w').write(''.join(f"file '{os.path.abspath(w)}'\n" for w in wavs))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c:a', 'libmp3lame', '-b:a', '192k', out], check=True)
def find(a, s):
    t = ''.join(a['characters']); i = t.find(s); assert i >= 0, s; return i
# s00: sentence 1 of the old take, its natural gap, then the new sentence 2
a = A(V1 + 's00.json'); i = find(a, 'guy.') + 4; t_end = a['character_end_times_seconds'][i - 1]
gap = a['character_start_times_seconds'][find(a, 'There')] - t_end
wav(V1 + 's00.mp3', P + 'x0.wav', 0, t_end); silence(P + 'g0.wav', gap); wav(P + 's00b.mp3', P + 'x1.wav')
b = A(P + 's00b.json'); sp = {'characters': [' '], 'character_start_times_seconds': [t_end], 'character_end_times_seconds': [t_end + gap]}
concat([P + 'x0.wav', P + 'g0.wav', P + 'x1.wav'], V2 + 's00.mp3')
json.dump(join(cut(a, 0, i, 0, 0), sp, cut(b, 0, len(b['characters']), 0, t_end + gap)), open(V2 + 's00.json', 'w'))
# s01: new take as is
for e in ('mp3', 'json'): subprocess.run(['cp', P + 's01.' + e, V2 + 's01.' + e], check=True)
# s02: old take up to "job.", its gap, then the new 99% line
a = A(V1 + 's02.json'); i = find(a, 'job.') + 4; t_end = a['character_end_times_seconds'][i - 1]
gap = min(0.6, a['character_start_times_seconds'][find(a, 'Survival')] - t_end)
wav(V1 + 's02.mp3', P + 'y0.wav', 0, t_end); silence(P + 'g1.wav', gap); wav(P + 's02b.mp3', P + 'y1.wav')
b = A(P + 's02b.json'); sp = {'characters': [' '], 'character_start_times_seconds': [t_end], 'character_end_times_seconds': [t_end + gap]}
concat([P + 'y0.wav', P + 'g1.wav', P + 'y1.wav'], V2 + 's02.mp3')
json.dump(join(cut(a, 0, i, 0, 0), sp, cut(b, 0, len(b['characters']), 0, t_end + gap)), open(V2 + 's02.json', 'w'))
# s03-s17: drop "Instruction: ..." and keep "...percent." The ElevenLabs alignment drifts up to 0.7 s here, so the cut sits in the
# measured silence between "percent." and "Instruction" (start of the < -42 dB run, checked against a whisper transcript) + 0.08 s
CUT = {'s03': 17.97, 's04': 20.27, 's05': 14.75, 's06': 15.53, 's07': 18.51, 's08': 17.45, 's09': 17.22, 's10': 19.00, 's11': 20.41,
       's12': 20.80, 's13': 15.75, 's14': 25.07, 's15': 19.08, 's16': 19.79, 's17': 27.02}
for s, c in CUT.items():
    a = A(V1 + s + '.json'); i = find(a, 'percent.') + 8; t_end = c + 0.08
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', V1 + s + '.mp3', '-af', f'atrim=end={t_end},afade=t=out:st={t_end - 0.04}:d=0.04',
                    '-ar', '44100', '-ac', '1', P + s + '.wav'], check=True)
    concat([P + s + '.wav'], V2 + s + '.mp3')
    b = cut(a, 0, i, 0, 0)
    b['character_start_times_seconds'] = [min(x, t_end - 0.05) for x in b['character_start_times_seconds']]
    b['character_end_times_seconds'] = [min(x, t_end) for x in b['character_end_times_seconds']]
    json.dump(b, open(V2 + s + '.json', 'w'))
for e in ('mp3', 'json'): subprocess.run(['cp', V1 + 's18.' + e, V2 + 's18.' + e], check=True)
for n in range(19):
    s = 's%02d' % n; d = float(subprocess.check_output(['ffprobe', '-v', '0', '-show_entries', 'format=duration', '-of', 'csv=p=0', V2 + s + '.mp3']))
    a = A(V2 + s + '.json'); print(s, round(d, 2), ''.join(a['characters'])[-60:])
