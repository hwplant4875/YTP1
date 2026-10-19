import {chromium} from 'playwright';
import fs from 'fs'; import path from 'path';
import {W,H,P,defs,fin,rnd,city,bokeh,heroBust,decal,remote,mitten,T} from './ifvlib.mjs';
const FPS=24, OUT=process.argv[2]||'frames', ONLY=process.argv[3]; fs.mkdirSync(OUT,{recursive:true});
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)), e=x=>{x=cl(x);return x<.5?2*x*x:1-Math.pow(-2*x+2,2)/2}, lerp=(a,b,t)=>a+(b-a)*t;
const cam=(s,cx,cy,inner,dx=0,dy=0)=>`<g transform="translate(${cx+dx} ${cy+dy}) scale(${s}) translate(${-cx} ${-cy})">${inner}</g>`;
// ---------- cached backgrounds ----------
function schoolWide(){let w1=`<rect width="${W}" height="${H}" fill="url(#sky)"/><circle cx="960" cy="610" r="380" fill="url(#sun)"/>`+`<g opacity="0.55">${city(760,7,'#4a3558',0.8,0.25)}</g>`+bokeh(18,3,[0,300,W,500]);
 w1+=`<rect x="520" y="430" width="880" height="370" fill="${P.bld}"/><polygon points="500,430 960,330 1420,430" fill="${P.bld2}"/><rect x="900" y="300" width="120" height="70" fill="${P.bld2}"/>`;
 for(let r=0;r<3;r++)for(let c=0;c<8;c++){const x=560+c*104,y=470+r*100,lit=!(r===2&&c===3);w1+=`<rect x="${x}" y="${y}" width="70" height="66" fill="${lit?P.win:'#2f2540'}"/>${lit?`<rect x="${x-10}" y="${y-10}" width="90" height="86" fill="${P.win}" opacity="0.25" filter="url(#b8)"/>`:''}<line x1="${x+35}" y1="${y}" x2="${x+35}" y2="${y+66}" stroke="${P.bld}" stroke-width="4"/>`;}
 w1+=`<circle cx="1000" cy="640" r="12" fill="${P.ink}"/><rect x="990" y="652" width="20" height="14" fill="${P.hood}"/>`;
 w1+=`<rect x="0" y="800" width="${W}" height="${H-800}" fill="url(#grd)"/><path d="M0 800 L${W} 800" stroke="#f2a66a" stroke-width="3" opacity="0.5"/>`;
 w1+=`<g fill="${P.ink}"><rect x="300" y="560" width="10" height="240"/><circle cx="305" cy="560" r="16" fill="${P.win}" filter="url(#b8)"/><path d="M1600 800 L1600 640 M1600 650 C1540 600 1560 540 1600 540 C1660 540 1670 610 1600 650" stroke="${P.ink}" stroke-width="12" fill="${P.ink}"/></g>`;return w1;}
function closeBg(){let w2=`<rect width="${W}" height="${H}" fill="url(#room)"/>`;
 w2+=`<rect x="120" y="150" width="900" height="560" fill="url(#sky)"/><circle cx="560" cy="640" r="300" fill="url(#sun)"/><g opacity="0.7"><svg x="120" y="150" width="900" height="560" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">${city(1000,11,'#4a3558',1,0.3)}</svg></g>`;
 w2+=`<path d="M120 150 h900 v560 h-900Z M570 150 v560 M120 430 h900" fill="none" stroke="#14101d" stroke-width="22"/><polygon points="120,710 1020,710 1420,${H} -200,${H}" fill="#ffb87a" opacity="0.10"/>`;
 w2+=`<rect x="1250" y="210" width="560" height="320" fill="#1b2a24" stroke="#120e18" stroke-width="16"/><path d="M1300 280 q40 -20 80 0 t80 0 M1300 350 h160 M1500 350 h120 M1300 420 q50 -24 100 0" stroke="#5f7466" stroke-width="5" fill="none"/>`;
 w2+=bokeh(14,5,[0,100,W,800])+`<rect x="0" y="880" width="${W}" height="200" fill="#120e18"/><path d="M0 880 h${W}" stroke="#ffb87a" stroke-width="3" opacity="0.4"/>`;return w2;}
