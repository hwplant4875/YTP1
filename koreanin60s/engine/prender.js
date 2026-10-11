// Parallel renderer: node prender.js <dir> [fps] [workers] -> <dir>/out.mp4 from short.html + timeline.json + mix.wav.
// Splits the frames into one chunk per worker (each its own browser page and encoder), then joins the chunks and adds the audio.
const { chromium } = require('playwright'); const { spawn, execFileSync } = require('child_process'); const fs = require('fs'); const path = require('path');
(async () => {
  const dir = path.resolve(process.argv[2]); const FPS = +(process.argv[3] || 60); const W = +(process.argv[4] || 4);
  const T = JSON.parse(fs.readFileSync(dir + '/timeline.json')); const n = Math.round((T.END + 0.3) * FPS);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const done = new Array(W).fill(0);
  const work = async (w) => {
    const a = Math.floor(n * w / W), z = Math.floor(n * (w + 1) / W);
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16',
      '-pix_fmt', 'yuv420p', '-profile:v', 'high', `${dir}/seg_${w}.mp4`], { stdio: ['pipe', 'inherit', 'inherit'] });
    const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
    await p.goto('file://' + dir + '/short.html'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500); await p.evaluate(() => { window.fit && window.fit(); window.layout && window.layout(); });
    for (let i = a; i < z; i++) {
      await p.evaluate(x => window.render(x), i / FPS); const buf = await p.screenshot({ type: 'jpeg', quality: 95 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      done[w] = i - a + 1; if (i % 60 == 0) fs.writeFileSync(dir + '/progress.txt', `${done.reduce((x, y) => x + y)}/${n}`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); await p.close();
  };
  await Promise.all([...Array(W).keys()].map(work)); await b.close();
  fs.writeFileSync(dir + '/segs.txt', [...Array(W).keys()].map(w => `file 'seg_${w}.mp4'`).join('\n') + '\n');
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', dir + '/segs.txt', '-i', dir + '/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
    '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', '-shortest', dir + '/out.mp4']);
  fs.writeFileSync(dir + '/progress.txt', 'done');
})();
