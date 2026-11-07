# Backrooms special shot list, read by build_edl.py (11/7 KST).
# A shot is (phrase, clip, in_s, -clean_s[, opts]): it starts 0.08 s before the first word of the exact script phrase and runs until
# the next shot. in_s = the in-point in the clip (seconds), -clean_s = seconds of clean picture from the in-point (no cut to another
# scene, no text, no end card); the builder slows a shot (never below 0.4x) when the clean span is shorter than its slot.
# opts (string): z=zoom (1.333 fills a 4:3 tape), dx/dy=pan in px, flip=1, g=gamma, a=clip audio dB (real foley under the voice).
# GENERATED SKELETON from shot_plan.md (cloud, 11/7): on the laptop replace every TODO with the verified in-point and clean span,
# switch to another candidate clip when the first one does not hold the moment, and keep each comment true to what is on screen.
# Extra cuts can be added on any other exact script phrase. Do not use: end_phil, s2_therapy, s7_dinner_full, s4_tree_pool (subtitles),
# the trailer and x_a24_c/d text or logo spans, and the last 16 s of every JoBlo clip (end card).
# Inserts: ins(after_phrase, seconds, kind, shots=[(t, clip, in, 1.0, opts)], sub=..., q=...). For a film line, in = 0.25 s before the
# first word, seconds = line length + 0.35 s, opts 'lufs=-17' (the line is levelled), sub = the words exactly as spoken.
TODO = None
T4 = 'z=1.333'   # the 1990 tape is 4:3 inside 16:9: zoom to fill
# ---------------------------------------------------------------- s00 cold open (15.7 s): one hard cut per caption --------------
X.append(sec('s00', [
  (0, 's8_pack_b', 92.72, -0.53),  # FRAME 0: Captain Clark big, bright, full upper body, tricorn hat, low angle in the store (= jf 289.13, the clearest face shot)
  ('went into', 's3_kids_enter', 63.40, -1.50, 'z=1.333'),  # Clark leans into the taped store wall and sinks into it, bag in hand
  ('the backrooms', 's1_first_a', 18.40, -1.40),  # wide empty yellow room, fluorescent ceiling, nobody in it
  ('in this movie', 's8_chase_a', 237.35, -0.95),  # the Escher space: endless floors of shelving around the giant drop, Mary tiny at the top (= jf 129.03)
  ('and they got', 's7_joblo_reveal', 269.15, -1.40),  # Mary terrified, close, low angle (after Captain Clark looms)
  ('chased', 's8_chase_a', 122.75, -0.85),  # Mary sprinting away down the fake apartment street (= jf 14.43)
  ('dragged', 's3_joblo_pullup', 68.70, -2.80, 'z=1.333'),  # Bobby yanked into the ramp hole on the rope, Kat and Clark grabbing him (no body)
  ('lost', 's3_joblo_pullup', 348.50, -3.00, 'z=1.333'),  # Clark tiny and alone at the far wall of the lit pool room
  ('eaten', 's7_joblo_reveal', 286.95, -1.10),  # QA fix: Mary's shocked gasp right after the grab (no bite, no silhouette)
  ('only one of them', 's8_chase_a', 124.95, -0.90),  # Mary running toward camera (= jf 16.63)
  ('made it back out', 'end_extract', 48.60, -1.30),  # hazmat men lift Mary up off the floor, her face (= jf ~449)
  ("now it's your turn", 's1_joblo_first', 21.80, -1.40),  # QA fix: Clark in the yellow room looks straight up into the lens
  ('and how long', 's1_joblo_first', 151.00, -1.20),  # POV push through empty yellow rooms (pillar)
  ('would you survive', 's8_pack_b', 121.20, -0.85, 'g=1.25'),  # Captain Clark's silhouette in the lit gap at the end of a dark hall, reaching
  ('in the backrooms', 's1_joblo_first', 162.20, -1.60),  # empty yellow room, slow pan, hold
  ], extra=[('cap', w, a, b) for w, a, b in [
    ('Five people', 0, 'went into'), ('Went into', 'went into', 'the backrooms'), ('The Backrooms', 'the backrooms', 'in this movie'),
    ('In this movie', 'in this movie', 'and they got'), ('And they got', 'and they got', 'chased'), ('Chased', 'chased', 'dragged'),
    ('Dragged', 'dragged', 'lost'), ('Lost', 'lost', 'eaten'), ('Eaten', 'eaten', 'only one of them'), ('Only one of them', 'only one of them', 'made it back out'),
    ('Made it back out', 'made it back out', "now it's your turn"), ("Now it's your turn", "now it's your turn", 'and how long'),
    ('And how long', 'and how long', 'would you survive'), ('Would you survive', 'would you survive', 'in the backrooms'),
    ('In the Backrooms?', 'in the backrooms', 999)]], clip_db=-22))
for ov in X[-1]['overlays']:   # QA fix: snap each caption to the cut's frame (it lagged one frame at 7 cuts)
    if ov[0] == 'cap':
        ov[2] = max(0.0, round(ov[2] * 30) / 30 - 0.005) if ov[2] > 0 else 0.0
        if ov[3] < 900: ov[3] = round(ov[3] * 30) / 30 - 0.005
