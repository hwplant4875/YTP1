---
name: horror-ranked-thumbnail
description: Make the Horror Ranked three-panel survival thumbnails (left GREEN %, middle YELLOW %, right RED %, big villain faces from official posters/stills, strong dark shadow under the numbers), always as three visually different variants A/B/C. Use for any Horror Ranked / Instruction 444 ranking video thumbnail.
---

# Horror Ranked thumbnail (owner's standing format, 10/31)

Reference: `reference_myers_v4_a.jpg` in this folder (EP01 Myers v4 A: 90% / 62% / 1%).

## Layout
- 1280x720, three panels 427 / 426 / 427 px, thin black gutters (6 px).
- One villain face per panel, **big**: the whole face fills most of the panel (forehead near the top edge, chin around 2/3 down),
  eyes in the upper third. Never crop mid-face, never show a tiny figure.
- Numbers: YouTube Sans Black (`ep01/YouTubeSans-Black.otf`, `gfx.f(182)`), stroke 8 black, drop shadow (`gfx.shadow_text`),
  centred in each panel at y = H - 178. **By position, always: LEFT GREEN (70,215,95), MIDDLE YELLOW (250,200,40), RIGHT RED (235,30,38).**
  The red number is the lowest survival rate in the video (e.g. Art the Clown 3%, not his other entry's 6%).
- **Shadow under the numbers is mandatory**: a vertical black gradient over each panel from 50 % height to the bottom
  (alpha ramps 0 -> ~235), so the picture under the % is dark and the numbers pop. Don't let the face sit under the %.

## Sources (quality first)
- Prefer **official posters / key art / HD stills** (TMDB: open `themoviedb.org/movie/<id>/images/posters|backdrops` in the built-in
  browser, collect the `/t/p/` paths with javascript, then download `https://image.tmdb.org/t/p/original/<path>`). Keep them in the
  scratchpad, never commit them.
  **Official art only** (owner 10/31: "official poster, not fan art"): TMDB poster lists mix in fan art and alternative
  posters; use only real theatrical / home-media key art (check it is a release poster: studio credits, title treatment)
  or official film stills (TMDB backdrops). If the official poster has no face (e.g. Halloween 1978's pumpkin), use an official still. Video frame grabs are soft; use them only when no poster/still shows the face (then the sharpest HD
  frame of an official clip, never a trailer graphic, never a letterboxed area: crop the active picture and scale it to fill).
- Search by villain name (owner 10/31 idea), but take the full-size official image: Wikipedia infobox images are fair-use
  downscales (~250-300 px) and may show a different film's version of the villain, so don't use them directly.
- Brighten dark faces a little (brightness 1.1-1.6, contrast ~1.18), keep blown-out whites under control (brightness < 1 if needed).

## Three variants, visually very different
Always make A, B and C with different faces/compositions so the test reads as three different videos, e.g.
Ghostface: A = Ghostface / character 1 / character 2; B = Ghostface 1 / Ghostface 2 / Ghostface 3.
Halloween special: A = Sweet Sixteen Killer 99 / Michael Myers 30 / Art 3; B = Harold 50 / Sam 40 / bloody Art 3;
C = Silver Shamrock skull mask 60 / Hell Fest's The Other 45 / Art 3.

## Tool
`concepts/i444/ep_halloween/thumbs.py`: `P(clip_or_'poster:<file>', t, cx, cy, face_h, pct, col, bright, face_px, eye_y)`
(cx, cy, face_h in source pixels; face_px = face height in the output; eye_y = where (cx, cy) lands vertically).
`python thumbs.py [clips_dir] [out_dir] [posters_dir]` writes `upload/<ep>_thumb_{a,b,c}.jpg`.

## QA before sending
View all three at 640x360 and 960x540: every face whole, sharp and large; no black or blurred bands; the three colours in
green / yellow / red order; numbers sit on dark shadow; the red % matches the narration's lowest rate. Send the three jpgs to the owner,
update the upload kit's thumbnail lines, push.
