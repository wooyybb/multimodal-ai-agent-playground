import hashlib
import json
from datetime import datetime
from pathlib import Path


class ContextCacheManager:
    def __init__(self, cache_path=None):
        self.cache_path = Path(cache_path or "memory/context_cache.json")

    def load(self):
        print("[ContextCache] Loading cache...")
        if not self.cache_path.exists():
            return {}
        try:
            with self.cache_path.open("r", encoding="utf-8") as file:
                cache = json.load(file)
        except (json.JSONDecodeError, OSError) as error:
            print(f"[ContextCache] Cache unavailable: {error}")
            return {}
        return cache if isinstance(cache, dict) else {}

    def save(self, cache):
        print("[ContextCache] Saving cache...")
        self.cache_path.parent.mkdir(exist_ok=True)
        payload = dict(cache or {})
        payload["updated_at"] = datetime.now().isoformat(timespec="seconds")
        with self.cache_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        print("[ContextCache] Cache updated.")
        return str(self.cache_path)

    def signature(self, payload):
        normalized = self._safe(payload)
        text = json.dumps(normalized, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _safe(self, value):
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, Path):
            return self._path_fingerprint(value)
        if isinstance(value, dict):
            return {str(key): self._safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._safe(item) for item in value]
        path = Path(str(value))
        if path.exists():
            return self._path_fingerprint(path)
        return str(value)

    def _path_fingerprint(self, path):
        try:
            stat = path.stat()
            return {
                "path": str(path),
                "mtime": stat.st_mtime,
                "size": stat.st_size,
            }
        except OSError:
            return {"path": str(path)}
