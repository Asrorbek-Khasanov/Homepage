# Shaxsiy Homepage

Kreativ, zamonaviy shaxsiy sahifa. Hech qanday build talab qilinmaydi — oddiy HTML, CSS va JavaScript.

## Ishga tushirish

`index.html` faylini brauzerda oching yoki:

```bash
python3 -m http.server 8000
# http://localhost:8000
```

## Imkoniyatlar

- Preloader (0 → 100% hisoblagich)
- Maxsus kursor (`data-cursor="Matn"` bilan yorliq qo'shiladi)
- Sichqonchaga reaksiya qiluvchi interaktiv nuqtalar maydoni (hero)
- Harf-harf chiqib keluvchi katta sarlavha
- Scroll tezligiga qarab tezlashadigan va qiyshayadigan marquee
- Scroll bo'yicha so'z-so'z yonadigan "Men haqimda" matni
- Loyihalar ro'yxati — hover'da kursor ortidan suzuvchi rangli preview
- Ustma-ust yig'iladigan (sticky) xizmatlar kartalari
- Magnit tugmalar, Toshkent vaqti bilan jonli soat
- Qorong'i / yorug' mavzu, `prefers-reduced-motion` qo'llab-quvvatlanadi, mobilga moslashgan

## Moslashtirish

| Nima | Qayerda |
| --- | --- |
| Ism, matnlar, havolalar | `index.html` (`Ism Familiya`, `salom@example.com`, ijtimoiy tarmoqlar) |
| Loyihalar | `index.html` → `.work__item` (`data-color`, `data-color2` — preview ranglari) |
| Ranglar, shriftlar | `style.css` → `:root` tokenlari |
| Statistikalar | `data-count` atributlari |
