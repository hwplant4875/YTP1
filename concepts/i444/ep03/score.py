# EP03 scene-matched score: real sampled instruments (VSCO-2 CE, Virtual Playing Orchestra, Salamander) via sfizz_render,
# placed from edl_v2.json + voice_v4 timings so every cue lands on the edit:
#   cold open: soft timpani/bass-drum hits on each action word over a quiet tremolo build
#   each entry: riser (timpani roll) into the rank card, soft hit + celesta lullaby on the card, warm cello/bass bed,
#               the bed ducks out just before the survival % and a low piano hit lands on the stamp
#   intensity grows from #16 (light: harp) to #1 (heavier: tremolo strings)
#   outro: harp + final D minor chord ringing out
# usage: python score.py edl_v2.json voice_v4 out.wav
import sys, os, json, subprocess
import numpy as np, soundfile as sf
sys.path.insert(0, r'C:\Users\hw549\Downloads\YTP1\music_lab\src')
from engine import sfz_render, SR
from pedalboard import Pedalboard, Reverb, LowShelfFilter, HighShelfFilter
EDL, VOICE, OUT = sys.argv[1:4]
D = os.path.dirname(os.path.abspath(__file__)) + '/'
TMP = os.path.join(os.path.dirname(os.path.abspath(OUT)), 'score_tmp')
FPS = 30
E = json.load(open(EDL)); W = json.load(open(D + VOICE + '/words.json'))
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))

# ---- timeline, computed exactly like render_v2.py (frame-rounded section starts)
secs = []; t = 0.0
for S in E['sections']:
    L = dur(os.path.join(VOICE, S['voice'] + '.mp3')) + S.get('pad', 0.5)
    st = round(t * FPS) / FPS
    stamp = next((st + o[2] + o[1]['t_pct'] for o in S['overlays'] if o[0] == 'stats' and isinstance(o[1].get('pct'), int)), None)
    secs.append({'v': S['voice'], 'start': st, 'end': st + L, 'rank': next((o[1][0] for o in S['overlays'] if o[0] == 'rank'), None), 'stamp': stamp})
    t += L
TOTAL = round(t * FPS) / FPS + 1.0
def word(seg, w, n=1):  # onset of the n-th occurrence of a word in a section (seconds from its start)
    hits = [x[0] for x in W[seg] if x[2].lower().strip('.,?!') == w]; return hits[n - 1]

VSCO = 'VSCO-2-CE-master/'; VPO = 'VirtualPlayingOrchestra/Virtual-Playing-Orchestra3/'
INST = {'cello': VSCO + 'CelloEnsSusVib-Quiet.sfz', 'bass': VSCO + 'ContrabassSusVB-Quiet.sfz', 'trem': VSCO + 'CelloEnsTrem.sfz',
        'harp': VSCO + 'Harp.sfz', 'celesta': VPO + 'Keys/celesta.sfz', 'timp': VPO + 'Percussion/timpani-hit.sfz',
        'roll': VPO + 'Percussion/timpani-roll.sfz', 'bd': VPO + 'Percussion/bassdrum.sfz',
        'piano': 'SalamanderGrandPiano-SFZ+FLAC-V3+20200602/SalamanderGrandPiano-V3+20200602.sfz'}
N = {k: [] for k in INST}   # (sec, dur, midi, vel) with bpm=60 so beats = seconds
DUCK = []                    # (t0, t1) windows where the bed drops out

# D minor progression per entry: i, VI, iv, V (roots)
PROG = [(38, 45), (34, 41), (31, 38), (33, 40)]       # (bass root, cello fifth) D/A, Bb/F, G/D, A/E
LULL = [86, 89, 88, 81]                                 # celesta lullaby: D6 F6 E6 A5
entries = [s for s in secs if s['rank']]
for i, s in enumerate(entries):
    k = 1 - (s['rank'] - 1) / 15                        # 0 at #16 .. 1 at #1
    root, fifth = PROG[i % 4]
    L = s['end'] - s['start']
    # riser into the rank card + the hit on it
    N['roll'].append((max(0, s['start'] - 1.3), 1.25, 38, int(28 + 30 * k)))
    N['timp'].append((s['start'], 2.0, 38, int(52 + 30 * k)))
    N['piano'].append((s['start'], 3.0, 26, int(40 + 25 * k))); N['piano'].append((s['start'], 3.0, 38, int(30 + 20 * k)))
    for j, n in enumerate(LULL):
        N['celesta'].append((s['start'] + 0.6 + 0.45 * j, 0.9, n, int(34 + 14 * k)))
    # warm bed for the whole entry (soft; never a harsh drone)
    b0 = s['start'] + 0.8
    N['bass'].append((b0, L - 0.9, root, int(38 + 22 * k)))
    N['cello'].append((b0, L - 0.9, fifth + 12, int(34 + 22 * k)))
    if k > 0.55: N['trem'].append((b0 + 1.0, L - 2.0, fifth, int(22 + 30 * (k - 0.55) / 0.45 * 1.0)))
    if k < 0.45:                                        # light entries: a slow harp figure instead of tension
        for j, n in enumerate([root + 24, fifth + 24, root + 31, fifth + 24] * 3):
            tt = b0 + 1.0 + 1.6 * j
            if tt < s['end'] - 1.5: N['harp'].append((tt, 1.4, n, int(30 + 10 * k)))
    if s['stamp']:
        DUCK.append((s['stamp'] - 0.75, s['stamp'] + 0.35))
        N['piano'].append((s['stamp'], 2.5, 26, int(48 + 30 * k))); N['piano'].append((s['stamp'], 2.5, 33, int(40 + 25 * k)))
        N['bd'].append((s['stamp'], 1.0, 36, int(40 + 25 * k)))

