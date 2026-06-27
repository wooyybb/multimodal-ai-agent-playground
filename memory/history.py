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
        if "initial_prompt" in record or "retry_prompt" in record:
            print("[Memory] Saving full retry record...")
        else:
            print("[Memory] Saving run...")

        history = self.get_history()
        stored_record = {
            "timestamp": record.get(
                "timestamp",
                datetime.now().isoformat(timespec="seconds"),
            ),
            **record,
        }
        history.append(
            self._normalize_record(stored_record)
        )

        self.history_path.parent.mkdir(exist_ok=True)
        with self.history_path.open("w", encoding="utf-8") as file:
            json.dump(history, file, ensure_ascii=False, indent=2)

        print("[Memory] History updated.")
        return str(self.history_path)

    def _normalize_record(self, record):
        if "initial_prompt" in record or "retry_prompt" in record:
            return {
                "timestamp": record.get("timestamp"),
                "caption": record.get("caption"),
                "initial_prompt": record.get("initial_prompt"),
                "initial_score": record.get("initial_score"),
                "initial_output_image_path": record.get(
                    "initial_output_image_path"
                ),
                "reflection": record.get("reflection"),
                "retry_needed": record.get("retry_needed"),
                "retry_prompt": record.get("retry_prompt"),
                "retry_score": record.get("retry_score"),
                "retry_output_image_path": record.get(
                    "retry_output_image_path"
                ),
                "best_prompt": record.get("best_prompt"),
                "best_score": record.get("best_score"),
                "best_output_image_path": record.get(
                    "best_output_image_path"
                ),
            }

        return {
            "timestamp": record.get("timestamp"),
            "caption": record.get("caption"),
            "prompt": record.get("prompt"),
            "score": record.get("score"),
            "reflection": record.get("reflection"),
            "retry": record.get("retry"),
            "output_image_path": record.get("output_image_path"),
        }

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
