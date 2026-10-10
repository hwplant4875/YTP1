"""Force a calm falling ending on a Korean TTS clip: pitch in the last part of the voiced audio is capped on a
line that glides from the clip's mid-phrase pitch down by DROP semitones (Praat PSOLA). Pitch is only ever lowered."""
import sys, numpy as np, parselmouth
from parselmouth.praat import call
DROP, TAIL = 3.0, 0.35
def fall(src, dst):
    snd = parselmouth.Sound(src)
    pitch = snd.to_pitch(time_step=0.01, pitch_floor=60, pitch_ceiling=300)
    t = pitch.xs(); f = pitch.selected_array["frequency"]; v = f > 0
    if v.sum() < 10: snd.save(dst, "WAV"); return
    tv, fv = t[v], f[v]; n = len(fv)
    ref = np.median(fv[int(n * .3):int(n * .6)]); t0 = tv[int(n * (1 - TAIL))]; t1 = tv[-1]
    man = call(snd, "To Manipulation", 0.01, 60, 300)
    tier = call(man, "Extract pitch tier")
    for k in range(call(tier, "Get number of points"), 0, -1):
        tt = call(tier, "Get time from index", k)
        if tt >= t0:
            cap = ref * 2 ** (-DROP * (tt - t0) / max(t1 - t0, 1e-3) / 12)
            val = call(tier, "Get value at index", k)
            if val > cap: call(tier, "Remove point", k); call(tier, "Add point", tt, cap)
    call([man, tier], "Replace pitch tier")
    call(man, "Get resynthesis (overlap-add)").save(dst, "WAV")
if __name__ == "__main__": fall(sys.argv[1], sys.argv[2])
