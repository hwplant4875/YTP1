import { chromium } from 'playwright';
import path from 'path';
import fs from 'fs';
const b64=f=>'data:font/ttf;base64,'+fs.readFileSync(path.resolve('fonts',f)).toString('base64');
export const C = { bg:'#0c0c0e', floor:'#6c696d', skin:'#e8e3cd', ink:'#2a2a2e', line:'#8d8a90', dim:'#3a3940', acc:'#ffc93c', accGlow:'#ffb100', white:'#f0ece0', red:'#ff4b3a' };
const FD = path.resolve('fonts');
export function defs(){ return `<defs>
 <filter id="wob" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="3.2"/></filter>
 <filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="14"/></filter>
 <filter id="glow2" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="40"/></filter>
 <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="9"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.05 0"/></filter>
 <radialGradient id="vig" cx="50%" cy="48%" r="75%"><stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity="0.75"/></radialGradient>
 <linearGradient id="shaft" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfd6e6" stop-opacity="0.13"/><stop offset="1" stop-color="#cfd6e6" stop-opacity="0"/></linearGradient>
</defs>`; }
export function overlay(w,h){ return `<rect width="${w}" height="${h}" fill="url(#vig)"/><rect width="${w}" height="${h}" filter="url(#grain)"/>`; }
// limb: dark outline + cream fill
export function limb(pts, w=17){ const d='M'+pts.map(p=>p.join(' ')).join(' L');
 return `<path d="${d}" fill="none" stroke="${C.ink}" stroke-width="${w+7}" stroke-linecap="round" stroke-linejoin="round"/><path d="${d}" fill="none" stroke="${C.skin}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`; }