# ---------------------------------------------------------------- s01 the 1990 tape (35.4 s) ------------------------------------
X.append(sec('s01', [
  (0, 'op_joblo_1990', 4.00, -3.90, 'z=1.333'),  # VHS POV: wall on the left, empty yellow room beyond
  ('naren a researcher', 'op_joblo_1990', 69.60, -3.00, 'z=1.333'),  # Naren's yellow hazmat sleeve + blue glove pushing past a bench
  ('has lost his team', 'op_joblo_1990', 22.00, -3.00, 'z=1.333'),  # camera turning through empty rooms, alone
  ("and he's on the radio", 'op_joblo_1990', 108.00, -3.20, 'z=1.333'),  # the radio set with the ball mic, amber dials
  ('nobody answers', 'op_joblo_1990', 120.00, -1.60, 'z=1.333'),  # radio and floppy disks on the desk, nothing happening
  ('down the hall a door', 'op_joblo_1990', 276.60, -2.60, 'z=1.333'),  # long yellow corridor, lit doorway far down the dark end
  ('something huge steps out', 'op_joblo_1990', 311.20, -0.90, 'z=1.333'),  # the camera rushes at the mural room's yellow doorway
  ('steps out', 'op_joblo_1990', 312.10, -0.50, 'z=1.333'),  # NEW CUT: black legs fill the doorway (312.2-312.4)
  ('and naren runs', 'op_joblo_1990', 288.00, -3.50, 'z=1.333'),  # camera running down the yellow corridor
  ('a room covered in', 'op_joblo_1990', 302.00, -2.80, 'z=1.333'),  # the dead end: beach/sky photo-mural room, yellow door
  ('and the moment he runs back', 'op_joblo_1990', 309.90, -1.45, 'z=1.333'),  # turning back to the mural room's door
  ('he runs straight into it', 'op_joblo_1990', 312.90, -0.75, 'z=1.333'),  # camera tumbling to the floor (no figure, nothing graphic)
  ('he had training', 'op_joblo_1990', 314.80, -2.90, 'z=1.333'),  # the dropped camera lying still, mural ceiling
  ("and he still didn't", 'op_joblo_1990', 323.10, -2.10, 'z=1.333'),  # NEW CUT: film shot of a CRT in the dark showing blue, then static
  ('and you have none of that', 's1_a24_clip', 0.05, -2.35, 'g=1.25'),  # Clark walking alone through his dark store
  ('the number in the corner', 's1_joblo_first', 11.80, -3.20),  # Clark on all fours in the empty yellow room, furniture behind
  ('and in here', 's1_joblo_first', 33.80, -2.60),  # Clark from behind, endless yellow room
  ], inserts=[ins('come and get him', 3.5, 'film', shots=[(0, 'op_joblo_1990', 128.37, 1.0, T4 + ',lufs=-17')], sub="There was something else in here.")],
  extra=[('date', ['JUNE 19, 1990'], 'dated june nineteenth', 'naren a researcher')]))
# ---------------------------------------------------------------- s02 THE SLIT (74.2 s) -----------------------------------------
X.append(sec('s02', [
  (0, 's1_commercial', 2.30, -1.30),  # Cap'n Clark at the helm in the store ad (in-film banner)
  ('a failed architect', 'd_clark_discovers', 22.90, -4.20),  # v2: Clark close, tired, store lamps behind (logo-free upload)
  ('who sleeps in the back', 'd_clark_discovers', 6.30, -3.60),  # v2: Clark asleep in a bed on the store floor
  ('the lights flicker', 'd_clark_discovers', 19.50, -2.80, 'g=1.25'),  # v2: dark store aisle, light level jumping
  ('there are two breakers', 'd_clark_discovers', 37.80, -3.00),  # v2: close, his hands on the two extra breakers
  ('and one night the tv', 's1_first_b', 6.85, -2.85, 'z=1.3,g=1.25'),  # the TV in the dark store, picture glitches at the end
  ('with a figure standing', 'd_clark_discovers', 0.35, -2.00, 'g=1.25'),  # v2: the store TV shows a yellow room, small figure in it
  ('you flip the strange breakers', 'd_clark_discovers', 44.60, -2.00),  # v2: wide, Clark at the breaker panel flipping them
  ('the store goes dark', 'd_clark_discovers', 49.20, -5.00, 'g=1.4'),  # v2: the store goes black, Clark's silhouette
  ('and there it is', 's1_a24_clip', 10.85, -1.60, 'g=1.25'),  # Clark close in the dark, staring at the glow
  ('a thin line of light', 's1_a24_clip', 26.60, -4.00, 'g=1.75'),  # the wall: thin vertical slit of light, glow on the plaster
  ('you lean on it', 's1_a24_clip', 55.00, -2.90, 'g=1.4'),  # Clark against the glowing wall, hands flat on it
  ('fall straight through', 's1_a24_clip', 58.10, -2.20),  # NEW CUT: Clark tumbles onto the yellow carpet
  ('into an empty yellow room', 's1_joblo_first', 6.00, -2.00),  # Clark lying on the yellow floor
  ('of melted furniture', 's1_joblo_first', 101.00, -2.00),  # fused furniture heap, Clark small behind
  ('and since you can step', 's1_joblo_first', 63.00, -2.60, 'g=1.25'),  # hand out of the wall, Clark back in the dark store
  ('you explore', 's1_joblo_first', 84.10, -1.50),  # Clark standing in a yellow room
  ("there's a backwards stop sign", 's1_joblo_first', 283.00, -2.50),  # mirrored STOP sign, Clark crouched behind
  ('a dead bird', 's1_first_a', 2.50, -2.90),  # the green parrot dead on the floor, Clark's legs, throne behind
  ('and a voice saying hello', 's1_joblo_first', 40.20, -2.50),  # Clark turning, listening
  ('in dozens of languages', 's1_joblo_first', 45.00, -2.00),  # Clark reaching toward the wall, following
  ('coming from a cardboard caveman', 's1_joblo_first', 36.60, -3.30),  # Clark turning to follow the sound (no caveman in my clips)
  ('behind a fake tile', 'op_joblo_1990', 270.20, -1.60, 'z=1.333'),  # ceiling tiles, stained tile (on the 1990 tape)
  ("naren's bag full of tapes", 'op_joblo_1990', 122.00, -2.00, 'z=1.333'),  # Naren's desk: radio, cassette tapes, disks
  ('and further in', 's1_joblo_first', 182.90, -1.50),  # deep wide room, Clark far off, shoes on the floor
  ('the chair from your own', 's1_first_a', 7.60, -3.40),  # Clark walks up to the purple throne
  ('slightly wrong', 's1_first_a', 12.20, -1.80),  # the throne close, Clark touching it
  ('with shoes sticking out', 's1_first_a', 38.75, -2.60),  # Clark by the hole, black shoes sticking out of the floor
  ('then the thuds start', 's1_joblo_first', 133.00, -2.00),  # Clark by the furniture, turning his head
  ('the caveman flies', 's1_joblo_first', 137.40, -3.80),  # a dark cutout spins through the air across the room
  ('and you squeeze through', 's1_joblo_first', 263.00, -2.50),  # Clark on his knees at the tiny door
  ('and run until', 's1_joblo_first', 292.20, -1.60),  # Clark running toward the camera
  ('back in your store', 's1_joblo_first', 342.50, -3.00, 'g=1.4'),  # dark store, Clark gripping the stool
  ('a camera in there', 's1_joblo_first', 217.00, -2.30),  # tunnel's square opening frames Clark (surveillance view)
  ('on a tape dated', 's1_first_b', 1.55, -2.40, 'z=1.3,g=1.25'),  # store TV playing a tape
  ('one trip through that wall', 's1_a24_clip', 7.70, -1.30, 'g=1.75'),  # the slit glowing in the dark wall
  ('gives you a ninety', 's1_first_a', 215.00, -2.80, 'g=1.4'),  # Clark in the dark store, staring
  ('the best it will ever be', 's1_joblo_first', 321.00, -2.50),  # wide empty yellow room, furniture far off
  ('rule one', 's1_first_a', 15.85, -2.40),  # wide: Clark beside the wrong copy of his chair
  ('leave', 's1_joblo_first', 76.00, -2.60, 'g=1.4'),  # Clark at the store wall in the dark, edging along it
  ], inserts=[ins('so what do you do', 0.9, 'choice', q='so what do you do')],
  extra=[('date', ['JUNE 29, 1990'], 'dated june twenty-ninth', 'one trip through that wall')]))