function classWide(skyMix=0){ // interior wide: window right, board left, desks
 let s=`<rect width="${W}" height="${H}" fill="url(#room)"/>`;
 s+=`<rect x="1260" y="170" width="560" height="470" fill="url(#sky)"/><rect x="1260" y="170" width="560" height="470" fill="#0b1030" opacity="${skyMix}"/><circle cx="1540" cy="${560+skyMix*200}" r="200" fill="url(#sun)" opacity="${1-skyMix}"/>`;
 s+=`<path d="M1260 170 h560 v470 h-560Z M1540 170 v470 M1260 400 h560" fill="none" stroke="#14101d" stroke-width="18"/>`;
 s+=`<rect x="160" y="200" width="760" height="330" fill="#1b2a24" stroke="#120e18" stroke-width="16"/><path d="M220 270 q40 -20 80 0 t80 0 M220 340 h200 M460 340 h140 M220 410 q50 -24 100 0 M380 410 h220" stroke="#5f7466" stroke-width="5" fill="none"/>`;
 s+=`<rect x="0" y="760" width="${W}" height="${H-760}" fill="#140f1d"/><path d="M0 760 h${W}" stroke="#ffb87a" stroke-width="3" opacity="0.35"/>`;
 return s;}
function clock(x,y,r,hh,mm,ss=null,spin=0){const R=Math.PI/180,a=(mm/60)*360-90+((ss??0)/3600)*360,b=((hh%12)/12+mm/720)*360-90;
 let s=`<circle cx="${x}" cy="${y}" r="${r}" fill="#f4ead8" stroke="#120e18" stroke-width="${r*0.09}"/>`;
 for(let i=0;i<12;i++){const t=i*30*R;s+=`<line x1="${x+Math.cos(t)*r*0.74}" y1="${y+Math.sin(t)*r*0.74}" x2="${x+Math.cos(t)*r*0.86}" y2="${y+Math.sin(t)*r*0.86}" stroke="#2a2036" stroke-width="${r*0.035}" stroke-linecap="round"/>`;}
 if(spin>0) for(let i=1;i<7;i++){const t=(a-i*14)*R;s+=`<line x1="${x}" y1="${y}" x2="${x+Math.cos(t)*r*0.7}" y2="${y+Math.sin(t)*r*0.7}" stroke="#2a2036" stroke-width="${r*0.03}" opacity="${0.35-i*0.05}" stroke-linecap="round"/>`;}
 s+=`<line x1="${x}" y1="${y}" x2="${x+Math.cos(b*R)*r*0.45}" y2="${y+Math.sin(b*R)*r*0.45}" stroke="#1a1424" stroke-width="${r*0.07}" stroke-linecap="round"/><line x1="${x}" y1="${y}" x2="${x+Math.cos(a*R)*r*0.7}" y2="${y+Math.sin(a*R)*r*0.7}" stroke="#1a1424" stroke-width="${r*0.045}" stroke-linecap="round"/>`;
 if(ss!==null){const c=(ss/60)*360-90;s+=`<line x1="${x-Math.cos(c*R)*r*0.15}" y1="${y-Math.sin(c*R)*r*0.15}" x2="${x+Math.cos(c*R)*r*0.78}" y2="${y+Math.sin(c*R)*r*0.78}" stroke="#e0402a" stroke-width="${r*0.018}" stroke-linecap="round"/>`;}
 return s+`<circle cx="${x}" cy="${y}" r="${r*0.05}" fill="#e0402a"/>`;}
function student(x,y,r,col,op=1,face='bored'){ // small seated/standing student bust (back view-ish)
 return `<g opacity="${op}"><path d="M${x-r*1.1} ${y+r*2.6} C${x-r*1.1} ${y+r*1.4} ${x-r*0.6} ${y+r*0.9} ${x} ${y+r*0.9} C${x+r*0.6} ${y+r*0.9} ${x+r*1.1} ${y+r*1.4} ${x+r*1.1} ${y+r*2.6}Z" fill="${col}"/><circle cx="${x}" cy="${y}" r="${r}" fill="${P.ink}"/>${face?decal(x,y,r,face,0):''}</g>`;}
