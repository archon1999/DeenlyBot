"""Original concise study notes checked against the Quranic Arabic Corpus.

These are linguistic notes and educational meaning paraphrases, not a tafsir,
fatwa, scholarly certification or a replacement for a qualified teacher.
Arabic text of the five existing chapters is reused without changing their IDs.
Only selected vocabulary is annotated; we do not invent analyses for other words.
Source pages are kept on every sidecar in the database.
"""

from django.db import transaction

from .models import (
    QuranAnalysisTranslation,
    QuranPassage,
    QuranPassageAnalysis,
    QuranPassageTranslation,
    QuranVerse,
    QuranVerseTranslation,
    QuranWord,
    QuranWordTranslation,
    ReligiousSource,
)

LANGUAGES = ("uz", "ru", "en")

# Each row: Arabic | Uzbek/English phonetic aid | Russian phonetic aid | Uzbek,
# Russian and English concise meanings. Phonetic aids do not replace listening.
NEW_CHAPTERS = {
    103: (
        "al-asr",
        ("Asr surasi", "Сура Аль-Аср", "Surah Al-Asr"),
        """
وَالْعَصْرِ|Val-'asr|Валь-'аср|Vaqtga qasam.|Клянусь временем.|By time.
إِنَّ الْإِنْسَانَ لَفِي خُسْرٍ|Innal-insana lafiy xusr|Инналь-инсана ляфи хуср|Albatta, inson ziyon ichidadir.|Воистину, человек в убытке.|Humanity is indeed in loss.
إِلَّا الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ وَتَوَاصَوْا بِالْحَقِّ وَتَوَاصَوْا بِالصَّبْرِ|Illallazina amanu va 'amilus-solihati va tavasov bil-haqqi va tavasov bis-sobr|Илляллязина аману ва 'амилюс-салихати ва тавасау биль-хакки ва тавасау бис-сабр|Faqat iymon keltirgan, yaxshi amallar qilgan, bir-birini haqqa va sabrga chaqirganlar bundan mustasno.|Кроме тех, кто уверовал, совершал добрые дела и побуждал друг друга к истине и терпению.|Except those who believe, do good deeds, and encourage one another to truth and patience.
""",
    ),
    108: (
        "al-kawthar",
        ("Kavsar surasi", "Сура Аль-Каусар", "Surah Al-Kawthar"),
        """
إِنَّا أَعْطَيْنَاكَ الْكَوْثَرَ|Inna a'toynakal-kavsar|Инна а'тайнакаль-каусар|Albatta, Biz senga Kavsarni berdik.|Воистину, Мы даровали тебе Каусар.|We have indeed given you al-Kawthar.
فَصَلِّ لِرَبِّكَ وَانْحَرْ|Fa solli li-Robbika vanhar|Фа салли ли-Раббика ванхар|Bas, Robbing uchun namoz o‘qi va qurbonlik qil.|Так молись своему Господу и приноси жертву.|So pray to your Lord and offer sacrifice.
إِنَّ شَانِئَكَ هُوَ الْأَبْتَرُ|Inna shani'aka huval-abtar|Инна шани'ака хуваль-абтар|Albatta, seni yomon ko‘ruvchining o‘zi uzilgandir.|Именно ненавидящий тебя останется отрезанным.|The one who hates you is the one cut off.
""",
    ),
    110: (
        "an-nasr",
        ("Nasr surasi", "Сура Ан-Наср", "Surah An-Nasr"),
        """
إِذَا جَاءَ نَصْرُ اللَّهِ وَالْفَتْحُ|Iza ja'a nasrullohi val-fath|Иза джа'а насруллахи валь-фатх|Allohning yordami va g‘alaba kelganda,|Когда придут помощь Аллаха и победа,|When Allah's help and the victory arrive,
وَرَأَيْتَ النَّاسَ يَدْخُلُونَ فِي دِينِ اللَّهِ أَفْوَاجًا|Va ro'aytan-nasa yadxuluna fiy dinillahi afvaja|Ва ра'айтан-наса ядхулюна фи динилляхи афваджа|va odamlar Allohning diniga to‘p-to‘p kirayotganini ko‘rganingda,|и ты увидишь людей, входящих в религию Аллаха толпами,|and you see people entering Allah's religion in groups,
فَسَبِّحْ بِحَمْدِ رَبِّكَ وَاسْتَغْفِرْهُ إِنَّهُ كَانَ تَوَّابًا|Fa sabbih bi-hamdi Robbika vastag‘firhu innahu kana tavvaba|Фа саббих би-хамди Раббика вастагфирху иннаху кана тавваба|Robbingga hamd bilan tasbeh ayt va Undan mag‘firat so‘ra. U tavbalarni ko‘p qabul qiluvchidir.|прославляй Господа с хвалой и проси у Него прощения. Он принимает покаяние.|glorify your Lord with praise and ask His forgiveness. He is ever accepting of repentance.
""",
    ),
    105: (
        "al-fil",
        ("Fil surasi", "Сура Аль-Филь", "Surah Al-Fil"),
        """
أَلَمْ تَرَ كَيْفَ فَعَلَ رَبُّكَ بِأَصْحَابِ الْفِيلِ|Alam taro kayfa fa'ala Robbuka bi-ashabil-fil|Алям тара кайфа фа'аля Раббука би-асхабиль-филь|Robbing fil egalariga qanday muomala qilganini ko‘rmadingmi?|Разве ты не видел, как твой Господь поступил с людьми слона?|Have you not seen how your Lord dealt with the people of the elephant?
أَلَمْ يَجْعَلْ كَيْدَهُمْ فِي تَضْلِيلٍ|Alam yaj'al kaydahum fiy tazlil|Алям ядж'аль кайдахум фи тадлиль|U ularning makrini barbod qilmadimi?|Разве Он не расстроил их замысел?|Did He not make their plan fail?
وَأَرْسَلَ عَلَيْهِمْ طَيْرًا أَبَابِيلَ|Va arsala 'alayhim toyron ababil|Ва арсаля 'аляйхим тайран абабиль|Ularning ustiga to‘p-to‘p qushlarni yubordi.|Он направил против них птиц стаями,|He sent birds against them in flocks,
تَرْمِيهِمْ بِحِجَارَةٍ مِنْ سِجِّيلٍ|Tarmihim bi-hijarotim min sijjil|Тармихим би-хиджаратин мин сиджжиль|ular pishgan loydan bo‘lgan toshlarni otar edi.|которые бросали в них камни из обожжённой глины,|striking them with stones of baked clay,
فَجَعَلَهُمْ كَعَصْفٍ مَأْكُولٍ|Fa ja'alahum ka'asfim ma'kul|Фа джа'аляхум ка'асфин ма'куль|U ularni yeb tashlangan somondek qilib qo‘ydi.|и сделал их подобными съеденной соломе.|and made them like chewed-up straw.
""",
    ),
    106: (
        "quraysh",
        ("Quraysh surasi", "Сура Курайш", "Surah Quraysh"),
        """
لِإِيلَافِ قُرَيْشٍ|Li-ilafi Quraysh|Ли-иляфи Курайш|Qurayshning ulfatlashuvi uchun,|Ради единения курайшитов,|For the accustomed security of Quraysh,
إِيلَافِهِمْ رِحْلَةَ الشِّتَاءِ وَالصَّيْفِ|Ilafihim rihlatash-shita'i vas-soyf|Иляфихим рихляташ-шита'и вас-сайф|ularning qish va yoz safarlariga ulfatlashuvi uchun,|их привычки к зимним и летним поездкам,|their accustomed journeys in winter and summer,
فَلْيَعْبُدُوا رَبَّ هَٰذَا الْبَيْتِ|Fal-ya'budu Robba hazal-bayt|Фаль-я'буду Рабба хазаль-байт|ular shu Uyning Robbisiga ibodat qilsinlar.|пусть они поклоняются Господу этого Дома,|let them worship the Lord of this House,
الَّذِي أَطْعَمَهُمْ مِنْ جُوعٍ وَآمَنَهُمْ مِنْ خَوْفٍ|Allaziy at'amahum min ju'iv va amanahum min xovf|Аллязи ат'амахум мин джу'ин ва аманахум мин хауф|U ularni ochlikdan to‘ydirdi va qo‘rquvdan omon qildi.|Который накормил их после голода и избавил от страха.|who fed them against hunger and gave them safety against fear.
""",
    ),
}

