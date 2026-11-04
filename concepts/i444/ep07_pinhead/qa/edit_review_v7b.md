# EP07 v7b edit review by the QA agent (2026-11-05 ~03:05 KST), against commit 42a8fea = the shots of the 68f012f render


Of the round-1 fixes, these hold:
- Chains in Hellbound and the Bloodline ending now play at normal speed.
- The Priest trailer shot and the Bloodline "Pathway" shot are no longer used twice.
- Kate and Sarah are now told apart.
- The Judgment opening and its survival-rate shot no longer share a moment.
- The only shots still slower than 0.6x are s01 "we score" (0.586x) and the s13 ending (0.4x).

The fix "Elliot Spencer's human face only in the death beat" did not land, and many beats are still wrong. Several claims below are checked against clip transcripts and YouTube descriptions, not just plot knowledge.

### Must fix (times are from the start of each section)

**s00 opening**
1. **3.64–6.76, "This one will peel your skin off while you're still alive."**
   - **Problem:** the clips are now Revelations (hr9_rev 3942.19, 3937.15, 2195.9, 2183.6). shots_v7.py still describes them as the 2022 Priest flaying Nora, and the script's shot list asks for the 2022 Priest flaying Nora. The film label on screen will say Revelations. These moments also sit 4–25 s from shots s05 uses (2173.75, 2199.40, 3922.38, 3951.70).
   - **Fix:** check the frames and fix the descriptions. Otherwise go back to the ffb77db Nora shots (hr22_nora 153.6, 169.13, 161.93), using an unused, non-trailer close-up of the Priest at hr22_bridge about 23.8–25.0.

**s04 Hellbound**

2. **2.03, "Doctor Channard forces."**
   - **Problem:** hr2_channardpack2 751.6 falls in 600–760, which beats_v7.md describes as Channard already a Cenobite, killing patients. He only becomes a Cenobite at 22.15.
   - **Fix:** a shot of human Channard: hr2_channardtrans before 105.5, or hr2_tiffany. Check the frame.
3. **3.23, "a young patient, Tiffany."**
   - **Problem:** hr2_legendary 176.0 is inside the Hellbound trailer that JoBlo attached after the scene. The scene ends around 152, the trailer voice-over ("the vision is renewed, the power is real") runs 170.7–184, and its title appears around 201.
   - **Fix:** hr2_tiffany 4K, for example 0.5 as v7 used.
4. **8.77, "because the desire that called them was his, not hers."**
   - **Problem:** hr2_legendary 53.4–57.1 is not the "it is desire" line. It is the photo scene ("What is this?" / "...escaped us like Frank?" / "this one didn't escape, and it's you", 46.8–63.9), and it runs straight on from the 50.15 photo shot.
   - **Fix:** a close-up of Channard, as the script's shot list asks, or hr2_tiffany after 262.55 (v7 used 295.75).
5. **The Spencer shots contradict the frame-checked beats in beats_v7.md:**

   | Time | Narration | Current shot | Actually shows (per beats_v7.md) | Use instead |
   |---|---|---|---|---|
   | 12.50 | "Then Kirsty..." | tiffvs 205.67, at 0.675x | Spencer standing among the chains | A Kirsty frame from hr2_legendary about 46–50 |
   | 19.26 | "a British army captain" | 201.40–202.76 | Spencer human again, from his death | 203.13–205.67 (the photo) |
   | 38.58 | "and for a moment he's Elliot" | 200.16–201.23 | Still the flare where Pinhead vanishes (199.73–201.27) | 201.27–203.13 at normal speed |
   | 40.10 | "Spencer again, human" | 211.83–213.83 | Not a checked span | 208.77–211.83 (checked close-up) |

**s05 Revelations**

6. **9.95 and 12.62, "Steven to kill for him" and "then kills Steven."**
   - **Problem:** they use 3274.5 and 2105. v6 had the same two shots the other way round. 2105 (35:05) falls between "solves the box" (31:06) and "dragged to Hell" (36:14), before either event can happen.
   - **Fix:** check both frames; one version is wrong.

**s06 1987**

