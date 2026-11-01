"""Jarvis kompyuterda bajaradigan amallar (brauzer, dasturlar, eslatmalar, taymer...).

Har bir funksiya oddiy matn qaytaradi - Claude shu natijani o'qib, sizga javob beradi.
Xavfli amallar (fayl o'chirish, buyruq satri, kompyuterni o'chirish) ataylab qo'shilmagan.
"""

import datetime
import json
import os
import platform
import re
import subprocess
import threading
import urllib.parse
import webbrowser
from pathlib import Path

import psutil

SYSTEM = platform.system()  # "Windows", "Darwin" (macOS), "Linux"
DATA_DIR = Path.home() / "Documents" / "Jarvis"
DATA_DIR.mkdir(parents=True, exist_ok=True)
NOTES_FILE = DATA_DIR / "eslatmalar.txt"
MEMORY_FILE = DATA_DIR / "xotira.json"

# Taymer tugaganda Jarvis gapirishi uchun - jarvis.py shu yerga funksiya qo'yadi
announce = lambda text: print(text)


# ---------- Xotira (Jarvis siz haqingizda eslab qoladigan narsalar) ----------

def load_memory() -> list[str]:
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def remember(fact: str) -> str:
    facts = load_memory()
    facts.append(fact.strip())
    MEMORY_FILE.write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8")
    return "Eslab qolindi."


# ---------- Brauzer ----------

def open_website(url: str) -> str:
    if not re.match(r"^https?://", url):
        url = "https://" + url
    webbrowser.open(url)
    return f"Ochildi: {url}"


def search_google(query: str) -> str:
    webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote(query))
    return f"Google'da qidirilmoqda: {query}"


def play_youtube(query: str) -> str:
    webbrowser.open("https://www.youtube.com/results?search_query=" + urllib.parse.quote(query))
    return f"YouTube'da ochildi: {query}"


# ---------- Dasturlar va papkalar ----------

# Ko'p ishlatiladigan dasturlarning tizimdagi nomlari
APP_ALIASES = {
    "Windows": {
        "kalkulyator": "calc", "calculator": "calc",
        "bloknot": "notepad", "notepad": "notepad",
        "paint": "mspaint", "explorer": "explorer", "fayllar": "explorer",
        "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
        "chrome": "chrome", "edge": "msedge", "telegram": "telegram",
        "sozlamalar": "ms-settings:", "settings": "ms-settings:",
        "vazifalar menejeri": "taskmgr", "task manager": "taskmgr",
        "spotify": "spotify", "vscode": "code", "vs code": "code",
    },
    "Darwin": {
        "kalkulyator": "Calculator", "calculator": "Calculator",
        "bloknot": "TextEdit", "notes": "Notes", "safari": "Safari",
        "chrome": "Google Chrome", "telegram": "Telegram", "finder": "Finder",
        "sozlamalar": "System Settings", "word": "Microsoft Word",
        "excel": "Microsoft Excel", "spotify": "Spotify", "vscode": "Visual Studio Code",
    },
    "Linux": {
        "kalkulyator": "gnome-calculator", "calculator": "gnome-calculator",
        "bloknot": "gedit", "fayllar": "nautilus", "chrome": "google-chrome",
        "firefox": "firefox", "telegram": "telegram-desktop", "vscode": "code",
    },
}


def open_app(name: str) -> str:
    key = name.strip().lower()
    target = APP_ALIASES.get(SYSTEM, {}).get(key, name.strip())
    # Faqat xavfsiz belgilar: harf, raqam, bo'sh joy, nuqta, chiziqcha, ikki nuqta
    if not re.fullmatch(r"[\w .:\-]+", target):
        return "Dastur nomi noto'g'ri."
    try:
        if SYSTEM == "Windows":
            os.startfile(target)  # noqa - faqat Windows'da mavjud
        elif SYSTEM == "Darwin":
            subprocess.Popen(["open", "-a", target])
        else:
            subprocess.Popen([target])
        return f"Ochildi: {name}"
    except (OSError, FileNotFoundError):
        return f"'{name}' dasturini topa olmadim. U o'rnatilganmi?"