# ---------------------------------------------------------------- s03 THE MAP (39.6 s) ------------------------------------------
X.append(sec('s03', [
  (0, 's1_a24_clip', 39.20, -2.90, 'g=1.25'),  # Clark in profile at the glowing wall
  ('so what do you do', 's1_a24_clip', 53.20, -1.70, 'g=1.25'),  # NEW CUT: Clark at the wall, head bowed
  ('you go back every night', 's1_joblo_first', 89.00, -3.50),  # Clark back inside a yellow room, looking around
  ('and you start drawing a map', 's2_tells_mary', 173.35, -2.05),  # Clark's hands unfold his hand-drawn maze map on the table
  ('you ask your therapist mary', 's2_tells_mary', 39.45, -5.10),  # Mary in her armchair, the therapy room
  ("if she's ever had someone committed", 's2_tells_mary', 36.75, -2.60),  # Clark asking "You ever 5150 someone?" (37.1-38.2)
  ('then tell her the store', 's2_tells_mary', 90.10, -5.70),  # Clark leaning in, explaining with his hands ("the store just keeps going")
  ('close but wrong', 's2_tells_mary', 95.95, -3.60),  # Mary's face, not following
  ('like a dog drawn by someone', 's2_tells_mary', 117.30, -4.10),  # Clark gesturing through the dog analogy (117.5-120.8); no dog drawing exists
  ('and your map is a maze', 's2_tells_mary', 183.30, -1.80),  # Mary holding the maze map close (after the film line ends 182.84)
  ('that goes on and on', 's2_tells_mary', 189.50, -5.00),  # Clark in his chair, explaining the hidden entrance
  ("she doesn't believe you", 's2_tells_mary', 199.80, -4.10),  # Mary with the map on her lap, unconvinced
  ('so you swear', 's2_tells_mary', 215.40, -6.50),  # Clark on his feet, pointing: he'll come back with proof
  ('that drops you to seventy', 's1_joblo_first', 147.00, -3.00),  # Clark tiny and alone among the pillars
  ('because a trained scientist', 'op_joblo_1990', 136.20, -3.40, 'z=1.333'),  # Naren's radio, amber dials, mic (1990 tape)
  ('and you keep going in alone', 's1_joblo_first', 241.10, -2.90),  # Clark walking deeper, alone
  ('rule two', 's1_a24_clip', 50.50, -2.60, 'g=1.25'),  # Clark at the glowing slit wall
  ('because this place only has to win once', 's1_joblo_first', 152.40, -3.00, 'g=1.25'),  # slow push into dimmer empty rooms
  ], inserts=[ins('so what do you do', 0.9, 'choice', q='so what do you do'),
              ins('and on and on', 1.95, 'film', shots=[(0, 's2_tells_mary', 181.03, 1.0, 'lufs=-17')], sub="Sometimes I'm scared I'll get lost.")]))
