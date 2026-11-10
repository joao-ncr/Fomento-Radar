// Renderiza reel.html quadro a quadro (determinístico) e gera build/video.mp4 sem áudio.
// Uso: node render.cjs [--preview t1,t2,...]
const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const HERE = __dirname;
(async () => {
const BUILD = path.join(HERE, 'build');
const FPS = 30;
const timing = JSON.parse(fs.readFileSync(path.join(BUILD, 'timing.json'), 'utf8'));
const prevArg = process.argv.indexOf('--preview');

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.addInitScript(t => { window.TIMING = t; }, timing);
await page.goto('file://' + path.join(HERE, 'reel.html'));
await page.evaluate(() => document.fonts.ready);
fs.writeFileSync(path.join(BUILD, 'cues.json'), JSON.stringify(await page.evaluate(() => window.cues()), null, 1));

if (prevArg > 0) {
  const ts = process.argv[prevArg + 1].split(',').map(Number);
  fs.mkdirSync(path.join(BUILD, 'preview'), { recursive: true });
  for (const t of ts) {
    await page.evaluate(t => window.render(t), t);
    await page.screenshot({ path: path.join(BUILD, 'preview', `f_${t.toFixed(2)}.jpg`), type: 'jpeg', quality: 80 });
  }
  await browser.close();
  process.exit(0);
}

const n = Math.ceil(timing.duration * FPS);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS), path.join(BUILD, 'video.mp4')],
  { stdio: ['pipe', 'inherit', 'inherit'] });
const t0 = Date.now();
for (let i = 0; i < n; i++) {
  await page.evaluate(t => window.render(t), i / FPS);
  const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 150 === 0) console.log(`quadro ${i}/${n} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();
console.log('ok', n, 'quadros');
})();
