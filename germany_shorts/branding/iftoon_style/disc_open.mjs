import {chromium} from 'playwright';
import fs from 'fs'; import path from 'path';
import {C,defs,overlay,limb,hand,head,text} from './lib.mjs';
import {W,H,F,bars,remote,room,clock,teacher,seated} from './disclib.mjs';
const FPS=24, OUT=process.argv[2]||'dframes', ONLY=process.argv[3]; fs.mkdirSync(OUT,{recursive:true});
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)), e=x=>{x=cl(x);return x<.5?2*x*x:1-Math.pow(-2*x+2,2)/2}, lerp=(a,b,t)=>a+(b-a)*t;
const bg=`<rect width="${W}" height="${H}" fill="${C.bg}"/>`;
const typed=(s,u,dur)=>s.slice(0,Math.floor(cl(u/dur)*s.length));
const wob=s=>`<g filter="url(#wob)">${s}</g>`;
const label=s=>text(130,190,s,46,C.acc,'start');
function stand(x,ex,{armUp=0,scarf=true,dir=0}={}){const fl=F;let s=limb([[x-14,fl-150],[x-20,fl-4]],17)+limb([[x+14,fl-150],[x+20,fl-4]],17)+limb([[x,fl-150],[x,fl-262]],48);
 s+=limb([[x-20,fl-245],[x-40,fl-170]],16)+hand(x-42,fl-166,13);
 const hx=lerp(x+44,x+120,armUp), hy=lerp(fl-166,fl-330,armUp); s+=limb([[x+20,fl-245],[lerp(x+40,x+80,armUp),lerp(fl-200,fl-280,armUp)],[hx,hy]],16);
 if(armUp>0.5) s+=remote(hx+18,hy-30,1.15,true); s+=hand(hx,hy,13);
 s+=head(x,fl-330,62,ex,dir);
 if(scarf) s+=`<path d="M${x-40} ${fl-268} Q${x} ${fl-252} ${x+40} ${fl-268}" stroke="${C.acc}" stroke-width="16" fill="none" stroke-linecap="round"/><path d="M${x+26} ${fl-262} L${x+46} ${fl-212}" stroke="${C.acc}" stroke-width="14" stroke-linecap="round"/>`;
 return s;}
function bedScene(u,clk){let s=`<line x1="0" y1="${F}" x2="${W}" y2="${F}" stroke="${C.floor}" stroke-width="3"/><g stroke="${C.line}" stroke-width="5" fill="none" stroke-linejoin="round"><path d="M700 ${F} L700 560 M700 650 L1300 650 L1300 ${F} M700 690 L1300 690"/><rect x="560" y="620" width="110" height="${F-620}" rx="8" fill="#141418"/></g>`;
 s+=`<rect x="575" y="585" width="80" height="40" rx="6" fill="#1a0e0e" stroke="#5a2420" stroke-width="3"/>`+text(615,617,clk,30,'#e0302a','middle','Patrick Hand');
 s+=`<path d="M800 650 Q900 600 1290 610 L1290 650Z" fill="#2c3550" stroke="${C.ink}" stroke-width="3"/>`+head(760,610,48,'smug',1);return s;}
function calendar(u){let s=`<rect x="610" y="250" width="700" height="520" rx="10" fill="#e8e3cd" stroke="${C.ink}" stroke-width="4"/><rect x="610" y="250" width="700" height="80" rx="10" fill="#d8b23a"/>`+text(960,305,'OCTOBER',44,'#2a2a2e','middle');
 const n=Math.floor(cl(u/1.1)*24);for(let i=0;i<28;i++){const cx=650+(i%7)*94+20,cy=350+Math.floor(i/7)*100;s+=`<rect x="${cx-20}" y="${cy}" width="80" height="80" fill="none" stroke="#b9b39f" stroke-width="2"/>`;if(i<n)s+=`<path d="M${cx-5} ${cy+15} L${cx+45} ${cy+65} M${cx+45} ${cy+15} L${cx-5} ${cy+65}" stroke="${C.acc}" stroke-width="7" stroke-linecap="round"/>`;}return s;}
function windowSeason(u){const p=cl(u/1.2);let s=`<rect x="660" y="230" width="600" height="480" rx="8" fill="${p<0.5?'#1a2236':'#24182a'}" stroke="${C.line}" stroke-width="5"/><line x1="960" y1="230" x2="960" y2="710" stroke="${C.line}" stroke-width="5"/><line x1="660" y1="470" x2="1260" y2="470" stroke="${C.line}" stroke-width="5"/>`;
 for(let i=0;i<40;i++){const x=680+((i*137)%560),y=250+((i*91+u*240*(1+i%3))%440);s+=p<0.5?`<circle cx="${x}" cy="${y}" r="${3+i%3}" fill="#e6ecf5" opacity="0.8"/>`:`<ellipse cx="${x}" cy="${y}" rx="7" ry="4" fill="#ff9ec4" opacity="0.85" transform="rotate(${i*30} ${x} ${y})"/>`;}
 return s+stand(1420,'smug',{scarf:false});}
