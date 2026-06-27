import json
from datetime import datetime
from pathlib import Path


class History:
    def __init__(self, history_path=None):
        self.history_path = Path(history_path or "memory/history.json")

    def save(self, caption, prompt, score, reflection, retry):
        print("[Memory] Saving history...")

        record = {
            "caption": caption,
            "prompt": prompt,
            "score": score,
            "reflection": reflection,
            "retry": retry,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

        history = []
        if self.history_path.exists():
            with self.history_path.open("r", encoding="utf-8") as file:
                history = json.load(file)

        history.append(record)

        self.history_path.parent.mkdir(exist_ok=True)
        with self.history_path.open("w", encoding="utf-8") as file:
            json.dump(history, file, ensure_ascii=False, indent=2)

        print(f"[Memory] History saved: {self.history_path}")
        return str(self.history_path)
