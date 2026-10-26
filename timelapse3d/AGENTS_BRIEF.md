# Agent brief: EP1 3D timelapse (read this first)

Repo: `E:\YTP2\3D Timelapse\repo\timelapse3d`. Touch nothing on E: outside `E:\YTP2`. Blender: `"/c/All The Programs/Blender/blender.exe"` (headless, `-b -P aot/scene.py -P <your render script> -- ...`). Windows + Git Bash.

## Read
- `EP1_plan_v2.md` (the shot table and the binding "User storyline feedback" section), `HANDOFF.md` (the newest sections at the end override older ones), `design_bible.md` when you need looks.
- Existing systems to reuse, not rewrite:
  - `aot/scene.py`: the town, walls, terrain, `gatehouse()` in anime flat style.
  - `aot/render_fast.py`: the opening. It is the model for a single-session per-frame render loop.
  - `aot/fx845.py`: per-frame destruction: gate breach, debris arcs, dust, house collapse.
  - `aot/swarm845.py`: minimal people and titans as a pure function of t; streets nav grid; boats.
  - `aot/people_kit.py`: faceless named characters: erwin, levi, hannes, carla, grisha, eren, mikasa, armin, jean, connie, sasha, reiner, bertholdt, christa, ymir, annie, marco, pixis, eren_child, mikasa_child; plus cadet, garrison, scout, mp and civilian pools.
  - `aot/attack_titan.py`: the Attack Titan plus shift FX.
  - `aot/colossal_asset.py`: the Colossal. Import it, don't edit it.
  - `aot/characters.py`, `aot/seq_carla.py`, `hud.py`: HUD captions and counters.

## Rules (user, binding)
- **ONE continuous camera take for the whole video.** Never cut to a full-frame graphic. Maps, counters and captions are small overlays on the running 3D shot, only where they fit.
- **Pace is everything.** Brisk drone moves, short holds. Holds exist only for the overlay beats listed in the plan, at 2-3 s each.
- **The whole EP1 is 8-10 min max.** Scale the plan's shot seconds by about 0.65 unless told otherwise.
- **Timelapse of the world, seen from the sky** (40-400 m). Characters are tiny and **faceless** (no eyes, nose or mouth), readable only by hair colour, outfit and silhouette.
- **People and titans use the MINIMAL style the user loves:** colourful, clearly visible, very simple figures. Lore-accurate details fans will notice: uniforms and emblems, the ODM gear, the gas, the flares (red, green, yellow, black), canon geography and order of events.
- **Never put the camera behind the Colossal's back.** Use smooth eased camera moves with no speed jumps and no camera passing through geometry.
- **Animation is a pure function of time.** One Blender session builds the scene once, then loops frames: set the state for t, render. Never rebuild per frame.

## Files
- Each agent owns the files named in its prompt. Create new modules instead of editing shared ones.
- If you must change a shared module, add a small opt-in hook behind an env flag and say so in your report.
- Never edit `scene.py`, `render_fast.py`, `colossal_asset.py`, `characters.py`, `flight.py`, `fx845.py` or `swarm845.py` unless your prompt says so.
- Do not git commit or push. The lead does.

## GPU (one GTX 1060, shared by several agents)
```
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"; until mkdir "$LOCK" 2>/dev/null; do sleep 5; done; trap 'rmdir "$LOCK" 2>/dev/null' EXIT
```
- Hold the lock only while Blender runs. Never kill a Blender process you didn't start.
- Check with a few 854x480 stills per session.
- **Previews:** 854x480, 15 fps, at most 20 min for a whole segment (about 4-5 s per frame). Use Eevee if it works with your scene, otherwise Cycles at 1-2 samples with denoise and simplify.
- Encode with ffmpeg H.264 at CRF 26.
- Put outputs in `E:\YTP2\3D Timelapse\renders\<your segment>\`: the mp4 plus 4-6 stills.

## Report back (short)
- The files and how to run them.
- The segment's length in seconds.
- The stills, with paths.
- Seconds per frame.
- Known gaps.

## WAVE v2 (10/26): implementing SCENE_BIBLE_v2.md section D (read this section first)
- MASTER SPEC = `SCENE_BIBLE_v2.md` (supersedes older layout/camera notes; owner rules in HANDOFF.md still win). More
  detail per beat: `design_specs/g1..g8_*.md`. Reference frames: `ref/anime/bible/` (REFERENCE ONLY, never in our video).
- Timings: the TIGHT column of bible table A1 is FINAL (owner 10:52 UTC: 7:02, keep every scene). Keep every beat time of
  a segment in ONE `BEATS`/keys table at the top of its module so a re-time is a one-place edit.
- Frames: Trost master M (outer gate O = (0,0), Rose Y 870); trost.py set coords = (X, Y - 870, Z). Shiganshina = W.
  Write positions in M in code (`TR.M(x, y, z)` converts) so they can be checked against the bible.
- Shared contracts (do not break them; ask the lead before changing one):
  * `aot/camchan.py`: `CamPath(keys=[(t, cam, look, lens), ...], v_in=None, v_out=None, look_v_in=None, look_v_out=None)`
    -> `.eval(t) -> (loc, look, lens)`; separate arc-length channels for position and look-at (chord Hermite + PCHIP arc
    length, as render_fast._Channel), lens in log space, optional seam tangents. `camchan.check(path, t0, t1)` prints
    peak m/s, yaw deg/s, pitch range, min height above ground, lens range, and flags the look-at passing under the camera.
    Every segment's camera must pass the bible's limits (A3) with this checker before rendering.
  * `aot/segtime.py`: the A1 table (id, tight duration, global start) + `seam(id)` returning the A2 seam (pos, look, lens, vel).
  * Trost segments g4-g8: generic driver `aot/render_seg.py` + `render_seg.sh` (`SEG=g8 bash render_seg.sh`,
    `STILLS="12,30" ...`, `WIN=0,25` windows). It builds the trost.py set once, imports `aot/seg_<id>.py` which exposes
    `DUR`, `BEATS`, `CAM` (a CamPath in M), `build(site)`, `update(t)` (pure function of local time t), `light(t)`.
- Renders: 854x480, 15 fps, Eevee, toon ON (less orange is the default in toon.py; do not change it), every invocation
  <= 20 min wall (render windows/parts if needed; STEP=2 with frame repeat is acceptable for previews). Hold the GPU lock
  only while Blender runs. Output: `E:/YTP2/3D Timelapse/renders/<seg>/<seg>_preview.mp4` and a 2 fps contact sheet
  `<seg>_sheet.jpg` (ffmpeg `fps=2,scale=320:-1,tile=6x<rows>`, under 2 MB). The lead copies them to renders/laptop/,
  commits and pushes. Agents never commit or push.
- Humans 1.65 m, faceless, downloaded assets only (people_kit); no red-cape giants; titans keep their faces.
