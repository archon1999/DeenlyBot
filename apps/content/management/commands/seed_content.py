from django.core.management.base import BaseCommand
from django.db import transaction

from apps.content.models import (
    Dua,
    DuaTranslation,
    NameOfAllah,
    NameTranslation,
    QuranPassage,
    QuranPassageTranslation,
    QuranPassageType,
    ReligiousSource,
)
from apps.content.seed_duas import EXTRA_DUAS, localized_dua_transcription
from apps.content.seed_names import ALLAH_NAME, name_description
from apps.content.seed_quran import (
    DUA_TRANSCRIPTIONS,
    EXTRA_PASSAGES,
    PASSAGE_TRANSCRIPTIONS,
)
from apps.islamic_calendar.models import EventTranslation, IslamicEvent

FULL_SURAH_SLUGS = {"al-fatiha", "al-kafirun", "al-ikhlas", "al-falaq", "an-nas"}

# Concise learning meanings for the widely used traditional enumeration. They are
# intentionally stored with source metadata and can be reviewed or corrected in Admin.
NAMES = [
    ("الرَّحْمَنُ", "Ar-Rahman", "Всемилостивый", "The Entirely Merciful", "Barchaga Rahmli"),
    ("الرَّحِيمُ", "Ar-Rahim", "Особо Милосердный", "The Especially Merciful", "O‘ta Mehribon"),
    ("الْمَلِكُ", "Al-Malik", "Владыка", "The King", "Podshoh"),
    ("الْقُدُّوسُ", "Al-Quddus", "Пречистый", "The Most Holy", "Mutlaq Pok"),
    (
        "السَّلَامُ",
        "As-Salam",
        "Источник мира и безопасности",
        "The Source of Peace",
        "Tinchlik Manbai",
    ),
    (
        "الْمُؤْمِنُ",
        "Al-Mu'min",
        "Дарующий безопасность",
        "The Giver of Faith and Security",
        "Omonlik Beruvchi",
    ),
    (
        "الْمُهَيْمِنُ",
        "Al-Muhaymin",
        "Хранитель и Свидетель",
        "The Guardian and Witness",
        "Qo‘riqlovchi va Guvoh",
    ),
    ("الْعَزِيزُ", "Al-Aziz", "Могущественный", "The Almighty", "Qudratli"),
    ("الْجَبَّارُ", "Al-Jabbar", "Всеподчиняющий", "The Compeller", "Bo‘ysundiruvchi"),
    ("الْمُتَكَبِّرُ", "Al-Mutakabbir", "Обладатель величия", "The Supremely Great", "Ulug‘lik Sohibi"),
    ("الْخَالِقُ", "Al-Khaliq", "Творец", "The Creator", "Yaratuvchi"),
    ("الْبَارِئُ", "Al-Bari'", "Создатель из небытия", "The Originator", "Yo‘qdan Bor Qiluvchi"),
    ("الْمُصَوِّرُ", "Al-Musawwir", "Придающий облик", "The Fashioner", "Shakl Beruvchi"),
    (
        "الْغَفَّارُ",
        "Al-Ghaffar",
        "Многократно Прощающий",
        "The Constant Forgiver",
        "Ko‘p Mag‘firat Qiluvchi",
    ),
    ("الْقَهَّارُ", "Al-Qahhar", "Всепобеждающий", "The All-Subduer", "Mutlaq G‘olib"),
    ("الْوَهَّابُ", "Al-Wahhab", "Щедро Дарующий", "The Bestower", "Ne’matlarni Ato Etuvchi"),
    ("الرَّزَّاقُ", "Ar-Razzaq", "Дарующий удел", "The Provider", "Rizq Beruvchi"),
    (
        "الْفَتَّاحُ",
        "Al-Fattah",
        "Открывающий и Решающий",
        "The Opener and Judge",
        "Ochuvchi va Hukm Qiluvchi",
    ),
    ("اَلْعَلِيْمُ", "Al-Alim", "Всезнающий", "The All-Knowing", "Har Narsani Biluvchi"),
    ("الْقَابِضُ", "Al-Qabid", "Удерживающий", "The Withholder", "Toraytiruvchi"),
    ("الْبَاسِطُ", "Al-Basit", "Расширяющий", "The Extender", "Kengaytiruvchi"),
    ("الْخَافِضُ", "Al-Khafid", "Понижающий", "The Reducer", "Pasaytiruvchi"),
    ("الرَّافِعُ", "Ar-Rafi'", "Возвышающий", "The Exalter", "Yuksaltiruvchi"),
    ("الْمُعِزُّ", "Al-Mu'izz", "Дарующий честь", "The Giver of Honor", "Izzat Beruvchi"),
    ("المُذِلُّ", "Al-Mudhill", "Лишающий почета", "The Humiliator", "Xor Qiluvchi"),
    ("السَّمِيعُ", "As-Sami'", "Всеслышащий", "The All-Hearing", "Har Narsani Eshituvchi"),
    ("الْبَصِيرُ", "Al-Basir", "Всевидящий", "The All-Seeing", "Har Narsani Ko‘ruvchi"),
    ("الْحَكَمُ", "Al-Hakam", "Судья", "The Judge", "Hukm Qiluvchi"),
    ("الْعَدْلُ", "Al-Adl", "Совершенно Справедливый", "The Utterly Just", "Mutlaq Adolatli"),
    (
        "اللَّطِيفُ",
        "Al-Latif",
        "Добрый и Проницательный",
        "The Subtle and Kind",
        "Lutfli va Nozik Biluvchi",
    ),
    ("الْخَبِيرُ", "Al-Khabir", "Всеведущий", "The All-Aware", "Har Narsadan Xabardor"),
    ("الْحَلِيمُ", "Al-Halim", "Выдержанный", "The Forbearing", "Halim"),
    ("الْعَظِيمُ", "Al-Azim", "Великий", "The Magnificent", "Buyuk"),
    ("الْغَفُورُ", "Al-Ghafur", "Всепрощающий", "The All-Forgiving", "Mag‘firati Keng"),
    (
        "الشَّكُورُ",
        "Ash-Shakur",
        "Воздающий за благодарность",
        "The Appreciative",
        "Shukrni Taqdirlovchi",
    ),
    ("الْعَلِيُّ", "Al-Aliyy", "Всевышний", "The Most High", "Eng Oliy"),
    ("الْكَبِيرُ", "Al-Kabir", "Величайший", "The Most Great", "Eng Buyuk"),
    ("الْحَفِيظُ", "Al-Hafiz", "Хранитель", "The Preserver", "Saqlovchi"),
    ("المُقيِت", "Al-Muqit", "Поддерживающий", "The Sustainer", "Quvvat Beruvchi"),
    (
        "الْحسِيبُ",
        "Al-Hasib",
        "Достаточный и Ведущий счет",
        "The Reckoner and Sufficient",
        "Hisob Qiluvchi va Kifoya Etuvchi",
    ),
    ("الْجَلِيلُ", "Al-Jalil", "Величественный", "The Majestic", "Ulug‘vor"),
    ("الْكَرِيمُ", "Al-Karim", "Щедрый", "The Generous", "Karami Keng"),
    ("الرَّقِيبُ", "Ar-Raqib", "Наблюдающий", "The Watchful", "Kuzatuvchi"),
    ("الْمُجِيبُ", "Al-Mujib", "Отвечающий на мольбы", "The Responsive", "Duolarga Javob Beruvchi"),
    ("الْوَاسِعُ", "Al-Wasi'", "Всеобъемлющий", "The All-Encompassing", "Qamrovi Keng"),
    ("الْحَكِيمُ", "Al-Hakim", "Мудрый", "The All-Wise", "Hikmat Sohibi"),
    ("الْوَدُودُ", "Al-Wadud", "Любящий", "The Most Loving", "Sevuvchi"),
    ("الْمَجِيدُ", "Al-Majid", "Славный", "The Most Glorious", "Shon-Sharaf Sohibi"),
    ("الْبَاعِثُ", "Al-Ba'ith", "Воскрешающий", "The Resurrector", "Qayta Tiriltiruvchi"),
    ("الشَّهِيدُ", "Ash-Shahid", "Свидетель", "The Witness", "Guvoh"),
    ("الْحَقُّ", "Al-Haqq", "Истина", "The Truth", "Haq"),
    ("الْوَكِيلُ", "Al-Wakil", "Попечитель", "The Trustee", "Vakil"),
    ("الْقَوِيُّ", "Al-Qawiyy", "Всесильный", "The All-Strong", "Kuchli"),
    ("الْمَتِينُ", "Al-Matin", "Непоколебимый", "The Firm", "Mustahkam"),
    ("الْوَلِيُّ", "Al-Waliyy", "Покровитель", "The Protecting Friend", "Do‘st va Homiy"),
    ("الْحَمِيدُ", "Al-Hamid", "Достойный хвалы", "The Praiseworthy", "Maqtovga Loyiq"),
    ("الْمُحْصِي", "Al-Muhsi", "Все исчисляющий", "The All-Enumerating", "Barchasini Hisoblovchi"),
    ("الْمُبْدِئُ", "Al-Mubdi'", "Начинающий творение", "The Initiator", "Yaratishni Boshlovchi"),
    ("الْمُعِيدُ", "Al-Mu'id", "Возвращающий", "The Restorer", "Qaytaruvchi"),
    ("الْمُحْيِي", "Al-Muhyi", "Оживляющий", "The Giver of Life", "Hayot Beruvchi"),
    ("اَلْمُمِيتُ", "Al-Mumit", "Умерщвляющий", "The Bringer of Death", "O‘lim Beruvchi"),
    ("الْحَيُّ", "Al-Hayy", "Вечно Живой", "The Ever-Living", "Abadiy Tirik"),
    (
        "الْقَيُّومُ",
        "Al-Qayyum",
        "Самосущный и Поддерживающий",
        "The Self-Subsisting Sustainer",
        "Qoyim va Tutib Turuvchi",
    ),
    ("الْوَاجِدُ", "Al-Wajid", "Не испытывающий нужды", "The Perceiver and Finder", "Behojat Topuvchi"),
    ("الْمَاجِدُ", "Al-Maajid", "Обладатель благородства", "The Noble", "Sharaf Sohibi"),
    ("الْواحِدُ", "Al-Wahid", "Единственный", "The One", "Yagona"),
    ("اَلاَحَدُ", "Al-Ahad", "Единый", "The Unique", "Yakka-yu Yagona"),
    (
        "الصَّمَدُ",
        "As-Samad",
        "Тот, в Ком нуждаются все",
        "The Eternal Refuge",
        "Barchaning Hojatini Ravo Qiluvchi",
    ),
    ("الْقَادِرُ", "Al-Qadir", "Всемогущий", "The All-Powerful", "Har Narsaga Qodir"),
    (
        "الْمُقْتَدِرُ",
        "Al-Muqtadir",
        "Совершенно Могущественный",
        "The Perfectly Powerful",
        "Mutlaq Qudrat Sohibi",
    ),
    ("الْمُقَدِّمُ", "Al-Muqaddim", "Выдвигающий вперед", "The Expediter", "Oldinga Suruvchi"),
    ("الْمُؤَخِّرُ", "Al-Mu'akhkhir", "Отодвигающий", "The Delayer", "Orqaga Suruvchi"),
    ("الأوَّلُ", "Al-Awwal", "Первый", "The First", "Avval"),
    ("الآخِرُ", "Al-Akhir", "Последний", "The Last", "Oxir"),
    ("الظَّاهِرُ", "Az-Zahir", "Явный", "The Manifest", "Zohir"),
    ("الْبَاطِنُ", "Al-Batin", "Скрытый", "The Hidden", "Botin"),
    ("الْوَالِي", "Al-Wali", "Управляющий", "The Governor", "Boshqaruvchi"),
    ("الْمُتَعَالِي", "Al-Muta'ali", "Превознесенный", "The Most Exalted", "Eng Yuksak"),
    ("الْبَرُّ", "Al-Barr", "Источник добра", "The Source of Goodness", "Yaxshilik Sohibi"),
    (
        "التَّوَابُ",
        "At-Tawwab",
        "Принимающий покаяние",
        "The Accepter of Repentance",
        "Tavbalarni Qabul Qiluvchi",
    ),
    (
        "الْمُنْتَقِمُ",
        "Al-Muntaqim",
        "Воздающий по справедливости",
        "The Just Avenger",
        "Adolat bilan Jazo Beruvchi",
    ),
    ("العَفُوُّ", "Al-Afuww", "Стирающий грехи", "The Pardoner", "Gunohlarni Afv Etuvchi"),
    ("الرَّؤُوفُ", "Ar-Ra'uf", "Сострадательный", "The Most Kind", "O‘ta Shafqatli"),
    (
        "مَالِكُ الْمُلْكِ",
        "Malik al-Mulk",
        "Владыка всякой власти",
        "Master of the Kingdom",
        "Butun Mulk Egasi",
    ),
    (
        "ذُوالْجَلَالِ وَالإكْرَامِ",
        "Dhul-Jalali wal-Ikram",
        "Обладатель величия и щедрости",
        "Lord of Majesty and Honor",
        "Ulug‘lik va Karam Sohibi",
    ),
    (
        "الْمُقْسِطُ",
        "Al-Muqsit",
        "Беспристрастно Справедливый",
        "The Equitable",
        "Adolat bilan Hukm Qiluvchi",
    ),
    ("الْجَامِعُ", "Al-Jami'", "Собирающий", "The Gatherer", "Jamlovchi"),
    ("الْغَنِيُّ", "Al-Ghaniyy", "Ни в чем не Нуждающийся", "The Self-Sufficient", "Behojat"),
    ("الْمُغْنِي", "Al-Mughni", "Обогащающий", "The Enricher", "Boyituvchi"),
    ("اَلْمَانِعُ", "Al-Mani'", "Удерживающий и Защищающий", "The Preventer", "To‘suvchi"),
    (
        "الضَّارَ",
        "Ad-Darr",
        "Допускающий испытание",
        "The One Who Allows Adversity",
        "Zararni Taqdir Qiluvchi",
    ),
    ("النَّافِعُ", "An-Nafi'", "Приносящий пользу", "The Giver of Benefit", "Manfaat Beruvchi"),
    ("النُّورُ", "An-Nur", "Свет", "The Light", "Nur"),
    ("الْهَادِي", "Al-Hadi", "Ведущий прямым путем", "The Guide", "Hidoyat Beruvchi"),
    (
        "الْبَدِيعُ",
        "Al-Badi'",
        "Неподражаемый Создатель",
        "The Incomparable Originator",
        "Betakror Yaratuvchi",
    ),
    ("اَلْبَاقِي", "Al-Baqi", "Вечный", "The Everlasting", "Boqiy"),
    ("الْوَارِثُ", "Al-Warith", "Наследующий все", "The Inheritor", "Barcha Narsaning Vorisi"),
    (
        "الرَّشِيدُ",
        "Ar-Rashid",
        "Направляющий верно",
        "The Guide to the Right Way",
        "To‘g‘ri Yo‘lga Boshlovchi",
    ),
    ("الصَّبُورُ", "As-Sabur", "Безгранично Терпеливый", "The Most Patient", "O‘ta Sabrli"),
]
NAMES.insert(0, ALLAH_NAME)


