const { chromium } = require('playwright'); const { spawn } = require('child_process'); const fs=require('fs');
(async () => {
  const FPS=60; const T=JSON.parse(fs.readFileSync('timeline.json')); const dur=T.END+0.3; const n=Math.round(dur*FPS);
  const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(FPS),'-c:v','png','-i','-','-i','mix.wav','-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','256k','-movflags','+faststart','-shortest','out.mp4'],{stdio:['pipe','inherit','inherit']});
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + require('path').resolve('short.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
  for (let i=0;i<n;i++){ await p.evaluate(x=>window.render(x), i/FPS); const buf=await p.screenshot({type:'png'}); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); if(i%120==0) fs.writeFileSync('progress.txt',`${i}/${n}`); }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); fs.writeFileSync('progress.txt','done');
})();