ENGLISH_TRANSCRIPTIONS = {
    103: (
        "Wal-'asr",
        "Innal-insana lafi khusr",
        "Illal-ladhina amanu wa 'amilus-salihati wa tawasaw bil-haqqi wa tawasaw bis-sabr",
    ),
    108: ("Inna a'taynaka-l-kawthar", "Fa salli li-Rabbika wanhar", "Inna shani'aka huwa-l-abtar"),
    110: (
        "Idha ja'a nasrullahi wal-fath",
        "Wa ra'aytan-nasa yadkhuluna fi dinillahi afwaja",
        "Fa sabbih bi-hamdi Rabbika wastaghfirhu innahu kana tawwaba",
    ),
    105: (
        "Alam tara kayfa fa'ala Rabbuka bi-ashabi-l-fil",
        "Alam yaj'al kaydahum fi tadlil",
        "Wa arsala 'alayhim tayran ababil",
        "Tarmihim bi-hijaratin min sijjil",
        "Fa ja'alahum ka'asfin ma'kul",
    ),
    106: (
        "Li-ilafi Quraysh",
        "Ilafihim rihlata-sh-shita'i wa-s-sayf",
        "Fal-ya'budu Rabba hadha-l-bayt",
        "Alladhi at'amahum min ju'in wa amanahum min khawf",
    ),
}

EXISTING_MEANINGS = {
    1: (
        (
            "Mehribon va Rahmli Alloh nomi bilan.",
            "Во имя Аллаха, Милостивого, Милосердного.",
            "In Allah's name, the Merciful, the Compassionate.",
        ),
        (
            "Hamd olamlar Robbisi Allohgadir.",
            "Хвала Аллаху, Господу миров.",
            "Praise belongs to Allah, Lord of all worlds.",
        ),
        (
            "U Mehribon va Rahmlidir.",
            "Милостивому, Милосердному.",
            "The Merciful, the Compassionate.",
        ),
        (
            "Jazo kunining Egasidir.",
            "Властелину Дня воздаяния.",
            "Master of the Day of Recompense.",
        ),
        (
            "Faqat Sengagina ibodat qilamiz va Sendangina yordam so‘raymiz.",
            "Тебе одному поклоняемся и у Тебя одного просим помощи.",
            "You alone we worship, and You alone we ask for help.",
        ),
        (
            "Bizni to‘g‘ri yo‘lga boshlagin.",
            "Веди нас прямым путём.",
            "Guide us along the straight path.",
        ),
        (
            "Ne’mat berganlaring yo‘liga; g‘azabga uchraganlar va adashganlar yo‘liga emas.",
            "Путём тех, кого Ты облагодетельствовал, не тех, кто навлёк гнев, и не заблудших.",
            "The path of those You blessed, not those who incurred anger, nor those who went astray.",
        ),
    ),
    112: (
        ("Ayting: U Alloh Yagonadir.", "Скажи: Он — Аллах Единый.", "Say: He is Allah, One."),
        (
            "Alloh behojat, barcha Unga muhtojdir.",
            "Аллах Самодостаточный, к Нему обращаются все.",
            "Allah is self-sufficient, the refuge of all.",
        ),
        (
            "U tug‘magan va tug‘ilmagan.",
            "Он не родил и не был рождён.",
            "He neither begets nor was begotten.",
        ),
        ("Unga hech kim teng emas.", "Никто не равен Ему.", "No one is comparable to Him."),
    ),
    113: (
        (
            "Ayting: Tong Robbisidan panoh so‘rayman,",
            "Скажи: ищу защиты у Господа рассвета,",
            "Say: I seek refuge with the Lord of daybreak,",
        ),
        (
            "U yaratgan narsalar yomonligidan,",
            "от зла того, что Он сотворил,",
            "from the evil of what He created,",
        ),
        (
            "qorong‘u tushgan tun yomonligidan,",
            "от зла мрака, когда он сгущается,",
            "from the evil of darkness when it settles,",
        ),
        (
            "tugunlarga dam soluvchilar yomonligidan,",
            "от зла дующих на узлы,",
            "from the evil of those who blow on knots,",
        ),
        (
            "va hasad qilgan hasadgo‘y yomonligidan.",
            "и от зла завистника, когда он завидует.",
            "and from an envier's evil when they envy.",
        ),
    ),
    114: (
        (
            "Ayting: Odamlar Robbisidan panoh so‘rayman,",
            "Скажи: ищу защиты у Господа людей,",
            "Say: I seek refuge with the Lord of humanity,",
        ),
        ("odamlar Podshohidan,", "Владыки людей,", "the King of humanity,"),
        ("odamlar Ilohidan,", "Бога людей,", "the God of humanity,"),
        (
            "chekinuvchi vasvasachi yomonligidan,",
            "от зла отступающего искусителя,",
            "from the evil of the retreating whisperer,",
        ),
        (
            "u odamlar ko‘ksiga vasvasa soladi,",
            "который нашёптывает в груди людей,",
            "who whispers in people's breasts,",
        ),
        ("jinlar va odamlardan bo‘lganidan.", "из джиннов и людей.", "from among jinn and people."),
    ),
    109: (
        ("Ayting: Ey kofirlar!", "Скажи: о неверующие!", "Say: O disbelievers!"),
        (
            "Men siz ibodat qiladigan narsalarga ibodat qilmayman.",
            "Я не поклоняюсь тому, чему поклоняетесь вы.",
            "I do not worship what you worship.",
        ),
        (
            "Siz ham men ibodat qiladigan Zotga ibodat qiluvchi emassiz.",
            "Вы не поклоняетесь Тому, Кому поклоняюсь я.",
            "Nor do you worship the One whom I worship.",
        ),
        (
            "Men siz ibodat qilgan narsalarga ibodat qiluvchi emasman.",
            "Я не поклоняюсь тому, чему поклонялись вы.",
            "Nor am I a worshipper of what you have worshipped.",
        ),
        (
            "Siz ham men ibodat qiladigan Zotga ibodat qiluvchi emassiz.",
            "Вы не поклоняетесь Тому, Кому поклоняюсь я.",
            "Nor do you worship the One whom I worship.",
        ),
        (
            "Sizga diningiz, menga dinim.",
            "Вам ваша религия, мне моя.",
            "For you is your religion, and for me mine.",
        ),
    ),
}

