# Baepsae v2: simple, soft, "하찮은" sticker style (hand-drawn line or soft flat)
INK="#2B2324"
BODY="M300 150 C398 148 474 214 478 312 C482 410 420 464 300 466 C180 464 118 410 122 312 C126 214 202 152 300 150Z"
def bird(pose="default", uid="a", style="line", sticker=True):
    u=uid; line = style=="line"
    sw = 7 if line else 0
    stroke = f'stroke="{INK}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"' if line else 'stroke="none"'
    # eyes / beak by pose
    E={"default":(f'<circle cx="256" cy="312" r="10" fill="{INK}"/><circle cx="344" cy="312" r="10" fill="{INK}"/>', f'<path d="M293 324 L307 324 L300 334Z" fill="{INK}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'),
       "happy":(f'<g fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"><path d="M244 316 Q256 302 268 316"/><path d="M332 316 Q344 302 356 316"/></g>', f'<path d="M292 324 Q300 321 308 324 Q305 340 300 341 Q295 340 292 324Z" fill="{INK}"/>'),
       "surprised":(f'<circle cx="256" cy="310" r="13" fill="{INK}"/><circle cx="344" cy="310" r="13" fill="{INK}"/><circle cx="252" cy="306" r="3.5" fill="#fff"/><circle cx="340" cy="306" r="3.5" fill="#fff"/>', f'<ellipse cx="300" cy="336" rx="8" ry="10" fill="{INK}"/>'),
       "wrong":(f'<g fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"><path d="M246 302 L264 312 L246 322"/><path d="M354 302 L336 312 L354 322"/></g>', f'<path d="M293 326 L307 326 L300 335Z" fill="{INK}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'),
       "thinking":(f'<circle cx="262" cy="306" r="10" fill="{INK}"/><circle cx="350" cy="306" r="10" fill="{INK}"/>', f'<path d="M299 320 L313 320 L306 330Z" fill="{INK}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'),
       "sleepy":(f'<g fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"><path d="M246 312 L266 312"/><path d="M334 312 L354 312"/></g>', f'<path d="M293 324 L307 324 L300 333Z" fill="{INK}"/>')}
    eyes,beak=E.get(pose,E["default"])
    extra={"surprised":f'<g stroke="{INK}" stroke-width="6" stroke-linecap="round"><path d="M404 150 l14 -26"/><path d="M432 168 l26 -14"/><path d="M196 150 l-14 -26"/></g>',
           "happy":'<path d="M440 150 c-14 -18 -38 -2 -20 16 l20 18 l20 -18 c18 -18 -6 -34 -20 -16z" fill="#FF8FA8" transform="rotate(14 440 160)"/>',
           "wrong":'<path d="M438 168 Q452 190 452 200 A14 14 0 0 1 424 200 Q424 190 438 168Z" fill="#8FD0FF"/>',
           "thinking":f'<text x="420" y="178" font-family="Jua" font-size="86" fill="{INK}">?</text>',
           "sleepy":f'<text x="410" y="170" font-family="Jua" font-size="60" fill="{INK}">z</text><text x="446" y="130" font-family="Jua" font-size="44" fill="{INK}">z</text>'}.get(pose,"")
    # wings: small dark nubs low on sides, with rosy-brown shoulder; raised wing for happy
    wl = 'M132 352 C118 366 116 396 128 410 C140 402 146 380 142 356Z'
    wr = 'M468 352 C482 366 484 396 472 410 C460 402 454 380 458 356Z'
    if pose=="happy": wr='M468 312 C496 292 512 266 506 248 C488 256 470 280 462 300Z'
    if pose=="surprised": wl='M132 312 C104 292 88 266 94 248 C112 256 130 280 138 300Z'; wr='M468 312 C496 292 512 266 506 248 C488 256 470 280 462 300Z'
    wings = f'<g fill="{INK}" {stroke}><path d="{wl}"/><path d="{wr}"/></g>'
    shoulder = f'<g fill="#C9A99D"><path d="M128 330 C130 312 138 300 148 296 C152 316 150 338 140 356 C132 350 128 342 128 330Z"/><path d="M472 330 C470 312 462 300 452 296 C448 316 450 338 460 356 C468 350 472 342 472 330Z"/></g>' if pose not in ("happy","surprised") else ''
    tail = f'<g fill="{INK}"><path d="M396 430 C430 452 462 480 486 512 C468 512 438 494 392 452Z"/><path d="M404 424 C444 438 478 458 506 484 C486 488 452 476 400 446Z"/><path d="M390 440 C414 470 434 504 446 536 C430 530 406 506 384 456Z"/></g>'
    feet = f'<g stroke="{INK}" stroke-width="5" stroke-linecap="round" fill="none"><path d="M270 462 l-4 22 m0 0 l-12 6 m12 -6 l2 10 m-2 -10 l12 4"/><path d="M330 462 l4 22 m0 0 l12 6 m-12 -6 l-2 10 m2 -10 l-12 4"/></g>'
    fluff = f'<g stroke="{INK}" stroke-width="5" stroke-linecap="round" fill="none"><path d="M166 430 l-10 8"/><path d="M180 442 l-6 10"/><path d="M432 434 l9 9"/></g>' if line else ''
    tuft = f'<path d="M292 152 C288 134 296 124 304 128 C300 136 302 144 310 150" fill="#fff" {stroke if line else ""} stroke-width="5"/>'
    blush = '<g fill="#FFB2C1" opacity=".75"><ellipse cx="232" cy="338" rx="20" ry="10"/><ellipse cx="368" cy="338" rx="20" ry="10"/></g>'
    wob = f'filter="url(#wob{u})"' if line else ''
    st = ''
    if sticker:
        st = f'''<g filter="url(#ss{u})"><path d="{BODY}" fill="#fff" stroke="#fff" stroke-width="54" stroke-linejoin="round"/>
        <g fill="#fff" stroke="#fff" stroke-width="44" stroke-linejoin="round"><path d="M396 430 C430 452 462 480 486 512 C468 512 438 494 392 452Z"/><path d="M404 424 C444 438 478 458 506 484 C486 488 452 476 400 446Z"/><path d="M390 440 C414 470 434 504 446 536 C430 530 406 506 384 456Z"/><ellipse cx="300" cy="470" rx="62" ry="22"/></g>
        <g fill="#fff" stroke="#fff" stroke-width="40" stroke-linejoin="round"><path d="{wl}"/><path d="{wr}"/></g></g>'''
    bodyfill = "#fff" if line else f"url(#sh{u})"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="40 60 520 520" width="520" height="520">
<defs>
 <filter id="wob{u}" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="1" seed="4"/><feDisplacementMap in="SourceGraphic" scale="5"/></filter>
 <filter id="ss{u}" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#6b4f48" flood-opacity=".22"/></filter>
 <radialGradient id="sh{u}" cx="45%" cy="35%" r="70%"><stop offset=".7" stop-color="#fff"/><stop offset="1" stop-color="#F1EBE8"/></radialGradient>
</defs>
{st}
<g {wob}>
 {tail}{feet}
 <path d="{BODY}" fill="{bodyfill}" {stroke}/>
 {tuft}{shoulder}{wings}{fluff}
</g>
{blush}{eyes}{beak}
<g {wob}>{extra}</g>
</svg>'''
