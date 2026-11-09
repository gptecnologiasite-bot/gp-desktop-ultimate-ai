"""Wrappers de autenticação Supabase."""

from __future__ import annotations

from typing import Any, Callable, Optional

from .client import get_supabase_client


class AuthManager:
    def __init__(self, client=None):
        self._client = client if client is not None else get_supabase_client()

    @property
    def auth(self):
        return self._client.auth

    def sign_in(self, email: str, password: str):
        return self._client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

    def sign_up(self, email: str, password: str, options: Optional[dict] = None):
        payload = {"email": email, "password": password}
        if options:
            payload.update(options)
        return self._client.auth.sign_up(payload)

    def sign_out(self):
        return self._client.auth.sign_out()

    def get_session(self):
        return self._client.auth.get_session()

    def get_user(self):
        return self._client.auth.get_user()

    def on_auth_state_change(self, callback: Callable[[Any, Any], None]):
        return self._client.auth.on_auth_state_change(callback)

    def refresh(self):
        session = self._client.auth.get_session()
        if session is None:
            return None
        refresh_token = getattr(session, "refresh_token", None)
        if refresh_token is None and isinstance(session, dict):
            refresh_token = session.get("refresh_token")
        if not refresh_token:
            return None
        return self._client.auth.refresh_session(refresh_token)
