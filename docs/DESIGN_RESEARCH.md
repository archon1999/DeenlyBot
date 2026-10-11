# Deenly React va MUI dizayn yo‘nalishi

2026 yil 11 oktabr. Shaxsiy platforma, UZ/RU/EN, Django backend va React + MUI frontend.

Asosiy tavsiya — kabinet uchun Minimal UI vizual tartibi, ixcham navigatsiya va navbatlar uchun Linear, Qur’on va duolarni o‘qish uchun Quran.com tamoyillari. MUI custom theme bu yo‘nalishlarni bitta Deenly interfeysiga birlashtiradi. Bosh ekran foydalanuvchini bugungi o‘rganish, takrorlash va qazo amaliga olib boradi.

Bu hujjat dastlabki dizayn researchi va taklif etilgan spetsifikatsiyani saqlaydi.
Keyingi bosqichda foydalanuvchi taqdim etgan Minimal TypeScript v7.4.0 asosida
ishlaydigan React frontend qurildi. Full `vite-ts`dagi Course/App/Post/Account
kompozitsiyalari moslashtirildi, navigatsiya esa `cp_uz` LearningLayoutga yaqin
yuqori header va mobil tepadan ochiladigan menyuga o‘zgartirildi. Amaldagi tuzilma
va ishga tushirish ko‘rsatmalari [README](../README.md)da; quyidagi tavsiyalar
tarixiy research bo‘lib, joriy kodning to‘liq inventarizatsiyasi emas.

## Mos sayt namunalari

