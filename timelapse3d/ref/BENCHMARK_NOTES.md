# Seoul 3D timelapse — benchmark notes

Source: `seoul timelapse.mp4` (1920x1080, 60 fps, 12:57, H.264 + AAC). Contact sheets: `sheet_01.jpg`, `sheet_02.jpg` (one frame every 10 s).

## Structure / editing
- **Effectively one continuous shot.** Scene-change detection finds no hard cuts (max scene score 0.16; cut threshold ~0.3). Location changes happen by the camera flying, not by cutting.
- The few spikes (~0:02, 3:06, 7:55, 8:29) are fast camera swoops or soft dissolves, not cuts.
- Time runs from 3740 BC to 2025. Each chapter gets roughly 10–20 s (about 50 chapters in 13 min). Early eras go fast; 1900–2025 gets about 70% of the runtime.
- The terrain stays fixed while the city grows on it: buildings, roads, bridges, walls and rail appear and disappear over time. Rivers change shape too (Han river sandbars and islands, Gangnam fields turning into a street grid).
- Special-event moments: the bridge exploding (5:30, a dark smoke column), the city burning (~6:00), and a night shot for Lotte World Tower (12:20, the only night scene, with glowing lights).
- Ending: the camera pulls up to a high, wide shot of the whole city with district labels ("SEOUL TODAY").

## Camera movement
- Low-to-mid altitude **oblique aerial**, about 25–45° below horizontal. There's almost always a horizon or mountain ridge in the top 10–20% of frame. It never looks straight down.
- Slow, continuous **drone-like glide**: forward dolly plus a gentle orbit. It eases between points of interest and lingers while each caption is on screen.
- It occasionally dips very low, at ground or treetop level (3:00, 3:30), for scale and parallax, then rises again.
- It follows linear features: the city wall along the ridgeline, the Han river curves, rail lines, and the Cheonggyecheon stream.
- On a reveal (a new bridge, tower or palace), it frames the object at the center or lower third and pushes in slightly.
- Over time the camera gets **higher and wider** as the city grows (village close-ups early on, broad metro views by the 2000s).

## Look
- Stylized low-poly / miniature look: lollipop trees, simple box houses (hanok-like roofs early, then white and red concrete blocks after the 1970s).
- Warm sun, soft shadows, light atmospheric haze toward the horizon, pale blue sky.
- Saturated greens with sandy-beige riverbanks and bare hills. Trees thin out in the 1900s and come back by the 2000s.

## On-screen graphics (HUD)
- **Top-right:** `year 1428` in a large serif, a person icon with the population (`109,408`) below it, and a small compass rose that rotates with the camera heading.
- **Top-left:** the era/state name (`Joseon`, `Korean Empire`), with a flag from the Korean Empire on.
- **Bottom-center:** a chapter title in ALL CAPS serif with a soft shadow ("THE STONE WALL"), plus a one-line serif subtitle with a fact or number.
- **In-world labels:** small white caps text placed on landmarks (CHANGDEOKGUNG, HANNAM BRIDGE). They fade in when the landmark is relevant.
- Text is white with a subtle drop shadow and no boxes or panels. The font looks like an old-style serif similar to Cormorant or EB Garamond. Ours would map to Pretendard for Korean, with a serif accent face.

## Audio
- A continuous music bed with no silence gaps over 1.5 s (mean −20 dB, peak −1.8 dB). There's no obvious voiceover, so the story is carried by the captions.

## Takeaways for our build (Blender)
1. One long camera path (a Bezier curve with a track-to empty), with eased speed and holds at each POI. Avoid cuts.
2. Drive the eras with a single `year` property. Keyframe the visibility/scale of building collections, plus bridge/road reveals (a grow-in or pop-up with overshoot).
3. Render plates and a data track (year, population, heading). Composite the HUD in post (ffmpeg or a compositor) so the text stays crisp and editable.
4. Pacing: about 12–15 s per chapter, compressing ancient eras and expanding the modern ones.