def localized_name_transcription(transliteration, language):
    if language in {"en", "uz"}:
        return transliteration
    special = {
        "Allah": "Аллах",
        "Dhul-Jalali wal-Ikram": "Зуль-Джаляли валь-Икрам",
        "Malik al-Mulk": "Малик аль-Мульк",
    }
    if transliteration in special:
        return special[transliteration]
    text = transliteration.lower()
    for latin, cyrillic in (
        ("sh", "ш"),
        ("kh", "х"),
        ("dh", "з"),
        ("th", "с"),
        ("gh", "г"),
        ("ch", "ч"),
    ):
        text = text.replace(latin, cyrillic)
    chars = {
        "a": "а",
        "b": "б",
        "d": "д",
        "e": "е",
        "f": "ф",
        "g": "г",
        "h": "х",
        "i": "и",
        "j": "дж",
        "k": "к",
        "l": "л",
        "m": "м",
        "n": "н",
        "o": "о",
        "p": "п",
        "q": "к",
        "r": "р",
        "s": "с",
        "t": "т",
        "u": "у",
        "v": "в",
        "w": "в",
        "y": "й",
        "z": "з",
    }
    result = "".join(chars.get(char, char) for char in text)
    result = result[:1].upper() + result[1:]
    return result.replace("Ал-", "Аль-").replace(" ал-", " аль-")


