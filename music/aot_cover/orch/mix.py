"""Mix the rendered stems, add hall tail (Valhalla Supermassive send), master to -14 LUFS / -1 dBTP.

Usage: python mix.py OUT_BASENAME      (writes OUT_BASENAME.wav and .mp3)
"""
import os, sys, json, subprocess
import numpy as np, soundfile as sf, pedalboard
from arrange import R0, SR, STEMS, SEG, SEGMENTS

T0, T1 = SEGMENTS[SEG]['T']
FADE = 0.5

# Relative level of each stem (dB, by RMS over the active window) - lead on top.
LEVEL = {
    'vln1_lead': 2.5, 'vc_lead': -6, 'tpt_counter': -9, 'horns_chords': -10, 'tbn_chords': -11,
    'vln2_spicc': -10, 'vla_spicc': -13, 'cb_spicc': -9, 'vc_spicc': -12, 'cb_long': -15,
    'btbn_down': -12, 'tuba_down': -13, 'timpani': -9, 'perc': -11, 'choir': -9,
}
SEND = {'vln1_lead': 0.30, 'vc_lead': 0.25, 'tpt_counter': 0.35, 'horns_chords': 0.4, 'tbn_chords': 0.3,
        'choir': 0.6, 'timpani': 0.2, 'perc': 0.35}

def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)

def main(out):
    a0, a1 = int((T0 - R0) * SR), int((T1 - R0) * SR)
    bus = None; send = None
    ref = None
    for name, lv in LEVEL.items():
        x, sr = sf.read(os.path.join(STEMS, f'{SEG}_{name}.wav'), always_2d=True)
        x = x.T
        N = int((SEGMENTS[SEG]['R'][1] - R0) * SR)
        x = np.pad(x, ((0, 0), (0, max(0, N - x.shape[1]))))[:, :N]
        act = x[:, a0:a1]
        # RMS over the louder half of 50 ms frames, so sparse parts are judged by their hits
        fr = act[:, : act.shape[1] // 2400 * 2400].reshape(2, -1, 2400)
        e = np.sqrt((fr ** 2).mean(axis=(0, 2)))
        loud = np.sort(e)[len(e) // 2:]
        cur = 20 * np.log10(np.sqrt(np.mean(loud ** 2)) + 1e-12)
        g = 10 ** ((lv - 30 - cur) / 20)
        y = x * g
        bus = y if bus is None else bus + y
        s = y * SEND.get(name, 0.15)
        send = s if send is None else send + s
        print(f'{name:14s} {cur:6.1f} dB -> gain {20*np.log10(g):+6.1f}')
    vh = pedalboard.load_plugin(r"C:\Program Files\Common Files\VST3\ValhallaSupermassive.vst3")
    vh.mode = 'Gemini'; vh.mix = 100.0; vh.delay_ms = 120.0; vh.feedback = 62.0; vh.density = 70.0
    vh.width = 100.0; vh.lowcut = 180.0; vh.highcut = 7500.0; vh.moddepth = 30.0
    wet = vh.process(send.astype(np.float32), SR)
    mixb = bus + 0.35 * wet
    board = pedalboard.Pedalboard([
        pedalboard.HighpassFilter(28),
        pedalboard.Compressor(threshold_db=-24, ratio=1.8, attack_ms=25, release_ms=220),
        pedalboard.Gain(0),
        pedalboard.Limiter(threshold_db=-12, release_ms=150),
    ])
    y = board(mixb.astype(np.float32), SR)[:, a0:a1]
    n = y.shape[1]; f = int(FADE * SR)
    env = np.ones(n); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
    y = y * env
    tmp = out + '_pre.wav'
    sf.write(tmp, y.T, SR, subtype='FLOAT')
    # two-pass loudnorm to -14 LUFS / -1 dBTP
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1])
    af = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', tmp, '-af', af + ',aresample=48000',
                    '-c:a', 'pcm_s24le', out + '.wav'], check=True)
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', out + '.wav', '-c:a', 'libmp3lame',
                    '-b:a', '320k', out + '.mp3'], check=True)
    os.remove(tmp)
    print('input', js['input_i'], 'LUFS', js['input_tp'], 'dBTP')

if __name__ == '__main__':
    main(sys.argv[1])
