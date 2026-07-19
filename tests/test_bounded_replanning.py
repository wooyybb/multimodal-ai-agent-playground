from workflow.execution_engine import DynamicExecutionEngine


def test_evaluation_pass_stops_without_replan():
    state = {
        "evaluation_result": {
            "weighted_score": 0.86,
            "identity_preservation": 0.82,
            "semantic_alignment": 0.88,
        },
        "output_image_path": "mock.png",
        "retry_needed": False,
        "replan_count": 0,
    }

    DynamicExecutionEngine()._record_final_stop_condition(state)

    assert state["replan_count"] == 0
    assert state["final_stop_condition"] == "evaluation_threshold_met"


def test_low_evaluation_triggers_at_most_one_bounded_replan():
    state = {
        "evaluation_result": {
            "weighted_score": 0.41,
            "identity_preservation": 0.32,
        },
        "output_image_path": "mock.png",
        "retry_needed": True,
        "reflection": "identity preservation below threshold",
        "replan_changed_tools": ["render_provider_prompt", "generation", "evaluation"],
        "replan_changed_parameters": {
            "sdxl_strength": 0.35,
            "ip_adapter_scale": 0.8,
        },
        "replan_count": 0,
    }

    engine = DynamicExecutionEngine()
    engine._record_final_stop_condition(state)
    engine._record_final_stop_condition(state)

    assert state["replan_count"] == 1
    assert state["final_stop_condition"] == "generation_success"
    assert set(state["replan_changed_tools"]) <= {
        "render_provider_prompt",
        "generation",
        "evaluation",
    }
    assert set(state["replan_changed_parameters"]) <= {
        "sdxl_strength",
        "ip_adapter_scale",
        "controlnet_scale",
        "style_strength",
    }
