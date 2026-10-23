# Attack on Titan Season 1: Blender Design Bible

Scope: Shiganshina (845), the Walls, the Titans (pure, Colossal, Armored, Attack, Female), child Eren and Mikasa at the tree, distant uniformed figures, and the Paradis map with other S1 places.

## 0. How to read this document

- **[WIKI]**: stated in text on attackontitan.fandom.com (anime pages unless noted), or on an official anime info card ("Currently Publicly Available Information", CPAI / ACPAI panels).
- **[SEEN]**: observed directly in a saved or viewed anime frame.
- **[EST]**: our own estimate for building. These are starting values, not canon.
- **[MEMORY]**: recalled from watching the anime, not confirmed by a wiki image or text. Low confidence.
- Hex colours were sampled from frames, so they include scene lighting. Where a neutral **albedo** is given, use it as the base colour. Use the raw samples only to match lighting.
- Art style: use WIT Studio S1–S3 frames. Final Season (MAPPA) frames are used only where noted, for layout (the tree and hill, the Paradis map, the S4 Shiganshina aerial). Do not use them for character or Titan styling.
- Units: metres, unless a section says km. Blender: 1 unit = 1 m.

### Cross-section conflicts (decide once and use throughout)

| Item | Values found | Recommended default |
|---|---|---|
| Wall pier/pilaster spacing | ~18 m module (walls spec, Karanes/Shiganshina); 20–30 m (Shiganshina S1); ~35 m (Stohess, map spec) | **18 m** on district bulges; up to 35 m allowed on Wall Sina [EST] |
| Gate opening | 10 × 14 m (Shiganshina); 8–10 × 12–15 m (walls); 12–15 × 15–20 m (map) | **10 m wide × 14 m tall** [EST] |
| Trost boulder | 12–16 m long × 8–10 m thick (shifters); 10–13 m sphere (map) | **~13 × 11 × 9 m** flattened ellipsoid [EST]; must plug an 8 m hole |
| Tree trunk diameter | 2–3 m (Shiganshina spec); 1.0–1.3 m at chest, ~2 m at roots (characters spec) | **1.2 m at chest, flaring to 2–2.5 m at roots** [EST] |
| Tree hill height above town | 30–60 m (Shiganshina spec); 15–30 m (characters spec) | **~30 m** [EST] |
| Tree distance from town | 1–2 km; 0.5–1.5 km | **~1 km** north of the inner gate [EST] |
| Shiganshina canal side | S3 frame shows it on the left; S4 and S1 aerials put it on the east | **East side** (S4 + aerial) |
| Wall-top walkway surface | sandy stone pavers (Wall Sina ep25, Trost ep4); dark red-brown brick (Trost ep3) | Sandy pavers by default; brick variant for Trost if desired |
| Attack Titan burning-state eyes | Wiki: blue; forest frame: pale green-white | **Owner to decide**; default pale green-white (matches the frame) |
| Wall ring radii | km: Sina 250 / Rose 380 / Maria 480 (0.52 : 0.79 : 1.00); S4 map draws 0.36 : 0.64 : 1.00 | km values for real scale; map ratios only for a map-style shot |

---

## 1. Shiganshina District

### 1.1 Wiki facts
- [WIKI] Southern district of Wall Maria, "built within an outcrop of Wall Maria": a bulge of wall sticking out beyond the main ring.
- [WIKI] Outer gate in the outcrop wall, facing the Titan side. Inner gate in the main Wall Maria line.
- [WIKI] In 845 the Colossal Titan (60 m) kicked a hole through the outer gate. The Armored Titan (15 m) then broke the inner (back/north) gate.
- [WIKI] Walls are about 50 m high and about 10 m thick, with cannons along the top. Each wall has 4 districts at the 4 compass points.
- [WIKI, ACPAI1B panel] Maria→Rose ~100 km, Rose→Sina ~130 km, Sina radius ~250 km. Each district is drawn as a half-disc on the wall with a road through it from the centre outward (diagram not to scale).
- [WIKI trivia] Shiganshina "resembles Nördlingen" (round walled Bavarian town). Use Nördlingen's red-roof medieval plan as the real-world model.
- The wiki gives no district size, and has no image or text of the canal boats or the Jaeger house exterior. Those parts below are estimates.

### 1.2 Shape, size and Blender layout
- [SEEN] Plan: a U/D outcrop. Two roughly straight, parallel side walls run out from the straight Wall Maria line and meet in a semicircular far end. Depth ≈ width. (S1 aerial Walls.png: small U bulge with the river through it. S4 aerial: rounded far end, straight sides.)
- [EST] Width ~1.0 km (E–W, along Wall Maria), depth ~1.0 km: ~500 m of straight sides plus a semicircle of 500 m radius. (Scaled from house sizes and the 10 m wall-top width in the S4 aerial. General district bulge range from the walls spec: 0.8–1.2 km across.)
- [EST] Blender layout:
  - Wall Maria line along X at Y = 0. District extends toward −Y (south).
  - Inner gate at (0, 0). Outer gate at (0, −1000).
  - Outcrop wall: same 50 m height and 10 m thickness as the main wall.

### 1.3 Wall appearance at Shiganshina
(Full wall construction in Section 2.)
- [SEEN] Flat, pale, concrete-like surface split into tall panels by regular vertical pilasters/buttresses.
  - S1: thin flat pilasters ~2–3 m wide, projecting ~1 m. [EST] spacing 20–30 m (see conflict table; default 18 m module). The S1E2 inner-gate shot shows a faint horizontal band ~1/3 of the way up.
  - S3: buttresses taper, wide at the base and narrowing upward.
  - Top: flat paved walkway of rectangular stone blocks, low parapet, rails for cannon carriages.
- Colour [EST] neutral daylight **#A9A79E**. In-frame shading: overcast #8BA8C3, S4 #98A5BC, sunset #DDC997, dusk #484833.

### 1.4 Gates
**Inner gate (on the Wall Maria line, centred at (0, 0))**
- [SEEN, S3/S4] Pale stone, castle-like gatehouse built against the district side of Wall Maria:
  - Wide block of 3–5 storeys.
  - Tall square central tower with a pyramid roof; its top is level with or slightly above the 50 m wall top.
  - Flanking/corner towers with pointed cone or spire caps; square keep; crenellated parapets.
  - Colour **#C8C6C0** in daylight; dark grey stone at night.
