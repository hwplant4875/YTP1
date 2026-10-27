"""Load BBC SO Discover instruments into pedalboard by injecting NKS preset XML into the VST3 state."""
import struct, re, glob, os
import pedalboard
from jb64 import jdec, jenc, parse_state
PLUG = r"C:\Program Files\Common Files\VST3\BBC Symphony Orchestra (64 Bit).vst3\Contents\x86_64-win\BBC Symphony Orchestra (64 Bit).vst3"
NKS = r"E:\YTP2\Spitfire\Spitfire Audio - BBC Symphony Orchestra\NKS"
HDR = '<?xml version="1.0" encoding="UTF-8"?>'

def nks_xml(name):
    f = os.path.join(NKS, f"BBCSO_Discover_{name}.nksf")
    b = open(f, 'rb').read(); i = 12
    while i < len(b):
        cid = b[i:i+4]; sz = struct.unpack('<I', b[i+4:i+8])[0]
        if cid == b'PCHK': d = b[i+8:i+8+sz]
        i += 8 + sz + (sz & 1)
    x = d[d.find(b'<'):d.rfind(b'>')+1].decode()
    return re.sub(r'^<\?xml[^>]*\?>', HDR, x)

def select_artic(x, idx):
    """Make articulation idx the only active one."""
    parts = x.split('<ARTIC>')
    out = [parts[0].replace('id="p_lastSelectedPrimaryArtic" value="0"', f'id="p_lastSelectedPrimaryArtic" value="{idx}"')]
    for k, p in enumerate(parts[1:]):
        p = re.sub(r'id="a_active" value="\d+"', f'id="a_active" value="{2 if k == idx else 0}"', p, count=1)
        out.append(p)
    return '<ARTIC>'.join(out)

def build_state(template_raw, auntie_xml):
    outer, c = parse_state(template_raw)
    old_len = struct.unpack('<I', c[180:184])[0]
    tail = c[184+old_len:]
    xb = auntie_xml.encode()
    chunk = b'VC2!' + struct.pack('<I', len(xb)) + xb + tail
    c2 = bytearray(c[:176]) + chunk
    struct.pack_into('>I', c2, 172, len(chunk))
    struct.pack_into('>I', c2, 20, len(c2) - 24)
    new_outer = re.sub(r'<IComponent>.*?</IComponent>', '<IComponent>' + jenc(bytes(c2)) + '</IComponent>', outer, flags=re.S)
    ob = new_outer.encode()
    return b'VC2!' + struct.pack('<I', len(ob) - 1) + ob

_template = None
def load(name, artic=0, **params):
    global _template
    p = pedalboard.load_plugin(PLUG)
    if _template is None: _template = p.raw_state
    p.raw_state = build_state(_template, select_artic(nks_xml(name), artic))
    for k, v in params.items(): setattr(p, k, v)
    return p

def current_name(p):
    _, c = parse_state(p.raw_state)
    m = re.search(rb'<META[^>]*name="([^"]+)"', c); a = re.findall(rb'a_name" value="([^"]+)"[^<]*<SETTING id="a_version"[^<]*<SETTING id="a_templateIdx"[^<]*<SETTING id="layerIdx"[^<]*<SETTING id="a_voiceLimit"[^<]*<SETTING id="a_odest"[^<]*<SETTING id="a_active" value="(\d)"', c)
    return m.group(1).decode() if m else None, a
