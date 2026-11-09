"""AssistantManager agregando chat, voz e comandos Windows."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .chat import ChatManager
from .voice import VoiceManager
from .commands import WindowsCommandHandler


class AssistantManager:
    """Orquestrador do assistente IA."""

    def __init__(
        self,
        provider_or_id: Any = None,
        config: Optional[Dict[str, Any]] = None,
        *,
        provider: Any = None,
        provider_id: Optional[str] = None,
        db: Any = None,
        user_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        confirm: Optional[Callable[[str], bool]] = None,
        on_transcript: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.config = config or {}
        self.confirm = confirm
        self.chat = ChatManager(
            provider_or_id,
            config=self.config,
            provider=provider,
            provider_id=provider_id,
            db=db,
            user_id=user_id,
            system_prompt=system_prompt,
        )
        self.voice = VoiceManager(on_transcript=on_transcript)
        self.commands = WindowsCommandHandler(confirm=confirm)

    # Atalhos convenientes
    def send_message(self, text: str, **kwargs: Any) -> str:
        return self.chat.send_message(text, **kwargs)

    def speak(self, text: str, voice: Any = None, rate: Any = None) -> bool:
        return self.voice.speak(text, voice=voice, rate=rate)

    def execute_command(self, command: Any, **kwargs: Any) -> Any:
        return self.commands.execute_command(command, **kwargs)
