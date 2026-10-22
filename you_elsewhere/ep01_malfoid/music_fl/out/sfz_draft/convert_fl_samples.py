# FL Studio ships some samples as Ogg Vorbis inside a WAV container (fmt tag 0x674f).
# Pull the Ogg stream out of the data chunk and decode it to FLAC so sfizz can read it.
import sys, struct, subprocess, os, glob, tempfile
def convert(src, dst):
    b = open(src, 'rb').read(); i = 12; ogg = None
    while i < len(b) - 8:
        cid = b[i:i + 4]; sz = struct.unpack('<I', b[i + 4:i + 8])[0]
        if cid == b'data': ogg = b[i + 8:i + 8 + sz]
        i += 8 + sz + (sz & 1)
    tmp = os.path.join(tempfile.gettempdir(), 'flconv.ogg')
    if ogg and ogg[:4] == b'OggS':
        open(tmp, 'wb').write(ogg); inp = tmp
    else:
        inp = src
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', inp, '-c:a', 'flac', '-sample_fmt', 's32', dst], check=True)
for src_glob, out_dir in [(sys.argv[1], sys.argv[2])]:
    os.makedirs(out_dir, exist_ok=True)
    for s in sorted(glob.glob(src_glob)):
        convert(s, os.path.join(out_dir, os.path.splitext(os.path.basename(s))[0].replace('#', 'n').replace(' ', '_') + '.flac'))
