import json
from datetime import datetime
from pathlib import Path

from agents.orchestrator_agent import OrchestratorAgent
from memory.history import MemoryManager


ROOT_DIR = Path(__file__).resolve().parent
PROMPTS_PATH = ROOT_DIR / "prompts.json"
RESULTS_DIR = ROOT_DIR / "results"


def load_prompts(path: Path = PROMPTS_PATH) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        prompts = json.load(file)
    if not isinstance(prompts, list):
        raise ValueError("benchmark prompts must be a list")
    return prompts


def run_benchmark() -> dict:
    benchmark_id = datetime.now().strftime("benchmark_%Y%m%d_%H%M%S")
    prompts = load_prompts()
    results = []

    print(f"[Benchmark] Starting benchmark: {benchmark_id}")
    orchestrator = OrchestratorAgent()

    for item in prompts:
        results.append(_run_single_prompt(orchestrator, item))

    report = {
        "benchmark_id": benchmark_id,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "total": len(results),
        "success_count": sum(1 for result in results if result.get("success")),
        "failure_count": sum(1 for result in results if not result.get("success")),
        "results": results,
    }
    output_path = save_results(report, benchmark_id)
    report["result_path"] = str(output_path)
    print(f"[Benchmark] Results saved: {output_path}")
    return report


def save_results(report: dict, benchmark_id: str) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / f"{benchmark_id}.json"
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
    return output_path


def _run_single_prompt(orchestrator: OrchestratorAgent, item: dict) -> dict:
    prompt_id = item.get("id", "unknown")
    user_prompt = item.get("user_prompt", "")
    requested_provider = item.get("provider")
    image = item.get("image")

    print(f"[Benchmark] Running prompt: {prompt_id}")
    try:
        result = orchestrator.run(
            image=image,
            user_prompt=user_prompt,
            provider=requested_provider,
        )
        debug_paths = _latest_debug_paths()
        final_prompt = result.get("final_prompt") or result.get("provider_prompt") or ""
        best_score = result.get("best_score")
        score = result.get("score")
        return {
            "id": prompt_id,
            "success": True,
            "user_prompt": user_prompt,
            "requested_provider": requested_provider,
            "provider": result.get("provider") or requested_provider,
            "score": score,
            "best_score": best_score if best_score is not None else score,
            "retry_needed": result.get("retry_needed"),
            "image_path": result.get("best_output_image_path")
            or result.get("output_image_path"),
            "debug_report_path": result.get("debug_report_path")
            or debug_paths.get("debug_report_path"),
            "prompt_preview_path": result.get("prompt_preview_path")
            or debug_paths.get("prompt_preview_path"),
            "run_dir": result.get("run_dir") or debug_paths.get("run_dir"),
            "prompt_word_count": len(str(final_prompt).split()),
            "agent_trace": result.get("agent_trace", []),
            "error": None,
        }
    except Exception as error:
        print(f"[Benchmark] Prompt failed: {prompt_id}: {error}")
        return {
            "id": prompt_id,
            "success": False,
            "user_prompt": user_prompt,
            "requested_provider": requested_provider,
            "provider": requested_provider,
            "score": None,
            "best_score": None,
            "retry_needed": None,
            "image_path": None,
            "debug_report_path": None,
            "prompt_preview_path": None,
            "run_dir": None,
            "prompt_word_count": 0,
            "agent_trace": [],
            "error": str(error),
        }


def _latest_debug_paths() -> dict:
    try:
        last_run = MemoryManager().load_last_run() or {}
        return {
            "debug_report_path": last_run.get("debug_report_path"),
            "prompt_preview_path": last_run.get("prompt_preview_path"),
            "run_dir": last_run.get("run_dir"),
        }
    except Exception as error:
        print(f"[Benchmark] Debug path lookup skipped: {error}")
        return {}


def main():
    run_benchmark()


if __name__ == "__main__":
    main()
