"""Gerenciador de voz do assistente (STT/TTS)."""

from __future__ import annotations

import threading
from typing import Any, Callable, List, Optional


class VoiceManager:
    """Reconhecimento de voz e síntese de fala, com fallback graceful."""

    def __init__(self, on_transcript: Optional[Callable[[str], None]] = None) -> None:
        self.on_transcript = on_transcript
        self._listening = False
        self._thread: Optional[threading.Thread] = None
        self._sr = None
        self._recognizer = None
        self._pyttsx3 = None

        try:
            import speech_recognition as sr  # type: ignore

            self._sr = sr
            self._recognizer = sr.Recognizer()
        except Exception:
            self._sr = None
            self._recognizer = None

        try:
            import pyttsx3  # type: ignore

            self._pyttsx3 = pyttsx3
        except Exception:
            self._pyttsx3 = None

    @property
    def is_listening(self) -> bool:
        return self._listening

    @property
    def has_stt(self) -> bool:
        return self._sr is not None and self._recognizer is not None

    @property
    def has_tts(self) -> bool:
        return self._pyttsx3 is not None

    def list_voices(self) -> List[Any]:
        """Lista vozes disponíveis no motor TTS."""
        if self._pyttsx3 is None:
            return []
        try:
            engine = self._pyttsx3.init()
            voices = engine.getProperty("voices") or []
            result = []
            for v in voices:
                result.append(
                    {
                        "id": getattr(v, "id", None),
                        "name": getattr(v, "name", None),
                        "languages": getattr(v, "languages", None),
                    }
                )
            try:
                engine.stop()
            except Exception:
                pass
            return result
        except Exception:
            return []

    def speak(self, text: str, voice: Any = None, rate: Optional[int] = None) -> bool:
        """Fala o texto usando TTS. Retorna True em sucesso."""
        if self._pyttsx3 is None:
            return False
        try:
            engine = self._pyttsx3.init()
            if voice is not None:
                engine.setProperty("voice", voice)
            if rate is not None:
                engine.setProperty("rate", rate)
            engine.say(text)
            engine.runAndWait()
            try:
                engine.stop()
            except Exception:
                pass
            return True
        except Exception:
            return False

    def start_listening(self, callback: Optional[Callable[[str], None]] = None) -> bool:
        """Inicia escuta em background. Retorna True se iniciou."""
        if callback is not None:
            self.on_transcript = callback
        if not self.has_stt:
            self._listening = False
            return False
        if self._listening:
            return True
        self._listening = True

        def _worker() -> None:
            sr = self._sr
            recognizer = self._recognizer
            while self._listening:
                try:
                    with sr.Microphone() as source:  # type: ignore[union-attr]
                        recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        audio = recognizer.listen(
                            source, timeout=5, phrase_time_limit=10
                        )
                    try:
                        text = recognizer.recognize_google(audio, language="pt-BR")
                    except Exception:
                        try:
                            text = recognizer.recognize_google(audio)
                        except Exception:
                            text = ""
                    if text and self.on_transcript is not None:
                        try:
                            self.on_transcript(text)
                        except Exception:
                            pass
                except Exception:
                    # microfone indisponível ou timeout
                    if not self._listening:
                        break
                    # pequena pausa
                    import time

                    time.sleep(0.5)
            self._listening = False

        self._thread = threading.Thread(target=_worker, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        """Para a escuta."""
        self._listening = False
        if self._thread is not None and self._thread.is_alive():
            try:
                self._thread.join(timeout=1.0)
            except Exception:
                pass
        self._thread = None
