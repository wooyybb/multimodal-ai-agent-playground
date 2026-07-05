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
    generation_is_mock: bool = False
    fallback_reason: str = ""
    generation_error_type: str = ""
    generation_error_repr: str = ""
    generation_error_traceback: str = ""
    generation_error_stage: str = ""
    model_id: str = ""
    strength: float | None = None
    device: str = ""
    dtype: str = ""
    reference_conditioning_enabled: bool = False
    conditioning_type: str = "none"
    ip_adapter_enabled: bool = False
    ip_adapter_loaded: bool = False
    ip_adapter_scale: float = 0.75
    used_conditioning_fallback: bool = False
    conditioning_fallback_reason: str = ""
    conditioning_reason: str = ""
    ip_adapter_status: dict = field(default_factory=dict)
    style_program: dict = field(default_factory=dict)
    selected_lora: str = ""
    lora_status: dict = field(default_factory=dict)
    controlnet_status: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)
