"""STRATA France Short #1: 'The TikTok that spread it'. Writes short1.json (see common.py for the render command).
Facts: research.md 1.1 (Créteil, Saint-Exupéry, strike 17 Sept, blockade 18 Sept, Booska-P 24 Sept, ~1.5M TikTok views),
2.1 (~60 Île-de-France schools disrupted 24-25 Sept; 1,027 lycées on 1 Oct, Interior Ministry)."""
from common import Short, P, ph, v2, news, cc, d3, MUSIC, BINS, TICK, HIT

s = Short(1, "FRANCE · LYCÉE PROTESTS")
s.line("A single TikTok video helped turn one school's strike into a national revolt.", [
    P(ph(432), cap="HOW A *TIKTOK*\nSPREAD A\nSCHOOL REVOLT", kb=[1.05, 0.5, 0.5, 1.16, 0.5, 0.45]),
    P(cc("Lycée_Colbert_in_Paris_35"), at="strike", start=1.0),
    P(ph(383), at="national", kb=[1.04, 0.5, 0.5, 1.12, 0.5, 0.5])])
s.line("It began in mid-September, at one lycée in Créteil, just outside Paris.", [
    P(d3("map", "spark"), start=0.6, cap="*CRÉTEIL*\nMID-SEPT 2026"),
    P(v2("creteil_saint_exupery"), at="Créteil", kb=[1.04, 0.5, 0.55, 1.15, 0.5, 0.5])])
s.line("Teaching posts there were empty, so the teachers went on strike.", [
    P(v2("carriat_307"), cap="*EMPTY*\nTEACHER POSTS"),
    P(ph(80), at="teachers", cap="TEACHERS\nON *STRIKE*", kb=[1.04, 0.5, 0.4, 1.14, 0.5, 0.35])])
s.line("The next day, pupils blocked the gates.", [
    P(ph(156), cap="PUPILS\n*BLOCKED*\nTHE GATES", kb=[1.05, 0.5, 0.5, 1.17, 0.5, 0.45])])
s.lf(21, [
    P(news("reuters_gate"), cap="24 SEPT\n*BOOSKA-P*\nINTERVIEW"),
    P(ph(155), at="rap-news", kb=[1.04, 0.5, 0.5, 1.15, 0.5, 0.48]),
    P(ph(154), at="eight pupils", kb=[1.04, 0.5, 0.5, 1.14, 0.55, 0.5])])
s.lf(22, [
    P(ph(191), cap="FEELING\n*ABANDONED*", kb=[1.04, 0.5, 0.45, 1.15, 0.5, 0.4]),
    P(ph(165), at="as kids", cap="KIDS OF THE\n*BANLIEUE*", kb=[1.04, 0.5, 0.5, 1.15, 0.5, 0.5])])
s.lf(23, [
    P(d3("phone", "viral"), start=7.0, cap="*{n}*\nTIKTOK VIEWS", count=[0, 1500000, 3.6]),
    P(ph(357), at="one and a half", kb=[1.04, 0.5, 0.5, 1.13, 0.5, 0.5])], sfx=TICK)
s.lf(24, [
    P(ph(120), cap="THE IDEA\n*SPREAD*", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.5]),
    P(ph(108), at="falling apart", cap="FALLING\nAPART?\n*BLOCK IT.*", kb=[1.04, 0.5, 0.5, 1.16, 0.45, 0.5])])
s.lf(25, [
    P(d3("map", "spread"), start=8.0, cap="25 SEPT\n*~60 SCHOOLS*\nPARIS REGION"),
    P(ph(100), at="Paris region", kb=[1.04, 0.5, 0.5, 1.14, 0.5, 0.45])])
s.lf(27, [
    P(d3("map", "ignite"), start=0.0, cap="1 OCTOBER\n*{n}* LYCÉES", count=[180, 1027, 2.4]),
    P(cc("Lycée_Louis-le-Grand_in_Paris_86"), at="twenty-seven", start=3.0)], sfx=TICK)
s.end(sfx=HIT)
s.write(MUSIC["crypto"], "One TikTok Video Spread France's School Revolt #shorts",
        "In mid-September, teachers at one lycée in Créteil went on strike over empty posts and pupils blocked the gates. "
        "A Booska-P interview with eight pupils hit ~1.5 million views on TikTok. By 1 October, 1,027 lycées were affected.",
        sfx_first=BINS)
