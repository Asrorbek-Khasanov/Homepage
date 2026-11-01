"""J.A.R.V.I.S. - ovozli shaxsiy yordamchi.

Ishga tushirish:  python jarvis.py
"Jarvis" deb murojaat qiling va buyruq bering, yoki pastdagi qatorga yozing.
"""

import json
import math
import os
import queue
import re
import threading
import time
import tkinter as tk
from difflib import SequenceMatcher
from pathlib import Path
from tkinter import scrolledtext

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

import brain as brain_mod  # noqa: E402  (.env yuklangandan keyin)
import pc_tools  # noqa: E402

CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))

COLORS = {"idle": "#1e90ff", "listening": "#00e5ff", "thinking": "#ffb300",
          "speaking": "#00e676", "off": "#455a64", "error": "#ff5252"}
STATUS_TEXT = {"idle": "Kutyapman... \"Jarvis\" deb chaqiring", "listening": "Tinglayapman...",
               "thinking": "O'ylayapman...", "speaking": "Gapiryapman...",
               "off": "Mikrofon o'chiq - yozib buyruq bering", "error": "Xatolik"}


def strip_wake_word(text: str, wake_words: list[str]) -> str | None:
    """Matnda "Jarvis" so'zi bo'lsa, uni olib tashlab qolganini qaytaradi; bo'lmasa None."""
    words = re.findall(r"[\w'ʻʼ‘’-]+", text.lower())
    for i, word in enumerate(words):
        if any(SequenceMatcher(None, word, w).ratio() >= 0.75 for w in wake_words):
            return " ".join(words[:i] + words[i + 1:]).strip(" ,.!?")
    return None


