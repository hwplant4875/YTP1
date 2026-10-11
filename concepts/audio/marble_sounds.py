# Marble collision sound schemes modelled on high-view ball/marble shorts:
#  - "melody": every hit plays the next note of a recognisable public-domain tune (Music Marble / bouncing-ball-song style)
#  - "tone":   every hit is one short pleasant tonal blip (Earclacks / Math Balls League style)
# usage: python3 -I marble_sounds.py <scheme> <out.wav> [t0 t1]      schemes: see SCHEMES below
import json, sys
import numpy as np
SR = 48000
C = '/home/user/YTP1/concepts'

def midi(n): return 440.0 * 2 ** ((n - 69) / 12)

def env_exp(n, tau, att=0.002):
    t = np.arange(n) / SR
    return np.minimum(1, t / att) * np.exp(-t / tau)

def marimba(f, v):
    n = int(1.2 * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * env_exp(n, 0.45) + 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * env_exp(n, 0.07) + 0.08 * np.sin(2 * np.pi * f * 9.2 * t) * env_exp(n, 0.02)
    return s * v

def musicbox(f, v):
    n = int(2.0 * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * env_exp(n, 0.9) + 0.4 * np.sin(2 * np.pi * f * 2.0 * t) * env_exp(n, 0.35) + 0.18 * np.sin(2 * np.pi * f * 5.43 * t) * env_exp(n, 0.08)
    return s * v * 0.8

def kalimba(f, v):
    n = int(1.6 * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * env_exp(n, 0.6) + 0.22 * np.sin(2 * np.pi * f * 6.1 * t) * env_exp(n, 0.05)
    thunk = np.random.default_rng(int(f)).normal(0, 1, n) * env_exp(n, 0.004) * 0.15
    return (s + thunk) * v

def epiano(f, v):  # 2-op FM, soft Rhodes-like bell
    n = int(1.6 * SR); t = np.arange(n) / SR
    idx = 1.6 * env_exp(n, 0.25)
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t)) * env_exp(n, 0.7, 0.004)
    return s * v

def boop(f, v):  # short sine with a quick downward pitch settle
    n = int(0.35 * SR); t = np.arange(n) / SR
    fr = f * (1 + 0.5 * np.exp(-t / 0.012)); ph = 2 * np.pi * np.cumsum(fr) / SR
    return np.sin(ph) * env_exp(n, 0.09, 0.001) * v

def bubble(f, v):  # water-drop plink: fast upward sweep
    n = int(0.25 * SR); t = np.arange(n) / SR
    fr = f * (0.6 + 0.9 * (1 - np.exp(-t / 0.02))); ph = 2 * np.pi * np.cumsum(fr) / SR
    return np.sin(ph) * env_exp(n, 0.05, 0.001) * v

def boom(f, v):  # Vine-boom-like low thump, kept very quiet in the mix
    n = int(1.4 * SR); t = np.arange(n) / SR
    fr = 48 + 70 * np.exp(-t / 0.05); ph = 2 * np.pi * np.cumsum(fr) / SR
    s = np.tanh(2.2 * np.sin(ph)) * env_exp(n, 0.38, 0.003)
    s += np.random.default_rng(1).normal(0, 1, n) * env_exp(n, 0.006) * 0.25
    return s * v

def chip(f, v):  # 8-bit square blip
    n = int(0.16 * SR); t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * f * t)) * 0.5
    k = np.exp(-np.arange(32) / 6); s = np.convolve(s, k / k.sum(), 'same')  # soften the edges
    return s * env_exp(n, 0.06, 0.001) * v

# melodies as MIDI note lists (all public domain)
MOUNTAIN_KING = [59, 61, 62, 64, 66, 62, 66, 65, 61, 65, 64, 60, 64, 59, 61, 62, 64, 66, 62, 66, 71, 69, 66, 62, 66, 69]
TWINKLE = [60, 60, 67, 67, 69, 69, 67, 65, 65, 64, 64, 62, 62, 60, 67, 67, 65, 65, 64, 64, 62, 67, 67, 65, 65, 64, 64, 62]
ODE = [64, 64, 65, 67, 67, 65, 64, 62, 60, 60, 62, 64, 64, 62, 62, 64, 64, 65, 67, 67, 65, 64, 62, 60, 60, 62, 64, 62, 60, 60]
ELISE = [76, 75, 76, 75, 76, 71, 74, 72, 69, 60, 64, 69, 71, 64, 68, 71, 72, 64, 76, 75, 76, 75, 76, 71, 74, 72, 69, 60, 64, 69, 71, 64, 72, 71, 69]
PENTA = [60, 62, 64, 67, 69, 72, 74, 76, 79, 81]

