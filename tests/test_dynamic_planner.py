import json
from pathlib import Path

from agents.planning_agent import PlanningAgent
from llm.requirement_parser import RequirementParser
from llm.tool_planner import ToolPlanner
from registry.tool_catalog import ToolCatalog
from workflow.plan_validator import PlanValidator


FIXTURE_PATH = Path("tests/fixtures/agent_cases.json")


def _tools_from_result(result):
    return [step["tool"] for step in result["tool_plan"]["steps"]]


def test_rule_planning_keeps_required_order(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "rule")
    result = PlanningAgent().run(
        "preserve identity and make a soft anime style transfer",
        image_provided=True,
    )

    assert result["planning_mode"] == "rule"
    assert result["planner_used_fallback"] is True
    assert result["plan_validation_result"]["valid"] is True
    assert result["execution_plan"][:5] == [
        "goal_planner",
        "memory_load",
        "vision",
        "reference_image_parser",
        "character_program_builder",
    ]


def test_openai_failure_falls_back_without_crash(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = PlanningAgent().run("make this watercolor", image_provided=False)

    assert result["planning_mode"] == "rule"
    assert result["planner_used_fallback"] is True
    assert result["plan_validation_result"]["valid"] is True


def test_mock_llm_json_plan_can_be_validated(monkeypatch):
    planner = ToolPlanner(provider="openai")
    planner.router.reason = lambda *args, **kwargs: {
        "goal": "mock valid plan",
        "selected_strategy": "mock",
        "steps": [
            {"step_id": 1, "tool": "parse_requirement", "reason": "parse"},
            {"step_id": 2, "tool": "prepare_context", "reason": "context"},
            {"step_id": 3, "tool": "compile_semantic_prompt", "reason": "semantic"},
            {"step_id": 4, "tool": "render_provider_prompt", "reason": "render"},
            {"step_id": 5, "tool": "generate_flux", "reason": "generate"},
            {"step_id": 6, "tool": "aggregate_evaluation", "reason": "evaluate"},
        ],
        "stop_conditions": ["generation_success"],
        "max_steps": 12,
        "confidence": 0.88,
        "reasoning_used_fallback": False,
    }

    catalog = ToolCatalog()
    result = planner.plan({"user_prompt": "text only", "image_provided": False}, catalog.tools_for_llm())
    validation = PlanValidator(catalog).validate(result["tool_plan"], {"user_prompt": "x"})

    assert result["llm_tool_planner_enabled"] is True
    assert validation["valid"] is True
    assert "generation" in validation["execution_plan"]


def test_conditional_tool_selection_from_fixture(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "rule")
    catalog = ToolCatalog()
    planner = ToolPlanner(provider="rule")
    cases = json.loads(FIXTURE_PATH.read_text(encoding="utf-8-sig"))

    for case in cases:
        result = planner.plan(case["input"], catalog.tools_for_llm())
        selected = _tools_from_result(result)
        for tool in case["expected_selected_tools"]:
            assert tool in selected, case["case_id"]
        for tool in case["expected_skipped_tools"]:
            assert tool not in selected, case["case_id"]


def test_user_constraints_override_reference_caption(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "rule")
    result = RequirementParser().parse(
        {
            "user_prompt": "preserve identity but remove the sword, no weapons",
            "vision_result": {"caption": "character holding a sword"},
        }
    )
    program = result["style_transfer_program"]
    remove = program["negative"]["remove"]

    assert any("sword" in item for item in remove)
    assert any("weapon" in item for item in remove)
    assert "sword" not in json.dumps(program.get("style", {})).lower()

