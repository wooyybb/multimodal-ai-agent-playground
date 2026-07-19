import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from llm.requirement_parser import RequirementParser
from llm.tool_planner import ToolPlanner
from registry.tool_catalog import ToolCatalog
from workflow.execution_engine import DynamicExecutionEngine
from workflow.plan_validator import PlanValidator


FIXTURE_PATH = Path("tests/fixtures/agent_cases.json")
SUMMARY_PATH = Path("artifacts/agent_validation_summary.json")


def selected_tools(plan):
    return [step.get("tool") for step in plan.get("steps") or []]


def simulate_replan(case):
    expected = case.get("expected_replan_count", 0)
    state = {
        "evaluation_result": case.get("input", {}).get("mock_evaluation")
        or {"weighted_score": 0.86},
        "output_image_path": "mock_generated_image.png",
        "retry_needed": expected > 0,
        "reflection": "mock identity failure" if expected > 0 else "mock pass",
        "replan_changed_tools": ["render_provider_prompt", "generation", "evaluation"]
        if expected > 0
        else [],
        "replan_changed_parameters": {
            "sdxl_strength": 0.35,
            "ip_adapter_scale": 0.8,
        }
        if expected > 0
        else {},
        "replan_count": 0,
    }
    engine = DynamicExecutionEngine()
    engine._record_final_stop_condition(state)
    engine._record_final_stop_condition(state)
    return state


def validate_case(case, catalog):
    planner = ToolPlanner(provider="rule")
    plan_result = planner.plan(case.get("input", {}), catalog.tools_for_llm())
    validation = PlanValidator(catalog).validate(
        plan_result["tool_plan"],
        {
            "user_prompt": case.get("input", {}).get("user_prompt", ""),
            "image": case.get("input", {}).get("image_provided", False),
        },
    )
    tools = selected_tools(plan_result["tool_plan"])
    replan_state = simulate_replan(case)

    expected_selected = case.get("expected_selected_tools", [])
    expected_skipped = case.get("expected_skipped_tools", [])
    selected_ok = all(tool in tools for tool in expected_selected)
    skipped_ok = all(tool not in tools for tool in expected_skipped)
    replan_ok = replan_state.get("replan_count") == case.get("expected_replan_count", 0)

    constraints = []
    if case.get("expected_constraints"):
        parser_result = RequirementParser().parse(case.get("input", {}))
        constraints = parser_result.get("style_transfer_program", {}).get(
            "negative", {}
        ).get("remove", [])
    constraints_ok = all(
        any(expected in item for item in constraints)
        for expected in case.get("expected_constraints", [])
    )

    return {
        "case_id": case["case_id"],
        "description": case["description"],
        "selected_tools": tools,
        "execution_plan": validation.get("execution_plan", []),
        "planner_used_fallback": plan_result.get("planner_used_fallback"),
        "validation": validation,
        "replan_count": replan_state.get("replan_count"),
        "final_stop_condition": replan_state.get("final_stop_condition"),
        "constraints": constraints,
        "passed": bool(
            validation.get("valid")
            and selected_ok
            and skipped_ok
            and replan_ok
            and constraints_ok
        ),
    }


def invalid_plan_checks(catalog):
    validator = PlanValidator(catalog)
    invalid_tool = validator.validate(
        {
            "goal": "invalid",
            "selected_strategy": "unsafe",
            "steps": [{"step_id": 1, "tool": "delete_workspace", "reason": "cleanup"}],
            "max_steps": 12,
            "confidence": 0.1,
        },
        {"user_prompt": "x"},
    )
    bad_order = validator.validate(
        {
            "goal": "bad order",
            "selected_strategy": "bad",
            "steps": [
                {"step_id": 1, "tool": "aggregate_evaluation", "reason": "too early"},
                {"step_id": 2, "tool": "generate_flux", "reason": "late"},
            ],
            "max_steps": 12,
            "confidence": 0.1,
        },
        {"user_prompt": "x"},
    )
    oversized = validator.validate(
        {
            "goal": "too many",
            "selected_strategy": "loop",
            "steps": [
                {"step_id": index, "tool": "prepare_context", "reason": "repeat"}
                for index in range(1, 21)
            ],
            "max_steps": 20,
            "confidence": 0.1,
        },
        {"user_prompt": "x"},
    )
    return {
        "invalid_tool_blocked": not invalid_tool.get("valid"),
        "invalid_tool_result": invalid_tool,
        "bad_order_blocked": not bad_order.get("valid"),
        "bad_order_result": bad_order,
        "step_limit_blocked": not oversized.get("valid"),
        "step_limit_result": oversized,
    }


def main():
    catalog = ToolCatalog()
    cases = json.loads(FIXTURE_PATH.read_text(encoding="utf-8-sig"))
    case_results = [validate_case(case, catalog) for case in cases]
    invalid_results = invalid_plan_checks(catalog)
    summary = {
        "total_cases": len(case_results),
        "passed_cases": sum(1 for item in case_results if item["passed"]),
        "case_results": case_results,
        "invalid_plan_checks": invalid_results,
        "supported_agent_level": "constrained LLM/rule tool planning with validated bounded replanning",
    }
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    for item in case_results:
        status = "PASS" if item["passed"] else "FAIL"
        print(f"[{status}] {item['case_id']}: {item['selected_tools']}")
    print(f"Invalid tool blocked: {invalid_results['invalid_tool_blocked']}")
    print(f"Bad order blocked: {invalid_results['bad_order_blocked']}")
    print(f"Step limit blocked: {invalid_results['step_limit_blocked']}")
    print(f"Saved: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()



