from __future__ import annotations

from dataclasses import dataclass, fields, field


@dataclass
class AgentState:
    image: object = None
    user_prompt: str = ""
    caption: str = ""
    planner_result: dict | None = None
    scene_plan: dict | None = None
    character_section: dict | None = None
    style_section: dict | None = None
    layout_section: dict | None = None
    pose_section: dict | None = None
    expression_section: dict | None = None
    lighting_section: dict | None = None
    negative_section: dict | None = None
    canonical_prompt: str = ""
    final_prompt: str = ""
    optimized_prompt: str = ""
    provider: str = ""
    provider_prompt: str = ""
    provider_negative_prompt: str = ""
    prompt_report: dict | None = None
    prompt_quality_score: int = 0
    optimization_report: dict | None = None
    llm_optimizer_report: dict | None = None
    score: float = 0.0
    retry: bool = False
    memory_context: dict | None = None
    retrieved_knowledge: dict | None = None
    agent_trace: list = field(default_factory=list)
    extra: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict | "AgentState" | None) -> "AgentState":
        print("[AgentState] Building state...")
        if isinstance(data, cls):
            return data

        data = data or {}
        field_names = set(cls.__dataclass_fields__.keys())
        known = {key: value for key, value in data.items() if key in field_names}
        extra = {key: value for key, value in data.items() if key not in field_names}
        state = cls(**known)
        state.extra.update(extra)
        return state

    def to_dict(self) -> dict:
        print("[AgentState] Exporting...")
        data = {item.name: getattr(self, item.name) for item in fields(self)}
        extra = data.pop("extra", {}) or {}
        data.update(extra)
        return data

    def update_from_dict(self, updates: dict | None) -> "AgentState":
        updates = updates or {}
        field_names = set(self.__dataclass_fields__.keys())
        for key, value in updates.items():
            if key in field_names and key != "extra":
                setattr(self, key, value)
            else:
                self.extra[key] = value
        return self

    def validate(self) -> list[str]:
        print("[AgentState] Validating...")
        warnings = []
        for key in ("user_prompt", "caption", "canonical_prompt", "provider", "score"):
            value = getattr(self, key, None)
            if value in (None, ""):
                warning = f"[AgentState] Warning: missing or empty '{key}'"
                print(warning)
                warnings.append(warning)
        return warnings
