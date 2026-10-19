import {C,defs,overlay,limb,hand,head,face,text} from './lib.mjs';
const W=1920,H=1080,F=770;
const bars=`<rect width="${W}" height="120" fill="#000"/><rect y="${H-120}" width="${W}" height="120" fill="#000"/>`;
function remote(x,y,s=1,glow=true){ return `<g transform="translate(${x} ${y}) rotate(-18) scale(${s})">
 ${glow?`<circle cx="0" cy="-22" r="46" fill="${C.accGlow}" opacity="0.55" filter="url(#glow)"/>`:''}
 <rect x="-20" y="-52" width="40" height="96" rx="12" fill="#26252b" stroke="${C.line}" stroke-width="3.5"/>
 <circle cx="0" cy="-22" r="13" fill="${glow?C.acc:'#5a5860'}"/>
 <path d="M-7 -29 L0 -22 L-7 -15Z M0 -29 L7 -22 L0 -15Z" fill="#26252b"/>
 <circle cx="-8" cy="8" r="4" fill="#4a4950"/><circle cx="8" cy="8" r="4" fill="#4a4950"/><circle cx="-8" cy="24" r="4" fill="#4a4950"/><circle cx="8" cy="24" r="4" fill="#4a4950"/></g>`; }
function room(ff){ // classroom set, line drawn
 const L=C.line;
 return `<line x1="0" y1="${F}" x2="${W}" y2="${F}" stroke="${C.floor}" stroke-width="3"/>
 <g fill="none" stroke="${L}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">
  <rect x="250" y="220" width="200" height="200" rx="6" fill="#121218"/><line x1="350" y1="220" x2="350" y2="420"/><line x1="250" y1="320" x2="450" y2="320"/>
 </g>
 <polygon points="250,420 450,420 760,${F} 380,${F}" fill="url(#shaft)"/>
 <g stroke="${L}" stroke-width="4" fill="none" stroke-linecap="round">
  <rect x="1240" y="300" width="520" height="290" rx="6" fill="#151a17"/>
  <path d="M1290 360 q30 -16 60 0 t60 0 M1290 420 l120 0 M1440 420 l90 0 M1290 480 q40 -20 80 0 M1400 480 l120 0" stroke="#59605a" stroke-width="3"/>
  <line x1="1240" y1="604" x2="1760" y2="604"/>
 </g>
 <!-- desk + chair -->
 <g stroke="${L}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path d="M830 600 L1040 600" stroke-width="7"/><path d="M850 600 L850 ${F} M1020 600 L1020 ${F}"/>
  <path d="M690 520 L700 660 L820 660 M710 660 L705 ${F} M810 660 L815 ${F}"/>
 </g>`; }
function clock(x,y,r,hh,mm,blur=false){ const a=(mm/60)*360-90, b=((hh%12)/12+mm/720)*360-90; const R=Math.PI/180;
 let s=`<circle cx="${x}" cy="${y}" r="${r}" fill="#141418" stroke="${C.line}" stroke-width="4.5"/>`;
 for(let i=0;i<12;i++){const t=i*30*R; s+=`<line x1="${x+Math.cos(t)*r*0.78}" y1="${y+Math.sin(t)*r*0.78}" x2="${x+Math.cos(t)*r*0.9}" y2="${y+Math.sin(t)*r*0.9}" stroke="${C.line}" stroke-width="3"/>`;}
 if(blur){ s+=`<path d="M${x} ${y-r*0.72} A${r*0.72} ${r*0.72} 0 1 1 ${x-r*0.72} ${y}" fill="none" stroke="${C.acc}" stroke-width="${r*0.18}" opacity="0.35" filter="url(#glow)"/>`;
  for(let i=0;i<6;i++){const t=(a-i*24)*R; s+=`<line x1="${x}" y1="${y}" x2="${x+Math.cos(t)*r*0.72}" y2="${y+Math.sin(t)*r*0.72}" stroke="${C.acc}" stroke-width="4" opacity="${0.8-i*0.13}" stroke-linecap="round"/>`;} }
 s+=`<line x1="${x}" y1="${y}" x2="${x+Math.cos(a*R)*r*0.72}" y2="${y+Math.sin(a*R)*r*0.72}" stroke="${C.white}" stroke-width="4" stroke-linecap="round"/><line x1="${x}" y1="${y}" x2="${x+Math.cos(b*R)*r*0.48}" y2="${y+Math.sin(b*R)*r*0.48}" stroke="${C.white}" stroke-width="6" stroke-linecap="round"/><circle cx="${x}" cy="${y}" r="5" fill="${C.white}"/>`;
 return s; }
function teacher(x,ghost=0){ const f='#4a4850', o=ghost?0.25:1; const t=`<g opacity="${o}" transform="translate(${ghost} 0)">
 ${''}<path d="M${x} ${F-150} L${x-6} ${F}" stroke="${f}" stroke-width="20" stroke-linecap="round"/><path d="M${x+14} ${F-150} L${x+18} ${F}" stroke="${f}" stroke-width="20" stroke-linecap="round"/>
 <path d="M${x+6} ${F-150} L${x+6} ${F-270}" stroke="${f}" stroke-width="56" stroke-linecap="round"/>
 <path d="M${x-6} ${F-250} L${x-60} ${F-300} L${x-110} ${F-360}" stroke="${f}" stroke-width="18" stroke-linecap="round" fill="none"/>
 <circle cx="${x+4}" cy="${F-330}" r="60" fill="${f}"/></g>`; return t; }
function seated(ex, armUp){ // student facing right
 const hip=[770,648], neck=[805,528], hc=[842,462];
 let s=limb([hip,[870,652],[868,F-4]],17)+limb([[778,650],[850,668],[846,F-4]],17);
 s+=limb([hip,neck],46);
 if(armUp) s+=limb([[808,540],[880,520],[960,470]],16)+remote(985,445,1.15,true)+hand(962,470,15);
 else s+=limb([[808,540],[905,590],[870,520]],16)+hand(870,516,15);
 s+=head(hc[0],hc[1],62,ex,1);
 if(!armUp) s+=limb([[812,545],[930,592],[990,592]],16)+hand(992,592,13);
 return s; }
export {W,H,F,bars,remote,room,clock,teacher,seated};
