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
 if(face==='unsure') return `<ellipse cx="${ex1}" cy="${ey}" rx="${11*k}" ry="${13*k}" fill="${Wc}"/><ellipse cx="${ex2}" cy="${ey}" rx="${11*k}" ry="${13*k}" fill="${Wc}"/><circle cx="${ex1+dir*3*k}" cy="${ey+3*k}" r="${5*k}" fill="${P.ink}"/><circle cx="${ex2+dir*3*k}" cy="${ey+3*k}" r="${5*k}" fill="${P.ink}"/>`+L(`M${ex1-14*k} ${ey-24*k} L${ex1+12*k} ${ey-28*k}`,5)+L(`M${ex2-12*k} ${ey-28*k} L${ex2+14*k} ${ey-24*k}`,5)+L(`M${cx+o-14*k} ${cy+40*k} Q${cx+o} ${cy+36*k} ${cx+o+14*k} ${cy+42*k}`,6);
 if(face==='joy') return L(`M${ex1-13*k} ${ey+4*k} Q${ex1} ${ey-12*k} ${ex1+13*k} ${ey+4*k}`,7)+L(`M${ex2-13*k} ${ey+4*k} Q${ex2} ${ey-12*k} ${ex2+13*k} ${ey+4*k}`,7)+`<path d="M${cx+o-22*k} ${cy+28*k} Q${cx+o} ${cy+60*k} ${cx+o+22*k} ${cy+28*k}Z" fill="${Wc}"/>`;
 if(face==='shock') return `<circle cx="${ex1}" cy="${ey}" r="${17*k}" fill="${Wc}"/><circle cx="${ex2}" cy="${ey}" r="${17*k}" fill="${Wc}"/><circle cx="${ex1+dir*4*k}" cy="${ey}" r="${6*k}" fill="${P.ink}"/><circle cx="${ex2+dir*4*k}" cy="${ey}" r="${6*k}" fill="${P.ink}"/>`+L(`M${ex1-16*k} ${ey-32*k} Q${ex1} ${ey-40*k} ${ex1+14*k} ${ey-33*k}`,5)+L(`M${ex2-14*k} ${ey-33*k} Q${ex2} ${ey-40*k} ${ex2+16*k} ${ey-32*k}`,5)+`<ellipse cx="${cx+o}" cy="${cy+44*k}" rx="${12*k}" ry="${16*k}" fill="${Wc}"/>`;
 return '';}
function remote(x,y,s,rot=-20){return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})"><circle cx="0" cy="-24" r="60" fill="#ffb100" opacity="0.55" filter="url(#b20)"/>
 <rect x="-22" y="-56" width="44" height="104" rx="14" fill="#1c1824"/><rect x="-22" y="-56" width="44" height="104" rx="14" fill="none" stroke="${P.rim}" stroke-width="2.5" opacity="0.7"/>
 <circle cx="0" cy="-24" r="14" fill="${P.acc}"/><path d="M-8 -31 L0 -24 L-8 -17Z M0 -31 L8 -24 L0 -17Z" fill="#1c1824"/>
 <circle cx="-9" cy="8" r="4.5" fill="#3a3346"/><circle cx="9" cy="8" r="4.5" fill="#3a3346"/><circle cx="-9" cy="26" r="4.5" fill="#3a3346"/><circle cx="9" cy="26" r="4.5" fill="#3a3346"/></g>`;}
function mitten(x,y,r){return `<circle cx="${x+r*0.12}" cy="${y-r*0.05}" r="${r}" fill="${P.rim}"/><circle cx="${x}" cy="${y}" r="${r}" fill="${P.ink}"/>`;}
const T=(x,y,s,size,fill,anchor='middle',extra='')=>`<text x="${x}" y="${y}" font-family="Nunito" font-weight="900" font-size="${size}" fill="${fill}" text-anchor="${anchor}" ${extra}>${s}</text>`;
export {W,H,P,defs,fin,rnd,city,bokeh,heroBust,decal,remote,mitten,T};