# Root and grammar tags here describe selected words, not every token of a verse.
# Word glosses are original concise learning aids rather than copied annotations.
# Arabic | root | phonetic latin | phonetic Russian | uz | ru | en | grammar tag
VOCABULARY = """
بِسْمِ|س م و|bismi|бисми|nomi bilan|с именем|in the name|preposition
اللَّهِ||Allohi|Аллахи|Allohning|Аллаха|of Allah|proper
اللَّهُ||Allohu|Аллаху|Alloh|Аллах|Allah|proper
الرَّحْمَٰنِ|ر ح م|ar-Rohmani|ар-Рахмани|Mehribon|Милостивый|the Merciful|adjective
الرَّحِيمِ|ر ح م|ar-Rohimi|ар-Рахими|Rahmli|Милосердный|the Compassionate|adjective
الْحَمْدُ|ح م د|al-hamdu|аль-хамду|hamd|хвала|praise|noun
لِلَّهِ||lillahi|лилляхи|Allohga|Аллаху|to Allah|preposition
رَبِّ|ر ب ب|Robbi|Рабби|Robb|Господь|Lord|noun
الْعَالَمِينَ|ع ل م|al-'alamin|аль-'алямин|olamlar|миры|worlds|plural
مَالِكِ|م ل ك|maliki|малики|egasi|властелин|master|noun
يَوْمِ|ي و م|yavmi|яуми|kun|день|day|noun
الدِّينِ|د ي ن|ad-din|ад-дин|jazo, hisob|воздаяние|recompense|noun
إِيَّاكَ||iyyaka|ийяка|faqat Seni|Тебе одному|You alone|pronoun
نَعْبُدُ|ع ب د|na'budu|на'буду|ibodat qilamiz|поклоняемся|we worship|verb
نَسْتَعِينُ|ع و ن|nasta'in|наста'ин|yordam so‘raymiz|просим помощи|we seek help|verb
اهْدِنَا|ه د ي|ihdina|ихдина|bizni boshlagin|веди нас|guide us|imperative
الصِّرَاطَ|ص ر ط|as-sirot|ас-сырат|yo‘l|путь|path|noun
الْمُسْتَقِيمَ|ق و م|al-mustaqim|аль-мустаким|to‘g‘ri|прямой|straight|adjective
أَنْعَمْتَ|ن ع م|an'amta|ан'амта|Sen ne’mat berding|Ты облагодетельствовал|You blessed|past
قُلْ|ق و ل|qul|куль|ayt|скажи|say|imperative
هُوَ||huva|хува|U|Он|He|pronoun
أَحَدٌ|أ ح د|ahad|ахад|yagona, bir|единый, один|one|noun
الصَّمَدُ|ص م د|as-Somad|ас-Самад|behojat Zot|Самодостаточный|the Self-Sufficient|noun
لَمْ||lam|лям|inkor: ...magan|не|not|negative
يَلِدْ|و ل د|yalid|ялид|tug‘adi|рождает|begets|verb
يُولَدْ|و ل د|yulad|юляд|tug‘iladi|рождается|is begotten|passive
كُفُوًا|ك ف أ|kufuvan|куфуван|teng|равный|equal|noun
أَعُوذُ|ع و ذ|a'uzu|а'узу|panoh so‘rayman|ищу защиты|I seek refuge|verb
الْفَلَقِ|ف ل ق|al-falaq|аль-фаляк|tong|рассвет|daybreak|noun
مِنْ||min|мин|...dan|от, из|from|preposition
شَرِّ|ش ر ر|sharri|шарри|yomonlik|зло|evil|noun
خَلَقَ|خ ل ق|xolaqa|халяка|U yaratdi|Он сотворил|He created|past
غَاسِقٍ|غ س ق|g‘osiq|гасик|qorong‘ilik|мрак|darkness|noun
إِذَا||iza|иза|qachonki|когда|when|time
الْعُقَدِ|ع ق د|al-'uqod|аль-'укад|tugunlar|узлы|knots|plural
حَاسِدٍ|ح س د|hasid|хасид|hasadgo‘y|завистник|envier|participle
النَّاسِ|ن و س|an-nas|ан-нас|odamlar|люди|people|plural
مَلِكِ|م ل ك|maliki|малики|podshoh|царь|king|noun
إِلَٰهِ|أ ل ه|ilahi|иляхи|iloh|Бог|God|noun
الْوَسْوَاسِ|و س و س|al-vasvas|аль-васвас|vasvasachi|искуситель|whisperer|noun
الْخَنَّاسِ|خ ن س|al-xonnas|аль-ханнас|chekinuvchi|отступающий|retreating|adjective
يُوَسْوِسُ|و س و س|yuvasvisu|ювасвису|vasvasa soladi|нашёптывает|whispers|verb
صُدُورِ|ص د ر|sudur|судур|ko‘ksilar|груди|breasts|plural
الْجِنَّةِ|ج ن ن|al-jinna|аль-джинна|jinlar|джинны|jinn|noun
لَا||la|ля|yo‘q, emas|нет, не|no, not|negative
أَعْبُدُ|ع ب د|a'budu|а'буду|ibodat qilaman|поклоняюсь|I worship|verb
تَعْبُدُونَ|ع ب د|ta'budun|та'будун|ibodat qilasizlar|вы поклоняетесь|you worship|verb
عَابِدُونَ|ع ب د|'abidun|абидун|ibodat qiluvchilar|поклоняющиеся|worshippers|participle
عَابِدٌ|ع ب د|'abid|абид|ibodat qiluvchi|поклоняющийся|worshipper|participle
دِينُكُمْ|د ي ن|dinukum|динукум|sizlarning diningiz|ваша религия|your religion|possessive
وَالْعَصْرِ|ع ص ر|val-'asr|валь-'аср|vaqtga qasam|клянусь временем|by time|oath
الْإِنْسَانَ|أ ن س|al-insan|аль-инсан|inson|человек|humanity|noun
خُسْرٍ|خ س ر|xusr|хуср|ziyon|убыток|loss|noun
آمَنُوا|أ م ن|amanu|аману|iymon keltirdilar|уверовали|they believed|past
بِالْحَقِّ|ح ق ق|bil-haqq|биль-хакк|haqqa|к истине|to truth|preposition
بِالصَّبْرِ|ص ب ر|bis-sobr|бис-сабр|sabrga|к терпению|to patience|preposition
أَعْطَيْنَاكَ|ع ط و|a'toynaka|а'тайнака|Biz senga berdik|Мы дали тебе|We gave you|past
الْكَوْثَرَ|ك ث ر|al-kavsar|аль-каусар|Kavsar, mo‘l ne’mat|Каусар, изобилие|al-Kawthar, abundance|noun
فَصَلِّ|ص ل و|fa solli|фа салли|bas, namoz o‘qi|так молись|so pray|imperative
وَانْحَرْ|ن ح ر|vanhar|ванхар|va qurbonlik qil|и принеси жертву|and offer sacrifice|imperative
الْأَبْتَرُ|ب ت ر|al-abtar|аль-абтар|uzilgan|отрезанный|cut off|adjective
نَصْرُ|ن ص ر|nasr|наср|yordam|помощь|help|noun
وَالْفَتْحُ|ف ت ح|val-fath|валь-фатх|va g‘alaba|и победа|and victory|noun
يَدْخُلُونَ|د خ ل|yadxulun|ядхулюн|kiradilar|входят|they enter|verb
أَفْوَاجًا|ف و ج|afvaja|афваджа|to‘p-to‘p|группами|in groups|plural
فَسَبِّحْ|س ب ح|fa sabbih|фа саббих|bas, tasbeh ayt|так прославляй|so glorify|imperative
وَاسْتَغْفِرْهُ|غ ف ر|vastag‘firhu|вастагфирху|va Undan mag‘firat so‘ra|и проси Его прощения|and ask His forgiveness|imperative
تَوَّابًا|ت و ب|tavvaba|тавваба|tavbalarni ko‘p qabul qiluvchi|принимающий покаяние|accepting repentance|adjective
كَيْفَ||kayfa|кайфа|qanday|как|how|question
فَعَلَ|ف ع ل|fa'ala|фа'аля|qildi|сделал|did|past
الْفِيلِ|ف ي ل|al-fil|аль-филь|fil|слон|elephant|noun
كَيْدَهُمْ|ك ي د|kaydahum|кайдахум|ularning makri|их замысел|their plan|possessive
طَيْرًا|ط ي ر|toyr|тайр|qushlar|птицы|birds|plural
أَبَابِيلَ||ababil|абабиль|to‘p-to‘p|стаями|in flocks|adjective
بِحِجَارَةٍ|ح ج ر|bi-hijara|би-хиджара|toshlar bilan|камнями|with stones|preposition
سِجِّيلٍ||sijjil|сиджжиль|pishgan loy|обожжённая глина|baked clay|noun
مَأْكُولٍ|أ ك ل|ma'kul|ма'куль|yeb tashlangan|съеденный|eaten|passive
قُرَيْشٍ||Quraysh|Курайш|Quraysh|курайшиты|Quraysh|proper
رِحْلَةَ|ر ح ل|rihla|рихля|safar|поездка|journey|noun
الشِّتَاءِ|ش ت و|ash-shita|аш-шита|qish|зима|winter|noun
وَالصَّيْفِ|ص ي ف|vas-soyf|вас-сайф|va yoz|и лето|and summer|noun
الْبَيْتِ|ب ي ت|al-bayt|аль-байт|uy|дом|house|noun
جُوعٍ|ج و ع|ju'|джу'|ochlik|голод|hunger|noun
خَوْفٍ|خ و ف|xovf|хауф|qo‘rquv|страх|fear|noun
الْحَيُّ|ح ي ي|al-Hayy|аль-Хайй|Tirik Zot|Живой|the Ever-Living|noun
الْقَيُّومُ|ق و م|al-Qoyyum|аль-Кайюм|Qoyim Zot|Поддерживающий всё|the Sustainer|adjective
يَعْلَمُ|ع ل م|ya'lamu|я'ляму|U biladi|Он знает|He knows|verb
سُبْحَانَكَ|س ب ح|subhanaka|субханака|Sen poksan|Пречист Ты|glory be to You|possessive
كُنْتُ|ك و ن|kuntu|кунту|men edim|я был|I was|past
الظَّالِمِينَ|ظ ل م|az-zolimin|аз-залимин|zulm qiluvchilar|поступившие несправедливо|wrongdoers|participle
"""