SCHEMES = {  # name: (kind, instrument, notes/transpose, gain dB, keep music bed)
    'A_marimba_mountain_king': ('melody', marimba, (MOUNTAIN_KING, 12), -6, False),
    'B_musicbox_twinkle': ('melody', musicbox, (TWINKLE, 12), -7, False),
    'C_kalimba_ode_to_joy': ('melody', kalimba, (ODE, 12), -6, False),
    'D_epiano_fur_elise': ('melody', epiano, (ELISE, 0), -7, False),
    'E_soft_boop': ('tone', boop, 'size', -11, True),
    'F_water_drop': ('tone', bubble, 'size', -6, True),
    'G_quiet_vine_boom': ('tone', boom, 'big', -19, True),
    'H_8bit_blip': ('tone', chip, 'penta', -5, True),
}

def reverb(x, sec=1.4, mix=0.18):
    n = int(sec * SR); rng = np.random.default_rng(7)
    ir = rng.normal(0, 1, (n, 2)) * np.exp(-np.arange(n) / SR / (sec / 5))[:, None]
    ir /= np.sqrt((ir ** 2).sum(0))
    L = len(x) + n; N = 1 << int(np.ceil(np.log2(L)))
    wet = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], N) * np.fft.rfft(ir[:, c], N), N)[:L] for c in (0, 1)], 1)
    out = wet * mix; out[:len(x)] += x * (1 - mix)
    return out[:len(x)].astype(np.float32)

def events(R, LEAD):
    F = np.array(R['frames']); fps = R['fps']
    v = np.diff(F[:, :, :2], axis=0) * fps
    a = np.linalg.norm(np.diff(v, axis=0), axis=2)
    last = np.full(F.shape[1], -99); ev = []
    for k in range(a.shape[0]):
        for i in range(a.shape[1]):
            if a[k, i] > 1.6 and k - last[i] > 4:
                last[i] = k
                ev.append((LEAD + (k + 1) / fps, i, min(1.0, (a[k, i] - 1.2) / 8), float(F[k, i, 0])))
    return [e for e in ev if e[0] >= 0]

def render(scheme, D, LEAD=-0.8):
    R = json.load(open(f'{C}/marble/race.json'))
    kind, inst, arg, gdb, _ = SCHEMES[scheme]
    buf = np.zeros((int((D + 2) * SR), 2), np.float32)
    ev = events(R, LEAD); rng = np.random.default_rng(5)
    def put(sig, t, pan):
        i = int(t * SR); n = min(len(sig), len(buf) - i)
        if n <= 0: return
        buf[i:i + n, 0] += sig[:n] * (1 - pan * 0.5); buf[i:i + n, 1] += sig[:n] * (1 + pan * 0.5)
    if kind == 'melody':
        notes, tr = arg; j = 0; lt = -1
        for t, i, st, x in ev:  # strongest hits drive the tune, rate-limited so it stays a melody, not a cluster
            if st < 0.12 or t - lt < 0.16: continue
            lt = t; f = midi(notes[j % len(notes)] + tr); j += 1
            put(inst(f, 0.55 + 0.45 * st), t, float(np.clip(x / 9, -0.6, 0.6)))
    else:
        lt = {}
        for t, i, st, x in ev:
            r = R['res'][i]['r']
            if arg == 'big' and st < 0.25: continue
            if t - lt.get(i, -1) < 0.08: continue
            lt[i] = t
            if arg == 'size': f = 1400 - 900 * min(1, (r - 0.3) / 0.9)   # big marble = low note
            elif arg == 'big': f = 1
            else: f = midi(PENTA[rng.integers(len(PENTA))] + 12)
            put(inst(f, (0.35 + 0.65 * st) * (0.6 + 0.6 * r if arg == 'big' else 1)), t, float(np.clip(x / 9, -0.6, 0.6)))
    buf = reverb(buf, 1.6 if kind == 'melody' else 0.9, 0.22 if kind == 'melody' else 0.12)
    return buf[:int(D * SR)] * 10 ** (gdb / 20)

if __name__ == '__main__':
    import wave
    scheme, out = sys.argv[1], sys.argv[2]
    b = render(scheme, float(sys.argv[3]) if len(sys.argv) > 3 else 43.0)
    b = b / max(1.0, np.abs(b).max() / 0.95)
    with wave.open(out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(b, -1, 1) * 32767).astype(np.int16).tobytes())
