import {render} from './lib.mjs';
const W=1920,H=1080;
const P={ink:'#0d0a12', hood:'#f2b51e', hoodSh:'#c98a10', rim:'#ffb35a', win:'#ffc978', bld:'#2a2036', bld2:'#1f1829', white:'#fff6e8', acc:'#ffc93c'};
const defs=`<defs>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#231c38"/><stop offset="0.45" stop-color="#5b3f72"/><stop offset="0.75" stop-color="#b8687a"/><stop offset="1" stop-color="#f2a66a"/></linearGradient>
 <radialGradient id="sun" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff1c8" stop-opacity="1"/><stop offset="0.25" stop-color="#ffd08a" stop-opacity="0.8"/><stop offset="1" stop-color="#ff9a5a" stop-opacity="0"/></radialGradient>
 <radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="0.5" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.7"/></radialGradient>
 <linearGradient id="grd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a2a44"/><stop offset="1" stop-color="#140f1c"/></linearGradient>
 <linearGradient id="room" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2b2140"/><stop offset="1" stop-color="#1a1428"/></linearGradient>
 <linearGradient id="title" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff3d6"/><stop offset="1" stop-color="#ffb84d"/></linearGradient>
 <filter id="b8"><feGaussianBlur stdDeviation="8"/></filter><filter id="b20" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter><filter id="b50" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="50"/></filter><filter id="b3"><feGaussianBlur stdDeviation="3"/></filter>
 <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.045 0"/></filter>
 <filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000" flood-opacity="0.6"/></filter>
</defs>`;
const fin=(w,h,lb=true)=>`<rect width="${w}" height="${h}" fill="url(#vig)"/><rect width="${w}" height="${h}" filter="url(#grain)"/>`+(lb?`<rect width="${w}" height="${h*0.11}" fill="#000"/><rect y="${h*0.89}" width="${w}" height="${h*0.11}" fill="#000"/>`:'');
function rnd(seed){let s=seed;return()=>((s=(s*9301+49297)%233280)/233280);}
function city(y0,seed,col,scale=1,lit=0.5){const r=rnd(seed);let s='',x=-40;while(x<W+40){const w=(70+r()*130)*scale,h=(120+r()*260)*scale;s+=`<rect x="${x}" y="${y0-h}" width="${w}" height="${h+400}" fill="${col}"/>`;for(let wy=y0-h+18*scale;wy<y0-20;wy+=34*scale)for(let wx=x+12*scale;wx<x+w-20*scale;wx+=26*scale){if(r()<lit)s+=`<rect x="${wx}" y="${wy}" width="${12*scale}" height="${16*scale}" fill="${P.win}" opacity="${0.5+r()*0.5}"/>`;}x+=w+4;}return s;}
function bokeh(n,seed,area){const r=rnd(seed);let s='';for(let i=0;i<n;i++){s+=`<circle cx="${area[0]+r()*area[2]}" cy="${area[1]+r()*area[3]}" r="${10+r()*45}" fill="${r()<0.5?'#ffd28a':'#c9a0ff'}" opacity="${0.06+r()*0.14}"/>`;}return s;}
// hero: black stickman, yellow hoodie, white decal face, rim light on right
function heroBust(cx,cy,r,face,opts={}){ // cx,cy head centre
 const body=`<path d="M${cx-r*1.15} ${cy+r*3} C${cx-r*1.2} ${cy+r*1.6} ${cx-r*0.8} ${cy+r*1.05} ${cx} ${cy+r*1.0} C${cx+r*0.8} ${cy+r*1.05} ${cx+r*1.2} ${cy+r*1.6} ${cx+r*1.15} ${cy+r*3}Z"`;
 const hood=`<path d="M${cx-r*0.78} ${cy+r*1.12} C${cx-r*1.16} ${cy+r*0.4} ${cx-r*1.12} ${cy-r*0.9} ${cx} ${cy-r*1.1} C${cx+r*1.12} ${cy-r*0.9} ${cx+r*1.16} ${cy+r*0.4} ${cx+r*0.78} ${cy+r*1.12}Z"`;
 let s='';
 // rim layer
 s+=`<g transform="translate(${r*0.04} ${-r*0.02})">${body} fill="${P.rim}"/>${hood} fill="${P.rim}"/><circle cx="${cx}" cy="${cy}" r="${r}" fill="${P.rim}"/></g>`;
 s+=`${hood} fill="${P.hoodSh}"/>${body} fill="${P.hood}"/>`;
 s+=`<path d="M${cx-r*0.25} ${cy+r*1.05} C${cx-r*0.28} ${cy+r*1.6} ${cx-r*0.3} ${cy+r*1.9} ${cx-r*0.32} ${cy+r*2.1}" stroke="${P.white}" stroke-width="${r*0.05}" fill="none" stroke-linecap="round"/><path d="M${cx+r*0.25} ${cy+r*1.05} C${cx+r*0.28} ${cy+r*1.6} ${cx+r*0.3} ${cy+r*1.9} ${cx+r*0.3} ${cy+r*2.05}" stroke="${P.white}" stroke-width="${r*0.05}" fill="none" stroke-linecap="round"/>`;
 s+=`<path d="M${cx-r*1.0} ${cy+r*1.7} C${cx-r*0.9} ${cy+r*1.5} ${cx-r*0.8} ${cy+r*1.4} ${cx-r*0.6} ${cy+r*1.35}" stroke="${P.hoodSh}" stroke-width="${r*0.06}" fill="none" opacity="0.6"/>`;
 s+=`<rect x="${cx-r*0.18}" y="${cy+r*0.8}" width="${r*0.36}" height="${r*0.35}" fill="${P.ink}"/><circle cx="${cx}" cy="${cy}" r="${r}" fill="${P.ink}"/>`;
 s+=decal(cx,cy,r,face,opts.dir||0);
 return s;}
