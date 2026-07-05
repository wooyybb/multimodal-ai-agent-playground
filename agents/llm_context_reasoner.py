from llm.openai_reasoner import dumps_payload
from llm.llm_client import LLMClient
from llm.reasoner_router import ReasonerRouter


class LLMContextReasoner:
    def __init__(self, llm_client=None, reasoner_router=None):
        self.llm_client = llm_client or LLMClient(provider="mock")
        self.reasoner_router = reasoner_router or ReasonerRouter()

    def run(self, state: dict) -> dict:
        print("[LLMContextReasoner] Running...")
        state = state or {}
        fallback = self.llm_client.reason(state)
        system_prompt = (
            "You are an AI planning reasoner. Return only JSON with keys: "
            "user_goal, scene_goal, composition_goal, interaction_goal, "
            "style_goal, priority."
        )
        user_prompt = dumps_payload(
            {
                "task": "context_reasoning",
                "state": {
                    "user_prompt": state.get("user_prompt"),
                    "caption": state.get("caption"),
                    "reference_image": state.get("reference_image"),
                    "goal_tree": state.get("goal_tree"),
                },
            }
        )
        reasoning = self.reasoner_router.reason(
            system_prompt,
            user_prompt,
            fallback=fallback,
            schema_name="context_reasoning",
        )
        print(f"[LLMContextReasoner] User Goal: {reasoning['user_goal']}")
        print(f"[LLMContextReasoner] Scene Goal: {reasoning['scene_goal']}")
        return {
            "context_reasoning": reasoning,
            "llm_provider": reasoning.get("llm_provider")
            or reasoning.get("reasoning_provider"),
            "llm_used_fallback": reasoning.get("llm_used_fallback")
            or reasoning.get("reasoning_used_fallback"),
            "llm_reasoning_raw_text": reasoning.get("llm_reasoning_raw_text")
            or reasoning.get("raw_text"),
        }
