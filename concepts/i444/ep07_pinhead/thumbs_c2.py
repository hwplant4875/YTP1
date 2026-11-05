# EP07 thumbnail C2 (owner 11/06 00:11 KST: "썸네일 C에서 숫자만 조금 아래로 내린 버전 만들어줘"): thumbnail C exactly as thumbs.py builds it,
# with the % numbers 45 px lower (centre at H-160 instead of H-205). The rebuilt C matches the delivered C to JPEG noise.
# usage: python3 thumbs_c2.py <dir with C's three TMDB originals o_<file>.jpg> [out_dir]
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
POST = sys.argv[1]; OUTD = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'upload')
sys.argv = [os.path.join(HERE, 'thumbs.py'), '/nonexistent', OUTD, POST]
src = open(os.path.join(HERE, 'thumbs.py'), encoding='utf-8').read()
exec(src[:src.index("three([F('poster:o_lnCm")])          # helpers only; A/B need the laptop's clips
specs = [F('poster:o_pl5OzUABUK5AgAsMlQg2VyybRHL.jpg', 0, 1719, 485, 188, '85%', GREEN, 0.95),   # same specs as C in thumbs.py
         F('poster:o_udZ3XqsurnNuGp1QfS5CLod6MS5.jpg', 0, 1000, 450, 283, '25%', YEL, 0.95),
         F('poster:o_xjeoa7KjnUMQzJXGunHmgMjhHmP.jpg', 0, 2556, 802, 405, '5%', RED, 1.05)]
im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); x = 0
for sp, pw in zip(specs, PW): im.alpha_composite(panel(sp, pw), (x, 0)); x += pw
d = ImageDraw.Draw(im); x = 0
for k in (1, 2): gx = sum(PW[:k]); d.rectangle([gx - 3, 0, gx + 3, H], fill=(0, 0, 0, 255))
for sp, pw in zip(specs, PW): shadow_text(im, (x + pw // 2, H - 160), sp['pct'], f(182), sp['col'], stroke=8); x += pw
im.convert('RGB').save(os.path.join(OUTD, 'pinhead_thumb_c2.jpg'), quality=92); print('pinhead_thumb_c2.jpg')