| Namuna | Ko‘rilgan interfeys va foydasi | Deenlyda qo‘llash |
| --- | --- | --- |
| [Minimal UI dashboard](https://minimals.cc/dashboard/) va [Course](https://minimals.cc/dashboard/course/) | Ochiq demo kabinet: yumaloq kartochkalar, keng oraliqlar, yon navigatsiya, sokin yashil active holatlar; Course sahifasi o‘rganishga mos ekran tartibini ko‘rsatadi. | Asosiy shell, Bugun sahifasi, arab tili darslari, progressning ko‘rinishi. Asosiy vizual namuna. |
| [MUI rasmiy dashboard](https://mui.com/material-ui/getting-started/templates/dashboard/) | Haqiqiy ishlaydigan custom-theme demo; sidebar, breadcrumb, kartochkalar, jadval va light/dark variantlar. | Bepul texnik boshlang‘ich baza va komponentlarning bir xil ishlashi. Demo biznes KPIlari o‘rniga Deenly amallari chiqadi. |
| [Quran.com o‘qish sahifasi](https://quran.com/al-fatihah) | Haqiqiy sura sahifasi: arabcha matn va tarjima ajratilgan, oyat raqami, o‘qish rejimi va lokal amallar. | Oyat, sura va duo o‘qish oynasi; kattalashtirish, transkripsiya, tarjima va saralanganlar. |
| [Linear display options](https://linear.app/docs/display-options) va [product sahifasi](https://linear.app/features) | Rasmiy mahsulot materiallari: ixcham list va grouped views, ko‘rinish sozlamalari, kam chalg‘ituvchi chrome. Signed-in Linear akkaunti tekshirilmagan. | Qazo navbati, kutubxona filtrlari va tez navigatsiya uchun vizual tartib. |

Minimalning dashboard va Course sahifalari demo sessiyada, MUI dashboard va Quran.com esa ochiq brauzerda vizual tekshirildi. Linear uchun rasmiy hujjatlar va mahsulot namunalari asos bo‘ldi. Marketing sahifasi bilan foydalanuvchi kabineti bir xil artefakt sifatida baholanmaydi.

## Uchta vizual yo‘nalish

| Yo‘nalish | Ko‘rinish | Qaysi ekranlarga mos |
| --- | --- | --- |
| Minimalga yaqin yumshoq kabinet | Yorug‘ neytral fon, oq yuzalar, 16–20 px radius, ko‘proq bo‘sh joy, emerald urg‘u. | Bugun, arab tili darslari, ismlar va progress. Butun platforma uchun tavsiya etilgan asos. |
| Linearga yaqin ixcham kabinet | Grafit yoki yorug‘ neytral yuzalar, kamroq radius, ingichka ajratgichlar, zichroq listlar. | Qazo va kutubxona. Dark mode shu yo‘nalishga yaqin bo‘lishi mumkin. |
| Quran.comga yaqin o‘qish muhiti | Markaziy matn ustuni, kuchli arabcha tipografiya, tarjima va transkripsiyaning aniq ajralishi. | Qur’on, duolar va uzun arab tili izohlari. Umumiy kabinet ichidagi maxsus o‘qish rejimi. |

Deenly uchun birinchi yo‘nalish asos bo‘ladi; navbatlar ikkinchi, o‘qish oynalari uchinchi yo‘nalishning tamoyillaridan foydalanadi. Har bir ekranda navigatsiya, button, spacing va rang tokenlari bir xil qoladi.

## Taklif etilgan dizayn tokenlari

Quyidagi qiymatlar Deenly uchun boshlang‘ich taklif; ular namuna saytlarining aynan o‘lchangan tokenlari emas. Yakuniy maketda uzun ruscha matnlar, o‘zbekcha apostroflar va arabcha harakatlar bilan tekshiriladi.

| Token | Yorug‘ tema | Qorong‘i tema |
| --- | --- | --- |
| Fon | `#F6F7F9` | `#141A21` |
| Asosiy yuzalar | `#FFFFFF` | `#1C252E` |
| Asosiy matn | `#1C252E` | `#F4F6F8` |
| Ikkinchi darajali matn | `#637381` | `#9BA7B2` |
| Asosiy urg‘u | `#087F5B` | `#5BE49B` |
| Dekorativ kichik urg‘u | Iliq oltin, masalan `#C29D58` | Shu oiladagi sokin oltin |

Asosiy UI shrifti uchun Inter kabi lotin va kirillni qamrab oladigan sans serif, arabcha o‘qish uchun Noto Naskh Arabic kabi alohida shrift tanlanadi. Font fayllari va litsenziyasi implementatsiyada tekshiriladi; kerakli glyphlar yuklanishi va harakatlar kesilmasligi amalda sinaladi. Qur’onning maxsus Mushaf shrifti kerak bo‘lsa, uni UI shriftiga aralashtirmaymiz.

Desktop sidebar 240–260 px, asosiy kabinet kontenti taxminan 1200 pxgacha, matnli reader 760–880 px atrofida bo‘ladi. Cardlar 16–20 px, button va inputlar 10–12 px radiusdan boshlanadi. Spacing 8 px tizimida; oddiy matn 16 px, arabcha matn o‘qish rejimida kattaroq va sozlanadigan bo‘ladi. Button balandligi mobil ekranda 44–48 px. Muhim holatlar rang bilan birga matn yoki ikon orqali ham ifodalanadi.

Soyalar asosan dialog, menu va boshqa overlaylarga beriladi. Oddiy cardlarda nozik border va yengil tonal farq yetarli. Geometrik ornament bo‘lsa kichik header yoki bo‘sh holat detalida ishlatiladi; o‘qish matnining foni sokin qoladi. Animatsiyalar 120–180 ms, reduced motion tanlovi hisobga olinadi.

## Bosh ekran

“Bugun” sahifasining asosiy kartochkasi “Davom ettirish” bo‘ladi. U navbatdagi ism yoki davom etayotgan arab tili darsini ko‘rsatadi va bitta aniq asosiy tugmaga ega bo‘ladi. Yonida muddati kelgan takrorlashlar va joriy qazo kartochkasi chiqadi. Pastda yaqindagi muhim sana va haftalik natija joylashadi.

Progress bloklari faqat mavjud yoki aniq yoziladigan ma’lumotni ko‘rsatadi: tanishtirilgan ismlar, tugatilgan arab tili darslari, quiz aniqligi va bajarilgan qazo. O‘qishga sarflangan soat yoki “strength” reytingi hozirgi modeldan olinmaydi; Minimal demo grafigini haqiqiy Deenly ko‘rsatkichi qilib chiqarmaymiz. Tarixiy qazoning quyi chegarasi belgilanmagan ekan, umumiy qolgan foiz o‘rniga kursor va bajarilgan son ko‘rsatiladi.

Minimalning to‘liq demo kabinetidagi kompaniya almashish, billing, ecommerce va boshqa korporativ navigatsiya shaxsiy platformaga kiritilmaydi. O‘zimizga kerak bo‘lgan sahifalar umumiy vizual iyerarxiyani saqlaydi.

## O‘rganish va o‘qish ekranlari

| Ekran | Tavsiya etilgan kompozitsiya | MUI orqali qurish |
| --- | --- | --- |
| Ismlar ro‘yxati | Ixcham card grid, arabcha ism, lokal nom va o‘rganish holati; navbatdagi ism ajratiladi. | Card, CardActionArea, Chip, Grid |
| Ism darsi | Markaziy kartochka, arabcha ism, transkripsiya, ma’no va izoh, aniq tasdiqlash tugmasi. | Paper, Typography, Stack, Button |
| Quiz | Bitta savol, to‘rtta katta javob varianti, tekshirilgandan keyin tushuntirish va qayta mashq. | Card yoki radio usulidagi javoblar, Button, Alert |
| Arab tili | Uch kategoriya, davom etayotgan dars, darslar ro‘yxati, bir bosqichdagi mavzu va kartochkalar. | Tabs, List, Accordion, LinearProgress |
| Qur’on va duo | O‘qish ustuni, arabcha matn, alohida transkripsiya va tarjima, ixcham o‘qish sozlamalari. | Container, Typography, Toolbar, Drawer, IconButton |
| Qazo | Joriy bitta namoz, bajarish tugmasi, qo‘lda qo‘shilgan va tarixiy navbat tablari; qo‘shish dialogi. | Paper, Tabs, List, Dialog, form komponentlari |
| Hisobotlar | Haftalik davr tanlash, haqiqiy ko‘rsatkichlar va kerak bo‘lsa sodda trend. | Card, Table va Community Charts |

UI tasdiqlashdan oldin ism progressini yozmaydi. Quizda tanlangan variant, server tekshirayotgan holat va to‘g‘ri/noto‘g‘ri natija alohida ko‘rinadi. Qazo tugmasi so‘rov ketayotganda band bo‘ladi; server navbat o‘zgarganini aytsa yangilangan kartochka chiqadi. Bu UI xatti-harakatlari backendning idempotent amallarini to‘ldiradi.

O‘qish rejimida arabcha matn `lang="ar"`, `dir="rtl"` bilan, butun UZ/RU/EN app esa LTR bilan ishlaydi. Readerda arabcha matn, transkripsiya va tarjimaning o‘lchamlari alohida boshqarilishi mumkin. Asosiy amallar matnni berkitmaydigan sticky toolbar yoki ixcham menu orqali chiqadi.

## Mobil ko‘rinish

Telefonda asosiy navigatsiya: Bugun, O‘rganish, Kutubxona, Qazo va Profil. Taqvim, hisobotlar va sozlamalar Profil yoki qo‘shimcha menu orqali ochiladi. Quiz va reader ekranida navigatsiya kichrayadi, asosiy kontent ustuvor bo‘ladi.

Grid bir ustunga o‘tadi, formalar to‘liq kenglikda chiqadi, dialog zarur bo‘lsa full screen bo‘ladi. Telegram Mini Appda safe area va BackButton hisobga olinadi. UZ/RU/EN satr uzunligi, katta shrift sozlamasi, 360 px atrofidagi tor ekran va qorong‘i tema bo‘yicha bir xil asosiy oqimlar tekshiriladi.

## MUI bilan amalga oshirish

MUIning `ThemeProvider`, palette, typography, spacing va component overrides orqali butun app uchun yagona tokenlar o‘rnatiladi. `MuiButton`, `MuiPaper`, `MuiCard`, `MuiTextField`, `MuiTabs` va `MuiDrawer`ni shu qatlamda moslashtirish kerak; har sahifaga alohida rang va radius qo‘yish dizaynning izchilligini buzadi. [MUI theming hujjatlari](https://mui.com/material-ui/customization/theming/)

Boshlang‘ich baza sifatida [MUI rasmiy free templates](https://mui.com/material-ui/getting-started/templates/) mos: custom tema va light/dark variantlari bor. Minimal to‘liq mahsuloti [MUI Storeda premium template](https://mui.com/store/items/minimal-dashboard/) sifatida berilgan; uning barcha ekranlari bepul source deb olinmaydi. [Minimal Free](https://mui.com/store/items/minimal-dashboard-free/) cheklangan bepul variant. Minimalning o‘zi backend va DBni bermaydi. [Minimal introduction](https://docs.minimals.cc/introduction/)

Tavsiya — rasmiy bepul MUI bazasi va o‘zimizning Deenly theme/componentlari; Minimal vizual reference bo‘ladi. Premium template kodini sotib olish alohida ixtiyoriy tanlov. MUI X Community va Pro/Premium qismlari litsenziyada farq qiladi; bu shaxsiy platforma uchun mavjud Community imkoniyatlari bilan boshlash mumkin. [MUI X](https://mui.com/x/introduction/)

## Dizaynni aniq maketga aylantirish

Keyingi dizayn deliverablei to‘rtta ekran bilan tekshiriladi: Bugun, ism quiz, Qur’on readeri va Qazo. Har biri desktop hamda mobileda ko‘rsatiladi; light/dark, bo‘sh ma’lumot, loading, xato va to‘ldirilgan holatlari bir dizayn tizimida bo‘ladi. Dastlabki maketdagi ma’lumotlar haqiqiy progress deb ko‘rsatilmaydi.

Tasdiqlash mezoni — tanlangan reference kayfiyati saqlanishi, bitta asosiy amal ravshanligi, arabcha matnning to‘g‘ri o‘qilishi, uzun lokal matnlarning sig‘ishi va MUI komponentlariga amalda mos kelishi. Bosh ekran uchun asosiy reference [Minimal Course](https://minimals.cc/dashboard/course/), o‘qish oynasi uchun [Quran.com](https://quran.com/al-fatihah) bo‘ladi; navigatsiya Linear materiallaridagi ixchamlikka yaqinlashtiriladi.
