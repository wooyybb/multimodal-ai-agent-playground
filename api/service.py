from agents.orchestrator_agent import OrchestratorAgent


def run_generation(user_prompt: str, provider: str | None = None, image: str | None = None) -> dict:
    print("[FastAPI] Generation started")
    orchestrator = OrchestratorAgent()

    result = orchestrator.run(
        image=image,
        user_prompt=user_prompt,
        provider=provider,
    )

    print("[FastAPI] Generation finished")
    return {
        "success": True,
        "provider": result.get("provider") or provider,
        "score": result.get("best_score") or result.get("score"),
        "image_path": result.get("best_output_image_path")
        or result.get("output_image_path"),
        "agent_trace": result.get("agent_trace", []),
        "error": None,
    }