function decal(cx,cy,r,face,dir){const o=dir*r*0.25,k=r/100,Wc=P.white;const ex1=cx+o-30*k,ex2=cx+o+30*k,ey=cy-5*k;
 const L=(d,w=6)=>`<path d="${d}" fill="none" stroke="${Wc}" stroke-width="${w*k}" stroke-linecap="round"/>`;
 if(face==='smug') return `<path d="M${ex1-14*k} ${ey} A${14*k} ${12*k} 0 0 0 ${ex1+14*k} ${ey}Z" fill="${Wc}"/><path d="M${ex2-14*k} ${ey} A${14*k} ${12*k} 0 0 0 ${ex2+14*k} ${ey}Z" fill="${Wc}"/>`+L(`M${ex1-18*k} ${ey} L${ex1+16*k} ${ey}`,6)+L(`M${ex2-16*k} ${ey} L${ex2+18*k} ${ey-2*k}`,6)+`<circle cx="${ex1+3*k}" cy="${ey+5*k}" r="${4*k}" fill="${P.ink}"/><circle cx="${ex2+3*k}" cy="${ey+5*k}" r="${4*k}" fill="${P.ink}"/>`+L(`M${cx+o-18*k} ${cy+38*k} Q${cx+o+4*k} ${cy+48*k} ${cx+o+24*k} ${cy+30*k}`,6);
 if(face==='bored') return L(`M${ex1-14*k} ${ey} L${ex1+14*k} ${ey}`,7)+L(`M${ex2-14*k} ${ey} L${ex2+14*k} ${ey}`,7)+`<path d="M${ex1-12*k} ${ey} A${12*k} ${8*k} 0 0 0 ${ex1+12*k} ${ey}Z M${ex2-12*k} ${ey} A${12*k} ${8*k} 0 0 0 ${ex2+12*k} ${ey}Z" fill="${Wc}"/>`+L(`M${cx+o-14*k} ${cy+40*k} L${cx+o+14*k} ${cy+38*k}`,6);
 return '';}
