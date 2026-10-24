# EP1 graphics layer: timeline format and per-segment hook

The graphics are composited onto the rendered PNG frames **after Blender**, in plain Python (PIL + numpy). No GPU, no lock.
Cost at 854x480: about 0.25 s per frame for HUD, tags and counters; about 1.5 s per frame when a full-frame map is drawn.

| file | role |
|---|---|
| `hudcam.py` | `dump()` inside Blender writes the camera of each frame to JSON; `project()` outside Blender maps world to pixel (matches `world_to_camera_view` exactly) |
| `hud2.py` | the compositor: reads a timeline JSON and draws the tracks onto the frames, then encodes the mp4 |
| `maps.py` | stylised 2D island map with walls, territory loss and routes. Presets `title` (shot 1), `loss` (shot 7), `march` (shot 10) |
| `hud.py` | the old one-off still HUD. Nobody imports it; it is left untouched |

## 1. Hook in a render script (one line per frame)

```python
import sys; sys.path.insert(0, r"E:/YTP2/3D Timelapse/repo/timelapse3d")
import hudcam
...
for i, t in enumerate(times):
    ...set the state and camera for t...
    hudcam.dump(sc, i, B.fast_out, t=t, track=("Eren", "Mikasa", "Armin"))   # optional track: per-frame object positions
    bpy.ops.render.render(write_still=True)
```

This writes `<out_dir>/_cam/00042.json`: matrix_world, lens, sensor, fit, shift, ortho, resolution and any tracked object
positions. ffmpeg globs such as `fast_%05d.png` never pick these files up. For stills named by time, pass `name="fast_t07.80"`.
Use the **same index** as the frame's file number, so that `fast_00042.png` matches `_cam/00042.json`.

## 2. Run after Blender

```
python hud2.py path/to/segment.json                 # all frames, plus the mp4 when "mp4" is set
python hud2.py path/to/segment.json --only 0,60,117 # spot checks
python hud2.py seg.json --still in.png out.png --index 117 [--t 7.8]
```

## 3. Timeline JSON

```json
{
  "segment": "shot13_trost_flood",
  "fps": 15,
  "frames": "E:/YTP2/3D Timelapse/renders/trost/frame_%05d.png",   // printf pattern or glob; omit for pure graphics
  "first": 0, "last": null,            // window of frame indices; t = t_offset + (index - first) / fps
  "t_offset": 0.0,
  "cams": "E:/YTP2/3D Timelapse/renders/trost",   // dir holding _cam/; defaults to the frames dir
  "size": [854, 480], "duration": 8.0,  // only for pure graphics (no frames): black frames of this size and length
  "out": "E:/YTP2/3D Timelapse/renders/trost/gfx", "prefix": "gfx",
  "mp4": "E:/YTP2/3D Timelapse/renders/trost/trost_gfx.mp4",       // H.264 CRF 26
  "tracks": [ ... ]
}
```

All times are seconds in the segment. Every track takes `t0`, `t1`, and optionally `fade_in` and `fade_out` (seconds).
Draw order: full-frame maps, then inset maps, then plates, then text and lines with a soft drop shadow, then glitch, then fades.

| type | keys | notes |
|---|---|---|
| `place` | `place`, `year`, `sub`, `pos` = `tl` or `tr` | Top corner HUD in the form "SHIGANSHINA · 845" (Pirata One, year in Grenze gold), a gold rule that draws in, and the sub line ("Eren, age 10") |
| `caption` | `text`, `caps`, `top`, `y`, `size`, `color` | One line at the bottom centre (or at the top with `top: true`), with short gold rules on each side |
| `title` | `text`, `sub`, `y` (fraction of H), `size` | Big title in Ditty. Ditty has **no digits or punctuation**, so any text containing them falls back to Pirata One. Letter spacing widens slowly |
| `tag` | `name`, `sub`, and the anchor: `world: [x,y,z]`, or `world_keys: [[t,x,y,z],...]`, or `obj: "Eren"` (from `dump(track=)`) plus `offset: [0,0,1.8]`, or `screen: [u,v]` | Dot, leader line, shelf and name in Pirata One. Optional `color` (dot), `len`, `lean` (+ right, - left; default auto), `dir` (`up` / `down` / `auto`), `size`. Hidden when the anchor is behind the camera or off screen. The line draws in from the dot |
| `counter` | `from`, `to`, `run: [ta, tb]`, `mode` (`log` / `linear`), `ease` (`inout` / `out`), `round` (step while running), `label`, `label_end`, `prefix`, `suffix`, `approx_end` (adds "~"), `color`, `color_end`, `bar`, `bar_color`, `note`, `note_t`, `pos` (`br` `bl` `tr` `tl` `bc` or `[u,v]`), `size` | Digits sit in fixed-width cells so the number does not jitter. The bar shows value / max |
| `map` | `mode` (`full` / `inset`), `spec` (preset name, or a dict with `"preset"` plus overrides), `rect: [u,v,w,h]` (inset), `map_t0` | The map clock is `t - t0 + map_t0`. An inset is a dark card with a gold border and a drop shadow, rendered at 2x |
| `glitch` | `t` (cut time), `dur` (default 0.6), `strength`, `flash` | RGB split, slice displacement, scanlines, a few inverted blocks, and a teal-white flash on the cut frame. Used for Grisha's injection (shot 8) |
| `fade` | `in: [t0, t1]`, `out: [t0, t1]`, `color` | Fades from and to near-black |

### Map spec (`maps.py`, km, origin = Mitras, +y = north)

`view: [[t, cx, cy, height_km], ...]` (eased, log zoom). `walls: {"maria": [start, dur], ...}` draws each wall in from the south;
a wall left out is always shown, and `null` hides it. `wall_labels: t` letters the wall names and radii along each belt.
`districts: {"Shiganshina": t, "Trost": t, "Karanes": t, "Stohess": t, "Mitras": t, ...}`. `lost: [t0, t1]` turns the Maria
belt grey, sweeping out from Shiganshina. `route: {"pts": [[x,y],...], "t": [t0,t1], "color", "losses": n, "dash", "back": {...}}`
(a single route or a list). Also `island_label`, `compass`, `scale_bar`, `grid`, `vignette`, `ui_scale`.
Canon radii: Maria 480 km, Rose 380 km, Sina 250 km. Each wall has four district salients (N, E, S, W). Shiganshina sits on
Maria's south salient and Trost on Rose's south salient.

## 4. Per-segment plan (from EP1_plan_v2)

| shot | tracks |
|---|---|
| 1 title | full map `title` (8 s), `title`, top `caption`, fade in |
| 2-6 Shiganshina | `place` "Shiganshina · 845" + "Eren, age 10"; `caption` "Outer gate destroyed" / "Inner gate destroyed"; `tag` on Eren, Mikasa, Hannes, Carla, Colossal and Armored (`obj` via `dump(track=)`) |
| 3 | `counter` "Survey Corps returning" (N set out, M return) |
| 7 | inset map `loss` + `counter` land lost / refugees |
| 8 | `glitch` at the injection cut |
| 10 | full or inset map `march` + `counter` 250,000 → ~100 (`linear`, `bar`, `approx_end`, `label_end`) |
| 13 | `counter` "Titans inside Trost" (`linear`, rising) + squads lost |
| 20 | `counter` "Trost: soldiers dead" + `tag` Marco |

Demo timelines (working examples): `E:/YTP2/3D Timelapse/renders/graphics/timelines/*.json`.