GRAMMAR = {
    "noun": (
        "Ot: narsa, ma’no yoki sifat nomi.",
        "Имя существительное: название предмета или понятия.",
        "A noun naming an entity or concept.",
    ),
    "plural": (
        "Ko‘plik ma’nosidagi ot.",
        "Имя со значением множественного числа.",
        "A noun with plural meaning.",
    ),
    "verb": (
        "Hozirgi-kelasi zamon fe’li; shaxsni qo‘shimchalar bildiradi.",
        "Глагол настоящего-будущего времени; лицо выражено формой.",
        "An imperfect verb; its form marks the person.",
    ),
    "past": ("O‘tgan zamon fe’li.", "Глагол прошедшего времени.", "A perfect-tense verb."),
    "imperative": (
        "Buyruq fe’li; duoda iltijo shakli bo‘lishi mumkin.",
        "Повелительная форма; в мольбе выражает просьбу.",
        "An imperative form; in supplication it expresses a request.",
    ),
    "preposition": (
        "Ko‘makchi yoki unga bog‘langan so‘z: munosabatni bildiradi.",
        "Предлог или слово с предлогом, выражающее отношение.",
        "A preposition or prefixed prepositional expression.",
    ),
    "adjective": (
        "Sifat yoki sifat ma’nosidagi so‘z.",
        "Прилагательное или слово со значением качества.",
        "An adjective or a word expressing a quality.",
    ),
    "pronoun": ("Olmosh: shaxsni bildiradi.", "Личное местоимение.", "A personal pronoun."),
    "proper": ("Atoqli ot.", "Имя собственное.", "A proper noun."),
    "negative": (
        "Inkor yuklamasi; ma’nosi gapdagi qo‘llanishiga bog‘liq.",
        "Отрицательная частица; значение зависит от конструкции.",
        "A negative particle; its effect depends on the construction.",
    ),
    "passive": (
        "Majhul shakl: ish bajaruvchisi emas, ish ta’siri ko‘rsatiladi.",
        "Страдательная форма: показано действие над объектом.",
        "A passive form highlighting the receiver of the action.",
    ),
    "participle": (
        "Ismi foil: ishni qiluvchi yoki holat egasini bildiradi.",
        "Действительное причастие: называет деятеля или носителя состояния.",
        "An active participle naming an agent or state.",
    ),
    "possessive": (
        "So‘zga olmosh qo‘shilgan: kimga tegishliligini bildiradi.",
        "К слову присоединено местоимение принадлежности.",
        "An attached pronoun marks possession.",
    ),
    "oath": (
        "Bu yerda va- qasam uchun kelgan; keyingi ot majrur.",
        "Здесь ва- вводит клятву; имя после него в родительном падеже.",
        "Here wa- introduces an oath and governs a genitive noun.",
    ),
    "question": ("So‘roq so‘zi.", "Вопросительное слово.", "An interrogative word."),
    "time": (
        "Vaqt yoki shartni bildiruvchi ifoda.",
        "Выражение времени или условия.",
        "An expression introducing time or a condition.",
    ),
}