PASSAGES = [
    {
        "slug": "ayat-al-kursi",
        "surah": 2,
        "start": 255,
        "end": 255,
        "arabic": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ ۚ لَهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَنْ ذَا الَّذِي يَشْفَعُ عِنْدَهُ إِلَّا بِإِذْنِهِ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَيْءٍ مِنْ عِلْمِهِ إِلَّا بِمَا شَاءَ ۚ وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ ۖ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ",
        "titles": {"ru": "Аят аль-Курси", "en": "Ayat al-Kursi", "uz": "Oyatul Kursiy"},
        "translations": {
            "ru": "Аллах — нет достойного поклонения, кроме Него, Живого, Поддерживающего жизнь. Им не овладевают ни дремота, ни сон. Ему принадлежит все на небесах и земле… Его Престол объемлет небеса и землю, и сохранение их не тяготит Его. Он — Возвышенный, Великий.",
            "en": "Allah—there is no deity worthy of worship except Him, the Ever-Living, the Sustainer. Neither drowsiness nor sleep overtakes Him. To Him belongs all in the heavens and the earth… His Kursi extends over the heavens and earth, and guarding them does not tire Him. He is the Most High, the Great.",
            "uz": "Alloh — Undan o‘zga ibodatga loyiq zot yo‘q. U Tirik va Qoyimdir. Uni mudroq ham, uyqu ham olmaydi. Osmonlaru yerdagi barcha narsa Unikidir… Uning Kursiysi osmonlaru yerni qamragan. Ularni saqlash Uni charchatmaydi. U Oliy va Buyukdir.",
        },
    },
    {
        "slug": "al-ikhlas",
        "surah": 112,
        "start": 1,
        "end": 4,
        "arabic": "قُلْ هُوَ اللَّهُ أَحَدٌ ۝ اللَّهُ الصَّمَدُ ۝ لَمْ يَلِدْ وَلَمْ يُولَدْ ۝ وَلَمْ يَكُنْ لَهُ كُفُوًا أَحَدٌ",
        "titles": {"ru": "Сура Аль-Ихляс", "en": "Surah Al-Ikhlas", "uz": "Ixlos surasi"},
        "translations": {
            "ru": "Скажи: «Он — Аллах Единый. Аллах Самодостаточный. Он не родил и не был рожден. И нет никого равного Ему».",
            "en": "Say: He is Allah, the One. Allah, the Eternal Refuge. He neither begets nor is born, and none is comparable to Him.",
            "uz": "Ayting: U Alloh Yagonadir. Alloh behojatdir. U tug‘magan va tug‘ilmagan. Unga hech kim teng emas.",
        },
    },
    {
        "slug": "al-falaq",
        "surah": 113,
        "start": 1,
        "end": 5,
        "arabic": "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ ۝ مِنْ شَرِّ مَا خَلَقَ ۝ وَمِنْ شَرِّ غَاسِقٍ إِذَا وَقَبَ ۝ وَمِنْ شَرِّ النَّفَّاثَاتِ فِي الْعُقَدِ ۝ وَمِنْ شَرِّ حَاسِدٍ إِذَا حَسَدَ",
        "titles": {"ru": "Сура Аль-Фаляк", "en": "Surah Al-Falaq", "uz": "Falaq surasi"},
        "translations": {
            "ru": "Скажи: «Ищу защиты у Господа рассвета от зла сотворенного Им, от зла ночи, когда она сгущается, от зла дующих на узлы и от зла завистника, когда он завидует».",
            "en": "Say: I seek refuge in the Lord of daybreak from the evil of what He created, from the evil of night when it grows dark, from those who blow on knots, and from an envier when they envy.",
            "uz": "Ayting: Tong Robbisidan U yaratgan narsalar yomonligidan, qorong‘u tushgan tun yomonligidan, tugunlarga dam soluvchilar yomonligidan va hasad qilgan hasadgo‘y yomonligidan panoh so‘rayman.",
        },
    },
    {
        "slug": "an-nas",
        "surah": 114,
        "start": 1,
        "end": 6,
        "arabic": "قُلْ أَعُوذُ بِرَبِّ النَّاسِ ۝ مَلِكِ النَّاسِ ۝ إِلَٰهِ النَّاسِ ۝ مِنْ شَرِّ الْوَسْوَاسِ الْخَنَّاسِ ۝ الَّذِي يُوَسْوِسُ فِي صُدُورِ النَّاسِ ۝ مِنَ الْجِنَّةِ وَالنَّاسِ",
        "titles": {"ru": "Сура Ан-Нас", "en": "Surah An-Nas", "uz": "Nos surasi"},
        "translations": {
            "ru": "Скажи: «Ищу защиты у Господа людей, Владыки людей, Бога людей, от зла отступающего искусителя, который нашептывает в груди людей, будь он из джиннов или людей».",
            "en": "Say: I seek refuge in the Lord of humanity, the King of humanity, the God of humanity, from the evil of the retreating whisperer who whispers into people's hearts, whether from jinn or people.",
            "uz": "Ayting: Odamlar Robbisidan, odamlar Podshohidan, odamlar Ilohidan, odamlar qalbiga vasvasa soluvchi chekinuvchi vasvasachining — jinlar va odamlardan bo‘lganining — yomonligidan panoh so‘rayman.",
        },
    },
]

