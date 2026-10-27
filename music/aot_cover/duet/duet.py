"""Guren no Yumiya - violin + cello duet from the owner's reference MIDI, plus a low-end layer.

The reference notes are played exactly as written. Performance only:
  - articulation: notes shorter than 0.25 s -> spiccato/staccato samples, longer -> sustain
  - phrase dynamics (velocity) from register/density, top-voice emphasis, light humanize
  - violin double/triple stops rolled bottom-to-top by a few ms, like a real bow crossing strings
Low-end layer underneath (not in the reference): contrabass on the cello's lowest note of every
onset (same rhythm), soft piano root octaves on downbeats, sparse timpani on riff downbeats.

Usage:
  python duet.py compare REF.mid            # 10 s snippet per string library -> duet_cmp_*.wav + metrics
  python duet.py render REF.mid OUT_BASE   # 30 s test (LEN env overrides)
"""
import os, sys, json, random, subprocess
import numpy as np, soundfile as sf, mido, pedalboard
import sfizz_host

SR = 48000
VSCO = r"C:\Users\hw549\Downloads\YTP1\_samples\VSCO-2-CE-master"
VPO = r"C:\Users\hw549\Downloads\YTP1\_samples\VirtualPlayingOrchestra\Virtual-Playing-Orchestra3\Strings"
LIBS = {
    'vsco': dict(vln=(f"{VSCO}\\SViolinVib.sfz", f"{VSCO}\\SViolinSpic.sfz"),
                 vc=(f"{VSCO}\\CelloEnsSusVib.sfz", f"{VSCO}\\CelloEnsSpic.sfz")),
    'vpo': dict(vln=(f"{VPO}\\1st-violin-SOLO-sustain.sfz", f"{VPO}\\1st-violin-SOLO-staccato.sfz"),
                vc=(f"{VPO}\\cello-SOLO-sustain.sfz", f"{VPO}\\cello-SOLO-staccato.sfz")),
    'bbc': dict(vln=('Strings_Violins_1', 'Strings_Violins_1'), vc=('Strings_Celli', 'Strings_Celli')),
}
CB = (f"{VSCO}\\ContrabassSusVB.sfz", f"{VSCO}\\ContrabassSpic.sfz")
SHORT = 0.25
random.seed(3)

# ------------------------------------------------------------------ score
def load(path):
    mf = mido.MidiFile(path)
    tempo = next((m.tempo for m in mf.tracks[0] if m.type == 'set_tempo'), 500000)
    spb = tempo / 1e6
    parts = []
    for tr in mf.tracks:
        t, on, ns = 0, {}, []
        for m in tr:
            t += m.time
            if m.type == 'note_on' and m.velocity > 0: on[m.note] = t
            elif m.type in ('note_off', 'note_on') and m.note in on:
                s = on.pop(m.note); ns.append([s / mf.ticks_per_beat * spb, t / mf.ticks_per_beat * spb, m.note])
        if ns: parts.append(sorted(ns))
    return parts[0], parts[1], spb

def curve(vln, vc, spb):
    blk = 8 * spb; length = max(x[1] for x in vln + vc); nb = int(length / blk) + 2
    reg, den = np.zeros(nb), np.zeros(nb)
    for s, e, n in vln: b = int(s / blk); reg[b] = max(reg[b], n); den[b] += 1
    for s, e, n in vc: den[int(s / blk)] += 0.5
    z = lambda x: (x - x.min()) / (np.ptp(x) + 1e-9)
    c = np.convolve(np.pad(0.6 * z(reg) + 0.4 * z(den), 1, mode='edge'), [0.25, 0.5, 0.25], 'valid')
    return lambda t: float(c[min(nb - 1, int(t / blk))])

def groups(ns):
    g = {}
    for s, e, n in ns: g.setdefault(round(s, 3), []).append([s, e, n])
    return [sorted(v, key=lambda x: x[2]) for _, v in sorted(g.items())]

def perform(ns, cv, spb, base, span, roll=0.0, top_boost=6):
    out = []
    for grp in groups(ns):
        s = grp[0][0]; b = (s / spb) % 4
        acc = 7 if b < 0.05 or b > 3.95 else 3 if abs(b - 2) < 0.05 else 0
        jit = random.uniform(-0.006, 0.006)
        for k, (s0, e, n) in enumerate(grp):
            v = base + span * cv(s) + acc + (top_boost if k == len(grp) - 1 else -4) + random.uniform(-4, 4)
            out.append([s0 + jit + k * roll, e, n, int(np.clip(v, 20, 124))])
    return out

