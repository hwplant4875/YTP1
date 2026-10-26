# g2_armored_boats: Armored Titan ram on the Shiganshina inner gate + refugee ferries north

Author: layout/camera/animation design pass (Opus). Sources: ep02 (all of this beat) and ep01 (wall and wall-top gun design only).
Ep01 has no Armored or boat material. Frame paths are abbreviated: `F2/000014428` means
`/tmp/claude-0/aot/anime/frames/ep02/000014428.jpg`, and `F1/...` means the same path under ep01.
"INF" marks an inference, meaning the frames do not show it directly.

Our coordinate frame is the one already in the code (aot/scene.py, states845.py). Units are metres. Wall Maria runs
along the x axis at y = 0, with its faces at y = +-5 (WALL_T 10). North is +y, toward Wall Rose and Trost, and east is +x.
Shiganshina lies at y < 0. The inner gate is at (0, 0), the outer gate at (0, -720) and the canal centre line at x = +228,
which is east. The current Carla/Yeager seam is SEAM_IN in render_fall2.py: cam (-130, -686, 114) aimed at (-165, -594, 0), 28 mm.

The geography in the anime matches our layout, and both orientations check out. Looking SOUTH at the inner wall from the
north side (F2/000007708 then the pan in F2/000007804), the canal water-gate arches are on the LEFT, which is EAST, and the windmill is on the RIGHT, which is WEST.
Our canal at x = +228 is therefore correct. The beat starts at the Carla seam on the WEST side of the outer gate (aim -165, -594),
which agrees with the owner rule (Yeager house LEFT of the outer gate as seen from the Colossal, i.e. at x < 0).
Ep01 does show the inner gate's NORTH face once (05:08.6 F1/000007400, 05:12.6 F1/000007496, Eren and Mikasa coming home
with firewood) and the wall top / water strip outside the wall (05:03.6 F1/000007280); those frames are used below.

---------------------------------------------------------------------------------------------------------------------

## 1. Lore summary in order, with evidence

1. **Shiganshina is burning while titans walk the streets.** 5-8 smoke columns rise from the town. Early on they are THIN, wavy and
   pale grey (02:31.9 F2/000003643, about 7 columns, several roofs caved in); later they are thick dark charcoal-brown (06:49.4
   F2/000009815, 07:56.1 F2/000011416). Pure titans walk slowly in loose columns of mixed size (3-10 m).
   ep02 05:12.7 F2/000007498, 07:59.3 F2/000011491 (an aerial with at least 5 titans spread along a diagonal pale-dirt street between
   black smoke columns).
   Street state near the avenue: collapsed houses with broken brick piers and stone rubble piles, drifting orange embers, small
   street fires (09:00.5 F2/000012958, 09:20.3 F2/000013433 lower left, 02:57.6 F2/000004257), and the big wall fragments thrown by
   the Colossal's kick lying in the streets (02:23.0 F2/000003429; that debris belongs to the kick group, keep it present here).
2. **The evacuation quay is on the NORTH side of the inner wall.** Refugees come out through the inner gate onto a road among
   a hamlet of cottages, fields and a windmill (ep02 05:21.5 F2/000007708). They pack a paved quay apron by the
   twin arched WATER GATES where the canal leaves the wall (05:25.5 F2/000007804); between the gate road and that apron there are
   lawns, footpaths and cottages, NOT one continuous plaza (7804). Two ferries load at the stone quay. A HIGH-LEVEL bridge on three
   square stone pylons with orange pyramid caps crosses the canal just north of the arches; its deck/chains run at pylon-top height,
   so the ferries pass underneath (05:29.5 F2/000007900; the pylon at the left edge of 7804 is one of these, not a separate tower;
   the thin lines crossing the canal in 8066 and the horizontal lines in front of the wall in 11172 are most likely its chains, INF).
   Seen top-down, the ferries sit on teal water with the quay wall-to-wall with people; a narrower LOWER berth at the waterline,
   also packed, runs below the upper paving with stair flights between them (05:36.4 F2/000008066). The canal runs dead straight north, with a paved quay packed with
   people on both banks and fields and cottages beyond (05:40.4 F2/000008162).
   Narration: "We're evacuating Shiganshina!" (05:25.5).
3. **The canal is sunken.** The quay retaining wall is tall cut stone, and a timber gangway juts out to the boat (06:06.6 F2/000008790).
   The FAR bank is a battered (sloping) stone revetment topped by a railing, not a vertical wall (07:09.1 F2/000010288, F2/000007900).
   A crowd shot shows a wide shallow stepped paved street running down to the quay, with half-timber houses on one side (07:05.1
   F2/000010192, 07:09.1 F2/000010288). A short plank gangway crosses to the ferry deck (07:13.1 F2/000010384).
4. **Garrison defence at the SOUTH face of the inner gate.** The gatehouse is red-orange brick with the goddess-profile crest
   (05:56.4 F2/000008546). Field guns on big spoked wheels stand at its foot (06:39.4 F2/000009575). From behind a gun you see a
   long straight dirt avenue running to the far (outer) wall, with a ground dust cloud at its end containing a dark-haired PURE titan
   (06:49.4 F2/000009815; the Armored is NOT in this shot). Refugees still run in ("They're right behind us already!", 06:53.2
   F2/000009908). Two pure titans stand in the avenue (07:56.1 F2/000011416). "These aren't accurate enough to be reliable!"
