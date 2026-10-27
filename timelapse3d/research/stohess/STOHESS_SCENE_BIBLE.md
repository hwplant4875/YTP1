# PART 3: Stohess (S1 ep23-25), scene bible (short)

**Sources:** contact sheets `sheets/ep23..25_NN.jpg` (6x5, 8 s per cell; cell i of sheet k = (k-1)*240 + 8*i s), finer
`sheets/ep25_wall_1520.jpg` (4 s/cell from 15:20) and `ep25_end_2030.jpg`. Frames local only (gitignored). Lead analysis 10/27.

**Pace:** same as the forest: fast sky drone, short beats, far framing, brief push-ins. One take that continues from f3
(the retreat's wide sky end looking SW). Target ~70 s of video, two segments (s1 0-30, s2 30-70).

## A. Beats (video seconds)

| # | Beat | Anime ref | t | M/O |
|---|---|---|---|---|
| s1a | From the retreat's sky end: time-lapse (a month: dusk, night, dawn) flying SW over Wall Rose to Wall Sina; Stohess reveal in morning light (classical stone facades, slate roofs, domed church, canals) | ep23 OP-end, ep24 12:00 town shots | 0-9 | M |
| s1b | The escort carriage procession down the main avenue (Eren decoy); Armin, Mikasa, Eren with Annie walk to the underground stairway | ep24 ~2:00-9:00 | 9-14 | M |
| s1c | Annie stops at the stairs and refuses; she bites her ring: light beam in the street; the Female rises, smashing houses; Eren stuck underground | ep24 9:30-12:30 | 14-20 | M |
| s1d | Hange's Plan C on the rooftops: the harpoon / net volley pins her briefly; she tears free and rampages through the streets (civilians flee, MPs gape) | ep24 19:00-20:00 | 20-30 | M |
| s2a | Lightning under the street: Eren's titan bursts up through the paving and tackles her | ep24 21:00, ep25 3:00 | 30-36 | M |
| s2b | Brawl through Stohess: punches, her kick, they crash through the church; berserk Eren pins her, bites | ep25 4:00-9:00 | 36-48 | M |
| s2c | She runs for the district wall and CLIMBS Wall Sina on hardened finger holds; near the top Mikasa cuts her fingers | ep25 9:00-13:00 | 48-56 | M |
| s2d | She falls; Eren catches her at the wall foot and rips her out of the nape; Annie encases herself in crystal; steam | ep25 13:00-15:40 | 56-62 | M |
| s2e | END: the camera rises up the wall face to where her fingers broke it: a TITAN FACE inside the wall, one eye looking out; Hange and Pastor Nick on the wall top; hold | ep25 final scene | 62-70 | M |

Lore: Annie climbs the wall from INSIDE Stohess (to escape out of Sina); Mikasa severs her fingers near the top; the crystal
is at the wall foot; the wall titan is revealed in the broken wall surface high up (Pastor Nick: "keep the sunlight off it").

## B. Map (world.py frame W; local frame S: origin = Sina EAST district centre on the ring, W (12500, 24000); +x outward/east, +y north)

- District bulge (world.py `_district`, Sina W 420 / S 300 / R 420): straight walls y = +-420 from x 0 to 300, arc centre
  (300, 0) r 420, outer gate at the tip (720, 0). The town fills the bulge and continues ~350 m inside the ring (x < 0).
- Main avenue along y = 0 (x -350..700). Canal N-S at x = 200 with three arched bridges; square with a statue at (-40, -60);
  domed church at (80, -170) with a bell tower; MP headquarters block at (-200, -120).
- Underground stairway at (-150, 60) (Annie's refusal / the shift point). Eren's titan bursts up at (-60, 40).
- Brawl path: (-60, 40) -> (100, 0) -> church (80, -170) -> (330, -150) -> climb point on the bulge arc at -30 deg:
  (664, -210), inner face normal pointing back to (300, 0). Crystal at the wall foot (648, -200). Wall titan face in the
  wall at the climb line, z ~ 40 m (wall top 50 m).

## C. Camera

- s1a: high (1.5-2 km) fast drone SW, the rings below; descend to a 400 m oblique over Stohess.
- s1b-c: 150-250 m oblique over the avenue; push-in to ~60 m at the stairway for the beam.
- s1d: high oblique 200 m tracking her through the roofs (the Plan C rooftops in frame).
- s2a-b: 120-200 m orbit around the two titans; push-in for the tackle and the bite.
- s2c-d: side view of the wall from the town, 250 m back, rising with her; push-in for the finger cut and the fall.
- s2e: crane up the wall face from the crystal to the face (lens 35 -> 45), end hold (slight drift).

## D. Assets

Reuse: forest kit (common.py Batch people / titans, Female, Eren, Wires, LightRig), fset.house_variants (paler stone
variants), world.py walls. New (aot/stohess/sset.py): Stohess blocks, canal + bridges, church dome + tower, statue,
stairway, rooftop launcher racks, the wall-titan face patch (hole + face, eye) built into the bulge's inner face.
