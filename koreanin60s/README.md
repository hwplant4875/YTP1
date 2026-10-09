# Korean in 60s (YouTube channel, formerly Top Techs)

Upload key: `YT_REFRESH_TOKEN_TT`. Plans and rendered assets live in the project shared folder `/mnt/project-files/plans/toptechs/`.

- `mascot/cat.py` — **Chizu**, Korean shorthair cheese cat (current mascot), poses: default, happy, surprised, wrong, thinking, sleepy. `bird.py`, `bird2.py`, `jindo.py` are rejected drafts.
- `mascot/brand.py` — profile picture (800×800) and banner (2560×1440) HTML; render with `node shot.js <html> <w> <h> <png>`.
- `shorts/NNN-*/` — one folder per short:
  1. `lines.json` script → ElevenLabs per-line VO in `vo/*.wav` (silence-trimmed)
  2. `timeline.py` → `timeline.json` (start/end per line)
  3. `audio.py` → synthesized SFX + music, ducked mix `mix.wav` (−14 LUFS)
  4. `build.py` + `template.html` → `short.html` with `window.render(t)`
  5. `render.js` → 60 fps frames via Playwright/Chromium piped to ffmpeg → `out.mp4`

Run node scripts with `NODE_PATH=/opt/node22/lib/node_modules`. Fonts: Pretendard, Jua, Fredoka in `~/.fonts`.
