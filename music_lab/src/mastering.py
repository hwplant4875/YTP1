"""Final loudness stage: 4x oversampled limiter + 2-pass loudnorm to a target LUFS."""
import json, re, subprocess


def master_ffmpeg(src, dst, lufs=-9.0, tp=-1.0):
    chain = f"aresample=176400,alimiter=limit={10 ** ((tp - 0.3) / 20):.4f}:attack=3:release=60:level=false,aresample=44100"
    # pass 1: measure loudness after limiting
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", chain + f",loudnorm=I={lufs}:TP={tp}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(re.findall(r"{[^{}]*}", r.stderr)[-1])
    gain = lufs - float(m["input_i"])
    # pass 2: static gain into the limiter (keeps punch, no dynamic loudnorm)
    chain2 = f"volume={gain:.2f}dB,aresample=176400,alimiter=limit={10 ** ((tp - 0.3) / 20):.4f}:attack=3:release=60:level=false,aresample=44100"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-af", chain2, "-c:a", "pcm_s24le", dst], check=True)
