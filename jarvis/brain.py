"""Jarvis'ning "miyasi": Claude bilan suhbat va asboblarni ishlatish."""

import anthropic

import pc_tools

SYSTEM_PROMPT = """Sen Jarvis'san - foydalanuvchining shaxsiy ovozli yordamchisi, "Temir odam" filmidagi Jarvis kabi.
Foydalanuvchini "ser" deb chaqir. Odobli, xotirjam, biroz hazilkash va juda foydali bo'l.

Muhim qoidalar:
- Javoblaring OVOZ CHIQARIB o'qiladi. Shuning uchun qisqa gapir (odatda 1-3 gap), markdown, ro'yxat,
  jadval, emoji va havolalar ishlatma. Raqam va qisqartmalarni o'qish oson qilib yoz.
- Foydalanuvchi qaysi tilda gapirsa, o'sha tilda javob ber (odatda o'zbekcha).
- Ovozni tanish xato qilishi mumkin: buyruq biroz noto'g'ri yozilgan bo'lsa, ma'nosini tushunishga harakat qil.
  Umuman tushunarsiz bo'lsa, qisqa qayta so'ra.
- Kompyuterda biror narsa qilish kerak bo'lsa, asboblardan foydalan va natijani bir gapda ayt.
- Yangi ma'lumot kerak bo'lsa (ob-havo, yangiliklar, kurslar), veb-qidiruvdan foydalan.
- Biror narsani o'rgatish so'ralsa, sodda tushuntir va kerak bo'lsa savol berib tekshir.
- Latency-sensitive; begin your visible answer immediately."""

MAX_TOOL_ROUNDS = 8


class Brain:
    def __init__(self, config: dict):
        self.cfg = config
        # Kalit .env faylidagi ANTHROPIC_API_KEY dan olinadi
        self.client = anthropic.Anthropic()
        self.messages: list = []
        self.tools = list(pc_tools.TOOLS)
        if config.get("web_search", True):
            self.tools.append({"type": "web_search_20260209", "name": "web_search", "max_uses": 3})

    def _system(self) -> str:
        facts = pc_tools.load_memory()
        if not facts:
            return SYSTEM_PROMPT
        return SYSTEM_PROMPT + "\n\nFoydalanuvchi haqida eslab qolganlaring:\n" + "\n".join(f"- {f}" for f in facts)

    def reset(self):
        """Yangi suhbat. Tarixni qisqartirish o'rniga butunlay yangidan boshlaymiz."""
        self.messages = []

    def ask(self, text: str, on_tool=None) -> str:
        if len(self.messages) > self.cfg.get("max_history_messages", 60):
            self.reset()
        turn_start = len(self.messages)
        self.messages.append({"role": "user", "content": text})
        try:
            return self._run_turn(turn_start, on_tool)
        except Exception:
            # Tarmoq yoki API xatosi: tugallanmagan navbatni olib tashlaymiz
            del self.messages[turn_start:]
            raise

    def _run_turn(self, turn_start: int, on_tool) -> str:
        for _ in range(MAX_TOOL_ROUNDS):
            response = self._call()

            if response.stop_reason == "refusal":
                # Rad etilgan navbatni tarixdan olib tashlaymiz - suhbat toza qoladi
                del self.messages[turn_start:]
                return "Kechirasiz ser, bu so'rovni bajara olmayman."

            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "pause_turn":
                continue  # server veb-qidiruvni davom ettiryapti
            if response.stop_reason != "tool_use":
                return _text_of(response) or "Bajarildi, ser."

            results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                if on_tool:
                    on_tool(block.name, block.input)
                output, is_error = pc_tools.run_tool(block.name, dict(block.input))
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": output, "is_error": is_error})
            self.messages.append({"role": "user", "content": results})

        return "Ser, bu vazifa juda ko'p qadam talab qildi. Boshqacha so'rab ko'ring."

    def _call(self):
        return self.client.beta.messages.create(
            model=self.cfg.get("model", "claude-opus-5-5"),
            max_tokens=16000,
            system=self._system(),
            messages=self.messages,
            tools=self.tools,
            output_config={"effort": self.cfg.get("effort", "low")},
            cache_control={"type": "ephemeral"},
            # Xavfsizlik filtri so'rovni rad etsa, server boshqa modelda qayta urinadi
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )


def _text_of(response) -> str:
    return " ".join(b.text for b in response.content if b.type == "text").strip()


def friendly_error(e: Exception) -> str:
    """API xatolarini foydalanuvchiga tushunarli tilga o'giradi."""
    if isinstance(e, anthropic.AuthenticationError):
        return "API kaliti noto'g'ri, ser. .env faylini tekshiring."
    if isinstance(e, anthropic.PermissionDeniedError):
        return "API kalitida ruxsat yetishmayapti, ser."
    if isinstance(e, anthropic.RateLimitError):
        return "Juda ko'p so'rov yuborildi, bir daqiqadan keyin qayta urinib ko'ring."
    if isinstance(e, anthropic.BadRequestError):
        return f"So'rovda xatolik bor: {e.message}"
    if isinstance(e, anthropic.APIStatusError):
        if e.status_code >= 500:
            return "Claude serverida vaqtincha muammo bor, birozdan keyin urinib ko'ring."
        return f"API xatosi: {e.message}"
    if isinstance(e, anthropic.APIConnectionError):
        return "Internetga ulanib bo'lmadi, ser."
    return f"Kutilmagan xatolik: {e}"