# ---------------------------------------------------------------- s04 THE LAUNDRY ROOM (47.0 s) ---------------------------------
X.append(sec('s04', [
  (0, 's3_kids_enter', 16.50, -7.00, 'z=1.333'),  # Clark in the store packing the gear bag (rope, flashlight) for the trip
  ('your assistant manager kat', 's3_kids_enter', 53.50, -3.00, 'z=1.333'),  # Kat close, in the store, wide-eyed
  ('and her boyfriend bobby', 's3_kids_enter', 1.30, -4.40, 'z=1.333'),  # Bobby filming himself in a store mirror with the camcorder
  ('and you lead them', 's3_kids_enter', 111.90, -6.20, 'z=1.333'),  # Kat stepping out of the taped wall into the yellow rooms
  ('a steep ramp down', 's3_laundry', 27.60, -3.40, 'z=1.333'),  # the long steep ramp, looking straight down it
  ('bobby volunteers', 's3_joblo_pullup', 48.00, -8.50, 'z=1.333'),  # Bobby with the rope tied at his waist, Kat checking him
  ('you tie a rope', 's3_laundry', 0.00, -4.20, 'z=1.333'),  # hands knotting the rope by the bed
  ('and he jokes', 's3_laundry', 33.70, -3.60, 'z=1.333'),  # Kat's worried face while Bobby (behind the camera) says "tell my mom I love her"
  ('down there is a basement', 's3_laundry', 97.80, -3.80, 'z=1.333'),  # the basement: piles of laundry under small lit windows
  ('with a t-shirt bobby', 's3_laundry', 136.60, -2.60, 'z=1.333,g=1.25'),  # his T-shirt surfacing in the pile
  ('a room turned on its side', 's3_laundry', 151.50, -6.00, 'z=1.333'),  # the tilted room: floor as a wall, windows sideways
  ('a cardboard caveman torn in half', 's3_laundry', 164.50, -4.50, 'z=1.333,g=1.25'),  # the torn cardboard caveman lying on the laundry pile
  ('and when a light flickers', 's3_laundry', 188.60, -3.00, 'z=1.333,g=1.25'),  # the dim room, the light pulsing (static camera)
  ('bobby sees something', 's3_laundry', 191.80, -3.40, 'z=1.333,g=1.25'),  # Bobby's camera fixed on the black open doorway
  ('you pull', 's3_joblo_pullup', 62.50, -5.90, 'z=1.333'),  # Clark and Kat bracing at the hole, hauling on Bobby and the rope
  ('but something pulls harder', 's3_joblo_pullup', 57.90, -2.90, 'z=1.333'),  # the rope yanks Bobby off his feet, Kat clinging to him
  ('dragging the bed', 's3_joblo_pullup', 83.60, -1.60, 'z=1.333'),  # Clark and Kat at the hole, then the bed-mounted camera lurches toward it
  ('just in time to see bobby', 's3_joblo_pullup', 93.40, -3.60, 'z=1.333'),  # from the floor: Bobby's legs dragged through the far door
  ('leaving a long trail of blood', 's3_joblo_pullup', 98.90, -4.10, 'z=1.333'),  # the red smear across the laundry-room floor (no body)
  ("you're down to forty", 's3_joblo_pullup', 74.50, -4.00, 'z=1.333'),  # Kat and Clark on their knees at the hole, staring down
  ('rule three', 's3_laundry', 40.20, -6.50, 'z=1.333'),  # POV going down the steep ramp into the dark
  ('and if your clothes got there', 's3_laundry', 139.20, -2.80, 'z=1.333'),  # the T-shirt again, close
  ], inserts=[ins('so what do you do', 0.9, 'choice', q='so what do you do'),
              ins('standing in the dark', 1.65, 'film', shots=[(0, 's3_joblo_pullup', 46.11, 1.0, T4 + ',lufs=-17')], sub="There's someone down there.")]))
# ---------------------------------------------------------------- s05 THE STILL LIFES (44.1 s) ----------------------------------
X.append(sec('s05', [
  (0, 's4_chase', 17.80, -3.40, 'z=1.333'),  # handheld POV running through the junk-filled rooms
  ('and lose each other', 's4_chase', 44.20, -7.00, 'z=1.333'),  # empty yellow rooms, nobody there
  ('while something heavy thuds', 's4_tree_a', 47.60, -4.10, 'z=1.333,g=1.25'),  # dim cluttered level, slow creeping POV
  ('room after room', 's4_tree_a', 75.50, -5.50, 'z=1.333'),  # running: the room of sofas, then hall after hall
  ('until you stumble into a dark room', 's4_tree_b', 10.60, -2.60, 'z=1.333'),  # a hand opens a white door into blackness
  ('lit only by a glowing christmas tree', 's4_tree_b', 22.50, -8.00, 'z=1.333'),  # the lone lit Christmas tree in the dark room, slow approach
  ('with people fused into the floor', 's4_tree_b', 37.80, -2.40, 'z=1.333,g=1.25'),  # a person sunk into the carpet, arms out
  ('a half-man in a wheelchair', 's4_tree_b', 63.30, -3.10, 'z=1.333'),  # the lamp clicks on beside the half man in the wheelchair
  ('and a red-haired woman', 's4_tree_b', 66.40, -2.40, 'z=1.333'),  # the red-haired still life steps out of the dark behind the lamp
  ('because the backrooms copies people too', 's4_tree_a', 143.00, -3.80, 'z=1.333,g=1.4'),  # still-life silhouettes standing beside the tree
  ('and fans call these copies', 's4_tree_b', 34.65, -2.90, 'z=1.333,g=1.25'),  # a still life half sunk into the carpet by the tree
  ('two of them chase you', 's4_chase', 121.20, -3.90, 'z=1.333'),  # running down dim halls into a green-lit corridor to a door
  ('and then you hear knocking', 's3_joblo_pullup', 307.50, -4.00, 'z=1.333'),  # Clark's camera entering the lit pool room
  ("it's kat", 's3_kids_enter', 141.70, -3.50, 'z=1.333'),  # Kat's frightened face looking up (yellow rooms)
  ('and from her side', 's3_joblo_pullup', 337.20, -7.00, 'z=1.333'),  # across the pool room: Clark small at the far wall
  ('but from yours', 's3_joblo_pullup', 359.80, -8.80, 'z=1.333'),  # Clark with his palm flat on the plain wall
  ('you set the camera down', 's3_joblo_pullup', 318.40, -12.20, 'z=1.333'),  # the camera settles on the floor facing the empty pool room
  ('and something much taller', 's3_joblo_pullup', 368.60, -6.00, 'z=1.333,g=1.25'),  # a dark shape crosses the lens and the camera is lifted (ends before Kat's line)
  ("you're down to fifteen", 's3_kids_enter', 146.60, -6.40, 'z=1.333'),  # Kat terrified, close
  ('rule four', 's4_tree_a', 61.40, -1.50, 'z=1.333,g=1.25'),  # a dark level, one lit doorway
  ('and nothing in here that looks', 's4_tree_a', 147.00, -4.00, 'z=1.333,g=1.4'),  # still-life silhouettes by the tree, people that aren't
  ], inserts=[ins('picks it up', 1.47, 'film', shots=[(0, 's3_joblo_pullup', 379.91, 1.0, T4 + ',lufs=-17')], sub='Clark, behind you!')]))
