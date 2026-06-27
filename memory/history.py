import json
from datetime import datetime
from pathlib import Path


class MemoryManager:
    def __init__(self, history_path=None):
        self.history_path = Path(history_path or "memory/history.json")

    def load_last_run(self):
        print("[Memory] Loading last run...")
        history = self.get_history()
        if not history:
            return None
        return history[-1]

    def save_run(self, record: dict):
        print("[Memory] Saving run...")
        history = self.get_history()
        history.append(
            {
                "timestamp": record.get(
                    "timestamp",
                    datetime.now().isoformat(timespec="seconds"),
                ),
                "caption": record.get("caption"),
                "prompt": record.get("prompt"),
                "score": record.get("score"),
                "reflection": record.get("reflection"),
                "retry": record.get("retry"),
                "output_image_path": record.get("output_image_path"),
            }
        )

        self.history_path.parent.mkdir(exist_ok=True)
        with self.history_path.open("w", encoding="utf-8") as file:
            json.dump(history, file, ensure_ascii=False, indent=2)

        print("[Memory] History updated.")
        return str(self.history_path)

    def get_history(self):
        if not self.history_path.exists():
            return []

        with self.history_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def clear_history(self):
        print("[Memory] Clearing history...")
        self.history_path.parent.mkdir(exist_ok=True)
        with self.history_path.open("w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=2)
        print("[Memory] History updated.")
        return str(self.history_path)


History = MemoryManager