NOTES = {
    1: (
        (
            "Hamd, ibodat va hidoyat so‘rash.",
            "Хвала, поклонение и просьба о наставлении.",
            "Praise, worship and a request for guidance.",
        ),
        (
            "Fotiha yetti oyatdan iborat. Bu material til jihatidan o‘rganish uchun tuzilgan.",
            "Аль-Фатиха состоит из семи аятов. Здесь рассматривается язык текста.",
            "Al-Fatiha has seven verses. This material studies the language of the text.",
        ),
        (
            "Iyyaka fe’ldan oldin kelib murojaatni ta’kidlaydi. Na’budu va nasta’in ‘biz’ shaklidagi fe’llar. Ihdina buyruq shaklida bo‘lib, bu duoda ‘bizni boshlagin’ degan iltijoni bildiradi.",
            "Ийяка перед глаголом выделяет адресата. На'буду и наста'ин — формы ‘мы’. Ихдина — повелительная форма, выражающая здесь просьбу ‘веди нас’.",
            "Iyyaka precedes the verbs to foreground the addressee. Na'budu and nasta'in are ‘we’ forms. Ihdina is an imperative functioning here as the request ‘guide us’.",
        ),
    ),
    112: (
        (
            "Allohning yagonaligi haqida qisqa sura.",
            "Краткая сура о единственности Аллаха.",
            "A short chapter affirming Allah's oneness.",
        ),
        (
            "To‘rt oyat. Lug‘aviy izohlar to‘liq tafsir o‘rnini bosmaydi.",
            "Четыре аята. Лексические пояснения не заменяют полный тафсир.",
            "Four verses. Vocabulary notes do not replace a full tafsir.",
        ),
        (
            "Qul — ‘ayt’ buyruq fe’li. Lam yalid faol, lam yulad esa majhul fe’l shaklidir; ikkisini bir xil tarjima qilish mumkin emas. Ahad so‘zi birinchi va oxirgi oyatda keladi.",
            "Куль — повелительное ‘скажи’. Ялид — действительная форма, юляд — страдательная; их значения различны. Ахад встречается в начале и конце суры.",
            "Qul is the imperative ‘say’. Yalid is active and yulad passive; the two forms have different meanings. Ahad occurs in the first and final verses.",
        ),
    ),
    113: (
        (
            "Turli yomonliklardan panoh so‘rash.",
            "Просьба о защите от разных видов зла.",
            "Seeking refuge from different forms of evil.",
        ),
        (
            "Besh oyat. Matndagi grammatik takrorlanishlarni kuzating.",
            "Пять аятов. Обратите внимание на повторяющиеся конструкции.",
            "Five verses. Notice the repeated grammatical structures.",
        ),
        (
            "A’uzu — ‘men panoh so‘rayman’. Min sharri bir necha marta takrorlanadi; min ko‘makchisi keyingi otni majrur qiladi. Iza vaqt yoki shart ma’nosini bildiradi.",
            "А'узу значит ‘я ищу защиты’. Мин шарри повторяется; мин управляет родительным падежом. Иза вводит время или условие.",
            "A'udhu means ‘I seek refuge’. Min sharri repeats; min governs a genitive noun. Idha introduces a time or condition.",
        ),
    ),
    114: (
        (
            "Vasvasadan Allohdan panoh so‘rash.",
            "Просьба к Аллаху о защите от наущений.",
            "Seeking Allah's refuge from whispering.",
        ),
        (
            "Olti oyat. Nos so‘zi surada takroran keladi.",
            "Шесть аятов. Слово нас повторяется в суре.",
            "Six verses. The word nas is repeated throughout the chapter.",
        ),
        (
            "Rabb, malik va ilah so‘zlari bir murojaatda keladi. Yuwaswisu hozirgi-kelasi zamon fe’li, sudur esa sadr so‘zining ko‘plik shaklidir. Min va fi ko‘makchilariga e’tibor bering.",
            "Рабб, малик и илях соединены в одном обращении. Ювасвису — глагол настоящего-будущего времени; судур — множественное от садр. Заметьте предлоги мин и фи.",
            "Rabb, malik and ilah belong to one address. Yuwaswisu is an imperfect verb; sudur is the plural of sadr. Notice the prepositions min and fi.",
        ),
    ),
    109: (
        (
            "Ibodat haqidagi takroriy inkor gaplar.",
            "Повторяющиеся отрицательные предложения о поклонении.",
            "Repeated negative statements about worship.",
        ),
        (
            "Olti oyat. Bu izoh grammatik shakllarni ajratishga yordam beradi.",
            "Шесть аятов. Разбор помогает различить грамматические формы.",
            "Six verses. The notes help distinguish grammatical forms.",
        ),
        (
            "A’budu ‘men ibodat qilaman’, ta’buduna ‘sizlar ibodat qilasizlar’. ‘Abidun ismi foil bo‘lib, fe’l bilan aynan bir shakl emas. Lakum va liya tegishlilik munosabatini bildiradi.",
            "А'буду — ‘я поклоняюсь’, та'будуна — ‘вы поклоняетесь’. 'Абидун — причастная форма, а не тот же глагол. Лякум и лия выражают принадлежность.",
            "A'budu is ‘I worship’, and ta'buduna ‘you worship’. 'Abidun is a participial form, not the same verb form. Lakum and liya express an attribution or relationship.",
        ),
    ),
    103: (
        (
            "Vaqt, iymon, yaxshi amal, haq va sabr.",
            "Время, вера, добрые дела, истина и терпение.",
            "Time, faith, good deeds, truth and patience.",
        ),
        (
            "Uch oyat. Til tahlili umumiy hukm va undan istisno tuzilishini ko‘rsatadi.",
            "Три аята. Разбор показывает общее утверждение и исключение.",
            "Three verses. The language presents a general statement followed by an exception.",
        ),
        (
            "Wal-‘asr boshidagi va- qasam uchun kelgan. Inna va la- ta’kid beradi. Illa istisnoni boshlaydi. Tawasaw o‘zaro bir-birini undash ma’nosidagi VI qolip fe’lidir.",
            "Ва- в валь-'аср вводит клятву. Инна и ля- усиливают утверждение. Илля начинает исключение. Тавасау — VI порода, выражающая взаимное побуждение.",
            "Wa- in wal-'asr introduces an oath. Inna and la- emphasize the statement. Illa begins the exception. Tawasaw is a form VI verb expressing mutual encouragement.",
        ),
    ),
    108: (
        (
            "Ne’mat va unga javoban ibodat.",
            "Дар и поклонение в ответ.",
            "A gift and worship in response.",
        ),
        (
            "Uch oyat. Kavsar nomining lug‘aviy asosi ko‘plik va mo‘llik ma’nosiga bog‘liq.",
            "Три аята. Лексическая основа названия Каусар связана с обилием.",
            "Three verses. The lexical root of Kawthar relates to abundance.",
        ),
        (
            "A’taynaka: ‘Biz berdik’ fe’liga ‘senga’ olmoshi qo‘shilgan. Salli va nhar buyruq fe’llari. Bu til izohi qurbonlik yoki namozning fiqhiy tartibini belgilamaydi.",
            "А'тайнака соединяет ‘Мы дали’ с объектным ‘тебе’. Салли и нхар — повелительные формы. Разбор не определяет правила молитвы или жертвоприношения.",
            "A'taynaka combines ‘We gave’ with the attached object ‘you’. Salli and nhar are imperatives. These language notes do not determine prayer or sacrifice rulings.",
        ),
    ),
    110: (
        (
            "Yordam, g‘alaba, hamd va mag‘firat so‘rash.",
            "Помощь, победа, хвала и просьба о прощении.",
            "Help, victory, praise and asking forgiveness.",
        ),
        (
            "Uch oyat. Birinchi ikki oyat shart-vaziyatni, uchinchisi javobni beradi.",
            "Три аята. Первые два описывают условие, третий — ответ.",
            "Three verses. The first two set up the condition and the third gives the response.",
        ),
        (
            "Iza vaqt-shartni boshlaydi. Fasabbih va istaghfir buyruq shakllari. Afwajan — ‘guruhlar’ ma’nosidagi ko‘plik ot. Tawwaban kuchaytirilgan sifat shaklidir.",
            "Иза вводит временное условие. Фасаббих и истагфир — повелительные формы. Афваджан — множественное ‘группы’. Таввабан — усиленная характеристика.",
            "Idha introduces a temporal condition. Fasabbih and istaghfir are imperative forms. Afwajan is a plural noun, ‘groups’. Tawwaban is an intensive descriptive form.",
        ),
    ),
    105: (
        (
            "Fil egalari va ularning barbod bo‘lgan makri.",
            "Люди слона и их расстроенный замысел.",
            "The people of the elephant and their failed plan.",
        ),
        (
            "Besh oyat. Bu yerda matnda aytilmagan tarixiy tafsilotlar qo‘shilmagan.",
            "Пять аятов. Исторические подробности вне текста здесь не добавлены.",
            "Five verses. No extra historical details beyond the text are added here.",
        ),
        (
            "Alam — so‘roq va inkor birikmasi. Rabbuka va kaydahum so‘zlaridagi olmoshlar kimga tegishlilikni bildiradi. Ka- o‘xshatish ko‘makchisi, ma’kul esa majhul sifatdosh.",
            "Алям соединяет вопрос и отрицание. Суффиксы в раббука и кайдахум выражают принадлежность. Ка- вводит сравнение; ма'куль — страдательное причастие.",
            "Alam combines interrogation and negation. The suffixes in rabbuka and kaydahum mark possession. Ka- introduces comparison, and ma'kul is a passive participle.",
        ),
    ),
    106: (
        (
            "Safar, rizq va omonlik ne’matlari.",
            "Поездки, пропитание и безопасность.",
            "Journeys, provision and security.",
        ),
        (
            "To‘rt oyat. Qish va yoz safarlari matnning o‘zida zikr qilingan.",
            "Четыре аята. Зимние и летние поездки названы в самом тексте.",
            "Four verses. Winter and summer journeys are mentioned in the text itself.",
        ),
        (
            "Rihla — safar; shita va sayf — qish va yoz. Fal-ya’budu bu yerda buyruq lamiga bog‘langan fe’ldir. Ju’ va khawf ochlik hamda qo‘rquvni bildiradi.",
            "Рихля — поездка, шита и сайф — зима и лето. Фаль-я'буду содержит повелительный лям. Джу' и хауф означают голод и страх.",
            "Rihla is a journey; shita and sayf are winter and summer. Fal-ya'budu includes the imperative lam. Ju' and khawf mean hunger and fear.",
        ),
    ),
    2: (
        (
            "Oyatul Kursiy: Allohning hayoti, ilmi va qudrati.",
            "Аят Аль-Курси: жизнь, знание и могущество Аллаха.",
            "Ayat al-Kursi: Allah's life, knowledge and power.",
        ),
        (
            "Baqara surasi 255-oyat. Quyida to‘liq oyat keltirilgan.",
            "Аят 255 суры Аль-Бакара. Ниже приведён весь аят.",
            "Verse 255 of Al-Baqarah. The full verse appears below.",
        ),
        (
            "La ... illa tuzilishi inkor va istisno bilan chegaralaydi. Lahu — ‘Unga tegishli’. Ya’lamu — ‘U biladi’. Bu sodda lug‘aviy va grammatik izoh; Kursiy haqidagi aqidaviy tafsirni mustaqil hal qilmaydi.",
            "Конструкция ля ... илля выражает ограничение через отрицание и исключение. Ляху — ‘Ему принадлежит’, я'ляму — ‘Он знает’. Лексический разбор не подменяет богословское толкование Курси.",
            "La ... illa restricts through negation and exception. Lahu means ‘to Him belongs’; ya'lamu means ‘He knows’. This lexical and grammatical note does not settle theological interpretation of Kursi.",
        ),
    ),
    21: (
        (
            "Yunus alayhissalomning duosi.",
            "Мольба пророка Юнуса.",
            "The supplication of Prophet Yunus.",
        ),
        (
            "Kutubxona matni 21:87 oyatining duo qismidir. Tahlilda to‘liq oyat ko‘rsatilgan; duo 15-so‘zdan boshlanadi.",
            "Основной текст — часть мольбы из 21:87. В разборе показан весь аят; мольба начинается с 15-го слова.",
            "The library text is the supplication excerpt of 21:87. The analysis shows the complete verse; the supplication begins at word 15.",
        ),
        (
            "Anta — ‘Sen’ olmoshi; subhanaka oxiridagi -ka ham ikkinchi shaxsga murojaat qiladi. Inni ‘albatta men’, kuntu ‘men edim’ ma’nolarini bildiradi. Muxtasar til izohi payg‘ambar haqidagi to‘liq tafsir emas.",
            "Анта — ‘Ты’; -ка в субханака также обращено ко второму лицу. Инни — ‘воистину я’, кунту — ‘я был’. Краткий языковой разбор не является полным тафсиром о пророке.",
            "Anta is ‘You’; -ka in subhanaka also addresses the second person. Inni is ‘indeed I’, and kuntu ‘I was’. This concise language note is not a complete tafsir about the prophet.",
        ),
    ),
}

