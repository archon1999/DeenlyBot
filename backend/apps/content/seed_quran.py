SHORT_SURAH_SLUGS = {
    "al-fatiha",
    "al-kafirun",
    "al-ikhlas",
    "al-falaq",
    "an-nas",
    "al-asr",
    "al-kawthar",
    "an-nasr",
    "al-fil",
    "quraysh",
}

PASSAGE_TRANSCRIPTIONS = {
    "ayat-al-kursi": {
        "en": "Allahu la ilaha illa Huwa, Al-Hayyul-Qayyum. La ta'khudhuhu sinatun wa la nawm. Lahu ma fis-samawati wa ma fil-ard. Man dhal-ladhi yashfa'u 'indahu illa bi-idhnih. Ya'lamu ma bayna aydihim wa ma khalfahum, wa la yuhituna bi-shay'in min 'ilmihi illa bima sha'. Wasi'a Kursiyyuhus-samawati wal-ard, wa la ya'uduhu hifzuhuma, wa Huwal-'Aliyyul-'Azim.",
        "uz": "Allohu la ilaha illa Huv, Al-Hayyul-Qoyyum. La ta'xuzuhu sinatuv va la navm. Lahu ma fis-samavati va ma fil-arz. Man zallaziy yashfa'u 'indahu illa bi-iznih. Ya'lamu ma bayna aydihim va ma xolfahum, va la yuhituna bi-shay'im min 'ilmihi illa bima sha'. Vasi'a Kursiyyuhus-samavati val-arz, va la ya'uduhu hifzuhuma, va Huval-'Aliyyul-'Azim.",
        "ru": "Аллаху ля иляха илля Хува, аль-Хайюль-Кайюм. Ля та'хузуху синатун ва ля навм. Ляху ма фис-самавати ва ма филь-ард. Ман заллязи яшфа'у 'индаху илля би-изних. Я'ляму ма байна айдихим ва ма хальфахум, ва ля юхитуна би-шай'ин мин 'ильмихи илля бима ша'. Васи'а Курсиюхус-самавати валь-ард, ва ля я'удуху хифзухума, ва Хуваль-'Алиюль-'Азым.",
    },
    "al-ikhlas": {
        "en": "Qul Huwa Allahu Ahad. Allahus-Samad. Lam yalid wa lam yulad. Wa lam yakun lahu kufuwan ahad.",
        "uz": "Qul Huvallohu Ahad. Allohus-Somad. Lam yalid va lam yulad. Va lam yakun lahu kufuvan ahad.",
        "ru": "Куль Хува Аллаху Ахад. Аллахус-Самад. Лям ялид ва лям юляд. Ва лям якун ляху куфуван ахад.",
    },
    "al-falaq": {
        "en": "Qul a'udhu bi-Rabbil-falaq. Min sharri ma khalaq. Wa min sharri ghasiqin idha waqab. Wa min sharrin-naffathati fil-'uqad. Wa min sharri hasidin idha hasad.",
        "uz": "Qul a'uzu bi-Rabbil-falaq. Min sharri ma xolaq. Va min sharri g‘osiqin iza vaqob. Va min sharrin-naffasati fil-'uqod. Va min sharri hasidin iza hasad.",
        "ru": "Куль а'узу би-Раббиль-фаляк. Мин шарри ма халяк. Ва мин шарри гасикин иза вакаб. Ва мин шаррин-наффасати филь-'укад. Ва мин шарри хасидин иза хасад.",
    },
    "an-nas": {
        "en": "Qul a'udhu bi-Rabbin-nas. Malikin-nas. Ilahin-nas. Min sharril-waswasil-khannas. Alladhi yuwaswisu fi sudurin-nas. Minal-jinnati wan-nas.",
        "uz": "Qul a'uzu bi-Rabbin-nas. Malikin-nas. Ilahin-nas. Min sharril-vasvasil-xonnas. Allaziy yuvasvisu fiy sudurin-nas. Minal-jinnati van-nas.",
        "ru": "Куль а'узу би-Раббин-нас. Маликин-нас. Иляхин-нас. Мин шарриль-васвасиль-ханнас. Аллязи ювасвису фи судурин-нас. Миналь-джиннати ван-нас.",
    },
}

