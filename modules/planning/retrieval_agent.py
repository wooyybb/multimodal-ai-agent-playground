from modules.memory.knowledge_manager import KnowledgeManager


class RetrievalAgent:
    def __init__(self, knowledge_manager=None):
        self.knowledge_manager = knowledge_manager or KnowledgeManager()

    def run(self, caption, user_prompt) -> dict:
        print("[RetrievalAgent] Running...")

        try:
            query = f"{caption or ''} {user_prompt or ''}".lower()
            knowledge = self.knowledge_manager.load_all()

            print("[RetrievalAgent] Searching style...")
            style = self._match_rule_group(query, knowledge.get("style", {}))

            print("[RetrievalAgent] Searching lighting...")
            lighting = self._match_rule_group(query, knowledge.get("lighting", {}))

            print("[RetrievalAgent] Searching composition...")
            composition = self._match_rule_group(
                query,
                knowledge.get("composition", {}),
            )

            print("[RetrievalAgent] Searching quality...")
            quality = self._default_rules(knowledge.get("quality", {}))

            print("[RetrievalAgent] Searching negative...")
            negative = self._default_rules(knowledge.get("negative", {}))

            retrieved_context = {
                "style": style,
                "lighting": lighting,
                "quality": quality,
                "negative": negative,
                "composition": composition,
            }
            print("[RetrievalAgent] Retrieved knowledge.")
            return retrieved_context
        except Exception as error:
            print(f"[RetrievalAgent] Error: {error}")
            return {}

    def _match_rule_group(self, query, rules):
        matches = []
        for name, rule in rules.items():
            keywords = rule.get("keywords", [])
            if self._matches(query, name, keywords):
                matches.extend(rule.get("prompt_rules", []))
        return self._deduplicate(matches)

    def _default_rules(self, rules):
        default = rules.get("default", {})
        return self._deduplicate(default.get("prompt_rules", []))

    def _matches(self, query, name, keywords):
        if str(name).lower() in query:
            return True
        return any(str(keyword).lower() in query for keyword in keywords)

    def _deduplicate(self, values):
        result = []
        for value in values:
            if value and value not in result:
                result.append(value)
        return result
