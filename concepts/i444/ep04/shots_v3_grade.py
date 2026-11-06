# EP04 v3 grade, read by build_edl_v3.py. BAR: clips that carry the grey "RT MOVIECLIPS" mark bottom-left (source y ~885-970, found on
# frames in beats_v3.md) get the black bottom bar from y 885 instead of 980 (the owner-approved cover; never blur/delogo).
RT_MARK = ['n3_marionette', 'n3_primetime', 'n3_taryn', 'n3_wizard_rt', 'n3_skeleton', 'n3_nancy', 'n3_souls', 'n3_heres', 'n3_worm',
           'n3_bed', 'n3_best4k', 'n5_forcefed4k', 'n5_son4k', 'n5_hell4k', 'n5_baby4k', 'n5_drunk', 'n5_motorcycle', 'n6_maggie',
           'fj_world', 'fj_kicks', 'fj_hell', 'fj_rave', 'fj_apesh', 'fj_pillar', 'fj_aftersex', 'fj_decap']
BAR.update({k: 885 for k in RT_MARK})
