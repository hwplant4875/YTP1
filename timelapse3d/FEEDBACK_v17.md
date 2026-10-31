# User feedback on full_onetake_v17 (10/31 18:37 UTC) — LAST PREVIEW before the final. Spec for v18.
"이제 최종본을 향해 다가가고 있어. 중요하지." Overrides older specs.

## Scope change
- The video ENDS BEFORE THE FOREST. Cut Part 2 and Part 3 entirely (formation, forest, Stohess, wall titan).
- Ending: after the boulder seal, the wall-corner mop-up and the night sky view of the burning titan corpses over
  Trost, rise straight up into the sky until Wall Maria, Wall Rose and Wall Sina are all in one frame; hold ~2 s,
  final caption. (Fallback if the map can't show all three: end on the full sky view of burning Trost.)

## Fixes
- Opening zoom-out is too large. The NEW frame-0 camera = the camera pose at 2 s into the CURRENT zoom-out
  (i.e. start already 2 s "zoomed out" and continue from there with the same easing).
- Colossal kick: the gate graphic has become transparent; fix it (opaque gate + wall material).
- Sky time-lapse (night -> morning while looking at the sky): exactly 1 second.
- 250,000 scene: excellent, keep. Make the number graphic show exactly and readably (counter reaches 250,000).
- Eren's leftover motion near HQ looks awkward (sped-up remains): zoom quickly into the HQ so Eren is never visible;
  pull the "Eren lying collapsed" state as early as possible so it is already visible when the camera zooms out.

## Make it COMPLETE (on-screen text and graphics)
- Bottom-centre captions (New Rocker, big, elegant, like the "Colossal Titan" title) that say what is happening at
  each major beat, e.g.: year/place (SHIGANSHINA, 845), "Wall Maria has fallen", the Armored Titan title at bottom
  centre like the Colossal Titan, evacuation to Trost, 846 the 250,000 counter, training corps / graduation, 850 Trost,
  the Colossal again, Eren's Titan, the boulder / Trost recaptured, the mop-up, the ending (three walls).
- Place names (SHIGANSHINA, TROST, WALL MARIA/ROSE/SINA), year HUD (Share Tech), name tags (Russo One, max 3; none at
  the training ground). Check every caption against the canon timeline (SCENE_BIBLE_v2.md) for wording and order.
- No overlaps: captions never cover tags/counters; safe margins; readable at 480p.

## Render
- One last 480p 15 fps PREVIEW of the whole thing (full_onetake_v18_preview.mp4 + sheet), push. The final 30 fps
  render comes only after the user OKs this preview.
