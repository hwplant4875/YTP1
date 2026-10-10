# Edit decision list for "Every Lie Walter White Tells" preview: segments, subtitles and lies (clip times).
import json, subprocess
EP = {'O44O4Dd-oT0': ('S1 · E6', "Crazy Handful of Nothin'"), 'Esv08l1mxak': ('S2 · E2', 'Bit by a Dead Bee'),
      'jEK5pIfDfzI': ('S4 · E12', 'End Times'), '9XR6GlaHLyI': ('S5 · E11', 'Confessions'), '_fZshzRh0KA': ('S5 · E12', 'Rabid Dog')}
SEG = [  # clip, in, out, scene start?
 ('O44O4Dd-oT0', 46.3, 63.3, True), ('O44O4Dd-oT0', 122.8, 141.8, False),
 ('Esv08l1mxak', 69.8, 77.0, True), ('Esv08l1mxak', 99.8, 111.5, False), ('Esv08l1mxak', 118.4, 126.0, False),
 ('jEK5pIfDfzI', 0.0, 19.2, True), ('jEK5pIfDfzI', 104.5, 119.4, False),
 ('9XR6GlaHLyI', 0.3, 33.4, True), ('9XR6GlaHLyI', 73.8, 84.9, False),
 ('_fZshzRh0KA', 3.6, 30.0, True), ('_fZshzRh0KA', 85.5, 117.8, False),
]
SUB = {  # clip: [start, end, text]
 'O44O4Dd-oT0': [[46.6, 49.8, "And recently, these afternoons..."], [49.8, 57.2, "when you're coming home so late, and we're just left wondering where you are."],
                 [58.9, 63.1, "Yeah, Dad. What's up with that?"], [129.2, 134.9, "I like to go on walks. A couple of times a week, maybe more. After work."], [137.6, 141.2, "I really enjoy the nature."]],
 'Esv08l1mxak': [[70.2, 71.4, "Do you have a second cell phone?"], [75.4, 76.8, "A second cell phone?"], [100.2, 104.2, "When Hank checked your phone records, there was no call."],
                 [105.7, 108.2, "No call on the phone I know about."], [108.4, 110.8, "I..."], [118.9, 120.3, "...don't remember any of that."],
                 [121.2, 125.6, "But one thing I am sure of is that I don't have a second cell phone."]],
 'jEK5pIfDfzI': [[0.4, 4.4, "Just put the gun down. Okay? Just put it down. We'll talk."], [5.4, 8.4, "Tell me what it is you think I did."], [8.4, 11.2, "Brock! Why'd you poison him?"],
                 [11.5, 12.4, "Who's Brock?"], [12.6, 18.9, "You saw him in my living room last night. You looked right at him, so don't tell me you don't know!"],
                 [104.7, 108.3, "Just admit it! Admit what you did!"], [109.8, 111.3, "I did not do this."], [115.4, 119.2, "I'm not lying. I'm not lying. Just listen to me."]],
 '9XR6GlaHLyI': [[0.5, 4.5, "This is my confession. If you're watching this tape..."], [5.7, 11.6, "I'm probably dead. Murdered by my brother-in-law, Hank Schrader."],
                 [12.7, 18.9, "Hank has been building a meth empire for over a year now, and using me as his chemist."],
                 [19.9, 26.4, "Shortly after my 50th birthday, he asked that I use my chemistry knowledge to cook methamphetamine,"],
                 [27.4, 33.1, "which he would then sell using connections he made through his career with the DEA."],
                 [74.0, 77.9, "Hank had a partner. A businessman named Gustavo Fring."], [78.1, 84.6, "Hank sold me into servitude to this man. When I tried to quit, Fring threatened my family."]],
 '_fZshzRh0KA': [[4.0, 10.8, "Pump malfunction. So I'm standing there filling up, like I've done a thousand times before, and I hear a 'chunk'."],
                 [10.9, 15.9, "You know, the pump's nozzle, the metal thing you squeeze... 'chunk'."], [16.0, 23.5, "So I suppose, in my naiveté, I took it that gas is no longer coming out of the nozzle,"],
                 [23.6, 29.6, "so I pull out the hose to put it back, and whoosh! I'm suddenly soaked in gasoline."], [85.9, 88.1, "You fainted, didn't you?"],
                 [89.2, 95.6, "'Cause you're sick again. You were pumping gas and the fumes made you pass out again."], [96.3, 99.6, "Just admit it. / No, that... no."],
                 [100.6, 101.8, "It was the pump."], [109.2, 117.5, "Maybe I did get a little swimmy at one point, but I did not faint. Okay? I'm fine, and that's the truth."]],
}
LIES = [  # clip, time, to, short quote, truth
 ('O44O4Dd-oT0', 129.4, 'his family', 'I like to go on walks.', "The 'walks' are meth cooks in Jesse's RV."),
 ('Esv08l1mxak', 75.5, 'Skyler', 'A second cell phone?', 'He has one. Only Jesse calls it.'),
 ('Esv08l1mxak', 119.0, 'Skyler', "I don't remember any of that.", 'He faked the fugue state. He remembers everything.'),
 ('Esv08l1mxak', 123.1, 'Skyler', "I don't have a second cell phone.", 'Still has it.'),
 ('jEK5pIfDfzI', 11.6, 'Jesse', "Who's Brock?", 'He knows exactly who Brock is.'),
 ('jEK5pIfDfzI', 109.9, 'Jesse', 'I did not do this.', 'He did. Lily of the valley, from his own garden.'),
 ('jEK5pIfDfzI', 115.5, 'Jesse', "I'm not lying.", "He is. It's the season's final shot."),
 ('9XR6GlaHLyI', 12.8, 'the DEA', 'Hank has been building a meth empire.', 'Walt built it. Hank spent a year hunting Heisenberg.'),
 ('9XR6GlaHLyI', 74.1, 'the DEA', 'Hank had a partner... Gustavo Fring.', "Gus was Walt's partner, not Hank's."),
 ('9XR6GlaHLyI', 78.2, 'the DEA', 'Hank sold me into servitude.', 'Walt took the deal himself. $3 million for 3 months.'),
 ('_fZshzRh0KA', 4.1, 'his family', 'Pump malfunction.', 'Jesse broke in and doused the house in gasoline.'),
 ('_fZshzRh0KA', 100.7, 'Walt Jr.', 'It was the pump.', 'Still not the pump.'),
]
INTRO = 3.2  # seconds of title card before the first scene
FPS = 30
out, t = [], INTRO
segs = []
for clip, a, b, scene in SEG:
    segs.append({'clip': clip, 'in': a, 'out': b, 'at': round(t, 3), 'scene': scene, 'ep': EP[clip]})
    t += b - a