YUNUS = {
    "arabic": "وَذَا النُّونِ إِذْ ذَهَبَ مُغَاضِبًا فَظَنَّ أَنْ لَنْ نَقْدِرَ عَلَيْهِ فَنَادَىٰ فِي الظُّلُمَاتِ أَنْ لَا إِلَٰهَ إِلَّا أَنْتَ سُبْحَانَكَ إِنِّي كُنْتُ مِنَ الظَّالِمِينَ",
    "transcriptions": (
        "Va zan-nuni iz zahaba mug‘oziban fa zonna an lan naqdiro 'alayhi fa nada fiz-zulumati an la ilaha illa anta subhanaka inniy kuntu minaz-zolimin.",
        "Ва зан-нуни из захаба мугадибан фа занна ан лян накдира 'аляйхи фа нада физ-зулюмати ан ля иляха илля анта субханака инни кунту миназ-залимин.",
        "Wa dha-n-nuni idh dhahaba mughadiban fa zanna an lan naqdira 'alayhi fa nada fi-z-zulumati an la ilaha illa anta subhanaka inni kuntu mina-z-zalimin.",
    ),
    "meanings": (
        "Zunnunni ham eslang: u g‘azablanib ketganida, Biz uni tang qilmaymiz deb o‘yladi. So‘ng zulmatlar ichida: ‘Sendan o‘zga iloh yo‘q. Sen poksan! Albatta, men zulm qiluvchilardan bo‘ldim’, deb nido qildi.",
        "Помяни Зун-Нуна: он ушёл разгневанным и думал, что Мы не стесним его. Затем во мраке он воззвал: ‘Нет божества, кроме Тебя. Пречист Ты! Воистину, я был из поступивших несправедливо’.",
        "Remember Dhun-Nun when he left in anger, thinking We would not constrain him. Then in the darkness he called: ‘There is no deity except You. Glory be to You! I was indeed among the wrongdoers’.",
    ),
}

