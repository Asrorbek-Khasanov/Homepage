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

## Imkoniyatlar

- UZ / EN / RU tillari: tanlov eslab qolinadi, `?lang=` orqali havola berish mumkin
- Hero: kursor atrofida “bog‘lanadigan” kristall panjara
- Tadqiqot bo‘limida jonli memristor modeli: pinch-gisterezis I–V egri chizig‘i va
  kislorod vakansiyalaridan filament hosil bo‘lishi (HRS ↔ LRS)
- Nashrlar ro‘yxati — hover’da material formulasi bilan suzuvchi karta
- Ustma-ust yig‘iladigan ko‘nikmalar kartalari, vaqt chizig‘i, magnit tugma
- Qorong‘i / yorug‘ mavzu, mobil moslashuv, `prefers-reduced-motion`

## Yangi nashr qo‘shish

`index.html` dagi `.pubs__list` ichiga yangi `<li class="pub reveal" ...>` qo‘shing.
`data-tag` — kartada ko‘rinadigan formula, `data-color` / `data-color2` — gradient ranglari.
