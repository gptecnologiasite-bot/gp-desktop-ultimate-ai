"""Gerenciador de chat do assistente IA."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


def _is_provider(obj: Any) -> bool:
    return hasattr(obj, "chat") and callable(getattr(obj, "chat", None))


class ChatManager:
    """Gerencia conversas, histórico e persistência via Supabase."""

    def __init__(
        self,
        provider_or_id: Any = None,
        config: Optional[Dict[str, Any]] = None,
        *,
        provider: Any = None,
        provider_id: Optional[str] = None,
        db: Any = None,
        database: Any = None,
        user_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        confirm: Optional[Callable[[str], bool]] = None,
    ) -> None:
        self.config = config or {}
        self.user_id = user_id
        self.system_prompt = system_prompt
        self.db = db if db is not None else database
        self.confirm = confirm

        # resolve provider
        resolved_provider = provider if provider is not None else provider_or_id
        if resolved_provider is None:
            resolved_provider = provider_id
        if isinstance(resolved_provider, str):
            from providers import get_provider

            pid = resolved_provider or provider_id or "openai"
            self.provider = get_provider(pid, self.config)
            self.provider_id = pid
        elif _is_provider(resolved_provider):
            self.provider = resolved_provider
            self.provider_id = getattr(resolved_provider, "name", None)
        else:
            # fallback
            from providers import get_provider

            pid = provider_id or "openai"
            self.provider = get_provider(pid, self.config)
            self.provider_id = pid

        self.messages: List[Dict[str, Any]] = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    # ------------------------------------------------------------------ #
    # Conversa
    # ------------------------------------------------------------------ #
    @property
    def history(self) -> List[Dict[str, Any]]:
        return self.messages

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self.messages)

    def send_message(self, text: str, **kwargs: Any) -> str:
        """Envia uma mensagem do usuário e retorna a resposta do provedor."""
        self.messages.append({"role": "user", "content": text})
        response = self.provider.chat(self.messages, **kwargs)
        self.messages.append({"role": "assistant", "content": response})
        return response

    def clear_history(self) -> None:
        """Limpa o histórico mantendo o prompt de sistema, se houver."""
        if self.system_prompt:
            self.messages = [{"role": "system", "content": self.system_prompt}]
        else:
            self.messages = []

    # ------------------------------------------------------------------ #
    # Persistência Supabase (ai_history)
    # ------------------------------------------------------------------ #
    def _get_db(self, db: Any = None) -> Any:
        if db is not None:
            return db
        if self.db is not None:
            return self.db
        try:
            from supabase import DatabaseManager

            return DatabaseManager()
        except Exception:
            return None

    def save_history(self, user_id: Optional[str] = None, db: Any = None) -> bool:
        """Salva o histórico na tabela ai_history."""
        uid = user_id if user_id is not None else self.user_id
        database = self._get_db(db)
        if database is None or uid is None:
            return False
        model = getattr(self.provider, "model", None)
        # monta pares (prompt, response)
        msgs = [m for m in self.messages if m.get("role") != "system"]
        pairs: List[Dict[str, Any]] = []
        i = 0
        while i < len(msgs):
            if msgs[i].get("role") == "user":
                prompt = msgs[i].get("content")
                response = None
                if i + 1 < len(msgs) and msgs[i + 1].get("role") == "assistant":
                    response = msgs[i + 1].get("content")
                    i += 2
                else:
                    i += 1
                pairs.append(
                    {
                        "user_id": uid,
                        "prompt": prompt,
                        "response": response,
                        "model": model,
                    }
                )
            else:
                i += 1
        try:
            for row in pairs:
                database.insert("ai_history", row)
            return True
        except Exception:
            return False

    def load_history(
        self, user_id: Optional[str] = None, db: Any = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Carrega o histórico da tabela ai_history."""
        uid = user_id if user_id is not None else self.user_id
        database = self._get_db(db)
        if database is None or uid is None:
            return list(self.messages)
        try:
            res = database.select("ai_history", filters={"user_id": uid})
            data = getattr(res, "data", None)
            if data is None:
                data = res if isinstance(res, list) else []
            if limit is not None:
                data = data[-limit:]
            msgs: List[Dict[str, Any]] = []
            if self.system_prompt:
                msgs.append({"role": "system", "content": self.system_prompt})
            for row in data or []:
                if row.get("prompt") is not None:
                    msgs.append({"role": "user", "content": row.get("prompt")})
                if row.get("response") is not None:
                    msgs.append({"role": "assistant", "content": row.get("response")})
            self.messages = msgs
            return list(self.messages)
        except Exception:
            return list(self.messages)