class Jarvis:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.ui_queue: queue.Queue = queue.Queue()
        self.jobs: queue.Queue = queue.Queue()
        self.busy = threading.Event()
        self.mic_on = False
        self.mic_generation = 0  # eski tinglovchi oqim to'xtashi uchun
        self.active_until = 0.0
        self.state = "idle"
        self.phase = 0.0

        self._build_ui()
        pc_tools.announce = lambda text: self.jobs.put(("say", text))

        self.brain = None
        if not os.environ.get("ANTHROPIC_API_KEY"):
            self.log("Tizim", "ANTHROPIC_API_KEY topilmadi. jarvis papkasidagi .env fayliga kalitni yozing "
                              "(namuna: .env.example) va dasturni qayta oching.")
            self.set_state("error")
        else:
            self.brain = brain_mod.Brain(CONFIG)

        try:
            from voice import Mouth
            self.mouth = Mouth(CONFIG)
        except Exception as e:
            self.mouth = None
            self.log("Tizim", f"Ovoz chiqarish ishlamadi ({e}). Javoblar faqat matnda ko'rinadi.")

        try:
            from voice import Ears
            self.ears = Ears(CONFIG)
        except Exception as e:
            self.ears = None
            self.log("Tizim", f"Mikrofon ishlamadi ({e}). Buyruqlarni yozib bering.")

        threading.Thread(target=self._worker, daemon=True).start()
        if self.ears and self.brain:
            self.toggle_mic()
        elif not self.ears:
            self.set_state("off")

        self.root.after(30, self._tick)
        if self.brain:
            self.jobs.put(("say", "Assalomu alaykum, ser. Jarvis xizmatingizga tayyor."))

    # ---------------- Interfeys ----------------

    def _build_ui(self):
        r = self.root
        r.title("J.A.R.V.I.S.")
        r.geometry("520x720")
        r.configure(bg="#0a0f1a")
        r.minsize(420, 560)

        self.canvas = tk.Canvas(r, width=260, height=260, bg="#0a0f1a", highlightthickness=0)
        self.canvas.pack(pady=(18, 4))
        self.status = tk.Label(r, text="", fg="#90caf9", bg="#0a0f1a", font=("Segoe UI", 12))
        self.status.pack()

        self.chat = scrolledtext.ScrolledText(r, wrap=tk.WORD, bg="#0f1726", fg="#e3f2fd", relief=tk.FLAT,
                                              font=("Segoe UI", 11), insertbackground="#e3f2fd", height=14)
        self.chat.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)
        self.chat.tag_config("Siz", foreground="#80d8ff", font=("Segoe UI", 11, "bold"))
        self.chat.tag_config("Jarvis", foreground="#69f0ae", font=("Segoe UI", 11, "bold"))
        self.chat.tag_config("Tizim", foreground="#ffab91", font=("Segoe UI", 10, "italic"))
        self.chat.tag_config("Asbob", foreground="#b0bec5", font=("Segoe UI", 9))
        self.chat.configure(state=tk.DISABLED)

        row = tk.Frame(r, bg="#0a0f1a")
        row.pack(fill=tk.X, padx=14)
        self.entry = tk.Entry(row, bg="#0f1726", fg="#e3f2fd", relief=tk.FLAT, font=("Segoe UI", 12),
                              insertbackground="#e3f2fd")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=7)
        self.entry.bind("<Return>", lambda _: self.send_typed())
        self._button(row, "Yuborish", self.send_typed).pack(side=tk.LEFT, padx=(8, 0))

        bar = tk.Frame(r, bg="#0a0f1a")
        bar.pack(fill=tk.X, padx=14, pady=12)
        self.mic_button = self._button(bar, "🎤 Mikrofon: o'chiq", self.toggle_mic)
        self.mic_button.pack(side=tk.LEFT)
        self._button(bar, "⏹ To'xta", self.stop_speaking).pack(side=tk.LEFT, padx=8)
        self._button(bar, "🆕 Yangi suhbat", self.new_chat).pack(side=tk.LEFT)

    def _button(self, parent, text, command):
        return tk.Button(parent, text=text, command=command, bg="#1565c0", fg="white", relief=tk.FLAT,
                         activebackground="#1e88e5", activeforeground="white", font=("Segoe UI", 10),
                         padx=10, pady=5, cursor="hand2")

    def _draw_reactor(self):
        c, cx, cy = self.canvas, 130, 130
        c.delete("all")
        color = COLORS[self.state]
        speed = {"thinking": 0.25, "speaking": 0.18, "listening": 0.12}.get(self.state, 0.05)
        self.phase += speed
        pulse = (math.sin(self.phase) + 1) / 2
        for i, radius in enumerate((110, 88, 66)):
            c.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline=color,
                          width=2 if i else 3)
        # aylanib turuvchi segmentlar
        for k in range(6):
            start = (k * 60 + self.phase * 40) % 360
            c.create_arc(cx - 98, cy - 98, cx + 98, cy + 98, start=start, extent=28, style=tk.ARC,
                         outline=color, width=6)
        core = 30 + 12 * pulse
        c.create_oval(cx - core, cy - core, cx + core, cy + core, fill=color, outline="")
        c.create_oval(cx - core / 2, cy - core / 2, cx + core / 2, cy + core / 2, fill="white", outline="")

    def _tick(self):
        while not self.ui_queue.empty():
            kind, *data = self.ui_queue.get()
            if kind == "log":
                who, text = data
                self.chat.configure(state=tk.NORMAL)
                self.chat.insert(tk.END, f"{who}: ", who)
                self.chat.insert(tk.END, text + "\n\n")
                self.chat.configure(state=tk.DISABLED)
                self.chat.see(tk.END)
            elif kind == "state":
                self.state = data[0]
                self.status.configure(text=STATUS_TEXT[self.state], fg=COLORS[self.state])
        self._draw_reactor()
        self.root.after(40, self._tick)

    def log(self, who: str, text: str):
        self.ui_queue.put(("log", who, text))

    def set_state(self, state: str):
        self.ui_queue.put(("state", state))

    def idle_state(self):
        self.set_state("idle" if self.mic_on else "off")

    # ---------------- Tugmalar ----------------

    def send_typed(self):
        text = self.entry.get().strip()
        if text:
            self.entry.delete(0, tk.END)
            self.jobs.put(("ask", text))

    def toggle_mic(self):
        if not self.ears:
            self.log("Tizim", "Mikrofon mavjud emas.")
            return
        self.mic_on = not self.mic_on
        self.mic_button.configure(text="🎤 Mikrofon: yoqiq" if self.mic_on else "🎤 Mikrofon: o'chiq")
        self.idle_state()
        if self.mic_on:
            self.mic_generation += 1
            threading.Thread(target=self._listener, args=(self.mic_generation,), daemon=True).start()

    def stop_speaking(self):
        if self.mouth:
            self.mouth.stop()

    def new_chat(self):
        if self.brain:
            self.brain.reset()
        self.log("Tizim", "Yangi suhbat boshlandi.")

    # ---------------- Fon jarayonlari ----------------

    def _listener(self, generation: int):
        try:
            self.ears.calibrate()
        except Exception as e:
            self.log("Tizim", f"Mikrofonga ulanib bo'lmadi: {e}")
            self.mic_on = False
            self.set_state("off")
            return
        wake_words = [w.lower() for w in CONFIG.get("wake_words", ["jarvis"])]
        alive = lambda: self.mic_on and self.mic_generation == generation
        while alive():
            if self.busy.is_set():
                time.sleep(0.1)
                continue
            try:
                audio = self.ears.listen(lambda: not alive() or self.busy.is_set())
                if audio is None:
                    continue
                self.set_state("listening")
                text = self.ears.transcribe(audio).strip()
            except Exception as e:
                self.log("Tizim", f"Ovozni tanishda xatolik: {e}")
                time.sleep(1)
                continue
            finally:
                if not self.busy.is_set():
                    self.idle_state()
            if not text:
                continue

            if time.time() < self.active_until:
                command = strip_wake_word(text, wake_words)
                command = text if command is None else command
            else:
                command = strip_wake_word(text, wake_words)
                if command is None:
                    continue  # Jarvis'ga murojaat qilinmadi
            if command:
                self.jobs.put(("ask", command))
            else:
                self.jobs.put(("say", "Labbay, ser?"))

    def _worker(self):
        while True:
            kind, text = self.jobs.get()
            self.busy.set()
            try:
                if kind == "ask":
                    self.log("Siz", text)
                    reply = self._think(text)
                else:
                    reply = text
                self.log("Jarvis", reply)
                if self.mouth:
                    self.set_state("speaking")
                    try:
                        self.mouth.say(reply)
                    except Exception as e:
                        self.log("Tizim", f"Ovoz chiqarishda xatolik: {e}")
            finally:
                self.active_until = time.time() + CONFIG.get("follow_up_seconds", 20)
                self.busy.clear()
                self.idle_state()

    def _think(self, text: str) -> str:
        if not self.brain:
            return "Avval API kalitini sozlashingiz kerak, ser."
        self.set_state("thinking")
        try:
            return self.brain.ask(
                text, on_tool=lambda name, args: self.log("Asbob", f"⚙ {name} {json.dumps(args, ensure_ascii=False)}"))
        except Exception as e:
            self.set_state("error")
            return brain_mod.friendly_error(e)


def main():
    root = tk.Tk()
    Jarvis(root)
    root.mainloop()


if __name__ == "__main__":
    main()