FOLDERS = {
    "yuklamalar": "Downloads", "downloads": "Downloads",
    "hujjatlar": "Documents", "documents": "Documents",
    "ish stoli": "Desktop", "desktop": "Desktop",
    "rasmlar": "Pictures", "pictures": "Pictures",
    "musiqa": "Music", "music": "Music",
    "videolar": "Videos", "videos": "Videos",
    "jarvis": str(DATA_DIR),
}


def open_folder(name: str) -> str:
    sub = FOLDERS.get(name.strip().lower())
    if sub is None:
        return "Bunday papkani bilmayman. Mavjudlari: " + ", ".join(sorted(set(FOLDERS)))
    path = Path(sub) if Path(sub).is_absolute() else Path.home() / sub
    if not path.exists():
        return f"Papka topilmadi: {path}"
    if SYSTEM == "Windows":
        os.startfile(str(path))  # noqa
    elif SYSTEM == "Darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])
    return f"Ochildi: {path}"


# ---------- Vaqt va tizim holati ----------

OYLAR = ["yanvar", "fevral", "mart", "aprel", "may", "iyun",
         "iyul", "avgust", "sentyabr", "oktyabr", "noyabr", "dekabr"]
KUNLAR = ["dushanba", "seshanba", "chorshanba", "payshanba", "juma", "shanba", "yakshanba"]


def get_datetime() -> str:
    now = datetime.datetime.now()
    return (f"{now.year}-yil {now.day}-{OYLAR[now.month - 1]}, {KUNLAR[now.weekday()]}, "
            f"soat {now:%H:%M}")


def system_status() -> str:
    parts = [f"Protsessor yuklamasi {psutil.cpu_percent(interval=0.5):.0f}%",
             f"xotira (RAM) {psutil.virtual_memory().percent:.0f}% band"]
    battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
    if battery:
        state = "quvvatlanmoqda" if battery.power_plugged else "batareyadan ishlayapti"
        parts.append(f"batareya {battery.percent:.0f}%, {state}")
    disk = psutil.disk_usage(str(Path.home()))
    parts.append(f"diskda {disk.free / 1e9:.0f} GB bo'sh joy bor")
    return ", ".join(parts) + "."


# ---------- Taymer va eslatmalar ----------

def set_timer(minutes: float, label: str) -> str:
    if minutes <= 0 or minutes > 24 * 60:
        return "Taymer 0 dan 1440 daqiqagacha bo'lishi kerak."
    t = threading.Timer(minutes * 60, lambda: announce(f"Ser, vaqt bo'ldi: {label}"))
    t.daemon = True
    t.start()
    return f"Taymer {minutes:g} daqiqaga qo'yildi: {label}"


def save_note(text: str) -> str:
    with NOTES_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] {text.strip()}\n")
    return "Eslatma saqlandi."


def read_notes() -> str:
    if not NOTES_FILE.exists():
        return "Hali eslatmalar yo'q."
    lines = NOTES_FILE.read_text(encoding="utf-8").strip().splitlines()
    return "\n".join(lines[-10:]) or "Hali eslatmalar yo'q."


# ---------- Musiqa va ovoz balandligi ----------

_WIN_KEYS = {"play_pause": 0xB3, "next": 0xB0, "previous": 0xB1,
             "volume_up": 0xAF, "volume_down": 0xAE, "mute": 0xAD}


def media_control(action: str) -> str:
    if action not in _WIN_KEYS:
        return "Noma'lum amal."
    if SYSTEM == "Windows":
        import ctypes
        vk = _WIN_KEYS[action]
        repeat = 5 if action.startswith("volume") else 1  # har bosish ~2%
        for _ in range(repeat):
            ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
            ctypes.windll.user32.keybd_event(vk, 0, 2, 0)
        return "Bajarildi."
    if SYSTEM == "Darwin":
        scripts = {
            "volume_up": "set volume output volume ((output volume of (get volume settings)) + 10)",
            "volume_down": "set volume output volume ((output volume of (get volume settings)) - 10)",
            "mute": "set volume with output muted",
            "play_pause": 'tell application "Music" to playpause',
            "next": 'tell application "Music" to next track',
            "previous": 'tell application "Music" to previous track',
        }
        subprocess.run(["osascript", "-e", scripts[action]], check=False)
        return "Bajarildi."
    if action.startswith("volume") or action == "mute":
        arg = {"volume_up": "5%+", "volume_down": "5%-", "mute": "toggle"}[action]
        subprocess.run(["amixer", "-q", "set", "Master", arg], check=False)
        return "Bajarildi."
    subprocess.run(["playerctl", {"play_pause": "play-pause"}.get(action, action)], check=False)
    return "Bajarildi."


