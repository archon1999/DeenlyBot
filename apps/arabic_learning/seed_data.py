"""Initial RU/EN/UZ curriculum for Quran-focused Arabic study."""

from .models import ArabicItemType, ArabicLessonCategory


def T(ru, en, uz):
    return {"ru": ru, "en": en, "uz": uz}


def letter(arabic, forms, ru_name, latin_name, ru_sound, en_sound, uz_sound):
    return {
        "type": ArabicItemType.LETTER,
        "arabic": arabic,
        "translations": {
            "title": T(ru_name, latin_name, latin_name),
            "transcription": T(ru_name, latin_name, latin_name),
            "meaning": T(f"Буква {ru_name}", f"The letter {latin_name}", f"{latin_name} harfi"),
            "explanation": T(
                f"Формы: {forms}. Основное звучание: {ru_sound}.",
                f"Forms: {forms}. Core sound: {en_sound}.",
                f"Shakllari: {forms}. Asosiy tovushi: {uz_sound}.",
            ),
        },
        "metadata": {"forms": forms},
    }


def vocab(
    arabic,
    ru_transcription,
    latin_transcription,
    ru_meaning,
    en_meaning,
    uz_meaning,
    *,
    root="",
    reference="",
    item_type=ArabicItemType.WORD,
    note=None,
    missing_word="",
    missing_options=None,
):
    metadata = {}
    if missing_word:
        metadata["missing_word"] = missing_word
        metadata["missing_options"] = missing_options or []
    return {
        "type": item_type,
        "arabic": arabic,
        "root": root,
        "reference": reference,
        "metadata": metadata,
        "translations": {
            "title": T(ru_transcription, latin_transcription, latin_transcription),
            "transcription": T(ru_transcription, latin_transcription, latin_transcription),
            "meaning": T(ru_meaning, en_meaning, uz_meaning),
            "explanation": note or T("", "", ""),
        },
    }


def lesson(category, order, slug, titles, note, items, *, minutes=6, level=1):
    return {
        "category": category,
        "order": order,
        "slug": slug,
        "level": level,
        "minutes": minutes,
        "translations": {
            "title": titles,
            "summary": T(
                "Короткий последовательный урок с примерами и карточками для повторения.",
                "A short sequential lesson with examples and review cards.",
                "Misollar va takrorlash kartalari bilan qisqa ketma-ket dars.",
            ),
            "explanation": note,
        },
        "items": items,
    }