def low_layer(vc, cv, spb):
    """Contrabass on the cello's lowest note of every onset; piano root octaves + timpani on downbeats."""
    cb, pno, timp = [], [], []
    for grp in groups(vc):
        s, e, n = grp[0]
        m = n - 12 if n - 12 >= 28 else n           # octave down where the double bass can reach it
        cb.append([s, e, m, int(np.clip(62 + 38 * cv(s) + random.uniform(-4, 4), 30, 118))])
        beat = (s / spb) % 4
        if beat < 0.05 or beat > 3.95:
            r = n if n < 40 else n - 12
            while r > 40: r -= 12
            while r < 24: r += 12
            v = int(40 + 22 * cv(s))
            pno += [[s, s + 4 * spb * 0.9, r, v], [s + 0.004, s + 4 * spb * 0.9, r + 12, v - 6]]
            bar = round(s / (4 * spb))
            if cv(s) > 0.6 and bar % 2 == 0:
                timp.append([s, s + 0.4, 50 + (n - 50) % 12, int(80 + 30 * cv(s))])
    return cb, pno, timp

# ------------------------------------------------------------------ rendering
def msgs_for(notes, t0):
    ms = []
    for s, e, n, v in notes:
        if s < t0 - 0.05: continue
        ms.append(mido.Message('note_on', note=n, velocity=v, time=max(0.0, s - t0)))
        ms.append(mido.Message('note_off', note=n, velocity=0, time=max(0.001, e - t0)))
    return sorted(ms, key=lambda m: (m.time, m.type == 'note_on'))

def render_sfz(sfz, notes, t0, dur):
    p = sfizz_host.load(sfz)
    p.process([], duration=3.0, sample_rate=SR, num_channels=2, buffer_size=1024, reset=True)
    return p.process(msgs_for(notes, t0), duration=dur, sample_rate=SR, num_channels=2, buffer_size=1024, reset=False)

def render_bbc(inst, art, notes, t0, dur):
    import bbc
    p = bbc.load(inst, art)
    p.process([], duration=3.0, sample_rate=SR, num_channels=2, reset=True)
    ms = [mido.Message('control_change', control=1, value=100, time=0.0), mido.Message('control_change', control=11, value=115, time=0.0)]
    return p.process(ms + msgs_for(notes, t0), duration=dur, sample_rate=SR, num_channels=2, buffer_size=512, reset=False)

def render_part(lib, part, notes, t0, dur):
    longs = [x for x in notes if x[1] - x[0] >= SHORT]
    shorts = [x for x in notes if x[1] - x[0] < SHORT]
    if lib == 'bbc':
        inst = LIBS['bbc'][part][0]
        return render_bbc(inst, 0, longs, t0, dur) + render_bbc(inst, 1, shorts, t0, dur)
    sus, sp = LIBS[lib][part] if part in LIBS[lib] else CB
    return render_sfz(sus, longs, t0, dur) + render_sfz(sp, shorts, t0, dur)

def pan(x, p):
    """p in [-1, 1]: balance a stereo signal (keeps the instrument's own stereo image)."""
    return x * np.array([[min(1, 1 - p)], [min(1, 1 + p)]])