function desk(x,y,w){return `<rect x="${x-w/2}" y="${y}" width="${w}" height="16" rx="4" fill="#3a2c48"/><rect x="${x-w/2+10}" y="${y+16}" width="10" height="${760-y-16}" fill="#2a2036"/><rect x="${x+w/2-20}" y="${y+16}" width="10" height="${760-y-16}" fill="#2a2036"/>`;}
function teacher(x,u,op=1){const ang=Math.sin(u*5)*8;return `<g opacity="${op}"><rect x="${x-34}" y="420" width="68" height="250" rx="34" fill="#3d3550"/><rect x="${x-28}" y="640" width="22" height="120" rx="10" fill="${P.ink}"/><rect x="${x+6}" y="640" width="22" height="120" rx="10" fill="${P.ink}"/><path d="M${x-20} 450 L${x-80} ${380+ang} L${x-120} ${330+ang}" stroke="#3d3550" stroke-width="24" stroke-linecap="round" fill="none"/><circle cx="${x-122}" cy="${328+ang}" r="14" fill="${P.ink}"/><circle cx="${x}" cy="370" r="62" fill="${P.ink}"/></g>`;}
function mina(cx,cy,r,face){ // friend: green cap, cream hoodie
 const body=`<path d="M${cx-r*1.15} ${cy+r*3} C${cx-r*1.2} ${cy+r*1.6} ${cx-r*0.8} ${cy+r*1.05} ${cx} ${cy+r*1.0} C${cx+r*0.8} ${cy+r*1.05} ${cx+r*1.2} ${cy+r*1.6} ${cx+r*1.15} ${cy+r*3}Z"`;
 return `<g transform="translate(${-r*0.04} ${-r*0.02})">${body} fill="${P.rim}"/><circle cx="${cx}" cy="${cy}" r="${r}" fill="${P.rim}"/></g>${body} fill="#e9e2d4"/><path d="M${cx-r*0.3} ${cy+r*1.05} Q${cx} ${cy+r*1.35} ${cx+r*0.3} ${cy+r*1.05}" stroke="#bdb3a3" stroke-width="${r*0.06}" fill="none"/><rect x="${cx-r*0.18}" y="${cy+r*0.8}" width="${r*0.36}" height="${r*0.35}" fill="${P.ink}"/><circle cx="${cx}" cy="${cy}" r="${r}" fill="${P.ink}"/>
 <path d="M${cx-r*0.98} ${cy-r*0.12} C${cx-r*0.95} ${cy-r*1.05} ${cx+r*0.95} ${cy-r*1.05} ${cx+r*0.98} ${cy-r*0.12}Z" fill="#2fa36b"/><path d="M${cx+r*0.6} ${cy-r*0.2} Q${cx+r*1.35} ${cy-r*0.25} ${cx+r*1.55} ${cy-r*0.05} L${cx+r*0.7} ${cy-r*0.02}Z" fill="#23824f"/><circle cx="${cx}" cy="${cy-r*0.98}" r="${r*0.08}" fill="#23824f"/>`+decal(cx,cy+r*0.12,r*0.9,face,1);}
