# J.A.R.V.I.S. — ovozli shaxsiy yordamchi

"Temir odam" filmidagi Jarvis kabi ishlaydigan, kompyuteringizga o'rnatiladigan ovozli yordamchi.
"Jarvis" deb chaqirasiz va o'zbekcha buyruq berasiz, u esa ovoz chiqarib javob beradi.

## Nimalar qila oladi

| Ayting | Nima bo'ladi |
|---|---|
| "Jarvis, soat necha?" | Vaqt va sanani aytadi |
| "Jarvis, kun.uz ni och" | Saytni brauzerda ochadi |
| "Jarvis, YouTube'da Sherali Jo'rayev qo'shiqlarini qo'y" | YouTube'da qidiradi |
| "Jarvis, kalkulyatorni och" | Dasturni ochadi (Word, Excel, Telegram, Chrome...) |
| "Jarvis, yuklamalar papkasini och" | Papkani ochadi |
| "Jarvis, 10 daqiqadan keyin choyni eslat" | Taymer qo'yadi va vaqti kelganda aytadi |
| "Jarvis, eslatma yoz: ertaga laboratoriyaga borish" | Eslatma saqlaydi |
| "Jarvis, ovozni balandlat" / "keyingi qo'shiq" | Ovoz va musiqani boshqaradi |
| "Jarvis, kompyuter holati qanday?" | Batareya, xotira va diskni aytadi |
| "Jarvis, Toshkentda ob-havo qanday?" | Internetdan qidirib javob beradi |
| "Jarvis, eslab qol: men fizik olimman" | Siz haqingizda eslab qoladi |
| "Jarvis, kvant tunnellanishini sodda tushuntir" | O'qituvchi sifatida tushuntiradi |

"Jarvis" deganingizdan keyin 20 soniya davomida qayta "Jarvis" demasdan suhbatni davom ettirsangiz bo'ladi.
Buyruqni pastdagi qatorga yozib yuborish ham mumkin.

## O'rnatish (Windows)

1. **Python o'rnating:** https://www.python.org/downloads/ (3.11 yoki undan yangi).
   O'rnatishda **"Add python.exe to PATH"** belgisini albatta qo'ying.
2. **API kalit oling:** https://console.anthropic.com/settings/keys sahifasida **Create Key** tugmasini bosing.
   Kalit `sk-ant-...` bilan boshlanadi. Bu kalit Claude Pro obunasidan alohida bo'lib, ishlatganingizcha
   to'lanadi, shuning uchun **Billing** bo'limida hisobingizni to'ldiring (masalan, 5$).
3. `jarvis` papkasidagi **`install.bat`** faylini ikki marta bosing. Kutubxonalar o'rnatiladi va
   Bloknot ochiladi: `ANTHROPIC_API_KEY=` qatoriga kalitingizni qo'yib, saqlang.
4. **`start.bat`** ni ikki marta bosing. Jarvis "Assalomu alaykum, ser" deb kutib oladi.

macOS yoki Linux'da `install.sh` va `start.sh` fayllaridan foydalaning.

## Sozlamalar (`config.json`)

| Sozlama | Ma'nosi |
|---|---|
| `wake_words` | Chaqiruv so'zlari ("jarvis" va uning tanilish variantlari) |
| `tts_voice` | Ovoz: `uz-UZ-SardorNeural` (erkak) yoki `uz-UZ-MadinaNeural` (ayol) |
| `tts_rate` | Gapirish tezligi, masalan `+10%` yoki `-10%` |
| `stt_engine` | `google` (internet orqali, yengil) yoki `whisper` (oflayn, `pip install faster-whisper` kerak) |
| `effort` | Claude qanchalik chuqur o'ylaydi: `low` tez, `medium` yoki `high` aqlliroq, lekin sekinroq |
| `mic_min_rms` | Mikrofon sezgirligi: shovqinli xonada oshiring, Jarvis eshitmasa kamaytiring |
| `follow_up_seconds` | "Jarvis" demasdan davom ettirish mumkin bo'lgan vaqt |

## Fayllar

- `jarvis.py` — oyna va asosiy dastur
- `brain.py` — Claude bilan suhbat (miya)
- `voice.py` — mikrofon (quloq) va ovoz (og'iz)
- `pc_tools.py` — kompyuterda bajariladigan amallar. Yangi imkoniyat qo'shish uchun shu faylga
  funksiya yozib, uni `TOOLS` va `HANDLERS` ro'yxatlariga qo'shasiz.

Eslatmalar va xotira `Hujjatlar/Jarvis` papkasida saqlanadi.

## Muammolar

- **Jarvis eshitmayapti:** Windows sozlamalarida (Privacy → Microphone) mikrofonga ruxsat bering,
  `config.json` da `mic_min_rms` ni 200 ga tushiring.
- **Ovoz chiqmayapti:** internet borligini tekshiring, chunki ovoz Microsoft serveri orqali yaratiladi.
- **"API kaliti noto'g'ri":** `.env` faylidagi kalitni tekshiring, ortiqcha bo'sh joy qolmasin.

Xavfsizlik uchun Jarvis fayllarni o'chira olmaydi, buyruq satrida ishlay olmaydi va kompyuterni o'chira olmaydi.
