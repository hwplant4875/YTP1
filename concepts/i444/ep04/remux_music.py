# EP04: swap the music bed of a finished render without re-rendering anything. The video stream is copied and only the audio
# is mixed again, with the same voice timing, voice fades, SFX bus, clip audio and mix as the last step of render_fk.py.
# It reads the renderer's work folder (work_<render name> next to the render: video.mp4, clip_audio.wav, sfx.wav).
# usage: python remux_music.py <edl.json> <voice_dir> <work_dir> <music.mp3> <out.mp4> [fps]
#   env MUSIC_LUFS (default -39) and MUSIC_LEVELLED=1 behave as in render_fk.py
# laptop (11/7, second EP04 version with the episode's ElevenLabs bed):
#   python remux_music.py edl.json voice "E:\YTP2\Horror Ranked\EP04 Freddy Krueger\2_renders\work_ep04_freddy_v3" music\freddy_bed_v1.mp3 "E:\YTP2\Horror Ranked\EP04 Freddy Krueger\2_renders\ep04_freddy_v3_eleven.mp4"
import json, os, subprocess, sys
edl, VOICE, WORK, MUSIC, OUT = sys.argv[1:6]
FPS = int(sys.argv[6]) if len(sys.argv) > 6 else 30
def run(cmd): subprocess.run(cmd, check=True)
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
E = json.load(open(edl))
# the renderer's frame-exact timeline: each section starts on the whole frame nearest the running voice time
t_global = 0.0; voice_items = []
for S in E['sections']:
    vp = os.path.join(VOICE, S['voice'] + '.mp3'); L = dur(vp) + S.get('pad', 0.5)
    voice_items.append((vp, round(t_global * FPS) / FPS)); t_global += L
t_global = round(t_global * FPS) / FPS
vid, clipa, sfxa = (os.path.join(WORK, n) for n in ('video.mp4', 'clip_audio.wav', 'sfx.wav'))
for p in (vid, clipa, sfxa, MUSIC):
    if not os.path.exists(p): sys.exit('missing ' + p)
dv = dur(vid)
if abs(dv - t_global) > 0.1: sys.exit(f'video.mp4 is {dv:.2f} s but the EDL timeline is {t_global:.2f} s: this work folder belongs to another EDL')
ins = ['-i', vid, '-i', clipa, '-i', sfxa]; fc = []
for k, (vp, t) in enumerate(voice_items):
    ins += ['-i', vp]; fc.append(f"[{k+3}:a]aresample=48000,afade=t=out:st={max(0, dur(vp) - 0.16):.3f}:d=0.1,adelay={int(round(t*1000))}|{int(round(t*1000))}[v{k}]")
m = len(voice_items) + 3; ins += ['-stream_loop', '-1', '-i', MUSIC]
mnorm = '' if os.environ.get('MUSIC_LEVELLED') == '1' else f"loudnorm=I={os.environ.get('MUSIC_LUFS', '-39')}:TP=-3,"
fc.append(f"[{m}:a]aresample=48000,atrim=0:{t_global},{mnorm}highshelf=f=3000:g=-4,afade=t=out:st={max(0, t_global-2)}:d=2[mu]")
fc.append(''.join(f'[v{k}]' for k in range(len(voice_items))) + f"amix=inputs={len(voice_items)}:normalize=0,loudnorm=I=-14.6:TP=-1.5[vo]")
fc.append("[1:a][vo][2:a][mu]amix=inputs=4:normalize=0:duration=first,alimiter=limit=0.84:level=0[a]")
run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(t_global), OUT])
print('done', OUT, round(t_global, 2), 'music', MUSIC)
