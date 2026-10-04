# Asrorbek Hasanov — shaxsiy sahifa

Yarimo‘tkazgichlar fizikasi tadqiqotchisi uchun 3 tilli (UZ / EN / RU) kreativ homepage.
Build talab qilinmaydi: oddiy HTML, CSS va JavaScript.

## Ishga tushirish

`index.html` faylini brauzerda oching yoki:

```bash
python3 -m http.server 8000
# http://localhost:8000          — avtomatik til
# http://localhost:8000/?lang=en — aniq til
```

## Tuzilma

| Fayl | Vazifasi |
| --- | --- |
| `index.html` | Sahifa tuzilmasi (nashrlar ro‘yxati shu yerda) |
| `i18n.js` | Barcha matnlar 3 tilda — matnni o‘zgartirish uchun shu faylni tahrirlang |
| `style.css` | Dizayn; ranglar va shriftlar `:root` tokenlarida |
| `script.js` | Animatsiyalar, til almashtirish, memristor simulyatsiyasi |
| `assets/` | Portret va favicon |
| `papers/` | Maqolalarning PDF fayllari |

## Imkoniyatlar

- UZ / EN / RU tillari: tanlov eslab qolinadi, `?lang=` orqali havola berish mumkin
- Hero: kursor atrofida “bog‘lanadigan” kristall panjara
- Tadqiqot bo‘limida jonli memristor modeli: pinch-gisterezis I–V egri chizig‘i va
  kislorod vakansiyalaridan filament hosil bo‘lishi (HRS ↔ LRS)
- Nashrlar ro‘yxati — hover’da material formulasi bilan suzuvchi karta
- Ustma-ust yig‘iladigan ko‘nikmalar kartalari, vaqt chizig‘i, magnit tugma
- Ikki qorong‘i mavzu: Graphite (yashil) va Midnight (to‘q ko‘k), mobil moslashuv, `prefers-reduced-motion`

## Yangi nashr qo‘shish

1. PDF faylni `papers/` papkasiga qo‘ying.
2. `index.html` dagi `.pubs__list` ichida mavjud `<li class="pub reveal" ...>` blokini nusxalab, ro‘yxat boshiga qo‘ying.
3. Sarlavha, mualliflar (`<b>A. Hasanov</b>`), jurnal, yil, PDF va DOI havolasini almashtiring.
4. `data-tag` — kartada ko‘rinadigan formula, `data-color` / `data-color2` — gradient ranglari.
5. Tartib raqamlarini (`01`, `02`, …) va “Tanlangan nashrlar” sonini (`data-count`) yangilang.