ALPHABET_LESSONS = [
    lesson(
        ArabicLessonCategory.ALPHABET,
        1,
        "alif-ba",
        T("Алиф и Ба", "Alif and Ba", "Alif va Ba"),
        T(
            "Алиф служит опорой для долгого ā и не соединяется со следующей буквой. Ба узнаётся по одной точке снизу.",
            "Alif supports the long ā and does not join the following letter. Ba has one dot below.",
            "Alif cho‘ziq ā uchun tayanch bo‘ladi va keyingi harfga ulanmaydi. Baning bir nuqtasi pastda.",
        ),
        [
            letter("ا", "ا ـا", "Алиф", "Alif", "долгое «а»", "long ā", "cho‘ziq ā"),
            letter("ب", "ب بـ ـبـ ـب", "Ба", "Ba", "б", "b", "b"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        2,
        "ta-tha",
        T("Та и Са", "Ta and Tha", "Ta va Tha"),
        T(
            "Буквы имеют одинаковую основу: у Та две точки сверху, у Са — три. Са произносится как английское th в think.",
            "The letters share one shape: Ta has two dots above and Tha has three. Tha sounds like th in think.",
            "Harflarning shakli bir xil: Tada tepada ikki, Thada uch nuqta bor. Tha inglizcha think so‘zidagi th kabi.",
        ),
        [
            letter("ت", "ت تـ ـتـ ـت", "Та", "Ta", "т", "t", "t"),
            letter("ث", "ث ثـ ـثـ ـث", "Са", "Tha", "межзубное «с»", "th in think", "tish oralig‘idagi th"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        3,
        "jim-ha",
        T("Джим и Ха", "Jim and Ha", "Jim va Ha"),
        T(
            "Джим имеет точку снизу. Ха пишется без точки и произносится мягким глубоким выдохом из середины горла.",
            "Jim has a dot below. Ha has no dot and is a soft breath from the middle throat.",
            "Jimning nuqtasi pastda. Ha nuqtasiz yozilib, halqum o‘rtasidan yumshoq nafas bilan aytiladi.",
        ),
        [
            letter("ج", "ج جـ ـجـ ـج", "Джим", "Jim", "дж", "j", "j"),
            letter("ح", "ح حـ ـحـ ـح", "Ха", "Ha", "глубокое мягкое «х»", "deep breathy h", "chuqur yumshoq h"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        4,
        "kha-dal",
        T("Ха и Даль", "Kha and Dal", "Xo va Dal"),
        T(
            "Ха отличается от предыдущей Ха точкой сверху. Даль не соединяется с последующей буквой.",
            "Kha differs from Ha by a dot above. Dal does not join the following letter.",
            "Xo oldingi Hadan tepadagi nuqta bilan farqlanadi. Dal keyingi harfga ulanmaydi.",
        ),
        [
            letter("خ", "خ خـ ـخـ ـخ", "Ха", "Kha", "х", "kh", "x"),
            letter("د", "د ـد", "Даль", "Dal", "д", "d", "d"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        5,
        "dhal-ra",
        T("Заль и Ра", "Dhal and Ra", "Zal va Ro"),
        T(
            "Обе буквы не соединяются со следующей. Заль имеет точку и звучит как th в английском this.",
            "Neither letter joins the following letter. Dhal has a dot and sounds like th in this.",
            "Ikkala harf ham keyingisiga ulanmaydi. Zal nuqtali bo‘lib, this so‘zidagi th kabi aytiladi.",
        ),
        [
            letter("ذ", "ذ ـذ", "Заль", "Dhal", "межзубное «з»", "th in this", "tish oralig‘idagi z"),
            letter("ر", "ر ـر", "Ра", "Ra", "р", "rolled r", "r"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        6,
        "zay-sin",
        T("Зай и Син", "Zay and Sin", "Zay va Sin"),
        T(
            "Зай не соединяется со следующей буквой. Син соединяется с обеих сторон и имеет три зубца.",
            "Zay does not join the next letter. Sin joins on both sides and has three teeth.",
            "Zay keyingi harfga ulanmaydi. Sin ikki tomondan ulanib, uch tishli yoziladi.",
        ),
        [
            letter("ز", "ز ـز", "Зай", "Zay", "з", "z", "z"),
            letter("س", "س سـ ـسـ ـس", "Син", "Sin", "с", "s", "s"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        7,
        "shin-sad",
        T("Шин и Сад", "Shin and Sad", "Shin va Sod"),
        T(
            "Шин похож на Син, но имеет три точки. Сад — твёрдая, наполненная версия звука с.",
            "Shin resembles Sin but has three dots. Sad is the emphatic, full form of s.",
            "Shin Singa o‘xshaydi, ammo uch nuqtali. Sod — qalin s tovushi.",
        ),
        [
            letter("ش", "ش شـ ـشـ ـش", "Шин", "Shin", "ш", "sh", "sh"),
            letter("ص", "ص صـ ـصـ ـص", "Сад", "Sad", "твёрдое «с»", "emphatic s", "qalin s"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        8,
        "dad-ta",
        T("Дад и Та", "Dad and Ta", "Dod va To"),
        T(
            "Дад — особый твёрдый звук арабского языка. Та также произносится твёрдо, с приподнятой задней частью языка.",
            "Dad is a distinctive emphatic Arabic sound. Ta is also emphatic, with the back of the tongue raised.",
            "Dod arab tiliga xos qalin tovushdir. To ham til orqasi ko‘tarilib qalin aytiladi.",
        ),
        [
            letter("ض", "ض ضـ ـضـ ـض", "Дад", "Dad", "твёрдое «д»", "emphatic d", "qalin d"),
            letter("ط", "ط طـ ـطـ ـط", "Та", "Ta", "твёрдое «т»", "emphatic t", "qalin t"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        9,
        "za-ayn",
        T("За и Айн", "Za and Ayn", "Zo va Ayn"),
        T(
            "За — твёрдый межзубный звук. Айн образуется сжатием в средней части горла и не имеет точного русского аналога.",
            "Za is an emphatic interdental sound. Ayn comes from the middle throat and has no exact English equivalent.",
            "Zo qalin tish oralig‘i tovushi. Ayn halqum o‘rtasidan chiqadi va o‘zbekchada aniq o‘xshashi yo‘q.",
        ),
        [
            letter("ظ", "ظ ظـ ـظـ ـظ", "За", "Za", "твёрдое межзубное «з»", "emphatic dh", "qalin tish oralig‘i z"),
            letter("ع", "ع عـ ـعـ ـع", "Айн", "Ayn", "горловой звук", "voiced throat sound", "halqum tovushi"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        10,
        "ghayn-fa",
        T("Гайн и Фа", "Ghayn and Fa", "G‘ayn va Fa"),
        T(
            "Гайн произносится в верхней части горла. Фа похожа на ф и имеет одну точку сверху.",
            "Ghayn is articulated high in the throat. Fa sounds like f and has one dot above.",
            "G‘ayn halqumning yuqori qismidan chiqadi. Fa f kabi aytilib, tepada bir nuqtasi bor.",
        ),
        [
            letter("غ", "غ غـ ـغـ ـغ", "Гайн", "Ghayn", "горловое «г»", "guttural gh", "g‘"),
            letter("ف", "ف فـ ـفـ ـف", "Фа", "Fa", "ф", "f", "f"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        11,
        "qaf-kaf",
        T("Каф и Кяф", "Qaf and Kaf", "Qof va Kaf"),
        T(
            "Каф произносится глубоко задней частью языка. Кяф — обычный мягкий звук к.",
            "Qaf is pronounced deeply with the back of the tongue. Kaf is the regular k sound.",
            "Qof tilning orqa qismi bilan chuqur aytiladi. Kaf oddiy k tovushidir.",
        ),
        [
            letter("ق", "ق قـ ـقـ ـق", "Каф", "Qaf", "глубокое «к»", "deep q", "chuqur q"),
            letter("ك", "ك كـ ـكـ ـك", "Кяф", "Kaf", "к", "k", "k"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        12,
        "lam-mim",
        T("Лям и Мим", "Lam and Mim", "Lam va Mim"),
        T(
            "Лям и Мим соединяются с обеих сторон и часто встречаются в слове Аллах и коранических окончаниях.",
            "Lam and Mim join on both sides and frequently occur in Allah's Name and Quranic endings.",
            "Lam va Mim ikki tomondan ulanadi, Alloh lafzi va Qur’oniy so‘zlarda ko‘p uchraydi.",
        ),
        [
            letter("ل", "ل لـ ـلـ ـل", "Лям", "Lam", "л", "l", "l"),
            letter("م", "م مـ ـمـ ـم", "Мим", "Mim", "м", "m", "m"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        13,
        "nun-ha",
        T("Нун и Ха", "Nun and Ha", "Nun va Ha"),
        T(
            "Нун имеет точку сверху. Конечная форма Ха заметно отличается от её начальной и средней форм.",
            "Nun has one dot above. Ha's final form differs visibly from its initial and medial forms.",
            "Nunning tepada bir nuqtasi bor. Haning oxirgi shakli bosh va o‘rta shaklidan ancha farq qiladi.",
        ),
        [
            letter("ن", "ن نـ ـنـ ـن", "Нун", "Nun", "н", "n", "n"),
            letter("ه", "ه هـ ـهـ ـه", "Ха", "Ha", "лёгкое «х»", "light h", "yengil h"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        14,
        "waw-ya",
        T("Вав и Йа", "Waw and Ya", "Vov va Ya"),
        T(
            "Вав не соединяется со следующей буквой и может обозначать w или долгий ū. Йа передаёт y или долгий ī.",
            "Waw does not join the next letter and can represent w or long ū. Ya represents y or long ī.",
            "Vov keyingi harfga ulanmaydi va w yoki cho‘ziq ūni bildiradi. Ya y yoki cho‘ziq īni bildiradi.",
        ),
        [
            letter("و", "و ـو", "Вав", "Waw", "в или долгое «у»", "w or long ū", "v yoki cho‘ziq ū"),
            letter("ي", "ي يـ ـيـ ـي", "Йа", "Ya", "й или долгое «и»", "y or long ī", "y yoki cho‘ziq ī"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        15,
        "special-forms",
        T("Хамза, та марбута и алиф максура", "Hamza, ta marbuta, and alif maqsura", "Hamza, ta marbuta va alif maqsura"),
        T(
            "Эти знаки не являются тремя новыми буквами алфавита, но постоянно встречаются в кораническом тексте и окончаниях слов.",
            "These are not three new alphabet letters, but they occur constantly in Quranic text and word endings.",
            "Bular alifbodagi uch yangi harf emas, ammo Qur’on matni va so‘z oxirlarida ko‘p uchraydi.",
        ),
        [
            letter("ء", "ء أ إ ؤ ئ", "Хамза", "Hamza", "твёрдый приступ гласного", "glottal stop", "bo‘g‘iz to‘sig‘i"),
            letter("ة", "ة ـة", "Та марбута", "Ta marbuta", "а/т в женском окончании", "a/t feminine ending", "ayollik oxiridagi a/t"),
            letter("ى", "ى ـى", "Алиф максура", "Alif maqsura", "долгое «а» в конце", "final long ā", "so‘z oxiridagi cho‘ziq ā"),
        ],
    ),
    lesson(
        ArabicLessonCategory.ALPHABET,
        16,
        "harakat-and-signs",
        T("Огласовки и знаки чтения", "Vowels and reading signs", "Harakatlar va o‘qish belgilari"),
        T(
            "Короткие гласные пишутся над или под буквой. Сукун убирает гласную, шадда удваивает согласную.",
            "Short vowels are written above or below a letter. Sukun removes the vowel and shadda doubles the consonant.",
            "Qisqa unlilar harf usti yoki ostiga yoziladi. Sukun unlini olib tashlaydi, shadda undoshni ikkilaydi.",
        ),
        [
            vocab("بَ", "ба", "ba", "Фатха: короткое «а»", "Fatha: short a", "Fatha: qisqa a", item_type=ArabicItemType.LETTER),
            vocab("بِ", "би", "bi", "Касра: короткое «и»", "Kasra: short i", "Kasra: qisqa i", item_type=ArabicItemType.LETTER),
            vocab("بُ", "бу", "bu", "Дамма: короткое «у»", "Damma: short u", "Damma: qisqa u", item_type=ArabicItemType.LETTER),
            vocab("بْ", "б", "b", "Сукун: без гласной", "Sukun: no vowel", "Sukun: unlisiz", item_type=ArabicItemType.LETTER),
            vocab("بّ", "бб", "bb", "Шадда: удвоение", "Shadda: doubling", "Shadda: ikkilanish", item_type=ArabicItemType.LETTER),
        ],
        minutes=8,
    ),
]


VOCABULARY_LESSONS = [
    lesson(
        ArabicLessonCategory.QURAN_VOCABULARY, 1, "allah-and-lord",
        T("Аллах и Господь", "Allah and Lord", "Alloh va Robb"),
        T("Три часто встречающихся слова, описывающих Господа и Его милость.", "Three frequent words referring to the Lord and His mercy.", "Robbimiz va Uning rahmatiga oid uch ko‘p uchraydigan so‘z."),
        [
            vocab("اللَّهُ", "Аллах", "Allah", "Аллах", "Allah", "Alloh", reference="1:1"),
            vocab("رَبٌّ", "Рабб", "Rabb", "Господь, Воспитывающий", "Lord and Sustainer", "Robb, tarbiya qiluvchi", root="ر ب ب", reference="1:2"),
            vocab("الرَّحْمَٰنُ", "Ар-Рахман", "Ar-Rahman", "Всемилостивый", "The Entirely Merciful", "Barchaga Rahmli", root="ر ح م", reference="1:1"),
        ],
    ),
    lesson(
        ArabicLessonCategory.QURAN_VOCABULARY, 2, "guidance-path-light",
        T("Наставление, путь и свет", "Guidance, path, and light", "Hidoyat, yo‘l va nur"),
        T("Слова, связанные с руководством Аллаха и прямым путём.", "Words connected to Allah's guidance and the straight path.", "Allohning hidoyati va to‘g‘ri yo‘lga oid so‘zlar."),
        [
            vocab("هُدًى", "худан", "hudan", "наставление", "guidance", "hidoyat", root="ه د ي", reference="2:2"),
            vocab("صِرَاطٌ", "сырат", "sirat", "путь", "path", "yo‘l", root="ص ر ط", reference="1:6"),
            vocab("نُورٌ", "нур", "nur", "свет", "light", "nur", root="ن و ر", reference="24:35"),
        ],
    ),
    lesson(
        ArabicLessonCategory.QURAN_VOCABULARY, 3, "worship-words",
        T("Слова поклонения", "Words of worship", "Ibodat so‘zlari"),
        T("Ключевые слова намаза, закята и обращения к Аллаху.", "Key words for prayer, zakat, and calling upon Allah.", "Namoz, zakot va Allohga iltijo qilishga oid asosiy so‘zlar."),
        [
            vocab("صَلَاةٌ", "салят", "salah", "молитва, намаз", "prayer", "namoz", root="ص ل و", reference="2:43"),
            vocab("زَكَاةٌ", "закят", "zakah", "очищающий обязательный дар", "obligatory purifying charity", "poklovchi farz sadaqa", root="ز ك و", reference="2:43"),
            vocab("دُعَاءٌ", "дуа", "dua", "мольба, обращение", "supplication", "duo, iltijo", root="د ع و", reference="25:77"),
        ],
    ),
    lesson(
        ArabicLessonCategory.QURAN_VOCABULARY, 4, "faith-and-piety",
        T("Вера и богобоязненность", "Faith and piety", "Iymon va taqvo"),
        T("Три центральных понятия веры, покорности и осознанности перед Аллахом.", "Three central ideas of faith, submission, and awareness of Allah.", "Iymon, bo‘ysunish va Allohdan ogohlikning uch asosiy tushunchasi."),
        [
            vocab("إِيمَانٌ", "иман", "iman", "вера", "faith", "iymon", root="أ م ن", reference="49:7"),
            vocab("تَقْوَى", "таква", "taqwa", "богобоязненность и осознанность", "piety and God-consciousness", "taqvo va Allohdan ogohlik", root="و ق ي", reference="2:197"),
            vocab("إِسْلَامٌ", "ислам", "islam", "покорность Аллаху", "submission to Allah", "Allohga bo‘ysunish", root="س ل م", reference="3:19"),
        ],
    ),
    lesson(
        ArabicLessonCategory.QURAN_VOCABULARY, 5, "mercy-forgiveness-repentance",
        T("Милость, прощение и покаяние", "Mercy, forgiveness, and repentance", "Rahmat, mag‘firat va tavba"),
        T("Слова надежды, возвращения и прощения.", "Words of hope, return, and forgiveness.", "Umid, qaytish va kechirimga oid so‘zlar."),
        [
            vocab("رَحْمَةٌ", "рахма", "rahmah", "милость", "mercy", "rahmat", root="ر ح م", reference="7:156"),
            vocab("مَغْفِرَةٌ", "магфира", "maghfirah", "прощение", "forgiveness", "mag‘firat", root="غ ف ر", reference="3:133"),
            vocab("تَوْبَةٌ", "тауба", "tawbah", "покаяние и возвращение", "repentance and return", "tavba va qaytish", root="ت و ب", reference="9:104"),
        ],
    ),
    lesson(
        ArabicLessonCategory.QURAN_VOCABULARY, 6, "world-hereafter-paradise",
        T("Этот мир и вечная жизнь", "This world and the Hereafter", "Dunyo va oxirat"),
        T("Слова о земной жизни, вечности и Рае.", "Words for worldly life, eternity, and Paradise.", "Dunyo hayoti, abadiyat va Jannatga oid so‘zlar."),
        [
            vocab("الدُّنْيَا", "ад-дунья", "ad-dunya", "ближняя, земная жизнь", "the worldly life", "dunyo hayoti", root="د ن و", reference="2:201"),
            vocab("الْآخِرَةُ", "аль-ахира", "al-akhirah", "Последняя жизнь", "the Hereafter", "oxirat", root="أ خ ر", reference="2:201"),
            vocab("جَنَّةٌ", "джанна", "jannah", "Рай, сад", "Paradise, garden", "Jannat, bog‘", root="ج ن ن", reference="2:25"),
        ],
    ),
    lesson(
        ArabicLessonCategory.QURAN_VOCABULARY, 7, "prophet-messenger-believer",
        T("Пророк, посланник и верующий", "Prophet, messenger, and believer", "Nabiy, rasul va mo‘min"),
        T("Частые обозначения носителей откровения и следующих за верой.", "Frequent terms for bearers of revelation and followers of faith.", "Vahiy yetkazuvchilar va iymon ahliga oid ko‘p uchraydigan atamalar."),
        [
            vocab("نَبِيٌّ", "набий", "nabiyy", "пророк", "prophet", "payg‘ambar", root="ن ب أ", reference="33:40"),
            vocab("رَسُولٌ", "расуль", "rasul", "посланник", "messenger", "rasul", root="ر س ل", reference="48:29"),
            vocab("مُؤْمِنٌ", "мумин", "mu'min", "верующий", "believer", "mo‘min", root="أ م ن", reference="2:285"),
        ],
    ),
    lesson(
        ArabicLessonCategory.QURAN_VOCABULARY, 8, "patience-gratitude-truth",
        T("Терпение, благодарность и правдивость", "Patience, gratitude, and truthfulness", "Sabr, shukr va rostgo‘ylik"),
        T("Три качества, многократно упоминаемые в Коране.", "Three qualities repeatedly emphasized in the Quran.", "Qur’onda ko‘p ta’kidlangan uch fazilat."),
        [
            vocab("صَبْرٌ", "сабр", "sabr", "терпение и стойкость", "patience and steadfastness", "sabr va matonat", root="ص ب ر", reference="2:153"),
            vocab("شُكْرٌ", "шукр", "shukr", "благодарность", "gratitude", "shukr", root="ش ك ر", reference="2:152"),
            vocab("صِدْقٌ", "сыдк", "sidq", "правдивость и искренность", "truthfulness and sincerity", "rostgo‘ylik va samimiyat", root="ص د ق", reference="33:24"),
        ],
    ),
    lesson(
        ArabicLessonCategory.QURAN_VOCABULARY, 9, "common-particles",
        T("Частые служебные слова", "Frequent particles", "Ko‘p uchraydigan yordamchi so‘zlar"),
        T("Короткие слова помогают увидеть отношения между частями аята.", "Short particles reveal relationships between parts of an ayah.", "Qisqa yordamchi so‘zlar oyat qismlari orasidagi aloqani ko‘rsatadi."),
        [
            vocab("فِي", "фи", "fi", "в, внутри", "in, within", "ichida, -da", reference="2:2"),
            vocab("مِنْ", "мин", "min", "из, от", "from", "-dan", reference="2:3"),
            vocab("إِلَى", "иля", "ila", "к, до", "to, toward", "-ga, tomon", reference="2:285"),
        ],
    ),
    lesson(
        ArabicLessonCategory.QURAN_VOCABULARY, 10, "famous-quran-phrases",
        T("Знаменитые коранические фразы", "Famous Quranic phrases", "Mashhur Qur’oniy iboralar"),
        T("Три фразы, часто читаемые и вспоминаемые мусульманами.", "Three phrases frequently recited and remembered by Muslims.", "Musulmonlar ko‘p o‘qib eslaydigan uch ibora."),
        [
            vocab("بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", "Бисмилляхир-Рахманир-Рахим", "Bismillahir-Rahmanir-Rahim", "С именем Аллаха, Всемилостивого, Милующего", "In the Name of Allah, the Entirely Merciful, the Especially Merciful", "Mehribon va Rahmli Alloh nomi bilan", reference="1:1", item_type=ArabicItemType.PHRASE, missing_word="اللَّهِ", missing_options=["اللَّهِ", "الْحَمْدُ", "النَّاسِ", "الْفَلَقِ"]),
            vocab("الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ", "Аль-хамду лилляхи Раббиль-алямин", "Al-hamdu lillahi Rabbil-'alamin", "Хвала Аллаху, Господу миров", "All praise is for Allah, Lord of all worlds", "Barcha hamd olamlar Robbi Allohgadir", reference="1:2", item_type=ArabicItemType.PHRASE, missing_word="الْحَمْدُ", missing_options=["الْحَمْدُ", "الْمُلْكُ", "الْحَقُّ", "النُّورُ"]),
            vocab("إِنَّا لِلَّهِ وَإِنَّا إِلَيْهِ رَاجِعُونَ", "Инна лилляхи ва инна иляйхи раджиун", "Inna lillahi wa inna ilayhi raji'un", "Поистине, мы принадлежим Аллаху и к Нему возвращаемся", "Indeed, we belong to Allah and to Him we return", "Albatta, biz Allohnikimiz va Unga qaytuvchimiz", reference="2:156", item_type=ArabicItemType.PHRASE, missing_word="رَاجِعُونَ", missing_options=["رَاجِعُونَ", "مُؤْمِنُونَ", "صَابِرُونَ", "شَاكِرُونَ"]),
        ],
        minutes=8,
    ),
    lesson(
        ArabicLessonCategory.QURAN_VOCABULARY, 11, "quran-supplications",
        T("Коранические мольбы", "Quranic supplications", "Qur’oniy duolar"),
        T("Короткие мольбы о знании, благе и избавлении от трудности.", "Short supplications for knowledge, goodness, and relief from hardship.", "Ilm, yaxshilik va qiyinchilikdan najot so‘raladigan qisqa duolar."),
        [
            vocab("رَبِّ زِدْنِي عِلْمًا", "Рабби зидни ильма", "Rabbi zidni 'ilma", "Господь мой, приумножь мои знания", "My Lord, increase me in knowledge", "Robbim, ilmimni ziyoda qil", reference="20:114", item_type=ArabicItemType.PHRASE, missing_word="عِلْمًا", missing_options=["عِلْمًا", "رِزْقًا", "نُورًا", "صَبْرًا"]),
            vocab("رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً", "Раббана атина фид-дунья хасана", "Rabbana atina fid-dunya hasanah", "Господь наш, даруй нам добро в этом мире", "Our Lord, grant us good in this world", "Robbimiz, bizga bu dunyoda yaxshilik ber", reference="2:201", item_type=ArabicItemType.PHRASE, missing_word="حَسَنَةً", missing_options=["حَسَنَةً", "رَحْمَةً", "مَغْفِرَةً", "حِكْمَةً"]),
            vocab("لَا إِلَٰهَ إِلَّا أَنْتَ سُبْحَانَكَ إِنِّي كُنْتُ مِنَ الظَّالِمِينَ", "Ля иляха илля Анта, субханака, инни кунту миназ-залимин", "La ilaha illa Anta, subhanaka, inni kuntu minaz-zalimin", "Нет достойного поклонения, кроме Тебя. Пречист Ты! Я был из несправедливых", "None is worthy of worship but You. Glory be to You; I was among the wrongdoers", "Sendan o‘zga ibodatga loyiq zot yo‘q. Sen poksan. Men zolimlardan bo‘ldim", reference="21:87", item_type=ArabicItemType.PHRASE, missing_word="سُبْحَانَكَ", missing_options=["سُبْحَانَكَ", "رَحْمَتَكَ", "مَغْفِرَتَكَ", "هِدَايَتَكَ"]),
        ],
        minutes=9,
    ),
    lesson(
        ArabicLessonCategory.QURAN_VOCABULARY, 12, "remembrance-and-trust",
        T("Поминание и упование", "Remembrance and trust", "Zikr va tavakkul"),
        T("Фразы прославления Аллаха, связывания планов с Его волей и полного упования.", "Phrases of glorification, connecting plans to Allah's will, and complete trust.", "Allohni poklash, rejani Uning irodasiga bog‘lash va to‘liq tavakkul iboralari."),
        [
            vocab("سُبْحَانَ اللَّهِ", "Субханаллах", "Subhanallah", "Пречист Аллах", "Glory be to Allah", "Alloh pokdir", reference="37:159", item_type=ArabicItemType.PHRASE, missing_word="اللَّهِ", missing_options=["اللَّهِ", "رَبِّي", "الْمَلِكِ", "الْحَقِّ"]),
            vocab("إِنْ شَاءَ اللَّهُ", "Ин ша Аллах", "In sha Allah", "Если пожелает Аллах", "If Allah wills", "Alloh xohlasa", reference="48:27", item_type=ArabicItemType.PHRASE, missing_word="شَاءَ", missing_options=["شَاءَ", "قَالَ", "عَلِمَ", "خَلَقَ"]),
            vocab("حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ", "Хасбуналлаху ва нималь-вакиль", "Hasbunallahu wa ni'mal-wakil", "Нам достаточно Аллаха, и Он — лучший Попечитель", "Allah is sufficient for us, and He is the best Trustee", "Bizga Alloh kifoya va U eng yaxshi Vakildir", reference="3:173", item_type=ArabicItemType.PHRASE, missing_word="الْوَكِيلُ", missing_options=["الْوَكِيلُ", "الْعَلِيمُ", "الْحَكِيمُ", "الْغَفُورُ"]),
        ],
        minutes=8,
    ),
]


GRAMMAR_LESSONS = [
    lesson(
        ArabicLessonCategory.GRAMMAR, 1, "three-word-classes",
        T("Три класса слов", "Three word classes", "So‘zlarning uch turi"),
        T("Классическая арабская грамматика делит слова на имя, глагол и частицу. «Имя» включает существительные и прилагательные.", "Classical Arabic divides words into noun, verb, and particle. The noun class includes nouns and adjectives.", "Klassik arab grammatikasi so‘zlarni ism, fe’l va harfga ajratadi. Ism turiga ot va sifatlar ham kiradi."),
        [
            vocab("كِتَابٌ", "китабун", "kitabun", "книга — имя", "book — noun", "kitob — ism", item_type=ArabicItemType.EXAMPLE),
            vocab("خَلَقَ", "халяка", "khalaqa", "Он создал — глагол", "He created — verb", "U yaratdi — fe’l", item_type=ArabicItemType.EXAMPLE),
            vocab("فِي", "фи", "fi", "в — частица/предлог", "in — particle/preposition", "ichida — harf/ko‘makchi", item_type=ArabicItemType.EXAMPLE),
        ],
    ),
    lesson(
        ArabicLessonCategory.GRAMMAR, 2, "definite-article",
        T("Определённый артикль ال", "The definite article ال", "ال aniqlik artikli"),
        T("Артикль ال делает имя определённым. Перед солнечной буквой звук л assimilируется, но продолжает писаться.", "The article ال makes a noun definite. Before a sun letter, the l sound assimilates although it remains written.", "ال artikli ismni aniq qiladi. Quyosh harfidan oldin l tovushi singishadi, ammo yozuvda qoladi."),
        [
            vocab("الْقَمَرُ", "аль-камар", "al-qamar", "луна — лунная буква", "the moon — moon letter", "oy — qamariy harf", item_type=ArabicItemType.EXAMPLE),
            vocab("الشَّمْسُ", "аш-шамс", "ash-shams", "солнце — солнечная буква", "the sun — sun letter", "quyosh — shamsiy harf", item_type=ArabicItemType.EXAMPLE),
        ],
    ),
    lesson(
        ArabicLessonCategory.GRAMMAR, 3, "gender-ta-marbuta",
        T("Род и та марбута", "Gender and ta marbuta", "Jins va ta marbuta"),
        T("Окончание ة часто указывает на женский род. При паузе оно обычно звучит как а/ah, а в связной конструкции — как t.", "The ending ة often marks feminine gender. In pause it usually sounds a/ah, and in connected construction it sounds t.", "ة oxiri ko‘pincha ayol jinsini bildiradi. To‘xtalganda a/ah, bog‘lanishda t kabi eshitiladi."),
        [
            vocab("رَحْمَةٌ", "рахматун", "rahmatun", "милость — женский род", "mercy — feminine", "rahmat — ayol jinsi", item_type=ArabicItemType.EXAMPLE),
            vocab("رَحْمَةُ اللَّهِ", "рахматуллах", "rahmatullah", "милость Аллаха; ة звучит как т", "Allah's mercy; ة is pronounced t", "Allohning rahmati; ة t bo‘lib aytiladi", item_type=ArabicItemType.EXAMPLE),
        ],
    ),
    lesson(
        ArabicLessonCategory.GRAMMAR, 4, "pronouns",
        T("Личные местоимения", "Personal pronouns", "Kishilik olmoshlari"),
        T("Арабские местоимения различают лицо, число и род. Они могут быть отдельными или присоединяться к слову.", "Arabic pronouns distinguish person, number, and gender. They can stand alone or attach to a word.", "Arab olmoshlari shaxs, son va jinsni ajratadi. Ular alohida yoki so‘zga qo‘shilib keladi."),
        [
            vocab("هُوَ", "хува", "huwa", "он", "he", "u (erkak)", item_type=ArabicItemType.EXAMPLE),
            vocab("هُمْ", "хум", "hum", "они", "they", "ular", item_type=ArabicItemType.EXAMPLE),
            vocab("رَبُّهُمْ", "раббухум", "rabbuhum", "их Господь", "their Lord", "ularning Robbi", item_type=ArabicItemType.EXAMPLE),
        ],
    ),
    lesson(
        ArabicLessonCategory.GRAMMAR, 5, "prepositions",
        T("Предлоги и окончания", "Prepositions and endings", "Ko‘makchilar va oxirlar"),
        T("После предлога имя получает родительный статус. В огласованном тексте это часто видно по касре.", "After a preposition, a noun takes the genitive state, often shown by kasra in vocalized text.", "Ko‘makchidan keyin ism qaratqich holatiga o‘tadi; harakatli matnda bu ko‘pincha kasra bilan ko‘rinadi."),
        [
            vocab("فِي الْأَرْضِ", "филь-арды", "fil-ardi", "на земле; после في стоит касра", "on earth; kasra follows في", "yerda; في dan keyin kasra", reference="2:11", item_type=ArabicItemType.EXAMPLE),
            vocab("مِنَ السَّمَاءِ", "минас-самаи", "minas-sama'i", "с неба", "from the sky", "osmondan", reference="2:22", item_type=ArabicItemType.EXAMPLE),
        ],
    ),
    lesson(
        ArabicLessonCategory.GRAMMAR, 6, "idafa",
        T("Идафа: связь принадлежности", "Idafa: possession", "Izofa: qarashlilik"),
        T("Два имени рядом могут образовать значение «что-то кого-то». Первое обычно не принимает артикль, второе определяет всю конструкцию.", "Two adjacent nouns can mean “something of someone.” The first normally lacks the article, and the second determines the phrase.", "Ikki yonma-yon ism «kimningdir nimasi» ma’nosini beradi. Birinchisi odatda artiklsiz, ikkinchisi birikmani aniqlaydi."),
        [
            vocab("رَسُولُ اللَّهِ", "расулуллах", "rasulullah", "Посланник Аллаха", "Messenger of Allah", "Allohning Rasuli", item_type=ArabicItemType.EXAMPLE),
            vocab("عَبْدُ اللَّهِ", "абдуллах", "abdullah", "раб Аллаха", "servant of Allah", "Allohning bandasi", item_type=ArabicItemType.EXAMPLE),
        ],
    ),
    lesson(
        ArabicLessonCategory.GRAMMAR, 7, "nominal-sentence",
        T("Именное предложение", "Nominal sentence", "Ismiy gap"),
        T("Именное предложение начинается с имени. В настоящем времени связка «есть» обычно не произносится.", "A nominal sentence begins with a noun. In the present tense, the verb “to be” is usually not stated.", "Ismiy gap ism bilan boshlanadi. Hozirgi zamonda «bo‘lmoq» bog‘lamasi odatda aytilmaydi."),
        [
            vocab("اللَّهُ غَفُورٌ", "Аллаху гафурун", "Allahu ghafurun", "Аллах — Прощающий", "Allah is Forgiving", "Alloh Mag‘firat qiluvchidir", item_type=ArabicItemType.EXAMPLE),
            vocab("اللَّهُ عَلِيمٌ", "Аллаху алимун", "Allahu 'alimun", "Аллах — Знающий", "Allah is Knowing", "Alloh Biluvchidir", item_type=ArabicItemType.EXAMPLE),
        ],
    ),
    lesson(
        ArabicLessonCategory.GRAMMAR, 8, "verbal-sentence",
        T("Глагольное предложение", "Verbal sentence", "Fe’liy gap"),
        T("Глагольное предложение обычно начинается с действия, после которого называется исполнитель и затем объект.", "A verbal sentence commonly begins with the action, followed by the doer and then the object.", "Fe’liy gap odatda harakat bilan boshlanib, undan so‘ng bajaruvchi va to‘ldiruvchi keladi."),
        [
            vocab("خَلَقَ اللَّهُ السَّمَاوَاتِ", "халякаллахус-самават", "khalaqallahu as-samawat", "Аллах создал небеса", "Allah created the heavens", "Alloh osmonlarni yaratdi", item_type=ArabicItemType.EXAMPLE),
            vocab("يَهْدِي اللَّهُ", "яхдиллах", "yahdillahu", "Аллах наставляет", "Allah guides", "Alloh hidoyat qiladi", item_type=ArabicItemType.EXAMPLE),
        ],
    ),
    lesson(
        ArabicLessonCategory.GRAMMAR, 9, "roots-and-patterns",
        T("Корни и модели слов", "Roots and word patterns", "O‘zak va so‘z qoliplari"),
        T("Многие арабские слова строятся вокруг трёх согласных корня. Модель добавляет оттенок значения и грамматическую функцию.", "Many Arabic words are built around three root consonants. A pattern adds meaning and grammatical function.", "Ko‘p arabcha so‘zlar uch undoshli o‘zak atrofida quriladi. Qolip ma’no va grammatik vazifa qo‘shadi."),
        [
            vocab("كَتَبَ", "катаба", "kataba", "он написал", "he wrote", "u yozdi", root="ك ت ب", item_type=ArabicItemType.EXAMPLE),
            vocab("كِتَابٌ", "китабун", "kitabun", "книга", "book", "kitob", root="ك ت ب", item_type=ArabicItemType.EXAMPLE),
            vocab("مَكْتُوبٌ", "мактубун", "maktubun", "написанный", "written", "yozilgan", root="ك ت ب", item_type=ArabicItemType.EXAMPLE),
        ],
        minutes=8,
    ),
    lesson(
        ArabicLessonCategory.GRAMMAR, 10, "quranic-script-facts",
        T("Особенности коранического письма", "Features of Quranic script", "Qur’on yozuvi xususiyatlari"),
        T("Османский рисунок Корана сохраняет традиционное написание. Маленький вертикальный алиф указывает долгий ā, а знаки остановки помогают выбрать место паузы.", "The Uthmani Quranic script preserves traditional spelling. A dagger alif marks long ā, and stop signs guide where to pause.", "Qur’onning Usmoniy yozuvi an’anaviy imloni saqlaydi. Kichik tik alif cho‘ziq āni, vaqf belgilari esa to‘xtash joyini ko‘rsatadi."),
        [
            vocab("الرَّحْمَٰنِ", "ар-Рахмани", "ar-Rahmani", "малый алиф ٰ обозначает долгий ā", "the dagger alif ٰ marks long ā", "kichik ٰ alif cho‘ziq āni bildiradi", reference="1:1", item_type=ArabicItemType.FACT),
            vocab("م ۚ لَا", "мим — пауза — ля", "mim — pause — la", "знак ۚ указывает допустимую остановку с предпочтением продолжить", "ۚ marks a permissible stop where continuation is preferred", "ۚ davom etish afzal bo‘lgan joiz to‘xtashni bildiradi", reference="2:255", item_type=ArabicItemType.FACT),
        ],
        minutes=8,
    ),
]


ARABIC_LESSONS = [*ALPHABET_LESSONS, *VOCABULARY_LESSONS, *GRAMMAR_LESSONS]
