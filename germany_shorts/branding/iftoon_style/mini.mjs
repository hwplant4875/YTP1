import {chromium} from 'playwright';
import fs from 'fs'; import path from 'path';
const W=1920,H=1080,FPS=30,DUR=20, OUT=process.argv[2]||'mframes', ONLY=process.argv[3]; fs.mkdirSync(OUT,{recursive:true});
const K={bg:'#F3EEE6',bg2:'#FFE3C7',ink:'#1F2A44',grey:'#C9C2B8',hero:'#FFC23D',coral:'#FF6B57',white:'#FFFFFF'};
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)), io=x=>{x=cl(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2}, out=x=>{x=cl(x);return 1-Math.pow(1-x,3)},
 back=x=>{x=cl(x);const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2)}, lerp=(a,b,t)=>a+(b-a)*t, mix=(c1,c2,t)=>{const p=c=>[1,3,5].map(i=>parseInt(c.slice(i,i+2),16));const a=p(c1),b=p(c2);return '#'+a.map((v,i)=>Math.round(lerp(v,b[i],cl(t))).toString(16).padStart(2,'0')).join('')};
const T=(x,y,s,size,fill,w=800,anchor='middle',extra='')=>`<text x="${x}" y="${y}" font-family="Montserrat" font-weight="${w}" font-size="${size}" fill="${fill}" text-anchor="${anchor}" ${extra}>${s}</text>`;
// pictogram person: head circle + capsule body. sc scale, tilt head droop
function person(x,y,sc,col,{droop=0,eyes=false,blink=0,happy=0}={}){const r=34*sc, bw=74*sc, bh=96*sc;
 let s=`<rect x="${x-bw/2}" y="${y-bh}" width="${bw}" height="${bh+30*sc}" rx="${bw/2}" fill="${col}"/>`;
 const hx=x+droop*14*sc, hy=y-bh-r-10*sc+droop*10*sc;
 s+=`<circle cx="${hx}" cy="${hy}" r="${r}" fill="${col}"/>`;
 if(eyes){const ey=hy-2*sc+droop*3*sc; if(happy>0.5) s+=`<path d="M${hx-14*sc} ${ey+2*sc} q6 ${-9*sc} ${12*sc} 0 M${hx+2*sc} ${ey+2*sc} q6 ${-9*sc} ${12*sc} 0" stroke="${K.ink}" stroke-width="${4*sc}" fill="none" stroke-linecap="round"/>`;
  else s+=`<ellipse cx="${hx-9*sc}" cy="${ey}" rx="${4.5*sc}" ry="${4.5*sc*(1-blink)+0.6}" fill="${K.ink}"/><ellipse cx="${hx+9*sc}" cy="${ey}" rx="${4.5*sc}" ry="${4.5*sc*(1-blink)+0.6}" fill="${K.ink}"/>`;}
 return s;}
function desk(x,y,sc,col){return `<rect x="${x-70*sc}" y="${y+4*sc}" width="${140*sc}" height="${14*sc}" rx="${7*sc}" fill="${col}"/>`;}
function clock(x,y,r,mins,{spin=0,col=K.ink}={}){const R=Math.PI/180,mA=(mins%60)/60*360-90,hA=((mins/60)%12)/12*360-90;
 let s=`<circle cx="${x}" cy="${y}" r="${r}" fill="${K.white}" stroke="${col}" stroke-width="${r*0.08}"/>`;
 for(let i=0;i<12;i+=3){const a=i*30*R;s+=`<circle cx="${x+Math.cos(a)*r*0.76}" cy="${y+Math.sin(a)*r*0.76}" r="${r*0.035}" fill="${col}"/>`;}
 if(spin>0){s+=`<path d="M${x} ${y} L${x+Math.cos(mA*R)*r*0.68} ${y+Math.sin(mA*R)*r*0.68} A${r*0.68} ${r*0.68} 0 0 0 ${x+Math.cos((mA-spin)*R)*r*0.68} ${y+Math.sin((mA-spin)*R)*r*0.68}Z" fill="${K.hero}" opacity="0.55"/>`;}
 s+=`<line x1="${x}" y1="${y}" x2="${x+Math.cos(hA*R)*r*0.42}" y2="${y+Math.sin(hA*R)*r*0.42}" stroke="${col}" stroke-width="${r*0.08}" stroke-linecap="round"/><line x1="${x}" y1="${y}" x2="${x+Math.cos(mA*R)*r*0.66}" y2="${y+Math.sin(mA*R)*r*0.66}" stroke="${col}" stroke-width="${r*0.055}" stroke-linecap="round"/><circle cx="${x}" cy="${y}" r="${r*0.06}" fill="${K.coral}"/>`;return s;}
