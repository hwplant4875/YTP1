# Korean shorthair cheese cat (치즈냥이) mascot, simple sticker style
INK="#2B2324"; FUR="#F6B66E"; STR="#E08A3C"; CREAM="#FFF6EA"
HEAD="M300 166 C390 166 452 214 456 280 C460 346 394 388 300 388 C206 388 140 346 144 280 C148 214 210 166 300 166Z"
BODYP="M218 352 C208 410 214 456 238 478 L362 478 C386 456 392 410 382 352Z"
EARL="M172 236 C164 196 170 152 184 128 C190 120 198 120 204 126 C226 148 246 172 256 192 C222 198 194 214 172 236Z"
EARR="M428 236 C436 196 430 152 416 128 C410 120 402 120 396 126 C374 148 354 172 344 192 C378 198 406 214 428 236Z"
EARLI="M190 212 C188 186 192 162 198 148 C214 164 226 180 232 194 C214 198 200 204 190 212Z"
EARRI="M410 212 C412 186 408 162 402 148 C386 164 374 180 368 194 C386 198 400 204 410 212Z"
TAIL="M370 456 C424 466 452 436 450 396 C448 362 436 338 418 322"
def cat(pose="default", uid="a", sticker=True):
    u=uid
    sk=f'stroke="{INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"'
    eyes={"default":f'<ellipse cx="248" cy="282" rx="10" ry="12" fill="{INK}"/><ellipse cx="352" cy="282" rx="10" ry="12" fill="{INK}"/><circle cx="245" cy="277" r="3.2" fill="#fff"/><circle cx="349" cy="277" r="3.2" fill="#fff"/>',
          "happy":f'<g fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"><path d="M234 288 Q248 272 262 288"/><path d="M338 288 Q352 272 366 288"/></g>',
          "surprised":f'<circle cx="248" cy="280" r="15" fill="{INK}"/><circle cx="352" cy="280" r="15" fill="{INK}"/><circle cx="243" cy="274" r="5" fill="#fff"/><circle cx="347" cy="274" r="5" fill="#fff"/>',
          "wrong":f'<g fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"><path d="M236 272 L256 282 L236 292"/><path d="M364 272 L344 282 L364 292"/></g>',
          "thinking":f'<ellipse cx="256" cy="276" rx="10" ry="12" fill="{INK}"/><ellipse cx="360" cy="276" rx="10" ry="12" fill="{INK}"/>',
          "sleepy":f'<g fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"><path d="M236 284 Q248 292 260 284"/><path d="M340 284 Q352 292 364 284"/></g>'}[pose]
    nose=f'<path d="M292 304 Q300 300 308 304 Q305 312 300 314 Q295 312 292 304Z" fill="#F58A9B" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
    mouth={"surprised":f'<ellipse cx="300" cy="332" rx="10" ry="12" fill="{INK}"/><ellipse cx="300" cy="337" rx="5" ry="5" fill="#FF8FA3"/>',
           "happy":f'<path d="M286 318 Q293 328 300 318 Q307 328 314 318" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/><path d="M290 324 Q300 350 310 324Z" fill="#FF8FA3" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>',
           "wrong":f'<path d="M288 332 Q300 322 312 332" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'}.get(pose,f'<path d="M286 318 Q293 328 300 318 Q307 328 314 318" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>')
    whisk=f'<g stroke="{INK}" stroke-width="3.5" stroke-linecap="round" opacity=".8"><path d="M196 304 L150 296"/><path d="M196 316 L152 320"/><path d="M404 304 L450 296"/><path d="M404 316 L448 320"/></g>'
    stripes=f'<g fill="{STR}"><path d="M288 168 Q300 196 312 168Z"/><path d="M262 172 Q272 196 280 170Z"/><path d="M320 170 Q328 196 338 172Z"/><path d="M146 262 Q172 266 184 276 Q166 278 148 280Z"/><path d="M454 262 Q428 266 416 276 Q434 278 452 280Z"/><path d="M148 290 Q168 292 178 300 Q162 302 150 304Z"/><path d="M452 290 Q432 292 422 300 Q438 302 450 304Z"/></g>'
    extra={"surprised":f'<g stroke="{INK}" stroke-width="6" stroke-linecap="round"><path d="M452 150 l16 -24"/><path d="M470 178 l26 -10"/></g>',
           "happy":'<path d="M470 150 c-14 -18 -38 -2 -20 16 l20 18 l20 -18 c18 -18 -6 -34 -20 -16z" fill="#FF8FA8" transform="rotate(14 470 160)"/>',
           "wrong":'<path d="M454 180 Q468 202 468 212 A14 14 0 0 1 440 212 Q440 202 454 180Z" fill="#8FD0FF"/>',
           "thinking":f'<text x="450" y="170" font-family="Jua" font-size="86" fill="{INK}">?</text>',
           "sleepy":f'<text x="446" y="170" font-family="Jua" font-size="60" fill="{INK}">z</text><text x="482" y="130" font-family="Jua" font-size="44" fill="{INK}">z</text>'}.get(pose,"")
    et=et2=""
    if pose in ("wrong","sleepy"): et=' transform="rotate(-22 210 220)"'; et2=' transform="rotate(22 390 220)"'
    paws=f'<g fill="{CREAM}" {sk}><ellipse cx="262" cy="474" rx="30" ry="18"/><ellipse cx="338" cy="474" rx="30" ry="18"/></g><g stroke="{INK}" stroke-width="4" stroke-linecap="round"><path d="M256 466 l0 10"/><path d="M268 466 l0 10"/><path d="M332 466 l0 10"/><path d="M344 466 l0 10"/></g>'
    if pose=="happy": paws=f'<g fill="{CREAM}" {sk}><ellipse cx="262" cy="474" rx="30" ry="18"/><ellipse cx="380" cy="350" rx="24" ry="28" transform="rotate(-30 380 350)"/></g>'
    blush='<g fill="#FFA7B8" opacity=".75"><ellipse cx="214" cy="316" rx="20" ry="11"/><ellipse cx="386" cy="316" rx="20" ry="11"/></g>'
    st=''
    if sticker:
        st=f'''<g filter="url(#ss{u})" fill="#fff" stroke="#fff" stroke-width="50" stroke-linejoin="round" stroke-linecap="round">
        <path d="{HEAD}"/><path d="{BODYP}"/><g{et}><path d="{EARL}"/></g><g{et2}><path d="{EARR}"/></g><path d="{TAIL}" fill="none" stroke-width="84"/><ellipse cx="300" cy="474" rx="70" ry="22"/><path d="M150 296 L196 310 M450 296 L404 310" stroke-width="40"/></g>'''
    # tail with stripes via dash
    tail=f'<path d="{TAIL}" fill="none" stroke="{INK}" stroke-width="40" stroke-linecap="round"/><path d="{TAIL}" fill="none" stroke="{FUR}" stroke-width="26" stroke-linecap="round"/><path d="{TAIL}" fill="none" stroke="{STR}" stroke-width="26" stroke-dasharray="10 22" stroke-dashoffset="-8"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="60 60 480 480" width="520" height="520">
<defs><filter id="ss{u}" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#6b4f48" flood-opacity=".22"/></filter>
<clipPath id="hc{u}"><path d="{HEAD}"/></clipPath></defs>
{st}{tail}
<path d="{BODYP}" fill="{FUR}" {sk}/>
<path d="M258 388 C258 432 268 470 300 474 C332 470 342 432 342 388Z" fill="{CREAM}"/>
{paws}
<g{et}><path d="{EARL}" fill="{FUR}" {sk}/><path d="{EARLI}" fill="#FFC2CF"/></g>
<g{et2}><path d="{EARR}" fill="{FUR}" {sk}/><path d="{EARRI}" fill="#FFC2CF"/></g>
<path d="{HEAD}" fill="{FUR}"/>
<g clip-path="url(#hc{u})">{stripes}<ellipse cx="300" cy="334" rx="74" ry="50" fill="{CREAM}"/></g>
<path d="{HEAD}" fill="none" {sk}/>
{blush}{whisk}<g class="eyes">{eyes}</g>{nose}{mouth}{extra}
</svg>'''