# cold open: quiet tremolo build, a soft hit on every action word
s0 = secs[0]
N['trem'].append((0.0, s0['end'] - 0.5, 38, 30)); N['bass'].append((0.0, s0['end'] - 0.5, 26, 34))
for w, n in [('shot', 1), ('stabbed', 1), ('set', 1), ('run', 1), ('shot', 2)]:
    tt = s0['start'] + word('s00', w, n)
    N['timp'].append((tt, 1.5, 38, 62)); N['bd'].append((tt, 1.0, 36, 50))
N['celesta'] += [(s0['start'] + word('s00', 'ghostface') + 0.45 * j, 0.9, n, 40) for j, n in enumerate(LULL)]
# rules section: calm piano + cello so the stat card reads
s1 = secs[1]
N['cello'].append((s1['start'] + 0.5, s1['end'] - s1['start'] - 0.8, 50, 32)); N['bass'].append((s1['start'] + 0.5, s1['end'] - s1['start'] - 0.8, 38, 32))
for j in range(int((s1['end'] - s1['start'] - 2) / 2.4)):
    N['piano'].append((s1['start'] + 1.0 + 2.4 * j, 2.2, [62, 65, 69, 65][j % 4], 30))
# outro: harp arpeggio, final chord
so = secs[-1]
for j, n in enumerate([50, 53, 57, 62, 65, 69, 74, 69, 65, 62] * 2):
    tt = so['start'] + 0.3 + 0.35 * j
    if tt < so['end'] - 2.0: N['harp'].append((tt, 1.2, n, 34))
N['timp'].append((so['end'] - 2.2, 3.0, 38, 70)); N['bd'].append((so['end'] - 2.2, 2.0, 36, 45))
for n in (26, 38, 41, 45, 50):
    N['piano'].append((so['end'] - 2.2, 4.0, n, 50))
N['cello'].append((so['start'] + 0.3, so['end'] - so['start'], 50, 34)); N['bass'].append((so['start'] + 0.3, so['end'] - so['start'], 38, 36))

# ---- render each instrument, mix with per-instrument gain, duck the bed before each stamp, reverb, light EQ
n_tot = int(TOTAL * SR) + SR * 4; mix = np.zeros((2, n_tot)); bed = np.zeros((2, n_tot))
GAIN = {'cello': 0.9, 'bass': 0.9, 'trem': 0.5, 'harp': 0.7, 'celesta': 0.45, 'timp': 0.55, 'roll': 0.35, 'bd': 0.45, 'piano': 0.6}
for k, notes in N.items():
    if not notes: continue
    x = sfz_render(INST[k], notes, 60, TMP, 'ep03_' + k)
    x = x[:, :n_tot] * GAIN[k]
    (bed if k in ('cello', 'bass', 'trem', 'harp') else mix)[:, :x.shape[1]] += x
    print('rendered', k, len(notes), flush=True)
g = np.ones(n_tot)
for a, b in DUCK:
    i0, i1 = int(a * SR), int(b * SR); r = int(0.25 * SR)
    g[i0:i1] = 0.12
    g[i0 - r:i0] = np.linspace(1, 0.12, r); g[i1:i1 + r] = np.linspace(0.12, 1, r)
mix += bed * g
board = Pedalboard([LowShelfFilter(cutoff_frequency_hz=120, gain_db=-2), HighShelfFilter(cutoff_frequency_hz=4000, gain_db=-3),
                    Reverb(room_size=0.7, damping=0.6, wet_level=0.22, dry_level=0.85, width=1.0)])
y = board(mix.astype(np.float32), SR)[:, :int(TOTAL * SR)]
y = y / max(1e-6, np.abs(y).max()) * 0.7
sf.write(OUT, y.T, SR)
print('score', OUT, round(TOTAL, 2), 's,', sum(len(v) for v in N.values()), 'notes')
