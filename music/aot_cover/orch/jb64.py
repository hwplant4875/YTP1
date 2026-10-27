import re
CH = ".ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+"
def jdec(s):
    size, data = s.split('.',1)
    size=int(size); out=bytearray(size); bit=0
    for c in data:
        v=CH.index(c)
        for i in range(6):
            if bit>=size*8: break
            if v>>i & 1: out[bit>>3] |= 1<<(bit&7)
            bit+=1
    return bytes(out)
def jenc(b):
    n=len(b)*8; out=[]; bit=0
    while bit<n:
        v=0
        for i in range(6):
            if bit+i<n and (b[(bit+i)>>3]>>((bit+i)&7))&1: v|=1<<i
        out.append(CH[v]); bit+=6
    return f"{len(b)}."+''.join(out)
def parse_state(raw):
    x=raw[8:].decode('utf-8','replace')
    m=re.search(r'<IComponent>(.*?)</IComponent>',x,re.S)
    return x, jdec(m.group(1).strip())
