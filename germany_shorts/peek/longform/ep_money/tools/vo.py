"""Place the ten narration takes at audio/offsets.json on one 48 kHz mono track -> <out>/vo.wav"""
import json, subprocess, sys, numpy as np, os
HERE = os.path.dirname(os.path.abspath(__file__)); EP = os.path.dirname(HERE)
TAKES = "/mnt/project-files/plans/peek/longform/ep_money/audio/takes/"
SR = 48000
def load(path):
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', 'pipe:1'], capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).copy()
def write(path, x, ch=1):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', str(ch), '-i', 'pipe:0', '-c:a', 'pcm_s24le', path], input=x.astype(np.float32).tobytes(), check=True)
if __name__ == '__main__':
    out = sys.argv[1]
    OFF = json.load(open(os.path.join(EP, 'audio/offsets.json')))
    vo = np.zeros(int(OFF['end'] * SR) + SR, np.float32)
    for b, t in OFF.items():
        if b == 'end': continue
        x = load(TAKES + b + '.mp3'); i = int(round(t * SR)); vo[i:i + len(x)] += x[:len(vo) - i]
    write(os.path.join(out, 'vo.wav'), vo[:int(OFF['end'] * SR)])
    print('vo', len(vo) / SR)