export function hand(x,y,r=13){ return `<circle cx="${x}" cy="${y}" r="${r}" fill="${C.skin}" stroke="${C.ink}" stroke-width="3.5"/>`; }
// face features, dir=1 faces right, 0 front
export function face(cx,cy,r,ex,dir=0){
 const o=dir*r*0.22, k=r/60, I=C.ink;
 const ex1=cx+o-20*k, ex2=cx+o+20*k, ey=cy-2*k;
 const L=(d,w=5)=>`<path d="${d}" fill="none" stroke="${I}" stroke-width="${w*k}" stroke-linecap="round" stroke-linejoin="round"/>`;
 const dot=(x,y,rr=6)=>`<circle cx="${x}" cy="${y}" r="${rr*k}" fill="${I}"/>`;
 const half=(x,y)=>`<path d="M${x-8*k} ${y} A${8*k} ${8*k} 0 0 0 ${x+8*k} ${y}Z" fill="${I}"/>`+L(`M${x-11*k} ${y} L${x+11*k} ${y}`,4.5);
 let s='';
 switch(ex){
  case 'meh': s=half(ex1,ey)+half(ex2,ey)+L(`M${cx+o-12*k} ${cy+24*k} L${cx+o+12*k} ${cy+22*k}`,4.5); break;
  case 'bored': s=half(ex1,ey+2*k)+half(ex2,ey+2*k)+L(`M${ex1-12*k} ${ey-14*k} L${ex1+10*k} ${ey-12*k}`,4)+L(`M${ex2-10*k} ${ey-12*k} L${ex2+12*k} ${ey-14*k}`,4)+L(`M${cx+o-10*k} ${cy+26*k} Q${cx+o} ${cy+22*k} ${cx+o+12*k} ${cy+27*k}`,4.5); break;
  case 'panic': s=`<circle cx="${ex1}" cy="${ey}" r="${12*k}" fill="#fff" stroke="${I}" stroke-width="${3.5*k}"/><circle cx="${ex2}" cy="${ey}" r="${12*k}" fill="#fff" stroke="${I}" stroke-width="${3.5*k}"/>`+dot(ex1+dir*2*k,ey,4)+dot(ex2+dir*2*k,ey,4)+L(`M${ex1-12*k} ${ey-24*k} Q${ex1} ${ey-30*k} ${ex1+10*k} ${ey-26*k}`,4)+L(`M${ex2-10*k} ${ey-26*k} Q${ex2} ${ey-30*k} ${ex2+12*k} ${ey-24*k}`,4)+`<ellipse cx="${cx+o}" cy="${cy+28*k}" rx="${7*k}" ry="${9*k}" fill="${I}"/>`; break;
  case 'sad': s=dot(ex1,ey+3*k,5.5)+dot(ex2,ey+3*k,5.5)+L(`M${ex1-12*k} ${ey-8*k} L${ex1+9*k} ${ey-16*k}`,4.5)+L(`M${ex2-9*k} ${ey-16*k} L${ex2+12*k} ${ey-8*k}`,4.5)+L(`M${cx+o-12*k} ${cy+30*k} Q${cx+o} ${cy+20*k} ${cx+o+12*k} ${cy+30*k}`,4.5); break;
  case 'smug': s=half(ex1,ey)+half(ex2,ey)+L(`M${ex1-12*k} ${ey-12*k} L${ex1+10*k} ${ey-14*k}`,4.5)+L(`M${ex2-10*k} ${ey-18*k} Q${ex2} ${ey-22*k} ${ex2+12*k} ${ey-17*k}`,4.5)+L(`M${cx+o-12*k} ${cy+24*k} Q${cx+o+4*k} ${cy+30*k} ${cx+o+16*k} ${cy+18*k}`,5); break;
  case 'angry': s=dot(ex1,ey+2*k,6)+dot(ex2,ey+2*k,6)+L(`M${ex1-14*k} ${ey-16*k} L${ex1+10*k} ${ey-7*k}`,7)+L(`M${ex2-10*k} ${ey-7*k} L${ex2+14*k} ${ey-16*k}`,7)+`<rect x="${cx+o-15*k}" y="${cy+18*k}" width="${30*k}" height="${13*k}" rx="${3*k}" fill="#fff" stroke="${I}" stroke-width="${3.5*k}"/>`+L(`M${cx+o-15*k} ${cy+24.5*k} L${cx+o+15*k} ${cy+24.5*k} M${cx+o-5*k} ${cy+18*k} L${cx+o-5*k} ${cy+31*k} M${cx+o+5*k} ${cy+18*k} L${cx+o+5*k} ${cy+31*k}`,2.5); break;
  case 'joy': s=L(`M${ex1-10*k} ${ey+3*k} Q${ex1} ${ey-10*k} ${ex1+10*k} ${ey+3*k}`,5)+L(`M${ex2-10*k} ${ey+3*k} Q${ex2} ${ey-10*k} ${ex2+10*k} ${ey+3*k}`,5)+`<path d="M${cx+o-15*k} ${cy+18*k} Q${cx+o} ${cy+40*k} ${cx+o+15*k} ${cy+18*k}Z" fill="${I}"/>`; break;
 }
 return s;
}
export function head(cx,cy,r,ex,dir=0){ return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${C.skin}" stroke="${C.ink}" stroke-width="${3.5*r/60}"/>`+face(cx,cy,r,ex,dir); }
export function text(x,y,s,size,fill=C.white,anchor='middle',font='Patrick Hand',weight=400){ return `<text x="${x}" y="${y}" font-family="${font}" font-weight="${weight}" font-size="${size}" fill="${fill}" text-anchor="${anchor}">${s}</text>`; }
export async function render(svg,w,h,out){
 const html=`<html><head><style>@font-face{font-family:'Patrick Hand';src:url(${b64('PatrickHand-Regular.ttf')})}@font-face{font-family:'Comic Neue';font-weight:700;src:url(${b64('ComicNeue-Bold.ttf')})}body{margin:0;background:#000}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${svg}</svg></body></html>`;
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:w,height:h}});
 await p.setContent(html); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
 await p.screenshot({path:out,type:'jpeg',quality:92}); await b.close(); }
