import json
from pathlib import Path


class KnowledgeManager:
    def __init__(self, knowledge_dir=None):
        self.knowledge_dir = Path(knowledge_dir or "knowledge")

    def load_style(self, style_name=None):
        print("[KnowledgeManager] Loading style library...")
        data = self._load_json("style_library.json")
        if style_name:
            return data.get(str(style_name).lower(), {})
        return data

    def load_lighting(self, keyword=None):
        print("[KnowledgeManager] Loading lighting rules...")
        data = self._load_json("lighting_rules.json")
        if keyword:
            return data.get(str(keyword).lower(), {})
        return data

    def load_quality(self):
        print("[KnowledgeManager] Loading quality rules...")
        return self._load_json("quality_rules.json")

    def load_negative(self):
        print("[KnowledgeManager] Loading negative prompt rules...")
        return self._load_json("negative_prompt_rules.json")

    def load_composition(self):
        print("[KnowledgeManager] Loading composition rules...")
        return self._load_json("composition_rules.json")

    def load_all(self):
        return {
            "style": self.load_style(),
            "lighting": self.load_lighting(),
            "quality": self.load_quality(),
            "negative": self.load_negative(),
            "composition": self.load_composition(),
        }

    def _load_json(self, filename):
        path = self.knowledge_dir / filename
        try:
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as error:
            print(f"[KnowledgeManager] Error loading {filename}: {error}")
            return {}
