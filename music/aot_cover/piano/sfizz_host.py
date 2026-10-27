"""Load an SFZ file into the sfizz VST3 inside pedalboard (by writing sfizz's state blob)."""
import glob, re, struct
import pedalboard
from jb64 import jenc, parse_state

SFIZZ = glob.glob(r"C:\Program Files\Common Files\VST3\sfizz.vst3\Contents\x86_64-win\*.vst3")[0]
SALAMANDER = r"C:\Users\hw549\Downloads\YTP1\_samples\SalamanderGrandPiano-SFZ+FLAC-V3+20200602\SalamanderGrandPiano-V3+20200602.sfz"

def load(sfz=SALAMANDER):
    p = pedalboard.load_plugin(SFIZZ, plugin_name="sfizz")
    outer, c = parse_state(p.raw_state)
    ver, n = c[:8], struct.unpack('<I', c[8:12])[0]
    path = sfz.encode('utf-8') + b'\0'
    c2 = ver + struct.pack('<I', len(path)) + path + c[12 + n:]
    new = re.sub(r'<IComponent>.*?</IComponent>', '<IComponent>' + jenc(c2) + '</IComponent>', outer, flags=re.S).encode()
    p.raw_state = b'VC2!' + struct.pack('<I', len(new) - 1) + new
    return p
