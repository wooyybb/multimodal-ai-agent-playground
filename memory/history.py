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

    def search_similar_runs(self, query: str, top_k: int = 1) -> list[dict]:
        print("[Memory] Searching similar runs...")
        history = self.get_history()
        if not history:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scored_runs = []
        for run in history:
            if not isinstance(run, dict):
                continue

            run_text = " ".join(
                str(run.get(key) or "")
                for key in (
                    "caption",
                    "initial_prompt",
                    "best_prompt",
                    "retry_prompt",
                    "prompt",
                )
            )
            run_tokens = self._tokenize(run_text)
            similarity = self._jaccard_similarity(query_tokens, run_tokens)
            if similarity <= 0:
                continue

            result = dict(run)
            result["memory_similarity"] = similarity
            scored_runs.append(result)

        scored_runs.sort(key=lambda item: item.get("memory_similarity", 0), reverse=True)
        matches = scored_runs[: max(1, top_k)]

        for match in matches:
            print(f"[Memory] Similar run score: {match.get('memory_similarity', 0):.2f}")

        return matches

    def get_best_run(self) -> dict | None:
        history = self.get_history()
        best_run = None
        best_score = None

        for run in history:
            if not isinstance(run, dict):
                continue

            score = self._get_run_score(run)
            if score is None:
                continue

            if best_score is None or score > best_score:
                best_score = score
                best_run = run

        if best_score is not None:
            print(f"[Memory] Best run score: {best_score:.2f}")
        return dict(best_run) if best_run else None

    def get_memory_context(self, query: str) -> dict:
        try:
            similar_runs = self.search_similar_runs(query, top_k=1)
            best_run = self.get_best_run()
            memory_score = (
                similar_runs[0].get("memory_similarity", 0.0)
                if similar_runs
                else 0.0
            )

            if similar_runs:
                memory_hint = "similar previous run found"
            elif best_run:
                memory_hint = "best previous run available"
            else:
                memory_hint = "no memory found"

            return {
                "similar_runs": similar_runs,
                "best_run": best_run,
                "memory_hint": memory_hint,
                "memory_score": memory_score,
            }
        except Exception as error:
            print(f"[Memory] Search failed: {error}")
            return {
                "similar_runs": [],
                "best_run": None,
                "memory_hint": "memory unavailable",
                "memory_score": 0.0,
            }

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
                "raw_suggested_prompt": record.get("raw_suggested_prompt"),
                "evaluation_prompt": record.get("evaluation_prompt"),
                "retry_evaluation_prompt": record.get("retry_evaluation_prompt"),
                "retry_score": record.get("retry_score"),
                "retry_output_image_path": record.get(
                    "retry_output_image_path"
                ),
                "best_prompt": record.get("best_prompt"),
                "best_score": record.get("best_score"),
                "best_output_image_path": record.get(
                    "best_output_image_path"
                ),
                "debug_report_path": record.get("debug_report_path"),
                "prompt_preview_path": record.get("prompt_preview_path"),
                "run_dir": record.get("run_dir"),
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

        try:
            with self.history_path.open("r", encoding="utf-8") as file:
                history = json.load(file)
        except (json.JSONDecodeError, OSError):
            return []

        if not isinstance(history, list):
            return []

        return history

    def clear_history(self):
        print("[Memory] Clearing history...")
        self.history_path.parent.mkdir(exist_ok=True)
        with self.history_path.open("w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=2)
        print("[Memory] History updated.")
        return str(self.history_path)

    def _tokenize(self, text):
        stopwords = {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "in",
            "is",
            "of",
            "on",
            "or",
            "the",
            "to",
            "with",
            "image",
            "prompt",
            "high",
            "quality",
            "detailed",
            "user",
            "request",
        }
        cleaned = []
        for char in str(text or "").lower():
            cleaned.append(char if char.isalnum() else " ")
        return {
            token
            for token in "".join(cleaned).split()
            if token and token not in stopwords
        }

    def _jaccard_similarity(self, left, right):
        if not left or not right:
            return 0.0
        union = left | right
        if not union:
            return 0.0
        return len(left & right) / len(union)

    def _get_run_score(self, run):
        for key in ("best_score", "retry_score", "initial_score", "score"):
            value = run.get(key)
            if value is None:
                continue
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
        return None


History = MemoryManager
