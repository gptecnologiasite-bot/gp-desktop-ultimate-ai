"""Gerenciador de Storage (buckets)."""

from __future__ import annotations

from typing import Any, Iterable, Optional

from .client import get_supabase_client

BUCKETS = ["wallpapers", "avatars", "themes"]


class StorageManager:
    def __init__(self, client=None):
        self._client = client if client is not None else get_supabase_client()

    def _bucket(self, bucket: str):
        if bucket not in BUCKETS:
            raise ValueError(f"Bucket não permitido: {bucket}")
        return self._client.storage.from_(bucket)

    def upload(
        self, bucket: str, path: str, file: Any, content_type: Optional[str] = None
    ):
        opts = {}
        if content_type:
            opts["content-type"] = content_type
        return self._bucket(bucket).upload(path, file, opts if opts else None)

    def download(self, bucket: str, path: str):
        return self._bucket(bucket).download(path)

    def delete(self, bucket: str, paths: Iterable[str]):
        return self._bucket(bucket).remove(list(paths))

    def list(self, bucket: str, path: str = ""):
        return self._bucket(bucket).list(path)

    def create_bucket(self, bucket: str, public: bool = False):
        return self._client.storage.create_bucket(bucket, {"public": public})

    def delete_bucket(self, bucket: str):
        return self._client.storage.delete_bucket(bucket)

    def list_buckets(self):
        return self._client.storage.list_buckets()
