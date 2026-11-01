"""Quloq va og'iz: mikrofondan gapni yozib olish, matnga aylantirish va javobni ovoz chiqarib o'qish."""

import asyncio
import os
import tempfile
import time

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000
BLOCK = 480  # 30 ms


class Ears:
    """Mikrofonni tinglaydi va gap tugaganda audio bo'lagini qaytaradi."""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.threshold = cfg.get("mic_min_rms", 350)
        self._whisper = None

    def calibrate(self, seconds: float = 1.0):
        """Xonadagi shovqin darajasini o'lchab, sezgirlikni moslaydi."""
        audio = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
        sd.wait()
        noise = _rms(audio)
        self.threshold = max(self.cfg.get("mic_min_rms", 350), noise * 3)

    def listen(self, should_stop) -> np.ndarray | None:
        """Gap boshlanishini kutadi, gap tugaguncha yozadi. should_stop() True bo'lsa None qaytaradi."""
        silence_blocks = int(self.cfg.get("silence_seconds", 0.9) * SAMPLE_RATE / BLOCK)
        max_blocks = int(self.cfg.get("max_phrase_seconds", 15) * SAMPLE_RATE / BLOCK)
        pre_roll = 10  # gap boshi kesilib qolmasligi uchun 0.3 s oldingi audio

        frames, history = [], []
        speaking, quiet = False, 0
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16", blocksize=BLOCK) as stream:
            while True:
                if should_stop():
                    return None
                block, _ = stream.read(BLOCK)
                loud = _rms(block) > self.threshold
                if not speaking:
                    history = (history + [block])[-pre_roll:]
                    if loud:
                        speaking, frames = True, list(history)
                    continue
                frames.append(block)
                quiet = 0 if loud else quiet + 1
                if quiet >= silence_blocks or len(frames) >= max_blocks:
                    break
        if len(frames) < 12:  # 0.35 s dan qisqa - shunchaki shovqin
            return None
        return np.concatenate(frames).flatten()

    def transcribe(self, audio: np.ndarray) -> str:
        if self.cfg.get("stt_engine", "google") == "whisper":
            return self._transcribe_whisper(audio)
        return self._transcribe_google(audio)

    def _transcribe_google(self, audio: np.ndarray) -> str:
        import speech_recognition as sr
        data = sr.AudioData(audio.tobytes(), SAMPLE_RATE, 2)
        try:
            return sr.Recognizer().recognize_google(data, language=self.cfg.get("stt_language", "uz-UZ"))
        except sr.UnknownValueError:
            return ""

    def _transcribe_whisper(self, audio: np.ndarray) -> str:
        if self._whisper is None:
            from faster_whisper import WhisperModel
            self._whisper = WhisperModel(self.cfg.get("whisper_model", "small"), compute_type="int8")
        lang = self.cfg.get("stt_language", "uz-UZ").split("-")[0]
        segments, _ = self._whisper.transcribe(audio.astype(np.float32) / 32768.0, language=lang)
        return " ".join(s.text for s in segments).strip()


class Mouth:
    """Microsoft Edge ovozlari orqali o'zbekcha gapiradi."""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        import pygame
        self.pygame = pygame
        pygame.mixer.init()
        self._stop = False

    def say(self, text: str):
        if not text.strip():
            return
        import edge_tts
        self._stop = False
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        try:
            communicate = edge_tts.Communicate(text, self.cfg.get("tts_voice", "uz-UZ-SardorNeural"),
                                               rate=self.cfg.get("tts_rate", "+0%"))
            asyncio.run(communicate.save(path))
            music = self.pygame.mixer.music
            music.load(path)
            music.play()
            while music.get_busy() and not self._stop:
                time.sleep(0.05)
            music.stop()
            music.unload()
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    def stop(self):
        self._stop = True


def _rms(block: np.ndarray) -> float:
    return float(np.sqrt(np.mean(block.astype(np.float32) ** 2)))
