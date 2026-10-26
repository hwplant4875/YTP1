# g5_trost_breach_evac: Trost 850, from the Colossal's return to the Attack Titan's first kills

Owner rules (BRIEF.md, HANDOFF 09:37 (10/25) and later) win over the anime. Tags: `[EV]` = I opened the frame myself; `[LOG]` = from the Sonnet logs, not re-checked; `[INF]` = my inference; `[CANON]` = series canon from **ep05, which we do not have** (no frames exist for the kick itself, the Colossal's vanish, the defence-line briefing or Eren being swallowed). Treat `[CANON]` items as lore that is right but unverified against our frames.
Frame aliases: `F04` = /tmp/claude-0/aot/anime/frames/ep04/, and likewise F06, F07 and F09. Coordinates use g4's **MASTER frame M** (metres; origin = outer-gate centre at ground level; +X east, +Y north into the city, +Z up). Conversions: trost.py set = (X, Y - 870); world.py = (X, Y + 4130).
Beat-local time `t` (seconds) starts at **t = 0 = g4's handoff (g4 t = 20.0)**: the lightning flash, with the Colossal's skull rising over the gatehouse. Mapping to trost_action.py BEATS: our 0-31 s covers "flood", 31-61 s covers "evacuation", and 59-84.0 s covers "mikasa_falls" plus "attack_titan" (the alley fight, then the second fight in square Q2) up to the walk toward the HQ. The take was 78.5 s before the section 11 review; the 5.5 s added hold the Attack Titan's second fight, which the anime shows and the old spec mis-read as him walking off. The "hq_despair" and "bell_tower" windows are replaced (see section 8).

---------------------------------------------------------------------------------------------------------------------

## 1. Lore summary of the beats, in order, with evidence

1. **Lightning, then the Colossal's head above the outer gate.** It is late morning with a clear sky and big cumulus. A yellow-gold bolt strikes, with several frames alternating full yellow and black. Then the skinless red skull appears right at the outer edge of the wall top. Its chin is level with the wall-top cannon and only head and shoulder-tops show above the coping. Thick white steam and floating orange embers surround it. `[EV]` ep04 20:42.7 F04/000029794 (yellow flash), 20:43.0 F04/000029803 (bolt), 20:44.8 F04/000029845 (face beside the cannon and a tiled wall-top hut, green plain behind), ep07 01:10.4 F07/000001688 (recap, same framing, caption "Year 850").
2. **The kick.** The town-side gatehouse is intact a moment before: brick, a stone cornice, 2 arched strap doors and the crest plaque. A sepia blast of planks and stone follows; the giant spiked slab barricades (tall plank boxes on small iron wheels) are rocked and rolled back by the blast wind, and debris rains over the gate square and the ring pit. Straight after the blast the slabs still stand (20:57.9 top-down); the toppled and leaning wrecks are the later state (item 5, F04/000031099, F07/000001960). The shock cloud sweeps the wall top and throws 4 soldiers into the air. `[EV]` ep04 20:55.6 F04/000030104, 20:56.2 F04/000030119, 20:56.5 F04/000030127, 20:57.9 F04/000030160 (top-down: slabs and stone blocks scattered on the grass, ring road and plank bridge), 20:59.8 F04/000030205 (cadets run along the brick wall top ahead of the cloud), 21:01.1 F04/000030236 (4 soldiers flung above the wall edge). The kick itself is `[CANON]` (ep05).
3. **The Colossal grips the wall top and sweeps it.** Seen from the inner face looking up (a south-looking shot, so left = east), the red fist lies on the wall top with its fingers curled over the INNER edge and the fingertips sunk into the inner face; cracks radiate across the inner face below them. The fist sits immediately right (west) of a vertical brick riser, and cadets' wires hang on the face to the left `[EV]` ep04 21:27.2 F04/000030862. Which hand it is cannot be read. A huge dark forearm then sweeps across the wall-top paving (large pinkish stone flags here) in tan dust and embers `[EV]` ep04 22:10.1 F04/000031890, 22:10.5 F04/000031900. The sweep wrecks the fixed cannons on that stretch `[CANON]`. One cadet (Eren) runs up the sweeping red forearm `[EV]` 22:14.0 F04/000031985 and flies at the steam-wrapped head and neck `[EV]` 22:18.0 F04/000032081. The Colossal vanishes in a burst of steam as he reaches the nape `[CANON]` (ep05).
4. **The breach, seen from inside.** Looking down the avenue, the gate slot glows white at its base and grey smoke pours out. Two slab barricades lean wrecked at the avenue mouth, stone chunks lie on the cobbles, the top of the Colossal's skull still shows over the wall, and smoke columns already rise beyond `[EV]` ep04 21:37.1 F04/000031099. Later state: a tall ragged hole through the 3-tier brick gatehouse, broken floor beams inside, a brick and stone rubble heap spilling out, daylight through the hole, and 2 jagged-rimmed craters in the grass in front, each with a twisting steam wisp `[EV]` ep04 23:55.8 F04/000034425. From outside: the rust-red iron gate frame is smashed below its transom, titans walk in, and grey smoke columns stand over the district `[EV]` ep09 07:59.5 F09/000011497.
5. **Titans pour in.** In the gate square just after the breach (high oblique aerial), about 10-13 titans of 3-10 m are spread loosely. They walk across the ring road and grass, one sits on the ring pit's middle ring, one lies face-down at the inner trench mouth, two crouch over something at the left, and one walks out between the houses. Slab barricades are toppled, crossed X-stakes and debris are strewn about, and orange embers float `[EV]` ep07 01:21.7 F07/000001960 (recap, caption "which allowed the Titans to invade", ep07 01:17.7 F07/000001864). Inside the town they stand among the roofs, sit and crouch, and dark blood stains mark the paving `[EV]` ep09 02:22.5 F09/000003417. By then smoke columns rise all over the district `[EV]` ep09 02:10.0 F09/000003117.
6. **Defence lines** `[CANON]`: the Garrison's vanguard engages near the gate; the 104th cadets plus Garrison squad leaders form the middle guard across mid-district; the Garrison elite rear guard covers the evacuation at the inner gate. The retreat signal is a bell `[CANON, manga ch.6; not verified]`. None of this is in our frames, apart from cadets on cannon duty and anchoring to the wall (ep04 21:06-21:57, sheet_29/30).
7. **The evacuation jam at the inner gate.** Seen from a high aerial: a solid crowd fills the forecourt in front of the inner gatehouse. The gatehouse is a stepped brick bastion with grey stone quoins and stone cornices: a taller central block carries the shield crest high above the round main arch, a narrow west wing has a narrow arched door, and a wider east wing has a second arched door with a timber leaf, nearly as tall as the main arch. A huge sack-load cart is jammed in the main arch. A giant pale Wall Rose pilaster flanks the bastion on EACH side. East of the east pilaster a grass slope with dark trees and shrubs runs along the wall foot above a paved terrace; west of the west pilaster is plain wall face with one dark tree at its foot (zoomed crop of F06/000008308). A street leaves the forecourt to the lower right (SE), with a few stragglers on it `[EV]` ep06 05:46.5 F06/000008308. The load is wedged in the arch, its bulging sacks overlapping BOTH jambs with the dark arch head 1.5-2 m clear above, and men push from behind on the tailboard ladder ("If you want to live, help push!") `[EV]` ep06 05:56.0 F06/000008536. The merchant and 3 of his men stand at the cart's rear, and the crowd keeps a 4-6 m gap from them `[EV]` ep06 06:26.1 F06/000009258. People press against the load with raised arms `[EV]` ep06 06:59.3 F06/000010052. Weather: dark overcast.
8. **An Abnormal charges the crowd.** A fat titan of about 12-13 m (measured: about 7.5x the height of the soldier at its feet) runs toward the gate down a straight street of 4-5 storey grey terraces with ground-floor arcades and a pale tower at the far end. A tan dust cloud as tall as the titan billows behind it. A soldier runs tiny at its feet, and the ODM soldiers chasing it shout "Damn, why is it ignoring us?!" `[EV]` ep06 06:52.9 F06/000009899, 07:06.3 (sheet_09).
9. **Mikasa kills it.** One pass at the nape `[EV]` ep06 07:16.9-07:21.4 (sheet_09). It pitches forward and skids prone in a dust cloud, and she stands on its back `[EV]` 07:29.0 F06/000010765. She looks down at the crowd from the corpse, with the cart in the arch beyond; the corpse has stopped right at the crowd's rear edge, people packed just below her `[EV]` 07:35.7 F06/000010927. She then walks the last stretch on foot through the crowd, which makes way, to the merchant `[EV]` 08:13.5 F06/000011831, 08:17.5 F06/000011927.
10. **"Move the wagon."** Mikasa faces the merchant at the cart, and a bodyguard is thrown aside `[EV]` 08:40.4 F06/000012476. Caption "Move the wagon." `[EV]` 08:58.0 F06/000012899. Men lean on the big spoked wheel beside the brick jamb `[EV]` 08:59.9 F06/000012944. **End state:** the cart stands beside the arch, east of it and a little south, in front of the east wing (the wing's arched timber door shows behind it, 09:09.6 F06/000013178). Its two dark horses face the arch, so the cart was heading north through the gate and has been backed out and swung aside. The crowd pours into the dark tunnel past it `[EV]` 09:03.9 F06/000013040. Mikasa is back on the steaming corpse ("Thanks, Sis!") `[EV]` 09:08.9 F06/000013160, and the corpse steams long afterwards in the street `[EV]` 09:41.2 F06/000013934.
11. **Rain, then broken overcast.** Rain starts right after the evacuation: the first drops darken the forecourt paving `[EV]` ep06 09:27.3 F06/000013602, 09:31.3 (sheet_11), and streaks fall over the steaming corpse `[EV]` 09:41.2 F06/000013934. It is heavy later in the present day `[EV]` ep06 22:04.7 (sheet_23, downpour), 22:05.2 F06/000031774 and 22:09.2 F06/000031870 (rain over the Trost skyline), and still falls on the rooftops before Mikasa's speech `[EV]` ep07 04:22.1 (sheet_07), 04:35.8 F07/000006613 (raindrops on Mikasa's hair, the HQ on a rise in the distance). By the 104th's charge it has stopped: heavy cumulus with blue gaps `[EV]` ep07 12:29.6 (sheet_15), dark cumulus over the arcaded street (12:52.1), sun shafts later (17:42.9, 19:52.5). (The forest rain in ep06 10:24.7, captioned "Year 844", is the flashback g4 meant.)
12. **Mikasa runs out of gas and falls.** After her rooftop speech she sets off alone and the whole surviving 104th follows her in a loose stream over the roofs toward the HQ, a dozen or more figures in the air at once `[EV]` ep07 11:21.1, 11:49.4 (sheet_14). She cuts down titans on the way in single passes `[EV]` 11:52.5-11:53.0 (sheet_14), 12:18.1-12:19.7 (sheet_15, a bald titan) and burns too much gas `[EV]` 12:07.2 (caption "Wait, she's expending too much gas", sheet_15). Armin sees her drop (12:37.3 "Mikasa!"); Connie tells Jean to lead the rest on (12:41.3), and Armin and Connie break off after her (12:42.9 "I'll stick with Armin", 12:44.8 "No, me too") `[EV]` sheets 15-16. The route runs along a straight arcaded street toward a tower, with the wall beyond `[EV]` 12:52.1 F07/000018512. Seen from far above, she lies tiny on the paler floor at the bottom of a deep dark street canyon `[EV]` 13:00.1 F07/000018704 (that it is a sunlit patch is `[INF]`; a light shaft does reach the alley wall beside her later, 16:24.3 F07/000023599). The canyon is a dead end: a broken masonry wall with a rubble heap, and the town rising beyond it `[EV]` 13:12.2 F07/000018995. Top-down view: about 5 broad stone steps lead up to a heap of angular dark boulders piled against the jagged broken wall, between 4-storey buildings `[EV]` 15:01.4 F07/000021613.
13. **Two titans approach.** First a stocky short-haired titan with a squinting grin (CAP) comes into the alley soon after she lands: a bare foot plants on the flagstones with the rubbled dead end in the background `[EV]` 13:28.3 F07/000019379; its grin rises above the alley wall `[EV]` 15:24.4 F07/000022164; it stoops and reaches for her while she kneels on the flagstones `[EV]` 15:15.2, 15:19.2, 15:32.2, 15:36.2 (sheet_18). Then a second, long-haired titan (LH, about 7 m `[INF]`) climbs in over the rubble heap, hands on its knees `[EV]` 16:16.1 F07/000023404, 16:37.3 F07/000023911 (she stands tiny in the foreground). She gets up and charges CAP, running in between its legs `[EV]` 17:15.8 F07/000024834.
14. **The Attack Titan arrives.** (Inside the belly of the titan that swallowed Eren, green lightning flashes `[EV]` ep07 16:49.6-16:50.3, sheet_19. The swallowing is a skipped close beat.) The 15 m Attack Titan charges in from the side with a straight right punch `[EV]` 17:23.0 F07/000025008. The punch hits CAP, the stocky short-haired titan that was reaching for her (its hair reads like a cap; same grin as 15:24.4); the Attack Titan leaps in from the side, fist first `[EV]` 17:24.6 F07/000025045, 17:25.3 F07/000025062. His momentum carries him and CAP together along the alley (his red-muscled legs in the air), and Mikasa is thrown `[EV]` 17:29.5 F07/000025164. She lies on the flagstones, then crouches on the steps holding her head, the rubble heap behind her `[EV]` 17:34.7, 17:50.3, 17:53.0 (sheet_21). The Attack Titan stands roaring in steam beside the pale alley wall (17:42.9, 17:43.9, sheet_21), then stomps a face-down titan again and again while Mikasa watches from the right, by a small rubble pile `[EV]` 18:03.2 F07/000025970, 18:11.6 F07/000026173. His eyes glow green in the roar and the stomps (17:59.6, 18:04.7, sheets 21-22). Which titan is stomped, and how LH dies, cannot be read from our frames `[INF]`.
15. **Afterwards: the rescue and the SECOND fight.** Mikasa stands alone in the alley looking up `[EV]` 18:42.3 F07/000026909; Armin flies in `[EV]` 18:38.9 (sheet_24), and he and Connie get her up onto a roof, kneeling beside her ("Mikasa, are you hurt?!") `[EV]` 18:52.2 F07/000027146. A second, crew-cut titan (CC) roars beside a gable near their roof `[EV]` 18:57.5 F07/000027273 and walks across a pale paved square right below them, its head at about the 4th floor of the terraces around it `[EV]` 18:59.0 F07/000027309. (The old spec read this figure as the Attack Titan walking off; it is crew-cut, not long-haired.) A titan corpse lies in a pool of dark blood, already evaporated to a steaming skeleton `[EV]` 19:05.7 F07/000027469. The Attack Titan comes for CC: he squares up with raised fists like a boxer `[EV]` 19:22.1 (sheet_25), lands blows `[EV]` 19:29.1 F07/000028030, 19:29.7-19:30.6, slams CC into a square stone tower whose top bursts in a tan cloud of dust and flying blocks `[EV]` 19:34.1 F07/000028151, grinds its face against the masonry (19:36.1), CC slides down steaming (19:41.9), and he stamps on the nape of the fallen titan `[EV]` 19:49.1 F07/000028511, 19:52.0 F07/000028580. The three cadets stand on a roof ridge watching, a wall across the horizon under a sun shaft `[EV]` 19:52.5 F07/000028592; "No, it's completely ignoring us" (20:03.0), and Armin hands Mikasa his gas (20:27.4-20:37.2, sheet_26). He then heads toward the HQ `[INF]` (handoff to the HQ group).

## 2. Layout and geography (MASTER frame M; top-down)

Everything not listed here (outline, wall, outer gatehouse, ring pit P, slabs, avenue AV, plaza C, HQ H, canal) is exactly as g4 gives it. Only additions and refinements follow.

### 2a. The outer-gate square at kick time (refines g4 2e)
- **Colossal stance:** feet at Y ≈ -18 to -28, body centred on X = 0 and facing north. Its chin sits at the wall-top level (Z ≈ 50-52) and the crown of its head at Z ≈ 60. Its face is 4-8 m outside the outer parapet `[EV]` F04/000029845 (the cannon is at mouth height).
- **Right-hand grip (side `[INF]`):** the fist on the wall top at X ≈ +22..+30, fingers curled over the INNER edge, fingertips sunk into the inner face at Z 44-50 `[EV]` F04/000030862. The crack decal goes on the inner face below the fingertips and spreads about 8 m. The frame shows the fist just west of a vertical brick riser but not which hand, so the side stays `[INF]`.
- **Arm-sweep path** `[EV partial]` F04/000031890, F04/000031900, `[CANON]`: the left forearm sweeps the wall top **westward** from X ≈ 0 to X ≈ -35 at Z 50-54, the Colossal leaning its chest on the outer parapet. True scale caps the reach: a 60 m titan's arm is about 27 m from shoulder to fingertip and the shoulder stands 10-15 m outside the wall, so one sweep covers at most 35-40 m of wall top (the old X -10..-130 needed a 120 m arm). What it hits (1-2 cannon sets, crates, the tiled hut) is flung west and off the inner edge, landing out to X ≈ -70. The west/east choice is `[INF]`.
- **Kick breach:** as in g4 2b: ragged, about 15 m wide at the ground (X -7.5..+7.5), up to Z 30-34. The iron gate leaf below the outside transom (Z 26) is smashed.
- **Kick debris field (new):**
  - Large masonry chunks (1-3 m, 20-30 pieces) land within r 20-90 m of O.
  - **2 of them make the 2 impact craters** at (±32, 20), 6-10 m across, as in g4. Their rims are jagged with radial splinters and spikes, not smooth bowls `[EV]` F04/000034425.
  - Medium chunks (0.4-1 m, about 80 pieces) reach r 150-220 m, up the first 150 m of AV and onto roofs around the square, each hit raising a small dust puff.
  - Planks and splinters (about 150 instanced cards) fly furthest.
- **Slabs after the kick:** at the blast itself they only rock and roll 2-5 m north on their small iron wheels and stay upright `[EV]` F04/000030127, F04/000030160. Passing titans knock them into this end state during the pour (t 8-20) `[INF]`:
  - Of the 6 by the pit: 3 toppled, lying flat toward the north; 2 tipped and leaning on each other; 1 still upright but shoved 15 m north.
  - Of the 8 across the avenue mouth: 2 lean wrecked at the avenue mouth either side of the street (X ±9, Y 80) `[EV]` F04/000031099; 4 are toppled; 2 still stand.
  - About 10 crossed timber X-stakes (2 m) lie on the middle ring and the grass `[EV]` F07/000001960.
- **Embers:** orange points drift over the square and the gatehouse for the whole beat `[EV]` F07/000001960, F04/000032081.

### 2b. Titan entry and spread
- **Outside staging:** about 40 titans wait or walk in the fields within 150-400 m south of O before the kick. They are visible at G5 only as small figures beyond the wall, if at all `[INF]`. The anime shows titans walking up to the smashed gate across the fields `[EV]` F09/000011497.
- **Lanes from the breach:**
  - **L1:** straight north over the pit's at-grade gap. 2 titans tumble into the outer trench (one climbs out, one stays sprawled on the middle ring).
  - **L2 and L3:** around the pit's east and west flanks to the ring road, then north up AV.
  - **L4 and L5:** along the ring road east and west, then into the first radials.
  - One early titan steps into the west crater and stumbles to its knees. It ties to the owner's "titans fall into the sunken ground".
  - Capacity: the hole is 15 m wide, so at most 3 titans abreast with at least 6 m nose to tail; at 2x playback that caps the flow at about 2-2.5 titans/s (section 6), with no interpenetration.
- **Spread targets by t = 31 s:**
  - About 35 titans inside.
  - Pour front at Y ≈ 200 on AV, led by 2 running abnormals at Y ≈ 260.
  - 6-8 titans in the ring and radial streets at r 100-250 m from O.
  - The rest mill in the square: 3-5 at the pit's lip, 1 sitting on the middle ring, 1 prone at the inner trench mouth `[EV]` F07/000001960, F11/000014506 (via g4).

### 2c. Defence-line positions `[CANON]` + `[INF]` positions
| unit | where (M) | strength | what they do in our take |
|---|---|---|---|
| Wall-top cannon crews (Garrison) | outer bulge wall top, every about 30 m (g4) | pairs | X -35..0 is swept at t 8.5-10.5 (1-2 sets lost). The others fire down into GS from t 12 (grapeshot) |
| Cadets on cannon duty | wall top above O, X -60..+60 (g4) | 7 | flung by the kick shock (4 visible), the rest drop down the inner face on wires; one (Eren) climbs back and runs up the sweeping forearm at t 9.5 (F04/000031985) |
| Vanguard (Garrison) | rooftops ringing GS at r 90-160 and lower AV, Y 80-250 | about 30, in 6 squads | engage the pour from t 10: gas puffs, 2-3 nape kills by t 26, one squad overrun (tiny, no gore) |
| Middle guard (104th plus Garrison squad leaders) | roof band Y 250-520, both sides of AV, about 100 m apart | 12-16 squads of 5-7 | on the roofs, a few relocating with gas puffs, as the camera passes (t 23-31) |
| Rear guard (Garrison elite) | roofs ringing E and the HQ, Y 640-820; 2 soldiers in E itself | about 20 + 2 | hold; 1 Garrison soldier chases the Abnormal with Mikasa |
| Wall Rose top above E | (-200..-80, 870, 50) | 6-8 | stand watching; no fire |

### 2d. Inner gate I and evacuation forecourt E (refines g4 2b and 2d)
- **Bastion (wider than g4; see Disagreements #8):** 38 m wide (X -153..-115), projecting Y 853..865, 38 m tall, built as 3 stepped blocks rather than 3 equal tiers `[EV]` F06/000008308 (zoomed crop), F06/000010927, F06/000013178:
  - **Central block** (X -147..-133, projecting 2 m further, to Y 851): the main round arch at its foot; the **shield crest** (2.5 x 3 m stone relief) high up at Z ≈ 20-23, about one arch height above the crown; cornices at 26 and 38 m.
  - **West wing** (X -153..-147): narrow, with a narrow arched door (1.5 x 3.5 m) and a slit window; cornice at 14 m.
  - **East wing** (X -133..-115): wider, with a **second arched door** (3.5 m wide x 5.5 m to the crown, grey voussoirs, dark timber leaf, centre X -124) and small square windows above; cornices at 18 and 30 m.
  - Proportion check: in F06/000008308 the bastion between its pilasters is about 7-8x the main arch's clear width. g4's 26 m would shrink the arch to about 3.5 m, too narrow for the cart's horse pair; hence 38 m with a 5 m arch.
- **Arch (disagrees with g4):** **5.0 m clear width x 6.5 m to the crown** (semicircular head springing at 4.0 m), not 6 x 8.
  - Grey stone voussoirs (#8d8a82) in brick (#7a4a3a).
  - Tunnel 22 m long (bastion plus wall), dark inside, with only a small bright patch of the far portal visible at oblique angles. **No green field visible through it.**
  - Reason: the cart load must visibly jam the arch ("...fit no matter how you push it!", ep06 06:04.0). In F06/000008536 the bulging sacks overlap BOTH jambs, with the dark arch head 1.5-2 m clear above the load; in F06/000009258 the load is as wide as the dark opening. So the load (5.3 m bulging, section 3) is wider than the 5.0 m clear arch and wedges against the jambs at 2-4 m height. The old 4.2 m load would have passed with 0.4 m to spare.
- **East of the bastion:** a giant pale Wall Rose pilaster (X -115..-105, full height, flaring at the foot), then a grass slope rising toward the wall foot (X -105..-60, Y 840..865, rising 0 → 4 m) with 3-4 dark broadleaf trees (10-14 m, #2f3b26) and shrubs `[EV]` F06/000008308, F06/000010927 (green slope at the upper right), F06/000012899 (trees behind the merchant). Below the slope, a paved terrace (X -105..-60, Y 820..840) behind a low retaining edge `[EV]` F06/000008308. In front of the east wing, a paved ledge 1.2 m high with 2-3 steps (X -133..-105, Y 849..853). The cart ends up in front of this ledge, between the main arch and the east-wing door `[EV]` F06/000013040, F06/000013178.
- **West of the bastion:** a second giant pale pilaster (X -163..-153), then plain wall face with one dark tree at its foot (X ≈ -172) `[EV]` F06/000008308 (left edge; the zoom shows pilaster and wall face, not a house). The old "3-storey gatekeeper's house" is removed: no frame shows it.
- **Forecourt E:** paved with dark grey setts #6f6c66 (darker than AV, F06/000009258). Usable plaza = g4's E, X -178..-102, Y 800..853, about 76 x 53 m.
  - Bounded south and west by 3-4 storey buildings with dormers. A corner turret with a conical roof stands at about (-140, 790), and a pale building with a square pyramid-roofed tower and stepped gables at about (-95, 815) `[EV]` F06/000008308.
  - **AV enters at the SW corner (-150, 800)** (g4 AV ends at (-140, 805)).
  - **The SE street EVS enters at the SE corner (-102, 800)**, 10 m wide and running straight SE to (0, 690) (bearing about 137° from E). This is the Abnormal's street `[EV]` F06/000008308 (a street leaves to the lower right with stragglers) and F06/000009899 (straight terrace street). g4 says "a street leaves east"; the frame shows it leaving to the SE.

### 2e. Mikasa's alley MA and the side street SS `[INF]` positions on g4's anchor (-260, 430)
- **MA:** N-S, centreline X = -262, 9 m wide (X -266.5..-257.5).
  - Its south mouth at Y 380 opens onto ring street r 240 around C. Its north end is a dead end at Y 458.
  - Floor Z = 0, flat grey flagstones #6e6d68.
  - The ground beyond the dead end rises toward the HQ (+4 to +8 m by Y 520), so the town visibly climbs past the broken wall `[EV]` F07/000018995, F07/000006613 (HQ on a rise).
- **West side (X -266.5):** a blank, dark, blocky masonry face, 20 m tall (#4a4640). The lower 12 m has no windows; a cornice sits at 14 m `[EV]` F07/000023911, F07/000025970.
- **East side (X -257.5):** a lighter ashlar terrace, 18 m tall (#b9b09a), with pairs of tall round-arched windows on the upper 2 floors and a crenellated/balustraded cornice. A dark stain or crack scar about 6 x 8 m sits on its lower wall at Y ≈ 445 `[EV]` F07/000025062, F07/000025970.
- **Steps:** 5 broad treads (0.3 m rise, 0.6 m going), full alley width, at Y 440-443 `[EV]` F07/000021613.
- **Rubble heap:** Y 443-458, 6 m high, made of 30-40 angular dark-grey blocks (0.5-2.5 m; #4d4f52 and #6b6a66) piled against a **broken end wall**. The wall's jagged top is 6-10 m high (keep it ≤ 10 m so the camera sees the steps), with black crack lines `[EV]` F07/000021613, F07/000018995. Titans climb in over it from the north.
- **SS (side street):** E-W, Y 418..428 (10 m wide), from MA at X -257.5 east to X -150 (joining AV near C), with 4-storey terraces on both sides.
- **Mikasa's landing spot:** (-262, 400), on a paler patch of flagstones about 6 x 4 m `[EV]` F07/000018704 (sunlight through a roofline gap is `[INF]`; a light shaft falls on the wall beside her later, F07/000023599).
- **BT** (the bearded titan holding Eren `[CANON]`): stands in SS at (-205, 423). Its being 57 m from Mikasa's alley is `[INF]` staging (the anime does not show where Eren emerges).
- **Q2, the second-fight square** (`[INF]` position, `[EV]` look): X -252..-222, Y 490..520 (30 x 30 m), just north of MA's broken end wall, on the rising ground (floor Z ≈ +5). Pale limestone paving #cfc4a8; 4-storey terraces on its W and S sides; a pale arcaded building with a dome on its N side `[EV]` F07/000027309. The Attack Titan reaches it by stepping over MA's rubble and broken end wall (≤ 10 m). g6's AT approach path (-224, 500) → (-230, 572) runs through it.
  - **Tower T:** a square ashlar tower at Q2's NE corner, centre (-218, 522), 8 x 8 m, 34 m tall with a belfry stage. Its top 8 m bursts in fight #2 `[EV]` F07/000028151 (tan dust cloud, flying blocks); a grind scar runs down its lower shaft (19:36.1).
  - **Roof R:** the tiled terrace roof on Q2's W side, ridge at (-258, 505, 25). Armin, Connie and Mikasa stand on its ridge from t 75 `[EV]` F07/000027146, F07/000028592.

### 2f. Distances that drive timing
- MA steps (-262, 441) → Q2 fight point (-245, 494): about 56 m over the end wall.
- O → E along AV: about 860 m. Breach → AV front at t 31: about 200-260 m.
- Abnormal path on EVS: (-18, 709) → kill point (-85, 782): 99 m. Skid to rest at (-96, 794), head NW, 3-5 m short of the crowd's rear edge (F06/000010927: the crowd is packed right below her).
- E → MA: about 450 m. MA → HQ plaza (-130, 640): about 270 m by street.

### 2g. ASCII (detail, north up, 1 char = 10 m)
```
Y 870  ######[I]##########       Wall Rose; I = arch (X -140)
Y 860  P BBBB P ....ttt          P pilasters (both sides), B bastion (38 m), t trees on the grass slope
Y 850  .....cc==ledge            cc cart start (in the arch) -> == end position (east, on the ledge edge)
Y 830  ..CROWD CROWD...          E forecourt (75 x 58 m), solid jam
Y 800  AV/....o.....\            AV enters SW; corpse o at the plaza mouth; EVS enters SE
Y 770         ...k..\            k = kill point (-85, 782)
Y 720             ...\..         EVS runs SE to (0, 690)
```

## 3. Set dressing and materials

- **Gate square post-kick:** g4 sections 2e and 3, plus:
  - Debris pieces: red brick #8e5040, grey stone #8d8a82, splintered planks #9a7a55, iron spikes black.
  - A rubble fan 15-20 m north of the breach, 3 m high at the hole, with broken beam ends sticking out `[EV]` F04/000034425.
  - The gatehouse hole shows broken floor beams in 3 layers (dark timber #3b2f25).
  - 2 slab barricades lean wrecked at the avenue mouth.
- **Wall-top sweep zone (X -35..0):** 1-2 cannon sets knocked off their turntables (one falls to the inner foot), crates smashed, the tiled hut flattened; debris strewn west to X ≈ -70. The paving is scuffed by a dark sweep streak decal (#5b3a30) about 8 m wide.
- **Smoke columns** start at t 14 (fires near GS from scattered debris) and number 10-15 across the district by t 30. Tall and thin; they twist and lean with the wind, some curling over at the top (F09/000011497), and read near-vertical only from far above (F09/000003117); dark grey-black (#3a3836) near the source, fading to pale grey; a slight olive-yellow haze far off `[EV]` F09/000003117, F09/000011497, F04/000031099.
- **Inner gatehouse:** section 2d. Brick #7a4a3a with dark mortar; quoins and cornices #8d8a82; crest relief #a9a291. The wall pilasters either side of it are pale #c9c1ae, the trees #2f3b26 and the grass #5f7344.
- **The cart (hero prop)** `[EV]` F06/000008536, F06/000009258, F06/000012944, F06/000013040:
  - **Bed:** flat wooden bed 5.4 m long x 4.0 m wide at 1.1 m height, dark timber #5a4532, with a rear tailboard and a short ladder of steps `[EV]` F06/000008536.
  - **Wheels:** 4 big spoked wooden wheels, 1.6 m diameter, iron tyres, outside the bed: outer track 4.8 m, so a wheel runs right beside each jamb `[EV]` F06/000012944.
  - **Shafts:** a pair of shafts at the front with 2 dark-brown draught horses side by side (#3a2a22, harness #2a2018), each about 2.4 m long and 1.6 m at the withers.
  - **Load:** one rounded bundle of about 12 big burlap sacks laid 3 across x 2 high x 2 long, wrapped in a rope lattice. Size about 5.0 L x 5.3 W (bulging past the bed) x 2.8 H, so the top is at about 3.9 m. It is wider than the 5.0 m arch and wedges against both jambs `[EV]` F06/000008536. Sack colour pale grey-beige #b4ae9f (shade #77726a), rope #5b4a36. A few dark tears in the sacking `[EV]` F06/000012944.
  - **Start state:** the horses stand inside the tunnel facing north (Y 856-862); the load is wedged in the arch mouth, its rear 1.5 m sticking out into E (Y 849-854).
  - **End state:** backed out 6 m and swung east about 40° (front still pointing NW toward the arch). Load centre at (-122, 842) with yaw 320° (front toward NW); horses' heads at about (-127, 848), just short of the east-wing ledge; the load hides the east-wing door behind it (F06/000013178). Clear lane X -146..-134 in front of the arch `[EV]` F06/000013040.
- **Fallen Abnormal:** prone, head NW, at (-96, 794), about 12 m long on the ground with its back about 4 m high, its head 3-5 m from the crowd's rear edge `[EV]` F06/000010765, F06/000010927. It steams for the rest of our take (section 5).
- **Alley MA:** section 2e. Dust layer on the flagstones. After the fight: 2 titan bodies on the steps and rubble, 15-20 chunks knocked off the heap, and a small dark blood decal (≤ 3 m) by the stomp.
- **Q2 after fight #2:** tower T's top 8 m gone; a tan dust cloud 20-30 m across settles over 6 s; 15-25 ashlar blocks (0.5-1.5 m) on Q2's paving and the nearby roofs; CC's corpse at the tower foot, steaming and shrinking toward a skeleton for the rest of the take.
- **BT carcass in SS:** after the Attack Titan tears out, a collapsed, steaming carcass (12 m) whose ribcage shows through the steam within 10 s. It becomes a skeleton in a dark pool by the end of the take `[EV]` F07/000027469.
- **Rain (optional, P2):** streak cards in a cylinder around the camera from t 52 (first drops as the crowd streams out, F06/000013602) to t 60, heaviest over the HQ pass (55-58), gone before Mikasa's fall `[EV]` F06/000013934, F06/000031774, F07/000006613, ep07 12:29.6. Optionally darken the E paving as drops land (a 2 s colour/roughness ramp). Wet-look roofs are not needed.

## 4. Characters and titans

### 4a. Titans (true scale)
| id | who | height | look | motion / speed | evidence |
|---|---|---|---|---|---|
| COL | Colossal | 60 m | skinless red muscle #b3262a / #d6453b, pale tendon stripes, lipless teeth, no hair; dense steam off the skin | head rises 0-2.5 s; still stare; kick (body dips 1.5 m at 5.0-5.5 as the leg goes back, behind the wall); right-hand grip 7.0; left-arm sweep 8.5-10.5 (whole arm about 27 m from the shoulder, chest leaning on the outer parapet, an arc of about 70° at about 35°/s over X 0..-35); vanishes 10.5 | F04/000029845, F04/000030862, F04/000031900, F04/000032081 |
| P1-P35 | pour titans | mix: 3-4 m 25%, 5-7 m 45%, 8-10 m 20%, 12-15 m 10% (g4) | naked, sexless, skin #c99a86 / #b98572 / #a8786a; bodies vary: slim, pot-bellied, long-haired, bald; 2 with long dark hair | walk 1.2-2 m/s real; play cycles at 2x (2.4-4 m/s) with matched stride, no foot sliding. 2 abnormals run 8-10 m/s, arms swinging. Some sit, crouch or crawl. 1 in the west crater, 2 in the pit | F07/000001960, F09/000003417, F09/000011497 |
| AB | Abnormal at the evac | 12-13 m (measured about 7.5x the soldier at its feet, F06/000009899) | fat, pot-bellied, short dark hair, sideburn/moustache shadow, open grin | lumbering sprint at 10-11 m/s with a tan dust cloud billowing behind it, as tall as the titan; ignores the soldiers; killed at t 40.0; pitches forward and skids 15 m | F06/000009899, F06/000010765 |
| LH | second alley titan | 7 m `[INF]` | long dark hair to the shoulders, slim | climbs in over the rubble from the north (hands on its knees) and stops on the heap; flattened by CAP's body at the punch; finished by a stamp `[INF]` | F07/000023404, F07/000023911 |
| CAP | first alley titan, the one punched | 8-9 m | stocky, short dark hair (bowl cut, reads like a cap), heavy shoulders, squinting grin | comes in over the rubble first, walks south and stoops over Mikasa, reaching; punched and hurled north along the alley; stamped face-down on the steps | F07/000019379, F07/000022164, F07/000024834, F07/000025045, F07/000025062 |
| CC | crew-cut titan of fight #2 | about 12 m (head at about the 4th floor, F07/000027309) | crew cut, square jaw, lean | walks into Q2 from the east at 2.5 m/s right below roof R; boxed, slammed into tower T, slides down, nape stamped | F07/000027273, F07/000027309, F07/000028030, F07/000028151, F07/000028580 |
| TR1 | titan Mikasa kills on the way | 5-7 m | bald | stands in a street on her route; one pass at the nape, then a steam column | ep07 11:52.9, 12:19.5 (sheets 14-15) |
| BT | bearded titan holding Eren `[CANON]` | 10 m | bearded, slack posture | stands still in SS; torn open at t 65.0 | ep07 16:49.6-16:50.3 (green lightning inside) |
| AT | Attack Titan | 15 m | lean, ripped, long dark-brown hair, pointed ears, lipless skeletal grin, skin missing in patches (red muscle on the legs and forearms), visible ribs; eyes glow green in the roar and the stomps | bursts out of BT; sprints 12 m/s; leaping straight right punch; roars; repeated one-foot stamps; runs to Q2; boxer's stance, blows, tower slam, nape stamp; then walks at 5-6 m/s (human gait, upright) | F07/000025008, F07/000025164, F07/000025970, F07/000028030, F07/000028151, ep07 17:59.6, 18:04.7 (sheets 21-22, green eyes) |

### 4b. Humans (faceless, toon, downloaded assets only, 1.65 m)
- **Mikasa:** black bob, **red scarf #8e1f1f** (the one colour that makes her readable from the air), tan Training Corps jacket #a87850, white trousers, ODM gear grey #8c9196. Must read at 10-14 px.
  - Arrival: chases AB at 8-12 m above the street (ODM, 20-25 m/s), on its left side.
  - Kill: lands on the corpse's back; then a short ODM hop over the crowd, landing about 8 m short of the cart, and she walks the rest through a lane the crowd opens (F06/000011927).
  - Confrontation: stands 3 m in front of the merchant, blade out; then back on the corpse.
  - Exit: leaves SW over the roofs at 25 m/s.
- **Garrison soldier with her:** same uniform (rose emblem); follows AB 20 m behind her.
- **Merchant:** bald, brown long coat #5a3a2a, stocky. **3 bodyguards:** dark grey-navy jackets #2e3440.
  - Start: they stand in the 4-6 m cleared gap at the cart rear, facing the crowd `[EV]` F06/000009258.
  - Confrontation: one bodyguard is shoved and falls sideways at t 46.0 `[EV]` F06/000012476.
  - End: 4-6 men (crowd plus guards) lean on the wheels and the tailboard to back the cart out `[EV]` F06/000012944.
- **Crowd at E (start of the jam):**
  - **Number:** about 5,500 `[INF]`: the jam fills about 75 x 45 m at about 1.6 people/m² on average (tight at the arch, looser at the rear edge), plus a tail of about 300 on the last 100 m of AV and about 50 stragglers on EVS. The old figure (2,000) cannot fill 75 x 50 m at the 2-3/m² it quoted; that would be 7,500-11,000.
  - **Behaviour:** packed shoulder to shoulder, facing the arch. The 15-20 nearest the load press against it with arms raised `[EV]` F06/000010052. At t 40 the rear edge recoils about 3 m from the falling titan.
  - **Palette:** muted earth tones only `[EV]` F06 05:49.5-06:08.0 (sheet_08): brown #6b4e3a, olive #5e6146, grey #7a7a72, off-white #cfc6b0, navy #3b4252, dull red #7a3b32, dark green #4e5a3e, beige #a8987a. About 10% wear head-scarves or caps. **No saturated colours.**
  - **Escape (t 50.5-61):** a funnel through the 12 m clear lane into the 5 m arch at an apparent 20-25 people/s (time-lapse; about 3x real). People walk briskly at about 3.5 m/s apparent, never sprinting in single file. The plaza decompresses from the arch outward. At that rate only about 210-260 people (about 5%) pass by t 61; the jam relaxes into a moving stream from the arch outward, but the plaza is still nearly full when the camera turns away (the old "60% by t 61" needed about 115 people/s). See the owner decision in the section 11 notes if the plaza must visibly empty.
- **The 104th behind Mikasa at the fall:** about 20-25 cadets (Jean, Armin, Connie and Sasha among them) in a loose stream 30-150 m behind her at 20 m/s over the roofs, with gas puffs `[EV]` ep07 11:21.1, 11:49.4. At her fall the stream carries on NE toward the HQ under Jean; Armin and Connie peel off toward MA.
- **Armin and Connie:** circle over MA from t 64. At t 72.0-75.0 Armin dives into the alley and takes Mikasa; with Connie he carries her NNE over the end wall to roof R on Q2's west side (about 100 m), where the three stand on the ridge for the rest of the take `[EV]` F07/000026909, F07/000027146, F07/000028592.

## 5. FX, lighting and time of day

- **Light arc (time-lapse inside the one take):**
  - t 0-14: clear late morning `[EV]` F04/000029845. Sun at azimuth about 135° (SE), elevation 45-50°, warm white #fff4e0 at full strength; deep-blue sky with big bright cumulus.
  - t 14-30: cloud roll-in (time-lapse cumulus speeding to about 15x, then a grey deck sliding over).
  - t 30-58: **dark overcast** `[EV]` F06/000009899, F06/000013160. Sun strength 20-25%, cooler; sky #6e7884 → #9aa3ad; soft shadows. One cool sun shaft moves across the Wall Rose face near E `[EV]` F06/000013040.
  - t 52-60: optional rain (P2; section 3).
  - t 61-84.0: breaking overcast with 2-3 warm sun shafts `[EV]` F07/000025970, F07/000028592. Sun strength 40-50%.
  - Throughout: no fog volumes (use the mist pass, g4).
- **Lightning (t 0.0-0.5):** a yellow-gold bolt (#ffd21a, core #fff6c8) from the sky to the field 25 m south of the gate.
  - World and sun strength spike for 2 frames, then a 1-frame dip to near black, then 1 more spike. This is the anime's yellow/black flicker `[EV]` ep04 20:42.7-20:43.4 (sheet_28), cut down to 0.5 s.
  - **Not at the Attack Titan's emergence, which uses a smaller version (below).**
- **Colossal steam:** white #f2f0ea to warm grey #cfcbc3. It rises 20-40 m above the head in continuously spawned billows, plus orange embers #ff9a3c (about 200 points) drifting `[EV]` F04/000029845, F04/000032081.
  - **Vanish at t 10.5:** a steam explosion. The cloud grows to about 100 m tall and 120 m wide outside the wall within 3 s, spills over the wall top, then thins by t 25.
- **Kick blast (t 5.5-9):**
  - A sepia/tan dust shock (#bba987 → #8e7e66) bursts from the gatehouse base, expands across GS as a low ring at 60 m/s to r about 120 m, then slows `[EV]` F04/000030119.
  - A dust column rises 60-80 m; debris arcs as in 2a; wind streak cards; a dust sheet runs along the wall top `[EV]` F04/000030205.
  - Dust lingers as a grey-brown haze in the breach. Grey smoke (#8c8984) pours out of the hole until t 30 `[EV]` F04/000031099.
- **Craters:** a thin twisting steam or smoke wisp from each (#d8d4cc, 15-20 m tall) `[EV]` F04/000034425.
- **Wall-top cannons (from t 12):** muzzle flash #ffb347 for 2 frames, then a white-grey smoke puff #e6e2da about 6 m that drifts. Grapeshot impacts are tan dust spurts on the GS grass. About 1 shot every 1.5 s along the bulge wall.
- **ODM:** small white gas puffs #f4f4f4 (0.5-1.5 m), lasting 0.4 s, every 0.3-0.6 s per flying soldier. Wires are invisible at this range. Blade sparks are not needed.
- **Titan kills and corpses:** steam starts within 1 s of death.
  - Dense white columns rise 5-15 m and keep going for the rest of our take `[EV]` F06/000013160, F06/000013934.
  - Corpses visibly shrink. BT evaporates to a skeleton in a dark pool `[EV]` F07/000027469.
  - **Blood:** only small dark red-brown decals #5a1a14 (≤ 3 m) at the stomp and at 2-3 spots near GS `[EV]` F09/000003417, plus a short dark spray of 1 m puffs at the punch, mostly hidden in steam. Keep it tasteful (owner).
- **Abnormal:** a tan dust cloud (#b0a080) billowing behind it, 10-14 m high, as tall as the titan `[EV]` F06/000009899. A big dust burst when it falls and skids `[EV]` F06/000010765.
- **Attack Titan emergence (t 64.5-65):** a small yellow-gold bolt (about 25 m) at BT plus a 1-frame local flash (a point light, not a world spike). Then a **steam burst** 25 m wide as BT is torn apart. A faint green tint in the steam core for 0.3 s `[INF]` nods to the green lightning inside the stomach (ep07 16:49.8). The AT's eyes glow green (#7cff5a, small emissive) only during the roar and the alley stamps (ep07 17:59.6-18:07.0).
- **Punch impact:** a dust ring and pale stone chips off the alley wall `[EV]` F07/000025164. **Stomp:** a dust puff and a steam geyser.
- **Tower burst (fight #2, t 78.8):** a tan dust cloud (#bba987) 20-30 m across from tower T's top, 15-25 ashlar blocks on ballistic arcs, settling over 6 s `[EV]` F07/000028151.
- **Mikasa's fall:** her gas puffs sputter (3 weak puffs, then none) at t 62. Then a ballistic drop of 22 m with a small dust puff on landing.

## 6. Choreography timeline for OUR one take (84.0 s; t = 0 = g4's G5 handoff)

| t (s) | where | what happens |
|---|---|---|
| 0.0-0.5 | south sky, gate | Yellow-gold bolt and flicker (section 5). |
| 0.0-2.5 | O, outside | The Colossal's skull rises above the gatehouse in steam; it settles with its chin at the wall top. Cadets on the wall top above O freeze. |
| 2.5-5.0 | O | Stare. Steam billows, embers drift. A few cadets back away along the rails. |
| 5.0-5.5 | O | Its shoulders dip 1.5 m (the leg goes back, hidden behind the wall). |
| **5.5** | O | **KICK.** The gatehouse bursts. Dust shock ring across GS; debris arcs (2a); slabs thrown; 2 craters punched at (±32, 20). |
| 5.8-7.0 | wall top above O | Shock sheet along the wall top; 4 soldiers flung (F04/000030236); the remaining cadets drop down the inner face on wires. |
| 7.0 | wall top, X +22..+30 | Right-hand grip on the coping; cracks spread. |
| 8.0 | breach | **First titan through** (a 5 m), stepping out of the dust haze. |
| 8.0-18.0 | breach → GS | **Pour**: 2-2.5 titans/s (max 3 abreast in the hole) on lanes L1-L5; they knock the slabs over as they pass. One stumbles into the west crater (t 10); 2 tumble into the pit's outer trench (t 11, 13); one ends prone on the middle ring. |
| 8.5-10.5 | wall top, X 0 → -35 | The left forearm sweeps west along the wall top: 1-2 cannon sets, crates and the hut fly off west and over the inner edge. One cadet (Eren, tiny) zips from the wall top up the forearm toward the nape (9.5-10.5), gas puffing. |
| 10.5-13.5 | outside O | The Colossal vanishes in a steam explosion (`[CANON]`). The cloud towers and spills over the wall. |
| 10-26 | GS, lower AV roofs | Vanguard engages: gas puffs. Nape kills at t 15 (AV mouth), 19 (east ring road) and 24 (pit lip), each followed by a steam column. One squad on a roof is overrun at t 21 (tiny, no gore). |
| 12-30 | bulge wall top | The surviving cannons fire down into GS (section 5). |
| 14-30 | district | Smoke columns appear one by one (10-15 by t 30). Clouds roll in; the light dims to overcast by t 30. |
| 18-31 | AV, ring streets | About 1 titan/s still entering. 2 abnormals run up AV ahead of the walkers; the front reaches Y about 200-260 by t 31. |
| 23-31 | mid-district (camera passing) | Middle-guard squads on the roofs; 2 squads relocate with gas puffs. The last civilians stream north up AV (thin tail) toward E. |
| 31.0 | EVS, (-18, 709) | AB rounds into EVS and sprints NW at 10 m/s with its dust cloud. Mikasa and the Garrison soldier swing in behind it on ODM from the SE. |
| 31-40 | E | The jam: solid crowd, the cart wedged in the arch, 4-6 men pushing at the tailboard, the merchant and 3 guards in the gap. |
| **40.0** | (-85, 782) | **Mikasa's nape cut.** AB pitches forward, skids 15 m and stops at (-96, 794) in a dust burst. The crowd's rear edge recoils 3 m. Steam begins. |
| 41.5-43.0 | corpse | Mikasa stands on AB's back facing the crowd (F06/000010927). |
| 43.0-44.0 | → crowd | A short ODM hop (about 45 m, anchored on the bastion face) over the crowd; she lands among the people at (-138, 838), about 8 m short of the cart. |
| 44.0-45.0 | crowd | She walks to the gap at the cart rear (-140, 846) as the crowd opens a lane in front of her (F06/000011927). |
| 45.0-47.5 | cart | Confrontation. The merchant gestures; at 46.0 one bodyguard is shoved and falls sideways. |
| 47.5-50.5 | arch | "Move the wagon": men grip the wheels; the cart backs out 6 m and swings east 40° to its end state (section 3). The horses walk backward, heads toward the arch. |
| 50.5-61 | E → tunnel | The crowd funnels into the arch (section 4b). Mikasa returns to the corpse at 51.5 (F06/000013160) and leaves SW over the roofs at 53.5. |
| 51-59 | camera pan | Passing west of the HQ: 6-10 titans gather at the HQ walls; cadets are stranded on roofs nearby (the HQ group owns the details). Optional rain 52-60 (section 3). |
| 59.0 | south of MA | The 104th stream (about 20-25 cadets) flies north over the roofs from about (-250, 300); Mikasa leads by 30 m, puffing hard. |
| 60.3 | (-256, 345) | Mikasa cuts down TR1 (5-7 m) in one pass on the way; a steam column rises (ep07 12:18-12:19). |
| 62.0 | (-258, 385), Z 22 | Her gas sputters out. |
| 63.0 | MA (-262, 400) | She falls into the alley onto the pale patch of flagstones. The stream flies on NE toward the HQ under Jean; Armin and Connie break off and circle back over MA. |
| 63.5 | MA north end → Y 410 | CAP climbs in over the broken end wall and rubble, walks south at 2.5 m/s and stops over Mikasa at Y ≈ 410, stooping, one hand reaching down (13:28.3, 15:15-15:36). She kneels. |
| 64.5 | MA north end | LH climbs in over the rubble behind it, hands on its knees, and stops on the heap (16:16.1, 16:37.3). |
| 64.5-65.0 | SS (-205, 423) | Small gold bolt at BT, then a steam burst. **The Attack Titan tears out**; the BT carcass collapses and steams. |
| 65.0-68.5 | SS → MA | The Attack Titan sprints west along SS at 12-15 m/s (about 52 m), skidding into the MA junction (Y 423). |
| 67.0 | MA | Mikasa gets up and charges CAP, running in between its feet (17:15.8). |
| **68.5** | MA (-262, 415) | **Punch**: the Attack Titan leaps out of the SS junction and lands a straight right on CAP's head (burst hidden in steam). CAP is hurled about 25 m north along the alley into LH; both sprawl on the steps and rubble. Mikasa is knocked flat by the blast; pale chips burst off the alley wall. Dust ring. |
| 70.0 | MA | The Attack Titan roars, head back and arms wide, green eyes, steam off his skin. |
| 71.5 | MA steps | CAP tries to rise face-down; the **stomp** on its nape, 3 quick stamps (18:01-18:11). Steam geyser, small dark decal. Mikasa watches from the side, by the west wall. |
| 72.0 | MA rubble | A stamp on LH as it struggles up from the heap `[INF]`; a second steam geyser. |
| 72.0-75.0 | MA → roof R | Armin dives into MA from the east roofs and takes Mikasa; with Connie he carries her NNE over the end wall to roof R (-258, 505, 25), where the three stand on the ridge (18:38.9-18:52.2). |
| 72.3-77.5 | MA → Q2 | The Attack Titan steps over the rubble and the broken end wall (0.5 s) and runs NNE into Q2 (about 56 m at 12 m/s), drawn by CC. |
| 73.0 | Q2 east side | CC walks into Q2 from the east at 2.5 m/s, passing right below roof R, and turns to face him (18:57.5, 18:59.0). |
| 77.5 | Q2 | The Attack Titan squares up, fists raised like a boxer (19:22.1). |
| 78.0 | Q2 | Two blows to CC's head and body (19:29.1-19:30.6). |
| **78.8** | Q2, tower T | He drives CC into tower T: T's top 8 m bursts in a tan dust cloud with flying blocks (19:34.1); CC's face grinds down the shaft (19:36.1). |
| 79.5 | T foot | CC slides down, steaming (19:41.9). |
| 80.3 | T foot | **Nape stamp** on CC (19:49.1-19:52.0). Steam geyser. The three cadets watch from the ridge of R (19:52.5). |
| 80.8-84.0 | Q2 → N | The Attack Titan turns and walks out of Q2 toward the HQ at 6 m/s, ignoring the cadets; the corpses in MA and Q2 steam. |
| **84.0** | about (-222, 531) | **Handoff to the HQ group**: the Attack Titan walking toward g6's plaza entry (-230, 572), bearing about 349°, at 6 m/s, low right in frame (section 7). |

**Compressed variant (about 68 s), if the owner finds it long:**
- stare 2.5 → 1.0 s
- C2→C3 drift shortened by 4 s
- confrontation 3.5 → 2.0 s
- crowd stream 10.5 → 6.0 s
- alley approach (CAP / LH) 2 s shorter
- fight #2 (77.5-80.3) down to 2 s; the run to Q2 cannot shrink
Keep every event; only shorten the holds.

## 7. Sky-observer CAMERA plan

**Rules applied:**
- Height 125-205 m; pitch 26-35° down at every key; lens 28-34 mm (never above 34); no roll.
- Positions and look-at points on Catmull-Rom/Hermite splines, **driven by arc length** so speeds never kink. Lens interpolated in log space.
- Yaw rate ≤ 30°/s at peak (all segments checked below). Ease in and out on every segment. Never fully stopped: holds keep a 1.5-3 m/s drift.
- No chase cam: the camera never rides with a character; it reframes from a fixed-height observer path. No cuts or wipes. Aerial throughout, as the owner requires from the Colossal to the Attack Titan.

| key | t | position (X, Y, Z) | look-at | lens | pitch | yaw (cw from N) | segment notes |
|---|---|---|---|---|---|---|---|
| C0 | 0.0 | (-40, 330, 170) | (0, 0, 30) | 32 | 22.9 | 173 | **= g4 G5 exactly**; incoming velocity (1.3, -8, -1) m/s. Colossal head 7.8° above frame centre; the whole of GS in frame |
| C1 | 5.5 | (-33, 290, 166) | (0, 5, 26) | 32 | 26.0 | 173 | drift 7 → 3 m/s south (41 m). Kick framed: gatehouse at centre-top, ring road at 12° below centre |
| C2 | 14.0 | (-75, 370, 200) | (0, 40, 8) | 28 | 29.6 | 167 | pull back and rise (97 m, about 11 m/s), lens widening. Takes in the steam explosion, the pour, the arm-sweep stretch at upper right, lower AV |
| C3 | 23.0 | (-20, 470, 205) | (-15, 150, 0) | 28 | 32.6 | 179 | dolly backward north at about 13 m/s, still looking south: the pour front walks up AV toward camera; smoke columns rise |
| C4 | 31.0 | (40, 590, 195) | (-170, 790, 10) | 30 | 32.5 | 314 | yaw +135° clockwise through west over 8 s (avg 17°/s, peak about 27°/s), 134 m at about 17 m/s. The pan crosses the west district (middle guard on roofs), the HQ keep, then the inner gate. AB visible entering EVS at lower right |
| C5 | 35.0 | (10, 600, 170) | (-130, 815, 8) | 32 | 32.3 | 327 | settle (40 m at 10 → 4 m/s). Wide evac frame: E, the cart, EVS with AB and Mikasa crossing the lower third (EVS is 143-300 m from camera, all in frame) |
| C6 | 47.0 | (-45, 690, 125) | (-138, 838, 6) | 34 | 34.2 | 328 | slow close-in (116 m over 12 s); the brief closer framing the owner allows. Mikasa at about 14 px; cart and horses clear; the corpse at frame bottom-centre |
| C7 | 51.0 | (-48, 693, 125) | (-139, 837, 6) | 34 | 34.9 | 328 | hold-drift; the crowd starts to stream past the moved cart |
| C8 | 59.0 | (-275, 655, 155) | (-262, 425, 0) | 30 | 33.9 | 177 | **turn and travel**: yaw -151° counter-clockwise over 8 s (avg 18.9°/s, peak about 29°/s), 232 m (avg 29 m/s, peak about 45), rising 30 m. The pan passes the HQ and its titans, then the length of MA from the north |
| C9 | 67.0 | (-270, 640, 150) | (-262, 422, 0) | 33 | 34.5 | 178 | slow push (15 m) plus lens 30 → 33 for the fight. MA is nearly on axis (8 m offset); BT/SS at about 60 m left of centre (frame half-width about 120 m) |
| C9' | 72.0 | (-280, 655, 148) | (-258, 440, 0) | 33 | 34.4 | 174 | hold-drift (18 m in 5 s) through the punch, roar and stamps; Q2 and tower T already sit in the upper-left third (5.9° below and 8.6° left of centre for Q2) |
| C9b | 80.0 | (-420, 455, 140) | (-236, 505, 10) | 32 | 34.3 | 75 | **swing west round the action**: 244 m in 8 s (avg 30.5 m/s, peak about 45 with easing), yaw -99° counter-clockwise (avg 12.4°/s, peak about 19°/s), path curving W then S with no reversal. Settles on fight #2: Q2 at centre, tower T 3° left, roof R with the 3 cadets 2° left, MA still at the right edge (24° right) |
| C10 | 84.0 | (-345, 455, 175) | (-185, 640, 15) | 30 | 33.2 | 41 | **handoff**, position/look-at/lens unchanged (= g6 H0): 83 m from C9b, about 30 m/s easing down to the 5.8 m/s exit velocity, path curving E then NNE, yaw -34°. The Attack Titan walks up into the lower right (17° right, body inside, feet 16° below centre against the 18.6° edge); HQ keep and turret in the upper half |

- **Line-of-sight checks:**
  - C1: Colossal crown (0, -25, 60) at 7.8° above centre within the 17.6° half-VFOV (32 mm, 16:9).
  - C5: the frame's ground band runs 143-530 m from camera, so EVS (from 158 m) and E (257 m) are inside.
  - C9: the broken end wall ≤ 10 m hides at most 15 m of floor behind it, so the steps (Y 440-443) stay visible.
  - C9b: the sight line to Q2 clears the 4-storey roofs between X -400 and -260 by more than 25 m; T's 34 m top is 9° below centre.
  - C10: the AT at (-222, 531) is in frame (above); the old 78.5 s handoff left him at (-218, 440), 56° right of the axis and out of frame, which contradicted "trailing the Attack Titan" (g6 review note D4).
  - No key is lower than a building plus 75 m; the HQ turret top is 49 m.
- **Handoff out (to the HQ group):** pass C10's position, look-at, lens 30, velocity (3, 5, 0) m/s (gently following the Attack Titan NNE) and dlnlens 0.
  - g6 already adopted C10 as its H0, so the camera contract is unchanged; only the time origin moves (g6 t = 0 = g5 t 84.0).
  - The AT's state at 84.0 is about (-222, 531), bearing about 349° (toward g6's plaza entry (-230, 572)), at 6 m/s. **g6 must start its approach there instead of (-218, 440)**; (-222, 531) lies on g6's own path (-224, 500) → (-230, 572).
- **What we deliberately do not do:** no low pass down the alley, no orbit around the Colossal's face, no zoom past 34 mm, and no camera height below 125 m.

## 8. Current render vs anime: gap list

Renders checked:
- trost_p1_sheet.jpg (36 cells, 1/s over trost_part1_preview.mp4)
- trost_p1_still_evacuation.png
- frames I pulled from trost_part1_preview.mp4 at 19-23 s, 26-30 s and 29-33 s

| # | P | what is wrong now | change to |
|---|---|---|---|
| 1 | P0 | **One-take broken by whip transits.** Outer gate (dust) → inner gate in about 1.5 s (preview 20.0 → 21.5 s, about 870 m, so about 500 m/s). Inner gate → plaza in about 1 s (preview 27-28 s). Both read as cuts. | Path C3 → C5 and C7 → C8 (≤ 45 m/s, yaw ≤ 30°/s), with the events placed so the camera's travel time is filled (section 6). |
| 2 | P0 | **Breach** is a small dark spot with a small grey puff (sheet row 3, cols 3-6); no debris, no thrown slabs, no craters, no smoke from the hole. | 15 m x 30-34 m ragged breach with a rubble fan; dust shock ring plus an 80 m column; debris arcs onto roofs; slabs thrown or leaning per 2a; 2 jagged craters with steam wisps; grey smoke from the hole. |
| 3 | P0 | **Titans pouring in are not visible**: the gate square is empty in sheet rows 3-4. | About 35 titans in view by t 31, from 2-3/s at first; lanes L1-L5; crater and pit stumbles; abnormal runners up AV. |
| 4 | P0 | **Colossal too exposed**: head, shoulders, upper chest and both forearms above the wall, leaning on it (row 2). The steam is a few small puffs; it never vanishes. | Chin at the wall top so only head and shoulder-tops show; one hand gripping the coping; a westward arm sweep wrecking the cannons; dense steam plus embers; a steam explosion at t 10.5. |
| 5 | P0 | **Inner gate**: a flat-topped rectangular opening in a featureless pale wall, with the green field visible straight through (still). | Stepped 38 m brick bastion (central crest block, narrow west wing with a narrow door, wide east wing with a second arched door), quoins and cornices; a 5 x 6.5 m round arch; a dark 22 m tunnel; giant pilasters on both sides; grass slope, terrace and trees to the east (2d). |
| 6 | P0 | **Cart**: a white canvas-hooded covered wagon in the opening (still). | Sack-bundle flatbed (load 5.3 m wide, wedged against both jambs) with the rope lattice and big spoked wheels, 2 dark horses inside the tunnel facing north. It backs out and swings east 40° (section 3). |
| 7 | P0 | **Crowd**: saturated rainbow colours, about 500 figures, people arriving in single-file "ant trails" (still; sheet rows 4-5). | About 5,500 in a solid jam filling E plus an AV tail; muted earth palette; arms raised at the load; the 4-6 m gap at the cart rear; a funnel exit at 20-25/s apparent. |
| 8 | P0 | **Abnormal and Mikasa's kill missing or unreadable**: nobody runs at the crowd, and there is no corpse at the plaza mouth. | AB on EVS with a dust cloud; Mikasa in a red scarf plus the Garrison soldier; kill at t 40; the corpse skids to the plaza mouth and steams. |
| 9 | P0 | **Attack Titan arrival** happens in an open plaza beside a white fountain disc and a white needle-spire church, with a big lightning bolt. The Attack Titan reads house-sized, and the fight is a loose skirmish (rows 5-6; preview 26-33 s). | The MA alley with steps, rubble heap and broken end wall; BT torn open in SS; a 15 m Attack Titan; punch → roar → stomp; Mikasa fallen at (-262, 400). Remove the fountain disc and the needle church (g4 #6, #12). Then Armin and Connie lift Mikasa to roof R, and fight #2 in Q2: boxer's stance, tower slam with a burst top, nape stamp (section 6). |
| 10 | P1 | **Lighting**: flat grey-blue from start to end. | Clear late morning → cloud roll-in → dark overcast at E → broken overcast with sun shafts at MA (section 5). |
| 11 | P1 | **No defence activity**: no soldiers on the roofs, no gas puffs, no wall-top cannon fire, no kills by soldiers. | Section 2c table plus section 5 cannon and ODM FX. |
| 12 | P1 | **No smoke columns** over the district after the kick. | 10-15 columns rising one by one from t 14. |
| 13 | P1 | **Evac camera** at about 80 m height and 45-50° pitch, with the wall filling the top half (still). | C5/C6: 125-170 m, 32-35°, 32-34 mm. |
| 14 | P1 | **Boulder** shows as a smooth blue-grey plastic ball in the open during the transit (preview about 20.5 s). | Stone ball in Boulder Court per g4 (cracked, marbled, steaming later); half-hidden among terraces in this beat. |
| 15 | P1 | **Fallen titans don't steam enough**, and there is no corpse decay. | Steam columns plus shrink and skeleton (section 5). |
| 16 | P2 | No embers, no rain episode, no blood decals, no crossed X-stakes in the square. | Section 5; section 2a. |
| 17 | P2 | Town fabric, walls and plaza paving (detached cubes, grey gravel). | Fix per g4 #3, #5 and #10; it is visible in every frame of this beat. |

## 9. Owner-rule overrides (where we intentionally differ from the anime)

- **Camera.** The anime tells all of this with ground-level, rooftop and close-up shots: Mikasa's face, the merchant's eyes, the punch from 1 m. We show every event from a calm aerial observer at 125-205 m, in one take. The brief closer framings (C6, C9 at 33-34 mm) stay aerial.
- **Skipped close beats.**
  - Eren being swallowed and the inside of the stomach are not shown.
  - We only see BT standing in SS, then the small bolt and the steam burst.
  - No faces anywhere (humans are faceless).
- **Inner gate open.** The anime gate has a dark tunnel; we keep it open (no door, owner). The cart is backed out and shoved a little to the side and **never drives through** (owner 10/26). This also matches the anime's end state (F06/000013040).
- **Time compression.** The anime's evacuation (ep06), the rain and the 104th's rooftop despair (ep07) span a long time. In one take we:
  - (a) run the clouds and light as a time-lapse;
  - (b) play titan locomotion at 2x with matched strides and the crowd's exit at about 3x;
  - (c) let Mikasa leave E heading SW at t 53.5 and **re-enter as the leader of the 104th stream flying north at t 59**. That is a continuity cheat a 10-14 px figure tolerates, justified by the time-lapse `[INF]`.
- **Colossal kick and vanish** are ep05 material we lack; staged from canon (`[CANON]`).
- **Rain.** The anime has present-day rain from just after the evacuation (F06/000013602, F06/000013934), heavy by ep06's end (F06/000031774), still falling in ep07's rooftop scenes (F07/000006613), and stopped by the 104th's charge (ep07 12:29.6). We make it optional and short (P2, t 52-60), because rain cards read poorly from the air. This **disagrees with g4 section 5** ("no rain; the anime's rain belongs to a flashback"): only the forest rain at ep06 10:24.7 ("Year 844") is a flashback.
- **Second fight (Q2) and Eren's emergence point.** The anime shows fight #2 beside the cadets' roof near the alley, and never shows where Eren bursts out. Q2, tower T and BT's spot in SS are `[INF]` placements on the AT's g6 approach path.
- **Blood and gore** reduced to small dark decals and steam (owner: tasteful).
- **Mountains** behind the Colossal (F04/000029845) are omitted (owner).
- **Arm-sweep direction (west)** and the **Mikasa alley position** are `[INF]` placements on g4's map; the anime does not fix either.

## 10. Must-have lore details checklist

- [ ] Yellow-gold lightning with a yellow/black flicker, then the Colossal's skull right at the outer wall edge, chin at wall-top level beside a cannon (ep04 20:42.7-20:44.8, F04/000029845).
- [ ] Steam plus floating orange embers around the Colossal (F04/000032081).
- [ ] Kick: the gatehouse bursts inward; sepia blast; spiked slab barricades thrown; stone blocks on the grass and ring road (F04/000030119, F04/000030127, F04/000030160).
- [ ] Soldiers flung off the wall top by the shock (F04/000030236); cadets drop down the inner face on wires (ep04 21:06-21:25).
- [ ] Red fingers curled over the wall top's inner edge, cracks radiating on the inner face (F04/000030862); a forearm sweep across about 35 m of wall top, one cadet running up the forearm (F04/000031900, F04/000031985).
- [ ] The Colossal vanishes in a steam explosion (`[CANON]` ep05).
- [ ] Tall ragged breach, broken floor beams, rubble heap, 2 jagged craters with steam wisps (F04/000034425); wrecked slabs leaning at the avenue mouth (F04/000031099).
- [ ] Titans walking loosely through the gate square, one sitting on the ring pit, one prone in it, X-stakes strewn, embers (F07/000001960); titans among the roofs (F09/000003417); titans walking in from the fields (F09/000011497).
- [ ] 10-15 smoke columns over the district after the kick (F09/000003117, F09/000011497).
- [ ] Defence lines: vanguard at the gate, middle guard of cadets on roofs, rear guard at the inner gate; wall-top cannons firing (`[CANON]`).
- [ ] Weather turns from clear (kick) to dark overcast (evacuation) (F04/000029845 vs F06/000009899); rain starts as the crowd streams out (F06/000013602).
- [ ] Inner gate: a stepped brick bastion with quoins, a shield crest high above the round arch and a second arched door in the east wing; giant pilasters on both sides; grass slope and dark trees to the east (F06/000008308).
- [ ] A solid crowd filling the forecourt, muted clothes, a 4-6 m gap in front of the merchant and 3 men at the cart rear (F06/000008308, F06/000009258).
- [ ] Sack-bundle cart wedged in the arch, its load overlapping both jambs, men pushing at the tailboard (F06/000008536); people pressing with raised arms (F06/000010052).
- [ ] A fat 12-13 m Abnormal sprinting down a straight terrace street toward the crowd with a dust cloud as tall as itself, ignoring soldiers (F06/000009899).
- [ ] Mikasa's one-pass kill; the corpse skids prone right up to the crowd; she stands on its back above them, then walks the last metres to the merchant through a lane in the crowd (F06/000010765, F06/000010927, F06/000011927).
- [ ] Bodyguard shoved; "Move the wagon"; men on the wheels (F06/000012476, F06/000012899, F06/000012944).
- [ ] Cart ends beside the arch to the east, horses facing the arch, crowd pouring into the dark tunnel (F06/000013040).
- [ ] The corpse steams long afterwards (F06/000013160, F06/000013934).
- [ ] The whole 104th follows Mikasa over the roofs; she kills titans in single passes on the way, runs out of gas and falls into a deep dark street canyon; Armin and Connie break off after her (ep07 11:49.4, 12:19.5, 12:07.2 caption, F07/000018704, 12:42.9).
- [ ] Dead end: broad steps up to a heap of angular boulders against a broken jagged wall, with the town rising beyond (F07/000021613, F07/000018995).
- [ ] A grinning short-haired titan (CAP) steps in and reaches for her (F07/000019379, F07/000022164); a long-haired titan climbs in over the rubble (F07/000023911).
- [ ] The Attack Titan (15 m, long dark hair, lipless grin, patchy skin) charges in from the side and punches CAP; the blow carries CAP and him along the alley; Mikasa thrown (F07/000025008, F07/000025045, F07/000025164).
- [ ] Roar with green eyes (ep07 17:43.9 / 17:59.6); one-foot stomp on a face-down titan with Mikasa watching (F07/000025970).
- [ ] Corpses evaporate to steaming skeletons in dark pools (F07/000027469).
- [ ] Armin and Connie get Mikasa onto a roof (F07/000027146). Fight #2: a crew-cut titan crosses a pale square below their roof; the Attack Titan boxes it, slams it into a stone tower whose top bursts, and stamps its nape (F07/000027309, F07/000028030, F07/000028151, F07/000028580); the three watch from the ridge under sun shafts (F07/000028592). Then he walks off toward the HQ.

## Disagreements with g4_trost_geography.md (for the map owner)
1. **Inner-gate arch:** 5.0 m wide x 6.5 m to the crown, not 6 x 8. The 5.3 m bulging sack load must visibly jam it (F06/000008536, F06/000009258).
2. **Rain:** g4 section 5 says there is no rain and the anime's rain is flashback. F06/000031870 and F07/000006613 show light rain over present-day Trost. Keep it optional (P2).
3. **Street leaving E:** g4 says "east"; F06/000008308 shows it leaving to the SE (lower right of a north-looking frame). Named EVS: (-102, 800) → (0, 690).
4. **Forecourt E:** g4 has X -178..-102 by Y 800..853, and this spec now uses exactly that (its earlier X -175..-100 / Y 795 drift is gone). I add the explicit AV entry at the SW corner and EVS at the SE corner, plus the east-wing ledge, the terrace and the grass slope east of the bastion where the cart ends.
5. **Craters:** same positions and size as g4, but the rims are jagged and splintered (F04/000034425), not "ragged turf lips" on smooth bowls.
6. **Titan pour rate:** g4 has "the first 300 m fills in about 60 s of story time". We use about 30 s to the front at Y 200-260, with 2x locomotion playback, for the owner's "pour in FAST".
7. **ep06 Sonnet log (not g4):** it says the horses point toward the crowd. Frame F06/000013040 shows them facing the arch, so the cart was heading north through the gate.
8. **Inner-gate bastion: 38 m wide (X -153..-115), not g4's 26 m.** In F06/000008308 the bastion between its flanking pilasters is about 7-8x the main arch's clear width; at 26 m the arch would be about 3.5 m, too narrow for the cart's horse pair. The bastion is stepped (central crest block, narrow west wing, wide east wing with a second arched door), and a pilaster flanks it on EACH side (west X -163..-153, east X -115..-105). The arch stays centred on g4's I (X -140).
9. **Colossal hands (g4 2f: "hands on the wall top at X ±25"):** kept for the grip, but true-scale reach limits the arm sweep to about 35 m of wall top (X 0..-35), not a 120 m stretch (section 2a).

## Eevee / GTX 1060 build notes
- **Crowd (about 5,850 agents):**
  - Geometry Nodes point cloud with a baked per-frame position attribute (flow-field sim run offline in Python: arch sink, cart obstacle, recoil impulse at t 40). Instance on the points.
  - 2 LODs: about 300 tris for the 600 nearest the camera path at C6; an 80-tri impostor for the rest.
  - Colour from a 9-entry palette index attribute.
  - Animation: 3-pose walk/bob flipbook (shape keys or an index-switched collection), random phase.
  - Budget: under 0.65 M tris (600 x 300 + 5,250 x 80 ≈ 0.6 M). Bake the flow field with the GN Bake node (positions for about 5,850 points over the t 31-61 window).
- **Pour titans (35-50):**
  - 8 Alembic-baked walk, run and crawl cycles; each instance is a Mesh Sequence Cache with a frame offset and random scale (3-15 m), its root on a curve per lane, with speed matched to the stride (cycle time scaled 2x).
  - Hero titans are rigged: COL, AB, LH, CAP, CC, BT and AT. TR1 can be a pour-cycle instance with a baked fall.
  - Budget: under 1.2 M tris.
- **Debris:**
  - Rigid-body bake of 30 large chunks (low poly) plus an 80-chunk particle system (instanced 6 rock meshes) plus 150 plank cards, all baked.
  - Craters: displaced discs plus a jagged-rim decal, revealed at t 5.6.
  - Gatehouse breach: a pre-broken mesh swap at t 5.5, hidden by the dust.
  - Tower T: a pre-fractured top (Cell Fracture, about 25 pieces) rigid-body baked from t 78.8, plus 8 dust cards; swap to the broken stump mesh once the dust covers it.
- **Steam and dust:**
  - Camera-facing alpha cards with a 16-frame flipbook (noise-eroded puffs), about 40 cards for the Colossal and its vanish, 6-10 per corpse, 12 for the kick shock ring.
  - Use soft alpha-blend fade by depth. No Eevee volumetrics (too costly on a 1060 across a 2 km set).
  - Smoke columns: 10-15 tall twisted ribbon meshes with a scrolling noise alpha.
- **Lightning:**
  - Colossal bolt: emissive curve, plus world and sun strength keyframes (2 frames bright, 1 dark, 1 bright).
  - Attack Titan bolt: a small emissive curve plus a point light, 3 frames.
- **Sun shafts:** additive gradient cones (2-3), no volumetrics.
- **Rain:** 3 nested cylinders of streak cards around the camera, opacity animated 0 → 0.25 → 0 over 52-60 s.
- **Shadows:** keep g4's shadow-pool advice; for the C6 and C9 close framings, add a contact-shadow-only local sun clone if the crowd looks floaty.
- **Test-render first:**
  - C2 (widest, with the debris and steam explosion)
  - C6 (crowd LOD transition)
  - C9 (alley occlusion)
  - C9b (fight #2 framing, tower burst)

## 11. Verification log (adversarial lore and buildability review, 2026-10-26)

Checked against BRIEF.md, HANDOFF.md (Trost rules, 00:44 cart rule, faceless = humans only), g4_trost_geography.md and g6's handoff notes. Every claim in section 1 was re-opened in the cited frames; ep04 sheets 28-32, ep06 sheets 07-12 and 23, and ep07 sheets 02, 07, 13-26 were scanned for contradictions and missed details. Changes:

1. **Attack Titan "walking off" was a different titan (biggest lore error).** F07/000027309 shows a crew-cut titan (CC) crossing a pale square below Armin and Connie's roof, not the long-haired Attack Titan. Rewrote item 15: the rescue of Mikasa onto a roof (F07/000026909, F07/000027146) and the anime's SECOND fight (boxer's stance 19:22.1, blows F07/000028030, tower slam with burst top F07/000028151, nape stamp F07/000028580). Added CC (4a), square Q2, tower T and roof R (2e), the tower burst FX (5), Q2 dressing (3), timeline rows 72.0-84.0 (6) and checklist items (10).
2. **Alley titans swapped.** The punched titan is the stocky short-haired "cap" titan (F07/000025045, F07/000025062), and it is the FIRST to come in (foot at 13:28.3 F07/000019379, grin at 15:24.4 F07/000022164, reaching at 15:32-15:36); the long-haired titan climbs in later (F07/000023404, F07/000023911). The old timeline punched LH. Items 13-14, 4a rows LH/CAP and timeline 63.5-72.0 corrected. In 17:29.5 the second flying body is the Attack Titan himself (red-muscled legs), not a second victim.
3. **Mikasa's route:** the whole 104th follows her (about 20-25 cadets, ep07 11:21.1, 11:49.4), not a squad of 6; she kills titans in single passes on the way (11:52.5-11:53.0, 12:18.1-12:19.7; added TR1 and the t 60.3 row); Armin sees her fall and breaks off with Connie while Jean leads the rest on (12:37.3-12:44.8), so "the squad overshoots, unaware" was wrong.
4. **Colossal arm sweep was physically impossible.** X -10..-130 needed a 120 m arm; at true scale (arm about 27 m, shoulder 10-15 m outside the wall) the sweep covers X 0..-35. Fixed in 2a, 2c, 3, 4a, 6 and the disagreements list.
5. **Colossal grip:** F04/000030862 is a south-looking shot up the INNER face: the fingers curl over the inner edge and the cracks are on the inner face, not on the coping. The hand side is now `[INF]`. Added Eren running up the forearm and flying at the neck (F04/000031985, F04/000032081, previously `[CANON]` only) and the 9.5-10.5 timeline detail. "Red-brick wall top" in F04/000031900 is pinkish stone flags.
6. **Slab barricades** stand upright right after the blast (F04/000030127 shows them rocking on their wheels, F04/000030160 still standing); the toppled state now comes from titans during the pour.
7. **Inner gatehouse:** the zoomed F06/000008308 shows pilasters on BOTH sides, a stepped bastion (central crest block, narrow west wing, wide east wing with a second arched door), and no gatekeeper's house (removed). The bastion is 7-8x the arch width, so it grows to 38 m (disagreement #8). The cart's end position is in front of the east wing, whose door shows behind it (F06/000013178); horse-head position corrected to (-127, 848) so they stop short of the ledge.
8. **Cart could not jam:** a 4.2 m load passes a 5.0 m arch. F06/000008536 shows the sacks overlapping both jambs, so the load is now 5.3 m bulging on a 4.0 m bed with a 4.8 m wheel track (F06/000012944 wheel beside the jamb).
9. **Abnormal size:** measured about 7.5x the soldier at its feet in F06/000009899, so 12-13 m, not 10 m (6.5x). Its dust cloud is as tall as the titan, not 6 m. The corpse stops 3-5 m from the crowd (F06/000010927), not 15 m.
10. **Mikasa reaches the merchant on foot** through a lane in the crowd (F06/000011927); the 50 m hop straight to the cart rear became a 45 m hop plus an 8 m walk (timeline 43.0-47.5).
11. **Crowd arithmetic:** 2,000 people cannot fill 75 x 50 m at the quoted 2-3/m² (that is 7,500-11,000); now about 5,500 at 1.6/m² with a 0.65 M-tri LOD budget. The escape rate (20-25/s apparent) passes only about 5% by t 61, not 60%; the text now says so honestly (owner decision below).
12. **Rain timing:** rain starts right after the evacuation (F06/000013602 drops on the paving, F06/000013934 rain over the corpse), is heavy by ep06's end (F06/000031774), still falls in ep07 04:22-04:36 and has stopped by 12:29.6. Window moved to t 52-60 (sections 3, 5, 6, 9; build notes). The "Year 844" forest rain (ep06 10:24.7) is the flashback g4 meant.
13. **Smoke columns** twist and lean with the wind and curl at the top (F09/000011497); only the far aerial F09/000003117 reads near-vertical.
14. **"Sunlit patch"** under the fallen Mikasa is not readable in F07/000018704 (a paler alley floor in a very dark shot); demoted to `[INF]`, with the later light shaft (F07/000023599) cited.
15. **Green eyes** also glow during the alley stamps (18:04.7, 18:07.0), not only the roar.
16. **Forecourt E** re-aligned exactly to g4 (X -178..-102, Y 800..853); the old -175..-100 / 795 drift claimed "size unchanged".
17. **Pour flow cap:** 2-3 titans/s through a 15 m hole implied overlapping bodies; now at most 3 abreast with 6 m spacing, about 2-2.5/s.
18. **Camera continuity:** inserted C9' (72.0, hold) and C9b (80.0, swing west round the action, no path reversal) and moved C10 to t 84.0 with its position, look-at and lens unchanged, so g6's H0 contract still holds. At the old handoff the Attack Titan was 56° off-axis and out of frame (g6 note D4); at 84.0 he is in the lower right. All new keys: pitch 34.3-34.4°, lens 32-33, height 140-148 m, peak speed about 45 m/s, peak yaw rate about 19°/s. Recomputed every existing key's pitch and yaw from its position and look-at: all match the table.
19. **Header and lengths:** take 78.5 → 84.0 s; trost_action mapping and the compressed variant (about 68 s) updated.
20. **Unchanged after checking:** lightning flicker (sheet_28), skull beside the cannon and tiled hut (F04/000029845), 4 soldiers flung (F04/000030236), breach with beams, rubble and 2 jagged steaming craters (F04/000034425), avenue view with leaning slabs (F04/000031099), gate-square titans and X stakes (F07/000001960), titans among roofs with blood (F09/000003417), the merchant and guards' gap (F06/000009258), raised arms at the load (F06/000010052), "Move the wagon" and the wheel push (F06/000012899, F06/000012944), horses facing the arch (F06/000013040), corpse steam (F06/000013160, F06/000013934), the arcaded street (F07/000018512), dead end with steps and rubble (F07/000018995, F07/000021613), the skeleton in a blood pool (F07/000027469). Owner rules: one take with no cuts, aerial throughout from the Colossal to the Attack Titan, heights 125-205 m, lens ≤ 34 mm, faceless true-scale humans, swallowing skipped, cart only backed out and shoved aside, no mountains: all respected.

**Open items the owner (or another group) must decide:**
- **g4 map owner:** accept the 38 m stepped inner-gate bastion with pilasters on both sides (disagreement #8) instead of g4's 26 m.
- **g6 (HQ group):** start the Attack Titan's approach at (-222, 531) instead of (-218, 440), with g6 t = 0 = g5 t 84.0. The camera contract (C10 = H0) is unchanged.
- **Owner:** the anime's second fight adds 5.5 s (take 84.0 s). Keep it, or use the compressed variant.
- **Owner:** at a believable 3x crowd time-lapse only about 5% of the jam passes the arch before the camera leaves. If "the crowd escapes" must read as an emptying plaza, either hold on E about 25 s longer or accept a 12-15x crowd time-lapse (people would visibly scurry).
- **Owner:** the C3→C4 and C7→C8 pans peak at 27-29°/s, right at the 30°/s cap. Review them in a test render for "calm"; stretching C7→C8 to 10 s (starting the turn at 49 s) is the easy fix.
- **Lore gaps (`[INF]`, our frames cannot settle them):** which hand grips the wall; LH's death; where Eren bursts out of BT (ep05/ep08 material); the positions of Q2 and tower T.