7. **4.00 and 14.32, Frank torn apart (twice).**
   - **Problem:** the two tearings are swapped.
     - 4.00 "the Cenobites rip him apart" uses hr1_jesuswept 124.25. That clip is the ending ("Kirsty tricks Frank / Jesus wept"), with Frank wearing Larry's skin.
     - 14.32 "all over again" uses hr1_pack4k 6.5–8.9. That is in the wordless start of the pack, before the "Frank solves the box" shot at 10.43.
     - Also, 5.72 "with hooked chains" (pack4k 110.85) runs straight on from s01's Pinhead shot, during Pinhead's "...this isn't for your eyes", so there are probably no chains in it.
   - **Fix:** use the attic tearing (pack4k after 10.43, check the frames) at 4.00 and 5.72, and jesuswept 131.5–138.9 at 14.32.
8. **16.74 "then come for her anyway" and 18.45 "and she only survives."**
   - **Problem:** both are from the earlier hospital bargain (hr1_youopened 354.85 "what has that to do with you?" and 358.44 "I can lead you to him").
   - **Fix:** "We have such sights to show you" (pack4k 117.44–123.16, or hr1_sights 4.67–8.22), then Kirsty with the box (pack4k 124.3–129.7, or hr1_dont).

**s07 Hellseeker**

9. **11.49, "She offers Pinhead five souls."**
   - **Problem:** kirstypack 156.5 is Pinhead talking, before her offer.
   - **Fix:** about 166–174 ("I will bring you five souls in exchange for mine").
10. **14.26, "she kills three of Trevor's mistresses."**
   - **Problem:** kirstypack 268.1 is the final scene, where Kirsty hands the box to the detective ("my anniversary gift... turn it in as evidence").
   - **Fix:** check the reveal at about 176–191 ("You'll get your five... all those women") for the murder flashbacks, or hr6_flashbacks.
