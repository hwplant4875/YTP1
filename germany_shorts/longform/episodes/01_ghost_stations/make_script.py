"""Beat script for 'Berlin ghost stations' (long-form #1). Writes script.json next to this file."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CR = {m["n"]: m["attribution"].replace("CC-BY-SA 3.0", "CC BY-SA 3.0").replace(", via Wikimedia Commons", "")
      for m in json.load(open(os.path.join(HERE, "assets/commons.json")))}
CR[19] = "Map: Ericmetro / CC0"


def g3(shot, scene="ghost_station", t0=0):
    return {"type": "3d", "scene": scene, "shot": shot, "t0": t0}


def img(n, frm=(1.05, 0.5, 0.5), to=(1.18, 0.5, 0.5), ext="jpg"):
    return {"type": "image", "file": f"assets/c{n:02d}.{ext}", "from": list(frm), "to": list(to), "credit": CR[n]}


def news(file, start, credit="Universal Newsreel, 1961 (public domain)"):
    return {"type": "video", "file": f"assets/{file}.mp4", "start": start, "credit": credit}


N61, N62 = "1961-08-31_Berlin", "1962-08-16_The_Wall"
C61, C62 = "Universal Newsreel, 31 Aug 1961 (public domain)", "Universal Newsreel, 16 Aug 1962 (public domain)"

B = []
def say(line, visual="same", **kw):
    B.append({"say": line, "visual": visual, **kw})


# ---------------------------------------------------------------- cold open
say("1975년, 서베를린.", g3("cab", t0=0), id="intro", text={"kind": "label", "content": "WEST-BERLIN · 1975", "pos": [0.5, 0.86]},
    sfx={"prompt": "subway train rumbling through a dark tunnel, steady rhythm of wheels on rails, interior perspective", "len": 22, "vol": 0.12})
say("당신은 지하철 8호선에 타고 있습니다.")
say("열차가 한 역에 멈추자, 안내 방송이 나옵니다.")
say("서베를린의 마지막 역입니다.", text={"kind": "quote", "content": "„Letzter Bahnhof in Berlin-West“", "pos": [0.5, 0.8]})
say("문이 닫히고, 열차는 다시 어두운 터널로 들어갑니다.")
say("그런데 잠시 후, 열차가 속도를 줄이기 시작합니다.", sfx={"prompt": "old subway train brakes squealing softly, slowing down", "len": 3, "vol": 0.4})
say("창밖으로, 희미한 불빛이 보입니다.")
say("역입니다.")
say("그런데 뭔가 이상합니다.", g3("platform", t0=2))
say("승강장에, 아무도 없습니다.")
say("벽에는 낡은 포스터가 그대로 붙어 있고,")
say("전등은 반쯤 꺼져 있습니다.")
say("아니, 딱 한 사람이 있습니다.", g3("guard", t0=0), sfx={"prompt": "low ominous cinematic hit, deep sub boom", "len": 2, "vol": 0.5})
say("총을 든 군인이, 열차 안의 당신을 똑바로 바라보고 있습니다.")
say("열차는 멈추지 않습니다.", g3("platform", t0=6))
say("그대로 역을 지나, 다시 어둠 속으로 사라집니다.", hold=1.2)
say("방금 지나친 역의 이름은, 로젠탈러 플라츠.", img(3, (1.1, 0.5, 0.45), (1.3, 0.45, 0.42)), text={"kind": "label", "content": "U-Bahnhof Rosenthaler Platz", "pos": [0.5, 0.86]})
say("이 역에서는 무려 28년 동안, 단 한 명의 승객도 내리지 못했습니다.")
say("베를린 지하에는, 이런 역이 16개나 있었습니다.", g3("reveal", "cross_section"))
say("열차는 매일 그 앞을 지나갔지만, 절대 멈추지 않았죠.")
say("사람들은 이곳을, 이렇게 불렀습니다.")
B.append({"visual": {"type": "black"}, "hold": 3.2, "text": {"kind": "title", "content": "베를린의 유령역", "pos": [0.5, 0.47]},
          "sfx": {"prompt": "deep cinematic impact boom with long dark reverb tail", "len": 4, "vol": 0.6}})

# ---------------------------------------------------------------- act 1: the night the city split
say("이 역들은 어떻게 만들어졌고, 그 안에서는 무슨 일이 있었을까요?", g3("pass", "cross_section"))
say("그리고 이 유령역을 통해 탈출한 남자는, 어떻게 살아남았을까요?")
say("오늘은 베를린 지하에 숨겨져 있던, 28년의 비밀을 따라가 보겠습니다.", hold=0.8)
say("장벽이 생기기 전, 베를린은 참 이상한 도시였습니다.", news(N62, 9, C62), id="act1")
say("전쟁에서 진 독일의 수도는, 승전국들이 나눠 가졌습니다.")
say("동쪽은 소련, 서쪽은 미국과 영국, 프랑스.")
say("하지만 사람들은, 지하철 한 번이면 동과 서를 자유롭게 오갔습니다.")
say("동쪽에 살면서 서쪽으로 출근하는 사람도 수만 명이었죠.")
say("문제는, 한번 서쪽으로 간 사람들이 돌아오지 않았다는 겁니다.")
say("1961년 여름에는, 하루에도 수천 명이 동독을 떠나고 있었습니다.")
say("그리고 1961년 8월 13일, 일요일 새벽.", news(N61, 57.5, C61), text={"kind": "year", "content": "1961"})
say("동독은 베를린을, 하룻밤 사이에 둘로 갈라버립니다.")
say("철조망이 깔리고, 벽돌이 쌓였습니다.", news(N61, 63, C61))
say("국경에 닿은 건물들은, 창문까지 벽돌로 막혔습니다.", news(N62, 36, C62))
say("어제까지 걸어서 건너던 길이, 하루아침에 국경이 된 겁니다.", news(N61, 87, C61))
say("가족과 친구들은, 철조망 너머로 손만 흔들 수 있었습니다.", news(N61, 98, C61), hold=1.5)
say("그런데, 동독에게는 골치 아픈 문제가 하나 남아 있었습니다.", g3("pass", "cross_section"))
say("땅 위는 벽으로 막을 수 있었지만, 땅 아래는 아니었거든요.")
say("베를린의 지하철은, 도시가 갈라지기 수십 년 전에 만들어졌습니다.")
say("그래서 몇몇 노선은 서베를린에서 출발해, 동베를린 땅 밑을 지나, 다시 서베를린으로 돌아왔습니다.",
    img(19, (1.0, 0.55, 0.5), (1.25, 0.62, 0.55), "png"))
say("지하철 6호선과 8호선, 그리고 남북을 잇는 S반 터널이었죠.")
say("서베를린 사람들에게는, 도시의 남과 북을 잇는 꼭 필요한 노선이었습니다.")
say("북쪽의 베딩에서 남쪽의 크로이츠베르크로 가려면, 이 지하철이 가장 빠른 길이었으니까요.")
say("그림으로 보면 이렇습니다.", g3("reveal", "cross_section", t0=0))
say("땅 위에는 장벽과 감시탑, 그리고 죽음의 띠라 불린 무인지대가 있습니다.")
say("그 아래 몇 미터의 흙을 지나면,")
say("바로 그 밑을, 서베를린의 지하철이 지나가고 있었던 거죠.", hold=0.8)
say("그래서 동독은 노선을 끊는 대신, 아주 기묘한 방법을 택합니다.", g3("cab", t0=10))
say("열차가 지나가는 건 허락하되, 동베를린 쪽 역에서는 절대 서지 못하게 한 겁니다.")
say("그런데, 이 이야기에서 가장 이상한 부분은 따로 있습니다.")
say("서베를린이, 이 터널을 쓰는 대가로 동독에 매달 돈을 내고 있었다는 거죠.")
say("그 이야기는 조금 뒤에 하고, 먼저 유령역 안으로 들어가 보겠습니다.")

# ---------------------------------------------------------------- act 2: anatomy of a ghost station
say("1961년 8월 13일, 역들은 하룻밤 사이에 유령이 되었습니다.", news(N62, 18, C62), id="act2", text={"kind": "label", "content": "Bernauer Straße", "pos": [0.5, 0.86]})
say("8호선에서는 베르나우어 거리, 로젠탈러 플라츠, 바인마이스터 거리, 알렉산더 광장, 얀노비츠브뤼케, 하인리히 하이네 거리.",
    img(19, (1.25, 0.72, 0.5), (1.4, 0.72, 0.62), "png"))
say("6호선에서는 슈바르츠코프 거리, 노르트반호프, 오라니엔부르거 토어, 프란최지셰 거리, 그리고 슈타트미테.", img(19, (1.3, 0.35, 0.45), (1.45, 0.4, 0.6), "png"))
say("S반 터널에서는 노르트반호프, 오라니엔부르거 거리, 운터 덴 린덴, 포츠담 광장.", img(19, (1.3, 0.5, 0.5), (1.4, 0.45, 0.8), "png"))
say("여기에 지상의 보른홀머 거리역까지, 모두 16곳이었습니다.")
say("지상의 입구는 벽으로 막히고, 지하철 표지판은 떼어졌습니다.", img(2, (1.08, 0.5, 0.42), (1.2, 0.55, 0.45)))
say("어떤 입구는 아예 흙으로 덮여서, 거리 풍경에서 사라져 버렸죠.")
say("동베를린 지도에서는, 이 역들은 물론 노선까지 통째로 지워졌습니다.", news(N62, 30, C62), text={"kind": "label", "content": "Potsdamer Platz", "pos": [0.5, 0.86]})
say("동베를린 사람들 대부분은, 발밑으로 서쪽 열차가 지나간다는 사실조차 잊고 살았을 겁니다.")
say("노르트반호프 역에서는, 동과 서를 나누기 위해 벽만 여섯 겹을 세웠습니다.")
say("거기에 철망 울타리까지 더해서요.")
say("반대로, 서베를린 지하철 노선도에는 이런 문구가 적혀 있었습니다.", {"type": "black"})
B.append({"visual": "same", "hold": 3.4, "text": {"kind": "quote", "content": "„Bahnhöfe, auf denen die Züge nicht halten“\\N\\N열차가 서지 않는 역", "pos": [0.5, 0.5]}})
say("그렇다면, 승강장 안은 어땠을까요?", g3("platform", t0=0))
say("조명은 거의 꺼진 채, 희미한 불빛만 남았습니다.")
say("시간은 1961년에 멈춰 있었습니다.")
say("벽의 광고와 간판들은, 28년 동안 한 번도 바뀌지 않았죠.")
say("그리고 그 어둠 속에, 국경수비대가 있었습니다.", g3("guard", t0=4))
say("경비병들은 2인 1조로, 잠긴 감시실 안에서 작은 창틈으로 승강장을 지켜봤습니다.")
say("교대 순서는 수시로 바뀌었고, 불시 점검도 있었습니다.")
say("감시하는 사람조차, 감시를 받았던 겁니다.", sfx={"prompt": "single heavy metal door closing with echo in an empty concrete hall", "len": 2.5, "vol": 0.45})
say("잠깐, 그 경비병의 입장이 되어 볼까요?", g3("thumb", t0=0))
say("하루 종일 빛도 들지 않는 승강장에서, 몇 분마다 서쪽 열차가 지나갑니다.")
say("창문 너머로 보이는 건, 서베를린 사람들의 얼굴입니다.")
say("신문을 읽는 사람, 졸고 있는 사람, 창밖의 당신을 신기하게 쳐다보는 사람.")
say("손만 뻗으면 닿을 것 같은 거리지만, 그 열차에 올라타는 순간 당신은 탈영병이 됩니다.")
say("동독이 경비병들을 서로 감시하게 만든 이유가, 바로 이것이었습니다.")
say("승강장 가장자리 아래에는 철조망이 깔렸고,", g3("platform", t0=12))
say("비상구는 용접으로 막혔습니다.")
say("선로 쪽으로는 셔터가 내려졌고, 1980년대에는 빛 감지 장치까지 설치됩니다.")
say("그리고 터널 벽에는, 흰 선 하나가 그어져 있었습니다.", g3("border", t0=0), sfx={"prompt": "eerie low drone swell, tension", "len": 4, "vol": 0.35})
say("여기서부터 동독이라는, 국경선이었죠.", hold=1.2)
say("서베를린 열차는 이 구간을, 시속 15킬로미터로 천천히 지나가야 했습니다.", g3("cab", t0=22))
say("그런데 어느 날, 한 동독 경찰관이 지나가는 열차에 뛰어오르려 한 사건이 벌어집니다.")
say("그 뒤로 제한 속도는, 시속 25킬로미터로 올라갑니다.")
say("천천히 달리면, 누군가 올라탈 수 있었으니까요.")

# ---------------------------------------------------------------- act 3: the escape
say("그렇다면, 유령역의 터널로 탈출한 사람은 정말 없었을까요?", g3("border", t0=4), id="act3")
say("있었습니다. 다만, 손에 꼽을 정도였죠.")
say("그중 가장 대담했던 사람은, 1980년 3월의 디터 벤트입니다.", {"type": "black"}, text={"kind": "label", "content": "DIETER WENDT · 1980", "pos": [0.5, 0.5]})
say("스물여덟 살, 동베를린의 신호 기술자였습니다.")
say("그는 지하철 터널의 신호 장치를, 누구보다 잘 알았습니다.", g3("cab", t0=0))
say("매일 그 터널에서 일했으니까요.")
say("그리고 계획을 세웁니다.")
say("신호 장치가 고장 난 것처럼 꾸미는 거였죠.")
say("고장이 나면, 기술자는 터널 안으로 들어갈 수 있었습니다.")
say("장소는 얀노비츠브뤼케 역 근처의 터널.", text={"kind": "label", "content": "Jannowitzbrücke", "pos": [0.5, 0.86]})
say("서베를린 열차가 다가오자, 그는 선로 옆에서 열차를 멈춰 세웁니다.", sfx={"prompt": "subway train emergency braking, loud metal screech in a tunnel", "len": 3, "vol": 0.5})
say("놀란 기관사가 문을 열고, 외칩니다.")
B.append({"visual": {"type": "black"}, "hold": 2.2, "text": {"kind": "quote", "content": "„Rein und hinlegen!“\\N\\N타요, 그리고 엎드려요!", "pos": [0.5, 0.5]}})
say("열차는 다시 출발했고, 몇 분 뒤 서베를린에 도착합니다.", g3("platform", t0=4),
    sfx={"prompt": "subway train accelerating away, doors closing beep", "len": 4, "vol": 0.4})
say("동독 사람이, 유령역의 터널을 지나 자유를 찾은 순간이었습니다.", hold=1.2)
say("하지만 이런 행운은 드물었습니다. 대부분의 시도는, 국경선에 닿기도 전에 끝났죠.")
say("유령역은 그렇게, 28년 동안 아무에게도 문을 열어주지 않았습니다.")

# ---------------------------------------------------------------- act 4: Friedrichstrasse and the money
say("이런 독일 이야기가 재미있으셨다면, 구독 버튼 한 번 눌러 주세요.", g3("cab", t0=40), id="act4")
say("그런데, 동베를린 땅 밑의 역들 가운데 딱 한 곳에서만 열차가 멈췄습니다.", img(13, (1.05, 0.5, 0.5), (1.2, 0.55, 0.5)))
say("바로, 프리드리히 거리역입니다.", text={"kind": "label", "content": "Bahnhof Friedrichstraße", "pos": [0.5, 0.86]})
say("이곳은 서베를린 사람들이 검문 없이 열차를 갈아타는 환승역이었고,", img(11, (1.08, 0.5, 0.44), (1.2, 0.45, 0.42)))
say("동시에, 동독으로 들어가는 국경 검문소였습니다.", img(7, (1.05, 0.5, 0.5), (1.18, 0.5, 0.55)))
say("한 역 안에, 두 나라가 벽 하나를 사이에 두고 있었던 겁니다.")
say("동독에 사는 가족을 만나러 온 사람들은, 이곳에서 긴 검문을 받았습니다.", img(9, (1.1, 0.5, 0.42), (1.22, 0.5, 0.4)))
say("그리고 헤어질 때 눈물을 흘리던 출국장은, 훗날 이렇게 불리게 됩니다.", img(17, (1.0, 0.5, 0.5), (1.12, 0.52, 0.48)))
say("눈물의 궁전.", text={"kind": "title", "content": "눈물의 궁전", "pos": [0.5, 0.47]})
say("이 역에는, 이상한 가게도 하나 있었습니다.", img(8, (1.08, 0.5, 0.4), (1.2, 0.46, 0.38)))
say("서독 마르크로만 물건을 파는 가게, 인터숍입니다.")
say("서베를린 사람들은 담배와 술을 싸게 사려고, 일부러 동독 땅 밑의 이 역까지 지하철을 타고 왔습니다.")
say("새벽 1시가 넘어 술에 취한 쇼핑객들을 싣고 돌아가는 마지막 열차에는, 별명까지 붙었죠.")
say("넝마주이.", text={"kind": "quote", "content": "„Lumpensammler“", "pos": [0.5, 0.8]})
say("하지만, 이 역이 늘 평화로웠던 건 아닙니다.", img(6, (1.1, 0.5, 0.42), (1.22, 0.5, 0.4)))
say("1974년 3월, 한 폴란드 남성이 서쪽으로 가겠다며 대사관에서 가짜 폭탄으로 협박합니다.")
say("동독은 출국을 허락하는 척했습니다.")
say("그리고 그가 이 역의 검문을 통과한 직후, 숨어 있던 슈타지 요원이 그를 쏩니다.")
say("서베를린까지는, 불과 몇 걸음이었습니다.", hold=1.5)
say("자, 이제 아까 말한 돈 이야기입니다.", g3("pass", "cross_section"))
say("서베를린은, 동베를린 땅 밑으로 지하철을 지나가게 하는 대가로,")
say("1963년부터 매달, 동독에 통과료를 냈습니다.", text={"kind": "year", "content": "1963"})
say("처음엔 한 달에 약 18만 마르크.")
say("1989년에는, 거의 50만 마르크까지 올라갔습니다.", text={"kind": "label", "content": "181,132 DM  →  495,756 DM / Monat", "pos": [0.5, 0.86]})
say("1년이면, 600만 마르크에 가까운 돈입니다.")
say("자기 도시의 지하철을 달리기 위해, 장벽을 세운 나라에 돈을 낸 셈이죠.")
say("더 황당한 건, S반이었습니다.", img(18, (1.05, 0.5, 0.5), (1.18, 0.6, 0.5)))
say("서베를린을 달리는 S반도, 운영은 동독 국영철도가 하고 있었거든요.")
say("서베를린 시민들은 분노했고, 보이콧을 시작합니다.")
say("S반을 타면, 그 요금이 철조망 값이 된다는 이유였죠.", text={"kind": "quote", "content": "„Der S-Bahn-Fahrer zahlt den Stacheldraht“", "pos": [0.5, 0.8]})
say("하루 50만 명이던 승객은, 5만 명 아래로 떨어졌습니다.")
say("사실 이 S반 터널이 유령이 된 건, 처음이 아니었습니다.", img(14, (1.05, 0.5, 0.5), (1.2, 0.5, 0.55)))
say("1945년 5월 2일, 전쟁 막바지에 터널이 폭파되면서, 물에 잠겨버린 적이 있었죠.")
say("한 번은 전쟁 때문에, 또 한 번은 장벽 때문에, 이 터널은 두 번이나 죽었던 겁니다.")

# ---------------------------------------------------------------- act 5: 1989
say("그렇게, 28년이 흘렀습니다.", g3("platform", t0=8), id="act5")
say("1989년 11월 9일 밤, 베를린 장벽이 무너집니다.", {"type": "black"}, text={"kind": "year", "content": "1989"},
    sfx={"prompt": "distant crowd cheering at night, celebration, fireworks far away", "len": 5, "vol": 0.35})
say("그날 밤 가장 먼저 열린 국경은, 보른홀머 거리 검문소였습니다.")
say("그리고 그 다리 바로 옆에 있던 역이, 바로 유령역 보른홀머 거리였죠.")
say("단 이틀 뒤인 11월 11일.", img(1, (1.05, 0.5, 0.5), (1.2, 0.42, 0.5)))
say("얀노비츠브뤼케 역에, 28년 만에 처음으로 열차가 멈춰 섭니다.")
say("행선지 표지판은 손으로 쓴 임시 표지판이었습니다.")
say("서베를린까지 요금은, 2마르크 70페니히.")
say("문이 열리자, 승강장은 사람들로 가득 찼습니다.", hold=1.2)
say("유령역들은 그렇게, 하나씩 다시 문을 열었습니다.", img(5, (1.05, 0.5, 0.45), (1.16, 0.5, 0.42)))
say("1989년 12월에는 로젠탈러 플라츠가,", img(3, (1.2, 0.45, 0.42), (1.08, 0.5, 0.45)))
say("28년 만에 다시 불이 켜진 그 승강장은, 정말 시간이 멈춘 것 같았다고 합니다.")
say("1990년 봄에는 베르나우어 거리가 다시 열렸고,", img(4, (1.05, 0.5, 0.5), (1.15, 0.5, 0.45)))
say("마지막 유령역인 포츠담 광장역이 다시 열린 건, 1992년 3월이었습니다.", news(N62, 30, C62))
say("오늘 베를린 지하철을 타면, 이 역들은 그저 평범한 역처럼 보입니다.", img(16, (1.05, 0.5, 0.5), (1.15, 0.5, 0.5)))
say("하지만 노르트반호프 역에 가면, 아직도 그 시절의 흔적을 볼 수 있습니다.", img(20, (1.05, 0.5, 0.5), (1.18, 0.4, 0.5)))
say("눈물의 궁전도 지금은 박물관이 되어, 분단의 기억을 전하고 있죠.", img(17, (1.12, 0.52, 0.48), (1.0, 0.5, 0.5)))
say("만약 여러분이 베를린에 간다면, 8호선을 타고 로젠탈러 플라츠를 지나 보세요.", g3("platform", t0=14))
say("28년 동안 열차가 서지 않던 역.")
say("그리고 아무도 내리지 못했던, 바로 그 승강장입니다.", hold=2.0)

# ---------------------------------------------------------------- teaser
say("그런데, 장벽 밑에는 지하철 말고도 또 다른 터널이 있었습니다.", g3("reveal", "cross_section", t0=2), id="outro")
say("1962년, 한 미국 방송사가 몰래 돈을 대고, 땅굴을 파는 대학생들을 촬영합니다.")
say("그리고 그 땅굴로, 29명이 탈출하죠.")
say("그 이야기는, 다음 영상에서 풀어보겠습니다.", {"type": "black"}, hold=2.5,
    text={"kind": "title", "content": "다음 이야기 · 터널 29", "pos": [0.5, 0.47]})
B.append({"visual": g3("platform", t0=20), "hold": 9.0})   # end screen: subscribe + next video cards go here

spec = {
    "voice": {"tempo": 1.3, "emotion": "normal"},
    "gap": 0.05,
    "music": [
        {"file": "music/m1_intro.mp3", "from": "intro", "to": "act1", "vol": 0.20},
        {"file": "music/m2_investigate.mp3", "from": "act1", "to": "act3", "vol": 0.15},
        {"file": "music/m3_escape.mp3", "from": "act3", "to": "act4", "vol": 0.17},
        {"file": "music/m2_investigate.mp3", "from": "act4", "to": "act5", "vol": 0.14, "offset": 0},
        {"file": "music/m4_resolution.mp3", "from": "act5", "to": "end", "vol": 0.18},
    ],
    "beats": B,
}
json.dump(spec, open(os.path.join(HERE, "script.json"), "w"), ensure_ascii=False, indent=1)
print(len(B), "beats,", sum(len(b.get("say", "")) for b in B), "chars")
