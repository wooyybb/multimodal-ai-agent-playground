from registry.tool_catalog import ToolCatalog
from workflow.plan_validator import PlanValidator


def _validator():
    return PlanValidator(ToolCatalog())


def test_invalid_tool_blocked_and_not_executable():
    plan = {
        "goal": "bad",
        "selected_strategy": "unsafe",
        "steps": [
            {"step_id": 1, "tool": "delete_workspace", "reason": "cleanup"}
        ],
        "max_steps": 12,
        "confidence": 0.1,
    }

    result = _validator().validate(plan, {"user_prompt": "x"})

    assert result["valid"] is False
    assert result["fallback_used"] is True
    assert any("Tool Catalog" in error for error in result["errors"])
    assert result["execution_plan"] == []


def test_forbidden_shell_tool_blocked():
    plan = {
        "goal": "bad",
        "selected_strategy": "unsafe",
        "steps": [{"step_id": 1, "tool": "shell", "reason": "run shell"}],
        "max_steps": 12,
        "confidence": 0.1,
    }

    result = _validator().validate(plan, {"user_prompt": "x"})

    assert result["valid"] is False
    assert any("forbidden tool" in error for error in result["errors"])


def test_evaluation_before_generation_is_invalid():
    plan = {
        "goal": "bad order",
        "selected_strategy": "bad",
        "steps": [
            {"step_id": 1, "tool": "aggregate_evaluation", "reason": "too early"},
            {"step_id": 2, "tool": "generate_flux", "reason": "late"},
        ],
        "max_steps": 12,
        "confidence": 0.2,
    }

    result = _validator().validate(plan, {"user_prompt": "x"})

    assert result["valid"] is False
    assert "evaluation selected before generation" in result["errors"]


def test_generation_before_prompt_rendering_is_invalid():
    plan = {
        "goal": "bad order",
        "selected_strategy": "bad",
        "steps": [{"step_id": 1, "tool": "generate_flux", "reason": "too early"}],
        "max_steps": 12,
        "confidence": 0.2,
    }

    result = _validator().validate(plan, {"user_prompt": "x"})

    assert result["valid"] is False
    assert "generation selected before provider prompt rendering" in result["errors"]


def test_step_limit_blocks_oversized_llm_plan():
    plan = {
        "goal": "too long",
        "selected_strategy": "loop",
        "steps": [
            {"step_id": index, "tool": "prepare_context", "reason": "repeat"}
            for index in range(1, 21)
        ],
        "max_steps": 20,
        "confidence": 0.2,
    }

    result = _validator().validate(plan, {"user_prompt": "x"})

    assert result["valid"] is False
    assert any("exceeds limit" in error for error in result["errors"])


def test_duplicate_tool_loop_warns_without_infinite_execution():
    plan = {
        "goal": "duplicate",
        "selected_strategy": "loop",
        "steps": [
            {"step_id": 1, "tool": "prepare_context", "reason": "first"},
            {"step_id": 2, "tool": "prepare_context", "reason": "duplicate"},
        ],
        "max_steps": 12,
        "confidence": 0.2,
    }

    result = _validator().validate(plan, {"user_prompt": "x"})

    assert any("duplicate tool skipped" in warning for warning in result["warnings"])
    assert result["selected_tools"].count("prepare_context") == 1