function flash(o){return o>0?`<rect width="${W}" height="${H}" fill="#fff" opacity="${o}"/>`:'';}
function rays(cx,cy,rot,op){let s='';for(let i=0;i<14;i++){const a=(rot+i*360/14)*Math.PI/180,b=a+0.09;s+=`<polygon points="${cx},${cy} ${cx+Math.cos(a)*1600},${cy+Math.sin(a)*1600} ${cx+Math.cos(b)*1600},${cy+Math.sin(b)*1600}" fill="#ffe3b0" opacity="${op}"/>`;}return s;}
const SW=schoolWide(), CB=closeBg(), CW0=classWide(0);
// ---------- shots ----------
const shots=[
 [0,3.4,u=>cam(1+0.12*e(u/3.4),1000,620,SW)],
 [3.4,5.2,u=>cam(1.02+0.04*u,1100,520,`<rect width="${W}" height="${H}" fill="url(#room)"/><g filter="url(#b8)" opacity="0.8"><rect x="80" y="230" width="700" height="360" fill="#1b2a24" stroke="#120e18" stroke-width="16"/>${teacher(560,u)}</g><g filter="url(#sh)">${clock(1180,520,250,10,14,12+Math.floor(u*1.1))}</g>`+bokeh(10,8,[0,0,W,H]))],
 [5.2,7.5,u=>{const up=e(u/0.8),hx=lerp(980,860,up),hy=lerp(1060,640,up),press=u>2.05?0.86:1;
   return cam(1+0.03*u,1100,600,CB+heroBust(1180,560,175,u<1.4?'bored':'smug',{dir:-1})+`<path d="M1010 910 C960 820 ${hx+40} ${hy+120} ${hx} ${hy}" stroke="${P.hood}" stroke-width="74" stroke-linecap="round" fill="none"/>`+`<g transform="translate(${hx-30} ${hy-80}) scale(${press}) translate(${-(hx-30)} ${-(hy-80)})">${remote(hx-30,hy-80,1.6,-15)}</g>`+mitten(hx-18,hy-22,42)+(u>2.05?`<circle cx="${hx-35}" cy="${hy-118}" r="${60+(u-2.05)*600}" fill="none" stroke="${P.acc}" stroke-width="10" opacity="${cl(1-(u-2.05)*4)}"/>`:''));}],
 [7.5,9.0,u=>{const p=e(u/1.5),m=14*60/60+p*(15.5-10.233)*60; const tot=10*60+14+p*(316); const hh=Math.floor(tot/60), mm=tot%60;
   let s=classWide(Math.sin(p*Math.PI)*0.6);
   for(let g=0;g<4;g++){const off=(g-1.5)*40*Math.sin(u*30+g);s+=teacher(520+off+g*60,u*8+g,0.25);}
   const cols=['#4a8fd8','#d8504a','#7a5cff','#2fa36b','#e9e2d4'];
   [[380,600],[700,600],[1020,600],[1340,600]].forEach(([x,y],i)=>{const j=Math.sin(u*40+i)*6;s+=student(x+j,y-90,46,cols[i],0.9,null)+desk(x,y+30,200);});
   s+=student(900,520,60,P.hood,1,'smug')+desk(900,610,220);
   s+=`<g opacity="0.5">${[...Array(16)].map((_,i)=>{const r=rnd(i+1);const y=150+r()*600, x=((u*3000+r()*W*2)%(W+600))-300;return `<line x1="${x}" y1="${y}" x2="${x+300+r()*300}" y2="${y}" stroke="#fff" stroke-width="${2+r()*4}" opacity="0.5"/>`}).join('')}</g>`;
   s+=`<g filter="url(#sh)">${clock(960,250,110,hh,mm,null,1)}</g>`+T(120,210,'▶▶ ×200',64,P.acc,'start');
   return s+flash(cl(1-u/0.3));}],
 [9.0,12.5,u=>{let s=CW0; const walk=u*260; const cols=['#4a8fd8','#d8504a','#7a5cff','#2fa36b'];
   [[380,600],[700,600],[1020,600],[1340,600]].forEach(([x,y],i)=>{s+=desk(x,y+30,200);const sx=x-walk*(1+i*0.15)-i*30; if(sx>-120) s+=student(sx,y-130+Math.abs(Math.sin(u*8+i))*-10,46,cols[i],1,null);});
   const st=e((u-0.3)/0.8)-e((u-2.0)/0.7); const ax=900, ay=520;
   s+=`<path d="M${ax-60} ${ay+90} L${ax-80-20*st} ${lerp(ay+180,ay-80,st)}" stroke="${P.hood}" stroke-width="36" stroke-linecap="round"/><path d="M${ax+60} ${ay+90} L${ax+80+20*st} ${lerp(ay+180,ay-80,st)}" stroke="${P.hood}" stroke-width="36" stroke-linecap="round"/>`;
   s+=mitten(ax-80-20*st,lerp(ay+190,ay-90,st),22)+mitten(ax+80+20*st,lerp(ay+190,ay-90,st),22);
   s+=student(ax,ay,60,P.hood,1,st>0.5?'joy':'smug')+desk(ax,610,220)+`<g filter="url(#sh)">${clock(960,250,110,15,30)}</g>`;
   return cam(1+0.02*u,900,500,s);}],
 [12.5,15.0,u=>cam(1.05+0.02*u,800,560,`<g filter="url(#b8)">${CB}</g>`+mina(800,560+Math.sin(u*2)*4,180,'shock'))],
 [15.0,18.6,u=>{let s=`<rect width="${W}" height="${H}" fill="#2a1f2e"/><g opacity="0.25">${[...Array(10)].map((_,i)=>`<rect x="0" y="${i*110}" width="${W}" height="4" fill="#120c16"/>`).join('')}</g>`;
   s+=`<g transform="rotate(-4 860 560)" filter="url(#sh)"><rect x="380" y="200" width="460" height="640" rx="10" fill="#f4ead8"/><rect x="860" y="200" width="460" height="640" rx="10" fill="#f6eedd"/><rect x="838" y="200" width="44" height="640" fill="#d9ccb4"/>`;
   const r=rnd(5);for(let p=0;p<2;p++)for(let l=0;l<15;l++){const y=250+l*38,x0=p?900:420,len=200+r()*180,show=cl(u*3-(p*15+l)*0.06);if(show>0){s+=`<path d="M${x0} ${y} q20 -8 40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0 t40 0" stroke="#4a5a8a" stroke-width="3.5" fill="none" stroke-dasharray="${len} 999" stroke-dashoffset="${len*(1-show)}"/>`;}
     s+=`<line x1="${x0-20}" y1="${y+12}" x2="${x0+400}" y2="${y+12}" stroke="#c8d4ec" stroke-width="1.5"/>`;}
   s+=`</g>`;
   const hud=cl((u-0.3)*4); s+=`<g opacity="${hud}" transform="translate(1560 260)"><circle r="70" fill="none" stroke="${P.white}" stroke-width="7"/><rect x="-12" y="-96" width="24" height="18" fill="${P.white}"/><line x1="0" y1="0" x2="${Math.cos(u*6)*48}" y2="${Math.sin(u*6)*48}" stroke="${P.acc}" stroke-width="7" stroke-linecap="round"/></g>`+`<g opacity="${hud}">`+T(1560,420,'5 h 16 min',72,P.white)+`</g>`;
   if(u>1.6){const k=u-1.6,sc=1+0.6*Math.max(0,1-k*6);s+=`<g transform="translate(1560 540) rotate(-8) scale(${sc})" opacity="${cl(k*6)}"><rect x="-210" y="-62" width="420" height="104" rx="14" fill="none" stroke="${P.acc}" stroke-width="9"/>`+T(0,22,'SKIPPED',80,P.acc)+`</g>`;}
   return cam(1.0+0.03*u,860,560,s);}],
 [18.6,21.6,u=>cam(1.0+0.05*u,1180,560,CB+heroBust(1180,560,175,u<1.3?'smug':'unsure',{dir:-1}))],
 [21.6,25.0,u=>{const ty=-600*e(u/3.4);let s=`<rect width="${W}" height="${H}" fill="#231c38"/><g transform="translate(0 ${ty})"><rect y="-400" width="${W}" height="${H+800}" fill="url(#sky)"/>${rays(960,980,u*4,0.05)}<circle cx="960" cy="1000" r="460" fill="url(#sun)"/>`;
   const r=rnd(3);for(let i=0;i<7;i++){const y=100+r()*700,x=((r()*W)+u*40*(1+i%3))%(W+400)-200;s+=`<rect x="${x}" y="${y}" width="${260+r()*300}" height="${18+r()*14}" rx="12" fill="#ffd6c2" opacity="${0.15+r()*0.2}"/>`;}
   s+=`<g transform="translate(0 ${H})">${SW.replace(`<rect width="${W}" height="${H}" fill="url(#sky)"/>`,'')}</g></g>`;return s;}],
 [25.0,30.0,u=>{const a=e((u-0.3)/0.9),b=e((u-1.1)/0.6),sc=1.08-0.08*a;
   return cam(1.12-0.02*u/5,1000,620,SW)+`<g opacity="${a}" filter="url(#sh)" transform="translate(960 300) scale(${sc}) translate(-960 -300)">`+T(W/2,240,'WHAT IF YOU COULD SKIP',84,'url(#title)','middle','letter-spacing="3"')+T(W/2,340,'THE BORING PARTS?',104,'url(#title)','middle','letter-spacing="3"')+`</g><g opacity="${b}">`+T(W/2,400,'AN  IF TOON  WHAT IF',26,'#e8d8c8','middle','letter-spacing="6" font-weight="700"')+`</g>`+flash(0.6*cl(1-(u-0.25)*5)*(u>0.25?1:0));}],
];
const fontsDir=path.resolve('fonts'); const b64=f=>'data:font/ttf;base64,'+fs.readFileSync(path.join(fontsDir,f)).toString('base64');
const html=`<html><head><style>@font-face{font-family:'Nunito';font-weight:200 1000;src:url(${b64('Nunito.ttf')})}body{margin:0;background:#000}</style></head><body><svg id="s" xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"></svg></body></html>`;
const br=await chromium.launch(); const pg=await br.newPage({viewport:{width:W,height:H}}); await pg.setContent(html); await pg.evaluate(()=>document.fonts.load('900 40px Nunito'));
const total=30, N=Math.round(total*FPS);
for(let f=0;f<N;f++){const t=f/FPS; if(ONLY && Math.abs(t-parseFloat(ONLY))>0.02) continue;
 const sh=shots.find(s=>t>=s[0]&&t<s[1])||shots[shots.length-1]; const body=defs+sh[2](t-sh[0])+fin(W,H);
 await pg.evaluate(b=>{document.getElementById('s').innerHTML=b;},body);
 await pg.screenshot({path:`${OUT}/f${String(f).padStart(4,'0')}.jpg`,type:'jpeg',quality:88}); if(f%120===0) console.log('frame',f);}
await br.close();