EXTRA_PASSAGES = [
    {
        "slug": "al-fatiha",
        "surah": 1,
        "start": 1,
        "end": 7,
        "arabic": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ ۝ الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ ۝ الرَّحْمَٰنِ الرَّحِيمِ ۝ مَالِكِ يَوْمِ الدِّينِ ۝ إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ ۝ اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ ۝ صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ",
        "titles": {
            "ru": "Открывающая Коран — Аль-Фатиха",
            "en": "The Opening — Al-Fatiha",
            "uz": "Qur’onni ochuvchi — Fotiha",
        },
        "translations": {
            "ru": "С именем Аллаха, Всемилостивого, Милосердного. Хвала Аллаху, Господу миров, Всемилостивому, Милосердному, Властелину Дня воздаяния. Тебе одному мы поклоняемся и Тебя одного просим о помощи. Веди нас прямым путем — путем тех, кого Ты облагодетельствовал, не тех, на кого пал гнев, и не заблудших.",
            "en": "In the name of Allah, the Entirely Merciful, the Especially Merciful. All praise belongs to Allah, Lord of all worlds, the Entirely Merciful, the Especially Merciful, Master of the Day of Judgment. You alone we worship and You alone we ask for help. Guide us to the straight path—the path of those You have blessed, not those who earned anger or went astray.",
            "uz": "Mehribon va Rahmli Alloh nomi bilan. Olamlar Robbisi Allohga hamd bo‘lsin. U Mehribon va Rahmli, jazo kunining Egasi. Faqat Sengagina ibodat qilamiz va faqat Sendangina yordam so‘raymiz. Bizni to‘g‘ri yo‘lga — ne’mat bergan zotlaring yo‘liga boshlagin; g‘azabga uchraganlar va adashganlar yo‘liga emas.",
        },
        "transcriptions": {
            "en": "Bismillahir-Rahmanir-Rahim. Alhamdu lillahi Rabbil-'alamin. Ar-Rahmanir-Rahim. Maliki yawmid-din. Iyyaka na'budu wa iyyaka nasta'in. Ihdinas-siratal-mustaqim. Siratal-ladhina an'amta 'alayhim, ghayril-maghdubi 'alayhim wa lad-dallin.",
            "uz": "Bismillahir-Rohmanir-Rohim. Alhamdu lillahi Robbil-'alamin. Ar-Rohmanir-Rohim. Maliki yavmid-din. Iyyaka na'budu va iyyaka nasta'in. Ihdinas-sirotal-mustaqim. Sirotollazina an'amta 'alayhim, g‘oyril-mag‘dubi 'alayhim va laz-zollin.",
            "ru": "Бисмилляхир-Рахманир-Рахим. Альхамду лилляхи Раббиль-'алямин. Ар-Рахманир-Рахим. Малики яумид-дин. Ийяка на'буду ва ийяка наста'ин. Ихдинас-сыраталь-мустаким. Сыраталлязина ан'амта 'аляйхим, гайриль-магдуби 'аляйхим ва ляд-даллин.",
        },
    },
    {
        "slug": "dua-yunus",
        "surah": 21,
        "start": 87,
        "end": 87,
        "arabic": "لَا إِلَٰهَ إِلَّا أَنْتَ سُبْحَانَكَ إِنِّي كُنْتُ مِنَ الظَّالِمِينَ",
        "titles": {
            "ru": "Аят — мольба пророка Юнуса",
            "en": "The Supplication of Prophet Yunus",
            "uz": "Yunus payg‘ambarning duosi",
        },
        "translations": {
            "ru": "Нет достойного поклонения, кроме Тебя. Пречист Ты! Поистине, я был из числа поступивших несправедливо.",
            "en": "There is no deity worthy of worship except You. Glory be to You! I was truly among the wrongdoers.",
            "uz": "Sendan o‘zga ibodatga loyiq zot yo‘q. Sen poksan! Albatta, men o‘ziga zulm qilganlardan bo‘ldim.",
        },
        "transcriptions": {
            "en": "La ilaha illa Anta, subhanaka, inni kuntu minaz-zalimin.",
            "uz": "La ilaha illa Anta, subhanaka, inniy kuntu minaz-zolimin.",
            "ru": "Ля иляха илля Анта, субханака, инни кунту миназ-залимин.",
        },
    },
    {
        "slug": "dua-musa",
        "surah": 20,
        "start": 25,
        "end": 28,
        "arabic": "رَبِّ اشْرَحْ لِي صَدْرِي ۝ وَيَسِّرْ لِي أَمْرِي ۝ وَاحْلُلْ عُقْدَةً مِنْ لِسَانِي ۝ يَفْقَهُوا قَوْلِي",
        "titles": {
            "ru": "Аят — мольба пророка Мусы",
            "en": "The Supplication of Prophet Musa",
            "uz": "Muso payg‘ambarning duosi",
        },
        "translations": {
            "ru": "Господь мой, раскрой мою грудь, облегчи мое дело и развяжи узел на моем языке, чтобы они понимали мою речь.",
            "en": "My Lord, expand my chest, make my task easy for me, and untie the knot from my tongue so they may understand my speech.",
            "uz": "Robbim, ko‘ksimni keng qil, ishimni oson qil va tilimdagi tugunni yechgin, toki ular so‘zimni anglasinlar.",
        },
        "transcriptions": {
            "en": "Rabbishrah li sadri. Wa yassir li amri. Wahlul 'uqdatan min lisani. Yafqahu qawli.",
            "uz": "Robbishroh liy sodriy. Va yassir liy amriy. Vahlul 'uqdatan min lisaniy. Yafqohu qovliy.",
            "ru": "Раббишрах ли садри. Ва яссир ли амри. Вахлюль 'укдатан мин лисани. Яфкаху каули.",
        },
    },
    {
        "slug": "dua-ayyub",
        "surah": 21,
        "start": 83,
        "end": 83,
        "arabic": "أَنِّي مَسَّنِيَ الضُّرُّ وَأَنْتَ أَرْحَمُ الرَّاحِمِينَ",
        "titles": {
            "ru": "Аят — мольба пророка Айюба",
            "en": "The Supplication of Prophet Ayyub",
            "uz": "Ayyub payg‘ambarning duosi",
        },
        "translations": {
            "ru": "Меня коснулась беда, а ведь Ты — Милосерднейший из милосердных.",
            "en": "Adversity has touched me, and You are the Most Merciful of those who show mercy.",
            "uz": "Menga musibat yetdi. Sen esa rahm qiluvchilarning eng Rahmlisisan.",
        },
        "transcriptions": {
            "en": "Anni massaniyad-durru wa Anta arhamur-rahimin.",
            "uz": "Anniy massaniyaz-zurru va Anta arhamur-rohimin.",
            "ru": "Анни массанияд-дурру ва Анта архамур-рахимин.",
        },
    },
    {
        "slug": "dua-zakariya",
        "surah": 21,
        "start": 89,
        "end": 89,
        "arabic": "رَبِّ لَا تَذَرْنِي فَرْدًا وَأَنْتَ خَيْرُ الْوَارِثِينَ",
        "titles": {
            "ru": "Аят — мольба пророка Закарии",
            "en": "The Supplication of Prophet Zakariya",
            "uz": "Zakariyo payg‘ambarning duosi",
        },
        "translations": {
            "ru": "Господь мой, не оставляй меня одиноким, и Ты — лучший из наследующих.",
            "en": "My Lord, do not leave me alone, though You are the best of inheritors.",
            "uz": "Robbim, meni yolg‘iz qoldirma. Sen vorislarning eng yaxshisisan.",
        },
        "transcriptions": {
            "en": "Rabbi la tadharni fardan wa Anta khayrul-warithin.",
            "uz": "Robbi la tazarniy fardav va Anta xoyrul-varisin.",
            "ru": "Рабби ля тазарни фардан ва Анта хайруль-варисин.",
        },
    },
    {
        "slug": "ayat-of-hope",
        "surah": 39,
        "start": 53,
        "end": 53,
        "arabic": "قُلْ يَا عِبَادِيَ الَّذِينَ أَسْرَفُوا عَلَىٰ أَنْفُسِهِمْ لَا تَقْنَطُوا مِنْ رَحْمَةِ اللَّهِ ۚ إِنَّ اللَّهَ يَغْفِرُ الذُّنُوبَ جَمِيعًا ۚ إِنَّهُ هُوَ الْغَفُورُ الرَّحِيمُ",
        "titles": {
            "ru": "Аят надежды и милости",
            "en": "The Verse of Hope and Mercy",
            "uz": "Umid va rahmat oyati",
        },
        "translations": {
            "ru": "Скажи: «О Мои рабы, поступившие чрезмерно против самих себя! Не отчаивайтесь в милости Аллаха. Поистине, Аллах прощает все грехи. Он — Прощающий, Милосердный».",
            "en": "Say: O My servants who have transgressed against themselves, do not despair of Allah’s mercy. Allah certainly forgives all sins. He is the All-Forgiving, the Especially Merciful.",
            "uz": "Ayting: Ey o‘zlariga qarshi haddan oshgan bandalarim! Allohning rahmatidan noumid bo‘lmang. Albatta, Alloh barcha gunohlarni mag‘firat qiladi. U Mag‘firatli va Rahmlidir.",
        },
        "transcriptions": {
            "en": "Qul ya 'ibadiyalladhina asrafu 'ala anfusihim la taqnatu mir-rahmatillah. Innallaha yaghfirudh-dhunuba jami'a. Innahu Huwal-Ghafurur-Rahim.",
            "uz": "Qul ya 'ibadiyallazina asrofu 'ala anfusihim la taqnatu mir-rohmatillah. Innalloha yag‘firuz-zunuba jami'a. Innahu Huval-G‘ofurur-Rohim.",
            "ru": "Куль я 'ибадияллязина асрафу 'аля анфусихим ля такнату мир-рахматиллях. Инналлаха ягфируз-зунуба джами'а. Иннаху Хуваль-Гафурур-Рахим.",
        },
    },
    {
        "slug": "hasbunallahu",
        "surah": 3,
        "start": 173,
        "end": 173,
        "arabic": "حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ",
        "titles": {
            "ru": "Аят упования — «Достаточен нам Аллах»",
            "en": "The Verse of Reliance — Allah Is Sufficient",
            "uz": "Tavakkul oyati — «Alloh bizga kifoya»",
        },
        "translations": {
            "ru": "Достаточен нам Аллах, и Он — прекрасный Попечитель.",
            "en": "Allah is sufficient for us, and He is the best Trustee.",
            "uz": "Alloh bizga kifoya va U eng yaxshi Vakildir.",
        },
        "transcriptions": {
            "en": "Hasbunallahu wa ni'mal-Wakil.",
            "uz": "Hasbunallohu va ni'mal-Vakil.",
            "ru": "Хасбуналлаху ва ни'маль-Вакиль.",
        },
    },
    {
        "slug": "last-two-al-baqarah",
        "surah": 2,
        "start": 285,
        "end": 286,
        "arabic": "آمَنَ الرَّسُولُ بِمَا أُنْزِلَ إِلَيْهِ مِنْ رَبِّهِ وَالْمُؤْمِنُونَ ۚ كُلٌّ آمَنَ بِاللَّهِ وَمَلَائِكَتِهِ وَكُتُبِهِ وَرُسُلِهِ لَا نُفَرِّقُ بَيْنَ أَحَدٍ مِنْ رُسُلِهِ ۚ وَقَالُوا سَمِعْنَا وَأَطَعْنَا ۖ غُفْرَانَكَ رَبَّنَا وَإِلَيْكَ الْمَصِيرُ ۝ لَا يُكَلِّفُ اللَّهُ نَفْسًا إِلَّا وُسْعَهَا ۚ لَهَا مَا كَسَبَتْ وَعَلَيْهَا مَا اكْتَسَبَتْ ۗ رَبَّنَا لَا تُؤَاخِذْنَا إِنْ نَسِينَا أَوْ أَخْطَأْنَا ۚ رَبَّنَا وَلَا تَحْمِلْ عَلَيْنَا إِصْرًا كَمَا حَمَلْتَهُ عَلَى الَّذِينَ مِنْ قَبْلِنَا ۚ رَبَّنَا وَلَا تُحَمِّلْنَا مَا لَا طَاقَةَ لَنَا بِهِ ۖ وَاعْفُ عَنَّا وَاغْفِرْ لَنَا وَارْحَمْنَا ۚ أَنْتَ مَوْلَانَا فَانْصُرْنَا عَلَى الْقَوْمِ الْكَافِرِينَ",
        "titles": {
            "ru": "Последние два аята Аль-Бакара — «Аманар-Расул»",
            "en": "The Last Two Verses of Al-Baqarah",
            "uz": "Baqara surasining oxirgi ikki oyati — «Amanar-Rosul»",
        },
        "translations": {
            "ru": "Посланник и верующие уверовали в ниспосланное ему от Господа. Все уверовали в Аллаха, Его ангелов, Писания и посланников… Аллах не возлагает на душу сверх ее возможностей… Господь наш, не взыщи с нас, если мы забыли или ошиблись; прости нас, помилуй нас и помоги нам.",
            "en": "The Messenger and the believers believe in what was revealed from his Lord. All believe in Allah, His angels, Books, and messengers… Allah does not burden a soul beyond its capacity… Our Lord, do not hold us accountable if we forget or make a mistake; pardon us, forgive us, have mercy on us, and help us.",
            "uz": "Payg‘ambar va mo‘minlar Robbisidan nozil qilingan narsaga iymon keltirdilar. Barchasi Allohga, farishtalariga, kitoblariga va payg‘ambarlariga iymon keltirdi… Alloh hech bir jonni toqatidan tashqari narsaga yuklamaydi… Robbimiz, unutsak yoki xato qilsak, bizni jazolama; bizni afv et, mag‘firat qil, rahm et va yordam ber.",
        },
        "transcriptions": {
            "en": "Amanar-Rasulu bima unzila ilayhi mir-Rabbihi wal-mu'minun... La yukallifullahu nafsan illa wus'aha... Rabbana la tu'akhidhna in nasina aw akhta'na... Wa'fu 'anna, waghfir lana, warhamna. Anta Mawlana fansurna 'alal-qawmil-kafirin.",
            "uz": "Amanar-Rosulu bima unzila ilayhi mir-Robbihi val-mu'minun... La yukallifullohu nafsan illa vus'aha... Robbana la tu'axizna in nasiyna av axto'na... Va'fu 'anna, vag‘fir lana, varhamna. Anta Mavlana fansurna 'alal-qovmil-kafirin.",
            "ru": "Аманар-Расулю бима унзиля иляйхи мир-Раббихи валь-му'минун... Ля юкаллифуллаху нафсан илля вус'аха... Раббана ля ту'ахизна ин насина ау ахта'на... Ва'фу 'анна, вагфир ляна, вархамна. Анта Мауляна фансурна 'аляль-каумиль-кафирин.",
        },
    },
    {
        "slug": "ayat-salawat",
        "surah": 33,
        "start": 56,
        "end": 56,
        "arabic": "إِنَّ اللَّهَ وَمَلَائِكَتَهُ يُصَلُّونَ عَلَى النَّبِيِّ ۚ يَا أَيُّهَا الَّذِينَ آمَنُوا صَلُّوا عَلَيْهِ وَسَلِّمُوا تَسْلِيمًا",
        "titles": {
            "ru": "Аят о салавате Пророку ﷺ",
            "en": "The Verse of Blessings upon the Prophet ﷺ",
            "uz": "Payg‘ambarga ﷺ salovat oyati",
        },
        "translations": {
            "ru": "Поистине, Аллах и Его ангелы благословляют Пророка. О верующие! Благословляйте его и приветствуйте совершенным приветствием.",
            "en": "Indeed, Allah and His angels send blessings upon the Prophet. O believers, invoke blessings and peace upon him abundantly.",
            "uz": "Albatta, Alloh va Uning farishtalari Payg‘ambarga salovat aytadilar. Ey iymon keltirganlar, siz ham unga salovat va mukammal salom aytinglar.",
        },
        "transcriptions": {
            "en": "Innallaha wa mala'ikatahu yusalluna 'alan-Nabiyy. Ya ayyuhalladhina amanu sallu 'alayhi wa sallimu taslima.",
            "uz": "Innalloha va malaikatahu yusolluna 'alan-Nabiy. Ya ayyuhallazina amanu sollu 'alayhi va sallimu taslima.",
            "ru": "Инналлаха ва маляикатаху юсаллюна 'алян-Набий. Я айюхаллязина аману саллю 'аляйхи ва саллиму таслима.",
        },
    },
    {
        "slug": "al-kafirun",
        "surah": 109,
        "start": 1,
        "end": 6,
        "arabic": "قُلْ يَا أَيُّهَا الْكَافِرُونَ ۝ لَا أَعْبُدُ مَا تَعْبُدُونَ ۝ وَلَا أَنْتُمْ عَابِدُونَ مَا أَعْبُدُ ۝ وَلَا أَنَا عَابِدٌ مَا عَبَدْتُمْ ۝ وَلَا أَنْتُمْ عَابِدُونَ مَا أَعْبُدُ ۝ لَكُمْ دِينُكُمْ وَلِيَ دِينِ",
        "titles": {"ru": "Сура Аль-Кафирун", "en": "Surah Al-Kafirun", "uz": "Kofirun surasi"},
        "translations": {
            "ru": "Скажи: «О неверующие! Я не поклоняюсь тому, чему поклоняетесь вы, и вы не поклоняетесь Тому, Кому поклоняюсь я… У вас ваша религия, а у меня моя».",
            "en": "Say: O disbelievers, I do not worship what you worship, nor do you worship the One I worship… You have your way, and I have mine.",
            "uz": "Ayting: Ey kofirlar! Men sizlar sig‘inayotgan narsalarga sig‘inmayman. Sizlar ham men ibodat qilayotgan Zotga ibodat qiluvchi emassizlar… Sizlarga o‘z diningiz, menga o‘z dinim.",
        },
        "transcriptions": {
            "en": "Qul ya ayyuhal-kafirun. La a'budu ma ta'budun. Wa la antum 'abiduna ma a'bud. Wa la ana 'abidum ma 'abadtum. Wa la antum 'abiduna ma a'bud. Lakum dinukum wa liya din.",
            "uz": "Qul ya ayyuhal-kafirun. La a'budu ma ta'budun. Va la antum 'abiduna ma a'bud. Va la ana 'abidum ma 'abadtum. Va la antum 'abiduna ma a'bud. Lakum dinukum va liya din.",
            "ru": "Куль я айюхаль-кафирун. Ля а'буду ма та'будун. Ва ля антум 'абидуна ма а'буд. Ва ля ана 'абидум ма 'абадтум. Ва ля антум 'абидуна ма а'буд. Лякум динукум ва лия дин.",
        },
    },
    {
        "slug": "rabbana-la-tuzigh",
        "surah": 3,
        "start": 8,
        "end": 8,
        "arabic": "رَبَّنَا لَا تُزِغْ قُلُوبَنَا بَعْدَ إِذْ هَدَيْتَنَا وَهَبْ لَنَا مِنْ لَدُنْكَ رَحْمَةً ۚ إِنَّكَ أَنْتَ الْوَهَّابُ",
        "titles": {
            "ru": "Аят — мольба о стойкости сердца",
            "en": "A Supplication for Steadfast Hearts",
            "uz": "Qalb sobitligi uchun duo oyati",
        },
        "translations": {
            "ru": "Господь наш, не уклоняй наши сердца после того, как Ты наставил нас, и даруй нам милость от Себя. Поистине, Ты — Дарующий.",
            "en": "Our Lord, do not let our hearts deviate after You have guided us. Grant us mercy from Yourself; You are truly the Bestower.",
            "uz": "Robbimiz, bizni hidoyat qilganingdan keyin qalblarimizni og‘dirma va bizga O‘z huzuringdan rahmat ato et. Albatta, Sen ko‘p Ato Etuvchisan.",
        },
        "transcriptions": {
            "en": "Rabbana la tuzigh qulubana ba'da idh hadaytana wa hab lana mil-ladunka rahmah. Innaka Antal-Wahhab.",
            "uz": "Robbana la tuzig‘ qulubana ba'da iz hadaytana va hab lana mil-ladunka rohmah. Innaka Antal-Vahhab.",
            "ru": "Раббана ля тузиг кулюбана ба'да из хадайтана ва хаб ляна мил-лядунка рахма. Иннака Анталь-Ваххаб.",
        },
    },
    {
        "slug": "al-hashr-last-verses",
        "surah": 59,
        "start": 22,
        "end": 24,
        "arabic": "هُوَ اللَّهُ الَّذِي لَا إِلَٰهَ إِلَّا هُوَ ۖ عَالِمُ الْغَيْبِ وَالشَّهَادَةِ ۖ هُوَ الرَّحْمَٰنُ الرَّحِيمُ ۝ هُوَ اللَّهُ الَّذِي لَا إِلَٰهَ إِلَّا هُوَ الْمَلِكُ الْقُدُّوسُ السَّلَامُ الْمُؤْمِنُ الْمُهَيْمِنُ الْعَزِيزُ الْجَبَّارُ الْمُتَكَبِّرُ ۚ سُبْحَانَ اللَّهِ عَمَّا يُشْرِكُونَ ۝ هُوَ اللَّهُ الْخَالِقُ الْبَارِئُ الْمُصَوِّرُ ۖ لَهُ الْأَسْمَاءُ الْحُسْنَىٰ ۚ يُسَبِّحُ لَهُ مَا فِي السَّمَاوَاتِ وَالْأَرْضِ ۖ وَهُوَ الْعَزِيزُ الْحَكِيمُ",
        "titles": {
            "ru": "Последние аяты Аль-Хашр — прекрасные имена",
            "en": "The Last Verses of Al-Hashr — The Beautiful Names",
            "uz": "Hashr surasining oxirgi oyatlari — go‘zal ismlar",
        },
        "translations": {
            "ru": "Он — Аллах, нет достойного поклонения, кроме Него, Знающий сокровенное и явное, Всемилостивый, Милосердный… Он — Владыка, Пречистый, Источник мира, Дарующий безопасность, Хранитель, Могущественный… Он — Творец, Создатель и Придающий облик. Ему принадлежат прекраснейшие имена.",
            "en": "He is Allah; none is worthy of worship except Him, Knower of the unseen and seen, the Entirely Merciful, the Especially Merciful… He is the King, the Most Holy, Source of Peace, Giver of Security, Guardian, Almighty… He is the Creator, Originator, and Fashioner. His are the most beautiful Names.",
            "uz": "U Allohdir. Undan o‘zga ibodatga loyiq zot yo‘q. U g‘ayb va oshkorani Biluvchi, Mehribon va Rahmlidir… U Podshoh, Mutlaq Pok, Tinchlik Manbai, Omonlik Beruvchi, Qo‘riqlovchi va Qudratlidir… U Yaratuvchi, Yo‘qdan Bor Qiluvchi va Shakl Beruvchidir. Eng go‘zal ismlar Unikidir.",
        },
        "transcriptions": {
            "en": "Huwallahu alladhi la ilaha illa Huwa, 'alimul-ghaybi wash-shahadah, Huwar-Rahmanur-Rahim... Huwallahul-Khaliqul-Bari'ul-Musawwir, lahul-asma'ul-husna... wa Huwal-'Azizul-Hakim.",
            "uz": "Huvallohullaziy la ilaha illa Huv, 'alimul-g‘oybi vash-shahadah, Huvar-Rohmanur-Rohim... Huvallohul-Xoliqul-Bari'ul-Musovvir, lahul-asma'ul-husna... va Huval-'Azizul-Hakim.",
            "ru": "Хуваллахуллязи ля иляха илля Хува, 'алимуль-гайби ваш-шахада, Хувар-Рахманур-Рахим... Хуваллахуль-Халикуль-Бари'уль-Мусаввир, ляхуль-асма'уль-хусна... ва Хуваль-'Азизуль-Хаким.",
        },
    },
]

