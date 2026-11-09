"""Gerenciador de personalização (com fallback em memória e sinais Qt)."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

# Qt (opcional, com shim para ambientes sem PySide6)
try:
    from PySide6.QtCore import QObject, Signal as _QtSignal  # type: ignore

    _HAS_QT = True
except Exception:  # pragma: no cover - fallback
    _HAS_QT = False

    class QObject:  # type: ignore
        pass

    class _SignalShim:
        def __init__(self):
            self._slots: List[Callable] = []

        def connect(self, slot: Callable) -> None:
            self._slots.append(slot)

        def disconnect(self, slot: Optional[Callable] = None) -> None:
            if slot is None:
                self._slots.clear()
            else:
                self._slots = [s for s in self._slots if s != slot]

        def emit(self, *args: Any, **kwargs: Any) -> None:
            for slot in list(self._slots):
                try:
                    slot(*args, **kwargs)
                except Exception:
                    pass

    class _SignalDescriptor:
        def __init__(self, *args: Any, **kwargs: Any):
            self._args = args
            self._kwargs = kwargs

        def __set_name__(self, owner, name):
            self._name = name

        def __get__(self, obj, owner=None):
            if obj is None:
                return self
            store = obj.__dict__.setdefault("_signal_store", {})
            if self._name not in store:
                store[self._name] = _SignalShim()
            return store[self._name]

    def _QtSignal(*args: Any, **kwargs: Any):  # type: ignore
        return _SignalDescriptor(*args, **kwargs)


# alias público usado nas classes
pyqtSignal = _QtSignal if not _HAS_QT else None
if _HAS_QT:
    from PySide6.QtCore import Signal as pyqtSignal  # type: ignore


from .models import (
    CustomizationProfile,
    Theme,
    AppearanceProfile,
    LayoutConfig,
    DesktopConfig,
)


def _resolve_db(db):
    if db is not None:
        return db
    try:
        from supabase import DatabaseManager

        return DatabaseManager()
    except Exception:
        return None


class PersonalizationManager(QObject):
    profile_changed = pyqtSignal(object) if _HAS_QT else pyqtSignal(object)
    preview_changed = pyqtSignal(object)
    profiles_changed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        db=None,
        user_id: Optional[str] = None,
        default_profile: Optional[CustomizationProfile] = None,
    ):
        super().__init__()
        self._db = _resolve_db(db)
        self._user_id = user_id
        self._profiles: Dict[str, CustomizationProfile] = {}
        self._current: Optional[CustomizationProfile] = None
        self._preview: Optional[CustomizationProfile] = None
        self._default = default_profile
        # carrega perfis existentes (best-effort)
        try:
            self.load()
        except Exception as exc:
            self._emit_error(str(exc))

    # ---------- helpers de sinal ----------
    def _emit_error(self, msg: str) -> None:
        try:
            self.error_occurred.emit(msg)
        except Exception:
            pass

    # ---------- persistência ----------
    def _row_to_profile(self, row: Any) -> Optional[CustomizationProfile]:
        try:
            if isinstance(row, dict):
                data = row.get("data")
                name = row.get("name")
            else:
                data = getattr(row, "data", None)
                name = getattr(row, "name", None)
            if isinstance(data, str):
                obj = json.loads(data)
            elif isinstance(data, dict):
                obj = data
            else:
                obj = row if isinstance(row, dict) else None
            if obj is None:
                return None
            prof = CustomizationProfile.from_dict(obj)
            if name and not prof.name:
                prof.name = name
            return prof
        except Exception:
            return None

    def load(self) -> List[CustomizationProfile]:
        profiles: List[CustomizationProfile] = []
        if self._db is not None:
            try:
                res = self._db.select("personalizations")
                rows = getattr(res, "data", res)
                if not isinstance(rows, list):
                    rows = list(rows) if rows is not None else []
                for row in rows:
                    p = self._row_to_profile(row)
                    if p is not None:
                        self._profiles[p.name] = p
                        profiles.append(p)
            except Exception as exc:
                self._emit_error(str(exc))
        # perfis em memória já presentes permanecem
        if not profiles and not self._profiles:
            pass
        # garante default
        if self._default is not None and self._default.name not in self._profiles:
            self._profiles[self._default.name] = self._default
            profiles.append(self._default)
        self.profiles_changed.emit(list(self._profiles.values()))
        return list(self._profiles.values())

    def save_profile(self, profile: CustomizationProfile) -> bool:
        if profile is None:
            return False
        profile.updated_at = datetime.utcnow().isoformat()
        self._profiles[profile.name] = profile
        if self._db is not None:
            try:
                payload = {
                    "name": profile.name,
                    "data": json.dumps(profile.to_dict(), ensure_ascii=False),
                }
                if self._user_id:
                    payload["user_id"] = self._user_id
                self._db.upsert("personalizations", payload, on_conflict="name")
            except Exception as exc:
                self._emit_error(str(exc))
                # mantém em memória
        self.profiles_changed.emit(list(self._profiles.values()))
        return True

    # alias
    save = save_profile

    def get_profile(self, name: str) -> Optional[CustomizationProfile]:
        return self._profiles.get(name)

    def list_profiles(self) -> List[str]:
        return list(self._profiles.keys())

    def apply(self, profile: Union[str, CustomizationProfile]) -> CustomizationProfile:
        p = self._resolve(profile)
        self._current = p
        self._preview = None
        try:
            self.profile_changed.emit(p)
        except Exception:
            pass
        return p

    def preview(
        self, profile: Union[str, CustomizationProfile]
    ) -> CustomizationProfile:
        p = self._resolve(profile)
        self._preview = p
        try:
            self.preview_changed.emit(p)
        except Exception:
            pass
        return p

    def cancel_preview(self) -> None:
        self._preview = None
        try:
            self.preview_changed.emit(self._current)
        except Exception:
            pass

    def restore_default(self) -> Optional[CustomizationProfile]:
        if self._default is None:
            # tenta perfil "Personalizado" ou primeiro
            if "Personalizado" in self._profiles:
                self._default = self._profiles["Personalizado"]
            elif self._profiles:
                self._default = next(iter(self._profiles.values()))
        if self._default is not None:
            return self.apply(self._default)
        return None

    def _resolve(
        self, profile: Union[str, CustomizationProfile]
    ) -> CustomizationProfile:
        if isinstance(profile, str):
            if profile in self._profiles:
                return self._profiles[profile]
            # busca case-insensitive
            for k, v in self._profiles.items():
                if k.lower() == profile.lower():
                    return v
            raise KeyError(f"Perfil não encontrado: {profile}")
        if isinstance(profile, dict):
            return CustomizationProfile.from_dict(profile)
        return profile

    def duplicate(self, name: str, new_name: str) -> CustomizationProfile:
        src = self.get_profile(name)
        if src is None:
            raise KeyError(f"Perfil não encontrado: {name}")
        import copy

        clone = copy.deepcopy(src)
        clone.name = new_name
        clone.profile_id = new_name.lower().replace(" ", "-")
        clone.is_default = False
        clone.created_at = datetime.utcnow().isoformat()
        clone.updated_at = clone.created_at
        self.save_profile(clone)
        return clone

    def rename(self, old_name: str, new_name: str) -> CustomizationProfile:
        if old_name not in self._profiles:
            raise KeyError(f"Perfil não encontrado: {old_name}")
        prof = self._profiles.pop(old_name)
        prof.name = new_name
        prof.profile_id = new_name.lower().replace(" ", "-")
        prof.updated_at = datetime.utcnow().isoformat()
        # remove antigo no db (best-effort)
        if self._db is not None:
            try:
                self._db.delete("personalizations", filters={"name": old_name})
            except Exception:
                pass
        self.save_profile(prof)
        return prof

    def delete_profile(self, name: str) -> bool:
        if name not in self._profiles:
            return False
        del self._profiles[name]
        if self._db is not None:
            try:
                self._db.delete("personalizations", filters={"name": name})
            except Exception as exc:
                self._emit_error(str(exc))
        self.profiles_changed.emit(list(self._profiles.values()))
        return True

    delete = delete_profile

    def export_profile(
        self, name: Optional[str] = None, path: Optional[str] = None
    ) -> str:
        if name is None:
            prof = self._current or (
                next(iter(self._profiles.values())) if self._profiles else None
            )
        else:
            prof = self.get_profile(name)
        if prof is None:
            raise KeyError("Nenhum perfil para exportar")
        payload = json.dumps(prof.to_dict(), ensure_ascii=False, indent=2)
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(payload)
        return payload

    export_theme = export_profile
    export = export_profile

    def import_profile(
        self, data: Union[str, dict, Any], name: Optional[str] = None
    ) -> CustomizationProfile:
        if hasattr(data, "read"):
            raw = data.read()
        elif os.path.isfile(str(data)):
            with open(str(data), "r", encoding="utf-8") as f:
                raw = f.read()
        else:
            raw = data
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")
        if isinstance(raw, str):
            obj = json.loads(raw)
        elif isinstance(raw, dict):
            obj = raw
        else:
            raise ValueError("Formato de importação inválido")
        prof = CustomizationProfile.from_dict(obj)
        if name:
            prof.name = name
            prof.profile_id = name.lower().replace(" ", "-")
        self.save_profile(prof)
        return prof

    import_theme = import_profile
    import_ = import_profile

    @property
    def current(self) -> Optional[CustomizationProfile]:
        return self._current

    @property
    def previewed(self) -> Optional[CustomizationProfile]:
        return self._preview

    @property
    def preview_profile(self) -> Optional[CustomizationProfile]:
        return self._preview

    @property
    def profiles(self) -> Dict[str, CustomizationProfile]:
        return self._profiles