def lvl(x):
    fr = x[:, : x.shape[1] // 2400 * 2400].reshape(2, -1, 2400)
    e = np.sqrt((fr ** 2).mean(axis=(0, 2))); loud = np.sort(e)[len(e) // 2:]
    return 20 * np.log10(np.sqrt(np.mean(loud ** 2)) + 1e-12)

def gain_to(x, target):
    return x * 10 ** ((target - lvl(x)) / 20)

# ------------------------------------------------------------------ metrics for the library comparison
def metrics(x):
    m = x.mean(0)
    env = np.sqrt(np.convolve(m ** 2, np.ones(480) / 480, 'same'))
    on = np.where((env[1:] > 0.02) & (env[:-1] <= 0.02))[0]
    rises = []
    for i in on[:60]:
        seg = env[i:i + int(0.2 * SR)]
        if len(seg) and seg.max() > 0: rises.append(np.argmax(seg >= 0.9 * seg.max()) / SR * 1000)
    S = np.abs(np.fft.rfft(m[: SR * 8] * np.hanning(SR * 8))); f = np.fft.rfftfreq(SR * 8, 1 / SR)
    hf = 10 * np.log10(S[(f > 9000) & (f < 16000)].mean() ** 2 / (S[(f > 200) & (f < 4000)].mean() ** 2 + 1e-20))
    fr = m[: len(m) // 4800 * 4800].reshape(-1, 4800)
    spec = np.abs(np.fft.rfft(fr, axis=1)) + 1e-9
    flat = np.mean(np.exp(np.log(spec).mean(1)) / spec.mean(1))
    return dict(attack_ms=round(float(np.median(rises)) if rises else -1, 1), hiss_db=round(float(hf), 1),
                flatness=round(float(flat), 3))

# ------------------------------------------------------------------ main
COVER_BPM = 180.676      # our transcription's tempo; the reference is 180 BPM with bar 1 = our t=0
DRUM_MIDI = r"E:\YTP2\AoT_Music\repo\music\aot_cover\midi\guren_from_0m21_full.mid"
SWIRLY = r"C:\Users\hw549\Downloads\YTP1\_samples\karoryfer.swirly-drums-main\Programs\Full_kit.sfz"
KIT = {36: 36, 35: 36, 38: 38, 40: 38, 46: 46, 42: 42, 44: 44, 49: 49, 57: 49, 51: 51, 43: 43, 45: 45, 47: 47, 50: 48, 48: 48}

def drums(spb, length):
    """The original song's kit part from our transcription, mapped to Swirly Drums (GM-style keys)."""
    from arrange import track_notes
    mf = mido.MidiFile(DRUM_MIDI)
    T = {t.name: i for i, t in enumerate(mf.tracks)}
    out, cc = [], []
    for s, e, n, v in track_notes(mf, T['Drums Drum kit']):
        if s > length + 1 or n not in KIT: continue
        k = KIT[n]
        if k == 51:                                   # ride: accent the beats, soften the offbeats
            b = (s / spb) % 1
            v = v * (1.0 if b < 0.1 or b > 0.9 else 0.8)
        if k == 46: cc.append((s - 0.005, 118))       # open hat: pedal CC4 open, then close again
        v = int(np.clip(v + random.uniform(-6, 6), 15, 127))
        out.append([s + random.uniform(-0.004, 0.004), s + 0.25, k, v])
        if k == 46: cc.append((s + 0.3, 0))
    return out, cc

def build(ref):
    vln, vc, spb = load(ref)
    k = 180.0 / COVER_BPM if abs(60 / spb - 180.0) < 0.5 else 1.0
    vln = [[s * k, e * k, n] for s, e, n in vln]; vc = [[s * k, e * k, n] for s, e, n in vc]; spb *= k
    cv = curve(vln, vc, spb)
    V = perform(vln, cv, spb, base=60, span=38, roll=0.012)
    C = perform(vc, cv, spb, base=56, span=36, roll=0.006, top_boost=-2)
    cb, pno, timp = low_layer(vc, cv, spb)
    return V, C, cb, pno, timp

def compare(ref):
    V, C, *_ = build(ref)
    res = {}
    for lib in LIBS:
        v = render_part(lib, 'vln', V, 0.0, 10.0); c = render_part(lib, 'vc', C, 0.0, 10.0)
        mix = gain_to(v, -20) + gain_to(c, -24)
        sf.write(f'duet_cmp_{lib}.wav', (mix * 0.5).T, SR)
        res[lib] = dict(violin=metrics(v), cello=metrics(c))
        print(lib, json.dumps(res[lib]), flush=True)
    return res

def peak_limit(y, ceiling_db=-1.5, look_ms=2.0, release_ms=80.0):
    """Look-ahead peak limiter (no makeup gain): the gain never lets |y| exceed the ceiling."""
    from scipy.ndimage import minimum_filter1d
    c = 10 ** (ceiling_db / 20)
    g = np.minimum(1.0, c / (np.abs(y).max(0) + 1e-12))
    la = max(1, int(look_ms / 1000 * SR))
    g = minimum_filter1d(g, size=2 * la + 1)
    a = np.exp(-1 / (release_ms / 1000 * SR)); out = np.empty_like(g); cur = 1.0
    for i, x in enumerate(g):                       # instant attack, smooth release
        cur = x if x < cur else a * cur + (1 - a) * x
        out[i] = cur
    return y * out

def loudness(y):
    tmp = '_meas.wav'; sf.write(tmp, y.T, SR, subtype='FLOAT')
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    os.remove(tmp)
    summ = r.stderr.split('Summary:')[1]
    return float(summ.split('I:')[1].split('LUFS')[0]), float(summ.split('Peak:')[1].split('dBFS')[0])

def master(y, out, fade=0.5, target=-14.0):
    f = int(fade * SR); y[:, -f:] *= np.linspace(1, 0, f)
    g = 0.0
    for _ in range(3):                              # gain -> limit -> re-measure
        z = peak_limit(y * 10 ** (g / 20), ceiling_db=-1.5)
        I, tp = loudness(z)
        if abs(I - target) < 0.2: break
        g += target - I
    sf.write(out + '.wav', z.T, SR, subtype='PCM_24')
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', out + '.wav', '-c:a', 'libmp3lame',
                    '-b:a', '320k', out + '.mp3'], check=True)
    print(f'master: {I:.1f} LUFS, true peak {tp:.1f} dBTP, makeup {g:+.1f} dB')

def render(ref, out, length=30.0):
    V, C, cb, pno, timp = build(ref)
    dur = length + 3.0
    import bbc
    parts = {
        'vln': render_part('bbc', 'vln', V, 0.0, dur),                      # BBC SO Discover Violins 1
        'vc': render_part('vpo', 'vc', C, 0.0, dur),                        # VPO solo cello
        'cb': render_bbc('Strings_Basses', 0, [x for x in cb if x[1] - x[0] >= SHORT], 0.0, dur)
              + render_bbc('Strings_Basses', 1, [x for x in cb if x[1] - x[0] < SHORT], 0.0, dur),
        'pno': render_sfz(sfizz_host.SALAMANDER, pno, 0.0, dur),
    }
    dn, dcc = drums(60 / COVER_BPM, length)
    kit = sfizz_host.load(SWIRLY)
    kit.process([], duration=4.0, sample_rate=SR, num_channels=2, buffer_size=1024, reset=True)
    ms = msgs_for([[s, e, n, v] for s, e, n, v in dn], 0.0)
    ms += [mido.Message('control_change', control=4, value=v, time=max(0.0, t)) for t, v in dcc]
    parts['drums'] = kit.process(sorted(ms, key=lambda m: m.time), duration=dur, sample_rate=SR, num_channels=2,
                                 buffer_size=1024, reset=False)
    # kick key-only render for sidechain: duck the contrabass ~3 dB under each kick
    kick_env = np.zeros(int(dur * SR))
    for s, e, n, v in dn:
        if n == 36:
            i = int(s * SR); L = int(0.12 * SR)
            kick_env[i:i + L] = np.maximum(kick_env[i:i + L], (v / 127) * np.exp(-np.arange(min(L, len(kick_env) - i)) / (0.05 * SR)))
    LV = dict(vln=-17, vc=-20, cb=-25, pno=-34, drums=-21)
    PAN = dict(vln=-0.25, vc=0.25, cb=0.1, pno=0.0, drums=0.0)
    SEND = dict(vln=0.25, vc=0.35, cb=0.15, pno=0.2, drums=0.08)
    bus = 0; send = 0
    for k, x in parts.items():
        y = pan(gain_to(x, LV[k]) if np.abs(x).max() > 0 else x, PAN[k])
        if k == 'cb':
            y = y * (1 - 0.3 * kick_env[: y.shape[1]])
            y = pedalboard.Pedalboard([pedalboard.HighpassFilter(38),
                                       pedalboard.PeakFilter(cutoff_frequency_hz=60, gain_db=-2.5, q=1.0)])(y.astype(np.float32), SR)
        if k == 'drums':   # leave the 80-120 Hz body to the basses, keep the kick's thump at ~55 Hz and click
            y = pedalboard.Pedalboard([pedalboard.PeakFilter(cutoff_frequency_hz=100, gain_db=-3, q=1.2),
                                       pedalboard.PeakFilter(cutoff_frequency_hz=4000, gain_db=1.5, q=0.8)])(y.astype(np.float32), SR)
        sf.write(f'stems/duet_{k}.wav', y.T.astype(np.float32), SR, subtype='FLOAT')
        bus = bus + y; send = send + y * SEND[k]
    vh = pedalboard.load_plugin(r"C:\Program Files\Common Files\VST3\ValhallaSupermassive.vst3")
    vh.mode = 'Gemini'; vh.mix = 100.0; vh.delay_ms = 110.0; vh.feedback = 58.0; vh.density = 80.0
    vh.width = 100.0; vh.lowcut = 200.0; vh.highcut = 7000.0; vh.moddepth = 25.0
    y = bus + 0.3 * vh.process(send.astype(np.float32), SR)
    y = pedalboard.Pedalboard([pedalboard.HighpassFilter(34), pedalboard.LowShelfFilter(cutoff_frequency_hz=55, gain_db=-3.0, q=0.7),
                               pedalboard.Compressor(threshold_db=-22, ratio=1.6, attack_ms=30, release_ms=250)])(y.astype(np.float32), SR)
    master(y[:, :int(length * SR)].copy(), out)

if __name__ == '__main__':
    if sys.argv[1] == 'compare':
        compare(sys.argv[2])
    else:
        render(sys.argv[2], sys.argv[3], float(os.environ.get('LEN', '30')))