function speed(cx,cy,n,len,op){let s='';for(let i=0;i<n;i++){const a=(i*360/n+7*(i%3))*Math.PI/180,r1=110+(i%3)*14,r2=r1+len*(0.6+(i%4)*0.2);s+=`<line x1="${cx+Math.cos(a)*r1}" y1="${cy+Math.sin(a)*r1}" x2="${cx+Math.cos(a)*r2}" y2="${cy+Math.sin(a)*r2}" stroke="${C.acc}" stroke-width="${3+(i%3)}" stroke-linecap="round" opacity="${op}"/>`;}return s;}
const flash=o=>o>0?`<rect width="${W}" height="${H}" fill="#fff" opacity="${o}"/>`:'';
const shots=[
 [0,5.5,u=>bg+wob(room()+clock(1080,320,62,10,14+u*0.2)+teacher(1560)+seated('bored',false))+`<g opacity="${cl((4.8-u)*2)}">`+text(W/2,215,'Every class felt like forever.',52)+`</g>`],
 [5.5,9.0,u=>bg+wob(room()+clock(1080,320,62,10,15)+teacher(1560)+seated('meh',false))+text(W/2,215,typed('just 46 more minutes...',u-0.3,1.6),46,C.red)+(u>1.8?`<g opacity="${cl(u-1.8)}">`+text(900,380-(u-1.8)*20,'z',30,'#8d8a90')+text(925,350-(u-1.8)*25,'z',24,'#8d8a90')+`</g>`:'')],
 [9.0,11.5,u=>bg+wob(clock(960,520,230,10,u<1.2?14:15))+(u>1.3?text(W/2,880,typed('10:15.',u-1.3,0.5),64,C.red):'')],
 [11.5,14.5,u=>{const r=e(u/1.6);return bg+wob(`<line x1="0" y1="${F}" x2="${W}" y2="${F}" stroke="${C.floor}" stroke-width="3"/><path d="M500 540 L1500 540" stroke="${C.line}" stroke-width="7" stroke-linecap="round"/>`+remote(1080,700,1.8,cl(u-1.2)>0)+limb([[300,520],[lerp(500,800,r),lerp(560,640,r)],[lerp(700,1030,r),lerp(620,700,r)]],22)+hand(lerp(700,1030,r),lerp(620,700,r),18))+`<g opacity="${cl((u-0.3)*2)}">`+text(W/2,215,'Then he found it.',50)+`</g>`;}],
 [14.5,15.5,u=>bg],
 [15.5,17.0,u=>{const p=u>0.5;return bg+wob(`<g transform="translate(960 560) scale(${p?0.96:1}) translate(-960 -560)">${remote(960,600,3.4,true)}</g>`+limb([[1500,1100],[1200,800],[1010,560]],34)+hand(1005,545,30)+(p?speed(960,500,20,300*cl((u-0.5)*4),0.8):''))+flash(p?cl(1-(u-0.5)*3):0);}],
 [17.0,18.25,u=>bg+wob(room()+clock(1080,320,62,15,30)+seated('smug',true))+label('SKIPPED: 5 HOURS')],
 [18.25,19.5,u=>bg+wob(bedScene(u,'7:00'))+label('SKIPPED: MONDAY')],
 [19.5,20.75,u=>bg+wob(calendar(u))+label('SKIPPED: 3 WEEKS')],
 [20.75,22.0,u=>bg+wob(windowSeason(u))+label('SKIPPED: WINTER')],
 [22.0,26.0,u=>{const a=e(u/0.6);return bg+wob(`<line x1="0" y1="${F}" x2="${W}" y2="${F}" stroke="${C.floor}" stroke-width="3"/>`+speed(1080,F-360,18,260,0.5*a)+stand(960,'smug',{armUp:a,scarf:true}))+`<circle cx="1098" cy="${F-390}" r="140" fill="${C.accGlow}" opacity="${0.18*a}" filter="url(#glow2)"/>`+(u>0.8?text(W/2,260,typed('skip.',u-0.8,0.4),110,C.acc):'');}],
 [26.0,30.0,u=>{const ul=cl((u-1.0)/0.6);let w='';for(let i=0;i<=40;i++){const x=760+i*10;w+=`${i?'L':'M'}${x} ${640+Math.sin(i*0.9)*7}`;}
   return bg+text(W/2,600,typed('SKIP',u-0.2,0.7),170,C.white,'middle','Comic Neue',700)+`<path d="${w}" stroke="${C.acc}" stroke-width="8" fill="none" stroke-linecap="round" stroke-dasharray="${420*ul} 999"/>`+`<g opacity="${cl((u-1.6)*2)}">`+text(W/2,740,'What if you could skip the boring parts?',44,'#d8d4c8')+`</g>`;}],
];
const fd=path.resolve('fonts'),b64=f=>'data:font/ttf;base64,'+fs.readFileSync(path.join(fd,f)).toString('base64');
const html=`<html><head><style>@font-face{font-family:'Patrick Hand';src:url(${b64('PatrickHand-Regular.ttf')})}@font-face{font-family:'Comic Neue';font-weight:700;src:url(${b64('ComicNeue-Bold.ttf')})}body{margin:0;background:#000}</style></head><body><svg id="s" xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"></svg></body></html>`;
const br=await chromium.launch(), pg=await br.newPage({viewport:{width:W,height:H}}); await pg.setContent(html); await pg.evaluate(()=>Promise.all([document.fonts.load('40px "Patrick Hand"'),document.fonts.load('700 40px "Comic Neue"')]));
for(let f=0;f<30*FPS;f++){const t=f/FPS; if(ONLY && !ONLY.split(',').some(x=>Math.abs(t-parseFloat(x))<0.021)) continue;
 const sh=shots.find(s=>t>=s[0]&&t<s[1])||shots[shots.length-1];
 await pg.evaluate(b=>{document.getElementById('s').innerHTML=b;},defs()+sh[2](t-sh[0])+overlay(W,H)+bars);
 await pg.screenshot({path:`${OUT}/f${String(f).padStart(4,'0')}.jpg`,type:'jpeg',quality:88});}
await br.close();