5. **The gate closing is ordered but never completed** ("The gate's closing" 08:10.7, "Don't close it yet!" 08:20.2, "Seal the gate,
   pronto!" 08:42.6; at 09:56.2 F2/000014295 the passage is still open). The north face has the same brick crest block between pale
   stone jambs, with two chains hanging from above (07:43.1 F2/000011103). The crest block hangs on those chains in a slot between two
   regular wall pilasters with visible gaps at its sides (08:07.5 F2/000011688): it reads as the raised DROP GATE leaf itself (INF,
   strong).
6. **The Armored Titan comes up the avenue.** His legs first appear among rubble and broken houses (09:00.5 F2/000012958). He walks
   hunched, head tucked between the shoulder plates (09:14.7 F2/000013299), and each footfall cracks and lifts the paving slabs with
   a low dust puff (09:20.3 F2/000013433). He then stops and crouches low, shoulders forward, eyes glowing, like a sprinter getting
   set ("What... is that?", 09:31.1 F2/000013692), before charging (owner override: see section 9). A field gun fires point-blank and whites out the frame
   (09:34.2-09:35.1). The shell glances off his head/face as a gold streak (09:37.4 F2/000013843), and he keeps coming.
7. **The charge.** His legs stride over the cannon line while the crews scatter, with a red pure titan behind him (09:49.4
   F2/000014132; the crews run TOWARD the camera, i.e. ahead of him toward the gate). "A Titan's coming!" Soldiers run across the
   apron in front of the open passage, which glows white-gold ("Quickly, shut the gate!", 09:56.2 F2/000014295; most run away from
   the passage and sideways, direction of the rest is ambiguous). He charges shoulder-first, smashing house roofs, with tiles and
   timbers flying (09:58.7 F2/000014354). A long avenue view shows the brick gatehouse at the end, a line of 5-6 field guns spread
   across the apron in front of it, big trees at the left by the gate, and roof tiles/timbers streaking past (10:01.8 F2/000014428).
8. **Impact and burst.** There is a dust and spark flash (10:04.7 F2/000014499), and house-sized stone blocks fly through the sky
   with a Garrison soldier flung (10:07.7 F2/000014571). The breach is a TALL arch-shaped bright hole (10:22.2 F2/000014917).
   The brick side wings of the gatehouse survive, and cracks radiate across the wall face (10:33.1 F2/000015180).
9. **The top-down aerial of the aftermath.** A lumpy cauliflower dust ball about 35-45 m across (about four cottage lengths) sits on
   the lawn north of the wall, with a gold armour shape inside it, cottages to one side, 8-10 loose boulders (1-4 m) scattered on the
   lawn around it, and a pale-blue water strip running along the wall foot between the lawn and the wall (10:25.1 F2/000014988).
   This is THE sky-observer frame of the beat.
10. **The ferry leaves.** Its deck is packed and it has a truss frame and a long roof (10:40.1 F2/000015348). From beside the
    windmill, the breach is a bright narrow slit in the wall while the Armored emerges into the haze and then STANDS upright in front
    of the hole (10:45.6 F2/000015478, 10:49.6 F2/000015574). Steam comes from his mouth (10:35.7 F2/000015241).
11. **The aftermath and the route north.** Shiganshina from inside a few hours later shows the twin barred water arches and a
    towered bridge (11:02.7 F2/000015890). The council says "the people there have evacuated by ferry" (11:29.0 F2/000016519) and
    "around 500 people onboard" (11:30.4 F2/000016554; the line does not say whether that is per ferry or in total).
    Inside the district the twin arches feed two parallel canals (15890, 19762). At dusk a lone ferry is on a wide river with a two-pier truss bridge
    (13:36.2 F2/000019570). The plan view shows the bulge, two parallel canals, a central bell tower and 5 smoke columns
    (13:44.2 F2/000019762).

---------------------------------------------------------------------------------------------------------------------

## 2. Layout and geography (top-down, metres, our frame)

```
                         N (+y)  toward Wall Rose / Trost
   [windmill(-95,165)]        gate road x=0 (12 m)        canal x=228 (30 m wide), quays both sides, ferries
   [cottages W of road]     |   lawns + paths [cottages]   quay apron x=+150..+213, y=+8..+110 (paved)
   ~~~~~~~~ dust ball (0,+55) r=20 after the ram ~~~~~~~~      high bridge on 3 pylons y=+40 across the canal
   ~~~~ water strip along the wall foot y=+15..+21, x=-250..+145, timber road bridge at x=0 ~~~~
 ==== WALL MARIA y=0 ==== [inner gate (0,0)] ===================== [twin water arches x=220 & 236] =====
   wall-top guns x=+-25,+-60,+-95 (south rim)                     towered bridge y=-30 (inside, F2/000015890)
   brick gatehouse front y=-13 south / +13 north (low front projects 8 m, INF); gate apron y=-60..-13, |x|<54
   field battery: 6 guns across the apron, x=+-12,+-26,+-40, y=-34, muzzles south (gaps between guns = refugee lanes)
   avenue x=0, 26 m wide, straight to the outer gate (0,-720)
                         S (-y)  outer gate / Colossal breach
   [square brackets] = buildings north of the wall, OMITTED by default under the owner rule (see section 9).
```

- **Avenue (south).** It runs straight N-S at x = 0 from (0, -720) to (0, -60): dirt, 26 m wide, with 3 m grass verges and wheel
  ruts and weedy grass patches down the middle (F2/000014428, F2/000009815). It is lined tight by 3-4 storey half-timber/stone houses
  with steep roofs; most have eaves to the street with dormers, but several show pointed gables or small turrets toward the avenue
  and one has a stepped (crow-step) gable (14428). A few big round deciduous trees stand by the gate at the avenue's west side (14428).
- **Gate apron (south).** The existing square is y -60..-13, |x| < 54: dirt with pebbles under the guns (07:52.4 F2/000011327) and
  pale flagstones with grass edges near the passage (F2/000014295).
  - The field battery is 5-6 guns spread evenly ACROSS the apron in one line (10:01.8 F2/000014428, crop of the gate end); use 6 at
    x = +-12, +-26, +-40, y = -34, muzzles south, so refugees run through the 8-10 m gaps. 1-2 roundshot lie on each carriage
    (F2/000011416); shot pyramids are INF (P2). F2/000009575 shows 3 guns side by side at the gatehouse foot.
- **Inner wall top (owner rule).** 6 wall guns stand at x = +-25, +-60, +-95, y = -2, z = 50. Each sits on a circular stone pad
  of 5 m diameter with a pair of timber sleeper rails, the same design as ep01 04:46 (F1/000006860 to F1/000007088). Muzzles point
  south and down into the avenue.
- **Gatehouse.** The SAME ensemble on both faces (south: F2/000008546, F2/000011688, F2/000014428; north: ep01 05:08.6
  F1/000007400, 05:12.6 F1/000007496, ep02 F2/000007708 shows the low stepped wings either side of the lit arch): a low brick front
  about 2 bays (32 m) wide and 9-10 m tall to a cream cornice, with the passage in the middle, and above the passage the brick crest
  leaf hanging in the regular pilaster bay. The low front projects about 8 m from the 5 m wall faces (INF), so its fronts are at y = -13 south and y = +13 north
  (the timeline in section 6 uses the south front at y = -13).
- **Water strip and road bridge (north).** A 5-6 m wide pale-blue water strip runs along the north wall foot at y = +15..+21,
  from x = -250 to the quay apron at x = +145 (F2/000014988; also the
  water channel along the wall outside the town in ep01 05:03.6 F1/000007280). The gate road crosses it on a short timber bridge with
  plank rails (the timber railing in front of the gate in F1/000007496; INF that it is the same bridge).
- **Water gate.** Twin round arches at x = 220 and x = 236, one per pilaster bay, separated by a 3 m pier: spans 11-13 m, crowns only
  about 8-9 m above the water (crown height is about 1/6 of the wall height in F2/000015890 and about half a bay in F2/000007804;
  the earlier 14 m was too tall). Iron grilles hang raised (F2/000015890). Our code currently cuts one 24 m gap at CX: replace it
  with the 2 arches. Inside the district each arch feeds one of two parallel canals (F2/000015890, F2/000019762).
- **Canal, north stretch y = +5..+450.** It is straight, 30 m wide (widen from 24; 8162 shows the canal at about 3 ferry beams) and
  sunken: the quay top is about 3.5-4 m above the water, roughly level with the ferry deck so the gangways are flat (F2/000010288,
  F2/000007983), with a cut-stone retaining wall (F2/000008790; INF height).
  - Paved quays about 20 m wide run on both banks (x = 193..213 and 243..263; 8162 shows each quay at about 0.7 of the canal width).
    Along the west quay, a 4-5 m LOWER berth runs at about 1.5 m above the water, joined to the upper paving by stair flights
    (F2/000008066). The east bank is a battered (sloping) stone revetment under the quay edge (F2/000010288, F2/000007900).
    Beyond the quays are a low parapet and a 1 m timber rail, then lawns (F2/000007900, F2/000008162).
  - Stair landings are 6 m wide: west quay at y = +60, +150, +260 and east quay at y = +100, +210 (F2/000008066 shows the stepped
    landings).
  - North of y = +450 the canal widens smoothly into the N-S river, 70-110 m wide, heading for Trost (F2/000019570).
- **Quay apron.** A paved apron of pale flags spans x = +150..+213, y = +8..+110, next to the arches and the west quay
  (F2/000007804, F2/000008066). Between it and the gate road (x = +20..+150) there are lawns crossed by pale footpaths, not paving
  (F2/000007804). A shallow stepped street of 4-5 broad steps descends to the west quay around y = +60 (F2/000010192).
- **Gate road (north).** It runs from the gate at x = 0 due north, 12 m wide, packed earth (F2/000007708).
- **High bridge over the canal.** It crosses at y = +40 on THREE square stone pylons (4 x 4 m, about 16-18 m tall from the water,
  with orange-tile pyramid caps): one on each quay edge at x = 228 +- 17 and one mid-channel at x = 228. A straight timber deck
  with chains/rails runs between the pylon tops at about 14 m above the water, so the ferries (cabin top about 6 m) pass underneath
  (F2/000007900 crop; F2/000007804 left edge). A similar towered bridge stands inside the district at y = -30 (F2/000015890).
- **Hamlet north of the gate (OMITTED by default, owner rule, see section 9).** If the owner allows it: 8-10 cottages within 250 m:
  - West of the road: (-60, 40), (-115, 70), (-45, 115), (-150, 125).
  - Between the road and the apron: (55, 135), (95, 190), (130, 60).
  - East of the canal: (300, 80), (325, 170).
  - (The "slim guard tower" at (205, 15) in the earlier draft is the west bridge pylon: removed.)
- **Windmill (OMITTED by default, owner rule).** If allowed: (-95, 165), west of the gate road (F2/000007708, F2/000015478).

**Sizes.** The wall is 50 m tall. Pilasters are 3.5 m wide, project 2 m and repeat every 16 m (wall height to bay ratio about 3:1
in F2/000007498 and F1/000006944). They rise 3-4 m above the parapet as stepped merlons. A string course of horizontal bands runs
at about 12 m (F2/000007498, F2/000011103).

---------------------------------------------------------------------------------------------------------------------

## 3. Set dressing and materials (hex colours are lit/shade for golden hour before toon)

- **Wall Maria.** Tan sandstone (#c9b38a lit, #8f7c5e shade, the north face in shade #66675a), with dark vertical grime streaks
  and pale pilaster edges. It is NOT grey or lilac (F2/000014428, F2/000007498). In neutral daylight the stone is a pale beige-grey
  (ep01 F1/000006944); the tan reading comes from the golden-hour key, so tint the albedo pale warm beige and let the light do the rest. Ivy patches climb the lowest 15 m near the gate (F2/000009575).
- **Inner gatehouse, both faces** (south: F2/000008546, F2/000009575, F2/000011688, F2/000014295, F2/000014428; north: F1/000007400,
  F1/000007496, F2/000011103, F2/000007708). Scale is taken from the regular 16 m pilaster bay (crop of F2/000014428):
  - **Low brick front**, about 32 m wide (2 bays) and 9-10 m tall, red-orange brick (#b4643f, mortar #d8c3a0) with a cream
    limestone cornice of two moulded bands (#e3d5b5) and cream corner strips. The two wings have small red-tile lean-to roofs above
    the cornice (F2/000011688 left). The left wing has a pointed-arch timber door (about 3 x 5 m) beside a barred window, the right
    wing a pointed arch (F2/000011688, F2/000014295). Ivy on the wall and wings beside it (F2/000009575, F1/000007496).
  - **Passage.** A pointed (gothic) arch with a thin green-painted inner trim (#4f7a55), only about 5 m wide x 7 m tall in the anime
    (figure scale in F2/000014295, bay scale in F2/000014428). A 15 m Armored cannot fit through it: that is why he breaks the
    WALL, not just the gate. Keep our 14 x 20 m opening only if changing GATE_W/GATE_H is costly (P2).
  - **The crest leaf (the drop gate).** Directly above the passage, filling the pilaster bay between two pale jambs: a brick block
    about 10 m wide x 12 m tall (bottom about 10 m, top about 22 m above the ground) with a recessed shield-shaped panel showing the
    Wall Maria goddess profile in cream stone on a dark blue/red field, and a row of protruding stone corbels (dentils) along its
    lower edge. Two iron chains run from its top up the wall. Dark gaps at its sides show it is a separate block hanging in a slot
    (F2/000011688, F2/000008546, F2/000011103). The north face shows the same leaf.
  - Above the leaf the bay continues up to the parapet between the two pilasters (the guide), with a small hood at the top
    (F1/000006944).
  - This leaf replaces the earlier "dark iron-and-timber drop plate inside the passage" (no frame shows one). It slides down in its
    slot to close the passage (see section 6). The earlier "brick tower 20 x 28 m projecting 8 m" is not supported: the whole brick
    composition is lower and flatter (overall about 22 m tall, under half the wall height in F2/000014428).
- **Breach shape after the ram** (F2/000014917, F2/000015478, F2/000015180):
  - A tall, NARROW arch-shaped hole (parabolic/pointed top), about 12-14 m wide x 24-26 m tall (height about 2x width: about 1.7x+
    in F2/000014917 with the bottom hidden by dust, about 2.5x for the bright slit in F2/000015478), centred on x = 0, with ragged
    edges chipped 0.5-1.5 m. Replace INNER_HOLE (12.5 half-width x 29 = 25 m wide), which is too wide and too rectangular.
  - The passage, the crest leaf and the brick between them are gone. Both brick side wings SURVIVE with jagged inner edges.
  - Dark crack decals radiate 15-30 m out from the hole across the wall face.
  - Warm light shows through the hole, which the code already does.
- **Field guns** (F2/000009575, F2/000011327, F2/000014132):
  - A dark grey-bronze barrel (#5c5648) about 3.2 m long with reinforcing rings of the same metal and a cascabel, on a timber box
    carriage with iron straps (F2/000011327, F2/000009575).
  - Two spoked wooden wheels of 2.0-2.4 m diameter, 12-14 spokes, iron tyre (F2/000011764: the wheel top is above a man's shoulder).
  - Garrison crews in brown jackets: 4 per gun.
- **Wall-top guns.** See section 2 (F1/000006944-7088 sequence; INF that they fire at the Armored, owner rule).
- **Canal.**
  - Water teal-green (#5f8f84, highlights #a9c9b8), with sparkle and a soft wake behind each ferry (F2/000008066).
  - Retaining walls cut stone (#a89a7e) with a darker, damp lower 1 m. Quays in pale paving (#cdbf9f).
- **Ferry, about 500 people each** (F2/000007900, F2/000007923, F2/000008066, F2/000010384, F2/000015348, F2/000011172, 11:30.4 dialogue):
  - Hull: 34 m x 10 m, oval plan with pointed ends, dark brown horizontal planking (#4a3526) and a paler rub strake.
    Freeboard 1.5 m.
  - Cabin: one storey, 20 x 5.5 x 3 m, in the middle, brown timber walls. A row of upright rectangular windows down each side
    (glazing #3e6b5a, pale timber frames) (F2/000007983, F2/000010384).
    A long barrel/barn roof in dark red-brown (#7a3a2a) with a pale ridge cap.
  - Two long parallel beams run along the whole boat above the roof, between the end trusses; the roof carries 2 rows of about 8
    round pale discs (F2/000008066 from above, F2/000007923 close-up).
  - At each end, a timber A-frame truss rises from the gunwale to a light railing slightly ABOVE the roof (F2/000007923, F2/000007983, F2/000015348).
  - A small lantern on a cabin corner (F2/000010384).
  - The deck around the cabin is packed with people standing shoulder to shoulder.
  - Build it once, 2-3k triangles, and instance it.
  - Propulsion is never shown (INF). There are no sails or oars, so give it a slow, steady glide.
- **Gangways.** Timber gangway piers 3 m wide jut 4-6 m from the quay edge with rope rails, plus short planks onto the ferry
  (F2/000008790, F2/000010384).
- **Hamlet cottages (only if the owner allows them, section 9).** 2 storeys, 8 x 10 m. Cream half-timber walls (#d9cdb0) with dark
  timbers and the SAME orange-brown tile as the town (#9a5a3a): they only look dark brown in the wall's shadow at dusk (F2/000007708,
  F2/000008162); in light they are orange (F2/000007900, F2/000010288).
- **Windmill (only if the owner allows it).** A round tapering tower 14 m tall (base 7 m, top 5 m) in rust/terracotta (#9a4f34) with
  faint horizontal bands, a pointed conical cap in orange-red (lit) rather than dark, and 4 lattice sails of 10 m radius
  (F2/000015478, F2/000015574).
- **Vegetation.**
  - Lawns #6f8a4a lit, #4d6438 shade.
  - Pale dirt footpaths 2 m wide, branching (#b9a27a).
  - Dark columnar cypresses 12-16 m tall along the quay outer edges every 25-40 m (F2/000008162, F2/000007900).
  - Round deciduous clumps around the cottages.
- **Avenue houses** (F2/000014428): steep orange-brown tile roofs (#a4532f) with dormers, cream plaster with dark timbers and
  stone ground floors.
- **Debris (ram).** Angular tan stone blocks, 1-6 m (#b59f78), plus brick fragments (#a85a3a) and timber beams (F2/000014571).
- **Street rubble (south).** Collapsed houses with broken brick piers and stone rubble piles (1-3 m) in side streets and at the
  avenue edges, small street fires and the Colossal-kick boulders (F2/000012958, F2/000013433, F2/000003429). Reuse the
  existing IMPACTS debris from states845.
- **Not in this beat.** No ground craters or pits at the inner gate. The only pit in ep02 is a human-scale ditch at 12:03.6
  (F2/000017348), which is not this location. The owner's cratered ground belongs to the Trost boulder beat (another group).

---------------------------------------------------------------------------------------------------------------------

## 4. Characters and titans

- **Armored Titan.** He is 15 m tall. Use the rigged Tripo model, rotated to face +y (it imports sideways).
  - Colours (F2/000013299, F2/000014354): plates golden cream (#e2c47a lit, #a8874a shade), red muscle in the gaps (#b8402e),
    off-white short hair (#e8e4dc). In the anime the eyes glow pale gold (F2/000013692, F2/000014499, F2/000014917). OWNER
    DECISION: the faceless rule may forbid this; default OFF (no eyes). If allowed, 2 tiny emissive dots (#fff2c0) only in the
    last 3 s; from 200+ m they are 1-2 px.
  - The neck is naturally short, so the head sits low between the shoulder plates (F2/000013299). That is the model's rest pose;
    do not add extra hunching.
  - **Gait (owner rule).** A normal upright run, facing forward.
    - Froude-correct sprint for a 15 m body: cadence 1.55 steps/s, step length 18-19 m, speed 29 m/s, so no foot skate.
    - Arms pump. Every footfall raises a dust puff 6-8 m wide plus a 4 m footprint scuff decal (F2/000013433).
  - **Last 0.4 s** (owner rule, 13:40 10/25): the torso twists 30-40 deg so the left shoulder leads, the head tucks, the legs keep
    driving and the whole root never rotates. The anime pose at the moment of impact is F2/000014354.
  - **After the burst.** He carries on about 25 m north through the hole, decelerating over 1.5 s. He straightens up, with white
    steam puffs from his mouth (F2/000015241), and STANDS upright in the dust in front of the hole (F2/000015478, F2/000015574).
    No frame shows him walking away; any later slow walk (about 4 m/s) and its direction are INF, so keep it to a few steps.
- **Follower pure titans.** 3 of them, 5 m, 7 m and 9 m, in the reddish/pink-beige skin of the existing pure titans
  (F2/000014132, F2/000011416).
  - They walk at 3-4 m/s up the avenue, 120-250 m behind him, and stop or stand by the end of the take.
  - Up to 3 more titans stand in side streets further south (F2/000011491).
- **Refugees, south side.**
  - About 150 stragglers start 60-250 m ahead of the Armored and run north at 4-5 m/s up the avenue, through the gaps in the gun
    line and into the gate passage (F2/000014428 shows figures at the passage mouth).
    All are through by about 11 s (see section 6).
  - About 10 freeze against the house fronts at the avenue edges (owner rule: they freeze or flee).
- **Garrison.**
  - 24 crew at the field guns. At about 12.4 s they scatter sideways and toward the gate, ahead of him (F2/000014132).
  - 10 run across the apron in front of the passage at 11.8 s, some in, most sideways (F2/000014295; direction partly ambiguous).
  - 12 on the wall top at the guns.
  - (Removed: "4 ODM soldiers fire their anchors from the wall face". No frame of this beat shows it; the only ODM move is a soldier
    dropping down the canal wall to the boat at 07:17.9, a skipped close beat.)
  - One soldier is flung north with the debris at impact (F2/000014571). Keep him a tiny tumbling silhouette (P2).
- **Refugees, north side.**
  - **Apron and quays.** About 3,000-4,000 instanced figures packed nearly wall to wall on the west quay, its lower berth and the
    apron by the arches, thinner (2-4 deep) on the east quay, plus a stream of people along the gate road from the passage
    (F2/000008162, F2/000008066, F2/000010192, F2/000007708). Faceless, 1.65 m, with variation from 1.55 to 1.80 m.
  - **Palette.** MUTED: dark brown, grey-brown, beige, cream and olive at about 85%, with about 15% soft pastel accents in dusty pink,
    lilac, pale blue and mustard (F2/000010192, F2/000010288). It must NOT be rainbow or saturated.
  - **Before the ram.** Slow shuffle (0.3-0.6 m/s) toward the landings and gangways, with small eddies.
  - **At the impact.** A panic wave spreads at about 8 m/s from (0, 30). People on the gate road and within 120 m turn and run away
    (north and east) at 3-4 m/s; the wave reaches the apron (x 150+) about 18 s into the beat and the quay crowd compresses toward
    the moored ferries (INF).
  - About 2,000 people stay on the quays at the end, because the boats cannot take them all ("No way! Please, let us on! At least my
    child!", 07:24.1 F2/000010648; "Hey, what are you doing?!", 07:20.1 F2/000010552).
- **Ferries.** 4 are visible (2 loading in F2/000007900 plus 2 under way in F2/000008162). Real speed would be about 2 m/s; in our timelapse they move at 8 m/s (INF). Positions at t = 0, on
  the canal centre x = 228:
  - F1, the lead ferry and Eren's (no close-up): y = +300, moving.
  - F2: y = +150, moving.
  - F3: moored at the west landing y = +60, casts off at t = 10 s.
  - F4: moored at the east landing y = +100 and still loading at the end.
- **Named characters.** Eren, Mikasa and Armin are on F1 and NOT distinguishable (owner SKIP). Reiner does not appear.

---------------------------------------------------------------------------------------------------------------------

## 5. FX (Eevee / GTX 1060 friendly)

- **Light.** Golden hour. Sun at 4-8 deg elevation, azimuth about 245 deg (WSW), as the code has it (SEG3_END_LIGHT).
  - Warm key #ffc98a. Sky gradient from teal-blue overhead (#6f9fb6) to peach at the horizon (#f2b98a).
  - Cumulus with gold rims and long shadows (F2/000007708, F2/000011172).
  - Shift toward dusk at the end of the take: pinker sky (#d9867a), with a purple-blue zenith as the camera flies north
    (F2/000019570).
- **Smoke columns over Shiganshina.** 6-8 in total, using existing smokecards.
  - Two kinds: 3-4 THICK dark charcoal-brown columns (#3b3632, warm-lit rims #8a6a50), 8-14 m at the base (F2/000009815,
    F2/000011416), and 3-4 THIN wavy pale grey ones (#a9a49a), 3-5 m at the base (F2/000003643). All rise 150-250 m.
  - Segmented puffy texture. They rise nearly vertical for the first 60-100 m, then bend over EAST into long drifting streamers
    (F2/000011172 seen from the north: all plumes stream to the left = east; F2/000009815 near-vertical low down).
  - 2 more columns rise just south of the inner gate.
- **Footfall dust.** Billboard puff cards (4-6 per step) in ochre (#c8a878), 1.2 s life, growing from 3 to 8 m.
- **Run dust trail.** Ground-hugging cards along the avenue behind him: 20-30 m wide, 8-12 m high, lingering 6-8 s while slowly
  dispersing (F2/000014354, F2/000014428).
- **Field gun fire.**
  - Muzzle flash: an emissive cone/sphere at 3 m, #fff0b0, 2-3 frames.
  - Muzzle smoke: a white-grey ball (#d8d4cc) growing from 4 to 12 m and drifting downwind, about 4 s.
  - Recoil: the carriage slides back 1 m.
- **Wall-top gun fire.** Same as the field guns but smaller, with puffs drifting off the wall top.
- **Ricochet** (owner rule, F2/000013843): at the shell's contact point, a gold emissive streak (#ffd060, a curve with bevel)
  0.12 s long that deflects up and sideways at 30-50 deg. A spark burst of about 40 points, plus a small grey puff on the armour.
  - Of the 4-5 impacts on head, chest and shoulders, at least 1 must be clearly readable from the camera.
  - 2 shells MISS and burst on the avenue: a small orange-yellow fireball (3-4 m, 3-4 frames) with flying embers, then a light-brown
    dirt kick 5-8 m tall (F2/000004963 shows the fireball-and-embers style, not a pure dirt geyser).
- **Impact.**
  - A 3-frame white-gold flash at the gate (F2/000014499).
  - 40-60 rigid debris chunks on precomputed ballistic arcs (no physics simulation), fanning north in a 60 deg cone from (0, 5).
    The biggest (3-6 m) land 20-60 m out, the smallest up to 150 m. Most peak at 20-45 m, which stays HIDDEN behind the 50 m wall
    from the south camera (K4: the sightline grazes the wall top at about 50 m). So give 6-8 of the bigger chunks steep arcs that
    peak at 60-80 m and fall 40-90 m north: those read above the wall top, like the house-sized blocks against the sky in
    F2/000014571. Leave 8-10 loose 1-4 m boulders lying on the lawn after they land (F2/000014988).
  - 10 brick pieces and 6 timber beams spray south and up from the gatehouse front.
  - Only if the hamlet is allowed (section 9): two cottages at (-60, 40) and (130, 60) take hits, the roof caves in and a tile puff
    rises. Otherwise the chunks land on the lawn and the gate road and splash the water strip.
- **Burst dust.** A lumpy cauliflower ball of about 40-60 overlapping toon puff cards or low-poly spheres with a noise displace,
  ochre #d1b07a with a darker core #9c8160 (F2/000014988).
  - It grows from 10 to about 40 m in diameter over 1.5 s (35-45 m: about four cottage lengths in F2/000014988), its top rises to
    40-45 m so it peeks over the wall top from the K4/K5 cameras (the sightline over the wall drops to about 32 m at y = +55), then drifts and thins over 8 s.
  - A secondary dust ring billows south out of the hole across the apron (F2/000015180).
- **Steam.** White wisps from the Armored's mouth and shoulders after the ram (F2/000015241). Small, 1-2 cards.
- **Flares.** None in this beat. Flares belong to Trost.
- **Blood.** None visible from the sky. At most 1-2 dark stains on the avenue (tasteful; F2/000004963 shows some at ground level).
- **Windmill (only if allowed).** The sails turn slowly, at about 0.12 rev/s.
- **Embers and street fires (P2).** A few small ground fires (2-3 m flame cards) at the avenue edges and drifting orange ember
  points around him (F2/000013299, F2/000013433, F2/000012958). From 200+ m only the fires read; skip the embers if costly.
- **Roof hits during the charge (P1).** In the anime he smashes roofs and tiles stream past (F2/000014354, F2/000014428). With the
  owner's upright run, add 3-4 tile/timber bursts (10-20 card fragments each) where his swinging arms clip eaves in the last 150 m.
- **Buildability on a GTX 1060 (6 GB) in Eevee.**
  - North crowd: ONE low-poly faceless figure (300-600 tris) instanced on a point cloud via Geometry Nodes, positions/anim phase
    driven per frame from a baked array (as MiniCrowd does). Never 3-4k separate objects or armatures. Total under about 2 M tris.
  - Ferries: one mesh (2-3k tris) linked 4 times, passengers as instanced points on the deck.
  - Dust/smoke: keep alpha-blended cards under about 150 on screen at once (ball 40-60, trail 30, muzzle 20-30, columns via the
    existing smokecards); overlapping blended cards are the main fill-rate cost. Use soft-edged textures, not volumetrics.
  - Debris: 40-60 precomputed keyframed rigid objects (no rigid-body sim), as already planned.
  - Sun at 4 deg casts shadows hundreds of metres long; if Eevee shadow maps flicker or alias at this angle, raise to 6-8 deg
    (still golden hour) rather than raising the shadow resolution.
  - Render one 1080p test frame at K4 and K6 (the heaviest: crowd + dust + debris) and time it before the full run.

---------------------------------------------------------------------------------------------------------------------

## 6. Choreography timeline for our one take (t in seconds within the beat, about 32 s total)

The Armored's position on the avenue (x = 0), with the run front at y:

- **t = 0-1.5:** y = -400 + 20t + 3t².
- **After t = 1.5:** y = -363 + 29 (t - 1.5).
- The gatehouse front is at y = -13, so the shoulder contacts at **T_I = 13.5 s** (his centre is at -16).
- Checkpoints: t = 3: y = -320; t = 6: -233; t = 9: -146; t = 11: -88; t = 12: -59; t = 13: -30.

| t (s) | Event |
|---|---|
| 0.0 | We leave the Carla seam. The Armored is already in the avenue at y -400 (he entered during the Carla beat, unseen; the anime's crouch-and-set at 09:31.1 is replaced by the owner's normal run), accelerating to a full run. The straggler refugees run ahead of him. The follower titans are at y -620..-560. |
| 0-10 | The ferries glide north (F1 and F2 moving, F3 and F4 loading). The north crowd shuffles. Smoke columns drift. |
| 3.0 | The wall-top guns are manned. The field crews ram their charges. |
| 5.8 / 6.3 / 6.9 / 7.4 | Wall-top guns fire (x = -25, +25, -60, +60) while he is at y -240..-195. Hits at 6.0 (chest ricochet) and 7.1 (shoulder ricochet). 6.5 and 7.6 are misses that throw up avenue dirt geysers. He does not break stride. |
| 9.0 | First field volley of 3 guns, with him at y -146. 9.15: one shell glances off his FACE (the 09:37.4 equivalent) in a big gold streak with sparks. Muzzle smoke billows over the apron. |
| 10.0 | F3 casts off from the west landing. The last stragglers squeeze into the passage. The ~10 freezers stay pressed against the house fronts. |
| 11.0 | Second field volley of 3 guns, with him at y -88: 1 ricochet off the shoulder, 2 misses. The wall-top guns fire their last round (x = +-95). |
| 11.8 | Garrison soldiers run across the apron, some into the passage ("Quickly, shut the gate!"). The crest leaf (the drop gate) starts sliding down its slot over the passage. |
| 12.4 | The gun crews scatter sideways. His feet come down inside the cannon line at 12.8 and 13.15, and one carriage is kicked over and rolls 8 m. |
| 13.1-13.5 | Shoulder drop in the last 0.4 s. The leaf's lower edge has come down to about 1/3 of the passage height: the gate still reads INTACT and closing. |
| 13.5 | IMPACT: white-gold flash, the passage, crest leaf and the brick between them explode, the hole opens (12-14 x 24-26 m narrow arch), debris fans north and 6-8 big chunks arc high over the wall top. A south dust ring rolls out of the hole. |
| 13.5-15.0 | He drives through the hole to y +25 and decelerates. The north dust ball grows to about 40 m at about (0, +55). The panic wave spreads along the gate road toward the apron and quays. Chunks land on the lawn (two cottages are hit only if the hamlet is allowed). |
| 15-18 | The dust peaks and starts to thin. Crack decals become visible on the wall face. The south side surviving brick wings are visible through the haze. The follower titans keep walking toward the gate (y -250..-150). |
| 18-23 | He stands upright in the dust north of the wall (steam), at most a few slow steps (INF). F4 is overfilled. The north crowd streams away north along the gate road and quay edges. |
| 23-32 | The ferries carry on north (F1 is at y +556 by t = 32). The camera rises and passes them. The canal widens into the river and the light shifts toward dusk. Hand off. |

---------------------------------------------------------------------------------------------------------------------

## 7. Sky-observer camera plan (one take: no cuts, no clouds, no chase)

Each key gives the camera location (x, y, z), its aim point, the lens, and an approximate pitch below the horizon. Interpolate
with Bezier/smoothstep easing; the run section uses near-constant velocity with an ease-out into the impact.
K1-K5 were REVISED in review: the earlier K0->K1 move covered 292 m in 3 s starting from rest (average 97 m/s, spline peak about
134 m/s, about 155 m/s^2), which breaks the calm one-take rule. Checked with a Catmull-Rom/Hermite spline (K0 at rest): the
revised keys peak at about 50 m/s with at most about 33 m/s^2, and he stays within about 1 deg of frame centre at K1-K5.

| Key | t (s) | Camera position | Aim point | Lens | Pitch | Note |
|---|---|---|---|---|---|---|
| K0 | 0.0 | (-130, -686, 114) | (-165, -594, 0) | 28 mm | 49 | = SEAM_IN (end of Carla). Must match the position, velocity and aim exactly. |
| K1 | 3.5 | (-180, -590, 118) | (0, -310, 10) | 32 mm | 18 | Eased start from rest (peak about 41 m/s): rise slightly and yaw about 55 deg right onto the avenue; he is at y -305, frame centre, running north. |
| K2 | 7.5 | (-215, -440, 120) | (0, -190, 10) | 35 mm | 18 | Flying north on his west side, about 215 m lateral and closing from behind-side (rear three-quarter at most), sun behind the camera. Not low, not a chase: a sky observer pacing him. The wall-top gun fire and ricochets read. |
| K3 | 11.0 | (-225, -275, 118) | (0, -80, 14) | 38 mm | 19 | The gate, the gun line, the crews and him are all in frame. Fastest part of the run (about 50 m/s). |
| K4 | 13.5 | (-215, -185, 118) | (0, -8, 18) | 38 mm | 20 | Ease-out so the camera settles at impact (about 275 m from the gate; the 50 m wall fills about a third of the frame height). The wall top sits below the camera, so the high debris and the top of the dust ball show above the wall, the rest through the hole. |
| K5 | 16.0 | (-195, -140, 132) | (10, 30, 12) | 35 mm | 24 | Slow rise during the debris. Brief hold-feel, no shake (or 1-2 px, 0.3 s at most). |
| K6 | 20.0 | (-110, -5, 170) | (45, 125, 0) | 32 mm | 39 | Craning over the wall top: the dust ball, the Armored in it, the apron crowd, the canal and F3/F4 at the quays. This is the 10:25.1 (F2/000014988) and 05:36.4 analogue. The dust ball is about 11 deg right of centre, F3/F4 17-23 deg right. |
| K7 | 24.0 | (-15, 130, 205) | (160, 290, 0) | 30 mm | 43 | The high aerial of the quays and the ferries heading north (the F2/000008162 analogue). The gate road and the lawns between road and apron are at the frame's lower left. (Corrected: the windmill at (-95, 165) is about 114 deg off-axis, behind-left, and NOT in frame.) |
| K8 | 28.0 | (105, 300, 222) | (228, 580, 0) | 30 mm | 36 | The "lone ferry at dusk" frame: F1 (y about 524, in the river) sits about 5 deg from frame centre; F2 (y about 374) has just slipped under the frame bottom. The camera is still BEHIND both ferries here. |
| K9 | 32.0 | (175, 480, 240) | (228, 1050, 0) | 28 mm | 23 | Heading north at about 45 m/s ground speed and still rising: the camera has passed F2; F1 (y about 556) is just ahead but below the frame bottom, so no ferry is in frame; the river runs to the horizon toward Wall Rose. The handoff key: the next beat (the Wall Maria overflight toward the Rose camps) starts with this exact position, velocity and aim, and continues climbing to its cruise height. |

**Rules honoured.**

- Height stays between 114 and 240 m, which is moderate. Pitch stays between 18 and 49 deg.
- The lens never goes longer than 38 mm, so nothing is over-zoomed. The Armored is about 7-9% of the frame height during the run
  (6.6% at K1, 9.4% at K4), readable but not a close-up.
- The camera never drops below the wall top, never sits directly behind the titan's back (rear three-quarter at most) and never
  gets a face close-up.
- During K1-K4 the framing is locked on him (owner rule): he stays within about 1 deg of the aim point.
- Peak speed is about 50 m/s (K2-K3 and K7-K8), peak acceleration about 33 m/s^2, starting from rest at the seam; no jumps.

**Shiganshina's later night beat** (seg 45, titans spreading north) is not in this group. If it stays in the cut, K9 must hand
off into it instead, with the same constraint of continuous velocity.

---------------------------------------------------------------------------------------------------------------------

## 8. Current render vs the anime: gap list

Sources: renders/laptop/fall3_still_armored.png, fall3_still_ferries.png, fall3_still_vow.png, master_contact.jpg (0:30.53
fall3 t = 4.3 and 0:35.53 fall3 t = 9.3), tripo_armored_image_preview.png.

**P0**

1. **No gatehouse.** The inner gate is a featureless grey recess with a few slot windows. Build the red-brick gatehouse on BOTH faces
   (the low 32 x 10 m brick front with cream cornice, wings with pointed doors and small tile roofs, the small pointed passage, and
   above it the crest leaf with corbel row and two chains hanging in the pilaster bay, the guide continuing up the wall; section 3).
   (fall3_still_armored)
2. **The ram is never shown.** The still and the master at 0:30 show the aftermath (the Armored standing static in the hole) from
   a low angle staring at the wall face, or the wall top from above with the gate hidden ("INNER GATE DESTROYED"). The intact gate,
   the run, the cannons and the impact must all be visible from the sky with framing locked on him (section 7, K1-K4).
3. **The breach shape is wrong.** It is a wide ragged rectangle with a frame above it. It should be a tall NARROW arch hole
   (12-14 x 24-26 m), the passage and crest leaf gone, the brick side wings standing, and radiating cracks.
4. **No dust.** There is no footfall dust, no run trail, no lumpy 40 m burst ball north and no south dust ring. Today: a clean
   ground with a few grey cubes.
5. **No Garrison defence.** There are no field guns, no wall-top guns, no muzzle flashes, no ricochets off the armour and no
   scattering crews (owner rule).
6. **The ferries are flat rafts carrying a block of people.** Replace them with the 34 x 10 m ferry (cabin, barrel roof, window
   row, A-frame end trusses, railing) and 4 ferries in the irregular states of section 4, not 5 evenly spaced in a line.
7. **The canal is wrong.** It is a flat, saturated blue, curving ribbon lying on grass. It needs to be a straight stone-lined sunken
   canal 30 m wide with about 20 m paved quays both sides (lower berth on the west, battered revetment on the east), landings,
   gangways, teal water and wakes, plus the twin low arched water gates in the wall and the high bridge on three pylons.
8. **The crowd is wrong.** It is a single file of rainbow-saturated figures on the grass bank. It needs 3-4k instanced figures
   packed on the quay apron and quays, in the muted palette (section 4).
9. **The vow hold must go.** The kids at the bow at s 8-11 (fall3_still_vow) form a close beat the owner has SKIPPED. Replace it
   with the K6-K9 aerial following the ferries north.
10. **The wall colour is off.** Grey-lilac with too few, too wide pilasters. It should be tan sandstone, with 3.5 m pilasters every
    16 m rising above the parapet and a string course at 12 m.

**P1**

11. The area south of the gate is a green grass strip plus a grey gravel square. It needs the dirt avenue (26 m, ruts, grass verges)
    lined tight with 3-4 storey houses right up to the gate apron.
12. There are no cypress-lined quays. The current render ALSO has half-timber houses north of the wall (fall3_still_ferries),
    which breaks the owner's "only Shiganshina and Trost have buildings" rule: remove them unless the owner allows the hamlet
    (section 9). If allowed, their roofs use the town's orange-brown tile (only shaded darker).
13. Debris fans north on ballistic arcs: big blocks near, small far, 6-8 big chunks peaking at 60-80 m so they read above the wall
    top; boulders left on the lawn.
14. The crest leaf (the drop gate) slides down during 11.8-13.5 s, so the gate reads "closing but intact" at impact.
15. Add the follower pure titans (3) on the avenue behind him.
16. After the ram, the Armored drives through, straightens up and stands steaming in the dust north of the wall. He must not stand
    frozen IN the hole.
17. Armored material: in toon, the plates should read warmer, more golden (#e2c47a). Eye glow only if the owner allows it (section 4). Check that the
    Tripo model faces +y (it imports sideways). The model shape is fine (tripo_armored_image_preview).
18. Stragglers freezing at the house fronts, and the panic wave on the north quays at impact.
19. Light: a golden-hour sky with gold-rimmed cumulus and long shadows, then dusk at the end. The current renders are flat grey-blue
    and overcast-looking (fall3_still_ferries, fall3_still_vow).

**P2**

20. Lanterns on the ferries and the disc rows on the cabin roof.
21. The cables/rails strung horizontally in front of the wall by the canal (F2/000011172): most likely the chains/rails of the high
    bridge (section 2), so they come with it.
22. The one flung Garrison soldier.
23. The water strip along the north wall foot with the timber road bridge (F2/000014988, F1/000007280, F1/000007496). Promote to
    P1: it is clearly visible in THE sky frame of the beat (10:25.1).
24. The two-pier truss bridge on the river further north (F2/000019570).
25. The anime passage is only about 5 x 7 m (section 3); ours is 14 x 20 m.
26. The district plan is a stadium shape in our code but a D or semicircle in the anime (F2/000019762). This belongs to another
    group; noted only.

---------------------------------------------------------------------------------------------------------------------

## 9. Owner-rule overrides (where we differ from the anime on purpose)

- **Gait.** In the anime he walks hunched, then charges with his torso nearly horizontal for several seconds (F2/000013299,
  F2/000014354), after first stopping and crouching low like a sprinter getting set (09:31.1 F2/000013692). We use an upright
  normal run with only a 0.4 s shoulder drop and no crouch (owner rule 13:40 10/25).
- **Wall-top guns.** The anime shows only ground field guns at the gatehouse firing, plus one off-screen explosion. Wall-top guns
  firing come from the owner rule ("wall cannons fire, shells bounce off"). We keep both, and the ground battery stays because it is
  lore.
- **Camera.** The anime is almost all ground-level or low close-ups. Ours is entirely aerial, a moderate-height observer. The only
  anime aerials we copy are 05:21.5, 05:36.4, 05:40.4, 07:59.3 and 10:25.1.
- **Gate state.** In the anime the passage is open and glowing, then ordered shut. The owner says "fully intact until the ram", so
  we show the passage open early for the refugees, the crest leaf sliding down from 11.8 s and the structure intact up to impact.
- **Skipped scenes.** Eren, Mikasa and Armin on the ferry (the vow and crying close-ups), Hannes, and the gate-room argument are
  all skipped.
- **Hamlet.** The anime shows a hamlet, a windmill and fields north of the inner gate, plus farm villages along the river further
  north (F2/000008162, F2/000019570). The owner says only Shiganshina and Trost have buildings.
  - DEFAULT (owner rule wins): NO cottages, NO windmill and no quay-side houses north of the wall. Keep only the wall-attached
    infrastructure the evacuation needs: the quays, lower berth, landings, gangways, the high bridge on three pylons, the water
    strip with its road bridge, lawns, footpaths, cypresses and the river. Add NO villages along the river.
  - OWNER DECISION: allow a small exception (≤ 10 cottages and the windmill within 250 m of the inner gate, section 2) as part of
    the Shiganshina complex, because the anime's evacuation happens among them (F2/000007708, F2/000007804, F2/000010192)?
    (The earlier "guard tower" was the west pylon of the bridge and is kept as part of the bridge.)
- **Timing.** The anime spreads the Armored's approach over minutes of cut-away time (06:49-10:04). We compress it to a 13.5 s
  continuous run at a physically consistent sprint.
- **Speeds.** The ferries move at a timelapse 8 m/s, about 4x real (INF).
- **Blood.** The anime shows blood at ground level. We show none from the sky.
- **Faces.** The anime Armored has glowing eyes; owner rule "characters are faceless". Default no eyes; owner decides.

---------------------------------------------------------------------------------------------------------------------

## 10. Must-have lore details (checklist)

- [ ] Red-orange BRICK gatehouse on BOTH faces of the inner gate: low brick front with cream cornice, a small pointed passage, and
      above it the crest leaf (goddess profile, corbel row) hanging on two chains in the pilaster bay (ep02 05:56.4 F2/000008546,
      06:39.4 F2/000009575, 10:01.8 F2/000014428; north face ep01 05:12.6 F1/000007496).
- [ ] Flanking brick wings with small pointed-arch doors (08:07.5 F2/000011688, 09:56.2 F2/000014295).
- [ ] Brick crest panel between pale jambs on the north face, chains above (07:43.1 F2/000011103).
- [ ] Straight dirt avenue from the outer to the inner gate, lined with tall half-timber houses, gatehouse at the end (10:01.8 F2/000014428, 06:49.4 F2/000009815).
- [ ] 5-6 field guns with big spoked wheels in a line across the apron, Garrison crews (06:39.4, 07:52.4 F2/000011327, 10:01.8 F2/000014428).
- [ ] Wall-top guns on circular pads with rails (ep01 04:46 F1/000006944 area; owner rule).
- [ ] A cannon shell glancing off the Armored as a gold streak (09:37.4 F2/000013843). He does not stop.
- [ ] Crews scatter as his legs pass over the cannon line, with a pure titan following (09:49.4 F2/000014132).
- [ ] Footfall dust puffs and a ground dust trail (09:20.3 F2/000013433, 09:58.7 F2/000014354).
- [ ] Gate closing ordered just before the ram, the crest leaf starting to slide down (08:10.7-08:42.6; 09:56.2 F2/000014295).
- [ ] House-sized stone blocks flung through the air, plus a soldier (10:07.7 F2/000014571).
- [ ] The breach as a TALL arch-shaped bright hole, side wings surviving, radiating cracks (10:22.2 F2/000014917, 10:33.1 F2/000015180, 10:45.6 F2/000015478).
- [ ] A top-down lumpy ochre dust ball about 40 m on the lawn north of the gate, armour glint inside, loose boulders around it, the
      water strip along the wall foot (10:25.1 F2/000014988).
- [ ] The Armored standing in the haze in front of the hole afterwards, with steam from the mouth (10:35.7 F2/000015241, 10:49.6
      F2/000015574).
- [ ] Evacuation on the NORTH side: refugees streaming from the gate up the road to the quays (05:21.5 F2/000007708). Hamlet and
      windmill (west of the road) only if the owner allows them.
- [ ] Twin arched water gates where the canal exits the wall EAST of the land gate (05:25.5 F2/000007804, 11:02.7 F2/000015890).
- [ ] High bridge on three square stone pylons with orange pyramid caps across the canal by the arches, ferries passing under (05:29.5 F2/000007900).
- [ ] Straight stone-lined, sunken canal, teal water, wide paved quays on BOTH sides packed with people, a lower waterline berth, cypresses (05:40.4 F2/000008162, 05:36.4 F2/000008066, 06:06.6 F2/000008790).
- [ ] Stair landings and timber gangways to the ferries (05:36.4 F2/000008066, 07:13.1 F2/000010384).
- [ ] Ferry design: oval dark hull, long cabin with a window row, barrel roof, A-frame end trusses, railing; packed decks, "around 500 onboard" (05:33.0 F2/000007983, 10:40.1 F2/000015348, 11:30.4 F2/000016554).
- [ ] Two ferries loading at once, ferries leaving north one by one (05:29.5 F2/000007900, 05:40.4 F2/000008162).
- [ ] Muted refugee clothing with a few colour accents (07:05.1 F2/000010192).
- [ ] Golden-hour light, gold-rimmed cumulus, 6-8 smoke columns over Shiganshina, thick dark and thin pale grey, bending east up high (02:31.9 F2/000003643, 07:46.0 F2/000011172, 13:44.2 F2/000019762).
- [ ] A lone ferry on a widening river at dusk, heading for Rose: framed at K8 (t = 28 s), out of frame by K9 (13:36.2 F2/000019570).

---------------------------------------------------------------------------------------------------------------------

## 11. Verification log (adversarial lore + buildability review, 2026-10-26)

Every cited frame in sections 1-10 was opened; ep02 sheets 05-14 and ep01 sheet 09 were scanned for contradicting or missing
detail; the camera keys were checked numerically (Hermite/Catmull-Rom spline, K0 at rest); repo constants were checked
(scene.py CX = 228, OUTER_GATE y = -720, GATE_W/H 14 x 20; states845.py INNER_HOLE (0, 0, 12.5, 29); render_fall2.py SEAM_IN).

**Corrected (claim was wrong or unsupported)**
1. Camera K0->K1: 292 m in 3 s from rest (avg 97 m/s, peak about 134 m/s, about 155 m/s^2) broke the calm one-take rule. K1-K5
   re-keyed (section 7): peak about 50 m/s, about 33 m/s^2, Armored within about 1 deg of the aim point at K1-K5.
2. K7 said the windmill and hamlet were at the frame's left edge: the windmill is about 114 deg off-axis (behind-left). Fixed.
3. K8/K9 said the camera passes and leads the ferries: at K8 it is still behind both (F1 framed near centre), at K9 F1 is ahead
   but below the frame. The "lone ferry at dusk" frame is now K8; checklist updated.
4. Debris "peak 20-45 m so some clear the wall top": a 50 m wall hides anything below 50 m from the south camera. Now 6-8 chunks
   peak at 60-80 m (F2/000014571).
5. Gatehouse: no "brick tower 20 x 28 m projecting 8 m", and no "dark drop plate inside the passage". The brick crest block hanging
   on two chains in the pilaster bay is the drop-gate leaf (F2/000011688, F2/000008546, F2/000011103). The whole brick composition
   is about 32 m wide and about 22 m tall, and the passage is only about 5 x 7 m (F2/000014428 bay scale, F2/000014295 figures).
6. North face: it is the same ensemble (brick front, wings, pointed doors, crest leaf), not "a darker block"
   (ep01 F1/000007400, F1/000007496; F2/000007708).
7. Breach: 16 x 26 m changed to a narrower 12-14 x 24-26 m arch (h:w about 2; F2/000014917, F2/000015478).
8. Dust ball: 50 m changed to 35-45 m (about four cottage lengths in F2/000014988); top 40-45 m so it shows over the wall.
9. "Dust at the avenue end where the Armored comes in" (F2/000009815): it is a pure titan in that dust; the Armored first appears
   at 09:00.5 (F2/000012958).
10. "Walks NW into the dust" (F2/000015478): the frames show him standing upright in front of the hole (F2/000015574); the walk
    and its direction are now INF and minimal.
11. "Chain footbridge, two pylon pairs, 3 m deck" and "guard tower at (205, 15)": it is a high bridge on three single square
    pylons with orange pyramid caps, deck at pylon-top height, ferries pass under (F2/000007900 crop); the "guard tower" in
    F2/000007804 is one of its pylons.
12. Plaza x = +20..+197: F2/000007804 shows lawns, paths and cottages between the road and the quay; the paving is a quay apron
    by the arches (x = +150..+213). Quays widened 16 -> about 20 m (F2/000008162).
13. Water arches: crowns 14 m -> about 8-9 m, spans 11-13 m (F2/000015890, F2/000007804).
14. Field battery: "3 + 3 guns either side of a 26 m lane" -> 5-6 guns spread across the apron (F2/000014428 crop); shot
    pyramids marked INF.
15. Field gun: "black iron barrel, bronze rings, 2.4 m wheels, 12 spokes" -> dark grey-bronze barrel, 2.0-2.4 m wheels,
    12-14 spokes (F2/000011327, F2/000011764).
16. Shell misses: "light-brown dirt geysers" cited to F2/000004963, which actually shows an orange fireball with embers. Fixed.
17. Smoke: "dark charcoal, leaning 15-20 deg east" -> thick dark plus thin pale grey columns (F2/000003643), near-vertical low,
    bending east into streamers up high (F2/000011172).
18. Hamlet roofs "darker than Shiganshina's": they are the same orange-brown tile, dark only in shade (F2/000007900,
    F2/000010288). Windmill cap: orange-red conical, not dark (F2/000015574).
19. Ferry: windows are upright rectangles with timber frames in brown cabin walls; truss railing rises above the roof
    (F2/000007983, F2/000010384, F2/000015348).
20. "2,000 left on the quays (lore, 06:09.5)": 06:09.5 is "abandon your possessions"; the evidence is 07:20.1 / 07:24.1
    (F2/000010552, F2/000010648). "500 people each": the 11:30.4 line does not say per ferry; marked ambiguous.
21. "10 Garrison run into the passage" (F2/000014295): most run away from it and sideways; reworded. "4 ODM soldiers fire anchors
    from the wall face": no evidence in this beat, removed.
22. Crowd palette accents: red/mustard/teal -> dusty pink, lilac, pale blue, mustard (F2/000010192).
23. Avenue houses "ridges parallel to the avenue": mixed, with street-facing gables, turrets and a crow-step gable (F2/000014428).

**Added (missing detail, with evidence)**
24. A water strip along the north wall foot with a timber road bridge (F2/000014988, F1/000007280, F1/000007496), promoted to P1.
25. A lower waterline berth on the west quay; a battered revetment on the east bank (F2/000008066, F2/000010288).
26. The Armored's crouch-and-set before the charge (F2/000013692), listed as an owner override (normal run, no crouch).
27. Footfalls crack and lift the paving (F2/000013433); street rubble, fires, embers and the kick boulders on the south side
    (F2/000012958, F2/000003429, F2/000004257).
28. Roof and tile bursts along the avenue during the charge (F2/000014354, F2/000014428).
29. Loose boulders lying around the dust ball afterwards (F2/000014988).
30. Inside the district the twin arches feed two parallel canals (F2/000015890, F2/000019762).
31. Big trees by the gate at the avenue's west side; dirt-and-pebble apron under the guns (F2/000014428, F2/000011327).
32. Buildability on a GTX 1060 (section 5): Geometry Nodes instancing for the crowd, a cap on alpha-blended cards, keyframed
    debris without simulation, a sun-angle fallback for shadows, and a test-frame budget at K4 and K6.

**Owner-rule compliance changes**
33. Hamlet, windmill and quay houses north of the wall are now OMITTED by default ("only Shiganshina and Trost have buildings");
    the earlier draft recommended keeping them. The current render also breaks this rule (fall3_still_ferries).
34. The Armored's glowing eyes are now default OFF pending the owner's ruling on the faceless rule.
35. Checked and kept: the beat starts at the WEST (left-of-gate) Carla seam; skipped beats (vow, Hannes, gate room, boat close-ups)
    stay skipped; true scale; normal run with a 0.4 s shoulder drop; refugees freeze or flee; the gate intact until the ram;
    no cart in this beat; no cuts.

**Checked and confirmed (no change)**
Canal on the EAST (F2/000007804 looking south: arches left); the wall-top gun design (F1/000006860); gold ricochet streak
(F2/000013843); crews scatter with a red pure titan behind (F2/000014132); flung soldier and house-sized blocks (F2/000014571);
side wings surviving with radiating cracks (F2/000015180); steam from the mouth (F2/000015241); ferry design and top-down view
(F2/000007900, F2/000007923, F2/000008066); two ferries loading (F2/000007900); lantern (F2/000010384); dusk river with a two-pier
truss bridge, plus farm villages that we omit (F2/000019570); the Armored run equation and checkpoints (T_I = 13.5 s); the
Froude-scaled gait (29 m/s, 1.55 steps/s, 18-19 m steps).

**Open issues for the owner**
- A. Allow the quay hamlet and windmill north of the inner wall (the anime's evacuation setting) as an exception to "buildings only
  in Shiganshina/Trost"? Default: no.
- B. May the Armored's eyes glow (anime) under the faceless rule? Default: no.
- C. Gate passage: keep our 14 x 20 m opening or shrink toward the anime's about 5 x 7 m? If kept, the crest leaf must grow to about
  16 x 22 m to cover it when it slides down.
