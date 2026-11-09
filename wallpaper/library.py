"""Biblioteca de wallpapers com favoritos e persistÃªncia Supabase."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any, Iterable, Optional

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
VIDEO_EXTS = {".mp4", ".webm", ".mov", ".avi", ".mkv"}
GIF_EXTS = {".gif"}


def _normalize_path(path: str) -> str:
    if path.startswith(("http://", "https://")):
        return path
    try:
        return os.path.abspath(path)
    except Exception:
        return path


def _type_from_path(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    if ext in GIF_EXTS:
        return "gif"
    return "unknown"


class WallpaperLibrary:
    """Gerencia a biblioteca de wallpapers em memÃ³ria e no Supabase."""

    def __init__(
        self,
        db: Any = None,
        user_id: Optional[str] = None,
        persist: bool = True,
        auto_load: bool = True,
    ):
        self._items: list[dict] = []
        self._db = db
        self._user_id = user_id
        self._persist = persist
        if auto_load and self._db is not None:
            try:
                self._load()
            except Exception:
                pass

    # ---------- helpers ----------

    def _new_id(self) -> str:
        return str(uuid.uuid4())

    def _load(self) -> None:
        if self._db is None:
            return
        filters = {}
        if self._user_id:
            filters["user_id"] = self._user_id
        try:
            res = self._db.select("wallpapers", filters=filters or None)
        except Exception:
            return
        data = getattr(res, "data", None)
        if not data:
            # pode ser lista direta
            data = res if isinstance(res, list) else None
        if not data:
            return
        for row in data:
            item = {
                "id": row.get("id") or self._new_id(),
                "path": row.get("path") or row.get("url") or "",
                "name": row.get("name") or os.path.basename(row.get("path", "")),
                "type": row.get("type") or _type_from_path(row.get("path", "")),
                "favorite": bool(row.get("favorite", False)),
                "metadata": row.get("metadata") or {},
            }
            if item["path"] and not any(i["path"] == item["path"] for i in self._items):
                self._items.append(item)

    def _persist_insert(self, item: dict) -> None:
        if not self._persist or self._db is None:
            return
        try:
            payload = {
                "id": item["id"],
                "path": item["path"],
                "name": item["name"],
                "type": item["type"],
                "favorite": item["favorite"],
            }
            if self._user_id:
                payload["user_id"] = self._user_id
            self._db.insert("wallpapers", payload)
        except Exception:
            pass

    def _persist_update(self, item: dict) -> None:
        if not self._persist or self._db is None:
            return
        try:
            payload = {"favorite": item["favorite"], "name": item["name"]}
            self._db.update("wallpapers", payload, filters={"id": item["id"]})
        except Exception:
            pass

    def _persist_delete(self, item: dict) -> None:
        if not self._persist or self._db is None:
            return
        try:
            self._db.delete("wallpapers", filters={"id": item["id"]})
        except Exception:
            pass

    # ---------- API ----------

    def add(
        self,
        path: str,
        name: Optional[str] = None,
        type: Optional[str] = None,
        favorite: bool = False,
        metadata: Optional[dict] = None,
    ) -> dict:
        path = _normalize_path(path)
        # evita duplicados
        for it in self._items:
            if it["path"] == path:
                if favorite and not it["favorite"]:
                    it["favorite"] = True
                    self._persist_update(it)
                return it
        item = {
            "id": self._new_id(),
            "path": path,
            "name": name or os.path.basename(path.rstrip("/\\")),
            "type": type or _type_from_path(path),
            "favorite": bool(favorite),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        self._items.append(item)
        self._persist_insert(item)
        return item

    def remove(self, path: Optional[str] = None, item_id: Optional[str] = None) -> bool:
        if path is not None:
            path = _normalize_path(path)
        for i, it in enumerate(self._items):
            if (path is not None and it["path"] == path) or (
                item_id is not None and it["id"] == item_id
            ):
                removed = self._items.pop(i)
                self._persist_delete(removed)
                return True
        return False

    def list(
        self,
        type: Optional[str] = None,
        favorite: Optional[bool] = None,
        search: Optional[str] = None,
        favorites_only: bool = False,
    ) -> list[dict]:
        out = list(self._items)
        if favorites_only or favorite is True:
            out = [i for i in out if i.get("favorite")]
        elif favorite is False:
            out = [i for i in out if not i.get("favorite")]
        if type:
            out = [i for i in out if i.get("type") == type]
        if search:
            q = search.lower()
            out = [
                i
                for i in out
                if q in (i.get("name") or "").lower()
                or q in (i.get("path") or "").lower()
            ]
        return out

    def favorites(self) -> list[dict]:
        return [i for i in self._items if i.get("favorite")]

    def toggle_favorite(
        self, path: Optional[str] = None, item_id: Optional[str] = None
    ) -> bool:
        if path is not None:
            path = _normalize_path(path)
        for it in self._items:
            if (path is not None and it["path"] == path) or (
                item_id is not None and it["id"] == item_id
            ):
                it["favorite"] = not it.get("favorite", False)
                self._persist_update(it)
                return it["favorite"]
        return False

    def get(
        self, path: Optional[str] = None, item_id: Optional[str] = None
    ) -> Optional[dict]:
        if path is not None:
            path = _normalize_path(path)
        for it in self._items:
            if (path is not None and it["path"] == path) or (
                item_id is not None and it["id"] == item_id
            ):
                return it
        return None

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterable[dict]:
        return iter(self._items)
