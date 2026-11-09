# EP08 grade and framing, read by build_edl.py after shots.py (cloud 11/9 KST from the marks measured in beats_v1.md; the laptop
# adds the VDARK/DARK lists after the first QA pass). All boxes and bar heights are in SOURCE pixels of the 1920x1080 frame (after
# the renderer's fill-scale), so they hold at any zoom: render_cj.py draws a bar only when the shot's framing still shows its mark.
# Owner rules: the only cover is a black bottom bar over a mark at the very bottom; never blur or delogo. The Conjuring Archives
# logo sits only in the letterbox bars, so those clips are cropped (zoom 1.38) instead of covered.
MC = ['ach_case', 'ach_bride', 'ach_ferry', 'ach_ferry_b', 'ach_wolf', 'ach_tv', 'ach_end', 'a14_basement', 'a14_stairs', 'a14_baby',
      'co_mother', 'co_doll', 'co_neck', 'c1_clap', 'c1_feed', 'c2_crooked', 'c2_grave']   # Movieclips mark in the bottom letterbox bar
# (n2_altar, n2_bell: no mark seen; n2_maurice, n2_exorcise, n2_goat: check one frame each and add them here if they carry it)
RT = ['c1_exorcism_b', 'lr_priest', 'lr_mirror']                     # old RT/Movieclips mark, its top 55 px inside the picture
CR_FULL = ['cr_stair', 'cr_soul', 'cr_sam', 'cr_wasnt', 'cr_well', 'cr_scarecrow']   # full-frame Creation clips, mark ON the picture
ARCH = ['a14_fire', 'c2_name', 'c2_name_b', 'dm_promise', 'dm_truth', 'dm_altar', 'dm_vision', 'dm_calvary', 'dm_heart', 'n1_open']
MARKS.update({k: [(69, 955, 481, 1043)] for k in MC})
MARKS.update({k: [(70, 885, 477, 970)] for k in RT})
MARKS.update({k: [(70, 968, 412, 1040)] for k in CR_FULL})
MARKS.update({k: [(740, 0, 1210, 145), (740, 935, 1210, 1080)] for k in ARCH})
MARKS['c1_dog_b'] = [(1718, 82, 1821, 149)]                         # the recap channel's red bug, top right, whole clip
BAR.update({k: 945 for k in MC})                                      # bottom bar from source y 945 (the picture ends ~941)
BAR.update({k: 880 for k in RT})                                      # EP04 v3: the owner-approved bar over the RT mark
BAR.update({k: 960 for k in CR_FULL})                                 # fallback only: CLIPOPT keeps the mark out of frame
CLIPOPT.update({k: 'z=1.38' for k in ARCH})                           # crop to the picture rows 146-934
CLIPOPT.update({k: 'z=1.13,dy=-300' for k in CR_FULL})                # top-anchored zoom: rows 0-956 visible, the mark (968+) never
CLIPOPT['c1_dog_b'] = 'z=1.3'                                         # crops the corner bug (visible x 222-1698)
# QA pass 1 (rendered frames): near-black spans lifted. VDARK = gamma 1.4, DARK = gamma 1.25 (default 1.06), per clip.
VDARK += ['ach_wolf']                                                 # beats_v1: the hellhound attack is very dark
DARK += ['ach_ferry_b', 'ach_room', 'co_mother_b', 'cr_soul', 'cr_trapped']
