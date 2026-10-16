"""Long-form #4: KPop Demon Hunters, one year recap (16:9, ~10 min). Facts checked 2026-10-16 (Wikipedia film/song/accolades
pages, Netflix Tudum, Billboard, THR, Deadline, Euronews, What's on Netflix, Korea JoongAng Daily, Korea Times).
Beats: (text, visual) pairs; consecutive pairs of one beat are read in ONE TTS request, the visual switches when its text starts.
Visual kinds: P photo, H headline paper over photo, N big number over photo, B big statement over photo. Images live outside the
repo (third-party): build.py <img dir> <out>. `cnt` updates the corner counters (views in millions, awards)."""

def P(img, src, t=None, cnt=None): return {"k": "P", "img": img, "src": src, "t": t, "cnt": cnt}
def H(head, img, src, cnt=None): return {"k": "H", "head": head, "img": img, "src": src, "cnt": cnt}
def N(num, label, img, src, cnt=None): return {"k": "N", "num": num, "label": label, "img": img, "src": src, "cnt": cnt}
def B(text, img, src, cnt=None): return {"k": "B", "text": text, "img": img, "src": src, "cnt": cnt}

NF, SPA = "Netflix", "Sony Pictures Animation / Netflix"
# timeline months: 0 = Jun 2025 ... 16 = Oct 2026
HOOK = [
    [("One year ago, almost nobody had heard of HUNTR/X.", P("og_mbw", SPA, "Who are <em>HUNTR/X</em>?"))],
    [("Then a cartoon girl group beat real pop stars on the charts,", B("<em>#1</em> on the Billboard Hot 100", "y_yebNIHKAC4A_maxres2", SPA)),
     ("packed movie theaters,", P("og_won", SPA, "Sold-out <em>sing-alongs</em>")),
     ("and walked away with two Oscars.", P("y_uH5bGSSw_l0_maxres2", "The Hollywood Reporter", "<em>2</em> Oscars 🏆"))],
    [("This is the year KPop Demon Hunters took over the world.", B("The Year <em>KPop Demon Hunters</em><br>Took Over the World", "y_AzCAwdp1uIQ_maxres3", NF)),
     ("Let's go back to where it all started.", P("y_oDSEGkT6J-0_maxresdefault", NF))],
]
CHAPTERS = [
  {"q": "Where did it all start?", "date": "June 2025", "m": (0, 0.6), "pose": "popcorn_tv", "beats": [
    [("On June twentieth, twenty twenty-five, Netflix released an animated movie with almost no hype.", P("y_AzCAwdp1uIQ_maxresdefault", NF, "June 20, 2025"))],
    [("It was made by Sony Pictures Animation, the studio behind the Spider-Verse movies,", P("y_3JTVQTk36R8_maxresdefault", SPA, "Sony Pictures Animation")),
     ("and directed by Maggie Kang and Chris Appelhans.", P("y_C7jHSbFCrO4_maxres3", "Collider", "Maggie Kang & Chris Appelhans"))],
    [("Kang first pitched the idea back in twenty eighteen. She wanted a story rooted in her Korean heritage, mixing K-pop, mythology and demons.", P("y_WxOZKMv3GTY_maxres1", "CNN", "Pitched in <em>2018</em>"))],
    [("The idea sounded wild.", B("The idea sounded <em>wild</em> 🤯", "y_HT46zbEQdiw_maxres3", NF)),
     ("Three K-pop idols, Rumi, Mira and Zoey, secretly hunt demons,", P("og_deadline", SPA, "Rumi · Mira · Zoey")),
     ("and their voices power a magic barrier called the Honmoon.", P("y_3JTVQTk36R8_maxres3", SPA, "The <em>Honmoon</em>"))],
    [("Their rivals? A boy band called the Saja Boys, who are secretly demons.", P("og_kt_saja", SPA, "The <em>Saja Boys</em> 😈"))],
    [("The voice cast included Arden Cho, May Hong, Ji-young Yoo and 안효섭,", P("og_jad_236", NF, "Arden Cho · May Hong · Ji-young Yoo · Ahn Hyo-seop")),
     ("while EJAE, Audrey Nuna and REI AMI sang for HUNTR/X.", P("y_z9PusX5ugbI_maxres2", "The Tonight Show Starring Jimmy Fallon / NBC", "EJAE · Audrey Nuna · REI AMI"))],
    [("There was no big theater launch, just a Netflix release.", P("y_uH5bGSSw_l0_maxresdefault", "The Hollywood Reporter")),
     ("But within days, something strange started happening.", P("y_2FS3JAPTKXs_maxres2", NF, "Something <em>strange</em>…"))],
  ]},
  {"q": "How did a fake girl group top the real charts?", "date": "Jul – Dec 2025", "m": (0.6, 6), "pose": "sing_mic", "ko": ("1위", "il-wi", "number one", "Korean moment! 1위. It means number one."), "beats": [
    [("The songs exploded online.", P("y_yebNIHKAC4A_maxres1", SPA, "'Golden' 🎵"))],
    [("Golden entered the Billboard Hot 100 at number eighty-one.", N("#81", "Billboard Hot 100 debut", "y_yebNIHKAC4A_maxres3", SPA)),
     ("Two weeks later, it was in the top ten. Then, it hit number one.", N("#1", "Billboard Hot 100", "y_8y-ViyUk7Dk_maxres3", "The Tonight Show Starring Jimmy Fallon / NBC"))],
    [("HUNTR/X became the first girl group of three or more to top the Hot 100 since Destiny's Child in two thousand one.", P("y_8y-ViyUk7Dk_maxres2", "The Tonight Show Starring Jimmy Fallon / NBC", "First since <em>2001</em>"))],
    [("In its fifth week at number one, Golden passed The Chipmunks and The Archies,", B("5 weeks at <em>#1</em><br>beats The Chipmunks & The Archies", "y_3JTVQTk36R8_maxres1", SPA)),
     ("becoming the longest-leading hit ever by an animated act.", P("og_visitseoul", "Netflix / Visit Seoul", "Longest <em>#1</em> ever by an animated act"))],
    [("In the U.K., it spent ten weeks at number one, the longest run ever for a fictional band.", N("10", "weeks at #1 in the UK", "og_wonend", NF))],
    [("It held number one on the Billboard Global 200 for eighteen weeks,", N("18", "weeks at #1 · Billboard Global 200", "y_yebNIHKAC4A_maxresdefault", NF)),
     ("and topped the charts in more than thirty countries.", N("30+", "countries at #1", "y_HT46zbEQdiw_maxresdefault", NF))],
    [("The soundtrack became the first ever to put four songs in the Hot 100 top ten at the same time.", N("4", "songs in the Hot 100 top 10 at once", "y_oDSEGkT6J-0_maxres2", NF))],
    [("The album itself debuted at number eight on the Billboard 200, the best debut for any soundtrack that year.", N("#8", "Billboard 200 debut · best soundtrack debut of 2025", "y_2FS3JAPTKXs_maxres3", NF))],
    [("Even the villains had a hit.", P("y_2FS3JAPTKXs_maxres1", NF, "Even the <em>villains</em>")),
     ("Your Idol took number one on the U.S. Spotify chart, the highest ever for a male K-pop group.", P("y_cWppAbqm9I8_maxres2", SPA, "'Your Idol' · #1 on U.S. Spotify"))],
    [("And in Korea, Golden scored a perfect all-kill: number one on every major chart at once.", P("y_LTbg4Wps4GE_maxres3", "Seoul Metropolitan Government", "Perfect <em>all-kill</em> in Korea 🇰🇷"))],
  ]},
  {"q": "Why would anyone pay to watch a free movie?", "date": "August 2025", "m": (2, 2.8), "pose": "popcorn_tv", "ko": ("극장", "geuk-jang", "movie theater", "Korean moment! 극장. It means movie theater."), "beats": [
    [("Here's the strangest part. The movie was free on Netflix.", B("It was <em>free</em> on Netflix 📺", "y_6m9Ur3bo7bY_maxres3", "TODAY / NBC"))],
    [("But on August twenty-third, a sing-along version opened in about seventeen hundred theaters for one weekend,", N("1,700", "theaters · one weekend", "y_fGyTN5UjnL4_maxres3", NF)),
     ("the widest release ever for a Netflix film.", B("Netflix's <em>widest</em> theater release ever", "y_fGyTN5UjnL4_maxres2", NF))],
    [("Fans showed up in costumes and sang every word.", P("y_LyM5k1d65TY_maxres1", "RUMCA (fan recording)", "Sing-along screening 🎤"))],
    [("It made an estimated eighteen million dollars, more than any other movie that weekend.", H("h1_thr", "og_thr", "The Hollywood Reporter")),
     ("A first for Netflix.", B("A <em>first</em> for Netflix 🍿", "y_fGyTN5UjnL4_maxres1", NF))],
  ]},
  {"q": "Who are the real voices of HUNTR/X?", "date": "Oct – Nov 2025", "m": (4, 5.9), "pose": "sing_mic", "ko": ("목소리", "mok-so-ri", "voice", "Korean moment! 목소리. It means voice."), "beats": [
    [("Meanwhile, the real singers were becoming stars too.", P("y_z9PusX5ugbI_maxres3", "The Tonight Show Starring Jimmy Fallon / NBC", "The <em>real</em> HUNTR/X"))],
    [("EJAE, the singing voice of Rumi, also co-wrote Golden.", P("y_bFdoLdNUCwg_maxres1", "Billboard", "EJAE · Rumi's voice ✍️ co-wrote 'Golden'"))],
    [("In October, they surprised everyone on Saturday Night Live, singing Golden and How It's Done.", B("Surprise on <em>Saturday Night Live</em> 🎤", "y_z9PusX5ugbI_maxres1", "The Tonight Show Starring Jimmy Fallon / NBC"))],
    [("Days later, they gave their first full live performance on The Tonight Show with Jimmy Fallon.", P("y_bzuUNSf0bCg_maxres2", "The Tonight Show Starring Jimmy Fallon / NBC", "First full live show · Oct 7")),
     ("", P("y_8y-ViyUk7Dk_maxres1", "The Tonight Show Starring Jimmy Fallon / NBC"))],
    [("By Thanksgiving, they were singing Golden at the Macy's parade in New York,", P("y_r7TA1mn91F8_maxres3", "NBC", "Macy's Thanksgiving Day Parade")),
     ("next to a giant Derpy Tiger balloon.", P("y_r7TA1mn91F8_maxres1", "NBC", "Derpy 🐯 balloon"))],
  ]},
  {"q": "Is it really Netflix's biggest movie ever?", "date": "Jul – Dec 2025", "m": (1, 6.8), "pose": "mind_blown", "ko": ("대박", "dae-bak", "awesome! / a huge hit", "Korean moment! 대박. It means awesome, or a huge hit."), "beats": [
    [("And the views kept climbing.", P("y_6m9Ur3bo7bY_maxres2", "TODAY / NBC", "Views keep <em>climbing</em> 📈"))],
    [("In August, it passed Red Notice to become Netflix's most-watched film ever.", H("h1_jad_236", "og_jad_squid", "Korea JoongAng Daily", cnt={"views": 236}))],
    [("In September, it passed Squid Game season one, and became Netflix's most-watched title of all time.", H("h1_jad_squid", "y_6m9Ur3bo7bY_maxres1", "Korea JoongAng Daily · TODAY / NBC", cnt={"views": 266}))],
    [("In its first ninety-one days, it reached three hundred twenty-five point one million views.", N("325.1M", "views in 91 days", "y_PakJTQn7VzY_maxres3", "ABC10", cnt={"views": 325.1})),
     ("By Christmas, it had passed five hundred million.", N("500M+", "views by Christmas 2025", "y_PakJTQn7VzY_maxres2", "ABC10", cnt={"views": 500}))],
    [("And in Seoul, you could feel it.", P("y_LTbg4Wps4GE_maxres1", "Seoul Metropolitan Government", "Meanwhile in <em>Seoul</em>")),
     ("Drone shows lit up the sky over the Han River.", P("y_LTbg4Wps4GE_maxres2", "Seoul Metropolitan Government", "Han River drone show 🚁"))],
    [("The city welcomed one point three six million foreign visitors in July alone, up twenty-three percent.", N("1.36M", "foreign visitors to Seoul · July 2025 (+23%)", "og_ttw", "Travel And Tour World"))],
    [("Even the movie's tiger and magpie, Derpy and Sussie, come from minhwa, Korean folk paintings from the Joseon era.", P("y_bzuUNSf0bCg_maxresdefault", "The Tonight Show Starring Jimmy Fallon / NBC", "Derpy 🐯 & Sussie 🐦 · Korean folk art"))],
    [("And the National Museum of Korea drew more than five million visitors,", N("5M+", "visitors · National Museum of Korea", "c_nmk", "Ethan Doyle White / CC BY-SA 4.0")),
     ("as fans hunted for tiger-and-magpie souvenirs.", H("h1_euronews", "og_animscoop", "Euronews · Animation Scoop"))],
  ]},
  {"q": "How many trophies can one cartoon win?", "date": "Jan – Mar 2026", "m": (7, 9.5), "pose": "trophy", "ko": ("상", "sang", "award, prize", "Korean moment! 상. It means award."), "beats": [
    [("Then came award season.", P("y_TEjd00f3ats_maxres1", "Golden Globes", "Award <em>season</em> 🏆"))],
    [("At the Critics' Choice Awards in January, it won Best Animated Feature and Best Song.", P("y_ztWeRpZvfl0_maxres3", "Critics Choice Association", "Critics' Choice · 2 wins", cnt={"awards": 2}))],
    [("At the Golden Globes, it won the same two.", P("y_TEjd00f3ats_maxres2", "Golden Globes", "Golden Globes · 2 wins", cnt={"awards": 4}))],
    [("At the Annie Awards, the biggest night in animation, it won all ten categories it was nominated in.", P("y_D0NtzXKC-FA_maxres2", "ASIFA-Hollywood", "Annie Awards · <em>10 for 10</em>", cnt={"awards": 14})),
     ("", P("y_c2MmGX8V-ok_maxres1", "ASIFA-Hollywood"))],
    [("On February first, Golden won the Grammy for Best Song Written for Visual Media, the first Grammy ever for a K-pop song.", P("y_YNJicfFVRuM_maxres2", "Recording Academy / GRAMMYs", "First K-pop <em>Grammy</em>", cnt={"awards": 15}))],
    [("Then, on March fifteenth, came the ninety-eighth Academy Awards.", P("y_kes94PVdEBw_maxres3", "ABC / A.M.P.A.S.", "98th Academy Awards · Mar 15, 2026")),
     ("", P("y_kes94PVdEBw_maxres2", "ABC / A.M.P.A.S.", "'Golden' live at the Oscars"))],
    [("Golden won Best Original Song, the first K-pop song ever to win an Oscar.", P("y_2ftx6oQzfoI_maxres2", "ABC / A.M.P.A.S.", "First K-pop <em>Oscar</em>", cnt={"awards": 16}))],
    [("And KPop Demon Hunters won Best Animated Feature.", P("y_w6qKAPC3vqE_maxres2", "ABC / A.M.P.A.S.", "Best Animated Feature 🏆", cnt={"awards": 17}))],
    [("Two Oscars, for a movie that started as a quiet Netflix release.", P("y_X5AqywbwReM_maxres2", "A.M.P.A.S.", "<em>2</em> Oscars"))],
  ]},
  {"q": "Where are the stars now?", "date": "Apr – Oct 2026", "m": (10, 16), "pose": "excited", "beats": [
    [("In April, Billboard honored EJAE, Audrey Nuna and REI AMI as Women of the Year,", P("y_25pyl_wl8ss_maxres1", "Billboard", "Billboard Women in Music 2026")),
     ("the first time a group was honored together.", P("y_9IxVmhL71gc_maxres3", "Billboard", "First <em>group</em> ever honored"))],
    [("The singing voices of the Saja Boys joined Korea's music performers' federation, getting ready for real activities.", H("h1_kt_saja", "y_2FS3JAPTKXs_maxresdefault", "The Korea Times · Netflix"))],
    [("안효섭, the voice of Jinu, now stars as a genius chef in the JTBC drama Final Table, premiering October twenty-fourth.", P("y_3gpEGPKI814_maxresdefault", "JTBC", "Ahn Hyo-seop · 〈Final Table〉 Oct 24")),
     ("", P("y_DVsxZ3a3uk0_maxres1", "JTBC"))],
    [("And KPop Demon Hunters is everywhere: LEGO sets,", P("y_qZthcA53JPM_maxres3", "LEGO", "LEGO 🧱")),
     ("Fortnite skins,", P("y_j50E1JDZrgU_maxres2", "Epic Games / IGN", "Fortnite 🎮")),
     ("Vans sneakers,", P("og_vans", "Vans / House of Heat", "Vans 👟")),
     ("and a new immersive experience opening at Netflix House in Dallas and Philadelphia this November.", P("og_tudumimm", "Netflix Tudum", "Netflix House · Nov 2026"))],
  ]},
  {"q": "What comes next?", "date": "2026 → 2029?", "m": (16, 16.6), "pose": "thinking", "ko": ("속편", "sok-pyeon", "sequel", "Korean moment! 속편. It means sequel."), "beats": [
    [("So, what's next? The sequel is official.", B("The <em>sequel</em> is official", "y_HT46zbEQdiw_maxres1", NF))],
    [("In March, Maggie Kang and Chris Appelhans were confirmed to return to write and direct.", P("y_C7jHSbFCrO4_maxres2", "Collider", "Kang & Appelhans are back"))],
    [("It's been reported for twenty twenty-nine, but Sony Pictures Animation's president has said it may not be finished by then.", N("2029?", "reported release year", "y_mUjA-pNVw1w_maxres2", "CBC News")),
     ("And at FanX, voice actor Alan Lee called every rumored date just rumor and clickbait.", B("“Just <em>rumor and clickbait</em>”<br><small>Alan Lee · FanX Salt Lake</small>", "y_cWppAbqm9I8_maxres1", SPA))],
    [("This time, it's headed to theaters. Netflix co-CEO Ted Sarandos promised a big, broad, global theatrical release.", H("h1_deadline", "y_cWppAbqm9I8_maxres3", "Deadline"))],
    [("And the biggest news for fans: in May, Netflix and AEG Presents announced an official KPop Demon Hunters world concert tour.", H("h1_won", "y_uH5bGSSw_l0_maxres1", "What's on Netflix · The Hollywood Reporter"))],
    [("Cities and dates haven't been announced yet, so for now, fans can only join the waitlist.", P("y_kes94PVdEBw_maxres1", "ABC / A.M.P.A.S.", "World tour · <em>dates TBA</em>"))],
  ]},
]
OUTRO = [
    [("From a quiet Netflix release to two Oscars and a world tour, all in one year.", P("y_56uqT8Hmjo0_maxres2", "ABC / A.M.P.A.S.", "One year. <em>One phenomenon.</em>")),
     ("Which moment was your favorite? Tell me in the comments,", B("Your favorite moment? 👇", "y_3JTVQTk36R8_maxres2", SPA)),
     ("and subscribe to Korean in 60s for more Korea news and Korean you can actually use.", {"k": "O"})],
]