# ---------------------------------------------------------------- s06 AFTER HIM (62.4 s) ----------------------------------------
X.append(sec('s06', [
  (0, 's3_joblo_pullup', 331.00, -5.00, 'z=1.333'),  # from the set-down camera: Clark walks away across the pool room, his last shot as himself
  ("so from here on you're mary", 's5_mary_enters', 54.20, -3.50, 'g=1.25'),  # Mary close in the flickering basement
  ('the house you grew up in', 's6_home', 0.00, -3.80, 'z=1.06'),  # the cluttered family living room (top level of the copies)
  ('your mother ended up', 's5_mary_b', 76.00, -4.40),  # Mary, troubled close (no mother in my clips)
  ('and you still keep the chunk', 's5_mary_b', 46.50, -4.50),  # Mary looking at her own hands (no concrete in my clips)
  ('then clark leaves a message', 's5_mary_enters', 67.40, -4.20),  # Clark talking in the therapy flashback (no phone)
  ('you go after him', 's5_mary_enters', 18.20, -3.20),  # Mary going down the stairs into Clark's basement
  ('with no rope', 's5_mary_enters', 36.40, -3.20, 'g=1.25'),  # Mary alone, empty-handed, in the dim basement
  ('his store is unlocked', 's5_mary_enters', 7.00, -2.00),  # Mary at the top of the shop's basement stairs (no door shot)
  ('days of mail', 's5_mary_enters', 26.30, -2.00, 'g=1.25'),  # wide of the shop basement, her silhouette on the stairs (no mail)
  ('and his map is on a whiteboard', 's5_mary_enters', 58.00, -2.60),  # the whiteboard map, over Mary's shoulder
  ('and when a fly buzzes', 's5_mary_enters', 97.80, -3.50),  # the wall with the tape outline, the fly specks on it
  ('you follow it', 's5_mary_enters', 110.30, -1.50),  # Mary's hand reaching into the wall
  ('inside a camera has been torn', 's5_mary_enters', 164.10, -2.70),  # Mary inside the yellow room, wide (no camera)
  ('chairs are piled', 's5_mary_enters', 169.90, -2.30),  # Mary close, staring, yellow room (no chairs)
  ('and someone has drawn a giant pirate', 'd_mary_meets', 12.20, -6.50),  # v2: the mural: a giant pirate drawn on the wall behind Mary
  ('lifting a tiny yellow figure', 'd_mary_meets', 7.00, -1.95),  # v2: over Mary's shoulder, the pirate drawing holding up a small figure
  ('clark steps out of hiding', 'd_mary_meets', 51.20, -7.50),  # v2: Clark appears at the far end of the yellow hall
  ("says you're too loud", 'd_mary_meets', 85.30, -1.70),  # v2: Clark steps in beside Mary at the mural, hushing her
  ('and tells you this is every place', 'd_mary_meets', 87.60, -6.00),  # v2: Clark talking to Mary in front of the mural
  ('then something growls', 's5_mary_b', 100.50, -2.00),  # Mary turns to look behind her in the yellow room
  ('the lights flicker', 's5_mary_enters', 9.00, -3.00),  # stairwell lit, then dark (flicker)
  ('the sound stops', 's5_mary_enters', 82.20, -2.20, 'g=1.25'),  # NEW CUT  wind chimes hanging in the dark basement
  ('the lights go out', 's5_mary_enters', 14.85, -0.90),  # stairwell dark, Mary barely visible
  ('and clark chokes you', 'd_mary_meets', 115.00, -1.85),  # v2: wide, Clark grabs Mary from behind (short)
  ('chokes you', 'd_mary_meets', 117.05, -2.40),  # v2 NEW CUT: close, the choke, her face (kept short)
  ("telling you it's for your own good", 'd_mary_meets', 127.90, -2.10),  # v2: her view of the ceiling light as she goes under
  ("you're down to ten", 's7_joblo_reveal', 109.50, -2.00),  # Mary close, worn out
  ('rule five', 's7_joblo_reveal', 123.00, -2.60),  # Clark's face, close
  ('might be the most dangerous', 's7_joblo_reveal', 192.00, -3.00),  # Clark with the knife, standing over Mary tied to her chair
  ], inserts=[ins('so what do you do', 0.9, 'choice', q='so what do you do')]))
# ---------------------------------------------------------------- s07 YOUR OLD HOME (26.8 s) ------------------------------------
X.append(sec('s07', [
  (0, 'd_mary_meets', 130.20, -2.30),  # v2: the ceiling light blooming to white: Mary out cold
  ('you dream of your mother', 's5_mary_b', 72.00, -3.00),  # Mary in profile, looking down (no mother in my clips)
  ('and of the house', 's6_home', 6.40, -3.00, 'z=1.06'),  # the cluttered home, camera sinking toward the carpet
  ('and the backrooms builds it', 's6_home', 13.00, -3.60, 'z=1.06'),  # level 2: same room, sparser, sun through the window
  ('then another below it', 's6_home', 27.30, -2.10, 'z=1.06'),  # level 3: half-empty room, the window boarded
  ('each one more wrong', 's6_home', 34.80, -2.80, 'z=1.06'),  # level 4: bare walls, a few scraps on the floor
  ('until the bottom one', 's6_home', 50.60, -2.80, 'z=1.06'),  # blank box, one ceiling light
  ('because as clark puts it', 's7_eat_them', 16.20, -3.00, 'z=1.45'),  # Clark at the arch, explaining with his hands
  ('the more times this place', 's6_home', 19.00, -5.00, 'z=1.06'),  # level 2 later moment, camera sinking (copies of copies)
  ("you're down to seven", 's6_home', 40.60, -3.60, 'z=1.06'),  # an empty copied room (no Mary in s6_home)
  ('and rule six', 's6_home', 46.00, -3.40, 'z=1.06'),  # empty room with tape outlines on the floor
  ("you're already too deep", 's6_home', 59.20, -5.60, 'z=1.06'),  # the deepest copy: bare room, one dark arched doorway
  ]))