# ---------- Claude uchun asboblar ro'yxati ----------

def _schema(props: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": props, "required": required,
            "additionalProperties": False}


_S = {"type": "string"}

TOOLS = [
    {"name": "open_website", "description": "Brauzerda veb-saytni ochadi.",
     "input_schema": _schema({"url": {**_S, "description": "Sayt manzili, masalan kun.uz"}}, ["url"])},
    {"name": "search_google", "description": "Brauzerda Google qidiruvini ochadi (foydalanuvchi o'zi ko'rishi uchun).",
     "input_schema": _schema({"query": _S}, ["query"])},
    {"name": "play_youtube", "description": "YouTube'da video yoki musiqa qidiruvini ochadi.",
     "input_schema": _schema({"query": _S}, ["query"])},
    {"name": "open_app", "description": "Kompyuterdagi dasturni ochadi. Masalan: kalkulyator, bloknot, chrome, telegram, word, excel, sozlamalar.",
     "input_schema": _schema({"name": _S}, ["name"])},
    {"name": "open_folder", "description": "Papkani ochadi: yuklamalar, hujjatlar, ish stoli, rasmlar, musiqa, videolar, jarvis.",
     "input_schema": _schema({"name": _S}, ["name"])},
    {"name": "get_datetime", "description": "Hozirgi sana, hafta kuni va vaqtni qaytaradi.",
     "input_schema": _schema({}, [])},
    {"name": "system_status", "description": "Kompyuter holati: protsessor, xotira, batareya, disk.",
     "input_schema": _schema({}, [])},
    {"name": "set_timer", "description": "Taymer yoki eslatma qo'yadi; vaqti kelganda Jarvis ovoz chiqarib aytadi.",
     "input_schema": _schema({"minutes": {"type": "number"}, "label": {**_S, "description": "Nima haqida eslatish"}},
                             ["minutes", "label"])},
    {"name": "save_note", "description": "Matnli eslatmani faylga saqlaydi.",
     "input_schema": _schema({"text": _S}, ["text"])},
    {"name": "read_notes", "description": "Oxirgi saqlangan eslatmalarni o'qiydi.",
     "input_schema": _schema({}, [])},
    {"name": "remember", "description": "Foydalanuvchi haqidagi muhim, doimiy ma'lumotni xotiraga yozadi (ism, odatlar, afzalliklar). Foydalanuvchi 'eslab qol' desa ishlat.",
     "input_schema": _schema({"fact": _S}, ["fact"])},
    {"name": "media_control", "description": "Musiqa va ovoz balandligini boshqaradi.",
     "input_schema": _schema({"action": {"type": "string",
                                         "enum": list(_WIN_KEYS)}}, ["action"])},
]
for _t in TOOLS:
    _t["strict"] = True

HANDLERS = {
    "open_website": open_website, "search_google": search_google, "play_youtube": play_youtube,
    "open_app": open_app, "open_folder": open_folder, "get_datetime": get_datetime,
    "system_status": system_status, "set_timer": set_timer, "save_note": save_note,
    "read_notes": read_notes, "remember": remember, "media_control": media_control,
}


def run_tool(name: str, args: dict) -> tuple[str, bool]:
    """Asbobni ishga tushiradi. (natija, xatomi) qaytaradi."""
    handler = HANDLERS.get(name)
    if handler is None:
        return f"Noma'lum asbob: {name}", True
    try:
        return handler(**args), False
    except Exception as e:  # asbob xatosi suhbatni buzmasligi kerak
        return f"Xatolik: {e}", True
