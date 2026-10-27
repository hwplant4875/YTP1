"""Render the piano MIDI through sfizz + Salamander Grand (pedalboard), add a gentle hall, master to -14 LUFS.

Usage: python piano_preview.py IN.mid OUT_BASENAME
"""
import sys, json, subprocess, os
import numpy as np, mido, pedalboard, soundfile as sf
import sfizz_host

SR = 48000
LEN, FADE = float(os.environ.get("LEN", "30")), 0.5

def main(mid_path, out):
    mf = mido.MidiFile(mid_path)
    msgs, t = [], 0.0
    for m in mf:                         # merged playback order, .time in seconds
        t += m.time
        if not m.is_meta: msgs.append(m.copy(time=t))
    p = sfizz_host.load()
    p.process([], duration=4.0, sample_rate=SR, num_channels=2, buffer_size=1024, reset=True)  # preload
    a = p.process(msgs, duration=LEN + 3, sample_rate=SR, num_channels=2, buffer_size=1024, reset=False)
    vh = pedalboard.load_plugin(r"C:\Program Files\Common Files\VST3\ValhallaSupermassive.vst3")
    vh.mode = 'Gemini'; vh.mix = 100.0; vh.delay_ms = 90.0; vh.feedback = 55.0; vh.density = 80.0
    vh.width = 100.0; vh.lowcut = 220.0; vh.highcut = 6000.0; vh.moddepth = 20.0
    wet = vh.process(a, SR)
    y = 0.35 * (a + 0.16 * wet)
    y = pedalboard.Pedalboard([pedalboard.Compressor(threshold_db=-20, ratio=1.6, attack_ms=30, release_ms=250),
                               pedalboard.Limiter(threshold_db=-6, release_ms=200)])(y.astype(np.float32), SR)
    y = y[:, :int(LEN * SR)]
    f = int(FADE * SR); y[:, -f:] *= np.linspace(1, 0, f)
    y[:, :240] *= np.linspace(0, 1, 240)
    tmp = out + '_pre.wav'; sf.write(tmp, y.T, SR, subtype='FLOAT')
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1])
    af = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true,aresample=48000")
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', tmp, '-af', af, '-c:a', 'pcm_s24le', out + '.wav'], check=True)
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', out + '.wav', '-c:a', 'libmp3lame', '-b:a', '320k', out + '.mp3'], check=True)
    os.remove(tmp)
    print('raw peak', float(np.abs(a).max()), 'input', js['input_i'], js['input_tp'])

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