# ---------------------------------------------------------------- s08 THE DINING ROOM (61.4 s) ----------------------------------
X.append(sec('s08', [
  (0, 's7_joblo_reveal', 57.20, -3.20),  # Mary tied to the chair at the table, wide, straps on her wrists
  ('where the guests are still lifes', 's7_eat_them', 64.80, -2.60, 'z=1.45'),  # the table: bearded still life seated, Clark coming
  ('and clark loves them', 's7_eat_them', 99.40, -1.80, 'z=1.45'),  # Clark close, smiling
  ("because they can't feel anything", 's7_eat_them', 26.10, -2.60, 'z=1.45'),  # the bearded still life's blank, misshapen face
  ('he pushes a knife', 's7_eat_them', 71.05, -1.50, 'z=1.45'),  # Clark's hand puts the knife to its neck; the face stays blank
  ("and it doesn't even blink", 's7_eat_them', 76.20, -2.40, 'z=1.45'),  # the still life sits unmoved, Clark beside it
  ('they simply exist', 's7_eat_them', 96.40, -2.30, 'z=1.45'),  # Clark close (shot over "like furniture")
  ('like furniture', 's7_joblo_reveal', 186.20, -2.80),  # the table of still lifes through the arch, Clark among them
  ('and the best part', 's7_eat_them', 108.20, -4.20, 'z=1.45'),  # Clark grinning beside the guest ("you can eat them")
  ('so he scoops out white stuffing', 's7_eat_them', 115.85, -3.50, 'z=1.45'),  # white stuffing pulled out over a plate
  ('and serves it', 's7_eat_them', 132.00, -2.40, 'z=1.45'),  # NEW CUT  Clark's arm puts stuffing on Mary's plate
  ("kat's head is in his fridge", 's7_eat_them', 143.50, -1.85, 'z=1.45'),  # Clark walks to the CLOSED fridge (head never shown)
  ('and all he says', 's7_joblo_reveal', 146.50, -3.00),  # Clark, calm, close
  ('then he makes you play his wife', 's7_stay_char', 0.00, -3.60),  # Mary in the red wig at the table, wide
  ('to relive the night', 's7_stay_char', 7.00, -3.50),  # Clark directing her ("I pay for everything")
  ("and when you say you're not", 's7_stay_char', 16.60, -3.00),  # Mary in the red wig, close
  ('so you tell him the truth', 's7_joblo_reveal', 50.10, -2.40),  # Mary speaking ("the real reason ... wasn't the drinking")
  ('that it was never the drinking', 's7_joblo_reveal', 69.40, -3.00),  # Mary, mid-speech
  ('and nothing is ever his fault', 's7_joblo_reveal', 76.60, -2.50),  # Clark taking it, medium
  ("he says he doesn't want", 's7_joblo_reveal', 139.60, -3.50),  # Clark close ("I like it in here" 141.3-142.5)
  ("right where he's supposed to be", 's7_joblo_reveal', 153.70, -1.70),  # Clark close (says it at 154.6-155.7)
  ('so you tell him to stay', 's7_joblo_reveal', 159.60, -3.00),  # Mary ("Then, stay." 159.9-161.3)
  ('and he starts to untie you', 's7_joblo_reveal', 200.30, -3.40),  # Clark at her strapped wrist, freeing it
  ("you're down to five", 's7_joblo_reveal', 189.50, -1.90),  # Mary close, low angle
  ('at a dinner party', 's7_joblo_reveal', 212.60, -5.80),  # the dining room through the arch: Clark, Mary, the guests
  ('who keeps a head', 's7_eat_them', 62.30, -2.00, 'z=1.45'),  # NEW CUT  the table and the closed white fridge, Clark at the arch
  ('rule seven', 's7_eat_them', 137.00, -3.50, 'z=1.45'),  # Clark leaning over the table, grinning, serving
  ("you're never leaving", 's7_joblo_reveal', 223.20, -1.80),  # Mary at the table, looking toward the arch
  ('and then the red-haired woman', 's7_joblo_reveal', 204.0, -2.6),  # SET (kept)
  ('panics and runs', 's7_joblo_reveal', 206.4, -1.15),  # SET (kept)
  ], inserts=[ins('he snaps', 2.9, 'film', shots=[(0, 's7_stay_char', 43.55, 1.0, 'lufs=-17')], sub='Stay in character! Stay in character!'),
              ins('END', 0.85, 'hum', shots=[(0, 's7_joblo_reveal', 219.5, 1.0, 'a=-24')])]))   # the empty dark arch (3:39-3:49), room tone
