# You, Elsewhere EP1 (Malfoid): Blender look test

Goal: a 40 s preview MP4 of a calm, cinematic "POV ambience" video made in Blender from ONE still photo
(`assets/closeup.png`, 1672x941, old-iPhone candid look: blonde young woman, fireplace on the left,
round lake windows at the top right with rain on the water).

## Hard rules from the channel owner
- The woman stays perfectly still. Do NOT warp, move, breathe or animate her face/body/hair.
- NO zoom, NO camera move, NO shake. Fixed 1920x1080 framing of the whole image (fit, no crop beyond aspect).
- NOTHING pulses or moves on the beat. No beat-synced flashes, no bass-driven scaling. Calm, not busy.
- Opening: the first 6 s ease from 20% brightness to 100% (smoothstep). After that, constant.
- Watermark "You, Elsewhere" in Allura (`assets/Allura.ttf`), bottom-left, margin ~64 px, height ~60 px,
  warm off-white (246,238,224) at ~80% opacity with a soft dark shadow. Always visible.
- 30 fps, 1920x1080, H.264 CRF ~20, audio = `assets/music_60s.mp3` (first 40 s, 3 s fade-in, 4 s fade-out).

## Ideas to try (pick what looks best; subtle beats flashy)
1. Image on an emission plane, orthographic camera, Filmic/AgX, compositor for the look.
2. Film filter: fine grain (fresh per frame), soft halation/glow on the fire and window lights,
   very gentle vignette, slightly lifted blacks, tiny chromatic aberration at the edges.
3. Fire area (left, roughly x<230, y 380-780 in image px): gentle flicker of the firelight brightness
   on the left wall and a faint warm spill. Small heat-shimmer on the flames ONLY, never on her.
4. Window area (top right round windows): slow rain streaks / drops running down the glass, faint
   water caustic shimmer. Keep it inside the window shapes.
5. A few dust motes floating slowly in the warm light (3D particles with depth of field, bokeh),
   max ~30, slow drift, never crossing her face prominently.
6. Optional slow light-leak or warm glow drifting very slowly across the left edge (period >= 20 s).
7. Audio spectrum: allowed only if it is small and calm. A thin, low-opacity (~35%) line or row of
   tiny bars right next to / under the watermark, heavily smoothed (attack/release ~300 ms+) so it
   flows instead of jumping. Bake with Blender "Bake Sound to F-Curves" or precompute with Python.
   If it looks busy, leave it out and say so.

## Output
- Save to `C:\Users\hw549\Downloads\YTP1\YouElsewhere\ep01_malfoid\` : `malfoid_blender_preview_v1.mp4`
  (CRF/tune so it is under ~90 MB), plus 2 stills (t=3 s and t=20 s) as JPG, plus the .blend and the
  generating Python script.
- Commit stills, script and the mp4 (if < 95 MB) to branch `claude/project-thread-uxub9k` in this repo,
  folder `you_elsewhere/ep01_malfoid/blender_out/`, and push.
- Report: which effects you used, render time per frame, and anything that did not work.
