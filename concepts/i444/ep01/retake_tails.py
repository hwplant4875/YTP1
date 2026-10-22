# re-record the ending of each segment (survival rate + instruction) and splice it onto the old head
# usage: python retake_tails.py <voice_dir_in> <voice_dir_out> lines.json
import json, os, sys, base64, subprocess, urllib.request
VIN, VOUT, LINES = sys.argv[1:4]; os.makedirs(VOUT, exist_ok=True)
L = json.load(open(LINES)); K = os.environ['ELEVENLABS_JC_API_KEY']
def tts(text, prev):
    body = json.dumps({'text': text, 'model_id': 'eleven_v4', 'previous_text': prev}).encode()
    r = urllib.request.Request('https://api.elevenlabs.io/v1/text-to-speech/s3TPKV1kjDlVtZbl4Ksh/with-timestamps', data=body,
                               headers={'xi-api-key': K, 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(r, timeout=300))
for seg, (marker, tail) in L.items():
    a = json.load(open(f'{VIN}/{seg}.json')); txt = ''.join(a['characters']); i = txt.find(marker); assert i > 0, (seg, marker)
    cut = a['character_start_times_seconds'][i] - 0.04
    head = f'{VOUT}/{seg}_head.wav'; tl = f'{VOUT}/{seg}_tail.mp3'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{VIN}/{seg}.mp3', '-t', str(cut), '-af', 'afade=t=out:st=%f:d=0.04' % (cut - 0.04), '-ar', '44100', '-ac', '1', head], check=True)
    d = tts(tail, txt[:i].strip()); open(tl, 'wb').write(base64.b64decode(d['audio_base64']))
    t = d['alignment']; lead = t['character_start_times_seconds'][0]
    gap = 0.35
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', head, '-i', tl, '-filter_complex',
                    f"[1:a]atrim=start={max(0, lead - 0.02)},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=mono[t];[0:a]apad=pad_dur={gap}[h];[h][t]concat=n=2:v=0:a=1",
                    '-b:a', '160k', f'{VOUT}/{seg}.mp3'], check=True)
    off = cut + gap - max(0, lead - 0.02)
    al = {'characters': a['characters'][:i] + t['characters'],
          'character_start_times_seconds': a['character_start_times_seconds'][:i] + [x + off for x in t['character_start_times_seconds']],
          'character_end_times_seconds': a['character_end_times_seconds'][:i] + [x + off for x in t['character_end_times_seconds']]}
    json.dump(al, open(f'{VOUT}/{seg}.json', 'w')); os.remove(head); print(seg, 'ok', round(cut, 2), flush=True)