KURSI_MEANINGS = (
    "Alloh — Undan o‘zga iloh yo‘q, U Tirik va Qoyimdir. Uni mudroq ham, uyqu ham olmaydi. Osmonlar va yerdagi barcha narsa Unikidir. Uning huzurida faqat izni bilan shafoat qilinadi. U ularning oldidagi va ortidagi narsalarni biladi. Ular Uning ilmidan faqat U xohlaganini qamray oladilar. Uning Kursiysi osmonlar va yerni qamraydi. Ularni saqlash Uni charchatmaydi. U Oliy va Buyukdir.",
    "Аллах — нет божества, кроме Него, Живого, Поддерживающего всё. Им не овладевают ни дремота, ни сон. Ему принадлежит всё на небесах и земле. Кто заступится перед Ним без Его разрешения? Он знает то, что перед ними, и то, что позади. Они постигают из Его знания лишь то, что Он пожелает. Его Курси охватывает небеса и землю. Их сохранение не утомляет Его. Он — Возвышенный, Великий.",
    "Allah: no deity exists except Him, the Ever-Living, the Sustainer. Neither drowsiness nor sleep overtakes Him. Everything in the heavens and earth belongs to Him. Who can intercede with Him without His permission? He knows what is before them and what is behind them. They grasp from His knowledge only what He wills. His Kursi encompasses the heavens and earth. Guarding them does not tire Him. He is the Most High, the Great.",
)


def _word_rows():
    return {
        parts[0]: parts for line in VOCABULARY.strip().splitlines() if (parts := line.split("|"))
    }