END = round(t, 3)
def to_out(clip, ct):
    for s in segs:
        if s['clip'] == clip and s['in'] <= ct <= s['out']: return round(s['at'] + ct - s['in'], 3)
    return None
subs = []
for clip, lines in SUB.items():
    for a, b, txt in lines:
        oa = to_out(clip, a); ob = to_out(clip, min(b, max(s['out'] for s in segs if s['clip'] == clip)))
        if oa is None:
            continue
        if ob is None: ob = oa + (b - a)
        subs.append({'a': oa, 'b': ob, 't': txt})
lies = []
for i, (clip, ct, who, q, truth) in enumerate(LIES):
    lies.append({'n': i + 1, 'at': to_out(clip, ct), 'to': who, 'q': q, 'truth': truth})
assert all(l['at'] is not None for l in lies), lies
json.dump({'segs': segs, 'subs': sorted(subs, key=lambda s: s['a']), 'lies': lies, 'intro': INTRO, 'end': END, 'outro': 5.0}, open('edl.json', 'w'), indent=1)
print('main', END, 'lies', len(lies))
# base cut: intro = first frame held dark, scenes with short fades at scene boundaries
fl, inputs = [], []
for k, s in enumerate(segs):
    inputs += ['-ss', str(s['in']), '-t', str(round(s['out'] - s['in'], 3)), '-i', f"src/{s['clip']}.mp4"]
parts = []
for k, s in enumerate(segs):
    d = s['out'] - s['in']
    nxt_scene = k + 1 == len(segs) or segs[k + 1]['scene']
    vf = f"[{k}:v]fps={FPS},scale=1920:1080:flags=lanczos,unsharp=5:5:0.6,setsar=1"
    af = f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo"
    if s['scene']: vf += ",fade=in:st=0:d=0.25"; af += ",afade=in:st=0:d=0.15"
    if nxt_scene: vf += f",fade=out:st={d-0.25:.3f}:d=0.25"; af += f",afade=out:st={d-0.2:.3f}:d=0.2"
    fl.append(vf + f"[v{k}]"); fl.append(af + f"[a{k}]"); parts.append(f"[v{k}][a{k}]")
fl.append(''.join(parts) + f"concat=n={len(segs)}:v=1:a=1[vc][ac]")
fl.append(f"[vc]tpad=start_duration={INTRO}:start_mode=clone:stop_duration=5:stop_mode=clone[v]")
fl.append(f"[ac]adelay={int(INTRO*1000)}|{int(INTRO*1000)},apad=pad_dur=5[a]")
subprocess.run(['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex', ';'.join(fl), '-map', '[v]', '-map', '[a]',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', 'base.mp4'], check=True)
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'base.mp4'], capture_output=True, text=True).stdout)
