# EP07 v3 (owner 11/04 16:12: "remove the silence between voice lines, natural, no stops"): every pause inside a take is cut down
# to GAP s (silencedetect -40 dB, >= 0.3 s; the middle of the pause is removed, both edges kept, 8 ms fades), the take's head
# silence to 0.03 s and its tail to 0.12 s. The originals stay in voice_orig/; words.json and the ElevenLabs alignment are
# re-timed with the same cut map, so every cut / caption / card anchor follows the new timing.
import json, os, re, shutil, subprocess
GAP, HEAD, TAIL, FADE = 0.25, 0.03, 0.12, 0.008
os.makedirs('voice_orig', exist_ok=True)
W = json.load(open('voice_orig/words.json' if os.path.exists('voice_orig/words.json') else 'voice/words.json'))
if not os.path.exists('voice_orig/words.json'): shutil.copy('voice/words.json', 'voice_orig/words.json')
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', '0', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
for seg in sorted(W):
    for ext in ('.mp3', '.json'):
        if not os.path.exists(f'voice_orig/{seg}{ext}'): shutil.copy(f'voice/{seg}{ext}', f'voice_orig/{seg}{ext}')
    src = f'voice_orig/{seg}.mp3'; D = dur(src)
    log = subprocess.run(['ffmpeg', '-nostats', '-i', src, '-af', 'silencedetect=n=-40dB:d=0.3', '-f', 'null', '-'], capture_output=True, text=True).stderr
    sil = [(float(a), float(b)) for a, b in zip(re.findall(r'silence_start: ([\d.]+)', log), re.findall(r'silence_end: ([\d.]+)', log))]
    cuts = []                                      # source intervals removed
    for a, b in sil:
        if a <= 0.01: cuts.append((0.0, max(0.0, b - HEAD)))
        elif b >= D - 0.02: cuts.append((min(D, a + TAIL), D))
        elif b - a > GAP: m = (a + b) / 2; cuts.append((m - (b - a - GAP) / 2, m + (b - a - GAP) / 2))
    keep, t = [], 0.0
    for a, b in cuts:
        if a > t: keep.append((t, a))
        t = b
    if t < D: keep.append((t, D))
    def mp(x):                                     # source time -> new time
        out = 0.0
        for a, b in keep:
            if x <= a: return out
            if x <= b: return out + x - a
            out += b - a
        return out
    parts = ''.join(f"[0:a]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS,afade=t=in:d={FADE},afade=t=out:st={max(0, b - a - FADE):.4f}:d={FADE}[k{i}];"
                    for i, (a, b) in enumerate(keep))
    fc = parts + ''.join(f'[k{i}]' for i in range(len(keep))) + f'concat=n={len(keep)}:v=0:a=1[o]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', fc, '-map', '[o]', '-c:a', 'libmp3lame', '-b:a', '192k', f'voice/{seg}.mp3'], check=True)
    al = json.load(open(f'voice_orig/{seg}.json'))
    for k in ('character_start_times_seconds', 'character_end_times_seconds'): al[k] = [round(mp(x), 4) for x in al[k]]
    json.dump(al, open(f'voice/{seg}.json', 'w'))
    W[seg] = [[round(mp(a), 3), round(mp(b), 3), w] for a, b, w in W[seg]]
    print(seg, round(D, 2), '->', round(sum(b - a for a, b in keep), 2), len(cuts), 'cuts')
json.dump(W, open('voice/words.json', 'w'))