EXTRA_PASSAGES.extend(
    [
        {
            "slug": "al-asr",
            "surah": 103,
            "start": 1,
            "end": 3,
            "arabic": "وَالْعَصْرِ ۝ إِنَّ الْإِنْسَانَ لَفِي خُسْرٍ ۝ إِلَّا الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ وَتَوَاصَوْا بِالْحَقِّ وَتَوَاصَوْا بِالصَّبْرِ",
            "titles": {
                "ru": "Сура Аль-Аср — Время",
                "en": "Surah Al-Asr — Time",
                "uz": "Asr surasi — Vaqt",
            },
            "translations": {
                "ru": "Клянусь временем! Поистине, человек в убытке, кроме тех, кто уверовал, совершал праведные дела, наставлял друг друга на истину и наставлял друг друга на терпение.",
                "en": "By time! Humanity is surely in loss, except those who believe, do righteous deeds, encourage one another to truth, and encourage one another to patience.",
                "uz": "Asrga qasam! Albatta, inson ziyondadir. Faqat iymon keltirgan, solih amallar qilgan, bir-biriga haqni va sabrni tavsiya qilganlar bundan mustasno.",
            },
            "transcriptions": {
                "ru": "Валь-'аср. Инналь-инсана ляфи хуср. Илляллязина аману ва 'амилюс-салихати ва тавасау биль-хакки ва тавасау бис-сабр.",
                "en": "Wal-‘asr. Innal-insana lafi khusr. Illal-ladhina amanu wa ‘amilus-salihati wa tawasaw bil-haqqi wa tawasaw bis-sabr.",
                "uz": "Val-‘asr. Innal-insana lafiy xusr. Illallazina amanu va ‘amilus-solihati va tavasov bil-haqqi va tavasov bis-sobr.",
            },
        },
        {
            "slug": "al-kawthar",
            "surah": 108,
            "start": 1,
            "end": 3,
            "arabic": "إِنَّا أَعْطَيْنَاكَ الْكَوْثَرَ ۝ فَصَلِّ لِرَبِّكَ وَانْحَرْ ۝ إِنَّ شَانِئَكَ هُوَ الْأَبْتَرُ",
            "titles": {
                "ru": "Сура Аль-Каусар — Изобилие",
                "en": "Surah Al-Kawthar — Abundance",
                "uz": "Kavsar surasi — Mo‘l-ko‘l ne’mat",
            },
            "translations": {
                "ru": "Поистине, Мы даровали тебе Аль-Каусар. Поэтому молись своему Господу и совершай жертвоприношение. Поистине, ненавидящий тебя сам лишен продолжения.",
                "en": "We have indeed granted you Al-Kawthar, abundant goodness. So pray to your Lord and sacrifice. The one who hates you is truly cut off.",
                "uz": "Albatta, Biz senga Kavsarni ato etdik. Bas, Robbing uchun namoz o‘qi va qurbonlik qil. Albatta, seni yomon ko‘ruvchining o‘zi uzilib qoluvchidir.",
            },
            "transcriptions": {
                "ru": "Инна а'тайнакаль-каусар. Фасалли ли-Раббика ванхар. Инна шаниака хуваль-абтар.",
                "en": "Inna a‘taynakal-kawthar. Fa-salli li-Rabbika wanhar. Inna shani’aka huwal-abtar.",
                "uz": "Inna a‘toynakal-kavsar. Fasolli li-Robbika vanhar. Inna shani’aka huval-abtar.",
            },
        },
        {
            "slug": "an-nasr",
            "surah": 110,
            "start": 1,
            "end": 3,
            "arabic": "إِذَا جَاءَ نَصْرُ اللَّهِ وَالْفَتْحُ ۝ وَرَأَيْتَ النَّاسَ يَدْخُلُونَ فِي دِينِ اللَّهِ أَفْوَاجًا ۝ فَسَبِّحْ بِحَمْدِ رَبِّكَ وَاسْتَغْفِرْهُ إِنَّهُ كَانَ تَوَّابًا",
            "titles": {
                "ru": "Сура Ан-Наср — Помощь",
                "en": "Surah An-Nasr — Divine Help",
                "uz": "Nasr surasi — Yordam",
            },
            "translations": {
                "ru": "Когда придут помощь Аллаха и победа, и ты увидишь, как люди входят в религию Аллаха толпами, прославляй своего Господа с хвалой и проси Его прощения. Поистине, Он принимает покаяние.",
                "en": "When Allah's help and victory come, and you see people entering Allah's religion in crowds, glorify your Lord with praise and ask His forgiveness. He is ever Accepting of repentance.",
                "uz": "Allohning yordami va fath kelganda, odamlarning Alloh diniga guruh-guruh kirayotganini ko‘rganingda, Robbingga hamd bilan tasbeh ayt va Undan mag‘firat so‘ra. Albatta, U tavbalarni qabul qiluvchidir.",
            },
            "transcriptions": {
                "ru": "Иза джаа насруллахи валь-фатх. Ва раайтан-наса йадхулюна фи динилляхи афваджа. Фасаббих бихамди Раббика вастагфирх. Иннаху кана тавваба.",
                "en": "Idha ja’a nasrullahi wal-fath. Wa ra’aytan-nasa yadkhuluna fi dinillahi afwaja. Fa-sabbih bihamdi Rabbika wastaghfirh. Innahu kana tawwaba.",
                "uz": "Iza ja’a nasrullohi val-fath. Va ro’aytan-nasa yadxuluna fiy dinillahi afvaja. Fasabbih bihamdi Robbika vastag‘firh. Innahu kana tavvaba.",
            },
        },
        {
            "slug": "al-fil",
            "surah": 105,
            "start": 1,
            "end": 5,
            "arabic": "أَلَمْ تَرَ كَيْفَ فَعَلَ رَبُّكَ بِأَصْحَابِ الْفِيلِ ۝ أَلَمْ يَجْعَلْ كَيْدَهُمْ فِي تَضْلِيلٍ ۝ وَأَرْسَلَ عَلَيْهِمْ طَيْرًا أَبَابِيلَ ۝ تَرْمِيهِمْ بِحِجَارَةٍ مِنْ سِجِّيلٍ ۝ فَجَعَلَهُمْ كَعَصْفٍ مَأْكُولٍ",
            "titles": {
                "ru": "Сура Аль-Филь — Слон",
                "en": "Surah Al-Fil — The Elephant",
                "uz": "Fil surasi",
            },
            "translations": {
                "ru": "Разве ты не видел, как твой Господь поступил с войском слона? Разве Он не обратил их замысел в тщету? Он послал на них птиц стаями, которые бросали в них камни из обожженной глины, и сделал их подобными изъеденной соломе.",
                "en": "Have you not seen how your Lord dealt with the people of the elephant? Did He not frustrate their scheme? He sent flocks of birds against them, pelting them with stones of baked clay, leaving them like chewed straw.",
                "uz": "Robbing fil egalari bilan qanday muomala qilganini ko‘rmadingmi? Ularning hiylasini behuda qilmadimi? Ularga to‘da-to‘da qushlarni yubordi. Qushlar ularga pishgan loydan toshlar otib, ularni yeb tashlangan somondek qildi.",
            },
            "transcriptions": {
                "ru": "Алям тара кайфа фа'аля Раббука би-асхабиль-филь. Алям йадж'аль кайдахум фи тадлиль. Ва арсаля 'аляйхим тайран абабиль. Тармихим бихиджаратим мин сиджжиль. Фаджа'аляхум ка'асфим ма'куль.",
                "en": "Alam tara kayfa fa‘ala Rabbuka bi-ashabil-fil. Alam yaj‘al kaydahum fi tadlil. Wa arsala ‘alayhim tayran ababil. Tarmihim bi-hijaratin min sijjil. Fa-ja‘alahum ka‘asfin ma’kul.",
                "uz": "Alam taro kayfa fa‘ala Robbuka bi-ashabil-fil. Alam yaj‘al kaydahum fiy tadlil. Va arsala ‘alayhim toyron ababil. Tarmihim bihijarotim min sijjil. Faja‘alahum ka‘asfim ma’kul.",
            },
        },
        {
            "slug": "quraysh",
            "surah": 106,
            "start": 1,
            "end": 4,
            "arabic": "لِإِيلَافِ قُرَيْشٍ ۝ إِيلَافِهِمْ رِحْلَةَ الشِّتَاءِ وَالصَّيْفِ ۝ فَلْيَعْبُدُوا رَبَّ هَذَا الْبَيْتِ ۝ الَّذِي أَطْعَمَهُمْ مِنْ جُوعٍ وَآمَنَهُمْ مِنْ خَوْفٍ",
            "titles": {"ru": "Сура Курайш", "en": "Surah Quraysh", "uz": "Quraysh surasi"},
            "translations": {
                "ru": "Ради привычной безопасности курайшитов, их привычных зимних и летних путешествий, пусть они поклоняются Господу этого Дома, Который накормил их после голода и избавил от страха.",
                "en": "For the accustomed security of Quraysh, their winter and summer journeys, let them worship the Lord of this House, who fed them against hunger and granted them safety from fear.",
                "uz": "Qurayshning ulfat qilinishi, qish va yoz safarlariga ulfat qilinishi uchun ular shu Bayt Robbisiga ibodat qilsinlar. U ularni ochlikdan to‘ydirdi va qo‘rquvdan omon qildi.",
            },
            "transcriptions": {
                "ru": "Ли-иляфи Курайш. Иляфихим рихляташ-шитаи вас-сайф. Фаль-йа'буду Рабба хазаль-байт. Аллязи ат'амахум мин джу'ин ва аманахум мин хауф.",
                "en": "Li-ilafi Quraysh. Ilafihim rihlatash-shita’i was-sayf. Fal-ya‘budu Rabba hadhal-bayt. Alladhi at‘amahum min ju‘in wa amanahum min khawf.",
                "uz": "Li-iylafi Quraysh. Iylafihim rihlatash-shita’i vas-soyf. Falyabudu Robba hazal-bayt. Allaziy at‘amahum min ju‘iv va amanahum min xovf.",
            },
        },
    ]
)

DUA_TRANSCRIPTIONS = {
    "knowledge": {
        "en": "Rabbi zidni 'ilma.",
        "uz": "Robbi zidniy 'ilma.",
        "ru": "Рабби зидни 'ильма.",
    },
    "good-in-worlds": {
        "en": "Rabbana atina fid-dunya hasanatan wa fil-akhirati hasanatan wa qina 'adhaban-nar.",
        "uz": "Robbana atina fid-dunya hasanatan va fil-axiroti hasanatan va qina 'azaban-nar.",
        "ru": "Раббана атина фид-дунья хасанатан ва филь-ахирати хасанатан ва кина 'азабан-нар.",
    },
    "forgiveness": {
        "en": "Rabbighfir li, warhamni, wahdini, wa 'afini, warzuqni.",
        "uz": "Robbig‘fir liy, varhamniy, vahdiniy, va 'afiniy, varzuqniy.",
        "ru": "Раббигфир ли, вархамни, вахдини, ва 'афини, варзукни.",
    },
}
