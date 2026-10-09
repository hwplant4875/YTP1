# Jindo dog mascot, simple sticker style
INK="#2B2324"
HEAD="M300 156 C386 156 444 202 450 262 C456 312 470 336 448 350 C420 378 368 390 300 390 C232 390 180 378 152 350 C130 336 144 312 150 262 C156 202 214 156 300 156Z"
BODYP="M214 350 C206 410 212 456 236 478 L364 478 C388 456 394 410 386 350Z"
EARL="M168 222 C160 180 166 136 182 112 C190 104 198 104 206 110 C230 128 248 150 258 172 C226 180 192 198 168 222Z"
EARR="M432 222 C440 180 434 136 418 112 C410 104 402 104 394 110 C370 128 352 150 342 172 C374 180 408 198 432 222Z"
EARLI="M186 200 C184 172 188 146 196 132 C212 144 226 160 234 174 C214 180 198 188 186 200Z"
EARRI="M414 200 C416 172 412 146 404 132 C388 144 374 160 366 174 C386 180 402 188 414 200Z"
TAIL="M380 430 C446 440 484 396 474 350 C466 312 422 306 410 336 C402 358 426 372 440 356"
def dog(pose="default", uid="a", coat="white", sticker=True):
    u=uid; fur = "#FBF1E2" if coat=="white" else "#EFC896"
    sk=f'stroke="{INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"'
    eyes={"default":f'<ellipse cx="248" cy="270" rx="10" ry="11" fill="{INK}"/><ellipse cx="352" cy="270" rx="10" ry="11" fill="{INK}"/><circle cx="245" cy="266" r="3" fill="#fff"/><circle cx="349" cy="266" r="3" fill="#fff"/>',
          "happy":f'<g fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"><path d="M234 276 Q248 260 262 276"/><path d="M338 276 Q352 260 366 276"/></g>',
          "surprised":f'<circle cx="248" cy="268" r="14" fill="{INK}"/><circle cx="352" cy="268" r="14" fill="{INK}"/><circle cx="243" cy="262" r="4.5" fill="#fff"/><circle cx="347" cy="262" r="4.5" fill="#fff"/>',
          "wrong":f'<g fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"><path d="M236 260 L256 270 L236 280"/><path d="M364 260 L344 270 L364 280"/></g>',
          "thinking":f'<ellipse cx="256" cy="264" rx="10" ry="11" fill="{INK}"/><ellipse cx="360" cy="264" rx="10" ry="11" fill="{INK}"/>',
          "sleepy":f'<g fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"><path d="M236 272 Q248 280 260 272"/><path d="M340 272 Q352 280 364 272"/></g>'}[pose]
    mouth = {"surprised":f'<ellipse cx="300" cy="330" rx="11" ry="13" fill="{INK}"/><ellipse cx="300" cy="335" rx="6" ry="6" fill="#FF8FA3"/>',
             "happy":f'<path d="M282 318 Q291 330 300 318 Q309 330 318 318" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/><path d="M288 326 Q300 356 312 326Z" fill="#FF8FA3" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>',
             "wrong":f'<path d="M286 330 Q300 320 314 330" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'}.get(pose, f'<path d="M282 318 Q291 330 300 318 Q309 330 318 318" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>')
    nose = f'<ellipse cx="300" cy="300" rx="17" ry="12" fill="{INK}"/><ellipse cx="294" cy="296" rx="5" ry="3" fill="#fff" opacity=".7"/><path d="M300 312 L300 318" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    extra={"surprised":f'<g stroke="{INK}" stroke-width="6" stroke-linecap="round"><path d="M452 140 l16 -24"/><path d="M470 168 l26 -10"/></g>',
           "happy":'<path d="M470 140 c-14 -18 -38 -2 -20 16 l20 18 l20 -18 c18 -18 -6 -34 -20 -16z" fill="#FF8FA8" transform="rotate(14 470 150)"/>',
           "wrong":'<path d="M454 170 Q468 192 468 202 A14 14 0 0 1 440 202 Q440 192 454 170Z" fill="#8FD0FF"/>',
           "thinking":f'<text x="450" y="160" font-family="Jua" font-size="86" fill="{INK}">?</text>',
           "sleepy":f'<text x="446" y="160" font-family="Jua" font-size="60" fill="{INK}">z</text><text x="482" y="120" font-family="Jua" font-size="44" fill="{INK}">z</text>'}.get(pose,"")
    # ears: droop slightly when wrong/sleepy
    el,er=EARL,EARR; eli,eri=EARLI,EARRI; et=""
    if pose in ("wrong","sleepy"): et=' transform="rotate(-18 200 200)"'; et2=' transform="rotate(18 400 200)"'
    else: et2=""
    muzzle = '<ellipse cx="300" cy="318" rx="80" ry="54" fill="#fff"/><path d="M262 386 C270 420 330 420 338 386Z" fill="#fff"/>'
    paws = f'<g fill="{fur}" {sk}><ellipse cx="262" cy="474" rx="30" ry="18"/><ellipse cx="338" cy="474" rx="30" ry="18"/></g><g stroke="{INK}" stroke-width="4" stroke-linecap="round"><path d="M256 466 l0 10"/><path d="M268 466 l0 10"/><path d="M332 466 l0 10"/><path d="M344 466 l0 10"/></g>'
    if pose=="happy": paws = f'<g fill="{fur}" {sk}><ellipse cx="262" cy="474" rx="30" ry="18"/><ellipse cx="372" cy="356" rx="22" ry="28" transform="rotate(-30 372 356)"/></g>'
    blush = '<g fill="#FFB2C1" opacity=".8"><ellipse cx="206" cy="300" rx="20" ry="11"/><ellipse cx="394" cy="300" rx="20" ry="11"/></g>'
    wagg = ' class="tail"'
    st=''
    if sticker:
        st=f'''<g filter="url(#ss{u})" fill="#fff" stroke="#fff" stroke-width="50" stroke-linejoin="round" stroke-linecap="round">
        <path d="{HEAD}"/><path d="{BODYP}"/><g{et}><path d="{el}"/></g><g{et2}><path d="{er}"/></g><path d="{TAIL}" fill="none" stroke-width="80"/><ellipse cx="300" cy="474" rx="70" ry="22"/></g>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="60 50 480 480" width="520" height="520">
<defs><filter id="ss{u}" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#6b4f48" flood-opacity=".22"/></filter></defs>
{st}
<path d="{TAIL}" fill="none" stroke="{INK}" stroke-width="40" stroke-linecap="round"/><path d="{TAIL}" fill="none" stroke="{fur}" stroke-width="26" stroke-linecap="round"/>
<path d="{BODYP}" fill="{fur}" {sk}/>
{'<path d="M262 386 C262 430 270 470 300 474 C330 470 338 430 338 386Z" fill="#fff"/>' }
{paws}
<g{et}><path d="{el}" fill="{fur}" {sk}/><path d="{eli}" fill="#FFC2CF"/></g>
<g{et2}><path d="{er}" fill="{fur}" {sk}/><path d="{eri}" fill="#FFC2CF"/></g>
<path d="{HEAD}" fill="{fur}" {sk}/>
{muzzle}
{blush}<g class="eyes">{eyes}</g>{nose}{mouth}{extra}
</svg>'''
