import math, random
# Baepsae (white-headed long-tailed tit) mascot, vector
CX, CY, RX, RY = 300, 332, 206, 214

def _sil(scale=1.0):
    pts=[]
    for i in range(720):
        t=2*math.pi*i/720
        sc=1+0.026*abs(math.sin(8*t))**0.55
        x=CX+RX*scale*sc*math.cos(t); y=CY+RY*scale*sc*(math.sin(t) if math.sin(t)<0 else math.sin(t)*0.98)
        pts.append(f"{x:.1f} {y:.1f}")
    return "M"+" L".join(pts)+"Z"

def _hints(u):
    rnd=random.Random(2); out=[]
    for a in [200,215,230,320,335,350,160,150,30,20,10,185,355]:
        t=math.radians(a); r=0.86
        x=CX+RX*r*math.cos(t); y=CY+RY*r*math.sin(t)
        out.append(f'<path d="M{x-9:.0f} {y:.0f} q9 -8 18 0" />')
    return '<g stroke="#E4D9D4" stroke-width="3" fill="none" stroke-linecap="round" opacity=".8">'+"".join(out)+'</g>'

def _fur(u, seed=5):
    rnd = random.Random(seed)
    out = []
    n = 150
    for i in range(n):
        a = 2*math.pi*i/n + rnd.uniform(-.01, .01)
        if 1.25 < a < 1.9:  # skip bottom (feet/tail area handled by body)
            pass
        r0x, r0y = RX-10, RY-10
        x0, y0 = CX + r0x*math.cos(a), CY + r0y*math.sin(a)
        L = rnd.uniform(14, 26)
        bend = rnd.uniform(-.35, .35)
        x1, y1 = CX + (RX+L)*math.cos(a+bend*0.04), CY + (RY+L)*math.sin(a+bend*0.04)
        mx, my = (x0+x1)/2 + 6*math.cos(a+math.pi/2)*bend, (y0+y1)/2 + 6*math.sin(a+math.pi/2)*bend
        w = rnd.uniform(7, 11)
        out.append(f'<path d="M{x0:.1f} {y0:.1f} Q{mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" stroke-width="{w:.1f}"/>')
    return f'<g stroke="url(#furc{u})" stroke-linecap="round" fill="none">' + "".join(out) + '</g>'