PASSAGES.extend(EXTRA_PASSAGES)

DUAS = [
    {
        "slug": "knowledge",
        "arabic": "رَبِّ زِدْنِي عِلْمًا",
        "translit": "Rabbi zidni ‘ilma.",
        "titles": {"ru": "Дуа о знании", "en": "Dua for knowledge", "uz": "Ilm uchun duo"},
        "translations": {
            "ru": "Господь мой, приумножь мои знания.",
            "en": "My Lord, increase me in knowledge.",
            "uz": "Robbim, ilmimni ziyoda qil.",
        },
        "source": "Коран 20:114 / Quran 20:114",
    },
    {
        "slug": "good-in-worlds",
        "arabic": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ",
        "translit": "Rabbana atina fid-dunya hasanatan wa fil-akhirati hasanatan wa qina ‘adhaban-nar.",
        "titles": {
            "ru": "Благо в обоих мирах",
            "en": "Good in both worlds",
            "uz": "Ikki dunyo yaxshiligi",
        },
        "translations": {
            "ru": "Господь наш, даруй нам добро в этом мире и добро в Последней жизни и защити нас от мучений Огня.",
            "en": "Our Lord, grant us good in this world and good in the Hereafter and protect us from the punishment of the Fire.",
            "uz": "Robbimiz, bizga bu dunyoda ham yaxshilik, oxiratda ham yaxshilik ber va bizni do‘zax azobidan saqla.",
        },
        "source": "Коран 2:201 / Quran 2:201",
    },
    {
        "slug": "forgiveness",
        "arabic": "رَبِّ اغْفِرْ لِي وَارْحَمْنِي وَاهْدِنِي وَعَافِنِي وَارْزُقْنِي",
        "translit": "Rabbighfir li, warhamni, wahdini, wa ‘afini, warzuqni.",
        "titles": {
            "ru": "Дуа о прощении и милости",
            "en": "Dua for forgiveness and mercy",
            "uz": "Mag‘firat va rahmat duosi",
        },
        "translations": {
            "ru": "Господь мой, прости меня, помилуй меня, наставь меня, даруй мне благополучие и надели меня уделом.",
            "en": "My Lord, forgive me, have mercy on me, guide me, grant me well-being, and provide for me.",
            "uz": "Robbim, meni mag‘firat qil, menga rahm qil, hidoyat ber, ofiyat ber va rizqlantir.",
        },
        "source": "Сахих Муслим 2697 / Sahih Muslim 2697",
    },
]
DUAS.extend(EXTRA_DUAS)

