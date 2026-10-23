# You, Elsewhere EP2: Voldemort's Room (Riddle House) - Blender look test

Goal: ONE photoreal still (1920x1080, Cycles) of the upstairs room of the abandoned Riddle House,
Little Hangleton, on Halloween night. Benchmark look: Ambient Worlds "Hogwarts Classroom" (3D-rendered,
believable, soft, painterly-real environment you could sit in for an hour). Detail matters a lot.

## Canon (Goblet of Fire ch.1) - keep it true
- Abandoned manor, empty ~50 years: thick dust, cobwebs, peeling wallpaper, warped floorboards,
  threadbare hearthrug. Old English country-house furniture (Victorian/Edwardian), nothing modern.
- A fire burning in the grate (NORMAL warm orange wood fire, NOT green) = main light.
- A tall high-backed armchair turned to face the fire (empty; nobody in the scene, no snake, no people).
- Windows: some boarded up, ivy pressing on the glass outside; far below in moonlight the village
  graveyard with a yew tree (can be a simple backplate/HDRI + a few silhouettes; very dark).
- Rainy October night (rain on the window glass).
- Small subtle hints only: a dusty side table with a few old books, an unlit candle stub, an old
  gold locket half hidden in dust (optional, tiny). No wands, no logos, no text.

## Camera / look
- Fixed camera, eye height ~1.2 m, 35 mm, view: fireplace + armchair left/centre, window right.
- Colours natural and muted (not saturated, not teal/orange AI look). AgX, medium-low contrast,
  warm firelight falling off into deep shadow; cool faint moonlight from the window.
- Atmosphere: light volumetric haze, visible dust motes in the firelight.
- Slight film grain only.

## Assets (CC0, no login)
- Poly Haven (api.polyhaven.com): models (armchair / chairs / tables / books / candles / shelves if
  available), PBR textures (old wood floor, plaster, brick/stone, wallpaper if any, fabric), HDRI night.
- ambientCG CC0 textures as fallback. Do NOT use anything needing a login or paid licence.
- Keep a credits list (asset name + URL) in assets_credits.md.

## Machine notes
- Laptop: Blender 5.2 at C:\All The Programs\Blender, GTX 1060. Another thread may be rendering
  (PEEK catacombs) on the GPU: check first; if busy, build the scene and render the still at lower
  samples (denoised) or wait, but do not stop the other render.
- Work folder: C:\Users\hw549\Downloads\YTP1\YouElsewhere\ep02_voldemort\ (this channel stays on C:).

## Output
- voldemort_room_look_v1.png (1920x1080) + a 960px JPG, the .blend, build script voldemort_room.py,
  assets_credits.md. Commit the JPG, script and credits (not the .blend/textures) to branch
  claude/project-thread-uxub9k under you_elsewhere/ep02_voldemort/blender_out/ and push.
- Report render time and what assets were used.

## Later (not now)
- 20 s seamless loop: fire flicker, rain on glass, drifting dust, faint candle/ember glow.