def bird(pose="default", uid="a", bg=True):
    u = uid
    wingL = wingR = 0; extra = ""
    if pose == "default":
        eyes = '''<g fill="#151112"><ellipse cx="250" cy="304" rx="12.5" ry="14.5"/><ellipse cx="350" cy="304" rx="12.5" ry="14.5"/></g>
        <g fill="#fff"><circle cx="246" cy="298.5" r="4.4"/><circle cx="346" cy="298.5" r="4.4"/><circle cx="254" cy="310" r="1.9"/><circle cx="354" cy="310" r="1.9"/></g>'''
        beak = '<path d="M290 322 Q300 318 310 322 L302.5 336 Q300 339 297.5 336 Z" fill="#231c1d"/>'
    elif pose == "surprised":
        eyes = '''<g fill="#151112"><circle cx="248" cy="300" r="18"/><circle cx="352" cy="300" r="18"/></g>
        <g fill="#fff"><circle cx="242" cy="292" r="6.5"/><circle cx="346" cy="292" r="6.5"/><circle cx="254" cy="308" r="2.6"/><circle cx="358" cy="308" r="2.6"/></g>'''
        beak = '<path d="M288 322 Q300 316 312 322 Q306 346 300 348 Q294 346 288 322Z" fill="#231c1d"/><path d="M293 328 Q300 325 307 328 Q304 340 300 341 Q296 340 293 328Z" fill="#ff8fa3"/>'
        extra = '''<g transform="translate(486 112) rotate(14)"><rect x="-12" y="-56" width="24" height="68" rx="12" fill="#FF4F81"/><circle cx="0" cy="36" r="13" fill="#FF4F81"/></g>
        <g stroke="#2B2426" stroke-width="7" stroke-linecap="round" opacity=".8"><path d="M140 118 l-22 -26"/><path d="M176 92 l-6 -32"/></g>'''
        wingL = wingR = 28
    elif pose == "happy":
        eyes = '<g fill="none" stroke="#151112" stroke-width="9" stroke-linecap="round"><path d="M234 308 Q250 288 266 308"/><path d="M334 308 Q350 288 366 308"/></g>'
        beak = '<path d="M287 322 Q300 317 313 322 Q307 344 300 345 Q293 344 287 322Z" fill="#231c1d"/><path d="M292 329 Q300 326 308 329 Q304 339 300 340 Q296 339 292 329Z" fill="#ff8fa3"/>'
        extra = '''<path d="M480 140 l10 24 24 10 -24 10 -10 24 -10 -24 -24 -10 24 -10z" fill="#FFD23F"/><path d="M110 170 l7 16 16 7 -16 7 -7 16 -7 -16 -16 -7 16 -7z" fill="#3DD6B5"/>'''
        wingR = -42
    elif pose == "wrong":
        eyes = '<g fill="none" stroke="#151112" stroke-width="8.5" stroke-linecap="round" stroke-linejoin="round"><path d="M236 292 L262 304 L236 316"/><path d="M364 292 L338 304 L364 316"/></g>'
        beak = '<path d="M290 326 Q300 322 310 326 L302 338 Q300 341 298 338 Z" fill="#231c1d"/>'
        extra = '<path d="M452 166 Q472 198 472 214 A20 20 0 0 1 432 214 Q432 198 452 166Z" fill="#7CC8FF" stroke="#fff" stroke-width="5"/>'
        wingL = wingR = -12
    elif pose == "thinking":
        eyes = '''<g fill="#151112"><ellipse cx="256" cy="298" rx="12.5" ry="14.5"/><ellipse cx="356" cy="298" rx="12.5" ry="14.5"/></g>
        <g fill="#fff"><circle cx="260" cy="291" r="4.4"/><circle cx="360" cy="291" r="4.4"/></g>'''
        beak = '<path d="M294 324 Q303 320 312 324 L305 337 Q303 340 301 337 Z" fill="#231c1d"/>'
        extra = '<text x="474" y="176" font-family="Fredoka, Jua" font-weight="700" font-size="120" fill="#7B6CFF" transform="rotate(12 474 176)">?</text>'
        wingR = -62

    def wing(side, rot):
        cx = CX + side*(196 if rot==0 else 188)
        return f'''<g transform="translate({cx} 420) rotate({rot*side}) scale({side} 1)">
          <path d="M-14 -58 C16 -54 34 -10 30 30 C27 62 8 80 -8 72 C-26 62 -34 20 -30 -18 C-28 -40 -24 -56 -14 -58Z" fill="url(#wing{u})"/>
          <path d="M4 -40 C18 -26 22 0 18 26" stroke="#C7907F" stroke-width="11" fill="none" stroke-linecap="round"/>
          <g stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" opacity=".9"><path d="M-14 12 C-10 34 -4 50 4 60"/><path d="M-22 22 C-18 40 -12 54 -6 64"/></g>
        </g>'''
    body = f'M{CX} {CY-RY} C{CX+RX*0.58} {CY-RY} {CX+RX} {CY-RY*0.56} {CX+RX} {CY+6} C{CX+RX} {CY+RY*0.6} {CX+RX*0.56} {CY+RY} {CX} {CY+RY} C{CX-RX*0.56} {CY+RY} {CX-RX} {CY+RY*0.6} {CX-RX} {CY+6} C{CX-RX} {CY-RY*0.56} {CX-RX*0.58} {CY-RY} {CX} {CY-RY}Z'
    sil=_sil()
    shadow = f'<ellipse cx="300" cy="588" rx="150" ry="18" fill="#7a5c55" opacity=".16" filter="url(#soft2{u})"/>' if bg else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 640" width="600" height="640">
  <defs>
    <radialGradient id="body{u}" cx="40%" cy="30%" r="74%">
      <stop offset="0" stop-color="#FFFFFF"/><stop offset=".6" stop-color="#FCFAF8"/><stop offset=".85" stop-color="#EFE8E4"/><stop offset="1" stop-color="#E2D7D2"/>
    </radialGradient>
    <radialGradient id="furc{u}" cx="40%" cy="30%" r="75%" gradientUnits="userSpaceOnUse" fx="270" fy="220"><stop offset="0" stop-color="#fff"/><stop offset=".7" stop-color="#F7F2EF"/><stop offset="1" stop-color="#E6DCD7"/></radialGradient>
    <linearGradient id="wing{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3d3435"/><stop offset="1" stop-color="#191415"/></linearGradient>
    <linearGradient id="tail{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2c2526"/><stop offset="1" stop-color="#120e0f"/></linearGradient>
    <filter id="soft{u}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="16"/></filter>
    <filter id="soft2{u}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>
    <filter id="drop{u}" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="12" stdDeviation="14" flood-color="#7a5c55" flood-opacity=".20"/></filter>
    <clipPath id="clip{u}"><path d="{sil}"/></clipPath>
  </defs>
  {shadow}
  <g transform="translate(380 488) rotate(-40)">
    <path d="M-13 -20 C-14 40 -18 90 -18 112 Q0 128 18 112 C18 90 14 40 13 -20Z" fill="url(#tail{u})"/>
    <path d="M-16 0 C-18 50 -21 92 -20 108" stroke="#fff" stroke-width="4.5" fill="none" stroke-linecap="round"/>
    <path d="M16 0 C18 50 21 92 20 108" stroke="#fff" stroke-width="4.5" fill="none" stroke-linecap="round"/>
  </g>
  <g stroke="#3a2f2f" stroke-width="7" stroke-linecap="round" fill="none"><path d="M266 538 l-5 34 M261 572 l-15 8 M261 572 l2 13"/><path d="M334 538 l5 34 M339 572 l15 8 M339 572 l-2 13"/></g>
  <g filter="url(#drop{u})">
    <path d="{_sil(1.03)}" fill="#fff" opacity=".7" filter="url(#soft2{u})"/>
    {wing(-1, wingL) if wingL==0 else ''}{wing(1, wingR) if wingR==0 else ''}
    <path d="{sil}" fill="url(#body{u})"/>
    <g clip-path="url(#clip{u})">
      <ellipse cx="128" cy="440" rx="44" ry="74" fill="#E3AA96" opacity=".55" filter="url(#soft{u})"/>
      <ellipse cx="472" cy="440" rx="44" ry="74" fill="#E3AA96" opacity=".55" filter="url(#soft{u})"/>
      <ellipse cx="266" cy="200" rx="110" ry="60" fill="#fff" filter="url(#soft{u})"/>
    </g>
    <g fill="#fff" stroke="#EDE5E1" stroke-width="2"><path d="M286 124 C272 92 292 72 308 84 C298 96 300 108 316 120Z"/><path d="M316 122 C326 96 348 92 354 106 C340 106 332 112 326 126Z"/></g>
    {_hints(u)}
    {wing(-1, wingL) if wingL!=0 else ''}{wing(1, wingR) if wingR!=0 else ''}
  </g>
  <g opacity=".7" filter="url(#soft2{u})"><ellipse cx="214" cy="340" rx="25" ry="12" fill="#FF9DB0"/><ellipse cx="386" cy="340" rx="25" ry="12" fill="#FF9DB0"/></g>
  <g class="eyes" style="transform-box:fill-box;transform-origin:center">{eyes}</g>{beak}<g class="extra">{extra}</g>
</svg>'''