EVENTS = [
    (
        "hijri-new-year",
        1,
        1,
        "month",
        [1],
        {
            "ru": ("Начало месяца Мухаррам", "Первый месяц исламского календаря."),
            "en": ("Beginning of Muharram", "The first month of the Islamic calendar."),
            "uz": ("Muharram oyi boshlanishi", "Islom taqvimining birinchi oyi."),
        },
    ),
    (
        "ashura",
        1,
        10,
        "virtuous",
        [1, 7],
        {
            "ru": ("День Ашура", "Десятый день Мухаррама."),
            "en": ("Day of Ashura", "The tenth day of Muharram."),
            "uz": ("Ashuro kuni", "Muharram oyining o‘ninchi kuni."),
        },
    ),
    (
        "ramadan",
        9,
        1,
        "month",
        [1, 7],
        {
            "ru": ("Начало Рамадана", "Расчетное начало месяца поста."),
            "en": ("Beginning of Ramadan", "Estimated beginning of the fasting month."),
            "uz": ("Ramazon boshlanishi", "Ro‘za oyining hisoblangan boshlanishi."),
        },
    ),
    (
        "last-ten-ramadan",
        9,
        21,
        "virtuous",
        [1],
        {
            "ru": (
                "Последние десять ночей Рамадана",
                "Начало особенно значимых последних ночей; Ляйлятуль-Кадр ищут в нечетные ночи.",
            ),
            "en": (
                "Last ten nights of Ramadan",
                "The especially significant final nights; Laylat al-Qadr is sought in the odd nights.",
            ),
            "uz": (
                "Ramazonning oxirgi o‘n kechasi",
                "Qadr kechasi toq kechalardan izlanadigan fazilatli davr.",
            ),
        },
    ),
    (
        "eid-fitr",
        10,
        1,
        "major",
        [1, 7],
        {
            "ru": ("Ид аль-Фитр", "Праздник разговения."),
            "en": ("Eid al-Fitr", "The festival marking the end of Ramadan."),
            "uz": ("Ramazon hayiti", "Ramazon yakunidagi hayit."),
        },
    ),
    (
        "arafah",
        12,
        9,
        "virtuous",
        [1, 7],
        {
            "ru": ("День Арафа", "Девятый день Зуль-хиджи."),
            "en": ("Day of Arafah", "The ninth day of Dhul Hijjah."),
            "uz": ("Arafa kuni", "Zulhijjaning to‘qqizinchi kuni."),
        },
    ),
    (
        "eid-adha",
        12,
        10,
        "major",
        [1, 7],
        {
            "ru": ("Ид аль-Адха", "Праздник жертвоприношения."),
            "en": ("Eid al-Adha", "The festival of sacrifice."),
            "uz": ("Qurbon hayiti", "Qurbonlik hayiti."),
        },
    ),
]


