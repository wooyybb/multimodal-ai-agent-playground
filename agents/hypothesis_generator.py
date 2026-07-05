from llm.openai_reasoner import dumps_payload
from llm.reasoner_router import ReasonerRouter


class HypothesisGenerator:
    def __init__(self, reasoner_router=None):
        self.reasoner_router = reasoner_router or ReasonerRouter()

    def run(self, state: dict) -> dict:
        print("[HypothesisGenerator] Running...")
        state = state or {}
        fallback = {
            "hypothesis": self._rule_hypothesis(state),
            "hypothesis_evidence": self._rule_evidence(state),
            "reasoning_used_fallback": True,
        }
        system_prompt = (
            "You are a failure-analysis reasoner. Return only JSON with keys: "
            "hypothesis and hypothesis_evidence. hypothesis_evidence must be a list."
        )
        user_prompt = dumps_payload(
            {
                "task": "hypothesis_generation",
                "score": state.get("score"),
                "reflection": state.get("reflection"),
                "evaluation_result": state.get("evaluation_result"),
                "self_verification": state.get("self_verification"),
            }
        )
        result = self.reasoner_router.reason(
            system_prompt,
            user_prompt,
            fallback=fallback,
            schema_name="hypothesis",
        )
        evidence = result.get("hypothesis_evidence")
        if not isinstance(evidence, list):
            evidence = fallback["hypothesis_evidence"]
        return {
            "hypothesis": result.get("hypothesis") or fallback["hypothesis"],
            "hypothesis_evidence": evidence,
            "hypothesis_reasoning": {
                "provider": result.get("reasoning_provider"),
                "used_fallback": result.get("reasoning_used_fallback"),
                "latency": result.get("reasoning_latency"),
                "fallback_reason": result.get("reasoning_fallback_reason"),
            },
        }

    def _rule_hypothesis(self, state):
        score = float(state.get("score") or 0.0)
        reflection = str(state.get("reflection") or "").lower()
        if score < 0.65:
            return "The generation likely failed because core subject alignment is weak."
        if "identity" in reflection or "character" in reflection:
            return "Character identity may not be preserved strongly enough."
        if "layout" in reflection or "composition" in reflection:
            return "Composition may not match the requested visual structure."
        return "The result may need small prompt and context refinements."

    def _rule_evidence(self, state):
        evidence = []
        if state.get("score") is not None:
            evidence.append(f"score={state.get('score')}")
        if state.get("reflection"):
            evidence.append(str(state.get("reflection"))[:160])
        return evidence
