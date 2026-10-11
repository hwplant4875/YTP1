# Compound-word puzzles: (meaning, word, romanization, pose, ((emoji, part meaning, part), (emoji, part meaning, part)))
CHAPTERS = [
 ("Body & Nature", "🌿", "m", [
  ("Tears.", "눈물", "nun-mul", "tissue_cry", (("👁️", "eye", "눈"), ("💧", "water", "물"))),
  ("Runny nose.", "콧물", "kon-mul", "nervous_sweat", (("👃", "nose", "코"), ("💧", "water", "물"))),
  ("Wrist.", "손목", "son-mok", "raise_hand", (("✋", "hand", "손"), ("🦒", "neck", "목"))),
  ("Ankle.", "발목", "bal-mok", "jump", (("🦶", "foot", "발"), ("🦒", "neck", "목"))),
  ("Finger.", "손가락", "son-kka-rak", "point_idea", (("✋", "hand", "손"), ("🧵", "strand", "가락"))),
  ("Toe.", "발가락", "bal-kka-rak", "shocked", (("🦶", "foot", "발"), ("🧵", "strand", "가락"))),
  ("Snowman.", "눈사람", "nun-sa-ram", "cold_scarf", (("❄️", "snow", "눈"), ("🧍", "person", "사람"))),
  ("Flame.", "불꽃", "bul-kkot", "clap_confetti", (("🔥", "fire", "불"), ("🌸", "flower", "꽃"))),
  ("Night sky.", "밤하늘", "bam-ha-neul", "sleeping", (("🌙", "night", "밤"), ("☁️", "sky", "하늘"))),
  ("Fish.", "물고기", "mul-kko-gi", "mind_blown", (("💧", "water", "물"), ("🥩", "meat", "고기")))]),
 ("Food", "🍚", "y", [
  ("Beef.", "소고기", "so-go-gi", "rice_bowl", (("🐄", "cow", "소"), ("🥩", "meat", "고기"))),
  ("Pork.", "돼지고기", "dwae-ji-go-gi", "laugh_flap", (("🐷", "pig", "돼지"), ("🥩", "meat", "고기"))),
  ("Chicken meat.", "닭고기", "dak-kko-gi", "excited", (("🐔", "chicken", "닭"), ("🥩", "meat", "고기"))),
  ("Bibimbap, mixed rice.", "비빔밥", "bi-bim-bap", "smug", (("🥄", "mixed", "비빔"), ("🍚", "rice", "밥"))),
  ("Gimbap, seaweed rice roll.", "김밥", "gim-bap", "kimbap", (("🟩", "seaweed", "김"), ("🍚", "rice", "밥"))),
  ("Fried rice.", "볶음밥", "bo-kkeum-bap", "thumbs_up", (("🍳", "stir-fried", "볶음"), ("🍚", "rice", "밥"))),
  ("Breakfast.", "아침밥", "a-chim-bap", "yawn", (("🌅", "morning", "아침"), ("🍚", "meal", "밥"))),
  ("Eating alone.", "혼밥", "hon-bap", "lying_flat", (("🧍", "alone", "혼"), ("🍚", "meal", "밥"))),
  ("Chicken and beer!", "치맥", "chi-maek", "cheers", (("🍗", "chicken", "치킨"), ("🍺", "beer", "맥주"))),
  ("Mukbang, an eating show.", "먹방", "meok-bang", "popcorn_tv", (("😋", "eat", "먹다"), ("📺", "broadcast", "방송")))]),
 ("Places", "🏙️", "b", [
  ("Bathroom.", "화장실", "hwa-jang-sil", "shy_cover", (("💄", "makeup", "화장"), ("🚪", "room", "실"))),
  ("Karaoke.", "노래방", "no-rae-bang", "sing_mic", (("🎤", "song", "노래"), ("🚪", "room", "방"))),
  ("Korean spa.", "찜질방", "jjim-jil-bang", "hot_fan", (("♨️", "hot steam", "찜질"), ("🚪", "room", "방"))),
  ("Internet cafe.", "피시방", "pi-si-bang", "headphones", (("💻", "PC", "피시"), ("🚪", "room", "방"))),
  ("Hospital.", "병원", "byeong-won", "nervous_sweat", (("🤒", "sickness", "병"), ("🏢", "place", "원"))),
  ("Library.", "도서관", "do-seo-gwan", "glasses_study", (("📚", "books", "도서"), ("🏛️", "building", "관"))),
  ("Movie theater.", "영화관", "yeong-hwa-gwan", "popcorn_tv", (("🎬", "movie", "영화"), ("🏛️", "building", "관"))),
  ("Post office.", "우체국", "u-che-guk", "writing", (("✉️", "mail", "우체"), ("🏢", "office", "국"))),
  ("Parking lot.", "주차장", "ju-cha-jang", "map_lost", (("🚗", "parking", "주차"), ("📍", "place", "장"))),
  ("Subway.", "지하철", "ji-ha-cheol", "bus", (("⬇️", "underground", "지하"), ("🛤️", "rail", "철")))]),
 ("Life & Love", "💌", "p", [
  ("Airplane.", "비행기", "bi-haeng-gi", "suitcase", (("🕊️", "flying", "비행"), ("⚙️", "machine", "기"))),
  ("Car.", "자동차", "ja-dong-cha", "dash", (("🔄", "self-moving", "자동"), ("🚙", "vehicle", "차"))),
  ("Cell phone.", "휴대폰", "hyu-dae-pon", "phone_chat", (("👜", "carry", "휴대"), ("📱", "phone", "폰"))),
  ("Birthday.", "생일", "saeng-il", "party_cake", (("👶", "birth", "생"), ("📅", "day", "일"))),
  ("Sunday.", "일요일", "i-ryo-il", "spin", (("☀️", "sun", "일"), ("📅", "weekday", "요일"))),
  ("Monday.", "월요일", "wo-ryo-il", "crying", (("🌙", "moon", "월"), ("📅", "weekday", "요일"))),
  ("First love.", "첫사랑", "cheot-sa-rang", "love_heart", (("1️⃣", "first", "첫"), ("💗", "love", "사랑"))),
  ("A crush, one-sided love.", "짝사랑", "jjak-sa-rang", "curtain_peek", (("🧦", "one of a pair", "짝"), ("💗", "love", "사랑"))),
  ("Boyfriend.", "남자친구", "nam-ja-chin-gu", "shy_cover", (("👨", "man", "남자"), ("🤝", "friend", "친구"))),
  ("Super fun!", "꿀잼", "kkul-jaem", "laugh_tears", (("🍯", "honey", "꿀"), ("🎉", "fun", "재미")))]),
]
NUM = ["one", "two", "three", "four", "five"]
HOOK = "Korean words are like LEGO. Snap two small words together, and you get a brand new one. Can you guess them before I do?"
OUTRO = "Which one surprised you the most? Tell me in the comments, and subscribe for more Korean!"
HOOK_HTML = "Korean Words Are<br>Like <span class=\"c-y\">LEGO</span> 🧩"
OUTRO_HTML = "Which one surprised<br>you the most? 👇"
HOOK_POSE = "point_idea"