# ---------------------------------------------------------------- s09 CAPTAIN CLARK (66.0 s) ------------------------------------
X.append(sec('s09', [
  (0, 's7_joblo_reveal', 230.4, -5.4),  # SET (kept) Captain Clark through the arch
  ('a copy of clark', 's7_joblo_reveal', 247.30, -3.30),  # Captain Clark full figure in the room (4:07), after the shortened 'This is Mary.' line
  ('towering and stretched', 's8_pack_a', 69.85, -1.65),  # Captain Clark's tall stretched silhouette on the lit hallway wall (= jf 99.3)
  ('dressed as the pirate', 's8_pack_b', 90.62, -1.00),  # Captain Clark in full costume (tricorn, coat) walking up behind Mary in the store
  ('from his own tv commercial', 's1_commercial', 23.50, -3.00),  # wide: Cap'n Clark at the helm in the store ad
  ('peg leg and all', 's8_pack_b', 91.66, -1.00),  # same shot, later: full body, the wooden peg leg visible
  ('this is captain clark', 's8_pack_b', 94.62, -0.93),  # Captain Clark wide, bright, face + hat + costume (= jf ~292)
  ('captain clark', 's8_pack_b', 106.15, -0.95),  # NEW CUT: his face under the tricorn, close (Mary's hand at his face, from the fight)
  ('and clark tries to calm it', 's7_joblo_reveal', 260.60, -2.20),  # Clark at the table, talking up at it
  ('introducing you like a dinner guest', 's7_joblo_reveal', 241.60, -3.20),  # Clark turns from it toward Mary
  ('he tells it', 's7_joblo_reveal', 255.40, -2.40),  # Clark by the table looking up ("No, no, you don't have to worry")
  ('and that you said', 's7_joblo_reveal', 251.30, -3.00),  # Mary frozen, close
  ("because it's just the way", 's7_joblo_reveal', 265.70, -2.90),  # Captain Clark's silhouette looming over Clark
  ("and that's when captain clark", 's7_joblo_reveal', 281.60, -1.75),  # it bends over Clark from behind, before the grab
  ('and bites into him', 's7_joblo_reveal', 293.70, -2.20),  # Mary screaming
  ('you tear free and run', 's8_joblo_fight', 0.20, -3.50),  # Mary bursts out of the house door into the fake street
  ('and it hobbles after you', 's8_chase_b', 23.95, -2.40),  # wide fake street, Captain Clark small and far, coming down the middle
  ('through a street of fake apartments', 's8_chase_a', 115.80, -2.10),  # Mary running down the street between the fake houses under the office ceiling (= jf 7.48)
  ('a room full of couches', 's8_chase_e', 195.05, -1.50),  # Mary climbing through the room piled with striped couches (= jf 62.98)
  ('and a hall with a locked door', 's8_chase_e', 153.75, -2.10),  # Mary shoving at the locked white door at the end of the street, turns back (= jf 21.68)
  ('so you crawl through a doggy door', 's8_chase_e', 234.15, -2.60),  # Mary crawling out through the doggy door onto the ledge (= jf 102.5)
  ('into the biggest space', 's8_joblo_fight', 111.35, -2.35),  # the Escher space: walls of shelving, Mary's hand on the ledge
  ('endless floors around a giant drop', 's8_joblo_fight', 114.90, -2.85),  # wide, tilting down into the giant drop
  ('with a staircase floating', 's8_joblo_fight', 141.20, -3.05),  # Mary on the floating staircase above the drop
  ('another door brings you up', 's8_joblo_fight', 173.85, -3.90),  # Mary climbing up out of the hatch in the floor
  ("of clark's store", 's8_joblo_fight', 202.45, -1.50),  # the copied store, wide
  ("except it's the copy", 's8_joblo_fight', 212.00, -2.40),  # Mary in the store, a blank white cut-out figure beside her
  ('ringed with gas canisters', 's8_joblo_fight', 205.40, -2.00),  # blue gas canisters standing in the aisles
  ('and its door opens onto a wall', 's8_joblo_fight', 229.30, -2.60),  # Mary pushing at the glass front door, yellow wall behind the glass
  ('with nowhere left to run', 's8_joblo_fight', 245.45, -1.80),  # Mary at the glass, frightened (4:05-4:07)
  ('you snap its peg leg', 's8_joblo_fight', 289.80, -0.68),  # Mary readies the hat rack
  ('its peg leg with', 's8_joblo_fight', 290.53, -0.50),  # NEW CUT: the swing, the peg leg in the foreground
  ('a hat rack', 's8_joblo_fight', 291.10, -0.74),  # NEW CUT: the peg leg snaps, close (cut on the hit)
  ('knock over a cutout', 's8_joblo_fight', 293.15, -1.08),  # Mary flails and crashes into the display
  ('cutout that sets', 's8_joblo_fight', 296.25, -1.25),  # NEW CUT: the fallen cutout's board, the igniter sparks
  ('the gas hissing', 's8_joblo_fight', 300.90, -0.80),  # NEW CUT: a blue canister hissing gas
  ("and when it's right on top of you", 's8_pack_b', 100.62, -0.55),  # Captain Clark crawling at her through the gas, face and hat bright
  ('on top of you', 's8_joblo_fight', 347.66, -0.95),  # NEW CUT: Captain Clark crawling over Mary
  ('you smash its face', 's8_joblo_fight', 368.52, -1.00),  # Mary on the floor, raising the concrete
  ('face with your', 's8_joblo_fight', 369.74, -0.52, 'g=1.25'),  # NEW CUT: Mary, concrete raised (dim)
  ('concrete handprint', 's8_joblo_fight', 370.33, -0.44),  # NEW CUT: the swing, concrete in her hand
  ('handprint until', 's8_joblo_fight', 370.82, -0.50),  # NEW CUT: the hit, his head snaps, fragments fly (cut on the hit)
  ('until the concrete breaks', 's8_joblo_fight', 371.40, -0.55),  # concrete fragments falling to the floor
  ('concrete breaks', 's8_joblo_fight', 372.90, -1.15),  # NEW CUT: Mary on the floor, gasping
  ("you're down to two", 's8_joblo_fight', 374.10, -1.85),  # Mary, spent, crawling away
  ('and rule eight is the simplest', 's8_joblo_fight', 322.20, -3.00),  # Mary crawling in the gas fog
  ("when you can't run", 's8_joblo_fight', 314.85, -2.25),  # Mary's face, gas spraying behind her (smoky store)
  ], inserts=[ins(0, 0.4, 'thud', shots=[(0, 's7_joblo_reveal', 229.9, 1.0, 'a=-16')]),   # the first heavy step at the arch
              ins('dinner guest', 1.2, 'film', shots=[(0, 's7_joblo_reveal', 244.97, 1.0, 'lufs=-17')], sub='This is Mary.')]))  # ~4:05, verify words and times