function remote(x,y,sc,press=0,glow=0){return `<g transform="translate(${x} ${y}) scale(${sc})"><rect x="-34" y="-80" width="68" height="160" rx="34" fill="${K.ink}"/>${glow>0?`<circle cx="0" cy="-38" r="${30+glow*16}" fill="${K.hero}" opacity="${0.25*glow}"/>`:''}<circle cx="0" cy="-38" r="${22*(1-press*0.15)}" fill="${K.hero}"/><path d="M-10 -47 L0 -38 L-10 -29Z M0 -47 L10 -38 L0 -29Z" fill="${K.ink}"/><circle cx="0" cy="18" r="7" fill="#3a4766"/><circle cx="0" cy="44" r="7" fill="#3a4766"/></g>`;}
const ring=(x,y,p,col,maxr=900,w=14)=>p>0&&p<1?`<circle cx="${x}" cy="${y}" r="${out(p)*maxr}" fill="none" stroke="${col}" stroke-width="${w*(1-p)}"/>`:'';
function frame(t){
 const bgc=t<8.4?K.bg:t<10.5?mix(K.bg,K.bg2,io((t-8.4)/0.8)):K.bg2; let s=`<rect width="${W}" height="${H}" fill="${bgc}"/>`;
 // --- clock: centre then moves to top-right
 const cm=io((t-2.6)/1.0); const cx=lerp(960,1600,cm), cy=lerp(500,250,cm), cr=lerp(230,95,cm);
 let mins=10*60+14+cl(t/8)*1; let spin=0; if(t>8.4){const p=io((t-8.4)/1.6); mins=lerp(10*60+15,15*60+30,p); spin=t<10?Math.min(300,(t-8.4)*400):0;}
 const clockOut=io((t-14.2)/0.5);
 if(t<15) s+=`<g transform="translate(${cx} ${cy}) scale(${1-clockOut}) translate(${-cx} ${-cy})">${clock(cx,cy,cr,mins,{spin})}</g>`;
 if(t<2.8) s+=`<g opacity="${1-cl((t-2.2)/0.4)}">`+T(960,830,'10:14',64,K.ink,800)+T(960,890,'MATH CLASS',28,K.ink,600,'middle','letter-spacing="8" opacity="0.5"')+`</g>`;
 // --- classroom row
 const seats=[400,680,960,1240,1520]; const rowY=860;
 if(t>2.8&&t<15){ seats.forEach((x,i)=>{const ap=back((t-3.0-i*0.08)/0.5); let gone=0; if(t>10.4) gone=io((t-10.4-i*0.12)/0.35); const sc=ap*(1-(i===2?0:gone)); if(sc<=0.01) return;
   const hero=i===2; const droop=hero?(t<7?0.6+Math.sin(t*1.5)*0.2:0):(0.5+0.5*Math.sin(t*1.2+i)); 
   let ox=0; if(t>8.4&&t<10.1&&!hero) ox=Math.sin((t-8.4)*40+i)*10;
   s+=`<g transform="translate(${x} ${rowY}) scale(${sc}) translate(${-x} ${-rowY})">`+person(x+ox,rowY,1.7,hero?K.hero:K.grey,{droop:hero?droop:droop*0.8,eyes:hero,blink:hero&&((t%3.1)<0.12)?1:0,happy:t>10.9&&t<15?1:0})+desk(x,rowY,1.7,K.ink)+`</g>`;}); }
 // hero bounce when happy
 // --- remote pops at 5.6 next to hero, pressed at 8.2
 if(t>5.6&&t<10.4){const p=back((t-5.6)/0.45), q=io((t-9.9)/0.4); const rx=820, ry=600; const press=t>8.1&&t<8.35?1:0;
   s+=`<g transform="translate(${rx} ${ry}) scale(${p*(1-q)}) translate(${-rx} ${-ry})">${remote(rx,ry,1.15,press,0.5+0.5*Math.sin(t*6))}</g>`;}
 s+=ring(820,556,(t-8.15)/0.8,K.hero,1400,40)+ring(820,556,(t-8.3)/0.8,K.coral,1400,14);
 // fast-forward chevrons
 if(t>8.3&&t<10.2){const o=Math.sin(cl((t-8.3)/1.9)*Math.PI);for(let i=0;i<3;i++){const x=180+i*90, a=0.35+0.65*((Math.floor(t*12)-i)%3===0?1:0);s+=`<path d="M${x} 190 l60 50 l-60 50Z" fill="${K.ink}" opacity="${o*a}"/>`;}}
 // --- 12-15: stat card
 if(t>11.6&&t<15){const a=out((t-11.6)/0.5), b=io((t-12.8)/0.4), c=back((t-13.2)/0.45), z=io((t-14.4)/0.4);
   s+=`<g opacity="${1-z}"><g transform="translate(0 ${(1-a)*40})" opacity="${a}">`+T(960,300,'5 h 16 min',120,K.ink,800)+`</g>`+`<rect x="${960-330}" y="262" width="${660*b}" height="16" rx="8" fill="${K.coral}"/>`+`<g transform="translate(960 400) scale(${c}) translate(-960 -400)">`+`<rect x="760" y="352" width="400" height="96" rx="48" fill="${K.ink}"/>`+T(960,420,'SKIPPED',52,K.hero,800,'middle','letter-spacing="6"')+`</g></g>`;}
 // --- 15-20: title. yellow circle wipe from hero
 if(t>14.6){const w=io((t-14.6)/0.8); s+=`<circle cx="960" cy="560" r="${w*1300}" fill="${K.hero}"/>`;
   const words=[['WHAT IF YOU COULD',90,430],['SKIP',230,640],['THE BORING PARTS?',90,780]];
   words.forEach(([str,size,y],i)=>{const p=out((t-15.3-i*0.22)/0.55);if(p<=0)return;s+=`<svg x="0" y="${y-size}" width="${W}" height="${size*1.25}" overflow="hidden"><g transform="translate(0 ${(1-p)*size*1.2})">`+T(960,size,str,size,K.ink,900,'middle',i===1?'letter-spacing="10"':'letter-spacing="2"')+`</g></svg>`;});
   const sk=io((t-16.4)/0.5); if(sk>0) s+=`<path d="M${960+300} ${545} l60 47 l-60 47Z M${960+360} 545 l60 47 l-60 47Z" fill="${K.coral}" transform="translate(${(1-sk)*-40} 0)" opacity="${sk}"/>`;
   const lg=out((t-17.2)/0.5); s+=`<g opacity="${lg}">`+T(960,930,'IF TOON',34,K.ink,800,'middle','letter-spacing="12" opacity="0.7"')+`</g>`;}
 return s;}
const fd=path.resolve('fonts'),b64=f=>'data:font/ttf;base64,'+fs.readFileSync(path.join(fd,f)).toString('base64');
const html=`<html><head><style>@font-face{font-family:'Montserrat';font-weight:100 900;src:url(${b64('Montserrat.ttf')})}body{margin:0}</style></head><body><svg id="s" xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"></svg></body></html>`;
const br=await chromium.launch(), pg=await br.newPage({viewport:{width:W,height:H}}); await pg.setContent(html); await pg.evaluate(()=>document.fonts.load('800 40px Montserrat'));
for(let f=0;f<DUR*FPS;f++){const t=f/FPS; if(ONLY && !ONLY.split(',').some(x=>Math.abs(t-parseFloat(x))<0.017)) continue;
 await pg.evaluate(b=>{document.getElementById('s').innerHTML=b;},frame(t));
 await pg.screenshot({path:`${OUT}/f${String(f).padStart(4,'0')}.jpg`,type:'jpeg',quality:90});}
await br.close();
