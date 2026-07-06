from dataclasses import asdict, dataclass


@dataclass
class GenerationConfig:
    provider: str = "flux_fast"
    mode: str = "fast"
    width: int = 1024
    height: int = 1024
    steps: int = 4
    cfg: float | None = None
    strength: float = 0.55
    scheduler: str = "schnell"
    resolution: str = "1024x1024"
    generation_preset: dict | None = None
    preset_reason: str = ""
    environment_overrides: dict | None = None

    @classmethod
    def from_plan(cls, plan: dict | None) -> "GenerationConfig":
        plan = plan or {}
        width, height = cls._parse_resolution(plan.get("resolution", "1024x1024"))
        return cls(
            provider=plan.get("provider", "flux_fast"),
            mode=plan.get("generation_mode", "fast"),
            width=width,
            height=height,
            steps=int(plan.get("steps") or 4),
            cfg=plan.get("cfg"),
            strength=float(plan.get("strength") or 0.55),
            scheduler=plan.get("scheduler") or "schnell",
            resolution=f"{width}x{height}",
            generation_preset=plan.get("generation_preset") or {},
            preset_reason=plan.get("preset_reason") or "",
            environment_overrides=plan.get("environment_overrides") or {},
        )

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def _parse_resolution(value):
        try:
            width, height = str(value).lower().split("x", 1)
            return max(256, int(width)), max(256, int(height))
        except (TypeError, ValueError):
            return 1024, 1024