- [SEEN, S1] A tall bright tower block at the centre of the far wall. A road climbs a hill beyond (north of) the wall, so the ground north of the inner gate rises.
- [SEEN, S1E2 breach shot, viewed not saved] After the Armored Titan's charge the opening is a tall, rough, rounded/pointed arch hole about the Armored Titan's height, full of bright light, with cracks spreading across the dark grey wall (#363530) and dust clouds at ground level.
- [EST] Gate tunnel ~10 m wide × 14 m tall arch through the 10 m wall. Gatehouse footprint ~60 × 30 m.
- Note: the S3/S4 castle may be a later rebuild; the S1 frame shows only a bright tower block. Build the castle-like gatehouse unless an S1 close-up contradicts it.

**Outer gate (tip of the U, at (0, −1000))**
- [SEEN] At ground level on the main avenue. No good anime close-up on the wiki.
- [EST] Arched opening of the same size (~10 × 14 m) with heavy doors (walls spec suggests a single heavy slab dropped vertically, portcullis-style).
- [EST] The 850 hole sealed by Eren's crouching 15 m Titan suggests a breach ~15 m tall × 10 m wide.
- [SEEN, S3] A straight road leads away from the gate through green grassland.

### 1.5 Canal / river
- [SEEN, S1 aerial] A blue-grey river runs N–S through the outcrop, continues north winding inside Wall Maria, and south outside.
- [SEEN, S4 aerial and 854 view] It is a straight, man-made canal, NOT through the centre but close to one side wall: on the **EAST** side (on the right when looking from the outer gate to the inner gate). Canal and inner gate meet Wall Maria about 1/3 of the district width apart.
- [SEEN] It leaves through the outcrop wall where the straight side meets the curve, bends slightly, then runs straight on through the fields outside.
- [SEEN, S3] One frame shows the canal on the left. The anime is inconsistent: follow S4 + aerial.
- [EST] Positions: centreline x = +380 m from y = 0 to the curved wall at ~(380, −825), then heading SE outside.
- [EST] Arched water gates where it passes under both walls, ~15 m wide × 8 m clear height.
- Cross-section [SEEN, dimensions EST]:
  - Vertical dressed-stone banks ~4–5 m deep.
  - Water ~20–25 m wide, teal **#5B8D96** (sky-lit #8EC6E2). (Map spec: canal water #4F9497 to #5D8F98.)
  - Narrow towpath/quay at water level on each side, ~4 m wide, **#6D6C5D**.
  - Paved street-level promenades, sand-grey **#998E73**, ~8–10 m wide.
  - One row of houses and a street between the canal and the side wall.
- [SEEN, S3/S4] ~3 tall gantry frames span the canal: paired square posts ~10–12 m tall [EST] with a top crossbeam. Probably footbridges or lift/crane frames; function unclear.
- [WIKI] Sail-less boats, pulled by pulleys and rails, carried people by river between Shiganshina and Trost (Ep2 evacuation).
- Boats / ferry landing: NOT pictured on the wiki. [MEMORY, S1E2] Refugees board crowded, low-sided, flat-bottomed wooden riverboats at stone steps/quays near the inner gate; boats leave through the wall and carry on along the river at sunset.
  - [EST] Boat: 12–18 m long, 3.5–4 m beam, freeboard ~0.6 m, poles/oars, wood **#6B4E35**.
  - [EST] Landing: stone stairs down to the quay beside the inner gate.

### 1.6 Streets and plaza
- [SEEN, S4 aerial] One wide main avenue runs straight from the outer gate to the inner gate. Streets form concentric rings around the inner gate with radial streets between them. A ring road follows the inside of the outcrop wall.
- [SEEN] Streets are narrow, 3–6 m [EST]. Packed earth **#B59D6D** with stone-slab steps and kerbs. Town sits on gentle slopes with many stairways.
- [SEEN] A stone arched passage carries a building over an alley: rough beige blocks **#C1B59D**, tiled roof.
- [SEEN] A tall square bell/clock tower with an open octagonal belfry and dark pointed cap rises above the houses. A large 3-storey civic building with arched windows. ([SEEN, S1E1] the Colossal face also appears between church spires.)
- No central monument is stated. The square pond seen at the centre in 854 is the post-850 crater: **do NOT build it for 845**.
- [EST] Put a market square with the bell tower near the middle of the main avenue.

### 1.7 Buildings
- [SEEN] Central-European half-timbered (Fachwerk) houses, 2–4 storeys (some 5), packed wall to wall.
  - Ground floors often rough beige stone **#C1B59D / #AC9C7E**.
  - Upper floors: dark brown timber frame **#3B2A20** with cream plaster infill **#D8CDB4**, some pale grey-blue. X and K braces. Upper floors overhang (jetties).
  - Small multi-pane windows with dark frames, gabled dormers, square stone chimneys.
- Roofs:
  - [SEEN] Steep gables ~45–55° in orange-red clay pan tiles with clear courses.
  - [EST] Base albedo **#9A5A40**, varying **#6E4A3C** to **#B5694A**.
  - From afar they read as muted red-brown **#7D6660 to #917550**, with a few blue-grey slate roofs **#6B7C8F** mixed in.

### 1.8 Jaeger house (wiki has no exterior image; all EST from S1 shots viewed, not saved)
- Modest 2-storey half-timbered house, terracotta roof, with a basement. In the residential blocks within reach of debris from the outer gate.
- Reached by stone steps with wooden post-and-rail handrails, roofs and the wall visible beyond (S3 flashback of Carla and Mikasa).
- [WIKI/SEEN] In S1E1 a large chunk of wall/rock kicked off by the Colossal crushes it; the X-braced frame and tiled roof collapse inward. Carla is trapped under the debris.

### 1.9 Hill with the big tree
(Character staging in Section 4.4.)
- [SEEN, finale frame] A single huge broadleaf (oak-like) tree on a grassy hilltop. Very thick trunk, ivy-covered and dark mossy **#354D37**. Wide rounded canopy **#648064** (sunlit **#83AE5F**) with low spreading branches. Hill grass **#658E2C to #83C843**, shrubs **#43724D** on the slope.
- [EST] Town spread out below, ~1 km away and ~30 m lower (see conflict table).
- [EST] Position: inside Wall Maria, on the rising ground north of the inner gate (S1 frame shows a road climbing a hill beyond the wall), since the children could not go outside the walls. [WIKI] Eren's page calls it "the tree he liked to nap under outside of Shiganshina District" (i.e. outside the district, not outside Wall Maria).

### 1.10 Surroundings
- Inside Wall Maria: patchwork farm fields (olive-yellow **#B8B079**), dirt roads, small hamlets of 10–20 red-roofed houses, the river winding north.
- Outside the outcrop wall: open green grassland, conifer groves (spruce/fir), forested hills **#464330**, blue-grey mountains on the horizon.

---

## 2. The Walls

### 2.1 Overall layout
- [WIKI] 3 concentric walls: Maria (outer), Rose (middle), Sina (inner). Each ~50 m tall, ~10 m thick (anime Walls page, citing official guidebook p.437).
- [WIKI] Maria→Rose ~100 km, Rose→Sina ~130 km, Sina→centre ~250 km. Ground rises toward the centre.
- [WIKI] Each wall has 4 districts: towns inside a bulge on the wall's outer side.
  - Maria: Shiganshina (S).
  - Rose: Trost (S), Karanes/Calaneth (E), Krolva (W), Utopia (N).
  - Sina: Stohess (E), Ehrmich (S), Orvud (N), Yarckel (W).
- [WIKI] Each district has an outer (south-facing) gate and an inner gate where it joins the main wall. The Colossal kicked the outer gate at both Shiganshina and Trost. The Armored Titan broke Shiganshina's inner (north/back) gate.
- [WIKI] Scale check: the 60 m Colossal shows head and shoulders above the 50 m wall.
- [SEEN, Trost/Karanes aerials] Each district is a horseshoe/semicircle bulge whose ends join the long main wall. Inner gate at the back in the main wall; outer gate at the tip. At Trost a canal runs alongside the bulge wall and passes out through it, with bridges.
- [EST] District bulge ~0.8–1.2 km across.

### 2.2 Wall face construction (most important for the model)
- [SEEN] Not a smooth cylinder: a ring of flat rectangular panels with a narrow full-height vertical pier between every two panels.
  - On curves each panel is a straight chord, so the wall reads as a many-sided polygon.
  - Outer side: piers project past the panel face.
  - Inner side: slim flat strips (pilasters).
  - Faces vertical; no base slope, no visible plinth. No battlements or crenellations.
- [EST] Module (Karanes inner face + Shiganshina ep1):
  - One module (panel + pier) every ~18 m (~0.35 × wall height).
  - Panel ~15–16 m wide.
  - Pier ~2–3 m wide, projecting ~2–4 m from the panel face.
  - Alternatives: map spec measured piers ~35 m apart on Wall Sina (Stohess), projecting 2–3 m; Shiganshina S1 tapered buttresses in S3.
- [SEEN] Pier tops: a raised block running across the full 10 m walkway width, [EST] ~1.5–2.5 m above the walkway over the panels. Walkway profile is stepped: low over panels, high over piers. Some pier tops carry small buildings (Trost ep4).
- [SEEN, inner face] Same broad panels and slim pilasters; pilasters rise slightly above the wall top. A pale horizontal band (string course) roughly 1/3 to 2/3 of the way up (Door of Wall Rose shot; Shiganshina inner-gate shot shows it ~1/3 up).
- [SEEN] Top edge: plain capping course projecting slightly. Outer face: dark vertical slots where pier meets panel (Wall Rose top shot, ep26/S2).
- [EST, map spec] Small blocky parapet ~1.2 m high along the top.

### 2.3 Material, texture, colour
- [WIKI] Very hard material. In reality formed from hardened Wall (Colossal) Titans hidden inside; the ground under the walls is the same material.
- [SEEN] Wide shots: one solid stone mass, no visible block joints, mottled stains, vertical weathering streaks, fine cracks.
- Colours sampled:
  - Lit face, daylight: **#A8A08C to #B4AB9A** (warm light grey-beige). Trost/Karanes in sun: #C8C1A4.
  - Shadow/skylight: **#585C7B** (blue-grey). Trost/Karanes shade: #7D8496.
  - Karanes aerial panel: #767E58 (haze-green; do NOT use as base).
  - Wall Sina (Stohess), warm light: #8A8A68, looks smoother.
  - Walkway lit: **#B4AB8F to #C2AE8B** (sandy). Sunset walkway (ep25): #C9A175.
  - Face at sunset: #312628. Night: #56698F.
  - Shiganshina neutral [EST]: #A9A79E.
- [EST] Recommended base albedo **#A39A86**, roughness 0.85–0.95, darker grime at the base and along vertical streaks.

### 2.4 Wall-top walkway, rails, supplies, buildings, lifts
- [WIKI] Rail lines run around the whole wall so cannons can be grouped on one spot. A cannon must be firmly fixed before firing, or recoil throws it off the track. At Trost the Colossal swept cannons and rails off the wall top.
- [SEEN] Walkway paving: rectangular stone pavers in running bond along the wall. [SEEN, Trost ep3] Variant: dark red-brown brick **#6B4A3A** (shade #322920).
- Rails [SEEN ep4/5]: one track (2 rails) on wooden sleepers. Rails dark iron **#5A4E50 to #685451**; sleepers brown wood **#573424**.
  - [EST] Gauge ~1.5 m, running roughly along the centreline of the 10 m walkway.
- [SEEN, ep25 Wall Sina] At a raised pier top the rails ramp up and over it on a stacked-log crib: ~5–6 round logs piled in a pyramid, each ~0.4 m across [EST].
- [SEEN] Small open iron/wood ore-cart tub, [EST] ~1.5 × 1 × 0.8 m, rides the rails with supplies.
- Supplies [SEEN ep4/5]: wooden crates [EST] ~0.6–0.8 m cubes, dark brown slatted boards **#53311B** with corner battens, stacked 1–3 high next to cannons. Barrels not seen; optional [EST].
- Wall-top building [SEEN, Trost ep4] on a raised pier block:
  - Base: pale stone/concrete plinth **#9B9786**, ~2–3 m high [EST].
  - Upper storey: half-timbered, dark timber frame with stone/brick infill **#8E847C**.
  - Roof: terracotta tiles, gabled or hipped (Trost ep3 guardhouse roof **#8A5A50**).
  - Roof-top metal pipe frame with posts and top beam.
  - [EST] Guardhouse or winch/lift house.
- Lifts: [WIKI] Scouts "ride the lift to the top of the Wall" at Trost (S3). [SEEN, CPAI ep5] Lattice-framed cage with gabled housing straddling the wall edge; a trussed frame runs down the face. [EST] Model as a timber-truss shaft on the inner face, wooden platform on ropes, winch house on the top.
- Stairs: none shown [EST: leave out, or hide inside a pier].

### 2.5 Cannons (Garrison wall-mounted artillery)
- [WIKI] Smoothbore (inaccurate), breech-loaded, fired by pulling a cord to a firing pin, ~20 s reload. Shot types: high-explosive shells (high damage, very poor accuracy) and grapeshot (takes off limbs to slow Titans). Can aim straight down the wall face. Ground cannons also guarded inner gates.
- [SEEN, CPAI ep5 FRONT/SIDE/ACTION] Barrel on trunnions between two upright side frames on a base plate; a large ~90° toothed/banded quarter-circle sector under the barrel sets elevation; ACTION view shows the barrel swung to vertical, pointing at the ground over the wall edge.
- [SEEN, ep4 colour]:
  - Barrel gunmetal **#807D7F** lit, ~**#4A4A50** shaded (Trost ep3: #69676A). Muzzle swell, ~3 reinforcing rings, round knob at the breech.
  - Carriage: wood **#504339 to #64492D**, iron-banded quarter-arc cheeks, bolts, straps.
  - Base: round wooden turntable disc with iron rim, sitting across the rails (rotates 360°, rolls along the track).
- [EST] Barrel ~3.2–3.5 m long, bore ~0.18 m, outer Ø ~0.45 m at breech. Turntable ~2.8 m across. Barrel top ~1.8 m above walkway.
- Spacing: [EST] Karanes inner face ~2 guns per 18 m module (~1 gun per 9 m); Trost ep4 2 guns within ~10–12 m. [WIKI] Walls too long to guard everywhere, so defences concentrate at districts. → Dense guns on district bulges (every ~9–18 m); sparse or none on long stretches.
- Ammunition [SEEN, CPAI ep5]: grapeshot = long canister, 4 rows of balls in a casing, pointed nose. HE shell = shorter oval shell, banded middle.

### 2.6 Gates
- [SEEN, Trost aerial] The inner gate occupies one whole module of the main wall: a full-height, slightly darker, set-back flat block between two piers, with a large rectangular door frame at the bottom and a framed rectangle near the top (gatehouse built into the wall). A gate frame is also visible at the bulge tip (outer gate). Trost's inner gate reads as a tall dark recessed slot, NW of district centre.
- [SEEN, Karanes aerial] Low gatehouse at the foot of the outer gate, two slate-blue roofs **#5F7C8A**.
- [SEEN, "Door of Wall Rose", S1 era] Brick gatehouse against the wall face:
  - Central red-brown brick tower **#6E4A3E** (daylight), tall pointed (gothic) arch gateway outlined in stone voussoirs.
  - Goddess shield plaque on the tower above the arch.
  - Two lower side wings with stepped/corbelled brick tops and small pointed-arch doors.
  - Behind: grey wall with darker pilasters and pale horizontal band.
- [SEEN, S3/S4 Shiganshina] Pale castle-like inner gatehouse with corner towers and central tower rising above the wall top (Section 1.4).
- [WIKI] Doors were "closed" to seal a district after evacuation. Refugees left Shiganshina by ferry, so water gates exist where canals pass through.
- [EST] Door: single heavy slab dropped vertically (portcullis-like). Opening ~8–10 m wide × 12–15 m tall (from the Shiganshina breach hole ~0.5 panel wide, and the boulder big enough to plug Trost's hole). [WIKI, manga] Trost outer-gate hole was 8 m.

### 2.7 Emblems and crests
- [SEEN, CPAI ep1] All three emblems share a shield: flat top, straight sides for ~60% of height, then tapering to a point (home-plate shape). Border frame; banner at top reading "WALL MARIA" / "WALL ROSE" / "WALL SINA". A cross (vertical + horizontal bar) behind the head splits the field into quadrants. Goddess head in profile facing **LEFT**:
  - Maria: spiked tiara-crown over a headband with a round ear-guard, curly hair.
  - Rose: square/castellated crown with a band, long wavy hair down the back.
  - Sina: spiky tiara with a ribbon, curled pinned-up hair.
- [SEEN, gate plaque] Carved stone relief: pale grey-blue head and frame **#9AA4B4** (lit), bluish/gold background field, proportions ~1 : 1.2 (w : h). [EST] ~6–8 m tall on a full-size gate.
- [EST] Maria on Shiganshina, Rose on Trost and Karanes, Sina on Stohess (wiki does not say which is on which gate).

### 2.8 Wall Cult (Order of the Walls) church (viewed, not saved)
- [SEEN] Dim stone hall, grey-green tile floor, inlaid brown circular ring marking a round congregation area, tall arched mullioned windows, benches along the walls.
- Clergy: long dark grey coats with white piping, gold neck collars/gorgets.
- [WIKI] Pastor Nick knew about the Titans inside the walls.

### 2.9 Damage and set dressing
- [SEEN, Stohess ep25] Where the Female Titan damaged Wall Sina, a giant Wall Titan face shows through. The Scouts cover it with a patchwork of multicoloured dyed cloth sheets hung on ropes from the wall top.

### 2.10 Coverage gaps
- No wiki close-up of an outer gate door from outside. For more accuracy, grab frames from S1 ep1 (Shiganshina gate opening for returning Scouts), ep5–6 (Trost inner gate), ep17 (Karanes gate departure), S3 ep37 (Trost lift).
- The Trost aerial in the walls folder is S2; its design matches S1.

---

## 3. Titans

### 3.1 Size reference
- [WIKI + ACPAI8B size card] Pure Titans 3–15 m (infobox "2–15 m average"). Card classes: **60 m, 15 m, 7 m, 5 m**; Wall **50 m**; human ~**1.7 m**.
- Colossal **60 m**. Armored **15 m**. Attack (Eren) **15 m**. Female (Annie) **14 m**. Smiling Titan [EST] 12–15 m.
- [WIKI] Nape weak point: **1 m tall × 10 cm wide**; for shifters the human body sits inside it.

### 3.2 Pure Titans (general)
- [WIKI] Naked humans with the normal number of limbs; mostly masculine bodies; no reproductive organs (smooth, doll-like groin). Deformed proportions (enlarged head, small limbs). Some have feminine faces on masculine bodies. Mouths "exceptionally wide" with "an enormous number of small, square teeth", mostly no canines. Bodies "unusually light", capable of "amazing bursts of speed". Steam from wounds while regenerating. A dead Titan evaporates to a skeleton then to nothing.
- [WIKI] Abnormals: unpredictable, "speed-walking or running, performing great jumps", often ignore lone humans; a few move on all fours.
- [SEEN] Hair: crew cuts, buzz cuts, balding, bowl cuts, long hair. No body hair. Hair colours **#2B2622, #5A4234, #9A7350, #8E5A3C**.
- [SEEN] Faces: vacant smiles, gaping mouths, bulging eyes.
- [SEEN] Skin range: pale peach **#E2BFA6**, peach-tan **#C99A78**, ruddy pink **#C27C6C**, tan-olive **#A9805E**, dark tan **#7E5A44**. S1 shows a faint mottled/cellular vein pattern ~10% darker on backs and arms.
- [SEEN] Body types: thin, average, fat (a fat dark-haired Titan in Trost). Nipples mostly absent; groin smooth.
- [SEEN] Movement: normal Titans lumber with a swaying gait, arms loose, head tilted. Abnormal sprint (S1): upright, forward lean, arms swinging, long strides, dust at every footfall.
- [EST] Head-to-height ratio 1/4.5–1/6 (human 1/7.5). Arms reach mid-thigh. Walk cycle ~1 step every 1–1.5 s, stride ~0.4 × height.
- [EST] Shading: toon/NPR with drawn fibre lines, not realistic SSS.

### 3.3 Smiling Titan (Dina)
- [WIKI] "Very tall", male-looking. Lips "fixed wide open, exposing its teeth and gums at all times". "Thin, emaciated frame with stocky proportions", ribs visible, "unusually-long neck". Hair "medium-length, light", "only barely reached down to its neck". Eyes "small, deeply sunken gray". Classed as Abnormal; went straight to the Jaeger house.
- [SEEN] Emaciated, visible ribs, very long neck, long thin arms, forward-leaning pose.
- Hair: chin-length centre-parted bob hanging over the cheeks, longer at the back. Daylight light-to-medium brown / dark blonde, base **#7A5A44**, highlights **#C8A07C**. Backlit in S1E1 it reads near-black.
- Face: permanent wide grin, lips pulled back, full upper and lower rows of ivory teeth **#E6DCC0**, red gums **#B83D25**. Prominent nose. Small sunken eyes with dark rims.
- Skin: neutral peach-tan **#C89A7C**.
- [EST] Height ~12–15 m (head clears 2–3-storey houses; fist holds a 1.7 m adult).
- Carla scene [WIKI/SEEN]: Hannes arrives, faces the Titan, "stands catatonic in fear", then carries Eren and Mikasa away, leaving Carla under the house debris. The Titan pulls Carla out, crushes and eats her. It holds her up in one fist against an orange-smoky Shiganshina sky, in profile, hair hanging behind.

### 3.4 Colossal Titan (60 m)
- [WIKI] Transformed outside Shiganshina's southern gate and kicked a hole in it, letting Pure Titans in. Strong enough to destroy the gate with one kick and throw houses. Releases huge amounts of steam at will; can evaporate its whole body instantly. Long steam release strips the muscle down to the skeleton.
- **Skin:** none. Exposed red striated muscle, fibre lines as fine parallel strokes. Pale bone/tendon at fixed places.
- **Face, pale areas:** forehead and cranium (faint vein lines), nose, a band along each cheekbone, a band along the jawline ear-to-chin, the ears (normal human shape).
- **Face, red muscle:** large oval on each temple, big vertical striated blocks on the cheeks, red fan around/under each eye, red block under the lower teeth on the chin.
- **Forehead:** dark vertical crease from forehead down the nose bridge; dark star-shaped furrow at the brow centre.
- **Mouth:** no lips. Full rows of square ivory teeth top and bottom; no cheeks, so teeth are visible from the side back to the molars. Gum line shows.
- **Eyes:** deep dark sockets under a heavy brow, small grey-green irises.
- **Hair:** none; completely bald, no eyebrows.
- **Body tendons:** white star/cross at top of sternum + white line down the sternum; white clavicles; white lower borders on pectorals; white costal arch; 8-pack of red abdominal blocks separated by a white grid, white linea alba; white inguinal V; white strips down outer thighs (IT band); white kneecaps; white strip down each shin; white bands at ankles and tops of feet; white strips along outer forearms. Back: pale diamond between the shoulder blades (trapezius aponeurosis), two red patches on the back of the skull. Fingers red with pale tendons.
- **Proportions** (size card at ~15.9 px/m):
  - Head ~6.2 m tall × ~3.2 m wide (~1/9.7 of height; small head).
  - Very thick neck; trapezius slopes into massive shoulders.
  - Width across shoulders incl. hanging arms ~19 m.
  - Width across hips/thighs ~13.5–14 m.
  - Arms hang to mid-thigh.
  - Against the 50 m Wall: wall top at its upper chest, just below the clavicles. Head, neck and tops of trapezius rise ~10 m above the wall.
- **845 appearance [SEEN]:**
  - A white-yellow lightning bolt down the left edge of a huge mushroom-like column of steam/smoke, pink-grey/tan **~#C9A08A**, rising behind the Wall.
  - A red skinless hand grips the wall top, fingers curled over the parapet, palm down.
  - The face rises above the wall top shedding heavy white steam; orange embers float around it.
  - Golden-orange haze lighting. From street level the red head/hand is a small blob breaking the wall's top line at the base of the plume.
  - [MEMORY, partly confirmed] Sequence: a single bolt strikes outside the wall, flash, then plume, then the hand appears.
- **Colours** (recommended bases):
  - Muscle **#B8402C**; highlight streaks **#F08C6E**; deep fibre lines **#5E1A14**.
  - Bone/tendon **#DCC6B2** (sampled #D5BDAB–#DDC7B5); shadow **#A8907E**.
  - Teeth **#E2D6B8**; sockets **#4A3530**; iris **#6E6A58**.
  - Steam **#E8E4DE**, semi-transparent; embers **#FF9A40**.

### 3.5 Armored Titan (15 m)
- [WIKI] Whole body covered in "plated, armor-like segments of hardened skin" that break ODM blades and survive cannon fire. Fully armoured it runs only at moderate speed; can drop plates (e.g. behind the knees) to move faster. In 845 it charged and broke the north (inner) gate. Modelled on wrestler Brock Lesnar.
- **Build [SEEN]:** bodybuilder bulk, huge trapezius and deltoids, thick neck, narrow waist, long arms; slightly hunched, fists hanging.
- **Plate layout [SEEN]:**
  - Face mask: forehead plate, vertical seam down forehead and nose, brow plates over deep sockets, nose plate, cheek plates, jagged zigzag crack for the mouth line. Red striated muscle at the sides of the face and jaw hinge. Ears visible.
  - Neck sides: ribbed horizontal segmented plates.
  - Shoulders/arms: trapezius plates, big rounded deltoid pauldrons, biceps and forearm plates, dark ring at each wrist.
  - Chest: two large pectoral plates with a dark red seam between.
  - Sides/abdomen: 4 finger-like serratus/rib plates per side; central stack of segmented abdominal plates (~3 pairs plus a lower block).
  - Legs: thigh plates, kneecaps, shin plates, ankle bands; plated feet.
  - Exposed red muscle strips: outer flanks (armpit to hip), inguinal crease, outer thighs, outer and back edges of calves. In S1 these strips glow orange-red.
  - Back plated along trapezius and lats.
- **Hair:** very short, slightly spiky crew cut, platinum ash-blond **#D2CCBA**, shadow **#8C8878**.
- **Eyes:** glowing white **#FFF8E0**, no pupils.
- **Colours:** plates khaki-ochre base **~#9C8660** (warm S1 light #AC8553–#C6A363; overcast olive-grey #79766E); seams **#3A3024**; exposed muscle **#8A3A24**, S1 rim to **#C55C30**. Material hard, slightly glossy, stone-like, with hand-drawn crease lines; gold edges on plates in neutral light.
- [EST] Plate seams ~2–4% of body width.
- **845 scene [SEEN]:** charges the inner gate shoulder-first, head down; leaves a tall rough arch-shaped hole full of bright light, cracks across the dark grey wall **~#363530** (regular vertical pilasters), dust clouds at ground level.

### 3.6 Attack Titan (Eren, 15 m)
- [WIKI] 15 m. Anime debut ep8 ("Small Blade"); called "Mysterious Titan"/"Berserk Titan" in ep8–9.
- [WIKI] Shoulder-length black hair ("grazes his shoulders"); elongated ears (pointed) and tongue; prominent hooked nose; deep-set eyes with a third transparent eyelid on both eyes; no lips and no cheek flesh, every tooth exposed in a jagged skull-like grin; roars, cannot speak; lean, well-proportioned, very muscular (not pot-bellied or skinny); smooth crotch.
- **Normal state [SEEN]:**
  - Hair: messy, tousled, to shoulders/collarbone; heavy fringe over forehead and part of the eyes; strands across the face. Near-black in shade #181818, dark brown in daylight #3b2f23–#554536, highlights #a79b8d. Albedo **#2a2019**.
  - Ears: long, pointed, elf-like; sweep up and back from about eye level; tip pokes through the hair at/just above the top of the skull; length ~1/3 head height; skin-coloured.
  - Mouth: two continuous rows of rectangular teeth (upper and lower) from centre back almost to under the ear, both sides; ~10–12 teeth per row visible per side; striated cheek muscle lines around them. Teeth ~**#d4c0ab** daylight, #393836 shade.
  - Eyes: sunken, dark under-lines, angry narrowed look. Full-body Trost shot: **glowing green** (sampled #749f69). Emission **#74a06a**, core **~#b8e0a0**. Close-up iris grey-green.
  - Skin: warm tan-brown; daylight lit #d2c1aa, mid #a78974, shadow #704d3a; steam shot redder #745b57 lit / #32262a shadow. Albedo **#a5806a**, warm reddish SSS, fine hatching/vein texture over muscles.
  - Body: very defined chest, 8-pack, long arms (hands to mid-thigh), long legs; standing pose leans forward with raised shoulders. Fighting pose: boxing guard, lead fist at chin height, rear fist guarding the jaw.
  - Steam: pale blue-white **#c5d2db, #b6bfc8**, wrapping the body, pouring off shoulders and torso.
- **Burning state** [WIKI]: boulder carry, forest fight, end of Stohess ("turns dark and fiery... with only one arm and leg"): body deep black with burn marks, eyes **blue**, teeth **sharp** instead of straight.
  - [SEEN, boulder carry ep13]: boulder across the back of the neck and shoulders, both arms up and behind holding it, filling the frame width. Irregular flattened ellipsoid, grey-brown (#695b56 / #5b4e49 in warm light), albedo **#7a706a** (map spec alternative: charcoal-brown **#4A3F3A** with lighter fracture faces). Skin torn into ragged strips, red muscle on arms and torso (lit #8c6c63, shadow #322422). Face in shadow, teeth showing. Orange embers **~#ffb040** and steam; warm orange evening sky.
  - [SEEN, forest fight ep21]: body darkened **#6e3c2c / #46281c** with orange-hot lava-crack burn patches between ribs and abs (**#e2b77b** and brighter). Jaw wide open, pointed saw-like teeth. Eyes glow **pale green-white** (conflicts with wiki blue; owner to decide). Hair rim-lit orange.
- [EST] Proportions: ~8 heads tall (head ~1.9 m crown-to-chin); shoulders ~4.2–4.5 m; hips ~2.6 m; arm span ≈ height; hands hang to ~45% of height; ear tip ~0.3 m above the hair; nape cut zone 1 m × 0.1 m (stated) centred ~1.2–1.5 m below the crown.
- **Trost boulder** [WIKI]: sat in the middle of Trost; Eren lifts it "albeit with difficulty", carries it a long way, slams it into the breached gate, sending out a large shock wave (ep13 "Primal Desire"). [EST] Size ~12–16 m long × 8–10 m thick (shifter spec, wider than ~3 Eren shoulder widths) vs ~10–13 m sphere (map spec); default ~13 × 11 × 9 m. [EST] Position: open square ~300–600 m NNW of the outer gate, straight main street to the gate.

### 3.7 Female Titan (Annie, 14 m)
- [WIKI] 14 m; anime debut ep17. Face and build close to Annie's. Body "mainly exposed muscle tissue" with "limited skin coverage"; **fingers made of bone**. Face "laden with muscle lining, notably underneath her cheeks", so the mouth can stretch very wide. Teeth yellowish. Lean, strong, clearly female; Annie's martial-arts stance, both fists raised.
- [WIKI] Hardening of chosen skin areas shatters steel blades; one blow can take off a limb or head (decapitates Eren in the forest). Attracts pure titans with a scream. At the end of Stohess she climbs Wall Sina; Mikasa cuts her fingers; she falls and encases herself in crystal from the nape; the crystal is moved underground.
- Hair [SEEN]: short blonde chin-length bob, long side-swept bangs over one eye, messier than Annie's (no bun). Lit #d7c175 / #dfce93, shadow #886034. Albedo **#c9b16a**.
- Face [SEEN]: Annie's face, small nose, **full closed lips**; pale grey-blue, washed-out irises; a **dark band from under each eye down the cheek #613f2d** ("muscle lining"); faint seam/scar lines on chin and jaw.
- Skin: pale beige-pink, lit #dbb499, mid #be8d71. Albedo **#d9b49b**.
- Exposed muscle: bright red-orange (peaks #e9462b, mid #b05f42). Albedo **#b8321f**, fibres **#e5734e**.
- **Muscle map (front):**
  - Arms: fully red from shoulder/deltoid to wrist (sleeves).
  - Hands/fists pale; knuckles and fingers bone-white **#ab9f8a** (warm light).
  - Neck, trapezius, collarbones, breasts: pale skin; breasts skin-covered, no nipples.
  - Flanks: red band armpit to hip (obliques/serratus).
  - Belly: red vertical strip from under the breasts to the navel, 6-pack visible, ~1/3 torso width.
  - Pelvis: smooth pale V to the crotch, no genitals.
  - Thighs: long red strips separated by pale gaps (outer quad, front centre, inner).
  - Knees pale. Shins/calves: red outer side, pale inner side.
  - Ankles pale with 2–3 thin ring lines.
  - Feet bare; one foot more red at heel and top, the other pale.
- Pose: boxing guard, both fists in front of the face, knees slightly bent.
- [EST] Proportions: ~9 heads (head ~1.55 m); shoulders ~3.2 m; waist ~1.8 m; hips ~2.5 m; crotch ~52% of height (~7.3 m); knee ~28% (~3.9 m); long slim legs. Next to Eren (14 : 15) her head top is at about his brow.
- **Hardening [SEEN, Stohess]:** forearm becomes iridescent opal/quartz-like: blue-violet speckles **#8a9dc7**, pale lilac **#c7c4d4**, dark slate **#57515f**, white sparkles **#ffffff**. Glossy, crisp edge against normal skin.
- **Crystal [SEEN, ep25]:** upright elongated egg with rounded-pointed top, large irregular triangular/diamond facets; translucent silver-white with dark internal facets and strong highlights (**#c6b096** in warm light). Annie inside, upright, head bowed. Underground it hangs from ~20+ dark cables fanning out to stone-block walls, on a wooden A-frame cradle. [EST] ~2.5 m tall × 1.3 m wide, ~20–30 facets (Annie 1.53 m).

### 3.8 Transformation, steam, embers
- [WIKI] Shifter draws blood (Eren bites his hand) with a clear goal; "a burst of energy was released (usually a bolt of lightning or an explosion), followed by the generation of the Titan body and a release of hot steam."
- [SEEN, ep21 forest] Body forms in mid-air inside a dome/cage of white-gold crescent light streaks curving outward and down like claws/ribs. Blinding yellow-white core at head/upper chest **#eaeada / #eae2be**, warmer streaks **#d5c8a4**, scattered orange embers, dark forest behind **#232a17**.
- [MEMORY/EST, ep8, 21, 24] Golden-yellow lightning bolt **~#ffe680** with white core from a clear sky onto the shifter → spherical flash/shockwave → debris burst → big steam cloud with the Titan rising → ~3–10 s of thick steam off the new body.
- [EST] Steam: white **#e6eef2**, density thinning with height, slow upward drift, emitted from all skin, strongest from wounds.
- [EST] Embers: orange **#ffb040 to #ff7a20**, emissive, tiny.

---

## 4. Characters

### 4.1 Scene facts: the S1E1 tree
- [WIKI] Year 845; Eren and Mikasa about 10. Eren "awakes from a dream crying"; Mikasa asks why. They walk back to Shiganshina and meet Hannes and the Garrison gate guards, who are drinking. Guards say the Walls are 50 m high.
- [WIKI] Eren carries "firewood ... bundled on his back". Later Mikasa throws him against a wall, "causing the firewood ... to scatter".
- [SEEN] The opening tree shot is from Eren's eye-line looking UP at Mikasa leaning over him: Eren lies on his back on the grass under the canopy.
- [EST] Eren pose: supine at the base of the trunk, head and shoulders slightly raised on a root or the trunk; arms loose at his sides; legs straight, one knee slightly bent; wet tear streaks on his cheeks; his firewood frame set down upright, leaning against the trunk ~0.5–1 m from him.
- [EST] Mikasa pose: standing at his side, bent forward ~35–45° at the waist, hands near her knees, face ~0.8–1.0 m above his, hair falling forward past her shoulders.
- [WIKI] No basement key at the tree in E1 (the key on a string comes later).

### 4.2 Child Eren (age 10)
- [WIKI] "brown trousers, a green shirt with string tassels at the collar, a maroon coat, and simple brown shoes". Hair "short and dark brown", middle-parted curtain bangs. Eyes "teal-green". Complexion "somewhat tan".
- Height: [WIKI] adult 170 cm (850). [EST] age 10: 1.35–1.40 m, head ~21–22 cm (~6.3 heads tall).
- Coat: maroon-brown, open front, long sleeves, hem at the hip, no visible buttons. Albedo [EST] **#6E3A2E** (shaded samples #4E3227, #4A2E27; washed #805C4C).
- Shirt: olive green, loose, under the coat. V-neck with criss-cross cord lacing, 3 crosses, ~12 cm long. Albedo [EST] **#8C8A55** (shaded #736F45; washed #A29864).
- Trousers: dark brown-charcoal, slightly baggy, ending just above the ankle. [EST] **#4A4034** (sample #473F34).
- Shoes: brown ankle boots with soft folded top. [EST] **#6B4A35** (shaded #543925).
- Hair: dark brown, short, spiky; bangs to the eyebrows; sides cover the tops of the ears; spiky tuft at the crown. [EST] base **#3B2F28**, highlight **#6B5546** (cool-lit sample #424445).
- Eyes: teal-green iris [EST] **#3F8F86**.
- Skin: lit **#E8BC95**, shadow [EST] **#B98A68**.

### 4.3 Child Mikasa (age 10)
- [WIKI] "pale skin, gray eyes, shaggy black hair that was long" (cut chin-length later). "Dark red scarf" given by Eren.
- Height: [WIKI] adult 170 cm (850). [EST] age 10: 1.35 m.
- Hair: straight black with blue-grey sheen; below the shoulders to mid-chest/upper back ([EST] ~40–45 cm); side-swept bangs split over the right eye. Base **#1C2230**, highlight **#506E85**.
- Scarf: dark crimson, smooth (no knit drawn), wrapped once loosely and high around the neck up to the chin, one end hanging down the front to the waist. [EST] albedo **#7E1E24**, shadow **#3A1216** (raw #3B2322 tree shade, #6D484C flashback haze).
- Outer layer: long dusty-pink / salmon-beige cardigan/coat, open front, long full sleeves, hem mid-thigh. [EST] albedo **#C99A8C**, shadow **#8E6A66** (raw #908487 tree teal cast; #E2C5B8 flashback haze).
- Under layer: off-white dress/tunic, gathered (smocked) neckline, hem just above the knee. [EST] **#E8E4E2**, cool shadow **#B5B3BB**.
- Legs bare.
- Shoes: not visible in any wiki frame. [EST] simple dark-brown flats or ankle boots **#5A3E2C**.
- Eyes: grey [EST] **#5E5F66**. Skin: pale [EST] **#F2D6C2**.

### 4.4 Firewood back-frames (seen in the S1E1 Hannes frame; dimensions EST)
- **Eren's frame** (shoiko ladder type):
  - 2 vertical poles, square section ~4 × 4 cm, ~1.1 m long; tops ~30 cm above his head.
  - 1 crossbar ~4 × 3 cm, ~70 cm wide, at shoulder-blade height, sticking out ~15 cm past each shoulder.
  - Dark rope lashed at each crossing; rope shoulder straps.
  - At the bottom, a horizontal bundle of thin peeled sticks (each 2–4 cm across, 80–100 cm long; bundle ~25–30 cm thick), tied with 2 rope bands, at lower-back/buttock level, sticking out on both sides of his body.
  - Wood: pale greenish-tan, lit [EST] **#8A8060** (shaded sample #544E32). Rope [EST] **#4A3F33**.
- **Mikasa's frame:** same 2-pole frame (2 pole tops above her left shoulder), bigger load: vertical stack of short round logs, end grain facing sideways.
  - Stack ~35 cm wide × 60 cm tall, waist to about the shoulders.
  - Logs 8–12 cm across, 30–40 cm long. Bark [EST] **#3A3022**; end faces [EST] **#8A7F55** with ring texture.
  - No straps visible on Mikasa in the tree close-up, but she carries it in the next scene.
- [MEMORY, Shiganshina spec] Mikasa carries firewood on an A-frame back-carrier.

### 4.5 The tree and the hill (character-scale detail)
- The wiki has NO wide shot of the S1E1 tree. The only S1E1 frame is the close-up from Eren's POV. The wide view is from the finale (same tree, ~4 years later). Massing is EST.
- [SEEN, S1E1 close-up] Dense broadleaf canopy, strongly backlit, god-rays and sparkles. Leaves simple, ovate, pointed, ~5–8 cm long. Backlit **#7ABE7F**, shadow **#23351D**, overall teal ambient **#3F9D79**. A thick dark limb (silhouette ~**#0A0B0A**) runs diagonally lower-left to upper-right behind Mikasa.
- [SEEN, finale] One large tree at the edge of a grassy hilltop; slope drops toward Shiganshina with red-orange tile roofs (in S1 the 50 m wall also surrounds the town). Trunk thick, mossy with ivy, grey-olive bark **#586838, #384838**, deep shadow **#283828**; base flares into roots. Grass sunlit **#88C848**, shade **#386828**. Bare earth / worn path [EST] **#CDBB8E**. Bushes and scrub on the downslope.
- [EST] Build: trunk 1.0–1.3 m at chest height flaring to ~2 m at the roots (Shiganshina spec: 2–3 m; see conflict table). First big limbs at 2.5–3.5 m. Canopy dome 14–18 m tall, 16–20 m across, slightly lopsided toward the town. Hill rises ~15–30 m above the plain (Shiganshina spec 30–60 m). Town 0.5–1.5 km away.
- [EST] Lighting: late-morning sun behind the canopy. In S1 the tree may read slightly smaller and less mossy than the finale (keep the shape, reduce ivy and moss).
- [WIKI] Eren's grave is later made at its foot.

### 4.6 Survey Corps (Scout Regiment) uniform (distant crowd figures)
- [WIKI] Short light-brown jacket with the regiment badge on both shoulders, front left pocket and centre back; white shirt; brown sash around the waist covering the hips; white pants; brown knee-high leather boots; green cape with the regiment symbol. Insignia: "Wings of Freedom".
- Cloak [SEEN]: dark green, hooded (hood down on shoulders), fastened at the throat, to about knee level. Daylight **#4A6254 / #485848**, shadow **#283828**.
- Back emblem: [EST] ~28 cm tall, centred between the shoulder blades. Left wing deep navy **#1A2C78** (darkest #112160), right wing white **#F4F4F7**, on a light-grey shield **#B0AEA8** split into 4 panes by black lines. At a distance: a white and dark blot on the green.
- Jacket: cropped at the lower ribs. Base **#9B6947**, lit #A87858–#C89878, shadow #6E4A33.
- Shirt: off-white/cream **#E6E2D8** (trainee model sheet #D3C69F).
- Trousers: **#CBC9C7**, shadow #B3AEAB.
- Hip wrap: dark brown, belt to mid-thigh like a short apron, **#2E1C16**.
- Boots: knee-high **#3A2218**.
- Harness: brown leather [EST] **#5A3A28**, 2.5–3 cm wide: one horizontal chest strap under the pecs; two vertical straps shoulders to belt; two straps around each thigh; diagonal straps down to the boots.
- Mounts [SEEN, S1E9]: mounted columns, chestnut/bay horses **#6C5A48**, some grey/white, dark saddles; covered wagons (canvas **#E6DFBB**, wood **#B4976E**).
- [SEEN, S1E1 return parade] Same cloaks, bandaged and wounded soldiers, one in an arm sling.

### 4.7 Garrison uniform (Hannes and the gate guards, S1E1)
- Same cropped tan jacket (**#A87858** lit, **#9B6947** base).
- Emblem: 2 dark-red roses (mid **#7A1F22**, shadow #451311, highlight #C58482) with a silver stem and thorns on a grey-white shield; on the left chest pocket, both shoulders, centre back.
- Inner shirt grey-white to cream **#C8B898 to #E0E0DA**.
- White trousers, dark-brown hip wrap, harness, knee boots as Survey Corps. **No cloak.**
- S1E1 guards off duty: jacket open, a belt pouch or holster, NO ODM hip units in the gate scene.
- Hannes: tall blond man [EST] 1.80 m.

### 4.8 ODM gear silhouette
- [WIKI] Body harness covering most of the body below the neck; winch housing on the lower back with two wire spools; two gas cylinders, one on each sheath; blade boxes "at the sides of their thighs"; two hand grips each "approximately 18 cm in height" that double as sword hilts; bladed anti-Titan gear in S1.
- [EST] Each hip unit: box ~60 × 14 × 9 cm, horizontal, angled ~10° down toward the rear, with a cylinder ~7 cm Ø × 55 cm long along its top. Back housing ~20 × 15 × 10 cm. Blades ~90–100 cm long, stored in the boxes.
- [EST] Colour: brushed steel **#9A9A94**, highlights **#D0D0C8**, dark fittings **#3A3A38**.
- Silhouette at distance: a 1.70–1.80 m figure with a horizontal bar sticking out ~15 cm each side at hip level. On Survey Corps figures the units stick out below and beside the cloak hem.

---

## 5. Paradis map and other places

Coordinates in **km**, origin at Capital Mitras, +X east, +Y north.

### 5.1 Walls and districts (global layout)
- [WIKI, Ep1 panel] Radii **Sina 250 km, Rose 380 km, Maria 480 km**; the panel says the areas between walls are roughly equal. Wiki: Maria perimeter ≈ 3,016 km; area inside Maria 723,822 km²; inside Rose 453,646 km².
- [WIKI] Walls ~50 m tall, ~10 m thick; 4 districts per wall. [SEEN diagram] Each district a semicircular bulge on the OUTER face at N/E/S/W; straight radial roads join matching districts in a "+" pattern. A road or river leaves Maria's east district and winds out into the "GIANT FIELD".
- District coordinates:
  - Sina: Orvud N (0, +250); **Stohess E (+250, 0)**; Ehrmich S (0, −250); Yarckel W (−250, 0).
  - Rose: Utopia N (0, +380); **Karanes/Calaneth E (+380, 0)**; **Trost S (0, −380)**; Krolva/Klorva W (−380, 0).
  - Maria: **Shiganshina S (0, −480)**; the other three at (0, +480), (+480, 0), (−480, 0), unnamed in S1.
  - Capital Mitras at the centre, with a royal palace.
- [EST] Derived distances: Shiganshina→Trost 100 km due N; Trost→Ehrmich 130 km due N; Karanes→Stohess 130 km due W; Karanes→Shiganshina ~612 km straight, heading SW; Trost→Karanes ~537 km chord or ~597 km along the wall.
- [WIKI] Titans come mostly from the south (frontline); the north is cold and safest.

### 5.2 Island and terrain
- [SEEN, S4 map] Tall N–S island (wiki: Madagascar flipped). Ragged coast with dark hatched shoreline and contour rings in the sea. Walls roughly centred E–W and about mid-island N–S.
- [SEEN] Walls drawn as red-orange concentric circles **~#A84A35** (shadow ~#793930), each with 4 outward half-circle district bumps at N/E/S/W; solid red dot at the centre.
- [SEEN, measured] Map ring ratio Sina : Rose : Maria ≈ **0.36 : 0.64 : 1.00** (stated km give 0.52 : 0.79 : 1.00). Use km for scale, map ratios for a map-look shot.
- [SEEN, measured] Wall Maria diameter ~45% of the island's E–W width at that latitude: west coast ~2.2 Maria-radii from centre, east coast ~2.1. The island continues past the top and bottom of the frame.
- Map colours: parchment land **#A88B66** (darker **#836C57**), relief hachures **#4A3A2C**, sea grey-green **#8E9A86**, rivers thin blue-green **#5E8C80**, faint brown grid.
- [SEEN] Rivers start in the central uplands and run outward roughly along N/E/S/W axes and through the districts. Several northern rivers run west to the west coast (wiki: 3 on the manga map). Hill/mountain hachures fill the outer belt, especially the west.
- [WIKI/Ep2 panel] Ground rises toward the centre; territory rich in water, minerals and natural gas. [EST] Very gentle cone, ~+300–500 m from Maria to Mitras over 480 km (flat at ground level).
- [SEEN, aerial establishing shot] Inner ring and outer wall each with a small southern district; one river N→S straight through both (meandering in the north, nearly straight in the south); small lakes/ponds beside it. Fields khaki **#9E8243** and olive **#8B804C**; forest patches **#544B30 / #3E4A2A**; roads and field edges pale cream **#E0D8B0**; cumulus below camera cream **#F2EBC8** with dark ground shadows.
- [SEEN, S1 Ep3, from Trost's wall looking south into Maria land] Flat-to-rolling grass plains **#9DB86F / #AABC96**; long belts and clumps of dark conifers **#2F4A35** (sample #3C423E); forested ridge; blue hazy mountains **#7C9CC8** (sample #6D90C0).

### 5.3 River from Shiganshina to Trost
- [WIKI] Sail-less boats pulled by pulleys and rails carry people between Shiganshina and Trost (Ep2 evacuation).
- [EST] Runs ~100 km roughly due N between the walls with gentle meanders. Flow runs south (downhill from the centre), so boats to Trost are hauled upstream.
- [EST] Canal width ~20–30 m; vertical stone quay walls ~4–6 m above the water. Water teal **#4F9497 to #5D8F98**.

### 5.4 Trost District (south of Wall Rose)
- [SEEN] D/U-shaped bulge pushed south out of the straight Wall Rose line. Inner (north) gate in the Wall Rose line: tall dark recessed gate slot, NW of centre. Outer (south) gate in the curved wall.
- [WIKI] Colossal kicked in the outer gate: **8 m hole** (manga). Civilians escaped through the north gate, jammed by Dimo Reeves' cart. Harpoon nets later bunched Titans near the north gate.
- [WIKI] Supply depot/HQ inside the district between the front and the north; trainees fought their way there. [EST] Mid-district, ~300–500 m in from the north wall: 3–4 storey stone block, big ground-floor supply hall, rooftop flat.
- Boulder: see Section 3.6.
- Canal [SEEN]: straight stone-banked canal N–S along the **east** side, just inside the curved district wall; passes through Wall Rose at the back (north) and leaves through the district's outer wall on the SE side, then continues south into Maria land with a bridge just outside. ~4 bridges (3 inside, 1 outside). Quay/walkway on each bank.
- Town [SEEN]: densely packed 3–5 storey half-timbered and stone houses; roofs orange-terracotta **#B0623E** (lit) / **#6B4532** (shade); walls cream **#C4B89E**. Streets in concentric arcs following the curved wall, plus radials. Landmark: tall cream/white civic or church building with a central square tower and spire, NW of centre near the inner gate.
- Size [EST]: ~1.2–1.5 km wide along Wall Rose, ~0.8–1.0 km deep (~10 m per house).
- Outside [SEEN]: rectangular green farm plots, small red-roofed hamlets just outside the east wall, scattered dark-green tree clumps.
- Wall top [SEEN, Ep3/ep4]: brick walkway (#6B4A3A), two iron rails, cannons on round wooden turntable carriages (barrels #69676A), small brick/stone guardhouses with red tile roofs (#8A5A50), wooden crates of shot; half-timbered house on a pier plinth (Section 2.4). [WIKI] Scouts ride a lift to the top.
- Eren's Titan fights in Trost and carries the boulder here (ep13).

### 5.5 Karanes (east of Wall Rose)
- [WIKI] The 57th expedition left from here: the shortest route to Shiganshina once Trost's outer gate was sealed.
- [SEEN, aerial] Same D-shaped district as Trost; town fills the bulge as a disc with an empty green/shadowed strip along the inside of the right wall. River with a bridge runs past outside through farmland. Outer gatehouse with dark (slate-blue #5F7C8A) roofs. Inner-face view: broad panels, slim pilasters rising above the top, cannon silhouettes ~2 per module, raised central section over the gate.

### 5.6 Stohess District (east of Wall Sina)
- [WIKI] Unused underground-city tunnels below. The Female Titan damaged Wall Sina here. Fight in ep24–25 ("Mercy", "Wall").
- [SEEN] Richer, more formal architecture than Trost:
  - 4–6 storey stone and stucco blocks, facades cream **#D8CFA8** (sample #ACA981).
  - Mansard roofs with rows of dormers; red-brown tile **#9A4E36** (dark **#533B2F**) and dark mauve **#4E3A36** roofs.
  - Slim corner turrets with red cone roofs, stepped gables, many chimneys.
  - Big dark slate ribbed dome **#2B2924** with a square lantern and red cone cap; other smaller domes.
- [SEEN] Wall Sina fills the whole horizon behind the town, ~3× taller than the buildings; smoother face, olive-grey #8A8A68 in warm light, thin vertical pilasters.
- [SEEN, later-season aerial, not saved] Large domed cathedral: red-brown dome on a cream drum, flanked by two spired bell towers.
- [SEEN, fight backdrop] Cream/ochre multi-storey building with mauve-brown mansard roof, dormers, narrow sash windows; a round stone tower with arched windows; a row of tall columnar poplars reaching about the Female Titan's chest/shoulder; smashed cobblestone square full of rubble, smoke plumes; Wall Sina hazy behind.
- Damage: patchwork cloth over the exposed Wall Titan face (Section 2.9). Annie's crystal moved underground (Section 3.7).

### 5.7 Forest of Giant Trees
- [WIKI/Ep18 panels] Groups of giant trees inside and outside the walls, only in certain patches, **over 80 m tall** ("generally around 80 m"), enormous trunks, big branches. Titans cannot climb them; ideal for ODM gear.
- [WIKI] Several such forests between Maria and Rose; tourist spots before 845. The Ep18 forest is "somewhere between Wall Maria and Wall Rose"; the Scouts' centre column rode in on a path/road through it. Forest fight ep21 ("Crushing Blow").
- [EST] Location: on the Karanes→Shiganshina route, SE part of Maria land, ~50–150 km SW of Karanes.
- Look [SEEN, ep19]: straight columnar trunks, bark warm grey-brown **#8B7A5A** to dark **#37311B** in shade; deep vertical bark grooves; fairly open forest floor, dusty brown earth **#5A4A2A** with ferns and shrubs; strong god-ray shafts through a dark green canopy **#2F5A40**. Ep18 panel silhouette: conical cedar/sequoia crown. Ep21 frame: olive haze **#403e1f to #aea06b**, dark-green undergrowth **#292e17**.
- [EST] Trunk Ø 6–10 m at the base; trunks ~20–40 m apart; first big branches 25–40 m up; crown from ~40 m to 80–90 m. The 14 m Female Titan stands ~1/6 of tree height.

### 5.8 104th Training Corps camp
- [WIKI] The 104th was the "Southern Division", trained 847–850.
- [SEEN, Ep3–4] Dirt parade ground backed by a sheer, vertically fissured rock cliff, blue-grey in shade **#6F7E95**. Training also in a nearby forest of very large trees (Ep4; bark grey-green **#8B8E7B** with lichen). Balance rig: two wooden posts with a crossbar and ropes.
- [EST, low confidence, chibi spin-off layout] Long 2-storey wooden barracks with red-brown gabled roof, smaller wooden huts, mess hall, behind a plank fence. Location: southern Wall Rose territory, within a day's ride of Trost.

### 5.9 Old Survey Corps HQ castle (Ep15)
- [WIKI] Old castle remodelled by the Scouts into a HQ; useless to them, became Eren's hideout. Dirty and abandoned. Eren sleeps in the basement; upper floor and courtyard (Hange's experiments nearby).
- [MEMORY, Ep15 dialogue] Useless because too far from the walls and the river. Place it in remote Wall Rose countryside.
- Look [SEEN]:
  - Pale limestone **#CECBA2**, heavily moss-stained **#8E9466**.
  - Front: two round flanking towers, each with a corbelled ring near the top and a crenellated parapet; between them a central gatehouse block with crenellated top.
  - Pointed-arch doorway with dark timber double doors **#2A241C** and iron straps, topped by a small triangular gable with a cross-shaped finial.
  - Round rose window (blue leaded glass **#294060**) centred above the door.
  - Narrow arched windows with blue diamond-lattice glazing.
  - Side wings of 3–4 storeys with crenellations and string-course mouldings. Weeds and grass at the base.
  - Interior and side walls: big grey-green stone blocks, wooden lattice shutters.
- [EST] Towers ~6–7 m across, ~20 m tall; gatehouse ~10 m wide × 18 m tall; door ~3 m × 5 m; overall ~40–60 m wide.

### 5.10 Gaps
- Map ring ratios do not match the stated km; island size worked out from the map is far larger than Madagascar.
- No S1 wiki screenshots of the camp exterior or the Trost supply depot interior.
- Boulder size and position, Trost size, camp and castle positions are all estimates.

---

## 6. Reference images

All paths under `/mnt/project-files/plans/3d_timelapse/ref/wiki/`.

### 6.1 Shiganshina (`shiganshina/`)
| File | Shows |
|---|---|
| `s1e1_town_overview_from_outer_wall_colossal_looming.jpg` | S1E1 sunset: Colossal head above the outer wall, dense gabled roofs, straight Wall Maria line with flat pilasters, bright inner-gate tower block at centre, road climbing a hill beyond the wall. |
| `s1e1_street_halftimber_houses_wall_behind.png` | S1E1 dusk: townspeople in a street of half-timbered houses, red tile roofs, dormers, bell tower with open belfry and pointed cap, grey panelled wall behind, Colossal steam rising. |
| `s1e1_alley_stone_arch_passage_steps.png` | S1E1 daylight street fabric: stone arched passage under a building, packed-earth alley with stone-slab steps, half-timber facades, orange pan-tile roofs, ivy and trees. |
| `s3_overview_from_outer_gate_canal_inner_gate.png` | S3 (850) from the outer wall top: whole roofscape, Wall Maria with tapered buttresses, white castle-like inner gatehouse, straight stone-banked canal (on the left here), mountains. |
| `s4_aerial_district_U_shape_canal_fields.png` | S4 (854) near top-down aerial: rounded U/D outcrop, ring-and-radial streets, main avenue, canal close to one side wall leaving through the shoulder of the curve, hamlets and forest outside. |
| `s4_854_canal_bridges_inner_gate_castle.png` | S4 (854) from the outer wall top: canal cross-section (stone banks, quays, promenades), 3 gantry frames, inner gate castle, post-850 crater pond (do not build for 845). |
| `s3_inner_gate_fortress_view_south.png` | S3 night: inner gate fortress (square keep, central tower with pyramid roof, pointed corner turrets, crenellations) looking south across town to the outer wall, Colossal explosion. |
| `s4_final_hill_tree_overlooking_town.png` | Final episode (857): the big tree on the grassy hill, ivy-covered trunk, broad canopy, Mikasa at its foot, town below among green fields. |

### 6.2 Walls (`walls/`)
| File | Shows |
|---|---|
| `trost_district_aerial_wall_rose_anime_s2.png` | Trost aerial: horseshoe bulge of flat panels and projecting piers, inner gate module (top-left), canal with bridges, pier tops (S2, same design as S1). |
| `karanes_district_aerial_outer_gate_anime_s1e22.png` | Karanes bulge: polygonal flat panels, thin projecting ribs with raised tops, low gatehouse with slate-blue roofs at the outer gate (S1, ep ~22). |
| `wall_top_walkway_rails_log_ramps_wall_sina_anime_s1e25.png` | Wall Sina top (Stohess, ep25): sandy walkway, single rail track ramping over pier blocks on stacked-log cribs, ore cart, projecting piers, patchwork cloth over the damaged face. |
| `wall_top_cannon_turntable_rails_crates_trost_anime_s1e4.png` | Trost wall top (ep4): grey smoothbore cannon on a wooden quarter-arc carriage and turntable over rails, paver texture, crates, half-timbered building on a stone plinth, Colossal head for scale. |
| `wall_cannon_diagram_front_side_action_cpai_anime_s1e5.png` | Ep5 info card: cannon FRONT/SIDE/ACTION blueprints (elevation sector, barrel to vertical), rail-mounted cannons along the wall top, lift/gatehouse lattice tower. |
| `wall_emblems_maria_rose_sina_cpai_anime_s1e1.png` | Ep1 info card: the three shield emblems, left-facing goddess over a cross-quartered field with text banner; clean line art for decals. |
| `inner_gatehouse_brick_with_rose_emblem_anime.png` | Brick gatehouse at the foot of Wall Rose (S1 era): central tower, pointed-arch gate, goddess plaque, two lower brick wings, grey wall with pilasters and band (night). |
| `wall_inner_face_pilasters_cannons_karanes_anime_s1e22.png` | Karanes inner face from a street (S1, ep ~22): broad panels between slim full-height pilasters rising above the top, ~2 cannons per module, raised section over the gate (sunset). |

### 6.3 Pure Titans, Colossal, Armored (`titans_pure/`)
| File | Shows |
|---|---|
| `size_chart_60m_15m_7m_5m_vs_50m_wall.png` | Anime size card (S1): 60 m Colossal with tendon pattern, 50 m wall at its upper chest, 15/7/5 m Titans, human, horse, cannon, buildings. |
| `colossal_face_closeup.png` | Colossal face: pale bone areas, red temple/cheek/chin muscle, lipless teeth, grey-green eyes, ear, neck tendon, red hand. |
| `colossal_845_head_over_wall_hand_gripping.png` | 845: Colossal head over the wall top, red hand gripping the parapet, steam, golden sky, forehead furrow, heavy brow. |
| `colossal_845_steam_plume_seen_from_street_S1E1.png` | S1E1 from a street: steam plume with white lightning at its left edge, small red head/hand breaking the wall top, half-timbered houses, crowd and kids. |
| `armored_fullbody_shiganshina_845_S1E2.png` | S1E2: Armored Titan full body among houses; plate layout, red side and thigh strips, wrist bands, pale crew cut, glowing eyes. |
| `armored_face_plates_closeup.png` | Armored close-up, neutral light: face seams, zigzag mouth crack, ribbed neck plates, olive-khaki plates with gold edges, red muscle, platinum hair. |
| `smiling_titan_dina_fullbody_crouch.png` | Smiling Titan crouching at sunset (S2): emaciated, ribs, long neck, centre-parted chin-length hair, grin with teeth and gums; Eren and Mikasa for scale. |
| `pure_titans_group_variety.png` | ~12 Pure Titans entering Shiganshina at dusk (WIT S3 flashback): range of sizes, skin tones, hair, smiles, smooth groins; dark wall and gate breach behind. |

### 6.4 Shifters (`titans_shifters/`)
| File | Shows |
|---|---|
| `attack_titan_eren_face_closeup_s1.png` | Attack Titan chest-up: shoulder-length black hair, pointed ear, lipless cheek-to-cheek teeth, sunken grey-green eyes, tan-brown skin. |
| `attack_titan_eren_fullbody_trost_steam.png` | Attack Titan near full body in Trost, low angle, white steam: glowing green eyes, 8-pack, long arms, hunched pose, smooth crotch, reddish-tan skin. |
| `attack_titan_boulder_carry_trost_ep13.png` | Ep13 burning state: boulder across neck and shoulders, arms up, torn skin, red muscle, embers, steam, evening sky. |
| `transformation_lightning_eren_forest_ep21.png` | Ep21 transformation: body forming mid-air in a dome of white-gold crescent streaks, yellow-white core, embers, dark green trees. |
| `forest_fight_eren_vs_female_titan_ep21.png` | Ep21: darkened Attack Titan with orange burn cracks, jaw open with sharp teeth, pale-green eyes, striking at the Female Titan between giant trunks. |
| `stohess_female_titan_fullbody_vs_eren_ep25.png` | Stohess: Female Titan front-on in boxing guard (clearest muscle map), Attack Titan's back, Stohess building, round tower, poplars, rubble square, Wall Sina. |
| `female_titan_hardened_forearm_block_stohess_ep25.jpg` | Hardened forearm block: iridescent blue-violet-white crystal skin; her face (blonde bob, dark cheek lines, full lips); red shoulder muscle. |
| `annie_crystal_cocoon_underground_ep25.png` | End of S1: Annie in the faceted egg-shaped crystal (~2.5 m), ~20 cables to stone walls, wooden cradle, Eren and Hange for scale. |

### 6.5 Characters (`characters/`)
| File | Shows |
|---|---|
| `s1e1_tree_scene_mikasa_wakes_eren_pov.png` | S1E1 from Eren's POV: Mikasa (10) leaning over, long black hair, dark-red scarf, dusty-pink cardigan, white smock-neck top, backlit canopy, god-rays, dark diagonal limb. |
| `s1e2_child_eren_845_portrait_clothes_same_as_e1.png` | 845 portrait of child Eren (E2, same outfit as E1): spiky dark-brown hair, teal-green eyes, maroon coat, olive laced shirt. Key string is post-E1. |
| `s1e1_firewood_back_frames_kids_and_garrison_hannes.png` | S1E1 Eren argues with Hannes: clearest view of both firewood frames; two Garrison soldiers with open tan jackets, rose emblems, harness, grey shirts. |
| `s2flashback_child_eren_mikasa_armin_fullbody_garrison_845.png` | Ep37 flashback (845, pink haze): full-body child Eren, Mikasa, Armin; Hannes in full Garrison uniform; rose emblem on a jacket back. |
| `s1_survey_corps_cloaks_horseback_from_behind.png` | S1E9 Survey Corps leaving Trost from behind: green hooded cloaks with Wings of Freedom, ODM hip units, bay and grey horses, covered wagons. Best crowd silhouette. |
| `soldier_uniform_base_fullbody_anime_model_sheet.png` | Official model of Eren in uniform (trainee badge): jacket, cream shirt, hip wrap, white trousers, full ODM harness layout, knee boots. Base mesh for all soldiers. |
| `eren_tree_on_hill_overlooking_shiganshina_final_season.png` | Final-season wide shot of the tree: mossy ivy trunk, green hilltop, Mikasa beneath, Shiganshina roofs below. Only wiki wide shot of tree and hill. |
| `emblems_survey_corps_wings_and_garrison_roses_wiki.png` | Composite of wiki emblem renders: Wings of Freedom and Garrison twin roses, for texture decals. |

### 6.6 Map and other places (`map/`)
| File | Shows |
|---|---|
| `paradis_island_map_anime_S4.jpg` | Final-season parchment map: concentric red rings with N/E/S/W district bumps, red capital dot, coast, rivers, hachures, grid. |
| `walls_distance_diagram_ep1_infopanel.jpg` | Ep1 info panel: Maria→Rose ~100 km, Rose→Sina ~130 km, Sina→centre ~250 km; semicircular districts, cross roads, road to the "Giant Field". |
| `walls_aerial_river_terrain_anime.jpg` | Aerial establishing shot: inner ring and outer wall with southern districts, N–S river, ponds, patchwork fields, forests, clouds below camera. |
| `trost_district_aerial_anime_S1.jpg` | S1 Trost aerial: D-shaped bulge, buttressed walls, terracotta roofs, white tower landmark, east-side canal with bridges, farmland. |
| `trost_walltop_cannons_view_south_ep3.jpg` | Ep3 from Trost's wall looking south: brick walkway, rails and cannon carriages, red-roof guardhouse, plains, conifers, blue mountains, Colossal Titan. |
| `stohess_district_rooftops_wall_sina_S1.jpg` | S1 Stohess rooftops: cream stucco blocks, mansard and red roofs, spires, dark slate dome, Wall Sina with thin pilasters across the horizon. |
| `survey_corps_old_hq_castle_entrance_ep15.jpg` | Ep15 old HQ castle: two round crenellated towers, central gatehouse, pointed-arch door, rose window, mossy pale limestone. |
| `forest_giant_trees_trunks_scale_ep19.jpg` | Ep19 Forest of Giant Trees: 14 m Female Titan trapped between columnar trunks, open dirt floor, undergrowth, light shafts. |

### 6.7 Viewed but not saved (fetch if needed; add `?format=original` or `&format=original` for PNG/JPG instead of WebP)
Base: `https://static.wikia.nocookie.net/shingekinokyojin/images/`
- `7/77/Walls.png`: S1 aerial with the south U-outcrop and river.
- `8/8a/ACPAI1B.png`: wall distances and district half-disc diagram.
- `3/35/An_armored_Titan_destroys_the_gate.png`: S1E2 inner gate breach.
- `f/f8/Carla_Jaeger%27s_death.jpg`: S1 roofscape; Carla's death profile.
- `2/25/Carla_tells_Mikasa_to_be_there_for_Eren.png`: steps near the Jaeger house.
- `9/99/Colossal_Titan.png`: Colossal torso tendon grid.
- `6/62/Colossal_Titan_reappears.png`: S1 Trost Colossal face beside wall cannons.
- `b/b4/The_Colossal_Titan_outside_Shiganshina.png`: S1E1 face between church spires.
- `c/c3/Abnormal_%28Anime%29_character_image.png`: S1 Abnormal running.
- `4/44/Female_Titan_%28Anime%29_character_image_%28Annie_Leonhart%29.png`: Female Titan face, bone-white fists.
- `7/72/Eren_in_Titan_form_ready_to_fight.jpg`: Attack Titan boxing profile in Trost (best ear view).
- `5/58/Annie_Leonhart_transforms.png`: Annie's titan face during transformation (cheek lines).
- `c/c6/Eren_protects_Armin_and_Mikasa.png`: ep10 partial-transformation skeleton.
- `e/e5/Eren_and_the_Female_Titan_rematch.png`: Stohess rematch (3.1 MB; add /scale-to-width-down/1280).
- `9/90/Order_of_the_Walls_%28Anime%29.png`: Wall Cult church interior.
- `9/9f/Stohess_aerial_view.png`: later-season Stohess cathedral aerial.
- `9/9a/Karanese-ANIME.png`: Karanes aerial.
- `d/d9/Eren_confronts_a_military_guard.png`: Garrison front view, harness and holster (S1E2).
- `2/29/The_Scouting_Legion_returns.png`: S1E1 Survey Corps return close-up.
- `e/e4/Eren_and_Mikasa_return_home.png`: S3 Scouts from behind (cloak length, hip units).
- `7/73/Omni-directional_mobility_gear.png`: ODM gear in its case.

### 6.8 Primary wiki pages
Shiganshina_District, Shiganshina_District_(Anime), Walls_(Anime), Wall-mounted_artillery_(Anime), Current_Publicly_Available_Information/Anime, Trost_District_(Anime), Calaneth_District_(Anime), Stohess_District_(Anime), Paradis_Island_(Anime), Forest_of_Giant_Trees_(Anime), Training_Corps, Fall_of_Wall_Maria_(Anime), Battle_of_Shiganshina_District_(Anime), Titan_(Anime), Colossal_Titan_(Anime), Armored_Titan_(Anime), Attack_Titan_(Anime), Female_Titan_(Anime), Dina_Fritz_(Anime), Abnormal_(Anime), Hannes_(Anime), Eren_Jaeger_(Anime), Mikasa_Ackermann_(Anime), Annie_Leonhart_(Anime), Scout_Regiment_(Anime), Garrison_Regiment_(Anime), Omni-directional_mobility_gear_(Anime), Order_of_the_Walls_(Anime), Wall_Titan_(Anime); episode pages for ep1, ep2, ep13, ep15, ep21, ep24, ep25 (all at https://attackontitan.fandom.com/wiki/).