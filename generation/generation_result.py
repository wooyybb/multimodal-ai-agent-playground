from dataclasses import asdict, dataclass, field


@dataclass
class GenerationResult:
    output_image_path: str
    generation_provider: str
    generation_backend: str
    generation_mode: str
    generation_config: dict
    latency: float = 0.0
    prompt_length: int = 0
    generation_notes: list[str] = field(default_factory=list)
    used_fallback: bool = False
    reference_conditioning_enabled: bool = False
    conditioning_type: str = "none"
    ip_adapter_enabled: bool = False
    used_conditioning_fallback: bool = False
    conditioning_reason: str = ""
    ip_adapter_status: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)