11. **16.82, "then Bret."**
   - **Problem:** hr6_painpleasure 175.3 is a scene Miramax lists as Trevor and Sage only (acupuncture and "I prefer pain"). Bret is not in it.
   - **Fix:** hr6_price (Trevor's flashback to the deal), or the reveal montage above.

**s08 2022**

12. **18.77, "as the final sacrifice."**
   - **Problem:** hr22_carousel 415 is Matt being taken, the first victim.
   - **Fix:** anything but Matt, for example Riley with the box's blade (hr22_trailer_20th 53.4–60.0; check it for on-screen text).
13. **20.41, 21.69 and 23.37, the three shots meant to show Trevor.**
   - **Problem:** none of them is a confirmed Trevor. 20.41 is hr22_trailer_20th 87.6 at 0.675x, unchecked. 21.69 and 23.37 are hr22_carousel 264 and 280.5, the carousel/park scene with Riley and the Cenobites.
   - **Fix:** frame-checked Trevor shots.
14. **25.29, "the millionaire who owned the box."**
   - **Problem:** hr22_final is 1280x720 and marked REJECT in clip_sources.txt.
   - **Fix:** Voight from hr22_trailer_20th (check about 6.3–8.2), or YouTube X5mrmW8QT9Q, "Voight explains his gift in his chest" (67 s); check that it is at least 1080p.

**s09 Bloodline**

15. **13.68, "then John Merchant."**
   - **Problem:** hr4_straighthell 59.0 is still the Sharpe scene.
   - **Fix:** a frame with John in hr4_pathway (Miramax: "Pinhead demands one thing of John").
16. **17.36 and 18.44, "In twenty-one twenty-seven..."**
   - **Problem:** both use hr4_painface ("Pain Has a Face"), where guards are fused into the Twins. That is the 1996 New York part of the film.
   - **Fix:** hr4_finalbattle 4K on the space station, about 75–126, avoiding 85.5–87.1 (already used).

**s02 Hellworld**

17. **23.53 and 24.45, "Only Chelsea and Jake are dug out."**
   - **Problem:** hr8_explain 224.5 and 228.0 fall while the Host says "I buried you in separate coffins... with ventilation" (215.7–229.1). That is the burial, not the rescue, and the clip ends ("see you in hell", 362.5) before any rescue.
   - **Fix:** check hr8_welcome 10–54 for the dig-out, or find another source.

**s10 Deader**

18. **23.89 and 25.20, "Rather than be taken, she takes her own life."**
   - **Problem:** hr7_returns 13.2 and 16.7 are in the ritual at the start of the clip (Miramax: "time for Amy to complete the Cenobite ritual"). They run straight on from the 10.55 shot used for "so he kills Amy and brings her back", and Pinhead has not arrived yet.
   - **Fix:** Amy's actual suicide. Check hr7_returns 191–224 and hr7_youopened after about 85.

**s03 Judgment** (checked against the clip transcripts)

19. **15.91, "then offers them up."**
   - **Problem:** hr10_hell4k 342.0 comes before Pinhead even appears.
   - **Fix:** hr10_judge4k 510.30–512.97 ("Them for me. Adulterers.").
20. **17.25, "Pinhead refuses any deal."**
   - **Problem:** hr10_judge4k 523.4 is the Auditor saying "Ah, Mr. Carter. So good to see you again."
   - **Fix:** 517.47–522.65 ("there is no bargaining to be done"), or 506.84–510.18 ("There is no deal to be made").
21. **22.11, 23.63 and 26.35: Sean killed, the angel torn apart, Pinhead thrown out of Hell.**
   - **Problem:** none of these happen in the shots used.
     - At judge4k 498.6, Sean is alive, before the deal.
     - 560.3–563.0 is "You have been found guilty by the jury."
     - 584.4 is "When the Surgeon and the Butcher are finished with you."
   - No clip in the library reaches those events. Each clip's dialogue ends first:
     - judge4k at 600.4 of 617 s
     - hr10_final at 241.7 of 248 s
     - hell4k cuts to a different victim (Watkins) at 482
   - A quick YouTube search found no clean clip of the ending.
   - **Fix:** get the film's last minutes from the owner's own file, as was done for Revelations (hr9_rev).
22. **28.55, survival-rate shot.**
   - **Problem:** judge4k 500.5 runs straight on from the 498.6 shot and lands on Sean saying "I knew someone would come for me."
   - **Fix:** a close-up of Pinhead, such as 593.2–600.4 or 561.4–564.1.

**s12 Hell on Earth**

23. **4.28 "breaks out of the Pillar" and 6.68 "once he's free."**
   - **Problem:** in hr3_pillar Pinhead never leaves the Pillar. 230.2 is him saying "Now, can we talk sensibly?", and the scene ends at 335–342 still inside it.
   - **Fix:** the breakout (check the start of hr3_club), then Pinhead walking free (hr3_iamtheway, entering the church).

### Should fix

**Slow motion**
- s01 5.59 (Rotten Tomatoes trailer at 0.586x): use any close-up of Pinhead at least 2.7 s long, at normal speed.
- s13 21.60, "keep that box closed" (0.4x, the build script's minimum): hr2_tiffany has a 9.9 s clean span from 49.59; use about 53–57 at normal speed.
- Borderline (0.63–0.70x): s11 11.52, s12 2.48, s04 12.50, s08 20.41, s05 0.00, s09 11.52, s12 0.00, s03 0.00.

**Hellbound (s04)**
- 17.01 "he remembers": hr2_legendary 64.45 is Pinhead denying it ("Nonsense, I—"). Use 94.2–103.2 ("I... remember").
- 22.15 "That's when Channard arrives": the current shot is Channard floating into the asylum ward. His arrival in front of Pinhead is hr2_legendary about 119–139 ("I'm your doctor. I'm here to help you").
- 20.62 (tiffvs 128.9) and 42.10 (tiffvs 120.8) are not in the checked beats. Confirm 128.9 is the photo and 120.8 is Channard.

**Other sections**
- **s05:** Kate is shown at 3922.38 and then 3914.08, later moment first. Swap them.
- **s06:**
  - Use the exact lines:
    - "You've done this before, right?" (333–336) for "she thinks fast"
    - "I can lead you to him" (358.55) for "She offers them a deal"
    - "take him back instead of me" (362.18) for "in exchange for her life"
  - The current 50.22, 337.38 and 351.18 don't match these lines.
- **s07:** at 8.63, use Kirsty saying "How did you find me?" (about 139.7) instead of Pinhead at 135.3.
- **s08:**
  - 17.01 "stabbing her boyfriend" is a stand-in: it's the bridge scene where Riley refuses. Keep it only if the owner accepts that no HD footage of the stabbing exists.
  - For "she says no", use Riley's actual "No." at hr22_bridge 21.2–22.5, answering "Two more and he is yours". The current 17.0 sits under the Priest talking.
  - 12.70 (hr22_carousel 535.5) and 5.34 (hr22_carousel 498) are unchecked.
- **s09:** 0.00 "the one that goes to space" is a 1996 shot.
- **s02:**
  - "had drugged all": use hr8_explain 171.6–178.7 or 187.9–198.1.
  - "buried them alive": use hr8_explain 215.7–220.3.
  - hr8_welcome 90.8 was the meat-hook shot in v7 and is the cleaver now. Check both against the frames.
- **s10:**
  - "tells her she now owes the Cenobites": use hr7_youopened 59.7–65.5 instead of Amy shouting at 5.26.
  - hr7_afraid is a loose match for "finds a cult".
- **s03:** 19.26 and 20.78, the chain shots, are unchecked and in the wrong story order. hell4k 351.4 comes before Pinhead's first line, about 85 s before judge4k 559.
- **s11:**
  - Replace both hr5_fineboy shots ("Fine Looking Boy", a 25 s spare clip).
  - For the hunt, use hr5_engineer.
  - For "he learns he's been in Hell", use hr5_torment 494.4–503.7 ("this is the hell you have created for yourself").
- **s12:**
  - 21.83 "Inferno's Pinhead wanted one man" shows Dr. Gregory, the therapist, played by James Remar, not Pinhead. Use hr5_torment 452.7–458.2.
  - Confirm Pinhead, not Joey, the priest or Elliot, is on screen at:
    - s12 0.00 and 7.77 (hr3_iamtheway)
    - s00 6.76 and s13 4.21 (hr3_unstoppable, which is Elliot's conversation with Joey)
    - s12 17.62 "Only Joey" (hr3_finalbattle 301.8)

**Adjacent moments reused**
- hr3_finalbattle 294.0, 299.9 and 301.8 (s12) plus 304.0 (s13) are four beats from one 12-second stretch.
- hr3_finalbattle 315.0 (s01) sits next to 317.8 (s12).
- hr10_judge4k 559.14 and 560.31 are back to back.
- hr5_welcome 0.0 (s00) and 1.2 (s11 survival-rate shot) are the same close-up.
- hr1_jesuswept 124.25 (s06) sits between the two s00 shots at 122.75 and 127.21.

**Text and resolution**
- Check these trailer shots for title cards or branding: hr9_trailer_rt 72.4, hr1_trailer_arrow2 76.0, hr8_trailer 14.6, hr22_trailer_20th 97.46, 95.88 and 87.6.
- hr8_explain is the film scene itself, not an interview. Confirm it is 1080p.
- hr1_dont's resolution reads "2560x1440x". Check whether the extra "x" is a typo.

### Hellbound verdict
From "Pinhead and his Cenobites" to "blade finishes him", the chains, tentacles, Cenobites being cut down and the strike all use checked spans at normal speed. Channard's beams hitting Pinhead (193.93–195.17) and the white-hot head (195.40) leave no doubt that Pinhead is struck. Four things are not exact:
- the arrival shot is the asylum ward
- 38.58 is still the flare, not Spencer
- 40.10 is an unchecked span
- 120.8 under "until Channard's" is unchecked

With item 5 and the s04 should-fix entries applied, the sequence is exact.

I didn't edit any files. I reviewed shots_v7.py, beats_v7.md, script_v7.md and clip_sources.txt in /home/user/YTP1/concepts/i444/ep07_pinhead, plus /tmp/claude-0/-home-user-YTP1/bb3b993e-7de0-5d78-af5e-c29db5ac82a5/scratchpad/shots_v7b.md.