function remote(x,y,s,rot=-20){return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})"><circle cx="0" cy="-24" r="60" fill="#ffb100" opacity="0.55" filter="url(#b20)"/>
 <rect x="-22" y="-56" width="44" height="104" rx="14" fill="#1c1824"/><rect x="-22" y="-56" width="44" height="104" rx="14" fill="none" stroke="${P.rim}" stroke-width="2.5" opacity="0.7"/>
 <circle cx="0" cy="-24" r="14" fill="${P.acc}"/><path d="M-8 -31 L0 -24 L-8 -17Z M0 -31 L8 -24 L0 -17Z" fill="#1c1824"/>
 <circle cx="-9" cy="8" r="4.5" fill="#3a3346"/><circle cx="9" cy="8" r="4.5" fill="#3a3346"/><circle cx="-9" cy="26" r="4.5" fill="#3a3346"/><circle cx="9" cy="26" r="4.5" fill="#3a3346"/></g>`;}
function mitten(x,y,r){return `<circle cx="${x+r*0.12}" cy="${y-r*0.05}" r="${r}" fill="${P.rim}"/><circle cx="${x}" cy="${y}" r="${r}" fill="${P.ink}"/>`;}
const T=(x,y,s,size,fill,anchor='middle',extra='')=>`<text x="${x}" y="${y}" font-family="Nunito" font-weight="900" font-size="${size}" fill="${fill}" text-anchor="${anchor}" ${extra}>${s}</text>`;

// 1) WIDE: school at dusk + title card
let w1=defs+`<rect width="${W}" height="${H}" fill="url(#sky)"/><circle cx="960" cy="610" r="380" fill="url(#sun)"/>`+`<g opacity="0.55">${city(760,7,'#4a3558',0.8,0.25)}</g>`+bokeh(18,3,[0,300,W,500]);
w1+=`<rect x="520" y="430" width="880" height="370" fill="${P.bld}"/><polygon points="500,430 960,330 1420,430" fill="${P.bld2}"/><rect x="900" y="300" width="120" height="70" fill="${P.bld2}"/><circle cx="960" cy="410" r="20" fill="#3b2f4a" stroke="${P.win}" stroke-width="4"/>`;
for(let r=0;r<3;r++)for(let c=0;c<8;c++){const x=560+c*104,y=470+r*100,lit=!(r===2&&c===3);w1+=`<rect x="${x}" y="${y}" width="70" height="66" fill="${lit?P.win:'#2f2540'}" opacity="${lit?0.95:1}"/>${lit?`<rect x="${x-10}" y="${y-10}" width="90" height="86" fill="${P.win}" opacity="0.25" filter="url(#b8)"/>`:''}<line x1="${x+35}" y1="${y}" x2="${x+35}" y2="${y+66}" stroke="${P.bld}" stroke-width="4"/>`;}
// tiny hero silhouette in window
w1+=`<circle cx="1000" cy="640" r="12" fill="${P.ink}"/><rect x="990" y="652" width="20" height="18" fill="${P.hood}"/>`;
w1+=`<rect x="0" y="800" width="${W}" height="${H-800}" fill="url(#grd)"/><path d="M0 800 L${W} 800" stroke="#f2a66a" stroke-width="3" opacity="0.5"/>`;
w1+=`<g fill="${P.ink}"><rect x="300" y="560" width="10" height="240"/><circle cx="305" cy="560" r="16" fill="${P.win}" filter="url(#b8)"/><path d="M1600 800 L1600 640 M1600 650 C1540 600 1560 540 1600 540 C1660 540 1670 610 1600 650" stroke="${P.ink}" stroke-width="12" fill="${P.ink}"/></g>`;
w1+=`<g filter="url(#sh)">`+T(W/2,240,'WHAT IF YOU COULD SKIP',84,'url(#title)','middle','letter-spacing="3"')+T(W/2,340,'THE BORING PARTS?',104,'url(#title)','middle','letter-spacing="3"')+`</g>`+T(W/2,400,'AN  IF TOON  WHAT IF',26,'#e8d8c8','middle','letter-spacing="6" font-weight="700"');
w1+=fin(W,H); await render(w1,W,H,'ifv_wide.jpg');

// 2) MEDIUM CLOSE-UP in classroom at dusk + HUD
let w2=defs+`<rect width="${W}" height="${H}" fill="url(#room)"/>`;
w2+=`<rect x="120" y="150" width="900" height="560" fill="url(#sky)"/><circle cx="560" cy="640" r="300" fill="url(#sun)"/><g opacity="0.7"><svg x="120" y="150" width="900" height="560" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">${city(1000,11,'#4a3558',1,0.3)}</svg></g>`;
w2+=`<path d="M120 150 h900 v560 h-900Z M570 150 v560 M120 430 h900" fill="none" stroke="#14101d" stroke-width="22"/><polygon points="120,710 1020,710 1420,${H} -200,${H}" fill="#ffb87a" opacity="0.10"/>`;
w2+=`<rect x="1250" y="210" width="560" height="320" fill="#1b2a24" stroke="#120e18" stroke-width="16"/><path d="M1300 280 q40 -20 80 0 t80 0 M1300 350 h160 M1500 350 h120 M1300 420 q50 -24 100 0" stroke="#5f7466" stroke-width="5" fill="none"/>`;
w2+=bokeh(14,5,[0,100,W,800]);
w2+=`<rect x="0" y="880" width="${W}" height="200" fill="#120e18"/><path d="M0 880 h${W}" stroke="#ffb87a" stroke-width="3" opacity="0.4"/>`;
w2+=heroBust(1180,560,175,'smug',{dir:-1});
w2+=`<path d="M1010 910 C960 820 900 720 860 640" stroke="${P.hood}" stroke-width="74" stroke-linecap="round" fill="none"/><path d="M1010 910 C960 820 900 720 860 640" stroke="${P.hoodSh}" stroke-width="10" stroke-linecap="round" fill="none" opacity="0.5" transform="translate(-24 6)"/>`;
w2+=remote(830,560,1.6,-15)+mitten(842,618,42);
// HUD
w2+=`<g transform="translate(1520 190)"><circle cx="0" cy="0" r="44" fill="none" stroke="${P.white}" stroke-width="5" opacity="0.85"/><rect x="-8" y="-62" width="16" height="12" fill="${P.white}"/><line x1="0" y1="0" x2="26" y2="-20" stroke="${P.acc}" stroke-width="5" stroke-linecap="round"/></g>`;
w2+=T(1600,175,'10:14',46,P.white,'start')+T(1600,230,'→ 15:30',54,P.acc,'start');
w2+=fin(W,H); await render(w2,W,H,'ifv_closeup.jpg');

// 3) THUMB
const TW=1280,TH=720;
let t=defs+`<rect width="${TW}" height="${TH}" fill="url(#sky)"/><circle cx="420" cy="560" r="330" fill="url(#sun)"/><g opacity="0.6" transform="scale(0.667)">${city(1080,21,'#4a3558',1,0.3)}</g>`+bokeh(14,9,[0,0,TW,TH]);
// speed streak + ghost clocks
t+=`<g opacity="0.9"><path d="M0 470 L520 452" stroke="#ffd08a" stroke-width="10" opacity="0.4" filter="url(#b3)"/></g>`;
t+=heroBust(930,420,215,'smug',{dir:-1});
t+=`<path d="M780 760 C730 650 640 600 540 550" stroke="${P.hood}" stroke-width="90" stroke-linecap="round" fill="none"/>`;
t+=remote(500,470,2.4,-18)+mitten(526,552,54);
t+=`<g filter="url(#sh)">`+T(48,170,'LIFE',150,P.white,'start')+T(48,320,'SKIPPED.',150,P.acc,'start')+`</g>`;
t+=fin(TW,TH,false); await render(t,TW,TH,'ifv_thumb.jpg');