# ---------------------------------------------------------------- s10 ASYNC (58.0 s) --------------------------------------------
X.append(sec('s10', [
  (0, 's8_joblo_fight', 423.62, -2.90),  # hazmat men (yellow, green suits) walking through the gas past the mural (7:04)
  ('and more gas knocks you out', 'end_extract', 20.75, -2.60),  # a hazmat man sprays Mary, she drops into the gas
  ('you wake up at async', 'end_extract', 55.35, -6.90),  # Mary on all fours in the blue Async room, hazmat men behind
  ('where they scan your body', 'end_extract', 74.50, -7.40),  # scientists in white coats + hazmat men walk in through the blue light (no scan exists)
  ('and down the hall captain clark', 's8_pack_b', 126.00, -2.70),  # the Async lab: a body on a table, the pirate hat on the lower table, head scans on a monitor
  ('his pirate hat part of his own body', 's8_joblo_fight', 350.35, -2.80),  # Captain Clark's tricorn filling the frame from above (store fight)
  ('and behind another door', 'end_joblo_phil', 9.00, -4.80),  # Async double doors at the end of the corridor
  ('is a room full of cardboard cavemen', 's8_joblo_fight', 208.45, -3.00),  # cardboard caveman cutouts standing in the copied store
  ('so that hello and welcome', 'x_a24_trailer', 25.35, -4.70),  # Clark's first trip: crouched, then walking into the empty yellow rooms (no text)
  ('came from async all along', 'end_joblo_phil', 4.45, -3.90),  # the white Async corridor, staff leading Mary
  ('phil the man who watched', 'end_joblo_phil', 186.00, -3.00),  # Phil at the desk, talking (3:06-3:09)
  ('tells you his company', 'end_joblo_phil', 198.00, -2.70),  # Phil, closer, talking
  ('until it found this place', 'end_joblo_phil', 205.90, -2.00),  # Mary listening
  ('that he goes in every day', 'end_joblo_phil', 209.60, -2.40),  # Phil
  ('and that doors are opening everywhere', 'end_joblo_phil', 224.00, -4.30),  # Phil talking (3:44-3:48)
  ("so you ask if they'll let you go", 'end_joblo_phil', 232.70, -2.30),  # Mary asking (3:53)
  ('and inside the backrooms', 'end_joblo_phil', 300.10, -4.50),  # her house's rubble heaped in a yellow Backrooms room under a street lamp
  ('your house', 'end_mary_still', 63.45, -3.80, 'g=1.25'),  # the copied living room of Mary's house, lamp lit
  ('a bookstore with your book', 'end_mary_still', 78.05, -4.15),  # the bookstore with her book's display stand
  ('missing posters for kat', 'end_joblo_phil', 329.55, -4.00),  # MISSING poster, Kathrine Taylor and Robert Franklin
  ('the strip mall', 'end_mary_still', 100.10, -4.60, 'g=1.25'),  # the strip-mall exterior at night, Clark's store with its pirate sign
  ('and finally a copy of the room', 'end_mary_still', 105.60, -4.70, 'g=1.25'),  # the copied interrogation room, wide, a figure sitting by the windows
  ('with a copy of you', 'end_mary_still', 110.45, -4.90, 'g=1.25'),  # Mary's still life sitting perfectly still, hands in her lap
  ('five people walked in', 's1_joblo_first', 328.70, -1.90),  # empty yellow room, curved wall
  ('one walked out', 'end_joblo_phil', 162.20, -5.20),  # Mary alone at the table, wide, the blue/orange room
  ('and even she never got', 'end_joblo_phil', 266.00, -2.60),  # Mary close in the room (long take, far from the 241 insert)
  ('one out of five', 's1_joblo_first', 164.00, -2.00),  # wide empty yellow room, a hole in the floor
  ], inserts=[ins("let you go", 2.19, 'film', shots=[(0, 'end_joblo_phil', 241.37, 1.0, 'lufs=-17')], sub="That decision's not up to me.")],  # ~4:01, verify
  pad=0.9))
# ---------------------------------------------------------------- s11 outro (35.5 s) --------------------------------------------
X.append(sec('s11', [
  (0, 'op_joblo_1990', 12.60, -2.50, 'z=1.333'),  # the tape again: wall + empty yellow room
  ('naren died on june', 'op_joblo_1990', 16.90, -2.30, 'z=1.333'),  # Naren's yellow sleeve grabbing past his black bag
  ('and clark found the door', 's1_a24_clip', 44.00, -2.60, 'g=1.25'),  # Clark at the glowing wall
  ('ten days later', 's1_a24_clip', 72.00, -2.00),  # Clark crawling into the yellow room
  ('the movie never says it', 'op_joblo_1990', 281.00, -2.50, 'z=1.333'),  # lit doorway far down the corridor
  ('but the only giant', 'op_joblo_1990', 296.40, -0.90, 'z=1.333'),  # empty yellow corridor, a door at its far end
  ('giant', 'op_joblo_1990', 312.41, -0.47, 'z=1.333'),  # NEW CUT: the dark blurred figure fills the frame, camera drops
  ('it ever shows you', 'op_joblo_1990', 283.60, -1.90, 'z=1.333'),  # NEW CUT: the doorway down the corridor again
  ('is captain clark', 's7_joblo_reveal', 283.62, -1.50),  # Captain Clark's face and pirate hat, close
  ('so the backrooms had already made', 's8_pack_a', 146.60, -3.05, 'g=1.25'),  # Captain Clark looming in the lit gap, reaching (= pack_b 122.35)
  ('before he ever walked in', 's1_a24_clip', 83.50, -2.40),  # Clark getting up and walking in for the first time
  ("it doesn't wait for you", 's1_a24_clip', 14.50, -1.50, 'g=1.75'),  # the slit glowing
  ("because it's already started on you", 's1_joblo_first', 155.60, -2.60, 'g=1.25'),  # dim empty rooms, slow move
  ('so how long would you have lasted', 's1_joblo_first', 246.30, -2.90),  # Clark walking into an empty yellow room
  ('and which stage', 's8_chase_a', 127.55, -2.25),  # Mary running down the long fake street toward the far door (= jf 19.23)
  ('tell me in the comments', 's1_a24_clip', 86.00, -3.95),  # calm wide yellow room, Clark from behind
  ('subscribe so you', 's1_first_a', 103.00, -1.70),  # calm wide yellow room, the throne far off
  ('and if you ever see a line of light', 's1_a24_clip', 47.00, -3.20, 'g=1.25'),  # Clark at the glowing wall at night
  ('leave it alone', 's1_a24_clip', 16.05, -1.55, 'g=1.75'),  # the slit, hold to the end
  ], extra=[('date', ['JUNE 19, 1990'], 'june nineteenth', 'and clark found'),
            ('date', ['JUNE 29, 1990'], 'june twenty-ninth', 'ten days later'),
            ('date', ['JUNE 29, 1990', '!10 DAYS LATER'], 'ten days later', 'the movie never says'),
            ('png', '../ep04/tiles/subscribe.png', 'subscribe so you', 'and if you ever')],
  pad=2.0))