class Command(BaseCommand):
    help = "Idempotently seed the initial multilingual religious content"

    @transaction.atomic
    def handle(self, *args, **options):
        names_source, _ = ReligiousSource.objects.update_or_create(
            title="Traditional 99 Names enumeration",
            defaults={
                "url": "https://sunnah.com/tirmidhi:3507",
                "notes": "Widely used traditional enumeration. Concise learning meanings should be reviewed with a qualified scholar.",
                "is_verified": False,
            },
        )
        quran_source, _ = ReligiousSource.objects.update_or_create(
            title="The Quran — Arabic text and concise meaning",
            defaults={
                "url": "https://quran.com",
                "notes": "Arabic Quran text with concise, non-authoritative learning meanings in three languages.",
                "is_verified": False,
            },
        )
        hadith_source, _ = ReligiousSource.objects.update_or_create(
            title="Quran and authentic hadith references",
            defaults={
                "url": "https://sunnah.com",
                "notes": "Each dua contains its specific reference.",
                "is_verified": False,
            },
        )
        # Preserve existing progress FKs when introducing the proper Name ``Allah``
        # before the traditional 99-name enumeration in an already seeded database.
        if not NameOfAllah.objects.filter(transliteration="Allah").exists():
            for existing in NameOfAllah.objects.order_by("-order"):
                existing.order += 1
                existing.save(update_fields=["order"])

        for order, (arabic, transliteration, ru, en, uz) in enumerate(NAMES, 1):
            name, _ = NameOfAllah.objects.update_or_create(
                order=order,
                defaults={
                    "arabic": arabic,
                    "transliteration": transliteration,
                    "source": names_source,
                    "is_published": True,
                },
            )
            for language, meaning in {"ru": ru, "en": en, "uz": uz}.items():
                NameTranslation.objects.update_or_create(
                    name=name,
                    language=language,
                    defaults={
                        "meaning": meaning,
                        "transcription": localized_name_transcription(transliteration, language),
                        "description": name_description(transliteration, language),
                    },
                )

        for data in PASSAGES:
            passage, _ = QuranPassage.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "surah_number": data["surah"],
                    "ayah_start": data["start"],
                    "ayah_end": data["end"],
                    "passage_type": (
                        QuranPassageType.SURAH
                        if data["slug"] in FULL_SURAH_SLUGS
                        else QuranPassageType.AYAH
                    ),
                    "arabic_text": data["arabic"],
                    "source": quran_source,
                    "is_published": True,
                },
            )
            for language in ("ru", "en", "uz"):
                transcriptions = data.get("transcriptions") or PASSAGE_TRANSCRIPTIONS.get(
                    data["slug"], {}
                )
                QuranPassageTranslation.objects.update_or_create(
                    passage=passage,
                    language=language,
                    defaults={
                        "title": data["titles"][language],
                        "transcription": transcriptions.get(language, ""),
                        "translation": data["translations"][language],
                        "note": "Concise meaning for learning; consult a recognized tafsir for detailed interpretation.",
                    },
                )

        for data in DUAS:
            dua, _ = Dua.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "arabic_text": data["arabic"],
                    "transliteration": data["translit"],
                    "source": hadith_source,
                    "is_published": True,
                },
            )
            for language in ("ru", "en", "uz"):
                DuaTranslation.objects.update_or_create(
                    dua=dua,
                    language=language,
                    defaults={
                        "title": data["titles"][language],
                        "transcription": DUA_TRANSCRIPTIONS.get(data["slug"], {}).get(
                            language, localized_dua_transcription(data, language)
                        ),
                        "translation": data["translations"][language],
                        "note": data["source"],
                    },
                )

        for slug, month, day, event_type, reminder_days, translations in EVENTS:
            event, _ = IslamicEvent.objects.update_or_create(
                slug=slug,
                defaults={
                    "hijri_month": month,
                    "hijri_day": day,
                    "event_type": event_type,
                    "requires_local_confirmation": True,
                    "reminder_days": reminder_days,
                    "is_published": True,
                },
            )
            for language, (title, description) in translations.items():
                EventTranslation.objects.update_or_create(
                    event=event,
                    language=language,
                    defaults={"title": title, "description": description},
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(NAMES)} Names, {len(PASSAGES)} passages, {len(DUAS)} duas and {len(EVENTS)} events"
            )
        )
