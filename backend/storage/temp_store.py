import os
import time
import threading
import uuid
from dataclasses import dataclass, field


@dataclass
class _Entry:
    path: str
    media_type: str
    filename: str
    size_bytes: int
    created_at: float = field(default_factory=time.time)


class TempStore:
    """
    Thread-safe in-process store mapping media_id -> file metadata.
    For production, replace with Redis + S3.
    """

    def __init__(self, upload_dir: str, ttl_seconds: int = 3600) -> None:
        self._upload_dir = upload_dir
        self._ttl = ttl_seconds
        self._store: dict[str, _Entry] = {}
        self._lock = threading.Lock()
        os.makedirs(upload_dir, exist_ok=True)

    def register(
        self,
        *,
        media_id: str | None = None,
        path: str,
        media_type: str,
        filename: str,
        size_bytes: int,
    ) -> str:
        media_id = media_id or str(uuid.uuid4())
        with self._lock:
            self._store[media_id] = _Entry(
                path=path,
                media_type=media_type,
                filename=filename,
                size_bytes=size_bytes,
            )
        return media_id

    def get(self, media_id: str) -> _Entry | None:
        with self._lock:
            return self._store.get(media_id)

    def delete(self, media_id: str) -> None:
        with self._lock:
            entry = self._store.pop(media_id, None)
        if entry and os.path.exists(entry.path):
            os.remove(entry.path)

    def cleanup_expired(self) -> int:
        now = time.time()
        expired = []
        with self._lock:
            for mid, entry in list(self._store.items()):
                if now - entry.created_at > self._ttl:
                    expired.append(mid)
            for mid in expired:
                self._store.pop(mid, None)
        for mid in expired:
            self.delete(mid)
        return len(expired)


_store_instance: TempStore | None = None


def get_store() -> TempStore:
    if _store_instance is None:
        raise RuntimeError("TempStore not initialized. Call init_store() first.")
    return _store_instance


def init_store(upload_dir: str, ttl_seconds: int = 3600) -> TempStore:
    global _store_instance
    _store_instance = TempStore(upload_dir=upload_dir, ttl_seconds=ttl_seconds)
    return _store_instance