def _english_aid(uzbek_aid):
    # Explicit reviewed locale spellings, not a Cyrillic/Latin transliteration
    # algorithm that could silently invent a pronunciation.
    return {
        "Allohi": "Allahi",
        "Allohu": "Allahu",
        "ar-Rohmani": "ar-Rahmani",
        "ar-Rohimi": "ar-Rahimi",
        "Robbi": "Rabbi",
        "yavmi": "yawmi",
        "as-sirot": "as-sirat",
        "huva": "huwa",
        "as-Somad": "as-Samad",
        "kufuvan": "kufuwan",
        "a'uzu": "a'udhu",
        "al-falaq": "al-falaq",
        "xolaqa": "khalaqa",
        "g‘osiq": "ghasiq",
        "iza": "idha",
        "al-'uqod": "al-'uqad",
        "al-vasvas": "al-waswas",
        "al-xonnas": "al-khannas",
        "yuvasvisu": "yuwaswisu",
        "val-'asr": "wal-'asr",
        "xusr": "khusr",
        "bis-sobr": "bis-sabr",
        "a'toynaka": "a'taynaka",
        "al-kavsar": "al-kawthar",
        "fa solli": "fa salli",
        "vanhar": "wanhar",
        "val-fath": "wal-fath",
        "yadxulun": "yadkhulun",
        "vastag‘firhu": "wastaghfirhu",
        "tavvaba": "tawwaba",
        "toyr": "tayr",
        "bi-hijara": "bi-hijara",
        "vas-soyf": "was-sayf",
        "xovf": "khawf",
        "al-Qoyyum": "al-Qayyum",
        "az-zolimin": "az-zalimin",
    }.get(uzbek_aid, uzbek_aid)


@transaction.atomic
def seed_study_content():
    # Importing data from the existing command does not execute its seed operation.
    from .management.commands.seed_content import PASSAGES
    from .seed_quran import PASSAGE_TRANSCRIPTIONS

    lexical_source, _ = ReligiousSource.objects.get_or_create(
        title="Quranic Arabic Corpus — linguistic reference",
        defaults={
            "url": "https://corpus.quran.com/documentation/",
            "is_verified": True,
            "notes": "Original concise lexical and grammatical learning notes checked against verse pages. Not tafsir or scholarly certification.",
        },
    )
    existing = {
        row["surah"]: row
        for row in PASSAGES
        if row["slug"]
        in {"al-fatiha", "al-ikhlas", "al-falaq", "an-nas", "al-kafirun", "ayat-al-kursi"}
    }
    words = _word_rows()
    created_passages = 0
    verse_count = 0
    for chapter in (*EXISTING_MEANINGS.keys(), *NEW_CHAPTERS.keys(), 2, 21):
        if chapter in NEW_CHAPTERS:
            slug, titles, raw = NEW_CHAPTERS[chapter]
            parsed = [row.split("|") for row in raw.strip().splitlines()]
            verses = [
                (row[0], (row[1], row[2], ENGLISH_TRANSCRIPTIONS[chapter][index]), tuple(row[3:]))
                for index, row in enumerate(parsed)
            ]
            passage, created = QuranPassage.objects.get_or_create(
                slug=slug,
                defaults={
                    "surah_number": chapter,
                    "ayah_start": 1,
                    "ayah_end": len(verses),
                    "passage_type": "surah",
                    "arabic_text": " ۝ ".join(row[0] for row in verses),
                    "source": lexical_source,
                },
            )
            created_passages += int(created)
            for index, language in enumerate(LANGUAGES):
                QuranPassageTranslation.objects.get_or_create(
                    passage=passage,
                    language=language,
                    defaults={
                        "title": titles[index],
                        "transcription": ". ".join(row[1][index] for row in verses),
                        "translation": " ".join(row[2][index] for row in verses),
                    },
                )
        elif chapter == 21:
            passage = QuranPassage.objects.filter(slug="dua-yunus").first()
            if passage is None:
                continue
            verses = [(YUNUS["arabic"], YUNUS["transcriptions"], YUNUS["meanings"])]
        else:
            data = existing[chapter]
            passage = QuranPassage.objects.filter(slug=data["slug"]).first()
            if passage is None:
                continue
            aids = data.get("transcriptions", PASSAGE_TRANSCRIPTIONS.get(data["slug"], {}))
            arabic = [part.strip() for part in data["arabic"].split("۝")]
            transcriptions = [
                [part.strip() for part in aids[language].split(".") if part.strip()]
                for language in LANGUAGES
            ]
            if chapter == 2:
                verses = [
                    (
                        data["arabic"],
                        tuple(aids[language] for language in LANGUAGES),
                        KURSI_MEANINGS,
                    )
                ]
            else:
                if any(len(values) != len(arabic) for values in transcriptions):
                    raise ValueError(f"Invalid transcription verse count for {data['slug']}")
                verses = [
                    (
                        part,
                        tuple(values[index] for values in transcriptions),
                        EXISTING_MEANINGS[chapter][index],
                    )
                    for index, part in enumerate(arabic)
                ]
        source, _ = ReligiousSource.objects.get_or_create(
            title=f"Quranic Arabic Corpus — study {chapter}",
            defaults={
                "url": f"https://corpus.quran.com/wordbyword.jsp?chapter={chapter}&verse={passage.ayah_start}",
                "is_verified": True,
                "notes": "Original learning paraphrases; selected linguistic facts checked against the referenced Arabic Corpus page. No independent tafsir claims.",
            },
        )
        analysis, _ = QuranPassageAnalysis.objects.get_or_create(
            passage=passage, defaults={"source": source, "is_verified": True}
        )
        for index, language in enumerate(LANGUAGES):
            QuranAnalysisTranslation.objects.get_or_create(
                analysis=analysis,
                language=language,
                defaults={
                    "summary": NOTES[chapter][0][index],
                    "context": NOTES[chapter][1][index],
                    "explanation": NOTES[chapter][2][index],
                },
            )
        for offset, (arabic, aids, meanings) in enumerate(verses):
            verse, _ = QuranVerse.objects.get_or_create(
                surah_number=chapter,
                ayah_number=passage.ayah_start + offset,
                defaults={"arabic_text": arabic, "source": source},
            )
            verse_count += 1
            for index, language in enumerate(LANGUAGES):
                QuranVerseTranslation.objects.get_or_create(
                    verse=verse,
                    language=language,
                    defaults={"translation": meanings[index], "transcription": aids[index]},
                )
            lexical_text = arabic
            for pause_mark in "ۚۖۗۙۘۛ":
                lexical_text = lexical_text.replace(pause_mark, "")
            for position, token in enumerate(lexical_text.split(), 1):
                entry = words.get(token)
                if entry is None:
                    continue
                word, _ = QuranWord.objects.get_or_create(
                    verse=verse,
                    position=position,
                    defaults={"arabic_text": token, "root": entry[1]},
                )
                for index, language in enumerate(LANGUAGES):
                    aid = (
                        entry[3]
                        if language == "ru"
                        else (_english_aid(entry[2]) if language == "en" else entry[2])
                    )
                    QuranWordTranslation.objects.get_or_create(
                        word=word,
                        language=language,
                        defaults={
                            "meaning": entry[4 + index],
                            "transcription": aid,
                            "grammar_note": GRAMMAR[entry[7]][index],
                        },
                    )
    return {"new_passages": created_passages, "verses": verse_count}
