# QA round 4 (autopilot, compare with the user refs)

- [x] g1 v8 opening vs ref/hill_tree_wall_opening_ref.png: tree still larger than in the still -> lens 0.7/0.6 n0 (g1 v8).
- [x] Colossal (g1 v8, g5 v9) vs ref/user/colossal_face_user_ref.png: texture greyish-pink under the amber grade -> colossal_asset._boost
      (saturation 1.45 + red push) for g1 v8 (and g5 next render).
- [x] f3 v7 at 480p OK (0 crashes, 755 unique) with clip 600 m descent / 350 m canopy (f3 v7); fallback = f3 v6 (360p).
- [x] master_onetake_v6 (g1 v8, g5 v9) + part2_3_onetake_v6 (f3 v7 480p) + full_onetake_v4 (6:30, tagged, all 480p).
- [~] forest far-clip white sky slivers -> make_sky 'ForestDim' (camera rays fade to dark forest tone under the canopy). Stills OK -> f2 v4, f3 v8.
- [x] g2|g3 seam: camera matches but g2's canal set vs g3's world river differ (content pop) -> concat_master.sh: 0.6 s night dissolve there only. master_onetake_v7 (210.0 s).
- [~] f1 plain bare -> fset keeps every 7th tree of the pruned world clumps on the f1 plain (floor patches stay removed). f0 v4 / f1 v6 / f2 v5 for consistent seams.
